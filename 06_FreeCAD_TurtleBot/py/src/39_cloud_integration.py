# -*- coding: utf-8 -*-
"""
파일 39: 클라우드 통합
================================
설계 데이터를 클라우드와 연동하는 시스템.

학습 목표:
- JSON 기반 설계 데이터 직렬화/역직렬화
- API 서버 모의 (로컬 환경에서 REST API 시뮬레이션)
- 설계 데이터 저장/조회/검색
- 외부 시스템 연동 준비 (IoT, ERP, PDM 등)
- HTTP 클라이언트 동작 이해

사용 방법:
    FreeCAD에서 실행하거나 외부 Python에서 모듈로 사용합니다.
    로컬 API 서버 모의를 통해 네트워크 없이도 테스트 가능합니다.

의존성: 표준 라이브러리만 사용
"""

import sys
import os
import json
import math
import time
import datetime
import hashlib
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# FreeCAD 환경 확인
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[정보] FreeCAD 모듈을 사용할 수 없습니다. 시뮬레이션 모드로 동작합니다.")


# ============================================================
# 1단계: 설계 데이터 직렬화
# ============================================================

class 설계데이터:
    """
    FreeCAD 설계 데이터를 JSON 호환 형식으로 직렬화/역직렬화하는 클래스.

    지원 데이터:
        - 기본 정보 (이름, 설명, 버전)
        - 치수 데이터
        - 재료 정보
        - 메타데이터 (작성일, 작성자, 태그)
        - 설계 이력
    """

    def __init__(self, 이름="미정"):
        self.기본정보 = {
            "이름": 이름,
            "설명": "",
            "버전": "1.0",
            "유형": "하우징",      # 하우징, 브래킷, 실린더 등
            "상태": "초안",        # 초안, 검토중, 승인, 반려
        }
        self.치수 = {
            "가로_mm": 80.0,
            "세로_mm": 60.0,
            "높이_mm": 35.0,
            "벽두께_mm": 2.0,
            "모서리반경_mm": 1.0,
        }
        self.재료 = {
            "이름": "PLA",
            "밀도_gcm3": 1.24,
            "融点_C": 210.0,
            "추정량_g": 0.0,
        }
        self.메타데이터 = {
            "작성일": datetime.datetime.now().isoformat(),
            "수정일": datetime.datetime.now().isoformat(),
            "작성자": "자동화시스템",
            "태그": [],
            "프로젝트": "",
        }
        self.설계이력 = []        # 변경 이력 목록
        self.추가속성 = {}        # 자유 속성

        # 초기 추정량 계산
        self._추정량_계산()

    def _추정량_계산(self):
        """현재 치수 기반 재료 사용량을 추정합니다."""
        가로 = self.치수.get("가로_mm", 80)
        세로 = self.치수.get("세로_mm", 60)
        높이 = self.치수.get("높이_mm", 35)
        벽 = self.치수.get("벽두께_mm", 2)

        외부부피 = 가로 * 세로 * 높이
        내부부피 = max(0, (가로 - 벽*2)) * max(0, (세로 - 벽*2)) * max(0, (높이 - 벽))
        재료부피 = 외부부피 - 내부부피

        밀도 = self.재료.get("밀도_gcm3", 1.24)
        self.재료["추정량_g"] = round(재료부피 / 1000.0 * 밀도, 1)

    def to_dict(self):
        """딕셔너리로 직렬화"""
        self.메타데이터["수정일"] = datetime.datetime.now().isoformat()
        self._추정량_계산()

        return {
            "기본정보": self.기본정보,
            "치수": self.치수,
            "재료": self.재료,
            "메타데이터": self.메타데이터,
            "설계이력": self.설계이력,
            "추가속성": self.추가속성,
        }

    def to_json(self, 들여쓰기=2):
        """JSON 문자열로 직렬화"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=들여쓰기)

    @classmethod
    def from_dict(cls, 데이터):
        """딕셔너리에서 역직렬화"""
        obj = cls()
        obj.기본정보 = 데이터.get("기본정보", obj.기본정보)
        obj.치수 = 데이터.get("치수", obj.치수)
        obj.재료 = 데이터.get("재료", obj.재료)
        obj.메타데이터 = 데이터.get("메타데이터", obj.메타데이터)
        obj.설계이력 = 데이터.get("설계이력", [])
        obj.추가속성 = 데이터.get("추가속성", {})
        return obj

    @classmethod
    def from_json(cls, json문자열):
        """JSON 문자열에서 역직렬화"""
        데이터 = json.loads(json문자열)
        return cls.from_dict(데이터)

    def 변경이력추가(self, 설명, 필드, 이전값, 이후값):
        """변경 이력을 추가합니다."""
        self.설계이력.append({
            "타임스탬프": datetime.datetime.now().isoformat(),
            "설명": 설명,
            "필드": 필드,
            "이전값": 이전값,
            "이후값": 이후값,
        })

    def FreeCAD에서_추출(self):
        """FreeCAD 활성 문서에서 데이터를 추출합니다."""
        if not FREECAD_AVAILABLE:
            return False

        try:
            doc = FreeCAD.ActiveDocument
            if doc is None:
                return False

            for obj in doc.Objects:
                if hasattr(obj, "Shape") and obj.Shape.Solids:
                    bb = obj.Shape.BoundBox
                    self.치수["가로_mm"] = round(bb.XLength, 2)
                    self.치수["세로_mm"] = round(bb.YLength, 2)
                    self.치수["높이_mm"] = round(bb.ZLength, 2)

                    for prop in obj.PropertiesList:
                        if prop == "Radius" or prop == "Radius1":
                            try:
                                self.치수["모서리반경_mm"] = round(getattr(obj, prop), 2)
                            except Exception:
                                pass

                    self._추정량_계산()
                    print(f"[추출] FreeCAD 모델 '{obj.Name}' 데이터 추출 완료")
                    return True

        except Exception as e:
            print(f"[오류] FreeCAD 데이터 추출 실패: {e}")

        return False

    def 샘플데이터_생성(self):
        """샘플 설계 데이터를 생성합니다."""
        self.기본정보["이름"] = "IoT_센서케이스_v2"
        self.기본정보["설명"] = "ESP32 기반 IoT 센서 노드 하우징"
        self.기본정보["유형"] = "하우징"
        self.기본정보["상태"] = "검토중"
        self.치수 = {
            "가로_mm": 90.0,
            "세로_mm": 65.0,
            "높이_mm": 38.0,
            "벽두께_mm": 2.5,
            "모서리반경_mm": 1.5,
        }
        self.재료["이름"] = "PETG"
        self.재료["밀도_gcm3"] = 1.27
        self.메타데이터["프로젝트"] = "스마트팜IoT"
        self.메타데이터["태그"] = ["IoT", "ESP32", "방수"]
        self._추정량_계산()

    def 정보_출력(self):
        """설계 데이터를 출력합니다."""
        print(f"\n  설계 데이터: {self.기본정보['이름']}")
        print(f"  설명: {self.기본정보['설명']}")
        print(f"  유형: {self.기본정보['유형']} | 상태: {self.기본정보['상태']}")
        print(f"  치수: {self.치수['가로_mm']} x {self.치수['세로_mm']} x {self.치수['높이_mm']} mm")
        print(f"  벽두께: {self.치수['벽두께_mm']}mm | 반경: {self.치수['모서리반경_mm']}mm")
        print(f"  재료: {self.재료['이름']} | 추정량: {self.재료['추정량_g']}g")
        print(f"  태그: {', '.join(self.메타데이터['태그']) or '없음'}")
        print(f"  변경 이력: {len(self.설계이력)}건")


# ============================================================
# 2단계: API 서버 모의 (로컬)
# ============================================================

# 전역 저장소 (API 서버용)
_저장소 = {}


class API요청처리기(BaseHTTPRequestHandler):
    """
    REST API 요청을 처리하는 핸들러.

    지원 엔드포인트:
        GET    /api/designs       - 전체 목록 조회
        GET    /api/designs/{id}  - 개별 조회
        POST   /api/designs       - 새 설계 저장
        PUT    /api/designs/{id}  - 설계 수정
        DELETE /api/designs/{id}  - 설계 삭제
        GET    /api/search        - 검색
        GET    /api/stats         - 통계
    """

    def log_message(self, format, *args):
        """로그 메시지 억제 ( 시연 깔끔하게)"""
        pass

    def _응답_보내기(self, 상태코드, 데이터):
        """JSON 응답을 보냅니다."""
        self.send_response(상태코드)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        응답 = json.dumps(데이터, ensure_ascii=False, indent=2)
        self.wfile.write(응답.encode("utf-8"))

    def _요청본문_읽기(self):
        """요청 본문을 읽어 JSON으로 파싱합니다."""
        길이 = int(self.headers.get("Content-Length", 0))
        if 길이 == 0:
            return {}
        본문 = self.rfile.read(길이)
        return json.loads(본문.decode("utf-8"))

    def do_GET(self):
        """GET 요청 처리"""
        parsed = urlparse(self.path)
        경로 = parsed.path
        쿼리 = parse_qs(parsed.query)

        if 경로 == "/api/designs":
            # 전체 목록 조회
            목록 = list(_저장소.values())
            self._응답_보내기(200, {
                "상태": "성공",
                "데이터수": len(목록),
                "데이터": 목록,
            })

        elif 경로.startswith("/api/designs/"):
            # 개별 조회
            id = 경로.split("/")[-1]
            if id in _저장소:
                self._응답_보내기(200, {
                    "상태": "성공",
                    "데이터": _저장소[id],
                })
            else:
                self._응답_보내기(404, {
                    "상태": "오류",
                    "메시지": f"설계 '{id}'을(를) 찾을 수 없습니다.",
                })

        elif 경로 == "/api/search":
            # 검색
            키워드 = 쿼리.get("q", [""])[0]
            결과 = []
            for id, 데이터 in _저장소.items():
                이름 = 데이터.get("기본정보", {}).get("이름", "")
                설명 = 데이터.get("기본정보", {}).get("설명", "")
                if 키워드.lower() in 이름.lower() or 키워드.lower() in 설명.lower():
                    결과.append(데이터)
            self._응답_보내기(200, {
                "상태": "성공",
                "검색어": 키워드,
                "결과수": len(결과),
                "데이터": 결과,
            })

        elif 경로 == "/api/stats":
            # 통계
            총수 = len(_저장소)
            유형별 = {}
            상태별 = {}
            for 데이터 in _저장소.values():
                유형 = 데이터.get("기본정보", {}).get("유형", "기타")
                상태 = 데이터.get("기본정보", {}).get("상태", "미정")
                유형별[유형] = 유형별.get(유형, 0) + 1
                상태별[상태] = 상태별.get(상태, 0) + 1

            self._응답_보내기(200, {
                "상태": "성공",
                "총설계수": 총수,
                "유형별": 유형별,
                "상태별": 상태별,
            })

        else:
            self._응답_보내기(404, {
                "상태": "오류",
                "메시지": "알 수 없는 경로",
            })

    def do_POST(self):
        """POST 요청 처리 (새 설계 저장)"""
        parsed = urlparse(self.path)

        if parsed.path == "/api/designs":
            try:
                데이터 = self._요청본문_읽기()
                이름 = 데이터.get("기본정보", {}).get("이름", f"design_{int(time.time())}")

                # ID 생성
                id = hashlib.md5(이름.encode()).hexdigest()[:8]
                데이터["_id"] = id
                데이터["_생성일"] = datetime.datetime.now().isoformat()

                _저장소[id] = 데이터

                self._응답_보내기(201, {
                    "상태": "성공",
                    "메시지": f"설계 '{이름}' 저장 완료",
                    "_id": id,
                    "데이터": 데이터,
                })

            except Exception as e:
                self._응답_보내기(400, {
                    "상태": "오류",
                    "메시지": str(e),
                })
        else:
            self._응답_보내기(404, {
                "상태": "오류",
                "메시지": "알 수 없는 경로",
            })

    def do_PUT(self):
        """PUT 요청 처리 (설계 수정)"""
        parsed = urlparse(self.path)

        if parsed.path.startswith("/api/designs/"):
            id = parsed.path.split("/")[-1]
            if id in _저장소:
                try:
                    데이터 = self._요청본문_읽기()
                    데이터["_id"] = id
                    데이터["_수정일"] = datetime.datetime.now().isoformat()
                    _저장소[id] = 데이터

                    self._응답_보내기(200, {
                        "상태": "성공",
                        "메시지": f"설계 '{id}' 수정 완료",
                        "데이터": 데이터,
                    })
                except Exception as e:
                    self._응답_보내기(400, {
                        "상태": "오류",
                        "메시지": str(e),
                    })
            else:
                self._응답_보내기(404, {
                    "상태": "오류",
                    "메시지": f"설계 '{id}'을(를) 찾을 수 없습니다.",
                })
        else:
            self._응답_보내기(404, {
                "상태": "오류",
                "메시지": "알 수 없는 경로",
            })

    def do_DELETE(self):
        """DELETE 요청 처리 (설계 삭제)"""
        parsed = urlparse(self.path)

        if parsed.path.startswith("/api/designs/"):
            id = parsed.path.split("/")[-1]
            if id in _저장소:
                삭제됨 = _저장소.pop(id)
                self._응답_보내기(200, {
                    "상태": "성공",
                    "메시지": f"설계 '{id}' 삭제 완료",
                })
            else:
                self._응답_보내기(404, {
                    "상태": "오류",
                    "메시지": f"설계 '{id}'을(를) 찾을 수 없습니다.",
                })
        else:
            self._응답_보내기(404, {
                "상태": "오류",
                "메시지": "알 수 없는 경로",
            })

    def do_OPTIONS(self):
        """CORS 프리플라이트 요청 처리"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


class 로컬API서버:
    """
    로컬에서 REST API 서버를 모의하는 클래스.

    실제 HTTP 서버를 시작하거나, 시뮬레이션 모드로 동작합니다.
    """

    def __init__(self, 포트=8765):
        self.포트 = 포트
        self.서버 = None
        self.스레드 = None
        self.실행중 = False

    def 시작(self):
        """백그라운드에서 API 서버를 시작합니다."""
        try:
            self.서버 = HTTPServer(("localhost", self.포트), API요청처리기)
            self.스레드 = threading.Thread(target=self.서버.serve_forever, daemon=True)
            self.스레드.start()
            self.실행중 = True
            print(f"[서버] 로컬 API 서버 시작: http://localhost:{self.포트}")
            return True
        except Exception as e:
            print(f"[오류] API 서버 시작 실패: {e}")
            print("[정보] 시뮬레이션 모드로 동작합니다.")
            self.실행중 = False
            return False

    def 중지(self):
        """API 서버를 중지합니다."""
        if self.서버:
            self.서버.shutdown()
            self.실행중 = False
            print("[서버] API 서버 중지")


# ============================================================
# 3단계: API 클라이언트
# ============================================================

class APIClient:
    """
    REST API 클라이언트.

    로컬 API 서버와 통신하거나,
    오프라인 시뮬레이션 모드로 동작합니다.
    """

    def __init__(self, 기본URL="http://localhost:8765"):
        self.기본URL = 기본URL

    def _요청(self, 메서드, 경로, 데이터=None):
        """
        HTTP 요청을 시뮬레이션합니다.

        실제 환경에서는 requests 라이브러리를 사용합니다.
        여기서는 로컬 저장소와 직접 통신하는 시뮬레이션을 수행합니다.
        """
        전체경로 = f"{self.기본URL}{경로}"
        print(f"  [API] {메서드} {전체경로}")

        # 시뮬레이션 모드: 전역 저장소 직접 접근
        parsed = urlparse(경로)
        url경로 = parsed.path
        쿼리 = parse_qs(parsed.query)

        if 메서드 == "GET" and url경로 == "/api/designs":
            목록 = list(_저장소.values())
            return {"상태": "성공", "데이터수": len(목록), "데이터": 목록}

        elif 메서드 == "GET" and url경로.startswith("/api/designs/"):
            id = url경로.split("/")[-1]
            if id in _저장소:
                return {"상태": "성공", "데이터": _저장소[id]}
            return {"상태": "오류", "메시지": f"'{id}' 없음"}

        elif 메서드 == "POST" and url경로 == "/api/designs" and 데이터:
            이름 = 데이터.get("기본정보", {}).get("이름", f"design_{int(time.time())}")
            id = hashlib.md5(이름.encode()).hexdigest()[:8]
            데이터["_id"] = id
            데이터["_생성일"] = datetime.datetime.now().isoformat()
            _저장소[id] = 데이터
            return {"상태": "성공", "_id": id, "메시지": f"저장 완료: {이름}"}

        elif 메서드 == "PUT" and url경로.startswith("/api/designs/") and 데이터:
            id = url경로.split("/")[-1]
            if id in _저장소:
                데이터["_id"] = id
                _저장소[id] = 데이터
                return {"상태": "성공", "메시지": f"수정 완료: {id}"}
            return {"상태": "오류", "메시지": f"'{id}' 없음"}

        elif 메서드 == "DELETE" and url경로.startswith("/api/designs/"):
            id = url경로.split("/")[-1]
            if id in _저장소:
                _저장소.pop(id)
                return {"상태": "성공", "메시지": f"삭제 완료: {id}"}
            return {"상태": "오류", "메시지": f"'{id}' 없음"}

        elif 메서드 == "GET" and url경로 == "/api/search":
            키워드 = 쿼리.get("q", [""])[0]
            결과 = [d for d in _저장소.values()
                    if 키워드.lower() in json.dumps(d, ensure_ascii=False).lower()]
            return {"상태": "성공", "검색어": 키워드, "결과수": len(결과), "데이터": 결과}

        elif 메서드 == "GET" and url경로 == "/api/stats":
            총수 = len(_저장소)
            유형별 = {}
            for d in _저장소.values():
                u = d.get("기본정보", {}).get("유형", "기타")
                유형별[u] = 유형별.get(u, 0) + 1
            return {"상태": "성공", "총설계수": 총수, "유형별": 유형별}

        return {"상태": "오류", "메시지": "알 수 없는 요청"}

    def 설계_저장(self, 설계데이터객체):
        """설계 데이터를 서버에 저장합니다."""
        데이터 = 설계데이터객체.to_dict()
        return self._요청("POST", "/api/designs", 데이터)

    def 설계_조회(self, id):
        """설계 데이터를 조회합니다."""
        return self._요청("GET", f"/api/designs/{id}")

    def 설계_목록(self):
        """전체 설계 목록을 조회합니다."""
        return self._요청("GET", "/api/designs")

    def 설계_수정(self, id, 데이터):
        """설계 데이터를 수정합니다."""
        return self._요청("PUT", f"/api/designs/{id}", 데이터)

    def 설계_삭제(self, id):
        """설계 데이터를 삭제합니다."""
        return self._요청("DELETE", f"/api/designs/{id}")

    def 검색(self, 키워드):
        """설계 데이터를 검색합니다."""
        return self._요청("GET", f"/api/search?q={키워드}")

    def 통계(self):
        """저장소 통계를 조회합니다."""
        return self._요청("GET", "/api/stats")


# ============================================================
# 4단계: 외부 시스템 연동 어댑터
# ============================================================

class 외부시스템연동:
    """
    외부 시스템과의 연동을 위한 어댑터 패턴 구현.

    지원 시스템:
        - IoT 플랫폼 (센서 데이터 연동)
        - ERP 시스템 (자재/비용 연동)
        - PDM 시스템 (제품 데이터 관리)
        - 3D 프린터 (출력 큐 연동)
    """

    @staticmethod
    def IoT_센서데이터_변환(설계데이터):
        """
        설계 데이터를 IoT 플랫폼용 포맷으로 변환합니다.

        매개변수:
            설계데이터 (설계데이터): 변환할 설계 데이터

        반환값:
            dict: IoT 플랫폼 호환 데이터
        """
        return {
            "device_type": "enclosure",
            "name": 설계데이터.기본정보["이름"],
            "dimensions": {
                "width": 설계데이터.치수["가로_mm"],
                "depth": 설계데이터.치수["세로_mm"],
                "height": 설계데이터.치수["높이_mm"],
                "wall_thickness": 설계데이터.치수["벽두께_mm"],
            },
            "material": {
                "type": 설계데이터.재료["이름"],
                "density": 설계데이터.재료["밀도_gcm3"],
            },
            "tags": 설계데이터.메타데이터["태그"],
            "status": 설계데이터.기본정보["상태"],
            "timestamp": datetime.datetime.now().isoformat(),
        }

    @staticmethod
    def ERP_자재명세서_생성(설계데이터):
        """
        설계 데이터를 ERP 시스템용 자재 명세서로 변환합니다.

        매개변수:
            설계데이터 (설계데이터): 설계 데이터

        반환값:
            dict: ERP 호환 자재 명세서
        """
        추정량 = 설계데이터.재료["추정량_g"]

        return {
            "BOM_유형": "제조BOM",
            "품목": [
                {
                    "품목명": f"{설계데이터.기본정보['이름']}_본체",
                    "소재": 설계데이터.재료["이름"],
                    "수량": 1,
                    "단위": "개",
                    "추정중량_g": 추정량,
                    "추정가격": round(추정량 * 0.02, 2),  # g당 0.02원 추정
                },
                {
                    "품목명": f"{설계데이터.기본정보['이름']}_나사",
                    "소재": "스테인리스",
                    "수량": 설계데이터.추가속성.get("나사수", 4),
                    "단위": "개",
                    "규격": "M3x8",
                    "추정가격": 50,
                },
            ],
            "총추정가격": round(추정량 * 0.02 + 설계데이터.추가속성.get("나사수", 4) * 50, 2),
        }

    @staticmethod
    def PDM_제품속성(설계데이터):
        """
        PDM(제품 데이터 관리) 시스템용 속성을 생성합니다.

        매개변수:
            설계데이터 (설계데이터): 설계 데이터

        반환값:
            dict: PDM 호환 속성 데이터
        """
        return {
            "문서유형": "3D모델",
            "문서번호": hashlib.md5(
                설계데이터.기본정보["이름"].encode()
            ).hexdigest()[:12].upper(),
            "문서명": 설계데이터.기본정보["이름"],
            "버전": 설계데이터.기본정보["버전"],
            "상태": 설계데이터.기본정보["상태"],
            "설명": 설계데이터.기본정보["설명"],
            "작성자": 설계데이터.메타데이터["작성자"],
            "작성일": 설계데이터.메타데이터["작성일"],
            "부서": "설계팀",
            "대여권한": ["설계팀", "제조팀"],
            "형식": "STEP, STL",
            "크기정보": {
                "가로": f"{설계데이터.치수['가로_mm']}mm",
                "세로": f"{설계데이터.치수['세로_mm']}mm",
                "높이": f"{설계데이터.치수['높이_mm']}mm",
            },
        }

    @staticmethod
    def 프린터_출력큐(설계데이터, 프린터="Creality Ender 3"):
        """
        3D 프린터 출력 큐용 데이터를 생성합니다.

        매개변수:
            설계데이터 (설계데이터): 설계 데이터
            프린터 (str): 프린터 이름

        반환값:
            dict: 프린터 출력 큐 데이터
        """
        추정량 = 설계데이터.재료["추정량_g"]
        # 출력 시간 추정: 약 20g/시간 (FDM 기준)
        추정시간_시간 = 추정량 / 20.0

        return {
            "프린터": 프린터,
            "파일명": f"{설계데이터.기본정보['이름']}.stl",
            "소재": 설계데이터.재료["이름"],
            "색상": "흰색",
            "추정중량_g": 추정량,
            "추정시간_시간": round(추정시간_시간, 1),
            "층고_mm": 0.2,
            "채움비율": 20,
            "지지체": "자동",
            "인쇄속도": "60mm/s",
            "상태": "대기",
            "우선순위": "보통",
        }


# ============================================================
# 메인 실행 함수
# ============================================================

def 시연():
    """클라우드 통합 시스템의 전체 기능을 시연합니다."""
    print("=" * 65)
    print("  클라우드 통합 시스템 시연")
    print("  설계 데이터 직렬화, API 서버, 외부 시스템 연동")
    print("=" * 65)

    # -----------------------------------------------------------
    # 1단계: 설계 데이터 생성 및 직렬화
    # -----------------------------------------------------------
    print("\n" + "-" * 65)
    print("  [1단계] 설계 데이터 생성 및 JSON 직렬화")
    print("-" * 65)

    설계1 = 설계데이터("IoT_센서케이스_v1")
    if not FREECAD_AVAILABLE or not 설계1.FreeCAD에서_추출():
        설계1.샘플데이터_생성()
    설계1.정보_출력()

    # JSON 직렬화
    json_텍스트 = 설계1.to_json()
    print(f"\n  JSON 직렬화 결과 (일부):")
    print(f"  {json_텍스트[:200]}...")

    # JSON 역직렬화
    복원됨 = 설계데이터.from_json(json_텍스트)
    print(f"\n  역직렬화 검증: {복원됨.기본정보['이름']} == {설계1.기본정보['이름']}")

    # 두 번째 설계
    설계2 = 설계데이터("블루투스_오디오케이스")
    설계2.치수 = {
        "가로_mm": 120.0, "세로_mm": 80.0, "높이_mm": 30.0,
        "벽두께_mm": 2.0, "모서리반경_mm": 2.0,
    }
    설계2.재료["이름"] = "ABS"
    설계2.기본정보["유형"] = "케이스"
    설계2.기본정보["상태"] = "승인"
    설계2.메타데이터["태그"] = ["블루투스", "오디오"]
    설계2._추정량_계산()

    # -----------------------------------------------------------
    # 2단계: API 서버 시작 및 CRUD 테스트
    # -----------------------------------------------------------
    print("\n" + "-" * 65)
    print("  [2단계] 로컬 API 서버 시작 및 CRUD 테스트")
    print("-" * 65)

    서버 = 로컬API서버(8765)
    서버시작됨 = 서버.시작()

    클라이언트 = APIClient()

    # 생성 (POST)
    print("\n  [저장] 설계 데이터 저장...")
    응답1 = 클라이언트.설계_저장(설계1)
    print(f"  결과: {json.dumps(응답1, ensure_ascii=False)[:120]}")

    응답2 = 클라이언트.설계_저장(설계2)
    print(f"  결과: {json.dumps(응답2, ensure_ascii=False)[:120]}")

    # 조회 (GET)
    print("\n  [목록] 전체 설계 목록 조회...")
    응답3 = 클라이언트.설계_목록()
    print(f"  총 {응답3.get('데이터수', 0)}건의 설계 데이터")

    # 검색
    print("\n  [검색] 'IoT' 키워드 검색...")
    응답4 = 클라이언트.검색("IoT")
    print(f"  검색 결과: {응답4.get('결과수', 0)}건")

    # 수정 (PUT)
    print("\n  [수정] 설계 데이터 수정...")
    수정데이터 = 설계1.to_dict()
    수정데이터["치수"]["벽두께_mm"] = 3.0
    수정데이터["기본정보"]["상태"] = "승인"
    # ID를 가져와서 수정
    if 응답1.get("_id"):
        응답5 = 클라이언트.설계_수정(응답1["_id"], 수정데이터)
        print(f"  결과: {json.dumps(응답5, ensure_ascii=False)[:120]}")

    # 통계
    print("\n  [통계] 저장소 통계 조회...")
    응답6 = 클라이언트.통계()
    print(f"  총 설계수: {응답6.get('총설계수', 0)}")
    print(f"  유형별: {json.dumps(응답6.get('유형별', {}), ensure_ascii=False)}")

    # -----------------------------------------------------------
    # 3단계: 외부 시스템 연동
    # -----------------------------------------------------------
    print("\n" + "-" * 65)
    print("  [3단계] 외부 시스템 연동 데이터 생성")
    print("-" * 65)

    # IoT 연동
    print("\n  [IoT] IoT 플랫폼 연동 데이터:")
    iot_데이터 = 외부시스템연동.IoT_센서데이터_변환(설계1)
    print(f"  {json.dumps(iot_데이터, ensure_ascii=False, indent=4)}")

    # ERP 연동
    print("\n  [ERP] 자재 명세서:")
    erp_데이터 = 외부시스템연동.ERP_자재명세서_생성(설계1)
    for 항목 in erp_데이터["품목"]:
        print(f"    - {항목['품목명']}: {항목['소재']} {항목['수량']}{항목['단위']}"
              f" (약 {항목.get('추정가격', 0):.0f}원)")
    print(f"    총 추정 가격: 약 {erp_데이터['총추정가격']:.0f}원")

    # PDM 연동
    print("\n  [PDM] 제품 속성:")
    pdm_데이터 = 외부시스템연동.PDM_제품속성(설계1)
    print(f"    문서번호: {pdm_데이터['문서번호']}")
    print(f"    문서명: {pdm_데이터['문서명']}")
    print(f"    버전: {pdm_데이터['버전']}")

    # 프린터 큐
    print("\n  [프린터] 3D 프린터 출력 큐:")
    프린터_데이터 = 외부시스템연동.프린터_출력큐(설계1)
    for 키, 값 in 프린터_데이터.items():
        print(f"    {키}: {값}")

    # -----------------------------------------------------------
    # 4단계: 변경 이력 추적
    # -----------------------------------------------------------
    print("\n" + "-" * 65)
    print("  [4단계] 설계 변경 이력")
    print("-" * 65)

    설계1.변경이력추가("벽 두께 증가", "벽두께_mm", 2.0, 3.0)
    설계1.변경이력추가("상태 변경", "상태", "초안", "승인")

    print(f"\n  변경 이력 ({len(설계1.설계이력)}건):")
    for 이력 in 설계1.설계이력:
        print(f"    [{이력['타임스탬프'][:19]}] {이력['설명']}: "
              f"{이력['이전값']} -> {이력['이후값']}")

    # -----------------------------------------------------------
    # 5단계: 파일 저장
    # -----------------------------------------------------------
    print("\n" + "-" * 65)
    print("  [5단계] 설계 데이터 파일 저장")
    print("-" * 65)

    출력디렉토리 = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
    os.makedirs(출력디렉토리, exist_ok=True)

    # JSON 파일 저장
    저장경로 = os.path.join(출력디렉토리, "design_data.json")
    전체데이터 = {
        "설계목록": [설계1.to_dict(), 설계2.to_dict()],
        "생성일": datetime.datetime.now().isoformat(),
        "시스템": "FreeCAD 클라우드 통합 v1.0",
    }
    with open(저장경로, "w", encoding="utf-8") as f:
        json.dump(전체데이터, f, ensure_ascii=False, indent=2)
    print(f"[저장] 설계 데이터: {저장경로}")

    # 서버 중지
    if 서버시작됨:
        서버.중지()

    # 최종 요약
    print("\n" + "=" * 65)
    print("  클라우드 통합 시스템 시연 완료!")
    print("=" * 65)
    print(f"  관리 설계수: {len(_저장소)}건")
    print(f"  지원 연동: IoT, ERP, PDM, 3D 프린터")
    print(f"  데이터 형식: JSON")
    print("=" * 65)


# ============================================================
# 스크립트 실행
# ============================================================

if __name__ == "__main__" or FREECAD_AVAILABLE:
    시연()
else:
    print("[정보] FreeCAD 모드에서 실행하면 실제 모델 데이터를 연동합니다.")
    print("[정보] 현재 시뮬레이션 모드로 동작합니다.")
    시연()

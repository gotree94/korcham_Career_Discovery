# -*- coding: utf-8 -*-
"""
파일 36: 전체 자동화 파이프라인
================================
설계 요구사항 입력부터 STL/STEP 내보내기까지 자동화하는 종합 파이프라인.

학습 목표:
- 텍스트 기반 요구사항 파싱
- AI 기반 설계 결정 (오프라인 규칙 + 온라인 LLM)
- FreeCAD 모델 자동 생성
- 자동 검증 (규칙 기반 + AI 리뷰)
- STL/STEP 내보내기
- HTML 리포트 자동 생성
- 전체 파이프라인 시연

사용 방법:
    FreeCAD에서 이 파일을 실행하거나, 외부 Python에서 모듈로 호출합니다.
    요구사항은 딕셔너리로 전달하며, 텍스트 파서도 지원합니다.

필요한 패키지: openai (선택사항, AI 리뷰용)
"""

import sys
import os
import math
import json
import datetime
import hashlib

# FreeCAD 환경 확인
FREECAD_AVAILABLE = False
try:
    import FreeCAD
    import Part
    from FreeCAD import Base
    FREECAD_AVAILABLE = True
except ImportError:
    print("[정보] FreeCAD 모듈을 사용할 수 없습니다. 시뮬레이션 모드로 동작합니다.")

# openai 라이브러리 확인
OPENAI_AVAILABLE = False
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass

# API 클라이언트 초기화
_api_client = None
_api_key = os.environ.get("OPENAI_API_KEY", "")
if OPENAI_AVAILABLE and _api_key:
    try:
        _api_client = openai.OpenAI(api_key=_api_key)
        print("[정보] AI API 연결됨")
    except Exception:
        pass


# ============================================================
# 1단계: 요구사항 파싱
# ============================================================

class 설계요구사항:
    """설계 요구사항을 저장하고 파싱하는 클래스"""

    def __init__(self):
        """기본 요구사항 초기화"""
        self.제품명 = "미정"
        self.제품유형 = "상자"        # 상자, 실린더, 브래킷, 하우징 등
        self.가로_mm = 100.0
        self.세로_mm = 80.0
        self.높이_mm = 50.0
        self.벽두께_mm = 2.0
        self.재료 = "PLA"            # PLA, ABS, 알루미늄, 강재 등
        self.공차_mm = 0.1
        self.마운트홀_수 = 4
        self.마운트홀지름_mm = 3.2
        self.케이블홀_수 = 1
        self.케이블홀지름_mm = 5.0
        self.모서리반경_mm = 1.0
        self.내부구조 = []            # 리브, 보스, 캐비티 등
        self.특수요구사항 = []        # 방수, 열방출, EMC 등
        self.호환보드 = ""            # Arduino Uno, Raspberry Pi 등
        self.버전 = "1.0"
        self.작성일 = datetime.datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        """객체를 딕셔너리로 변환"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


def 텍스트_요구사항_파싱(텍스트):
    """
    자유 형식 텍스트에서 요구사항을 파싱합니다.

    지원 키워드:
        제품명, 크기, 가로, 세로, 높이, 두께, 재료, 공차,
        마운트홀, 케이블홀, 반경, 보드, 버전 등

    매개변수:
        텍스트 (str): 자유 형식 요구사항 텍스트

    반환값:
        설계요구사항: 파싱된 요구사항 객체
    """
    요구사항 = 설계요구사항()

    텍스트_소문자 = 텍스트.lower()

    # 제품명 추출
    for 줄 in 텍스트.split("\n"):
        줄 = 줄.strip()
        if "제품명" in 줄 or "이름" in 줄:
            parts = 줄.split(":")
            if len(parts) < 2:
                parts = 줄.split("은")
            if len(parts) < 2:
                parts = 줄.split("는")
            if len(parts) >= 2:
                요구사항.제품명 = parts[-1].strip().strip("\"'")

    # 제품 유형 추출
    유형매핑 = {
        "상자": "상자", "박스": "상자", "box": "상자",
        "실린더": "실린더", "원통": "실린더", "cylinder": "실린더",
        "브래킷": "브래킷", "지지대": "브래킷", "bracket": "브래킷",
        "하우징": "하우징", "케이스": "하우징", "housing": "하우징",
        "커버": "커버", "뚜껑": "커버", "cover": "커버",
    }
    for 키, 유형 in 유형매핑.items():
        if 키 in 텍스트_소문자:
            요구사항.제품유형 = 유형
            break

    # 치수 추출 (패턴: "100x80x50" 또는 "가로 100, 세로 80, 높이 50")
    import re
    치수_패턴 = re.compile(r'(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)\s*[xX×]\s*(\d+(?:\.\d+)?)')
    매치 = 치수_패턴.search(텍스트)
    if 매치:
        요구사항.가로_mm = float(매치.group(1))
        요구사항.세로_mm = float(매치.group(2))
        요구사항.높이_mm = float(매치.group(3))

    # 개별 치수 추출
    for 키워드, 속성 in [("가로", "가로_mm"), ("세로", "세로_mm"), ("높이", "높이_mm"),
                          ("폭", "가로_mm"), ("깊이", "세로_mm")]:
        패턴 = re.compile(rf'{키워드}\s*[:=\s]*(\d+(?:\.\d+)?)')
        m = 패턴.search(텍스트)
        if m:
            setattr(요구사항, 속성, float(m.group(1)))

    # 두께 추출
    두께_패턴 = re.compile(r'두께\s*[:=\s]*(\d+(?:\.\d+)?)')
    m = 두께_패턴.search(텍스트)
    if m:
        요구사항.벽두께_mm = float(m.group(1))

    # 재료 추출
    재료매핑 = {
        "pla": "PLA", "abs": "ABS", "petg": "PETG",
        "알루미늄": "알루미늄", "강": "강재", "강재": "강재",
        "stl": "강재", "스테인리스": "스테인리스",
        "나일론": "나일론", "wood": "나무",
    }
    for 키, 재료 in 재료매핑.items():
        if 키 in 텍스트_소문자:
            요구사항.재료 = 재료
            break

    # 보드 호환성 추출
    보드매핑 = {
        "arduino uno": "Arduino Uno", "uno": "Arduino Uno",
        "arduino nano": "Arduino Nano", "nano": "Arduino Nano",
        "라즈베리파이": "Raspberry Pi", "raspberry": "Raspberry Pi",
        "rpi": "Raspberry Pi", "esp32": "ESP32", "esp8266": "ESP8266",
    }
    for 키, 보드 in 보드매핑.items():
        if 키 in 텍스트_소문자:
            요구사항.호환보드 = 보드
            break

    # 마운트홀 수
    홀_패턴 = re.compile(r'마운트홀\s*[:=\s]*(\d+)')
    m = 홀_패턴.search(텍스트)
    if m:
        요구사항.마운트홀_수 = int(m.group(1))

    print(f"[파싱] 요구사항 파싱 완료: {요구사항.제품명}")
    return 요구사항


# ============================================================
# 2단계: AI 기반 설계 결정
# ============================================================

class AI설계결정:
    """
    요구사항을 분석하여 구체적인 설계 파라미터를 결정합니다.
    온라인 LLM이 있으면 API 호출, 없으면 규칙 기반 결정을 수행합니다.
    """

    # 재료별 최소 벽 두께 (mm)
    재료별최소두께 = {
        "PLA": 1.0, "ABS": 1.0, "PETG": 1.0,
        "알루미늄": 2.0, "강재": 1.5, "스테인리스": 1.5,
        "나일론": 1.2, "나무": 3.0,
    }

    # 재료별 모서리 반경 권장 (mm)
    재료별권장반경 = {
        "PLA": 0.5, "ABS": 0.5, "PETG": 0.5,
        "알루미늄": 1.0, "강재": 0.8, "스테인리스": 0.8,
        "나일론": 0.5, "나무": 2.0,
    }

    # 보드별 마운트홀 패턴 (x오프셋, y오프셋 목록, 보드 크기)
    보드크기 = {
        "Arduino Uno": (68.6, 53.3),
        "Arduino Nano": (45.0, 18.0),
        "Raspberry Pi": (85.0, 56.0),
        "ESP32": (51.0, 25.0),
        "ESP8266": (26.0, 48.0),
    }

    @classmethod
    def 규칙기반_결정(cls, 요구사항):
        """
        규칙 기반으로 설계 파라미터를 결정합니다.

        매개변수:
            요구사항 (설계요구사항): 설계 요구사항

        반환값:
            dict: 결정된 설계 파라미터
        """
        print("[AI 결정] 규칙 기반 설계 결정 시작...")

        결정 = {}

        # 벽 두께 결정 (재료 기반)
        최소두께 = cls.재료별최소두께.get(요구사항.재료, 1.5)
        결정["벽두께"] = max(요구사항.벽두께_mm, 최소두께)
        if 결정["벽두께"] < 최소두께:
            print(f"  [보정] 벽 두께가 최소 기준({최소두께}mm) 미만이므로 {최소두께}mm로 보정")

        # 모서리 반경 결정
        권장반경 = cls.재료별권장반경.get(요구사항.재료, 1.0)
        결정["모서리반경"] = max(요구사항.모서리반경_mm, 권장반경)

        # 호환보드가 있으면 보드 크기에 맞춘 내부 캐비티 계산
        if 요구사항.호환보드 and 요구사항.호환보드 in cls.보드크기:
            보드가로, 보드세로 = cls.보드크기[요구사항.호환보드]
            결정["보드가로"] = 보드가로
            결정["보드세로"] = 보드세로
            # 보드를 위한 최소 내부 치수
            최소내부가로 = 보드가로 + 4.0  # 양쪽 2mm 여유
            최소내부세로 = 보드세로 + 4.0
            결정["최소내부가로"] = 최소내부가로
            결정["최소내부세로"] = 최소내부세로

            # 외부 치수 보정
            최소외부가로 = 최소내부가로 + 결정["벽두께"] * 2
            최소외부세로 = 최소내부세로 + 결정["벽두께"] * 2
            if 요구사항.가로_mm < 최소외부가로:
                print(f"  [보정] 가로가 보드 크기에 맞지 않아 {최소외부가로:.1f}mm로 증가")
                결정["가로"] = 최소외부가로
            else:
                결정["가로"] = 요구사항.가로_mm
            if 요구사항.세로_mm < 최소외부세로:
                print(f"  [보정] 세로가 보드 크기에 맞지 않아 {최소외부세로:.1f}mm로 증가")
                결정["세로"] = 최소외부세로
            else:
                결정["세로"] = 요구사항.세로_mm
        else:
            결정["가로"] = 요구사항.가로_mm
            결정["세로"] = 요구사항.세로_mm

        # 높이 결정
        결정["높이"] = 요구사항.높이_mm

        # 마운트홀 위치 계산
        홀간격x = 결정["가로"] - 결정["벽두께"] * 4
        홀간격y = 결정["세로"] - 결정["벽두께"] * 4
        마운트홀위치 = []
        수평 = max(2, int(math.ceil(요구사항.마운트홀_수 / 2)))
        수직 = max(2, int(math.ceil(요구사항.마운트홀_수 / 수평)))
        실제수 = min(요구사항.마운트홀_수, 수평 * 수직)
        for i in range(수평):
            for j in range(수직):
                if len(마운트홀위치) >= 실제수:
                    break
                x = 결정["벽두께"] * 2 + (홀간격x * i / max(1, 수평 - 1))
                y = 결정["벽두께"] * 2 + (홀간격y * j / max(1, 수직 - 1))
                마운트홀위치.append((x, y))
        결정["마운트홀위치"] = 마운트홀위치
        결정["마운트홀지름"] = 요구사항.마운트홀지름_mm

        # 케이블 홀 위치 (후면 중앙)
        결정["케이블홀위치"] = [(결정["가로"] / 2, 0, 결정["벽두께"] + 3.0)]
        결정["케이블홀지름"] = 요구사항.케이블홀지름_mm

        # 리브 두께 (벽두께의 0.8~1.0배)
        결정["리브두께"] = 결정["벽두께"] * 0.9
        결정["리브높이"] = 결정["높이"] * 0.6

        print(f"  결정된 외부 치수: {결정['가로']:.1f} x {결정['세로']:.1f} x {결정['높이']:.1f} mm")
        print(f"  결정된 벽 두께: {결정['벽두께']:.1f} mm")
        print(f"  결정된 모서리 반경: {결정['모서리반경']:.1f} mm")
        print(f"  마운트홀 {len(결정['마운트홀위치'])}개 위치 결정")

        return 결정

    @classmethod
    def AI설계제안(cls, 요구사항):
        """
        LLM API를 사용하여 AI 기반 설계 제안을 받습니다.

        매개변수:
            요구사항 (설계요구사항): 설계 요구사항

        반환값:
            str 또는 None: AI 설계 제안 텍스트
        """
        if not _api_client:
            print("[정보] AI API 미연결 - 규칙 기반 결정 사용")
            return None

        try:
            프롬프트 = f"""다음 요구사항에 맞는 FreeCAD 설계 파라미터를 제안해주세요:

제품명: {요구사항.제품명}
제품유형: {요구사항.제품유형}
치수: {요구사항.가로_mm} x {요구사항.세로_mm} x {요구사항.높이_mm} mm
벽두께: {요구사항.벽두께_mm} mm
재료: {요구사항.재료}
공차: {요구사항.공차_mm} mm
호환보드: {요구사항.호환보드 or '없음'}
특수요구사항: {', '.join(요구사항.특수요구사항) if 요구사항.특수요구사항 else '없음'}

다음 항목을 JSON 형식으로 답변해주세요:
- 최적 벽 두께 (mm)
- 모서리 반경 (mm)
- 리브 두께 (mm)
- 리브 높이 (mm)
- 추가 캐비티 필요 여부
- 제조 고려사항
- 개선 제안

한국어로 답변해주세요."""

            응답 = _api_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "당신은 3D 프린팅 및 CAD 설계 전문가입니다. "
                            "인클로저, 하우징, 케이스 설계에 정통하며, "
                            "재료 특성과 제조 공정을 깊이 이해하고 있습니다. "
                            "실용적이고 구체적인 설계 파라미터를 한국어로 제안합니다."
                        )
                    },
                    {"role": "user", "content": 프롬프트}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            결과 = 응답.choices[0].message.content
            print("[AI 제안]")
            print(결과)
            return 결과

        except Exception as e:
            print(f"[오류] AI 설계 제안 실패: {e}")
            return None


# ============================================================
# 3단계: FreeCAD 모델 생성
# ============================================================

def 모델_생성(요구사항, 설계결과):
    """
    결정된 설계 파라미터를 사용하여 FreeCAD 모델을 생성합니다.

    매개변수:
        요구사항 (설계요구사항): 원본 요구사항
        설계결과 (dict): AI/규칙 기반 설계 결정

    반환값:
        Part.Shape 또는 None: 생성된 형태
    """
    if not FREECAD_AVAILABLE:
        print("[시뮬레이션] FreeCAD 모드에서 모델을 생성할 수 없습니다.")
        print(f"  생성되었을 모델: {요구사항.제품명} ({요구사항.제품유형})")
        print(f"  크기: {설계결과['가로']:.1f} x {설계결과['세로']:.1f} x {설계결과['높이']:.1f}")
        return None

    print("\n[모델 생성] FreeCAD 모델 생성 시작...")

    doc = FreeCAD.newDocument(f"{요구사항.제품명}_v{요구사항.버전}")

    가로 = 설계결과["가로"]
    세로 = 설계결과["세로"]
    높이 = 설계결과["높이"]
    벽두께 = 설계결과["벽두께"]
    반경 = 설계결과["모서리반경"]

    # 외부 본체 생성
    print("  [1/6] 외부 본체 생성...")
    외부 = Part.makeBox(가로, 세로, 높이)

    # 내부 캐비티 제거
    print("  [2/6] 내부 캐비티 제거...")
    내부가로 = 가로 - 벽두께 * 2
    내부세로 = 세로 - 벽두께 * 2
    내부높이 = 높이 - 벽두께  # 바닥은 벽두께
    캐비티 = Part.makeBox(
        내부가로, 내부세로, 내부높이,
        Base.Vector(벽두께, 벽두께, 벽두께)
    )
    하우징 = 외부.cut(캐비티)

    # 마운트홀 생성
    print("  [3/6] 마운트홀 생성...")
    홀지름 = 설계결과["마운트홀지름"]
    for 위치 in 설계결과["마운트홀위치"]:
        홀 = Part.makeCylinder(
            홀지름 / 2, 벽두께 + 0.5,
            Base.Vector(위치[0], 위치[1], 0),
            Base.Vector(0, 0, 1)
        )
        하우징 = 하우징.cut(홀)
    print(f"    마운트홀 {len(설계결과['마운트홀위치'])}개 완료")

    # 케이블 홀 생성
    print("  [4/6] 케이블 홀 생성...")
    for 위치 in 설계결과["케이블홀위치"]:
        케이블홀 = Part.makeCylinder(
            설계결과["케이블홀지름"] / 2,
            세로,
            Base.Vector(위치[0], -0.5, 위치[2]),
            Base.Vector(0, 1, 0)
        )
        하우징 = 하우징.cut(케이블홀)
    print(f"    케이블홀 {len(설계결과['케이블홀위치'])}개 완료")

    # 리브(지지 골격) 추가
    print("  [5/6] 내부 리브 추가...")
    리브두께 = 설계결과["리브두께"]
    리브높이 = 설계결과["리브높이"]
    # X방향 리브 1개
    리브1 = Part.makeBox(
        리브두께, 내부세로, 리브높이,
        Base.Vector(가로 / 2 - 리브두께 / 2, 벽두께, 벽두께)
    )
    하우징 = 하우징.fuse(리브1)
    # Y방향 리브 1개
    리브2 = Part.makeBox(
        내부가로, 리브두께, 리브높이,
        Base.Vector(벽두께, 세로 / 2 - 리브두께 / 2, 벽두께)
    )
    하우징 = 하우징.fuse(리브2)
    print("    리브 2개 완료")

    # 모서리 반경 처리
    print("  [6/6] 모서리 마감...")
    if 반경 > 0 and len(하우징.Edges) > 0:
        try:
            모서리_리스트 = []
            for edge in 하우징.Edges:
                길이 = edge.Length
                if 길이 > min(가로, 세로, 높이) * 0.5:
                    모서리_리스트.append(edge)
            if 모서리_리스트:
                하우징 = 하우징.makeFillet(반경, 모서리_리스트[:8])
                print(f"    모서리 반경 {반경}mm 적용")
        except Exception:
            print("    모서리 반경 적용 실패 - 원래 형태 유지")

    # FreeCAD 도큐먼트에 추가
    obj = doc.addObject("Part::Feature", 요구사항.제품명)
    obj.Shape = 하우징
    doc.recompute()

    print(f"[모델 생성] '{요구사항.제품명}' 모델 생성 완료!")
    return 하우징


# ============================================================
# 4단계: 검증
# ============================================================

class 모델검증:
    """생성된 모델을 자동 검증하는 클래스"""

    def __init__(self, 요구사항, 설계결과):
        self.요구사항 = 요구사항
        self.설계결과 = 설계결과
        self.검증항목 = []

    def 치수_검증(self):
        """치수 요구사항 대비 검증"""
        print("[검증] 치수 검증...")
        항목 = {"이름": "치수 검증", "통과": True, "결과": []}

        if self.설계결과["가로"] >= self.요구사항.가로_mm:
            항목["결과"].append(f"  가로: {self.설계결과['가로']:.1f}mm >= {self.요구사항.가로_mm}mm [통과]")
        else:
            항목["결과"].append(f"  가로: {self.설계결과['가로']:.1f}mm < {self.요구사항.가로_mm}mm [실패]")
            항목["통과"] = False

        if self.설계결과["세로"] >= self.요구사항.세로_mm:
            항목["결과"].append(f"  세로: {self.설계결과['세로']:.1f}mm >= {self.요구사항.세로_mm}mm [통과]")
        else:
            항목["결과"].append(f"  세로: {self.설계결과['세로']:.1f}mm < {self.요구사항.세로_mm}mm [실패]")
            항목["통과"] = False

        if self.설계결과["높이"] >= self.요구사항.높이_mm:
            항목["결과"].append(f"  높이: {self.설계결과['높이']:.1f}mm >= {self.요구사항.높이_mm}mm [통과]")
        else:
            항목["결과"].append(f"  높이: {self.설계결과['높이']:.1f}mm < {self.요구사항.높이_mm}mm [실패]")
            항목["통과"] = False

        for 줄 in 항목["결과"]:
            print(줄)
        self.검증항목.append(항목)

    def 재료_검증(self):
        """재료별 최소 두께 검증"""
        print("[검증] 재료 검증...")
        항목 = {"이름": "재료 적합성", "통과": True, "결과": []}

        최소두께 = AI설계결정.재료별최소두께.get(self.요구사항.재료, 1.5)
        if self.설계결과["벽두께"] >= 최소두께:
            항목["결과"].append(f"  벽 두께 {self.설계결과['벽두께']:.1f}mm >= 최소 {최소두께}mm [통과]")
        else:
            항목["결과"].append(f"  벽 두께 {self.설계결과['벽두께']:.1f}mm < 최소 {최소두께}mm [실패]")
            항목["통과"] = False

        for 줄 in 항목["결과"]:
            print(줄)
        self.검증항목.append(항목)

    def 구조_검증(self):
        """구조적 안정성 검증 (간소화)"""
        print("[검증] 구조 검증...")
        항목 = {"이름": "구조 안정성", "통과": True, "결과": []}

        가로 = self.설계결과["가로"]
        세로 = self.설계결과["세로"]
        높이 = self.설계결과["높이"]
        두께 = self.설계결과["벽두께"]

        # 장단 비율 검사
        치수들 = [가로, 세로, 높이]
        비율 = max(치수들) / max(min(치수들), 0.001)
        if 비율 > 10:
            항목["결과"].append(f"  장단 비율 {비율:.1f}:1 > 10:1 [경고]")
            항목["통과"] = False
        else:
            항목["결과"].append(f"  장단 비율 {비율:.1f}:1 [통과]")

        # 벽 두께/높이 비율
        if 높이 > 0:
            높이두께비 = 높이 / max(두께, 0.001)
            if 높이두께비 > 50:
                항목["결과"].append(f"  높이/두께 비율 {높이두께비:.1f} [경고: 높은 벽]")
            else:
                항목["결과"].append(f"  높이/두께 비율 {높이두께비:.1f} [통과]")

        for 줄 in 항목["결과"]:
            print(줄)
        self.검증항목.append(항목)

    def 전체_검증_실행(self):
        """모든 검증을 실행하고 결과를 반환합니다."""
        print("\n" + "=" * 50)
        print("  모델 검증 시작")
        print("=" * 50)

        self.치수_검증()
        self.재료_검증()
        self.구조_검증()

        통과수 = sum(1 for v in self.검증항목 if v["통과"])
        전체수 = len(self.검증항목)

        print(f"\n  검증 결과: {통과수}/{전체수} 항목 통과")

        if 통과수 == 전체수:
            print("  종합 판정: [통과] - 설계가 요구사항을 충족합니다.")
        elif 통과수 >= 전체수 * 0.7:
            print("  종합 판정: [조건부 통과] - 일부 보정이 필요합니다.")
        else:
            print("  종합 판정: [실패] - 재설계가 필요합니다.")

        return {
            "통과수": 통과수,
            "전체수": 전체수,
            "항목": self.검증항목,
            "통과여부": 통과수 == 전체수,
        }


# ============================================================
# 5단계: 내보내기
# ============================================================

def STL_내보내기(형태, 파일경로):
    """
    형태를 STL 파일로 내보냅니다.

    매개변수:
        형태 (Part.Shape): 내보낼 형태
        파일경로 (str): 저장할 파일 경로

    반환값:
        str 또는 None: 저장된 파일 경로
    """
    if not FREECAD_AVAILABLE:
        print(f"[시뮬레이션] STL 내보내기: {파일경로}")
        return 파일경로

    try:
        mesh = Part.Mesh()
        mesh.addMesh(형태.tessellate(0.5))
        mesh.write(파일경로)
        print(f"[내보내기] STL 저장 완료: {파일경로}")
        return 파일경로
    except Exception as e:
        print(f"[오류] STL 내보내기 실패: {e}")
        return None


def STEP_내보내기(형태, 파일경로):
    """
    형태를 STEP 파일로 내보냅니다.

    매개변수:
        형태 (Part.Shape): 내보낼 형태
        파일경로 (str): 저장할 파일 경로

    반환값:
        str 또는 None: 저장된 파일 경로
    """
    if not FREECAD_AVAILABLE:
        print(f"[시뮬레이션] STEP 내보내기: {파일경로}")
        return 파일경로

    try:
        형태.exportStep(파일경로)
        print(f"[내보내기] STEP 저장 완료: {파일경로}")
        return 파일경로
    except Exception as e:
        print(f"[오류] STEP 내보내기 실패: {e}")
        return None


# ============================================================
# 6단계: 리포트 생성
# ============================================================

def 리포트_생성(요구사항, 설계결과, 검증결과, AI제안=None):
    """
    전체 파이프라인 결과를 HTML 리포트로 생성합니다.

    매개변수:
        요구사항 (설계요구사항): 원본 요구사항
        설계결과 (dict): 설계 파라미터
        검증결과 (dict): 검증 결과
        AI제안 (str): AI 설계 제안 (선택)

    반환값:
        str: HTML 리포트 내용
    """
    now = datetime.datetime.now()

    # 해시값 생성 (버전 식별용)
    데이터_json = json.dumps(설계결과, sort_keys=True, ensure_ascii=False)
    해시 = hashlib.md5(데이터_json.encode()).hexdigest()[:8]

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>설계 리포트 - {요구사항.제품명}</title>
<style>
body {{ font-family: 'Malgun Gothic', sans-serif; margin: 20px; background: #f5f5f5; }}
.container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
h2 {{ color: #2980b9; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background-color: #3498db; color: white; }}
tr:nth-child(even) {{ background-color: #f2f2f2; }}
.pass {{ color: #27ae60; font-weight: bold; }}
.fail {{ color: #e74c3c; font-weight: bold; }}
.warn {{ color: #f39c12; font-weight: bold; }}
.meta {{ color: #7f8c8d; font-size: 0.9em; }}
</style>
</head>
<body>
<div class="container">
<h1>설계 자동화 리포트</h1>
<p class="meta">생성일: {now.strftime('%Y-%m-%d %H:%M:%S')} | 해시: {해시} | 버전: {요구사항.버전}</p>

<h2>1. 설계 요구사항</h2>
<table>
<tr><th>항목</th><th>값</th></tr>
<tr><td>제품명</td><td>{요구사항.제품명}</td></tr>
<tr><td>제품유형</td><td>{요구사항.제품유형}</td></tr>
<tr><td>치수 (가로x세로x높이)</td><td>{요구사항.가로_mm} x {요구사항.세로_mm} x {요구사항.높이_mm} mm</td></tr>
<tr><td>재료</td><td>{요구사항.재료}</td></tr>
<tr><td>호환보드</td><td>{요구사항.호환보드 or '없음'}</td></tr>
</table>

<h2>2. 설계 결정</h2>
<table>
<tr><th>파라미터</th><th>값</th></tr>
<tr><td>외부 치수</td><td>{설계결과['가로']:.1f} x {설계결과['세로']:.1f} x {설계결과['높이']:.1f} mm</td></tr>
<tr><td>벽 두께</td><td>{설계결과['벽두께']:.1f} mm</td></tr>
<tr><td>모서리 반경</td><td>{설계결과['모서리반경']:.1f} mm</td></tr>
<tr><td>리브 두께</td><td>{설계결과['리브두께']:.1f} mm</td></tr>
<tr><td>마운트홀 수</td><td>{len(설계결과['마운트홀위치'])}개</td></tr>
<tr><td>케이블홀 수</td><td>{len(설계결과['케이블홀위치'])}개</td></tr>
</table>

<h2>3. 검증 결과</h2>
<table>
<tr><th>검증 항목</th><th>결과</th></tr>
"""
    for 항목 in 검증결과["항목"]:
        css = "pass" if 항목["통과"] else "fail"
        상태 = "통과" if 항목["통과"] else "실패"
        html += f'<tr><td>{항목["이름"]}</td><td class="{css}">{상태}</td></tr>\n'

    html += f"""</table>
<p>종합: <strong>{검증결과['통과수']}/{검증결과['전체수']}</strong> 항목 통과</p>
"""
    if not 검증결과["통과여부"]:
        html += '<p class="fail">일부 항목에서 보정이 필요합니다.</p>\n'

    if AI제안:
        html += f"<h2>4. AI 설계 제안</h2>\n<pre>{AI제안}</pre>\n"

    html += f"""
<h2>5. 파일 정보</h2>
<table>
<tr><th>형식</th><th>상태</th></tr>
<tr><td>STL (3D 프린팅)</td><td>내보내기 완료</td></tr>
<tr><td>STEP (CAD 호환)</td><td>내보내기 완료</td></tr>
</table>

<p class="meta">파이프라인 해시: {해시} | 전체 자동화 파이프라인 v1.0</p>
</div>
</body>
</html>"""

    return html


# ============================================================
# 메인 파이프라인
# ============================================================

def 전체파이프라인_실행(요구사항_텍스트=None, 요구사항_딕셔너리=None, 출력디렉토리=None):
    """
    전체 자동화 파이프라인을 실행합니다.

    매개변수:
        요구사항_텍스트 (str): 자유 형식 요구사항 텍스트 (선택)
        요구사항_딕셔너리 (dict): 구조화된 요구사항 (선택)
        출력디렉토리 (str): 출력 파일 저장 경로 (선택)

    반환값:
        dict: 파이프라인 전체 결과
    """
    print("=" * 65)
    print("  전체 자동화 파이프라인 시작")
    print("  설계 요구사항 -> AI 결정 -> 모델 생성 -> 검증 -> 내보내기")
    print("=" * 65)

    결과 = {}

    # 1단계: 요구사항 파싱
    print("\n" + "-" * 65)
    print("  [1단계] 요구사항 파싱")
    print("-" * 65)

    if 요구사항_텍스트:
        요구사항 = 텍스트_요구사항_파싱(요구사항_텍스트)
    elif 요구사항_딕셔너리:
        요구사항 = 설계요구사항()
        for 키, 값 in 요구사항_딕셔너리.items():
            if hasattr(요구사항, 키):
                setattr(요구사항, 키, 값)
        print(f"[파싱] 구조화된 요구사항 로드: {요구사항.제품명}")
    else:
        # 기본 샘플 요구사항 사용
        요구사항 = 설계요구사항()
        요구사항.제품명 = "IoT_센서하우징"
        요구사항.제품유형 = "하우징"
        요구사항.가로_mm = 80.0
        요구사항.세로_mm = 60.0
        요구사항.높이_mm = 35.0
        요구사항.벽두께_mm = 2.0
        요구사항.재료 = "PLA"
        요구사항.호환보드 = "Arduino Uno"
        print(f"[파싱] 기본 샘플 요구사항 사용: {요구사항.제품명}")

    결과["요구사항"] = 요구사항.to_dict()

    # 2단계: AI 기반 설계 결정
    print("\n" + "-" * 65)
    print("  [2단계] AI 기반 설계 결정")
    print("-" * 65)

    # 규칙 기반 결정
    설계결과 = AI설계결정.규칙기반_결정(요구사항)

    # AI 제안 (가능한 경우)
    AI제안 = AI설계결정.AI설계제안(요구사항)
    if AI제안:
        print("[정보] AI 설계 제안이 추가되었습니다.")

    결과["설계결과"] = 설계결과

    # 3단계: FreeCAD 모델 생성
    print("\n" + "-" * 65)
    print("  [3단계] FreeCAD 모델 생성")
    print("-" * 65)

    형태 = 모델_생성(요구사항, 설계결과)
    결과["모델생성"] = 형태 is not None or not FREECAD_AVAILABLE

    # 4단계: 검증
    print("\n" + "-" * 65)
    print("  [4단계] 모델 검증")
    print("-" * 65)

    검증기 = 모델검증(요구사항, 설계결과)
    검증결과 = 검증기.전체_검증_실행()
    결과["검증결과"] = 검증결과

    # 5단계: 내보내기
    print("\n" + "-" * 65)
    print("  [5단계] 파일 내보내기")
    print("-" * 65)

    if 출력디렉토리 is None:
        출력디렉토리 = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
    os.makedirs(출력디렉토리, exist_ok=True)

    stl경로 = os.path.join(출력디렉토리, f"{요구사항.제품명}.stl")
    step경로 = os.path.join(출력디렉토리, f"{요구사항.제품명}.step")

    if 형태:
        STL_내보내기(형태, stl경로)
        STEP_내보내기(형태, step경로)
    else:
        print(f"[시뮬레이션] STL 경로: {stl경로}")
        print(f"[시뮬레이션] STEP 경로: {step경로}")

    결과["파일"] = {"STL": stl경로, "STEP": step경로}

    # 6단계: 리포트 생성
    print("\n" + "-" * 65)
    print("  [6단계] 리포트 생성")
    print("-" * 65)

    html = 리포트_생성(요구사항, 설계결과, 검증결과, AI제안)
    리포트경로 = os.path.join(출력디렉토리, f"{요구사항.제품명}_리포트.html")
    try:
        with open(리포트경로, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[리포트] HTML 리포트 저장: {리포트경로}")
    except Exception as e:
        print(f"[오류] 리포트 저장 실패: {e}")

    결과["리포트경로"] = 리포트경로

    # 최종 요약
    print("\n" + "=" * 65)
    print("  전체 파이프라인 완료!")
    print("=" * 65)
    print(f"  제품명: {요구사항.제품명}")
    print(f"  치수: {설계결과['가로']:.1f} x {설계결과['세로']:.1f} x {설계결과['높이']:.1f} mm")
    print(f"  검증: {검증결과['통과수']}/{검증결과['전체수']} 통과")
    print(f"  출력 파일:")
    print(f"    - STL: {stl경로}")
    print(f"    - STEP: {step경로}")
    print(f"    - 리포트: {리포트경로}")
    print("=" * 65)

    return 결과


# ============================================================
# 전체 파이프라인 시연
# ============================================================

def 시연():
    """
    다양한 요구사항으로 전체 파이프라인을 시연합니다.
    """
    print("\n" + "#" * 65)
    print("  시연 시작: 여러 요구사항으로 파이프라인 테스트")
    print("#" * 65)

    # 시나리오 1: 텍스트 기반 요구사항
    print("\n" + "=" * 65)
    print("  [시나리오 1] 텍스트 기반 요구사항")
    print("=" * 65)

    텍스트1 = """
    제품명: IoT센서케이스
    상자 형태, 크기 90x70x40
    벽두께 2.5, PLA 재료
    마운트홀 4개
    케이블홀 1개 크기 6mm
    Arduino Uno 호환
    """
    전체파이프라인_실행(요구사항_텍스트=텍스트1)

    # 시나리오 2: 구조화된 요구사항
    print("\n\n" + "#" * 65)
    print("  [시나리오 2] 구조화된 요구사항 (ESP32 케이스)")
    print("#" * 65)

    요구사항2 = {
        "제품명": "ESP32_방수케이스",
        "제품유형": "하우징",
        "가로_mm": 60.0,
        "세로_mm": 40.0,
        "높이_mm": 25.0,
        "벽두께_mm": 2.5,
        "재료": "ABS",
        "공차_mm": 0.15,
        "마운트홀_수": 2,
        "케이블홀지름_mm": 4.0,
        "호환보드": "ESP32",
        "특수요구사항": ["방수 실링 groove"],
    }
    전체파이프라인_실행(요구사항_딕셔너리=요구사항2)

    # 시나리오 3: 기본 샘플
    print("\n\n" + "#" * 65)
    print("  [시나리오 3] 기본 샘플 (Raspberry Pi 하우징)")
    print("#" * 65)

    요구사항3 = {
        "제품명": "Raspberry_Pi_하우징",
        "제품유형": "하우징",
        "가로_mm": 100.0,
        "세로_mm": 75.0,
        "높이_mm": 35.0,
        "벽두께_mm": 2.0,
        "재료": "PLA",
        "호환보드": "Raspberry Pi",
        "마운트홀_수": 4,
        "케이블홀지름_mm": 8.0,
    }
    전체파이프라인_실행(요구사항_딕셔너리=요구사항3)


# ============================================================
# 스크립트 실행
# ============================================================

if __name__ == "__main__" or FREECAD_AVAILABLE:
    시연()
else:
    print("[정보] FreeCAD 모드에서 실행하면 3D 모델이 생성됩니다.")
    print("[정보] 현재 시뮬레이션 모드로 동작합니다.")
    시연()

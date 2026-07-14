# -*- coding: utf-8 -*-
"""
부품 카탈로그 자동 생성 매크로

실행 방법:
    FreeCAD에서 이 파일을 열고: 매크로 > 매크로 실행(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\13_part_catalog.py").read())

설명:
    부품 디렉토리를 스캔하여 각 .FCStd 파일의 정보를 추출하고,
    파일명, 치수, 재료, 설명 등을 CSV 카탈로그로 자동 생성합니다.

사용법:
    1. 아래 변수들에 원하는 경로를 설정하세요.
    2. FreeCAD에서 이 매크로를 실행합니다.
    3. 지정된 출력 경로에 CSV 카탈로그가 생성됩니다.
"""

import os
import sys
import csv
import time
import datetime
import FreeCAD

# ======================== 사용자 설정 ========================
# 부품 파일이 있는 루트 디렉토리 경로
부품_디렉토리 = r"C:\Users\Administrator\Downloads\py\fcstd"

# 카탈로그 CSV 출력 경로
카탈로그_출력_경로 = r"C:\Users\Administrator\Downloads\py\catalog\부품_카탈로그.csv"

# 검색할 파일 확장자
파일_확장자 = ".FCStd"

# 하위 디렉토리 포함 여부
하위_디렉토리_포함 = True

# CSV 구분자 (콤마, 세미콜론 등)
CSV_구분자 = ","

# CSV 인코딩
CSV_인코딩 = "utf-8-sig"  # 한글 엑셀 호환

# 기본 재료명 매핑 (파일명에 포함된 키워드로 추정)
재료_매핑 = {
    "steel": "강재",
    "aluminum": "알루미늄",
    "aluminium": "알루미늄",
    "plastic": "플라스틱",
    "rubber": "고무",
    "copper": "구리",
    "brass": "황동",
    "stainless": "스테인리스강",
    "wood": "목재",
    "titanium": "티타늄",
    "nylon": "나일론",
    "glass": "유리",
    "carbon": "카본",
    "ceramic": "세라믹",
}

# =============================================================


def 디렉토리_존재_확인(경로):
    """지정된 디렉토리가 존재하는지 확인하고, 없으면 생성합니다."""
    if not os.path.isdir(경로):
        try:
            os.makedirs(경로)
            print("[정보] 디렉토리를 생성했습니다: {}".format(경로))
            return True
        except OSError as 오류:
            print("[오류] 디렉토리를 생성할 수 없습니다: {} - {}".format(경로, 오류))
            return False
    return True


def fcstd_파일_검색(루트_경로, 하위_포함=True):
    """
    지정된 디렉토리에서 .FCStd 파일 목록을 검색합니다.

    Args:
        루트_경로: 검색할 시작 디렉토리
        하위_포함: 하위 디렉토리 포함 여부

    Returns:
        찾은 .FCStd 파일의 전체 경로 리스트
    """
    찾은_파일들 = []

    if 하위_포함:
        for 디렉토리_경로, 하위_디렉토리들, 파일_이름들 in os.walk(루트_경로):
            for 파일_이름 in 파일_이름들:
                if 파일_이름.lower().endswith(파일_확장자.lower()):
                    전체_경로 = os.path.join(디렉토리_경로, 파일_이름)
                    찾은_파일들.append(전체_경로)
    else:
        if os.path.isdir(루트_경로):
            for 파일_이름 in os.listdir(루트_경로):
                if 파일_이름.lower().endswith(파일_확장자.lower()):
                    전체_경로 = os.path.join(루트_경로, 파일_이름)
                    찾은_파일들.append(전체_경로)

    return 찾은_파일들


def 파일명에서_재료_추출(파일명):
    """
    파일명에서 재료 키워드를 추출합니다.

    Args:
        파일명: 확인할 파일 이름

    Returns:
        추정 재료명 (한국어)
    """
    파일명_소문자 = 파일명.lower()

    for 키워드, 재료명 in 재료_매핑.items():
        if 키워드 in 파일명_소문자:
            return 재료명

    return "미지정"


def 파일명에서_설명_추출(파일명):
    """
    파일명에서 부품 설명을 추출합니다.
    예: "bracket_v2.FCStd" -> "Bracket V2"

    Args:
        파일명: 확인할 파일 이름

    Returns:
        추출된 설명 문자열
    """
    # 확장자 제거
    이름 = os.path.splitext(파일명)[0]

    # 언더스코어를 공백으로 변환
    이름 = 이름.replace("_", " ")

    # 각 단어의 첫 글자를 대문자로
    설명 = " ".join(단어.capitalize() for 단어 in 이름.split())

    return 설명


def 파일명에서_부품번호_추출(파일명):
    """
    파일명에서 부품번호 패턴을 추출합니다.
    예: "A001_bolt.FCStd" -> "A001"

    Args:
        파일명: 확인할 파일 이름

    Returns:
        추출된 부품번호 또는 빈 문자열
    """
    import re

    이름 = os.path.splitext(파일명)[0]

    # 접두사-숫자 패턴 매칭 (예: A001, P-123, Part_001)
    패턴 = r'^([A-Za-z]+[-_]?\d+)'
    매칭 = re.match(패턴, 이름)

    if 매칭:
        return 매칭.group(1)

    # 숫자만 있는 경우
    숫자_패턴 = r'^(\d+)'
    숫자_매칭 = re.match(숫자_패턴, 이름)

    if 숫자_매칭:
        return 숫자_매칭.group(1)

    return ""


def 문서_정보_추출(파일_경로):
    """
    .FCStd 파일에서 FreeCAD 문서 정보를 추출합니다.

    Args:
        파일_경로: .FCStd 파일 경로

    Returns:
        딕셔너리: {
            "객체_수": int,
            "바운딩박스": dict,
            "부피": float,
            "표면적": float,
            "객체_이름들": list
        }
    """
    문서 = None
    정보 = {
        "객체_수": 0,
        "바운딩박스": {"너비": 0, "높이": 0, "깊이": 0},
        "부피": 0.0,
        "표면적": 0.0,
        "객체_이름들": []
    }

    try:
        문서 = FreeCAD.open(파일_경로)

        if 문서 is None:
            return 정보

        객체_목록 = list(문서.Objects)
        정보["객체_수"] = len(객체_목록)

        # 전체 바운딩 박스 계산
        전체_바운딩박스 = None
        총_부피 = 0.0
        총_표면적 = 0.0

        for 객체 in 객체_목록:
            try:
                if hasattr(객체, 'Shape') and 객체.Shape is not None:
                    형상 = 객체.Shape

                    # 바운딩 박스 업데이트
                    if 전체_바운딩박스 is None:
                        전체_바운딩박스 = 형상.BoundBox
                    else:
                        전체_바운딩박스 = 전체_바운딩박스.united(형상.BoundBox)

                    # 부피 및 표면적 누적
                    총_부피 += 형상.Volume
                    총_표면적 += 형상.Area

                    # 객체 이름 수집
                    정보["객체_이름들"].append(객체.Name)
            except:
                continue

        # 바운딩 박스 정보 저장
        if 전체_바운딩박스 is not None:
            정보["바운딩박스"] = {
                "너비": 전체_바운딩박스.XLength,
                "높이": 전체_바운딩박스.YLength,
                "깊이": 전체_바운딩박스.ZLength
            }

        정보["부피"] = 총_부피
        정보["표면적"] = 총_표면적

        # 문서 닫기
        FreeCAD.closeDocument(문서.Name)

    except Exception as 오류:
        print("  [경고] 정보 추출 실패 ({}): {}".format(파일_경로, 오류))
        if 문서 is not None:
            try:
                FreeCAD.closeDocument(문서.Name)
            except:
                pass

    return 정보


def 카탈로그_생성(카탈로그_데이터, 출력_경로):
    """
    카탈로그 데이터를 CSV 파일로 저장합니다.

    Args:
        카탈로그_데이터: 각 행의 데이터 리스트
        출력_경로: CSV 파일 출력 경로
    """

    # 헤더 정의
    헤더 = [
        "번호",
        "파일명",
        "부품번호",
        "설명",
        "재료",
        "객체 수",
        "너비 (mm)",
        "높이 (mm)",
        "깊이 (mm)",
        "부피 (mm³)",
        "표면적 (mm²)",
        "파일 크기 (KB)",
        "변경일",
        "상대 경로"
    ]

    try:
        with open(출력_경로, 'w', newline='', encoding=CSV_인코딩) as CSV_파일:
            작성기 = csv.writer(CSV_파일, delimiter=CSV_구분자)

            # 헤더 작성
            작성기.writerow(헤더)

            # 데이터 작성
            for 번호, 행_데이터 in enumerate(카탈로그_데이터, 1):
                행_데이터["번호"] = 번호
                작성기.writerow([
                    행_데이터["번호"],
                    행_데이터["파일명"],
                    행_데이터["부품번호"],
                    행_데이터["설명"],
                    행_데이터["재료"],
                    행_데이터["객체_수"],
                    "{:.2f}".format(행_데이터["너비"]),
                    "{:.2f}".format(행_데이터["높이"]),
                    "{:.2f}".format(행_데이터["깊이"]),
                    "{:.2f}".format(행_데이터["부피"]),
                    "{:.2f}".format(행_데이터["표면적"]),
                    "{:.1f}".format(행_데이터["파일_크기"]),
                    행_데이터["변경일"],
                    행_데이터["상대_경로"]
                ])

        return True

    except Exception as 오류:
        print("[오류] CSV 파일 저장 실패: {}".format(오류))
        return False


def 부품_카탈로그_생성_실행():
    """부품 카탈로그 자동 생성의 전체 프로세스를 실행합니다."""

    print("=" * 65)
    print("  부품 카탈로그 자동 생성 시작")
    print("=" * 65)
    print("  부품 디렉토리 : {}".format(부품_디렉토리))
    print("  출력 경로     : {}".format(카탈로그_출력_경로))
    print("  하위 디렉토리 : {}".format("포함" if 하위_디렉토리_포함 else "미포함"))
    print("-" * 65)

    # 디렉토리 존재 확인
    if not os.path.isdir(부품_디렉토리):
        print("[실패] 부품 디렉토리가 없습니다. 경로를 확인하세요.")
        return

    # 출력 디렉토리 생성
    출력_디렉토리 = os.path.dirname(카탈로그_출력_경로)
    디렉토리_존재_확인(출력_디렉토리)

    # .FCStd 파일 검색
    print("\n[1단계] 부품 파일 검색 중...")
    찾은_파일들 = fcstd_파일_검색(부품_디렉토리, 하위_디렉토리_포함)
    전체_파일_수 = len(찾은_파일들)

    if 전체_파일_수 == 0:
        print("[정보] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 부품 파일을 찾았습니다.".format(전체_파일_수))

    # 부품 정보 수집
    print("\n[2단계] 부품 정보 수집 중...")
    시작_시간 = time.time()
    카탈로그_데이터 = []
    성공_수 = 0
    실패_수 = 0

    for 순번, 파일_경로 in enumerate(찾은_파일들, 1):
        진행률 = (순번 / 전체_파일_수) * 100
        파일명 = os.path.basename(파일_경로)
        상대_경로 = os.path.relpath(파일_경로, 부품_디렉토리)

        print("  [{:5.1f}%] ({}/{}) 정보 수집: {}".format(
            진행률, 순번, 전체_파일_수, 상대_경로))

        try:
            # 파일 크기 및 수정 시간
            파일_정보 = os.stat(파일_경로)
            파일_크기 = 파일_정보.st_size / 1024.0  # KB
            수정_시간 = datetime.datetime.fromtimestamp(파일_정보.st_mtime)
            수정_일자 = 수정_시간.strftime("%Y-%m-%d %H:%M")

            # FreeCAD 문서 정보 추출
            문서_정보 = 문서_정보_추출(파일_경로)

            # 부품 정보 구성
            부품_정보 = {
                "번호": 0,
                "파일명": 파일명,
                "부품번호": 파일명에서_부품번호_추출(파일명),
                "설명": 파일명에서_설명_추출(파일명),
                "재료": 파일명에서_재료_추출(파일명),
                "객체_수": 문서_정보["객체_수"],
                "너비": 문서_정보["바운딩박스"]["너비"],
                "높이": 문서_정보["바운딩박스"]["높이"],
                "깊이": 문서_정보["바운딩박스"]["깊이"],
                "부피": 문서_정보["부피"],
                "표면적": 문서_정보["표면적"],
                "파일_크기": 파일_크기,
                "변경일": 수정_일자,
                "상대_경로": 상대_경로
            }

            카탈로그_데이터.append(부품_정보)
            성공_수 += 1

            print("    -> 객체: {}, 크기: {:.0f}x{:.0f}x{:.0f}mm".format(
                문서_정보["객체_수"],
                문서_정보["바운딩박스"]["너비"],
                문서_정보["바운딩박스"]["높이"],
                문서_정보["바운딩박스"]["깊이"]
            ))

        except Exception as 수집_오류:
            print("    [오류] 정보 수집 실패: {}".format(수집_오류))
            실패_수 += 1

    # CSV 카탈로그 생성
    print("\n[3단계] CSV 카탈로그 파일 생성 중...")
    if 카탈로그_생성(카탈로그_데이터, 카탈로그_출력_경로):
        print("  -> 카탈로그 파일 생성 완료: {}".format(카탈로그_출력_경로))
    else:
        print("  -> 카탈로그 파일 생성 실패!")
        return

    # 결과 요약
    종료_시간 = time.time()
    총_소요_시간 = 종료_시간 - 시작_시간

    print("\n" + "=" * 65)
    print("  부품 카탈로그 생성 완료")
    print("=" * 65)
    print("  총 파일 수    : {}".format(전체_파일_수))
    print("  성공          : {}".format(성공_수))
    print("  실패          : {}".format(실패_수))
    print("  총 소요 시간  : {:.2f}초".format(총_소요_시간))
    print("  출력 파일     : {}".format(카탈로그_출력_경로))
    print("=" * 65)

    # 통계 출력
    if 카탈로그_데이터:
        print("\n[부품 통계]")
        부피_합계 = sum(데이터["부피"] for 데이터 in 카탈로그_데이터)
        표면적_합계 = sum(데이터["표면적"] for 데이터 in 카탈로그_데이터)
        평균_객체수 = sum(데이터["객체_수"] for 데이터 in 카탈로그_데이터) / len(카탈로그_데이터)
        print("  총 부피       : {:,.2f} mm³".format(부피_합계))
        print("  총 표면적     : {:,.2f} mm²".format(표면적_합계))
        print("  평균 객체 수  : {:.1f}".format(평균_객체수))


# ======================== 실행 ========================
if __name__ == "__main__":
    부품_카탈로그_생성_실행()
else:
    # FreeCAD에서 직접 실행할 때
    부품_카탈로그_생성_실행()

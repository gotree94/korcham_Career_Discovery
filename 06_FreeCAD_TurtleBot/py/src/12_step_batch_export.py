# -*- coding: utf-8 -*-
"""
STEP 일괄 변환 매크로

실행 방법:
    FreeCAD에서 이 파일을 열고: 매크로 > 매크로 실행(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\12_step_batch_export.py").read())

설명:
    지정된 디렉토리(및 하위 디렉토리)의 모든 .FCStd 파일을 찾아
    STEP (ISO 10303) 포맷으로 일괄 변환합니다.

사용법:
    1. 아래 변수들에 원하는 경로를 설정하세요.
    2. FreeCAD에서 이 매크로를 실행합니다.
    3. 변환 결과가 콘솔에 출력됩니다.
"""

import os
import sys
import time
import FreeCAD
import Import
import Part

# ======================== 사용자 설정 ========================
# 검색할 루트 디렉토리 경로
입력_디렉토리 = r"C:\Users\Administrator\Downloads\py\fcstd"

# STEP 파일을 저장할 출력 디렉토리 경로
출력_디렉토리 = r"C:\Users\Administrator\Downloads\py\step"

# 변환할 파일 확장자
입력_확장자 = ".FCStd"

# 출력 파일 확장자
출력_확장자 = ".step"

# 하위 디렉토리 포함 여부
하위_디렉토리_포함 = True

# STEP 내보내기 스키마 (AP203 또는 AP214)
# AP203: 3D 설계 (기본값)
# AP214: 자동차/항공우주 (컬러 지원)
# AP242: 최신 표준 (리핑 지원)
STEP_스키마 = "AP203"

# 색상 정보 포함 여부 (AP214에서만 유효)
색상_정보_포함 = True

# 로고/문서 정보 포함 여부
문서_정보_포함 = True
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
                if 파일_이름.lower().endswith(입력_확장자.lower()):
                    전체_경로 = os.path.join(디렉토리_경로, 파일_이름)
                    찾은_파일들.append(전체_경로)
    else:
        if os.path.isdir(루트_경로):
            for 파일_이름 in os.listdir(루트_경로):
                if 파일_이름.lower().endswith(입력_확장자.lower()):
                    전체_경로 = os.path.join(루트_경로, 파일_이름)
                    찾은_파일들.append(전체_경로)

    return 찾은_파일들


def 스키마_변환(스키마_문자열):
    """
    사용자 친화적 스키마 이름을 STEP 스키마 식별자로 변환합니다.

    Args:
        스키마_문자열: "AP203", "AP214", "AP242" 등

    Returns:
        Import 모듈에서 사용하는 스키마 딕셔너리
    """
    스키마_맵 = {
        "AP203": {"AP203": True},
        "AP214": {"AP214": True},
        "AP242": {"AP242": True},
    }

    if 스키마_문자열 in 스키마_맵:
        return 스키마_맵[스키마_문자열]
    else:
        print("  [경고] 알 수 없는 스키마: {} (AP203 사용)".format(스키마_문자열))
        return {"AP203": True}


def 단일_파일_step_변환(입력_경로, 출력_경로):
    """
    하나의 .FCStd 파일을 STEP로 변환합니다.

    Args:
        입력_경로: 원본 .FCStd 파일 경로
        출력_경로: 출력 .step 파일 경로

    Returns:
        (성공_여부, 객체_수, 형상_수) 튜플
    """
    문서 = None

    try:
        # FreeCAD 문서 열기
        문서 = FreeCAD.open(입력_경로)

        if 문서 is None:
            print("  [경고] 문서를 열 수 없습니다: {}".format(입력_경로))
            return False, 0, 0

        # 활성 문서의 모든 객체를 가져옵니다
        객체_목록 = list(문서.Objects)

        if not 객체_목록:
            print("  [경고] 문서에 객체가 없습니다: {}".format(입력_경로))
            FreeCAD.closeDocument(문서.Name)
            return False, 0, 0

        # STEP로 내보낼 형상 수집
        내보낼_형상들 = []
        for 객체 in 객체_목록:
            try:
                if hasattr(객체, 'Shape') and 객체.Shape is not None:
                    형상 = 객체.Shape
                    # 유효한 형상인지 확인
                    if 형상.Volume > 0 or 형상.Area > 0:
                        내보낼_형상들.append(형상)
            except Exception as 형상_오류:
                print("  [경고] 객체 형상 수집 실패 ({}): {}".format(
                    객체.Name, 형상_오류))
                continue

        if not 내보낼_형상들:
            print("  [경고] 내보낼 유효한 형상이 없습니다: {}".format(입력_경로))
            FreeCAD.closeDocument(문서.Name)
            return False, 0, 0

        # 형상 병합 시도 (하나의 STEP 파일로 내보내기)
        if len(내보낼_형상들) > 1:
            try:
                병합된_형상 = Part.makeCompound(내보낼_형상들)
                내보낼_형상들 = [병합된_형상]
            except:
                # 병합 실패 시 개별 형상으로 내보내기
                pass

        # STEP 내보내기 옵션 설정
        내보내기_옵션 = {}

        # 색상 정보 포함
        if 색상_정보_포함 and STEP_스키마 in ["AP214", "AP242"]:
            내보내기_옵션['ColorMode'] = True
        else:
            내보내기_옵션['ColorMode'] = False

        # 문서 정보 포함 여부
        if 문서_정보_포함:
            내보내기_옵션['DocumentName'] = True
        else:
            내보내기_옵션['DocumentName'] = False

        # STEP 파일로 내보내기
        Import.export(내보낼_형상들, 출력_경로)

        # 형상 수와 객체 수 반환
        총_형상_수 = len(내보낼_형상들)

        # 문서 닫기
        FreeCAD.closeDocument(문서.Name)

        return True, len(객체_목록), 총_형상_수

    except Exception as 전체_오류:
        print("  [오류] STEP 변환 중 오류 발생 ({}): {}".format(
            입력_경로, 전체_오류))
        if 문서 is not None:
            try:
                FreeCAD.closeDocument(문서.Name)
            except:
                pass
        return False, 0, 0


def STEP_일괄_변환_실행():
    """STEP 일괄 변환의 전체 프로세스를 실행합니다."""

    print("=" * 65)
    print("  STEP 일괄 변환 시작")
    print("=" * 65)
    print("  입력 디렉토리 : {}".format(입력_디렉토리))
    print("  출력 디렉토리 : {}".format(출력_디렉토리))
    print("  STEP 스키마   : {}".format(STEP_스키마))
    print("  색상 정보     : {}".format("포함" if 색상_정보_포함 else "미포함"))
    print("  문서 정보     : {}".format("포함" if 문서_정보_포함 else "미포함"))
    print("-" * 65)

    # 디렉토리 존재 확인
    if not 디렉토리_존재_확인(입력_디렉토리):
        print("[실패] 입력 디렉토리가 없습니다. 경로를 확인하세요.")
        return

    디렉토리_존재_확인(출력_디렉토리)

    # .FCStd 파일 검색
    print("\n[1단계] .FCStd 파일 검색 중...")
    찾은_파일들 = fcstd_파일_검색(입력_디렉토리, 하위_디렉토리_포함)
    전체_파일_수 = len(찾은_파일들)

    if 전체_파일_수 == 0:
        print("[정보] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 파일을 찾았습니다.".format(전체_파일_수))

    # STEP 스키마 확인
    print("\n[2단계] STEP 변환 설정 확인...")
    print("  -> 적용 스키마: {}".format(STEP_스키마))

    # 일괄 변환 실행
    print("\n[3단계] STEP 변환 시작...")
    시작_시간 = time.time()
    성공_수 = 0
    실패_수 = 0
    건너뜀_수 = 0
    총_객체_수 = 0

    for 순번, 입력_파일_경로 in enumerate(찾은_파일들, 1):
        # 진행률 계산
        진행률 = (순번 / 전체_파일_수) * 100

        # 출력 파일 경로 계산 (상대 경로 유지)
        상대_경로 = os.path.relpath(입력_파일_경로, 입력_디렉토리)
        출력_파일_이름 = os.path.splitext(상대_경로)[0] + 출력_확장자
        출력_파일_경로 = os.path.join(출력_디렉토리, 출력_파일_이름)

        # 출력 디렉토리 생성
        출력_하위 = os.path.dirname(출력_파일_경로)
        디렉토리_존재_확인(출력_하위)

        # 이미 출력 파일이 존재하는지 확인
        if os.path.exists(출력_파일_경로):
            print("  [{:5.1f}%] ({}/{}) 건너뜀 (이미 존재): {}".format(
                진행률, 순번, 전체_파일_수, 상대_경로))
            건너뜀_수 += 1
            continue

        print("  [{:5.1f}%] ({}/{}) 변환 중: {}".format(
            진행률, 순번, 전체_파일_수, 상대_경로))

        # STEP 변환 실행
        파일_시작 = time.time()
        결과, 객체_수, 형상_수 = 단일_파일_step_변환(
            입력_파일_경로, 출력_파일_경로
        )
        파일_소요 = time.time() - 파일_시작

        if 결과:
            성공_수 += 1
            총_객체_수 += 객체_수
            # 파일 크기 표시
            파일_크기 = os.path.getsize(출력_파일_경로)
            print("    -> 완료 (객체: {}, 형상: {}, {:.1f}KB, {:.2f}초)".format(
                객체_수, 형상_수, 파일_크기 / 1024.0, 파일_소요))
        else:
            실패_수 += 1

    # 결과 요약
    종료_시간 = time.time()
    총_소요_시간 = 종료_시간 - 시작_시간

    print("\n" + "=" * 65)
    print("  STEP 일괄 변환 완료")
    print("=" * 65)
    print("  총 파일 수    : {}".format(전체_파일_수))
    print("  성공          : {}".format(성공_수))
    print("  실패          : {}".format(실패_수))
    print("  건너뜀        : {}".format(건너뜀_수))
    print("  총 객체 수    : {}".format(총_객체_수))
    print("  총 소요 시간  : {:.2f}초".format(총_소요_시간))
    if 성공_수 > 0:
        print("  평균 변환 시간: {:.2f}초/파일".format(총_소요_시간 / 성공_수))
    print("=" * 65)


# ======================== 실행 ========================
if __name__ == "__main__":
    STEP_일괄_변환_실행()
else:
    # FreeCAD에서 직접 실행할 때
    STEP_일괄_변환_실행()

# -*- coding: utf-8 -*-
"""
STL 일괄 내보내기 매크로

실행 방법:
    FreeCAD에서 이 파일을 열고: 매크로 > 매크로 실행(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\11_stl_batch_export.py").read())

설명:
    지정된 디렉토리(및 하위 디렉토리)의 모든 .FCStd 파일을 찾아
    STL 포맷으로 일괄 변환합니다.

사용법:
    1. 아래 변수들에 원하는 경로를 설정하세요.
    2. FreeCAD에서 이 매크로를 실행합니다.
    3. 변환 결과가 콘솔에 출력됩니다.
"""

import os
import sys
import time
import FreeCAD
import Mesh

# ======================== 사용자 설정 ========================
# 검색할 루트 디렉토리 경로 (변경하여 사용하세요)
입력_디렉토리 = r"C:\Users\Administrator\Downloads\py\fcstd"

# STL 파일을 저장할 출력 디렉토리 경로
출력_디렉토리 = r"C:\Users\Administrator\Downloads\py\stl"

# 변환할 파일 확장자
입력_확장자 = ".FCStd"

# 출력 파일 확장자
출력_확장자 = ".stl"

# 하위 디렉토리 포함 여부
하위_디렉토리_포함 = True

# STL 메시지 품질 (olerance, 낮을수록 정밀)
최대_편차 = 0.1  # 최대 허용 편차 (mm)
세밀_모드 = False  # True로 설정하면 더 정밀한 메시 생성
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


def 단일_파일_stl_변환(입력_경로, 출력_경로):
    """
    하나의 .FCStd 파일을 STL로 변환합니다.

    Args:
        입력_경로: 원본 .FCStd 파일 경로
        출력_경로: 출력 .stl 파일 경로

    Returns:
        성공 여부 (True/False)
    """
    try:
        # FreeCAD 문서 열기
        문서 = FreeCAD.open(입력_경로)

        if 문서 is None:
            print("  [경고] 문서를 열 수 없습니다: {}".format(입력_경로))
            return False

        # 활성 문서의 모든 객체(파트)를 가져옵니다
        객체_목록 = list(문서.Objects)

        if not 객체_목록:
            print("  [경고] 문서에 객체가 없습니다: {}".format(입력_경로))
            FreeCAD.closeDocument(문서.Name)
            return False

        # 메시 객체 생성
        메시_객체 = Mesh.Mesh()

        # 모든 파트의 형상을 메시로 변환
        for 객체 in 객체_목록:
            try:
                형상 = 객체.Shape
                if 형상 is not None:
                    # 형상을 메시로 변환하여 추가
                    부분_메시 = Mesh.Mesh( 형상.tessellate(최대_편차) )
                    메시_객체.addMesh(부분_메시)
            except Exception as 형상_오류:
                print("  [경고] 객체 변환 실패 ({}): {}".format(
                    객체.Name, 형상_오류))
                continue

        # 메시에 면이 없는 경우 (변환 실패)
        if 메시_객체.CountFaces == 0:
            print("  [경고] 변환된 메시가 비어 있습니다: {}".format(입력_경로))
            FreeCAD.closeDocument(문서.Name)
            return False

        # STL 파일로 내보내기
        메시_객체.write(출력_경로)

        # 문서 닫기 (변경 사항 저장 안 함)
        FreeCAD.closeDocument(문서.Name)

        return True

    except Exception as 전체_오류:
        print("  [오류] 변환 중 오류 발생 ({}): {}".format(
            입력_경로, 전체_오류))
        try:
            FreeCAD.closeDocument(문서.Name)
        except:
            pass
        return False


def STL_일괄_변환_실행():
    """STL 일괄 변환의 전체 프로세스를 실행합니다."""

    print("=" * 60)
    print("  STL 일괄 내보내기 시작")
    print("=" * 60)
    print("  입력 디렉토리 : {}".format(입력_디렉토리))
    print("  출력 디렉토리 : {}".format(출력_디렉토리))
    print("  하위 디렉토리 : {}".format("포함" if 하위_디렉토리_포함 else "미포함"))
    print("-" * 60)

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

    # 일괄 변환 실행
    print("\n[2단계] STL 변환 시작...")
    시작_시간 = time.time()
    성공_수 = 0
    실패_수 = 0
    건너뜀_수 = 0

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

        # STL 변환 실행
        파일_시작 = time.time()
        결과 = 단일_파일_stl_변환(입력_파일_경로, 출력_파일_경로)
        파일_소요 = time.time() - 파일_시작

        if 결과:
            성공_수 += 1
            # 파일 크기 표시
            파일_크기 = os.path.getsize(출력_파일_경로)
            print("    -> 완료 ({:.1f}KB, {:.2f}초)".format(
                파일_크기 / 1024.0, 파일_소요))
        else:
            실패_수 += 1

    # 결과 요약
    종료_시간 = time.time()
    총_소요_시간 = 종료_시간 - 시작_시간

    print("\n" + "=" * 60)
    print("  STL 일괄 내보내기 완료")
    print("=" * 60)
    print("  총 파일 수    : {}".format(전체_파일_수))
    print("  성공          : {}".format(성공_수))
    print("  실패          : {}".format(실패_수))
    print("  건너뜀        : {}".format(건너뜀_수))
    print("  총 소요 시간  : {:.2f}초".format(총_소요_시간))
    if 성공_수 > 0:
        print("  평균 변환 시간: {:.2f}초/파일".format(총_소요_시간 / 성공_수))
    print("=" * 60)


# ======================== 실행 ========================
if __name__ == "__main__":
    STL_일괄_변환_실행()
else:
    # FreeCAD에서 직접 실행할 때
    STL_일괄_변환_실행()

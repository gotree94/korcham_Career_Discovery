# -*- coding: utf-8 -*-
"""
STL 일괄 내보내기 매크로

실row_val 방법:
    FreeCAD에서 이 파일을 col_data고: 매크로 > 매크로 실row_val(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\11_stl_batch_export.py").read())

description:
    지정된 디렉토리(및 sub 디렉토리)의 모든 .FCStd 파일을 찾아
    STL 포맷으로 일괄 변환합니다.

사용법:
    1. 아래 변수들에 원하는 path를 설정하세요.
    2. FreeCAD에서 이 매크로를 실row_val합니다.
    3. 변환 result가 콘솔에 출력됩니다.
"""

import os
import sys
import time
import FreeCAD
import Mesh

# ======================== 사용자 설정 ========================
# 검색할 루트 디렉토리 path (변경하여 사용하세요)
input_dir = r"C:\Users\Administrator\Downloads\py\fcstd"

# STL 파일을 저장할 출력 디렉토리 path
output_dir = r"C:\Users\Administrator\Downloads\py\stl"

# 변환할 파일 확장자
input_ext = ".FCStd"

# 출력 파일 확장자
output_ext = ".stl"

# sub 디렉토리 포함 여부
include_subdirs = True

# STL message 품질 (olerance, 낮을수록 정밀)
max_tolerance = 0.1  # 최대 허용 편차 (mm)
fine_mode = False  # True로 설정하면 더 정밀한 메시 생성
# =============================================================


def check_directory_exists(path):
    """지정된 디렉토리가 존재하는지 check하고, 없으면 생성합니다."""
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
            print("[info_val] 디렉토리를 생성했습니다: {}".format(path))
            return True
        except OSError as error:
            print("[error] 디렉토리를 생성할 수 없습니다: {} - {}".format(path, error))
            return False
    return True


def search_fcstd_files(root_path, include_sub=True):
    """
    지정된 디렉토리에서 .FCStd 파일 목록을 검색합니다.

    Args:
        root_path: 검색할 start 디렉토리
        include_sub: sub 디렉토리 포함 여부

    Returns:
        찾은 .FCStd 파일의 combined path 리스트
    """
    found_files = []

    if include_sub:
        for dir_path, subdirs, filenames in os.walk(root_path):
            for filename in filenames:
                if filename.lower().endswith(input_ext.lower()):
                    full_path = os.path.join(dir_path, filename)
                    found_files.append(full_path)
    else:
        if os.path.isdir(root_path):
            for filename in os.listdir(root_path):
                if filename.lower().endswith(input_ext.lower()):
                    full_path = os.path.join(root_path, filename)
                    found_files.append(full_path)

    return found_files


def convert_single_file_to_stl(input_path, output_path):
    """
    하나의 .FCStd 파일을 STL로 변환합니다.

    Args:
        input_path: 원본 .FCStd 파일 path
        output_path: 출력 .stl 파일 path

    Returns:
        성공 여부 (True/False)
    """
    try:
        # FreeCAD doc col_data기
        doc = FreeCAD.open(input_path)

        if doc is None:
            print("  [경고] doc를 col_data 수 없습니다: {}".format(input_path))
            return False

        # 활성 doc의 모든 obj(파트)를 가져옵니다
        objects_list = list(doc.Objects)

        if not objects_list:
            print("  [경고] doc에 obj가 없습니다: {}".format(input_path))
            FreeCAD.closeDocument(doc.Name)
            return False

        # 메시 obj 생성
        mesh_obj = Mesh.Mesh()

        # 모든 파트의 shape을 메시로 변환
        for obj in objects_list:
            try:
                shape = obj.Shape
                if shape is not None:
                    # shape을 메시로 변환하여 추가
                    partial_mesh = Mesh.Mesh( shape.tessellate(max_tolerance) )
                    mesh_obj.addMesh(partial_mesh)
            except Exception as shape_error:
                print("  [경고] obj 변환 FAIL ({}): {}".format(
                    obj.Name, shape_error))
                continue

        # 메시에 면이 없는 경우 (변환 FAIL)
        if mesh_obj.CountFaces == 0:
            print("  [경고] 변환된 메시가 비어 있습니다: {}".format(input_path))
            FreeCAD.closeDocument(doc.Name)
            return False

        # STL 파일로 내보내기
        mesh_obj.write(output_path)

        # doc 닫기 (변경 사항 저장 안 함)
        FreeCAD.closeDocument(doc.Name)

        return True

    except Exception as overall_error:
        print("  [error] 변환 중 error 발생 ({}): {}".format(
            input_path, overall_error))
        try:
            FreeCAD.closeDocument(doc.Name)
        except:
            pass
        return False


def run_stl_batch_conversion():
    """STL 일괄 변환의 combined 프로세스를 실row_val합니다."""

    print("=" * 60)
    print("  STL 일괄 내보내기 start")
    print("=" * 60)
    print("  입력 디렉토리 : {}".format(input_dir))
    print("  출력 디렉토리 : {}".format(output_dir))
    print("  sub 디렉토리 : {}".format("포함" if include_subdirs else "미포함"))
    print("-" * 60)

    # 디렉토리 존재 check
    if not check_directory_exists(input_dir):
        print("[FAIL] 입력 디렉토리가 없습니다. path를 check하세요.")
        return

    check_directory_exists(output_dir)

    # .FCStd 파일 검색
    print("\n[1단계] .FCStd 파일 검색 중...")
    found_files = search_fcstd_files(input_dir, include_subdirs)
    total_files = len(found_files)

    if total_files == 0:
        print("[info_val] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 파일을 찾았습니다.".format(total_files))

    # 일괄 변환 실row_val
    print("\n[2단계] STL 변환 start...")
    start_time = time.time()
    success_count = 0
    fail_count = 0
    skip_count = 0

    for index, input_file_path in enumerate(found_files, 1):
        # progress 계산
        progress = (index / total_files) * 100

        # 출력 파일 path 계산 (상대 path 유지)
        rel_path = os.path.relpath(input_file_path, input_dir)
        output_filename = os.path.splitext(rel_path)[0] + output_ext
        output_file_path = os.path.join(output_dir, output_filename)

        # 출력 디렉토리 생성
        output_sub = os.path.dirname(output_file_path)
        check_directory_exists(output_sub)

        # 이미 출력 파일이 존재하는지 check
        if os.path.exists(output_file_path):
            print("  [{:5.1f}%] ({}/{}) 건너뜀 (이미 존재): {}".format(
                progress, index, total_files, rel_path))
            skip_count += 1
            continue

        print("  [{:5.1f}%] ({}/{}) 변환 중: {}".format(
            progress, index, total_files, rel_path))

        # STL 변환 실row_val
        file_start = time.time()
        result = convert_single_file_to_stl(input_file_path, output_file_path)
        file_elapsed = time.time() - file_start

        if result:
            success_count += 1
            # 파일 size 표시
            file_size = os.path.getsize(output_file_path)
            print("    -> 완료 ({:.1f}KB, {:.2f}초)".format(
                file_size / 1024.0, file_elapsed))
        else:
            fail_count += 1

    # result 요약
    end_time = time.time()
    total_elapsed = end_time - start_time

    print("\n" + "=" * 60)
    print("  STL 일괄 내보내기 완료")
    print("=" * 60)
    print("  총 파일 수    : {}".format(total_files))
    print("  성공          : {}".format(success_count))
    print("  FAIL          : {}".format(fail_count))
    print("  건너뜀        : {}".format(skip_count))
    print("  총 소요 시간  : {:.2f}초".format(total_elapsed))
    if success_count > 0:
        print("  평균 변환 시간: {:.2f}초/파일".format(total_elapsed / success_count))
    print("=" * 60)


# ======================== 실row_val ========================
if __name__ == "__main__":
    run_stl_batch_conversion()
else:
    # FreeCAD에서 직접 실row_val할 때
    run_stl_batch_conversion()

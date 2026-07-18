# -*- coding: utf-8 -*-
"""
STEP 일괄 변환 매크로

실row_val 방법:
    FreeCAD에서 이 파일을 col_data고: 매크로 > 매크로 실row_val(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\12_step_batch_export.py").read())

description:
    지정된 디렉토리(및 sub 디렉토리)의 모든 .FCStd 파일을 찾아
    STEP (ISO 10303) 포맷으로 일괄 변환합니다.

사용법:
    1. 아래 변수들에 원하는 path를 설정하세요.
    2. FreeCAD에서 이 매크로를 실row_val합니다.
    3. 변환 result가 콘솔에 출력됩니다.
"""

import os
import sys
import time
import FreeCAD
import Import
import Part

# ======================== 사용자 설정 ========================
# 검색할 루트 디렉토리 path
input_dir = r"C:\Users\Administrator\Downloads\py\fcstd"

# STEP 파일을 저장할 출력 디렉토리 path
output_dir = r"C:\Users\Administrator\Downloads\py\step"

# 변환할 파일 확장자
input_ext = ".FCStd"

# 출력 파일 확장자
output_ext = ".step"

# sub 디렉토리 포함 여부
include_subdirs = True

# STEP 내보내기 스key마 (AP203 또는 AP214)
# AP203: 3D 설계 (기본value)
# AP214: 자동차/항공우주 (컬러 지원)
# AP242: 최신 표준 (리핑 지원)
step_schema = "AP203"

# 색상 info_val 포함 여부 (AP214에서만 유효)
include_color = True

# 로고/doc info_val 포함 여부
include_doc_info = True
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


def convert_schema(schema_string):
    """
    사용자 친화적 스key마 name을 STEP 스key마 식별자로 변환합니다.

    Args:
        schema_string: "AP203", "AP214", "AP242" 등

    Returns:
        Import 모듈에서 사용하는 스key마 딕셔너리
    """
    schema_map = {
        "AP203": {"AP203": True},
        "AP214": {"AP214": True},
        "AP242": {"AP242": True},
    }

    if schema_string in schema_map:
        return schema_map[schema_string]
    else:
        print("  [경고] 알 수 없는 스key마: {} (AP203 사용)".format(schema_string))
        return {"AP203": True}


def convert_single_file_to_step(input_path, output_path):
    """
    하나의 .FCStd 파일을 STEP로 변환합니다.

    Args:
        input_path: 원본 .FCStd 파일 path
        output_path: 출력 .step 파일 path

    Returns:
        (성공_여부, obj_count, shape_count) 튜플
    """
    doc = None

    try:
        # FreeCAD doc col_data기
        doc = FreeCAD.open(input_path)

        if doc is None:
            print("  [경고] doc를 col_data 수 없습니다: {}".format(input_path))
            return False, 0, 0

        # 활성 doc의 모든 obj를 가져옵니다
        objects_list = list(doc.Objects)

        if not objects_list:
            print("  [경고] doc에 obj가 없습니다: {}".format(input_path))
            FreeCAD.closeDocument(doc.Name)
            return False, 0, 0

        # STEP로 내보낼 shape 수집
        shapes_to_export = []
        for obj in objects_list:
            try:
                if hasattr(obj, 'Shape') and obj.Shape is not None:
                    shape = obj.Shape
                    # 유효한 shape인지 check
                    if shape.Volume > 0 or shape.Area > 0:
                        shapes_to_export.append(shape)
            except Exception as shape_error:
                print("  [경고] obj shape 수집 FAIL ({}): {}".format(
                    obj.Name, shape_error))
                continue

        if not shapes_to_export:
            print("  [경고] 내보낼 유효한 shape이 없습니다: {}".format(input_path))
            FreeCAD.closeDocument(doc.Name)
            return False, 0, 0

        # shape 병합 시도 (하나의 STEP 파일로 내보내기)
        if len(shapes_to_export) > 1:
            try:
                merged_shape = Part.makeCompound(shapes_to_export)
                shapes_to_export = [merged_shape]
            except:
                # 병합 FAIL 시 개별 shape으로 내보내기
                pass

        # STEP 내보내기 옵션 설정
        export_options = {}

        # 색상 info_val 포함
        if include_color and step_schema in ["AP214", "AP242"]:
            export_options['ColorMode'] = True
        else:
            export_options['ColorMode'] = False

        # doc info_val 포함 여부
        if include_doc_info:
            export_options['DocumentName'] = True
        else:
            export_options['DocumentName'] = False

        # STEP 파일로 내보내기
        Import.export(shapes_to_export, output_path)

        # shape 수와 obj 수 반환
        total_shape_count = len(shapes_to_export)

        # doc 닫기
        FreeCAD.closeDocument(doc.Name)

        return True, len(objects_list), total_shape_count

    except Exception as overall_error:
        print("  [error] STEP 변환 중 error 발생 ({}): {}".format(
            input_path, overall_error))
        if doc is not None:
            try:
                FreeCAD.closeDocument(doc.Name)
            except:
                pass
        return False, 0, 0


def run_step_batch_conversion():
    """STEP 일괄 변환의 combined 프로세스를 실row_val합니다."""

    print("=" * 65)
    print("  STEP 일괄 변환 start")
    print("=" * 65)
    print("  입력 디렉토리 : {}".format(input_dir))
    print("  출력 디렉토리 : {}".format(output_dir))
    print("  STEP 스key마   : {}".format(step_schema))
    print("  색상 info_val     : {}".format("포함" if include_color else "미포함"))
    print("  doc info_val     : {}".format("포함" if include_doc_info else "미포함"))
    print("-" * 65)

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

    # STEP 스key마 check
    print("\n[2단계] STEP 변환 설정 check...")
    print("  -> 적용 스key마: {}".format(step_schema))

    # 일괄 변환 실row_val
    print("\n[3단계] STEP 변환 start...")
    start_time = time.time()
    success_count = 0
    fail_count = 0
    skip_count = 0
    total_object_count = 0

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

        # STEP 변환 실row_val
        file_start = time.time()
        result, obj_count, shape_count = convert_single_file_to_step(
            input_file_path, output_file_path
        )
        file_elapsed = time.time() - file_start

        if result:
            success_count += 1
            total_object_count += obj_count
            # 파일 size 표시
            file_size = os.path.getsize(output_file_path)
            print("    -> 완료 (obj: {}, shape: {}, {:.1f}KB, {:.2f}초)".format(
                obj_count, shape_count, file_size / 1024.0, file_elapsed))
        else:
            fail_count += 1

    # result 요약
    end_time = time.time()
    total_elapsed = end_time - start_time

    print("\n" + "=" * 65)
    print("  STEP 일괄 변환 완료")
    print("=" * 65)
    print("  총 파일 수    : {}".format(total_files))
    print("  성공          : {}".format(success_count))
    print("  FAIL          : {}".format(fail_count))
    print("  건너뜀        : {}".format(skip_count))
    print("  총 obj 수    : {}".format(total_object_count))
    print("  총 소요 시간  : {:.2f}초".format(total_elapsed))
    if success_count > 0:
        print("  평균 변환 시간: {:.2f}초/파일".format(total_elapsed / success_count))
    print("=" * 65)


# ======================== 실row_val ========================
if __name__ == "__main__":
    run_step_batch_conversion()
else:
    # FreeCAD에서 직접 실row_val할 때
    run_step_batch_conversion()

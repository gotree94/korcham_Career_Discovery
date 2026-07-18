# -*- coding: utf-8 -*-
"""
치수 check_val 매크로

실row_val 방법:
    FreeCAD에서 이 파일을 col_data고: 매크로 > 매크로 실row_val(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\14_dimension_check.py").read())

description:
    model_val의 바운딩 박스를 check하고 허용 치수 범위를 check_val합니다.
    tolerance(公差) 범위 검사, 치수 report를 생성합니다.

사용법:
    1. 아래 변수들에 원하는 path와 check_val 기준을 설정하세요.
    2. FreeCAD에서 이 매크로를 실row_val합니다.
    3. check_val result가 콘솔에 출력되고 report 파일이 생성됩니다.
"""

import os
import sys
import csv
import time
import datetime
import FreeCAD

# ======================== 사용자 설정 ========================
# check_val할 파일이 있는 디렉토리 path
input_dir = r"C:\Users\Administrator\Downloads\py\fcstd"

# check_val report 출력 path
report_dir = r"C:\Users\Administrator\Downloads\py\report"

# 검색할 파일 확장자
file_ext = ".FCStd"

# sub 디렉토리 포함 여부
include_subdirs = True

# ==================== 치수 check_val 기준 ====================
# combined 치수 범위 (mm) - 바운딩 박스 기준
min_width = 1.0     # 최소 허용 width (mm)
max_width = 500.0   # 최대 허용 width (mm)
min_height = 1.0     # 최소 허용 height (mm)
max_height = 500.0   # 최대 허용 height (mm)
min_depth = 1.0     # 최소 허용 depth (mm)
max_depth = 500.0   # 최대 허용 depth (mm)

# tolerance 설정 (mm)
general_tolerance = 0.5       # 일반 치수 tolerance (±)
precision_tolerance = 0.01      # 정밀 치수 tolerance (±)
max_tolerance = 2.0       # 최대 허용 tolerance (±)

# aspect_ratio(Aspect Ratio) check_val - 가장 긴 변 / 가장 짧은 변
max_aspect_ratio = 50.0

# volume check_val (mm³)
min_volume = 1.0       # 최소 허용 volume (mm³)
max_volume = 1000000.0  # 최대 허용 volume (mm³)

# 정상 범위를 벗어난 치수의 ratio_val 경고 기준
warning_ratio = 0.3       # 30% 이상이 경고 시 combined 경고
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
                if filename.lower().endswith(file_ext.lower()):
                    full_path = os.path.join(dir_path, filename)
                    found_files.append(full_path)
    else:
        if os.path.isdir(root_path):
            for filename in os.listdir(root_path):
                if filename.lower().endswith(file_ext.lower()):
                    full_path = os.path.join(root_path, filename)
                    found_files.append(full_path)

    return found_files


def check_dimension(name, value, min_val, max_val, tolerance=0.0):
    """
    단일 치수에 대한 check_val을 수row_val합니다.

    Args:
        name: 치수 name (예: "width")
        value: 측정된 value (mm)
        min_val: 허용 min_val (mm)
        max_val: 허용 max_val (mm)
        tolerance: 허용 tolerance (mm, ±)

    Returns:
        딕셔너리: {
            "name": str,
            "value": float,
            "허용_최소": float,
            "허용_최대": float,
            "status": str ("PASS" 또는 "FAIL"),
            "message": str
        }
    """
    tol_allowed_min = min_val - tolerance
    tol_allowed_max = max_val + tolerance

    if value < tol_allowed_min:
        status = "FAIL"
        diff = tol_allowed_min - value
        message = "{}이(가) 최소 허용value보다 {:.2f}mm 작습니다".format(
            name, diff)
    elif value > tol_allowed_max:
        status = "FAIL"
        diff = value - tol_allowed_max
        message = "{}이(가) 최대 허용value보다 {:.2f}mm 큽니다".format(
            name, diff)
    else:
        status = "PASS"
        message = "정상 범위 내"

    return {
        "name": name,
        "value": value,
        "허용_최소": tol_allowed_min,
        "허용_최대": tol_allowed_max,
        "status": status,
        "message": message
    }


def check_aspect_ratio(width, height, depth):
    """
    바운딩 박스의 aspect_ratio(가장 긴 변 / 가장 짧은 변)를 check_val합니다.

    Args:
        width, height, depth: 바운딩 박스 치수 (mm)

    Returns:
        딕셔너리: {"aspect_ratio": float, "status": str, "message": str}
    """
    dimensions = [width, height, depth]
    max_val = max(dimensions)
    min_val = min(dimensions)

    if min_val == 0:
        aspect_ratio = float('inf')
    else:
        aspect_ratio = max_val / min_val

    if aspect_ratio > max_aspect_ratio:
        status = "FAIL"
        message = "aspect_ratio {:.2f}가 허용value {:.2f}를 초과합니다".format(
            aspect_ratio, max_aspect_ratio)
    else:
        status = "PASS"
        message = "정상 범위 내 (aspect_ratio: {:.2f})".format(aspect_ratio)

    return {
        "aspect_ratio": aspect_ratio,
        "status": status,
        "message": message
    }


def extract_doc_dimension_info(file_path):
    """
    .FCStd 파일에서 치수 관련 info_val를 추출합니다.

    Args:
        file_path: .FCStd 파일 path

    Returns:
        딕셔너리: 치수 check_val에 필요한 모든 info_val
    """
    doc = None
    info_val = {
        "obj_count": 0,
        "width": 0.0,
        "height": 0.0,
        "depth": 0.0,
        "volume": 0.0,
        "area_val": 0.0,
        "obj_name들": [],
        "shape_error": []
    }

    try:
        doc = FreeCAD.open(file_path)

        if doc is None:
            return info_val

        objects_list = list(doc.Objects)
        info_val["obj_count"] = len(objects_list)

        total_bbox = None

        for obj in objects_list:
            try:
                if hasattr(obj, 'Shape') and obj.Shape is not None:
                    shape = obj.Shape

                    # 바운딩 박스 업데이트
                    if total_bbox is None:
                        total_bbox = shape.BoundBox
                    else:
                        total_bbox = total_bbox.united(shape.BoundBox)

                    # volume 및 area_val 누적
                    info_val["volume"] += shape.Volume
                    info_val["area_val"] += shape.Area

                    info_val["obj_name들"].append(obj.Name)
            except Exception as shape_error:
                info_val["shape_error"].append({
                    "obj명": obj.Name,
                    "error": str(shape_error)
                })
                continue

        # 바운딩 박스 치수 저장
        if total_bbox is not None:
            info_val["width"] = total_bbox.XLength
            info_val["height"] = total_bbox.YLength
            info_val["depth"] = total_bbox.ZLength

        FreeCAD.closeDocument(doc.Name)

    except Exception as error:
        print("  [경고] info_val 추출 FAIL ({}): {}".format(file_path, error))
        if doc is not None:
            try:
                FreeCAD.closeDocument(doc.Name)
            except:
                pass

    return info_val


def generate_dimension_report(check_results_list, output_path):
    """
    check_val result를 CSV report로 저장합니다.

    Args:
        check_results_list: 각 파일별 check_val result 리스트
        output_path: CSV 파일 출력 path

    Returns:
        bool: 성공 여부
    """

    header = [
        "number",
        "fname",
        "obj 수",
        "width (mm)",
        "height (mm)",
        "depth (mm)",
        "volume (mm³)",
        "area_val (mm²)",
        "width check_val",
        "height check_val",
        "depth check_val",
        "volume check_val",
        "aspect_ratio",
        "aspect_ratio check_val",
        "combined result",
        "notes"
    ]

    try:
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)

            for index, result in enumerate(check_results_list, 1):
                # combined result 판정
                all_pass = all(
                    check_val["status"] == "PASS"
                    for check_val in result["check_dimension"]
                ) and result["check_aspect_ratio"]["status"] == "PASS"

                combined_status = "PASS" if all_pass else "FAIL"

                # notes 수집
                notes_list = []
                for check_val in result["check_dimension"]:
                    if check_val["status"] == "FAIL":
                        notes_list.append(check_val["message"])
                if result["check_aspect_ratio"]["status"] == "FAIL":
                    notes_list.append(result["check_aspect_ratio"]["message"])

                notes = " | ".join(notes_list) if notes_list else "정상"

                writer.writerow([
                    index,
                    result["fname"],
                    result["obj_count"],
                    "{:.2f}".format(result["width"]),
                    "{:.2f}".format(result["height"]),
                    "{:.2f}".format(result["depth"]),
                    "{:.2f}".format(result["volume"]),
                    "{:.2f}".format(result["area_val"]),
                    result["check_dimension"][0]["status"],
                    result["check_dimension"][1]["status"],
                    result["check_dimension"][2]["status"],
                    result["volume_check"]["status"],
                    "{:.2f}".format(result["check_aspect_ratio"]["aspect_ratio"]),
                    result["check_aspect_ratio"]["status"],
                    combined_status,
                    notes
                ])

        return True

    except Exception as error:
        print("[error] report 파일 저장 FAIL: {}".format(error))
        return False


def run_dimension_check():
    """치수 check_val의 combined 프로세스를 실row_val합니다."""

    print("=" * 70)
    print("  치수 check_val start")
    print("=" * 70)
    print("  입력 디렉토리 : {}".format(input_dir))
    print("  report 출력   : {}".format(report_dir))
    print("  허용 치수 범위:")
    print("    width: {:.1f} ~ {:.1f} mm (tolerance: ±{:.2f} mm)".format(
        min_width, max_width, general_tolerance))
    print("    height: {:.1f} ~ {:.1f} mm (tolerance: ±{:.2f} mm)".format(
        min_height, max_height, general_tolerance))
    print("    depth: {:.1f} ~ {:.1f} mm (tolerance: ±{:.2f} mm)".format(
        min_depth, max_depth, general_tolerance))
    print("    volume: {:.1f} ~ {:,.1f} mm³".format(min_volume, max_volume))
    print("    최대 aspect_ratio: {:.1f}".format(max_aspect_ratio))
    print("-" * 70)

    # 디렉토리 존재 check
    if not os.path.isdir(input_dir):
        print("[FAIL] 입력 디렉토리가 없습니다. path를 check하세요.")
        return

    # 출력 디렉토리 생성
    check_directory_exists(report_dir)

    # .FCStd 파일 검색
    print("\n[1단계] .FCStd 파일 검색 중...")
    found_files = search_fcstd_files(input_dir, include_subdirs)
    total_files = len(found_files)

    if total_files == 0:
        print("[info_val] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 파일을 찾았습니다.".format(total_files))

    # 치수 check_val 실row_val
    print("\n[2단계] 치수 check_val 실row_val...")
    start_time = time.time()
    check_results_list = []
    pass_count = 0
    fail_count = 0

    for index, file_path in enumerate(found_files, 1):
        progress = (index / total_files) * 100
        fname = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, input_dir)

        print("  [{:5.1f}%] ({}/{}) check_val 중: {}".format(
            progress, index, total_files, rel_path))

        # doc info_val 추출
        doc_info = extract_doc_dimension_info(file_path)

        # 치수 check_val 수row_val
        width_check = check_dimension("width", doc_info["width"], min_width, max_width, general_tolerance)
        height_check = check_dimension("height", doc_info["height"], min_height, max_height, general_tolerance)
        depth_check = check_dimension("depth", doc_info["depth"], min_depth, max_depth, general_tolerance)

        # volume check_val
        volume_check = check_dimension("volume", doc_info["volume"], min_volume, max_volume)

        # aspect_ratio check_val
        check_aspect_ratio = check_aspect_ratio(doc_info["width"], doc_info["height"], doc_info["depth"])

        # combined 판정
        all_pass = (
            width_check["status"] == "PASS" and
            height_check["status"] == "PASS" and
            depth_check["status"] == "PASS" and
            volume_check["status"] == "PASS" and
            check_aspect_ratio["status"] == "PASS"
        )

        if all_pass:
            pass_count += 1
            verdict_text = "✓ PASS"
        else:
            fail_count += 1
            verdict_text = "✗ FAIL"

        # check_val result 저장
        result = {
            "fname": fname,
            "rel_path": rel_path,
            "obj_count": doc_info["obj_count"],
            "width": doc_info["width"],
            "height": doc_info["height"],
            "depth": doc_info["depth"],
            "volume": doc_info["volume"],
            "area_val": doc_info["area_val"],
            "check_dimension": [width_check, height_check, depth_check],
            "volume_check": volume_check,
            "check_aspect_ratio": check_aspect_ratio
        }
        check_results_list.append(result)

        # 콘솔 출력
        print("    -> {} | {:.1f}x{:.1f}x{:.1f}mm | volume: {:.1f}mm³".format(
            verdict_text,
            doc_info["width"],
            doc_info["height"],
            doc_info["depth"],
            doc_info["volume"]
        ))

        # FAIL 항목 상세 출력
        if not all_pass:
            for check_val in [width_check, height_check, depth_check, volume_check]:
                if check_val["status"] == "FAIL":
                    print("      [FAIL] {}".format(check_val["message"]))
            if check_aspect_ratio["status"] == "FAIL":
                print("      [FAIL] {}".format(check_aspect_ratio["message"]))

    # report 생성
    print("\n[3단계] check_val report 생성...")
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = "치수check_val_report_{}.csv".format(current_time)
    report_path = os.path.join(report_dir, report_filename)

    if generate_dimension_report(check_results_list, report_path):
        print("  -> report 파일 생성 완료: {}".format(report_path))
    else:
        print("  -> report 파일 생성 FAIL!")

    # result 요약
    end_time = time.time()
    total_elapsed = end_time - start_time

    print("\n" + "=" * 70)
    print("  치수 check_val 완료")
    print("=" * 70)
    print("  총 파일 수    : {}".format(total_files))
    print("  PASS          : {}".format(pass_count))
    print("  FAIL          : {}".format(fail_count))

    if total_files > 0:
        pass_ratio = (pass_count / total_files) * 100
        print("  PASS율        : {:.1f}%".format(pass_ratio))

        if pass_ratio < (1 - warning_ratio) * 100:
            print("  [주의] combined 파일의 {:.1f}%가 check_val 기준에 미달합니다!".format(
                100 - pass_ratio))

    print("  총 소요 시간  : {:.2f}초".format(total_elapsed))
    print("  report 파일   : {}".format(report_path))
    print("=" * 70)


# ======================== 실row_val ========================
if __name__ == "__main__":
    run_dimension_check()
else:
    # FreeCAD에서 직접 실row_val할 때
    run_dimension_check()

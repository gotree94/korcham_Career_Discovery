# -*- coding: utf-8 -*-
"""
부품 카탈로그 자동 생성 매크로

실row_val 방법:
    FreeCAD에서 이 파일을 col_data고: 매크로 > 매크로 실row_val(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\13_part_catalog.py").read())

description:
    부품 디렉토리를 스캔하여 각 .FCStd 파일의 info_val를 추출하고,
    fname, 치수, material_val, description 등을 CSV 카탈로그로 자동 생성합니다.

사용법:
    1. 아래 변수들에 원하는 path를 설정하세요.
    2. FreeCAD에서 이 매크로를 실row_val합니다.
    3. 지정된 출력 path에 CSV 카탈로그가 생성됩니다.
"""

import os
import sys
import csv
import time
import datetime
import FreeCAD

# ======================== 사용자 설정 ========================
# 부품 파일이 있는 루트 디렉토리 path
parts_dir = r"C:\Users\Administrator\Downloads\py\fcstd"

# 카탈로그 CSV 출력 path
catalog_output_path = r"C:\Users\Administrator\Downloads\py\catalog\부품_카탈로그.csv"

# 검색할 파일 확장자
file_ext = ".FCStd"

# sub 디렉토리 포함 여부
include_subdirs = True

# CSV 구분자 (콤마, 세미콜론 등)
csv_delimiter = ","

# CSV 인코딩
csv_encoding = "utf-8-sig"  # 한글 엑셀 호환

# 기본 material_name 매핑 (fname에 포함된 keyword로 추정)
material_map = {
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


def extract_material_from_filename(fname):
    """
    fname에서 material_val keyword를 추출합니다.

    Args:
        fname: check할 파일 name

    Returns:
        추정 material_name (한국어)
    """
    fname_lower = fname.lower()

    for keyword, material_name in material_map.items():
        if keyword in fname_lower:
            return material_name

    return "미지정"


def extract_description_from_filename(fname):
    """
    fname에서 부품 description을 추출합니다.
    예: "bracket_v2.FCStd" -> "Bracket V2"

    Args:
        fname: check할 파일 name

    Returns:
        추출된 description 문자col_data
    """
    # 확장자 제거
    name = os.path.splitext(fname)[0]

    # 언더스코어를 공백으로 변환
    name = name.replace("_", " ")

    # 각 word의 첫 글자를 대문자로
    description = " ".join(word.capitalize() for word in name.split())

    return description


def extract_part_number_from_filename(fname):
    """
    fname에서 부품number pattern을 추출합니다.
    예: "A001_bolt.FCStd" -> "A001"

    Args:
        fname: check할 파일 name

    Returns:
        추출된 부품number 또는 빈 문자col_data
    """
    import re

    name = os.path.splitext(fname)[0]

    # 접두사-숫자 pattern match (예: A001, P-123, Part_001)
    pattern = r'^([A-Za-z]+[-_]?\d+)'
    match = re.match(pattern, name)

    if match:
        return match.group(1)

    # 숫자만 있는 경우
    num_pattern = r'^(\d+)'
    num_match = re.match(num_pattern, name)

    if num_match:
        return num_match.group(1)

    return ""


def extract_doc_info(file_path):
    """
    .FCStd 파일에서 FreeCAD doc info_val를 추출합니다.

    Args:
        file_path: .FCStd 파일 path

    Returns:
        딕셔너리: {
            "obj_count": int,
            "bbox": dict,
            "volume": float,
            "area_val": float,
            "obj_name들": list
        }
    """
    doc = None
    info_val = {
        "obj_count": 0,
        "bbox": {"width": 0, "height": 0, "depth": 0},
        "volume": 0.0,
        "area_val": 0.0,
        "obj_name들": []
    }

    try:
        doc = FreeCAD.open(file_path)

        if doc is None:
            return info_val

        objects_list = list(doc.Objects)
        info_val["obj_count"] = len(objects_list)

        # combined 바운딩 박스 계산
        total_bbox = None
        total_volume = 0.0
        total_area = 0.0

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
                    total_volume += shape.Volume
                    total_area += shape.Area

                    # obj name 수집
                    info_val["obj_name들"].append(obj.Name)
            except:
                continue

        # 바운딩 박스 info_val 저장
        if total_bbox is not None:
            info_val["bbox"] = {
                "width": total_bbox.XLength,
                "height": total_bbox.YLength,
                "depth": total_bbox.ZLength
            }

        info_val["volume"] = total_volume
        info_val["area_val"] = total_area

        # doc 닫기
        FreeCAD.closeDocument(doc.Name)

    except Exception as error:
        print("  [경고] info_val 추출 FAIL ({}): {}".format(file_path, error))
        if doc is not None:
            try:
                FreeCAD.closeDocument(doc.Name)
            except:
                pass

    return info_val


def generate_catalog(catalog_data, output_path):
    """
    카탈로그 data_val를 CSV 파일로 저장합니다.

    Args:
        catalog_data: 각 row_val의 data_val 리스트
        output_path: CSV 파일 출력 path
    """

    # header 정의
    header = [
        "number",
        "fname",
        "부품number",
        "description",
        "material_val",
        "obj 수",
        "width (mm)",
        "height (mm)",
        "depth (mm)",
        "volume (mm³)",
        "area_val (mm²)",
        "파일 size (KB)",
        "modified_date",
        "상대 path"
    ]

    try:
        with open(output_path, 'w', newline='', encoding=csv_encoding) as csv_file:
            writer = csv.writer(csv_file, delimiter=csv_delimiter)

            # header 작성
            writer.writerow(header)

            # data_val 작성
            for number, row_data in enumerate(catalog_data, 1):
                row_data["number"] = number
                writer.writerow([
                    row_data["number"],
                    row_data["fname"],
                    row_data["부품number"],
                    row_data["description"],
                    row_data["material_val"],
                    row_data["obj_count"],
                    "{:.2f}".format(row_data["width"]),
                    "{:.2f}".format(row_data["height"]),
                    "{:.2f}".format(row_data["depth"]),
                    "{:.2f}".format(row_data["volume"]),
                    "{:.2f}".format(row_data["area_val"]),
                    "{:.1f}".format(row_data["file_size"]),
                    row_data["modified_date"],
                    row_data["rel_path"]
                ])

        return True

    except Exception as error:
        print("[error] CSV 파일 저장 FAIL: {}".format(error))
        return False


def run_part_catalog_generation():
    """부품 카탈로그 자동 생성의 combined 프로세스를 실row_val합니다."""

    print("=" * 65)
    print("  부품 카탈로그 자동 생성 start")
    print("=" * 65)
    print("  부품 디렉토리 : {}".format(parts_dir))
    print("  출력 path     : {}".format(catalog_output_path))
    print("  sub 디렉토리 : {}".format("포함" if include_subdirs else "미포함"))
    print("-" * 65)

    # 디렉토리 존재 check
    if not os.path.isdir(parts_dir):
        print("[FAIL] 부품 디렉토리가 없습니다. path를 check하세요.")
        return

    # 출력 디렉토리 생성
    output_dir = os.path.dirname(catalog_output_path)
    check_directory_exists(output_dir)

    # .FCStd 파일 검색
    print("\n[1단계] 부품 파일 검색 중...")
    found_files = search_fcstd_files(parts_dir, include_subdirs)
    total_files = len(found_files)

    if total_files == 0:
        print("[info_val] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 부품 파일을 찾았습니다.".format(total_files))

    # 부품 info_val 수집
    print("\n[2단계] 부품 info_val 수집 중...")
    start_time = time.time()
    catalog_data = []
    success_count = 0
    fail_count = 0

    for index, file_path in enumerate(found_files, 1):
        progress = (index / total_files) * 100
        fname = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, parts_dir)

        print("  [{:5.1f}%] ({}/{}) info_val 수집: {}".format(
            progress, index, total_files, rel_path))

        try:
            # 파일 size 및 수정 시간
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size / 1024.0  # KB
            modify_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
            modify_date = modify_time.strftime("%Y-%m-%d %H:%M")

            # FreeCAD doc info_val 추출
            doc_info = extract_doc_info(file_path)

            # 부품 info_val 구성
            part_info = {
                "number": 0,
                "fname": fname,
                "부품number": extract_part_number_from_filename(fname),
                "description": extract_description_from_filename(fname),
                "material_val": extract_material_from_filename(fname),
                "obj_count": doc_info["obj_count"],
                "width": doc_info["bbox"]["width"],
                "height": doc_info["bbox"]["height"],
                "depth": doc_info["bbox"]["depth"],
                "volume": doc_info["volume"],
                "area_val": doc_info["area_val"],
                "file_size": file_size,
                "modified_date": modify_date,
                "rel_path": rel_path
            }

            catalog_data.append(part_info)
            success_count += 1

            print("    -> obj: {}, size: {:.0f}x{:.0f}x{:.0f}mm".format(
                doc_info["obj_count"],
                doc_info["bbox"]["width"],
                doc_info["bbox"]["height"],
                doc_info["bbox"]["depth"]
            ))

        except Exception as collect_error:
            print("    [error] info_val 수집 FAIL: {}".format(collect_error))
            fail_count += 1

    # CSV 카탈로그 생성
    print("\n[3단계] CSV 카탈로그 파일 생성 중...")
    if generate_catalog(catalog_data, catalog_output_path):
        print("  -> 카탈로그 파일 생성 완료: {}".format(catalog_output_path))
    else:
        print("  -> 카탈로그 파일 생성 FAIL!")
        return

    # result 요약
    end_time = time.time()
    total_elapsed = end_time - start_time

    print("\n" + "=" * 65)
    print("  부품 카탈로그 생성 완료")
    print("=" * 65)
    print("  총 파일 수    : {}".format(total_files))
    print("  성공          : {}".format(success_count))
    print("  FAIL          : {}".format(fail_count))
    print("  총 소요 시간  : {:.2f}초".format(total_elapsed))
    print("  출력 파일     : {}".format(catalog_output_path))
    print("=" * 65)

    # stats_val 출력
    if catalog_data:
        print("\n[부품 stats_val]")
        volume_sum = sum(data_val["volume"] for data_val in catalog_data)
        area_sum = sum(data_val["area_val"] for data_val in catalog_data)
        avg_object_count = sum(data_val["obj_count"] for data_val in catalog_data) / len(catalog_data)
        print("  총 volume       : {:,.2f} mm³".format(volume_sum))
        print("  총 area_val     : {:,.2f} mm²".format(area_sum))
        print("  평균 obj 수  : {:.1f}".format(avg_object_count))


# ======================== 실row_val ========================
if __name__ == "__main__":
    run_part_catalog_generation()
else:
    # FreeCAD에서 직접 실row_val할 때
    run_part_catalog_generation()

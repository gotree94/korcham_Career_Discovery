# -*- coding: utf-8 -*-
"""
보고서 자동 생성 매크로

실row_val 방법:
    FreeCAD에서 이 파일을 col_data고: 매크로 > 매크로 실row_val(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\15_report_generator.py").read())

description:
    부품의 3D model_val info_val를 HTML 보고서로 자동 생성합니다.
    치수, volume, area_val, material_val info_val 등을 포함한 형식화된 보고서를 생성합니다.

사용법:
    1. 아래 변수들에 원하는 path를 설정하세요.
    2. FreeCAD에서 이 매크로를 실row_val합니다.
    3. 지정된 출력 path에 HTML 보고서가 생성됩니다.
"""

import os
import sys
import time
import datetime
import FreeCAD

# ======================== 사용자 설정 ========================
# analysis_val할 파일이 있는 디렉토리 path
input_dir = r"C:\Users\Administrator\Downloads\py\fcstd"

# HTML 보고서 출력 path
report_output_path = r"C:\Users\Administrator\Downloads\py\report\부품_보고서.html"

# 검색할 파일 확장자
file_ext = ".FCStd"

# sub 디렉토리 포함 여부
include_subdirs = True

# material_name 매핑 (fname keyword 기반)
material_map = {
    "steel": {"name": "강재 (Steel)", "density": 7.85, "색상": "#888888"},
    "aluminum": {"name": "알루미늄 (Aluminum)", "density": 2.70, "색상": "#C0C0C0"},
    "aluminium": {"name": "알루미늄 (Aluminum)", "density": 2.70, "색상": "#C0C0C0"},
    "plastic": {"name": "플라스틱 (Plastic)", "density": 1.20, "색상": "#FFCC00"},
    "rubber": {"name": "고무 (Rubber)", "density": 1.50, "색상": "#333333"},
    "copper": {"name": "구리 (Copper)", "density": 8.96, "색상": "#B87333"},
    "brass": {"name": "황동 (Brass)", "density": 8.50, "색상": "#CD9B1D"},
    "stainless": {"name": "스테인리스강", "density": 7.93, "색상": "#D0D0D0"},
    "wood": {"name": "목재 (Wood)", "density": 0.60, "색상": "#8B4513"},
    "titanium": {"name": "티타늄 (Titanium)", "density": 4.51, "색상": "#A0A0A0"},
    "nylon": {"name": "나일론 (Nylon)", "density": 1.15, "색상": "#F5F5DC"},
    "glass": {"name": "유리 (Glass)", "density": 2.50, "색상": "#E0F0FF"},
    "carbon": {"name": "카본 (Carbon)", "density": 1.80, "색상": "#2C2C2C"},
    "ceramic": {"name": "세라믹 (Ceramic)", "density": 3.00, "색상": "#F5F5F5"},
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
    """fname에서 material_val info_val를 추출합니다."""
    fname_lower = fname.lower()

    for keyword, material_info in material_map.items():
        if keyword in fname_lower:
            return material_info

    return {"name": "미지정", "density": 0.0, "색상": "#CCCCCC"}


def extract_doc_info(file_path):
    """
    .FCStd 파일에서 상세 info_val를 추출합니다.

    Args:
        file_path: .FCStd 파일 path

    Returns:
        딕셔너리: model_val의 모든 info_val
    """
    doc = None
    info_val = {
        "obj_count": 0,
        "bbox": {
            "width": 0.0,
            "height": 0.0,
            "depth": 0.0
        },
        "volume": 0.0,
        "area_val": 0.0,
        "mass": 0.0,
        "obj_info들": [],
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

                    # obj별 상세 info_val
                    obj_info = {
                        "name": obj.Name,
                        "type_id":对象.TypeId if hasattr(obj, 'TypeId') else "알 수 없음",
                        "volume": shape.Volume,
                        "area_val": shape.Area,
                        "center": {
                            "x": shape.CenterOfGravity.x,
                            "y": shape.CenterOfGravity.y,
                            "z": shape.CenterOfGravity.z,
                        }
                    }

                    # 바운딩 박스 업데이트
                    if total_bbox is None:
                        total_bbox = shape.BoundBox
                    else:
                        total_bbox = total_bbox.united(shape.BoundBox)

                    info_val["volume"] += shape.Volume
                    info_val["area_val"] += shape.Area
                    info_val["obj_info들"].append(obj_info)

            except Exception as shape_error:
                info_val["shape_error"].append({
                    "obj명":对象.Name,
                    "error": str(shape_error)
                })
                continue

        # 바운딩 박스 치수 저장
        if total_bbox is not None:
            info_val["bbox"] = {
                "width": total_bbox.XLength,
                "height": total_bbox.YLength,
                "depth": total_bbox.ZLength
            }

        FreeCAD.closeDocument(doc.Name)

    except Exception as error:
        print("  [경고] info_val 추출 FAIL ({}): {}".format(file_path, error))
        if doc is not None:
            try:
                FreeCAD.closeDocument(doc.Name)
            except:
                pass

    return info_val


def generate_html_report(parts_data_list, output_path):
    """
    수집된 부품 data_val를 HTML 보고서로 생성합니다.

    Args:
        parts_data_list: 각 부품별 info_val 리스트
        output_path: HTML 파일 출력 path

    Returns:
        bool: 성공 여부
    """

    current_time = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    total_parts = len(parts_data_list)

    # 총 volume, area_val 합계 계산
    total_volume = sum(data_val["volume"] for data_val in parts_data_list)
    total_area = sum(data_val["area_val"] for data_val in parts_data_list)

    # HTML 템플릿 start
    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>부품 보고서 - FreeCAD 자동 생성</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Malgun Gothic', '맑은 고딕', 'Apple SD Gothic Neo', sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a5276, #2e86c1);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }
        .header .meta {
            font-size: 0.95em;
            opacity: 0.9;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        .summary-card {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.08);
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #1a5276;
        }
        .summary-card .label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        .content {
            padding: 30px 40px;
        }
        .section-title {
            font-size: 1.5em;
            color: #1a5276;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #2e86c1;
        }
        .part-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        }
        .part-card-header {
            background: #2e86c1;
            color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .part-card-header h3 {
            font-size: 1.1em;
        }
        .part-card-body {
            padding: 25px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .info-item {
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #2e86c1;
        }
        .info-item .key {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 4px;
        }
        .info-item .val {
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
        }
        .object-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .object-table th {
            background: #eaf2f8;
            color: #1a5276;
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }
        .object-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }
        .object-table tr:hover {
            background: #f5f8fc;
        }
        .footer {
            background: #2c3e50;
            color: #bdc3c7;
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .badge-info {
            background: #d4efdf;
            color: #1e8449;
        }
        .material-badge {
            background: #ebf5fb;
            color: #2e86c1;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FreeCAD 부품 보고서</h1>
            <div class="meta">
                자동 생성 일시: {report_datetime} | 생성 도구: FreeCAD Python 매크로
            </div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="value">{total_parts}</div>
                <div class="label">총 부품 수</div>
            </div>
            <div class="summary-card">
                <div class="value">{total_volume:,.1f}</div>
                <div class="label">총 volume (mm³)</div>
            </div>
            <div class="summary-card">
                <div class="value">{total_area:,.1f}</div>
                <div class="label">총 area_val (mm²)</div>
            </div>
            <div class="summary-card">
                <div class="value">{total_object_count}</div>
                <div class="label">총 obj 수</div>
            </div>
        </div>

        <div class="content">
            <h2 class="section-title">부품 상세 info_val</h2>
""".format(
        report_datetime=current_time,
        total_parts=total_parts,
        total_volume=total_volume,
        total_area=total_area,
        total_object_count=sum(data_val["obj_count"] for data_val in parts_data_list)
    )

    # 각 부품별 상세 info_val 추가
    for index, data_val in enumerate(parts_data_list, 1):
        fname = data_val["fname"]
        material_val = data_val["material_val"]

        # obj 테이블 row_val 생성
        object_table_row = ""
        for obj in data_val["obj_info들"]:
            object_table_row += """
                <tr>
                    <td>{name}</td>
                    <td>{type_id}</td>
                    <td>{volume:.2f}</td>
                    <td>{area_val:.2f}</td>
                    <td>({x:.2f}, {y:.2f}, {z:.2f})</td>
                </tr>""".format(
                name=obj["name"],
                type_id=obj["type_id"],
                volume=obj["volume"],
                area_val=obj["area_val"],
                x=obj["center"]["x"],
                y=obj["center"]["y"],
                z=obj["center"]["z"]
            )

        # 추정 mass 계산
        estimated_mass = data_val["volume"] * material_val["density"] / 1000.0  # g 단위

        html_content += """
            <div class="part-card">
                <div class="part-card-header">
                    <h3>#{index} {fname}</h3>
                    <span class="material-badge">{material_name}</span>
                </div>
                <div class="part-card-body">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="key">fname</div>
                            <div class="val">{fname}</div>
                        </div>
                        <div class="info-item">
                            <div class="key">obj 수</div>
                            <div class="val">{obj_count}개</div>
                        </div>
                        <div class="info-item">
                            <div class="key">width (X)</div>
                            <div class="val">{width:.2f} mm</div>
                        </div>
                        <div class="info-item">
                            <div class="key">height (Y)</div>
                            <div class="val">{height:.2f} mm</div>
                        </div>
                        <div class="info-item">
                            <div class="key">depth (Z)</div>
                            <div class="val">{depth:.2f} mm</div>
                        </div>
                        <div class="info-item">
                            <div class="key">volume</div>
                            <div class="val">{volume:.2f} mm³</div>
                        </div>
                        <div class="info-item">
                            <div class="key">area_val</div>
                            <div class="val">{area_val:.2f} mm²</div>
                        </div>
                        <div class="info-item">
                            <div class="key">추정 mass</div>
                            <div class="val">{mass:.2f} g</div>
                        </div>
                        <div class="info-item">
                            <div class="key">material_val</div>
                            <div class="val">{material_name}</div>
                        </div>
                        <div class="info-item">
                            <div class="key">density</div>
                            <div class="val">{density} g/cm³</div>
                        </div>
                    </div>

                    <h4 style="margin-top: 25px; color: #1a5276;">obj 상세 목록</h4>
                    <table class="object-table">
                        <thead>
                            <tr>
                                <th>obj명</th>
                                <th>type_id</th>
                                <th>volume (mm³)</th>
                                <th>area_val (mm²)</th>
                                <th>무게center (mm)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {obj_table}
                        </tbody>
                    </table>
                </div>
            </div>
""".format(
            index=index,
            fname=fname,
            material_name=material_val["name"],
            obj_count=data_val["obj_count"],
            width=data_val["bbox"]["width"],
            height=data_val["bbox"]["height"],
            depth=data_val["bbox"]["depth"],
            volume=data_val["volume"],
            area_val=data_val["area_val"],
            mass=estimated_mass,
            density=material_val["density"],
            obj_table=object_table_row
        )

    # HTML 템플릿 마무리
    html_content += """
        </div>

        <div class="footer">
            <p>이 보고서는 FreeCAD Python 매크로에 의해 자동 생성되었습니다.</p>
            <p>생성 일시: {report_datetime} | FreeCAD Python + AI 설계 자동화</p>
        </div>
    </div>
</body>
</html>""".format(report_datetime=current_time)

    # HTML 파일 저장
    try:
        output_dir = os.path.dirname(output_path)
        check_directory_exists(output_dir)

        with open(output_path, 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        return True

    except Exception as error:
        print("[error] HTML 보고서 저장 FAIL: {}".format(error))
        return False


def run_auto_report_generation():
    """보고서 자동 생성의 combined 프로세스를 실row_val합니다."""

    print("=" * 65)
    print("  부품 보고서 자동 생성 start")
    print("=" * 65)
    print("  입력 디렉토리 : {}".format(input_dir))
    print("  보고서 출력   : {}".format(report_output_path))
    print("  sub 디렉토리 : {}".format("포함" if include_subdirs else "미포함"))
    print("-" * 65)

    # 디렉토리 존재 check
    if not os.path.isdir(input_dir):
        print("[FAIL] 입력 디렉토리가 없습니다. path를 check하세요.")
        return

    # .FCStd 파일 검색
    print("\n[1단계] .FCStd 파일 검색 중...")
    found_files = search_fcstd_files(input_dir, include_subdirs)
    total_files = len(found_files)

    if total_files == 0:
        print("[info_val] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 파일을 찾았습니다.".format(total_files))

    # 부품 info_val 수집
    print("\n[2단계] 부품 info_val 수집 중...")
    start_time = time.time()
    parts_data_list = []
    success_count = 0
    fail_count = 0

    for index, file_path in enumerate(found_files, 1):
        progress = (index / total_files) * 100
        fname = os.path.basename(file_path)
        rel_path = os.path.relpath(file_path, input_dir)

        print("  [{:5.1f}%] ({}/{}) info_val 수집: {}".format(
            progress, index, total_files, rel_path))

        try:
            # doc info_val 추출
            doc_info = extract_doc_info(file_path)

            # material_val info_val 추출
            material_val = extract_material_from_filename(fname)

            # 부품 data_val 구성
            part_data = {
                "fname": fname,
                "rel_path": rel_path,
                "obj_count": doc_info["obj_count"],
                "bbox": doc_info["bbox"],
                "volume": doc_info["volume"],
                "area_val": doc_info["area_val"],
                "material_val": material_val,
                "obj_info들": doc_info["obj_info들"]
            }

            parts_data_list.append(part_data)
            success_count += 1

            estimated_mass = doc_info["volume"] * material_val["density"] / 1000.0
            print("    -> obj: {}, volume: {:.1f}mm³, 추정 mass: {:.1f}g, material_val: {}".format(
                doc_info["obj_count"],
                doc_info["volume"],
                estimated_mass,
                material_val["name"]
            ))

        except Exception as collect_error:
            print("    [error] info_val 수집 FAIL: {}".format(collect_error))
            fail_count += 1

    # HTML 보고서 생성
    print("\n[3단계] HTML 보고서 생성 중...")
    if generate_html_report(parts_data_list, report_output_path):
        print("  -> HTML 보고서 생성 완료: {}".format(report_output_path))
    else:
        print("  -> HTML 보고서 생성 FAIL!")
        return

    # result 요약
    end_time = time.time()
    total_elapsed = end_time - start_time

    print("\n" + "=" * 65)
    print("  보고서 자동 생성 완료")
    print("=" * 65)
    print("  총 파일 수    : {}".format(total_files))
    print("  성공          : {}".format(success_count))
    print("  FAIL          : {}".format(fail_count))
    print("  총 소요 시간  : {:.2f}초".format(total_elapsed))
    print("  출력 파일     : {}".format(report_output_path))

    if parts_data_list:
        total_volume = sum(data_val["volume"] for data_val in parts_data_list)
        total_area = sum(data_val["area_val"] for data_val in parts_data_list)
        print("  총 volume       : {:,.2f} mm³".format(total_volume))
        print("  총 area_val     : {:,.2f} mm²".format(total_area))

    print("=" * 65)


# ======================== 실row_val ========================
if __name__ == "__main__":
    run_auto_report_generation()
else:
    # FreeCAD에서 직접 실row_val할 때
    run_auto_report_generation()

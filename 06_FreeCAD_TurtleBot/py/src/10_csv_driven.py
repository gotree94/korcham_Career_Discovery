# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 2 - Lesson 10: CSV 데이터 기반 설계 (CSV-Driven Design)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "10_csv_driven" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/10_csv_driven.py").read())

[학습 목표]
- CSV 파일 읽기 (Python csv 모듈)
- CSV 데이터로 부품 자동 생성
- 샘플 CSV 파일 자동 생성
- 엑셀/스프레드시트에서 설계 데이터 관리
- 대량 부품 일괄 생성 파이프라인
=============================================================
"""

import sys
import os
import csv
import math

# ============================================================
# 1. FreeCAD 환경 확인
# ============================================================
try:
    import FreeCAD
    import Part
    print(f"[INFO] FreeCAD {FreeCAD.Version()[0]}.{FreeCAD.Version()[1]} 환경 확인")
except ImportError:
    print("[ERROR] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)

# ============================================================
# 2. 새 문서 생성
# ============================================================
if FreeCAD.ActiveDocument:
    FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

doc = FreeCAD.newDocument("CSV_Driven_Design")
print("[INFO] 새 문서 생성됨: CSV_Driven_Design")

# ============================================================
# 3. 샘플 CSV 파일 자동 생성
# ============================================================
# 실제 프로젝트에서는 엑셀이나 스프레드시트에서 CSV로 내보냅니다.
# 여기서는 샘플 CSV를 자동으로 만들어 학습합니다.

output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(output_dir, exist_ok=True)

# ---- 샘플 1: 브라켓 데이터 ----
bracket_csv_path = os.path.join(output_dir, "brackets_data.csv")

bracket_data = [
    ["name", "base_length", "base_width", "thickness", "vertical_height", "hole_radius", "color_r", "color_g", "color_b"],
    ["Bracket_S", "30", "20", "3", "25", "2.0", "0.2", "0.6", "0.9"],
    ["Bracket_M", "50", "30", "4", "40", "3.0", "0.3", "0.8", "0.3"],
    ["Bracket_L", "80", "40", "5", "60", "4.0", "0.9", "0.6", "0.1"],
    ["Bracket_XL", "100", "50", "6", "80", "5.0", "0.8", "0.2", "0.2"],
    ["Bracket_XXL", "120", "60", "8", "100", "6.0", "0.5", "0.2", "0.8"],
]

with open(bracket_csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(bracket_data)

print(f"[INFO] 샘플 브라켓 CSV 생성: {bracket_csv_path}")

# ---- 샘플 2: 원기둥 데이터 ----
cylinder_csv_path = os.path.join(output_dir, "cylinders_data.csv")

cylinder_data = [
    ["name", "radius", "height", "color_r", "color_g", "color_b"],
    ["Pin_S", "2", "10", "0.9", "0.3", "0.3"],
    ["Pin_M", "3", "15", "0.3", "0.9", "0.3"],
    ["Pin_L", "5", "25", "0.3", "0.3", "0.9"],
    ["Shaft_S", "4", "40", "0.7", "0.7", "0.7"],
    ["Shaft_M", "6", "60", "0.6", "0.6", "0.6"],
    ["Shaft_L", "8", "80", "0.5", "0.5", "0.5"],
    ["Roller", "10", "5", "0.8", "0.8", "0.2"],
    ["Spacer", "3", "8", "0.6", "0.8", "0.6"],
]

with open(cylinder_csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(cylinder_data)

print(f"[INFO] 샘플 원기둥 CSV 생성: {cylinder_csv_path}")

# ============================================================
# 4. CSV 읽기 유틸리티 함수
# ============================================================
def read_csv_data(filepath):
    """
    CSV 파일을 읽어 딕셔너리 리스트로 반환합니다.

    매개변수:
        filepath (str): CSV 파일 경로

    반환값:
        list[dict]: 각 행이 딕셔너리인 리스트
    """
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

# ============================================================
# 5. L-브라켓 CSV 데이터로 생성
# ============================================================
print("\n===== CSV 데이터로 브라ACKET 생성 =====")

bracket_rows = read_csv_data(bracket_csv_path)

x_offset = 0

for row in bracket_rows:
    name = row["name"]
    base_length = float(row["base_length"])
    base_width = float(row["base_width"])
    thickness = float(row["thickness"])
    vertical_height = float(row["vertical_height"])
    hole_radius = float(row["hole_radius"])
    color = (float(row["color_r"]), float(row["color_g"]), float(row["color_b"]))

    # ---- 수평면 ----
    base = Part.makeBox(base_length, base_width, thickness)

    # ---- 수직면 ----
    vertical = Part.makeBox(thickness, base_width, vertical_height)
    vertical.translate(FreeCAD.Vector(0, 0, thickness))

    # ---- 합치기 ----
    bracket = base.fuse(vertical)

    # ---- 구멍 ----
    # 수평면 구멍
    hole1 = Part.makeCylinder(hole_radius, thickness + 2)
    hole1.translate(FreeCAD.Vector(base_length * 0.25, base_width / 2, -1))
    bracket = bracket.cut(hole1)

    hole2 = Part.makeCylinder(hole_radius, thickness + 2)
    hole2.translate(FreeCAD.Vector(base_length * 0.75, base_width / 2, -1))
    bracket = bracket.cut(hole2)

    # 수직면 구멍
    hole3 = Part.makeCylinder(hole_radius, thickness + 2)
    hole3.rotate(
        FreeCAD.Vector(0, 0, 0),
        FreeCAD.Vector(0, 1, 0),
        90
    )
    hole3.translate(FreeCAD.Vector(-1, base_width / 2, thickness + vertical_height * 0.5))
    bracket = bracket.cut(hole3)

    # ---- 문서에 추가 ----
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = bracket
    obj.ViewObject.ShapeColor = color

    # 속성 추가
    obj.addProperty("App::PropertyString", "Source", "Info", "출처")
    obj.Source = "CSV"

    # 위치 이동
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()

    x_offset += base_length + 20

    print(f"  {name}: {base_length}x{base_width}x{thickness}mm, 높이 {vertical_height}mm")

print(f"==============================\n")

# ============================================================
# 6. 원기둥 CSV 데이터로 생성
# ============================================================
print("===== CSV 데이터로 원기둥 생성 =====")

cylinder_rows = read_csv_data(cylinder_csv_path)

y_offset = 80  # 브라켓과 다른 줄에 배치

for i, row in enumerate(cylinder_rows):
    name = row["name"]
    radius = float(row["radius"])
    height = float(row["height"])
    color = (float(row["color_r"]), float(row["color_g"]), float(row["color_b"]))

    # 원기둥 생성
    shape = Part.makeCylinder(radius, height)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color

    # X축을 따라 배치
    obj.Shape.translate(FreeCAD.Vector(i * 25, y_offset, 0))
    doc.recompute()

    print(f"  {name}: 반지름={radius}mm, 높이={height}mm")

print(f"==============================\n")

# ============================================================
# 7. 사용자 정의 CSV 생성 및 읽기
# ============================================================
# 사용자가 직접 만든 CSV로 부품을 생성하는 예제

custom_csv_path = os.path.join(output_dir, "custom_parts.csv")

custom_data = [
    ["name", "type", "size_a", "size_b", "size_c", "material"],
    ["Custom_Plate", "box", "100", "50", "5", "steel"],
    ["Custom_Cyl1", "cylinder", "15", "30", "0", "aluminum"],
    ["Custom_Cyl2", "cylinder", "8", "50", "0", "brass"],
    ["Custom_Cone", "cone", "20", "0", "35", "plastic"],
]

with open(custom_csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(custom_data)

print(f"[INFO] 사용자 정의 CSV 생성: {custom_csv_path}")

# ============================================================
# 8. 사용자 정의 CSV 데이터 파싱 및 생성
# ============================================================
print("\n===== 사용자 정의 CSV 처리 =====")

custom_rows = read_csv_data(custom_csv_path)

material_colors = {
    "steel":    (0.6, 0.6, 0.6),
    "aluminum": (0.8, 0.8, 0.85),
    "brass":    (0.85, 0.75, 0.3),
    "plastic":  (0.3, 0.7, 0.3),
}

x_pos = 0

for row in custom_rows:
    name = row["name"]
    part_type = row["type"]
    size_a = float(row["size_a"])
    size_b = float(row["size_b"])
    size_c = float(row["size_c"])
    material = row["material"]
    color = material_colors.get(material, (0.5, 0.5, 0.5))

    if part_type == "box":
        shape = Part.makeBox(size_a, size_b, size_c)
    elif part_type == "cylinder":
        shape = Part.makeCylinder(size_a, size_b)
    elif part_type == "cone":
        shape = Part.makeCone(size_a, 0, size_c)
    else:
        print(f"  [WARN] 알 수 없는 타입: {part_type}")
        continue

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color

    obj.addProperty("App::PropertyString", "Material", "Info", "재료")
    obj.Material = material

    obj.addProperty("App::PropertyString", "Source", "Info", "출처")
    obj.Source = "Custom_CSV"

    obj.Shape.translate(FreeCAD.Vector(x_pos, -80, 0))
    doc.recompute()

    x_pos += max(size_a, size_b) + 20

    print(f"  {name}: 타입={part_type}, 크기=({size_a},{size_b},{size_c}), 재료={material}")

print(f"==============================\n")

# ============================================================
# 9. CSV 데이터 검증
# ============================================================
print("===== CSV 데이터 검증 =====")

# 모든 CSV 파일의 행 수 확인
csv_files = [bracket_csv_path, cylinder_csv_path, custom_csv_path]
total_parts = 0

for csv_file in csv_files:
    rows = read_csv_data(csv_file)
    print(f"  {os.path.basename(csv_file)}: {len(rows)}개 부품 정의")
    total_parts += len(rows)

print(f"  총 {total_parts}개 부품 정의")
print(f"==============================\n")

# ============================================================
# 10. 전체 부품 목록 출력
# ============================================================
print("===== 생성된 전체 부품 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        mat = getattr(obj, 'Material', 'N/A')
        source = getattr(obj, 'Source', 'N/A')
        print(f"  {obj.Name}: V={vol:.1f}mm³, 재료={mat}, 출처={source}")

# ============================================================
# 11. STL 내보내기
# ============================================================
for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(output_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)

print(f"\n[INFO] STL 내보내기 완료 ({len(doc.Objects)}개 파일)")

# ============================================================
# 12. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  CSV 기반 설계 완료!")
print(f"  총 {len(doc.Objects)}개 부품 자동 생성")
print("  3개 CSV 파일 생성 (brackets, cylinders, custom)")
print("=" * 50)
print("\nPart 2 완료! 다음: Part 3 — 배치 처리와 파일 관리\n")

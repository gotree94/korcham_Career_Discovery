# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 2 - Lesson 08: 너트 생성기 (Nut Generator)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "08_nut_generator" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/08_nut_generator.py").read())

[학습 목표]
- ISO 규격 육각 너트 치수 정의
- 육각형 외부 + 원형 구멍 조합
- 규격별 너트 일괄 생성
- 워셔 포함 너트 (Flange Nut)
=============================================================
"""

import sys
import os
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

doc = FreeCAD.newDocument("NutGenerator")
print("[INFO] 새 문서 생성됨: NutGenerator")

# ============================================================
# 3. ISO 규격 너트 치수 데이터
# ============================================================
# ISO 4032 (육각 너트, 형식 1) 기준
# 치수 단위: mm

NUT_SPECS = {
    "M3": {
        "thread_diameter": 3.0,
        "pitch": 0.5,
        "width_across_flats": 5.5,     # 평면 간 너비
        "width_across_corners": 6.35,   # 꼭짓점 간 너비
        "thickness": 2.4,               # 너트 높이
    },
    "M4": {
        "thread_diameter": 4.0,
        "pitch": 0.7,
        "width_across_flats": 7.0,
        "width_across_corners": 8.08,
        "thickness": 3.2,
    },
    "M5": {
        "thread_diameter": 5.0,
        "pitch": 0.8,
        "width_across_flats": 8.0,
        "width_across_corners": 9.24,
        "thickness": 4.7,
    },
    "M6": {
        "thread_diameter": 6.0,
        "pitch": 1.0,
        "width_across_flats": 10.0,
        "width_across_corners": 11.55,
        "thickness": 5.2,
    },
    "M8": {
        "thread_diameter": 8.0,
        "pitch": 1.25,
        "width_across_flats": 13.0,
        "width_across_corners": 15.01,
        "thickness": 6.8,
    },
    "M10": {
        "thread_diameter": 10.0,
        "pitch": 1.5,
        "width_across_flats": 16.0,
        "width_across_corners": 18.48,
        "thickness": 8.4,
    },
    "M12": {
        "thread_diameter": 12.0,
        "pitch": 1.75,
        "width_across_flats": 18.0,
        "width_across_corners": 20.78,
        "thickness": 10.8,
    },
    "M16": {
        "thread_diameter": 16.0,
        "pitch": 2.0,
        "width_across_flats": 24.0,
        "width_across_corners": 27.71,
        "thickness": 14.8,
    },
    "M20": {
        "thread_diameter": 20.0,
        "pitch": 2.5,
        "width_across_flats": 30.0,
        "width_across_corners": 34.64,
        "thickness": 18.0,
    },
}

# ============================================================
# 4. 육각형 프리즘 생성 헬퍼 함수
# ============================================================
def make_hexagon_prism(width, height):
    """
    육각형 프리즘을 만듭니다.
    width: 평면 간 너비
    height: 높이
    """
    side = width / math.sqrt(3)
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = side * math.cos(angle)
        y = side * math.sin(angle)
        points.append(FreeCAD.Vector(x, y, 0))

    edges = []
    for i in range(6):
        edges.append(Part.makeLine(points[i], points[(i + 1) % 6]))

    wire = Part.Wire(edges)
    face = Part.Face(wire)
    prism = face.extrude(FreeCAD.Vector(0, 0, height))

    return prism

# ============================================================
# 5. 너트 생성 함수
# ============================================================
def create_nut(name, spec, color=(0.7, 0.7, 0.7), flange=False):
    """
    육각 너트를 생성합니다.

    매개변수:
        name  (str)  : 객체 이름
        spec  (dict) : 너트 규격 딕셔너리
        color (tuple): RGB 색상
        flange (bool): 워셔형 베이스 포함 여부

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    d = spec["thread_diameter"]
    w = spec["width_across_flats"]
    h = spec["thickness"]
    hole_r = d / 2

    # ---- 1. 육각형 외부 생성 ----
    hex_body = make_hexagon_prism(w, h)

    # ---- 2. 원형 구멍 뚫기 ----
    hole = Part.makeCylinder(hole_r, h + 2)
    hole.translate(FreeCAD.Vector(0, 0, -1))  # 관통을 위해 약간 아래로
    nut = hex_body.cut(hole)

    # ---- 3. 워셔형 베이스 (옵션) ----
    if flange:
        flange_r = w * 0.7  # 워셔 반지름
        flange_h = 1.5      # 워셔 두께
        flange_disk = Part.makeCylinder(flange_r, flange_h)
        flange_disk.translate(FreeCAD.Vector(0, 0, -flange_h))

        # 워셔에 구멍 뚫기
        flange_hole = Part.makeCylinder(hole_r, flange_h + 2)
        flange_hole.translate(FreeCAD.Vector(0, 0, -flange_h - 1))
        flange_disk = flange_disk.cut(flange_hole)

        # 너트와 워셔 합치기
        nut = nut.fuse(flange_disk)

    # ---- 4. 모서리 처리 (선택) ----
    # 상단 모서리에 약간의 Chamfer 적용 시도
    try:
        # 육각형 상단 에지에 Chamfer
        edges_to_chamfer = []
        for edge in nut.Edges:
            # z 좌표가 h 근처인 상단 에지 선택
            if hasattr(edge, 'Vertexes') and len(edge.Vertexes) >= 2:
                z_vals = [v.Point.z for v in edge.Vertexes]
                if all(abs(z - h) < 0.01 for z in z_vals):
                    edges_to_chamfer.append(edge)

        # Chamfer 적용 (0.3mm)
        if edges_to_chamfer:
            nut = nut.makeChamfer(0.3, edges_to_chamfer)
    except:
        pass  # Chamfer 실패 시 무시

    # ---- 5. 문서에 추가 ----
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = nut
    obj.ViewObject.ShapeColor = color

    # 커스텀 속성
    obj.addProperty("App::PropertyString", "NutSpec", "Info", "너트 규격")
    obj.NutSpec = name.split("_")[0]

    obj.addProperty("App::PropertyFloat", "NutThickness", "Dimensions", "너트 두께")
    obj.NutThickness = h

    obj.addProperty("App::PropertyBool", "HasFlange", "Info", "워셔 포함 여부")
    obj.HasFlange = flange

    return obj

# ============================================================
# 6. 규격별 너트 일괄 생성
# ============================================================
print("\n===== 규격별 육각 너트 일괄 생성 =====")

x_offset = 0
colors = [
    (0.7, 0.7, 0.7),   # 은색 (기본)
    (0.65, 0.65, 0.65),
    (0.75, 0.75, 0.75),
]

for i, (spec_name, spec_data) in enumerate(NUT_SPECS.items()):
    obj = create_nut(
        name=f"{spec_name}_Nut",
        spec=spec_data,
        color=colors[i % len(colors)]
    )

    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()

    x_offset += spec_data["width_across_flats"] + 15

    print(f"  {spec_name}: 너비={spec_data['width_across_flats']}mm, "
          f"두께={spec_data['thickness']}mm, "
          f"구멍={spec_data['thread_diameter']}mm")

print(f"==============================\n")

# ============================================================
# 7. 워셔형 너트 (Flange Nut) 생성
# ============================================================
print("===== 워셔형 너트 (Flange Nut) 생성 =====")

for spec_name in ["M6", "M8", "M10"]:
    spec_data = NUT_SPECS[spec_name]
    obj = create_nut(
        name=f"{spec_name}_FlangeNut",
        spec=spec_data,
        color=(0.6, 0.6, 0.5),
        flange=True
    )
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()
    x_offset += spec_data["width_across_flats"] + 20

    print(f"  {spec_name} Flange Nut: 베이스 포함")

print(f"==============================\n")

# ============================================================
# 8. 잠금 너트 (Lock Nut) — 높이가 절반인 너트
# ============================================================
print("===== 잠금 너트 (Lock Nut) =====")

lock_nut_specs = {
    "M6_Lock": {"thread_diameter": 6, "width_across_flats": 10, "thickness": 3.0},
    "M8_Lock": {"thread_diameter": 8, "width_across_flats": 13, "thickness": 4.0},
    "M10_Lock": {"thread_diameter": 10, "width_across_flats": 16, "thickness": 5.0},
}

for name, spec in lock_nut_specs.items():
    # 잠금 너트는 일반 너트보다 얇음
    obj = create_nut(
        name=name,
        spec=spec,
        color=(0.8, 0.75, 0.5)  # 금색
    )
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()
    x_offset += spec["width_across_flats"] + 15

    print(f"  {name}: 두께={spec['thickness']}mm (일반 너트의 ~60%)")

print(f"==============================\n")

# ============================================================
# 9. 전체 너트 목록 출력
# ============================================================
print("===== 전체 너트 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        spec = getattr(obj, 'NutSpec', 'N/A')
        thickness = getattr(obj, 'NutThickness', 'N/A')
        has_flange = getattr(obj, 'HasFlange', False)
        flange_str = " (Flange)" if has_flange else ""
        print(f"  {obj.Name}: 규격={spec}, V={vol:.1f}mm³{flange_str}")

# ============================================================
# 10. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)

print(f"\n[INFO] STL 내보내기 완료 ({len(doc.Objects)}개 파일)")

# ============================================================
# 11. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

total_nuts = len(doc.Objects)
print("\n" + "=" * 50)
print("  너트 생성기 완료!")
print(f"  총 {total_nuts}개 너트 생성")
print("  (일반 너트 + 워셔형 + 잠금 너트)")
print("=" * 50)
print("\n다음 단계: 09_washer_series.py — 와셔 시리즈\n")

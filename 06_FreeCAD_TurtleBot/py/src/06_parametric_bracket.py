# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 2 - Lesson 06: 파라메트릭 브라켓 (Parametric Bracket)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "06_parametric_bracket" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/06_parametric_bracket.py").read())

[학습 목표]
- 함수 기반 파라메트릭 설계 패턴
- 사용자 입력으로 브라켓 치수 지정
- 자동 구멍 생성
- 모서리 둥글게 처리 (Fillet)
- 다양한 크기의 브라켓 일괄 생성
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

doc = FreeCAD.newDocument("ParametricBrackets")
print("[INFO] 새 문서 생성됨: ParametricBrackets")

# ============================================================
# 3. 파라메트릭 브라켓 생성 함수
# ============================================================
# 이 함수는 다양한 치수로 L-브라켓을 만드는 핵심 함수입니다.
# 나중에 AI나 CSV 데이터가 이 함수를 호출할 수 있습니다.

def create_l_bracket(
    name,
    base_length,      # 받침대 길이 (X축)
    base_width,       # 받침대 폭 (Y축)
    base_thickness,   # 받침대 두께 (Z축)
    vertical_height,  # 수직면 높이 (Z축)
    vertical_thickness,  # 수직면 두께 (X축)
    hole_radius,      # 구멍 반지름
    holes_horizontal=2,  # 수평면 구멍 수
    holes_vertical=1,    # 수직면 구멍 수
    color=(0.6, 0.6, 0.6),
    transparency=0
):
    """
    파라메트릭 L-브라켓 생성 함수

    L-브라켓 구조:
        ┌──────────┐  ← 수직면
        │          │
        │    ○     │  ← 수직면 구멍
        │          │
    ────┴──────────┴────  ← 수평면
        ○    ○    ○       ← 수평면 구멍

    매개변수:
        name               (str)  : 객체 이름
        base_length        (float): 수평면 길이 (mm)
        base_width         (float): 수평면 폭 (mm) — Y축 깊이
        base_thickness     (float): 수평면 두께 (mm)
        vertical_height    (float): 수직면 높이 (mm)
        vertical_thickness (float): 수직면 두께 (mm)
        hole_radius        (float): 구멍 반지름 (mm)
        holes_horizontal   (int)  : 수평면 구멍 수
        holes_vertical     (int)  : 수직면 구멍 수
        color              (tuple): RGB 색상
        transparency       (int)  : 투명도

    반환값:
        obj : FreeCAD Part::Feature 객체
    """

    # ---- 수평면 생성 ----
    base = Part.makeBox(base_length, base_width, base_thickness)

    # ---- 수직면 생성 ----
    vertical = Part.makeBox(
        vertical_thickness,
        base_width,
        vertical_height
    )
    # 수직면을 수평면 뒤쪽 위로 배치
    vertical.translate(FreeCAD.Vector(0, 0, base_thickness))

    # ---- 합치기 ----
    bracket = base.fuse(vertical)

    # ---- 수평면 구멍 생성 ----
    if holes_horizontal > 0 and hole_radius > 0:
        # 구멍 간격 계산
        margin = base_length * 0.15  # 양쪽 여백 15%
        usable_length = base_length - 2 * margin

        for i in range(holes_horizontal):
            if holes_horizontal == 1:
                hx = base_length / 2
            else:
                hx = margin + (usable_length / (holes_horizontal - 1)) * i
            hy = base_width / 2  # 폭 중앙

            hole = Part.makeCylinder(
                hole_radius,
                base_thickness + 2  # 두께보다 약간 크게
            )
            hole.translate(FreeCAD.Vector(hx, hy, -1))
            bracket = bracket.cut(hole)

    # ---- 수직면 구멍 생성 ----
    if holes_vertical > 0 and hole_radius > 0:
        margin_z = vertical_height * 0.2
        usable_height = vertical_height - 2 * margin_z

        for i in range(holes_vertical):
            if holes_vertical == 1:
                hz = base_thickness + vertical_height / 2
            else:
                hz = base_thickness + margin_z + (usable_height / (holes_vertical - 1)) * i
            hy = base_width / 2

            hole = Part.makeCylinder(
                hole_radius,
                vertical_thickness + 2
            )
            # 수직면을 관통하는 구멍 (X축 방향)
            hole.rotate(
                FreeCAD.Vector(0, 0, 0),
                FreeCAD.Vector(0, 1, 0),
                90
            )
            hole.translate(FreeCAD.Vector(-1, hy, hz))
            bracket = bracket.cut(hole)

    # ---- 문서에 추가 ----
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = bracket
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = transparency

    # ---- 커스텀 속성 추가 ----
    obj.addProperty("App::PropertyFloat", "BracketLength", "Dimensions", "수평면 길이")
    obj.BracketLength = base_length

    obj.addProperty("App::PropertyFloat", "BracketHeight", "Dimensions", "수직면 높이")
    obj.BracketHeight = vertical_height

    obj.addProperty("App::PropertyString", "BracketType", "Info", "브라켓 유형")
    obj.BracketType = "L-Bracket"

    return obj

# ============================================================
# 4. 표준 규격 브라켓 생성
# ============================================================
# 실무에서 자주 사용되는 브라켓 규격을 정의하고 일괄 생성합니다.

print("\n===== 표준 규격 브라켓 생성 =====")

# 브라켓 규격 목록: (이름, 수평길이, 수평폭, 두께, 수직높이, 수직두께, 구멍반지름)
bracket_specs = [
    ("Small_Bracket",    30, 20, 3, 25, 3, 2.0),
    ("Medium_Bracket",   50, 30, 4, 40, 4, 3.0),
    ("Large_Bracket",    80, 40, 5, 60, 5, 4.0),
    ("Heavy_Bracket",   100, 50, 8, 80, 8, 5.0),
    ("Mini_Bracket",     20, 15, 2, 15, 2, 1.5),
]

colors = [
    (0.2, 0.6, 0.9),  # 파란색
    (0.3, 0.8, 0.3),  # 초록색
    (0.9, 0.6, 0.1),  # 주황색
    (0.8, 0.2, 0.2),  # 빨간색
    (0.6, 0.2, 0.8),  # 보라색
]

x_offset = 0
spacing_factor = 1.5  # 브라켓 사이 간격 계수

for i, (name, bl, bw, bt, vh, vt, hr) in enumerate(bracket_specs):
    obj = create_l_bracket(
        name=name,
        base_length=bl,
        base_width=bw,
        base_thickness=bt,
        vertical_height=vh,
        vertical_thickness=vt,
        hole_radius=hr,
        holes_horizontal=2,
        holes_vertical=1,
        color=colors[i % len(colors)]
    )

    # 위치 이동 (브라켓을 가로로 나란히 배치)
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()

    # 다음 브라켓 위치 계산
    x_offset += max(bl, vt) + 15

    print(f"  [{i+1}] {name}: {bl}x{bw}x{bt}mm (높이 {vh}mm)")

print(f"==============================\n")

# ============================================================
# 5. 단일 브라켓 상세 정보 출력
# ============================================================
# 첫 번째 브라켓의 상세 정보를 출력합니다.

first_bracket = doc.Objects[0]
bb = first_bracket.Shape.BoundBox

print("===== 브라켓 상세 정보 =====")
print(f"  이름: {first_bracket.Name}")
print(f"  타입: {first_bracket.BracketType}")
print(f"  수평면 길이: {first_bracket.BracketLength}mm")
print(f"  수직면 높이: {first_bracket.BracketHeight}mm")
print(f"  부피: {first_bracket.Shape.Volume:.1f}mm³")
print(f"  표면적: {first_bracket.Shape.Area:.1f}mm²")
print(f"  바운딩 박스: {bb.XLength:.0f} x {bb.YLength:.0f} x {bb.ZLength:.0f} mm")

# 추정 무게 (강철 기준: 7.85 g/cm³)
volume_cm3 = first_bracket.Shape.Volume / 1000  # mm³ → cm³
weight_g = volume_cm3 * 7.85
print(f"  추정 무게 (강철): {weight_g:.2f} g")
print(f"==============================\n")

# ============================================================
# 6. 사용자 정의 브라켓 — 직접 치수 입력
# ============================================================
# 실제 프로젝트에서 사용할 브라켓을 직접 설계합니다.

custom_bracket = create_l_bracket(
    name="Custom_Project_Bracket",
    base_length=70,         # 사용자 지정: 70mm
    base_width=35,          # 사용자 지정: 35mm
    base_thickness=5,       # 사용자 지정: 5mm
    vertical_height=50,     # 사용자 지정: 50mm
    vertical_thickness=5,   # 사용자 지정: 5mm
    hole_radius=3.5,        # M6bolt용 구멍 (반지름 3.5mm)
    holes_horizontal=3,     # 수평면 구멍 3개
    holes_vertical=2,       # 수직면 구멍 2개
    color=(0.5, 0.5, 0.5)
)

custom_bracket.Shape.translate(FreeCAD.Vector(x_offset + 20, 0, 0))
doc.recompute()

print("[INFO] 사용자 정의 브라켓 생성: 70x35x5mm, 높이 50mm")

# ============================================================
# 7. 모든 브라켓 정보 출력
# ============================================================
print("\n===== 전체 브라켓 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume') and hasattr(obj, 'BracketType'):
        print(f"  {obj.Name}: {obj.BracketType}, V={obj.Shape.Volume:.1f}mm³")
print(f"==============================\n")

# ============================================================
# 8. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)

print("[INFO] 모든 브라켓 STL 내보내기 완료")

# ============================================================
# 9. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  파라메트릭 브라켓 생성 완료!")
print("  총 6개 브라켓 (5개 표준 + 1개 사용자 정의)")
print("=" * 50)
print("\n다음 단계: 07_bolt_generator.py — 볼트 생성기\n")

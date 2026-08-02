# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 1 - Lesson 02: 원기둥 (Cylinder)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "02_cylinder" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/02_cylinder.py").read())

[학습 목표]
- Part.makeCylinder() 로 원기둥 생성
- 반지름과 높이를 파라메트릭으로 제어
- 각도를 지정하여 부채꼴 모양 원기둥 생성
- Multiple 원기둥 비교 시각화
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
    print("[ERROR] FreeCAD 모듈을 찾을 수 없습니다. FreeCAD에서 실행해 주세요.")
    sys.exit(1)

# ============================================================
# 2. 새 문서 생성
# ============================================================
if FreeCAD.ActiveDocument:
    FreeCAD.closeDocument(FreeCAD.ActiveDocument.Name)

doc = FreeCAD.newDocument("CylinderExamples")
print("[INFO] 새 문서 생성됨: CylinderExamples")

# ============================================================
# 3. 기본 원기둥 생성
# ============================================================
# Part.makeCylinder(반지름, 높이)
# 단위: mm (FreeCAD 기본 단위)
# 원점(0,0,0)에서 Z축을 중심으로 생성됩니다.

radius = 15      # 반지름: 15mm (지름 30mm)
height = 40      # 높이: 40mm

cylinder1 = Part.makeCylinder(radius, height)

# 문서에 추가
obj1 = doc.addObject("Part::Feature", "BasicCylinder")
obj1.Shape = cylinder1
obj1.ViewObject.ShapeColor = (0.2, 0.8, 0.3)  # 초록색

print(f"[INFO] 기본 원기둥: 반지름={radius}mm, 높이={height}mm")

# ============================================================
# 4. 각도를 지정한 원기둥 (부채꼴)
# ============================================================
# Part.makeCylinder(반지름, 높이, Vector(원점), Vector(방향), 각도)
# 각도는 도(degree) 단위이며, 360도보다 작으면 부채꼴이 됩니다.

partial_radius = 20
partial_height = 30
partial_angle = 120  # 120도 부채꼴

# 부채꼴 원기둥 생성
cylinder2 = Part.makeCylinder(
    partial_radius,              # 반지름
    partial_height,              # 높이
    FreeCAD.Vector(0, 0, 0),    # 시작점 (원점)
    FreeCAD.Vector(0, 0, 1),    # 방향 (Z축)
    math.radians(partial_angle)  # 각도 (라디안으로 변환)
)

obj2 = doc.addObject("Part::Feature", "PartialCylinder")
obj2.Shape = cylinder2
obj2.ViewObject.ShapeColor = (1.0, 0.5, 0.0)  # 주황색

print(f"[INFO] 부채꼴 원기둥: 반지름={partial_radius}mm, 높이={partial_height}mm, 각도={partial_angle}°")

# ============================================================
# 5. 이동된 원기둥 — 위치 제어
# ============================================================
# 원기둥을 생성한 후 .translate() 로 위치를 이동할 수 있습니다.
# 또는 makeCylinder 의 Vector 파라미터로 시작점을 지정합니다.

moved_cylinder = Part.makeCylinder(10, 25)
moved_cylinder.translate(FreeCAD.Vector(40, 0, 0))  # X축으로 40mm 이동

obj3 = doc.addObject("Part::Feature", "MovedCylinder")
obj3.Shape = moved_cylinder
obj3.ViewObject.ShapeColor = (0.8, 0.2, 0.2)  # 빨간색

print(f"[INFO] 이동된 원기둥: X축 +40mm")

# ============================================================
# 6. 파라메트릭 원기둥 함수
# ============================================================
# 재사용 가능한 함수로 원기둥을 생성합니다.
# 나중에 AI나 CSV 데이터로 이 함수를 호출할 수 있습니다.

def create_cylinder(name, radius, height, color, x=0, y=0, z=0):
    """
    파라메트릭 원기둥 생성 함수

    매개변수:
        name   (str)  : 객체 이름
        radius (float): 반지름 (mm)
        height (float): 높이 (mm)
        color  (tuple): RGB 색상 (0.0~1.0)
        x, y, z(float): 시작점 좌표 (mm)

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    # 원기둥 생성
    shape = Part.makeCylinder(radius, height)

    # 시작점이 원점이 아니면 이동
    if x != 0 or y != 0 or z != 0:
        shape.translate(FreeCAD.Vector(x, y, z))

    # 문서에 추가
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color

    return obj

# ============================================================
# 7. 함수를 이용한 다중 원기둥 생성
# ============================================================
# 다양한 크기의 원기둥을 한 번에 생성합니다.

# 규격별 원기둥 데이터: (이름, 반지름, 높이, R, G, B)
cylinder_specs = [
    ("Small",    5,  15, (0.9, 0.2, 0.2)),   # 소형 - 빨간색
    ("Medium",  10,  25, (0.2, 0.9, 0.2)),   # 중형 - 초록색
    ("Large",   20,  40, (0.2, 0.2, 0.9)),   # 대형 - 파란색
    ("Tall",     8,  60, (0.9, 0.9, 0.1)),   # 높은 - 노란색
    ("Wide",    25,  10, (0.9, 0.2, 0.9)),   # 넓은 - 보라색
]

# 각 원기둥을 X축 방향으로 일정 간격으로 배치
spacing = 60  # 원기둥 사이 간격

print("\n===== 규격별 원기둥 생성 =====")
for i, (name, r, h, (cr, cg, cb)) in enumerate(cylinder_specs):
    x_offset = i * spacing  # X축 간격
    obj = create_cylinder(
        name=f"{name}Cyl",
        radius=r,
        height=h,
        color=(cr, cg, cb),
        x=x_offset,
        y=0,
        z=0
    )
    print(f"  [{i+1}] {name}: 반지름={r}mm, 높이={h}mm, 위치=({x_offset}, 0, 0)")

print(f"==============================\n")

# ============================================================
# 8. 빈 원기둥 (Pipe / 파이프)
# ============================================================
# Part.makeCylinder()로 바깥 원기둥을 만들고,
# makeCylinder()로 안쪽 원기��을 잘라내어 파이프를 만듭니다.

outer_radius = 20
inner_radius = 15
pipe_height = 35

# 바깥 원기둥
outer = Part.makeCylinder(outer_radius, pipe_height)
# 안쪽 원기둥 (구멍)
inner = Part.makeCylinder(inner_radius, pipe_height)

# 빼기 연산 (Cut) — 바깥에서 안쪽을 뺍니다
pipe = outer.cut(inner)

obj_pipe = doc.addObject("Part::Feature", "Pipe")
obj_pipe.Shape = pipe
obj_pipe.ViewObject.ShapeColor = (0.5, 0.5, 0.5)  # 회색
obj_pipe.ViewObject.Transparency = 30  # 30% 투명

print(f"[INFO] 파이프 생성: 바깥={outer_radius}mm, 안쪽={inner_radius}mm, 높이={pipe_height}mm")

# ============================================================
# 9. 치수 정보 출력
# ============================================================
print("\n===== 생성된 원기둥 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        area = obj.Shape.Area
        bb = obj.Shape.BoundBox
        print(f"  {obj.Name}: 부피={vol:.1f}mm³, 표면적={area:.1f}mm², "
              f"크기=({bb.XLength:.0f}x{bb.YLength:.0f}x{bb.ZLength:.0f})mm")

# ============================================================
# 10. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

stl_path = os.path.join(export_dir, "cylinders_example.stl")

# 전체 문서를 하나의 STL로 내보내기
# FreeCAD 에서는 각 객체를 개별적으로 내보내는 것이 일반적입니다.
for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)
        print(f"[INFO] STL 내보내기: {filepath}")

# ============================================================
# 11. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  원기둥 예제 생성 완료!")
print("  총 7개 원기둥 (기본, 부채꼴, 이동, 5개 규격, 파이프)")
print("=" * 50)
print("\n다음 단계: 03_sphere.py — 구 만들기\n")

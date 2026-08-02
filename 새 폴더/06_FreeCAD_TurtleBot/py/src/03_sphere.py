# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 1 - Lesson 03: 구 (Sphere)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "03_sphere" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/03_sphere.py").read())

[학습 목표]
- Part.makeSphere() 로 구 생성
- 반지름을 파라메트릭으로 제어
- 부채꼴 구 (Sphere Segment) 생성
- 구를 이용한 복합 구조물
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

doc = FreeCAD.newDocument("SphereExamples")
print("[INFO] 새 문서 생성됨: SphereExamples")

# ============================================================
# 3. 기본 구 생성
# ============================================================
# Part.makeSphere(반지름)
# 원점(0,0,0)을 중심으로 하는 완전한 구를 만듭니다.
# 단위: mm

radius = 20  # 반지름 20mm (지름 40mm)

sphere1 = Part.makeSphere(radius)

obj1 = doc.addObject("Part::Feature", "BasicSphere")
obj1.Shape = sphere1
obj1.ViewObject.ShapeColor = (0.2, 0.5, 0.9)  # 파란색

print(f"[INFO] 기본 구: 반지름={radius}mm")

# ============================================================
# 4. 파라메트릭 구 함수
# ============================================================
def create_sphere(name, radius, color, x=0, y=0, z=0, transparency=0):
    """
    파라메트릭 구 생성 함수

    매개변수:
        name         (str)  : 객체 이름
        radius       (float): 반지름 (mm)
        color        (tuple): RGB 색상
        x, y, z     (float): 중심 좌표
        transparency (int)  : 투명도 (0~100)

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    shape = Part.makeSphere(radius)

    # 중심점 이동
    if x != 0 or y != 0 or z != 0:
        shape.translate(FreeCAD.Vector(x, y, z))

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = transparency

    return obj

# ============================================================
# 5. 다양한 크기의 구 생성
# ============================================================
# X축을 따라 크기가 다른 구들을 배치합니다.

sphere_specs = [
    ("Tiny",      5,  (0.9, 0.3, 0.3)),  # 아주 작은 구
    ("Small",    10,  (0.3, 0.9, 0.3)),  # 작은 구
    ("Medium",   18,  (0.3, 0.3, 0.9)),  # 중간 구
    ("Large",    28,  (0.9, 0.9, 0.3)),  # 큰 구
]

spacing = 75  # 구 사이 간격

print("\n===== 규격별 구 생성 =====")
for i, (name, r, (cr, cg, cb)) in enumerate(sphere_specs):
    x_offset = i * spacing
    obj = create_sphere(
        name=f"{name}Sphere",
        radius=r,
        color=(cr, cg, cb),
        x=x_offset
    )
    print(f"  [{i+1}] {name}: 반지름={r}mm, 위치=({x_offset}, 0, 0)")
print(f"==========================\n")

# ============================================================
# 6. 부채꼴 구 (Sphere Segment)
# ============================================================
# Part.makeSphere(반지름, Vector(원점), Vector(방향), 시작각도, 끝각도, 시작방위각, 끝방위각)
# 두 개의 각도 범위를 지정하여 구의 일부분만 만들 수 있습니다.

# 위쪽 반구 (Z > 0 영역)
# 시작각도: 0도 (최하단), 끝각도: 90도 (적도)
upper_hemi = Part.makeSphere(
    15,                             # 반지름
    FreeCAD.Vector(0, 0, 0),       # 중심점
    FreeCAD.Vector(0, 0, 1),       # 기준 방향 (Z축)
    0,                               # 시작 각도 (라디안이 아닌 도 단위)
    math.radians(90),               # 끝 각도
    0,                               # 시작 방위각
    math.radians(360)               # 끝 방위각
)

obj_upper = doc.addObject("Part::Feature", "UpperHemisphere")
obj_upper.Shape = upper_hemi
obj_upper.ViewObject.ShapeColor = (0.9, 0.4, 0.1)  # 주황색
obj_upper.ViewObject.Transparency = 40

print("[INFO] 위쪽 반구 생성됨")

# ============================================================
# 7. 구 뚫기 (도넛/링 형태)
# ============================================================
# 큰 구에서 작은 구를 빼내어 구멍이 뚫린 형태를 만듭니다.

outer = Part.makeSphere(25)    # 바깥 구
inner = Part.makeSphere(15)    # 안쪽 구 (구멍용)

# 구멍 뚫기 (Cut 연산)
holed_sphere = outer.cut(inner)

# 위치 이동
holed_sphere.translate(FreeCAD.Vector(250, 0, 0))

obj_holed = doc.addObject("Part::Feature", "HoledSphere")
obj_holed.Shape = holed_sphere
obj_holed.ViewObject.ShapeColor = (0.6, 0.2, 0.8)  # 보라색
obj_holed.ViewObject.Transparency = 50

print("[INFO] 구멍 뚫린 구 생성됨 (반지름 25mm, 구멍 15mm)")

# ============================================================
# 8. 점 구조 — 구를 격자로 배치
# ============================================================
# 작은 구들을 3D 격자에 배치하여 분자 구조 같은 형태를 만듭니다.

small_r = 3      # 작은 구 반지름
grid_count = 3   # 각 축에 3개
grid_gap = 20    # 격자 간격

print("\n===== 3D 격자 구 배치 =====")
for xi in range(grid_count):
    for yi in range(grid_count):
        for zi in range(grid_count):
            x = xi * grid_gap
            y = yi * grid_gap
            z = zi * grid_gap

            # 색상: 위치에 따라 그라데이션
            cr = xi / (grid_count - 1)
            cg = yi / (grid_count - 1)
            cb = zi / (grid_count - 1)

            create_sphere(
                name=f"Atom_{xi}{yi}{zi}",
                radius=small_r,
                color=(cr, cg, cb),
                x=x, y=y, z=z,
                transparency=30
            )

total_atoms = grid_count ** 3
print(f"  총 {total_atoms}개 구 생성 (격자: {grid_count}x{grid_count}x{grid_count})")
print(f"  격자 간격: {grid_gap}mm, 구 반지름: {small_r}mm")
print(f"============================\n")

# ============================================================
# 9. 치수 정보 출력
# ============================================================
print("===== 구 정보 요약 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        area = obj.Shape.Area
        bb = obj.Shape.BoundBox
        print(f"  {obj.Name}: V={vol:.1f}mm³, S={area:.1f}mm², "
              f" 크기=({bb.XLength:.0f}x{bb.YLength:.0f}x{bb.ZLength:.0f})mm")

# ============================================================
# 10. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)
        print(f"[INFO] STL: {filepath}")

# ============================================================
# 11. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  구 예제 생성 완료!")
print("  기본 구, 반구, 구멍 구, 3D 격자 구")
print("=" * 50)
print("\n다음 단계: 04_cone.py — 원뿔 만들기\n")

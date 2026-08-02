# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 1 - Lesson 04: 원뿔 (Cone)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "04_cone" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/04_cone.py").read())

[학습 목표]
- Part.makeCone() 로 원뿔 생성
- 상단/하단 반경 제어 (원뿔 vs 원대)
- 각도를 지정한 부채꼴 원뿔
- 원뿔를 이용한 복합 구조물 (☌, 깔때기 등)
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

doc = FreeCAD.newDocument("ConeExamples")
print("[INFO] 새 문서 생성됨: ConeExamples")

# ============================================================
# 3. 기본 원뿔 생성
# ============================================================
# Part.makeCone(하단반지름, 상단반지름, 높이)
#
# - 하단반지름 > 0, 상단반지름 = 0 : 뾰족한 원뿔
# - 하단반지름 > 0, 상단반지름 > 0 : 원대(Frustum)
# - 하단반지름 = 상단반지름        : 원기둥과 동일

bottom_radius = 20   # 하단 반지름: 20mm
top_radius = 0       # 상단 반지름: 0mm (뾰족)
height = 40          # 높이: 40mm

cone1 = Part.makeCone(bottom_radius, top_radius, height)

obj1 = doc.addObject("Part::Feature", "BasicCone")
obj1.Shape = cone1
obj1.ViewObject.ShapeColor = (0.9, 0.3, 0.3)  # 빨간색

print(f"[INFO] 기본 원뿔: 하단반지름={bottom_radius}mm, 상단반지름={top_radius}mm, 높이={height}mm")

# ============================================================
# 4. 원대(Frustum) 생성
# ============================================================
# 상단 반지름이 0보다 크면 원뿔이 뚫려서 원대 형태가 됩니다.

frustum_bottom = 25   # 하단 반지름
frustum_top = 10      # 상단 반지름
frustum_height = 35   # 높이

frustum = Part.makeCone(frustum_bottom, frustum_top, frustum_height)

# 위치 이동
frustum.translate(FreeCAD.Vector(60, 0, 0))

obj2 = doc.addObject("Part::Feature", "Frustum")
obj2.Shape = frustum
obj2.ViewObject.ShapeColor = (0.3, 0.8, 0.3)  # 초록색

print(f"[INFO] 원대: 하단={frustum_bottom}mm, 상단={frustum_top}mm, 높이={frustum_height}mm")

# ============================================================
# 5. 파라메트릭 원뿔 함수
# ============================================================
def create_cone(name, bottom_r, top_r, height, color,
                angle=360, x=0, y=0, z=0, transparency=0):
    """
    파라메트릭 원뿔/원대 생성 함수

    매개변수:
        name      (str)  : 객체 이름
        bottom_r  (float): 하단 반지름 (mm)
        top_r     (float): 상단 반지름 (mm), 0이면 뾰족
        height    (float): 높이 (mm)
        color     (tuple): RGB 색상
        angle     (float): 부채꼴 각도 (0~360), 기본 360
        x, y, z  (float): 하단 중심 좌표
        transparency (int): 투명도 (0~100)

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    # 각도가 360도 미만이면 부채꼴 원뿔 생성
    if angle < 360:
        shape = Part.makeCone(
            bottom_r, top_r, height,
            FreeCAD.Vector(0, 0, 0),    # 시작점
            FreeCAD.Vector(0, 0, 1),    # 방향 (Z축)
            math.radians(angle)          # 각도 (라디안)
        )
    else:
        shape = Part.makeCone(bottom_r, top_r, height)

    # 위치 이동
    if x != 0 or y != 0 or z != 0:
        shape.translate(FreeCAD.Vector(x, y, z))

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.ViewObject.Transparency = transparency

    return obj

# ============================================================
# 6. 다양한 원뿔 시리즈
# ============================================================

cone_specs = [
    # (이름, 하단반지름, 상단반지름, 높이, RGB)
    ("SharpCone",   15,  0, 45, (0.9, 0.2, 0.2)),  # 뾰족 원뿔
    ("WideCone",    30,  0, 20, (0.2, 0.7, 0.9)),  # 넓고 낮은 원뿔
    ("TallCone",     8,  0, 60, (0.9, 0.9, 0.2)),  # 높고 가느다란 원뿔
    ("Frustum1",    25, 15, 30, (0.6, 0.2, 0.8)),  # 원대 1
    ("Frustum2",    20,  5, 40, (0.2, 0.8, 0.5)),  # 원대 2
]

spacing = 70

print("\n===== 원뿔 시리즈 생성 =====")
for i, (name, br, tr, h, (cr, cg, cb)) in enumerate(cone_specs):
    x_offset = i * spacing
    create_cone(
        name=name,
        bottom_r=br,
        top_r=tr,
        height=h,
        color=(cr, cg, cb),
        x=x_offset
    )
    shape_type = "원대" if tr > 0 else "원뿔"
    print(f"  [{i+1}] {name} ({shape_type}): 하단={br}mm, 상단={tr}mm, 높이={h}mm")
print(f"============================\n")

# ============================================================
# 7. 부채꼴 원뿔
# ============================================================
# 120도 부채꼴 원뿔 3개를 회전시켜 붙이면 꽃잎 형태를 만들 수 있습니다.

petal_count = 3
petal_angle = 360 / petal_count  # 120도

print("===== 부채꼴 원뿔 (꽃잎) =====")
for i in range(petal_count):
    angle_offset = i * petal_angle
    obj = create_cone(
        name=f"Petal_{i}",
        bottom_r=18,
        top_r=0,
        height=30,
        color=(0.9, 0.3 - i*0.1, 0.5 + i*0.1),
        angle=petal_angle - 5,  # 약간 간격
        transparency=40
    )
    # Z축 주위 회전 (위에서 아래로 바라보면 회전됨)
    # FreeCAD 회전: rotate(Vector(축시작), Vector(축끝), 각도)
    obj.Shape.rotate(
        FreeCAD.Vector(0, 0, 0),  # 회전 중심
        FreeCAD.Vector(0, 0, 1),  # 회전 축 (Z축)
        angle_offset               # 회전 각도 (도)
    )
    doc.recompute()
    print(f"  꽃잎 {i+1}: 각도={angle_offset:.0f}°, 크기={petal_angle-5:.0f}°")

print(f"============================\n")

# ============================================================
# 8. 깔때기 형태 (反转 원대)
# ============================================================
# 위쪽이 넓고 아래쪽이 좁은 깔때기 모양을 만듭니다.
# 이것은 원대를 180도 회전하여 뒤집는 것으로 구현합니다.

funnel_top = 30       # 상단 반지름 (넓은 부분)
funnel_bottom = 5     # 하단 반지름 (좁은 부분)
funnel_height = 25    # 높이

funnel = Part.makeCone(funnel_bottom, funnel_top, funnel_height)
# Z축 방향으로 위로 이동
funnel.translate(FreeCAD.Vector(0, 0, 50))

obj_funnel = doc.addObject("Part::Feature", "Funnel")
obj_funnel.Shape = funnel
obj_funnel.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
obj_funnel.ViewObject.Transparency = 40

print(f"[INFO] 깔때기: 상단={funnel_top}mm, 하단={funnel_bottom}mm, 높이={funnel_height}mm")

# ============================================================
# 9. 원뿔 + 원기둥 조합 (나사산 기본 형태)
# ============================================================
# 하단에 원기둥, 상단에 원뿔을 결합합니다.

shaft_radius = 6
shaft_height = 20
tip_radius = 0
tip_height = 10

# 원기둥 (축)
shaft = Part.makeCylinder(shaft_radius, shaft_height)

# 원뿔 (팁)
tip = Part.makeCone(shaft_radius, tip_radius, tip_height)
tip.translate(FreeCAD.Vector(0, 0, shaft_height))  # 원기둥 위에 배치

# 합치기 (Fuse)
combined = shaft.fuse(tip)

obj_combined = doc.addObject("Part::Feature", "ShaftWithTip")
obj_combined.Shape = combined
obj_combined.ViewObject.ShapeColor = (0.7, 0.5, 0.3)

print(f"[INFO] 축+팁 조합: 원기둥 높이={shaft_height}mm, 원뿔 높이={tip_height}mm")

# ============================================================
# 10. 치수 정보 출력
# ============================================================
print("\n===== 생성된 원뿔 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        bb = obj.Shape.BoundBox
        print(f"  {obj.Name}: V={vol:.1f}mm³, "
              f"크기=({bb.XLength:.0f}x{bb.YLength:.0f}x{bb.ZLength:.0f})mm")

# ============================================================
# 11. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)

print(f"[INFO] STL 파일 내보내기 완료 ({len(doc.Objects)}개 파일)")

# ============================================================
# 12. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  원뿔 예제 생성 완료!")
print("  기본 원뿔, 원대, 꽃잎, 깔때기, 축+팁 조합")
print("=" * 50)
print("\n다음 단계: 05_compound.py — 복합도형 만들기\n")

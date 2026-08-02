# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 1 - Lesson 05: 복합도형 (Compound Shapes)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "05_compound" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/05_compound.py").read())

[학습 목표]
- 기본 도형의 결합 (Fuse / 합치기)
- 기본 도형의 차감 (Cut / 빼기)
- 교차 (Common / 교집합)
- Bool 연산을 통한 복합도형 설계
- 실용적인 예: 기계 부품 형태
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

doc = FreeCAD.newDocument("CompoundShapes")
print("[INFO] 새 문서 생성됨: CompoundShapes")

# ============================================================
# 3. Boolean 연산 개요
# ============================================================
# FreeCAD 에서 두 쉐이프를 결합하는 3가지 기본 방법:
#
# 3-1. fuse()    — 합치기 (OR) : 두 도형을 합칩니다.
# 3-2. cut()     — 빼기 (NOT) : 첫 번째 도형에서 두 번째를 뺍니다.
# 3-3. common()  — 교집합 (AND) : 겹치는 부분만 남깁니다.
#
# 모든 연산은 Part.Shape 객체에서 직접 호출합니다.

# ============================================================
# 4. Fuse (합치기) 예제
# ============================================================
# 가로로 눕힌 원기둥 + 세로로 선 원기둥 = T자 형태

horizontal_cyl = Part.makeCylinder(8, 40)             # 가로 원기둥
horizontal_cyl.rotate(
    FreeCAD.Vector(0, 0, 0),
    FreeCAD.Vector(0, 1, 0),  # Y축 주위 회전
    90                          # 90도 회전 → X축 방향
)

vertical_cyl = Part.makeCylinder(8, 30)                # 세로 원기둥
vertical_cyl.translate(FreeCAD.Vector(0, 0, 0))        # 원점에서 시작

# T자 형태로 배치: 가로 원기둥의 끝에 세로 원기둥 연결
# 가로 원기둥이 X축을 따라 뻗어 있으므로, 가운데에 세로 원기둥을 배치
horizontal_cyl.translate(FreeCAD.Vector(-20, 0, 0))    # 왼쪽으로 이동

# 합치기 (Fuse)
t_shape = horizontal_cyl.fuse(vertical_cyl)

obj_fuse = doc.addObject("Part::Feature", "Fuse_TShape")
obj_fuse.Shape = t_shape
obj_fuse.ViewObject.ShapeColor = (0.2, 0.6, 0.9)

print("[INFO] Fuse (합치기): T자 형태 생성 완료")

# ============================================================
# 5. Cut (빼기) 예제 — 구멍 뚫기
# ============================================================
# 큰 큐브에서 작은 원기둥으로 구멍을 뚫습니다.

# 바닥판 (큐브)
plate = Part.makeBox(50, 50, 10)

# 구멍용 원기둥 (바닥판보다 높게)
hole_cyl = Part.makeCylinder(8, 15)
hole_cyl.translate(FreeCAD.Vector(25, 25, -2))  # 가운데에 배치, 약간 아래로

# 빼기 (Cut) — 큐브에서 원기둥을 뺍니다
plate_with_hole = plate.cut(hole_cyl)

# 위치 이동
plate_with_hole.translate(FreeCAD.Vector(80, 0, 0))

obj_cut = doc.addObject("Part::Feature", "Cut_PlatesWithHole")
obj_cut.Shape = plate_with_hole
obj_cut.ViewObject.ShapeColor = (0.9, 0.6, 0.2)
obj_cut.ViewObject.Transparency = 30

print("[INFO] Cut (빼기): 구멍 뚫린 판 생성 완료")

# ============================================================
# 6. Common (교집합) 예제
# ============================================================
# 두 도형이 겹치는 부분만 남깁니다.

sphere = Part.makeSphere(15)
box = Part.makeBox(20, 20, 20)
box.translate(FreeCAD.Vector(-10, -10, -10))  # 구 중심에 맞춤

# 교집합
intersection = sphere.common(box)

# 위치 이동
intersection.translate(FreeCAD.Vector(180, 0, 0))

obj_common = doc.addObject("Part::Feature", "Common_Intersection")
obj_common.Shape = intersection
obj_common.ViewObject.ShapeColor = (0.8, 0.2, 0.8)
obj_common.ViewObject.Transparency = 40

print("[INFO] Common (교집합): 구와 큐브의 교차 부분")

# ============================================================
# 7. 실용 예제 1: 너트 모양 (육각형 + 구멍)
# ============================================================
# 육각 기둥을 만들고 가운데에 원형 구멍을 뚫습니다.

def make_hexagon_prism(side_length, height):
    """
    육각형 프리즘(기둥)을 만듭니다.

    매개변수:
        side_length (float): 한 변의 길이 (mm)
        height      (float): 높이 (mm)

    반환값:
        shape : FreeCAD Shape
    """
    # 육각형 꼭짓점 계산
    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)  # 첫 번째 꼭짓점이 위쪽
        x = side_length * math.cos(angle)
        y = side_length * math.sin(angle)
        points.append(FreeCAD.Vector(x, y, 0))

    # 꼭짓점 연결하여 와이어(wire) 생성
    wires = []
    for i in range(6):
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        edge = Part.makeLine(p1, p2)
        wires.append(edge)

    # 와이어로 평면 쉐이프 생성
    wire = Part.Wire(wires)
    face = Part.Face(wire)

    # 프리즘(Extrude)으로 높이 추가
    prism = face.extrude(FreeCAD.Vector(0, 0, height))

    return prism

# 육각 너트 생성
hex_nut = make_hexagon_prism(12, 8)  # 변길이 12mm, 높이 8mm

# 가운데 구멍
nut_hole = Part.makeCylinder(5, 12)  # 반지름 5mm, 충분히 높게
nut_hole.translate(FreeCAD.Vector(0, 0, -2))

# 구멍 뚫기
hex_nut_holed = hex_nut.cut(nut_hole)

obj_nut = doc.addObject("Part::Feature", "HexNut")
obj_nut.Shape = hex_nut_holed
obj_nut.ViewObject.ShapeColor = (0.7, 0.7, 0.7)  # 은색

print("[INFO] 육각 너트: 변길이=12mm, 높이=8mm, 구멍=5mm")

# ============================================================
# 8. 실용 예제 2: 기계 브라켓 (L자형)
# ============================================================
# 두 개의 판을 결합하여 L자 브라켓을 만듭니다.

# 수직 판
vertical_plate = Part.makeBox(5, 40, 30)

# 수평 판
horizontal_plate = Part.makeBox(40, 40, 5)

# 위치 조정: 수직 판의 오른쪽 끝에 수평 판 연결
# 수평 판을 수직 판 옆에 배치
horizontal_plate.translate(FreeCAD.Vector(0, 0, 0))

# 합치기
l_bracket = vertical_plate.fuse(horizontal_plate)

# 구멍 추가 (수직 판 상단)
hole1 = Part.makeCylinder(3, 10)
hole1.translate(FreeCAD.Vector(2.5, 20, 20))
hole1.rotate(
    FreeCAD.Vector(2.5, 20, 25),
    FreeCAD.Vector(1, 0, 0),
    90
)

# 구멍 추가 (수평 판)
hole2 = Part.makeCylinder(3, 10)
hole2.translate(FreeCAD.Vector(20, 20, -2))

# 구멍 뚫기
l_bracket_final = l_bracket.cut(hole1).cut(hole2)

# 위치 이동
l_bracket_final.translate(FreeCAD.Vector(0, -20, 0))

obj_bracket = doc.addObject("Part::Feature", "L_Bracket")
obj_bracket.Shape = l_bracket_final
obj_bracket.ViewObject.ShapeColor = (0.4, 0.4, 0.4)

print("[INFO] L자 브라켓: 40x40x30mm, 구멍 2개")

# ============================================================
# 9. 실용 예제 3: 심플 캡 (원추 + 원기둥)
# ============================================================

# 원기둥 몸체
body = Part.makeCylinder(10, 25)

# 원뿔 캡
cap = Part.makeCone(10, 0, 12)
cap.translate(FreeCAD.Vector(0, 0, 25))

# 합치기
bullet = body.fuse(cap)

# 위치 이동
bullet.translate(FreeCAD.Vector(-80, 0, 0))

obj_bullet = doc.addObject("Part::Feature", "Bullet_Cap")
obj_bullet.Shape = bullet
obj_bullet.ViewObject.ShapeColor = (0.8, 0.7, 0.2)

print("[INFO] 캡 형태: 원기둥(10x25mm) + 원뿔(10x12mm)")

# ============================================================
# 10. 실용 예제 4: 기어 휠 기본 형태
# ============================================================
# 중심 원기둥 + 바깥 톱니 (작은 큐브들)

gear_radius = 15     # 기어 반지름
gear_height = 8      # 기어 높이
tooth_count = 12     # 톱니 수
tooth_size = 4       # 톱니 크기

# 중심 축
gear_center = Part.makeCylinder(gear_radius, gear_height)

# 톱니 추가
gear = gear_center
for i in range(tooth_count):
    angle = (360 / tooth_count) * i
    tooth = Part.makeBox(tooth_size, 4, gear_height)

    # 톱니 위치 계산 (원형 배치)
    rad = math.radians(angle)
    tx = (gear_radius + tooth_size / 2) * math.cos(rad)
    ty = (gear_radius + tooth_size / 2) * math.sin(rad)

    tooth.translate(FreeCAD.Vector(tx - tooth_size/2, ty - 2, 0))
    tooth.rotate(
        FreeCAD.Vector(tx, ty, 0),
        FreeCAD.Vector(0, 0, 1),
        angle
    )

    gear = gear.fuse(tooth)

# 구멍
gear_hole = Part.makeCylinder(4, gear_height + 2)
gear_hole.translate(FreeCAD.Vector(0, 0, -1))
gear = gear.cut(gear_hole)

# 위치 이동
gear.translate(FreeCAD.Vector(80, 0, 0))

obj_gear = doc.addObject("Part::Feature", "Simple_Gear")
obj_gear.Shape = gear
obj_gear.ViewObject.ShapeColor = (0.6, 0.6, 0.6)

print(f"[INFO] 기어: 반지름={gear_radius}mm, 톱니={tooth_count}개, 높이={gear_height}mm")

# ============================================================
# 11. Bool 연산 결과 비교 출력
# ============================================================
print("\n===== 복합도형 요약 =====")
print(f"  총 {len(doc.Objects)}개 객체 생성")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        area = obj.Shape.Area
        bb = obj.Shape.BoundBox
        print(f"  {obj.Name}: V={vol:.1f}mm³, S={area:.1f}mm²")

# ============================================================
# 12. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)

print(f"\n[INFO] STL 파일 내보내기 완료")

# ============================================================
# 13. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  복합도형 예제 완료!")
print("  Fuse, Cut, Common, 너트, 브라켓, 캡, 기어")
print("=" * 50)
print("\nPart 1 완료! 다음: Part 2 — 파라메트릭 설계 자동화")
print("다음 단계: 06_parametric_bracket.py\n")

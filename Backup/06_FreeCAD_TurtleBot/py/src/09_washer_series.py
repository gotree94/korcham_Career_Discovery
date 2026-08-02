# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 2 - Lesson 09: 와셔 시리즈 (Washer Series)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "09_washer_series" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/09_washer_series.py").read())

[학습 목표]
- ISO 규격 와셔 치수 정의
- 평와셔, 스프링 와셔, 플랜지 와셔 생성
- 규격별 와셔 일괄 생성 및 비교
- 3D 프린팅 가능한 와셔 모델
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

doc = FreeCAD.newDocument("WasherSeries")
print("[INFO] 새 문서 생성됨: WasherSeries")

# ============================================================
# 3. ISO 규격 와셔 치수 데이터
# ============================================================
# ISO 7089/7090 (평와셔) 기준
# 치수 단위: mm

WASHER_SPECS = {
    "M3": {
        "inner_diameter": 3.2,    # 안쪽 직경 (구멍)
        "outer_diameter": 7.0,    # 바깥 직경
        "thickness": 0.5,         # 두께
    },
    "M4": {
        "inner_diameter": 4.3,
        "outer_diameter": 9.0,
        "thickness": 0.8,
    },
    "M5": {
        "inner_diameter": 5.3,
        "outer_diameter": 10.0,
        "thickness": 1.0,
    },
    "M6": {
        "inner_diameter": 6.4,
        "outer_diameter": 12.0,
        "thickness": 1.6,
    },
    "M8": {
        "inner_diameter": 8.4,
        "outer_diameter": 16.0,
        "thickness": 1.6,
    },
    "M10": {
        "inner_diameter": 10.5,
        "outer_diameter": 20.0,
        "thickness": 2.0,
    },
    "M12": {
        "inner_diameter": 13.0,
        "outer_diameter": 24.0,
        "thickness": 2.5,
    },
    "M16": {
        "inner_diameter": 17.0,
        "outer_diameter": 30.0,
        "thickness": 3.0,
    },
    "M20": {
        "inner_diameter": 21.0,
        "outer_diameter": 37.0,
        "thickness": 3.0,
    },
}

# ============================================================
# 4. 평와셔 (Flat Washer) 생성 함수
# ============================================================
def create_flat_washer(name, spec, color=(0.75, 0.75, 0.75), z_offset=0):
    """
    평와셔를 생성합니다.

    구조: 원형 판에 가운데 구멍
    ┌─────────────┐
    │   ┌─────┐   │
    │   │     │   │  ← 구멍
    │   │     │   │
    │   └─────┘   │
    └─────────────┘

    매개변수:
        name  (str)  : 객체 이름
        spec  (dict) : 와셔 규격
        color (tuple): RGB 색상
        z_offset(float): Z축 위치 오프셋

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    outer_r = spec["outer_diameter"] / 2
    inner_r = spec["inner_diameter"] / 2
    thickness = spec["thickness"]

    # 바깥 원형 판
    disk = Part.makeCylinder(outer_r, thickness)

    # 안쪽 구멍
    hole = Part.makeCylinder(inner_r, thickness + 2)
    hole.translate(FreeCAD.Vector(0, 0, -1))

    # 빼기
    washer = disk.cut(hole)

    # 위치 이동
    if z_offset != 0:
        washer.translate(FreeCAD.Vector(0, 0, z_offset))

    # 문서에 추가
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = washer
    obj.ViewObject.ShapeColor = color

    # 커스텀 속성
    obj.addProperty("App::PropertyString", "WasherSpec", "Info", "와셔 규격")
    obj.WasherSpec = name.split("_")[0]

    obj.addProperty("App::PropertyFloat", "InnerDia", "Dimensions", "안쪽 직경")
    obj.InnerDia = spec["inner_diameter"]

    obj.addProperty("App::PropertyFloat", "OuterDia", "Dimensions", "바깥 직경")
    obj.OuterDia = spec["outer_diameter"]

    obj.addProperty("App::PropertyFloat", "Thickness", "Dimensions", "두께")
    obj.Thickness = thickness

    return obj

# ============================================================
# 5. 스프링 와셔 (Spring Washer) 생성 함수
# ============================================================
def create_spring_washer(name, spec, color=(0.6, 0.6, 0.65), z_offset=0):
    """
    스프링 와셔 ( Belleville washer )를 생성합니다.
    돔형 와셔로, 나사 풀림을 방지합니다.

    구조: 돔(볼록) 형태의 와셔
    매개변수:
        name  (str)  : 객체 이름
        spec  (dict) : 와셔 규격
        color (tuple): RGB 색상
        z_offset(float): Z축 위치 오프셋

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    outer_r = spec["outer_diameter"] / 2
    inner_r = spec["inner_diameter"] / 2
    thickness = spec["thickness"]

    # 스프링 와셔는 돔형 — 바깥쪽이 약간 높음
    # Part.makeCylinder으로 기본 원형 + 위쪽을 돔형으로 변환
    # 간이 방법: 원형 판을 만들고 상단을 약간 높인 돔형으로 표현

    # 방법: 회전체(Revolve)로 돔형 생성
    # 단면도를 그린 후 Z축 주위를 360도 회전

    # 돔 높이 (스프링 효과용)
    dome_height = thickness * 0.8

    # 회전체 단면 포인트 (xy 평면, y는 반지름 방향)
    # 안쪽 → 바깥쪽 → 돔형 상단
    profile_points = [
        FreeCAD.Vector(inner_r, 0, 0),                   # 안쪽 아래
        FreeCAD.Vector(inner_r, 0, thickness),            # 안쪽 위
        FreeCAD.Vector(outer_r * 0.7, 0, thickness),     # 중간 위
        FreeCAD.Vector(outer_r, 0, thickness + dome_height),  # 바깥쪽 위 (돔)
        FreeCAD.Vector(outer_r, 0, 0),                    # 바깥쪽 아래
        FreeCAD.Vector(inner_r, 0, 0),                    # 닫힘
    ]

    # 와이어 생성
    edges = []
    for i in range(len(profile_points) - 1):
        edge = Part.makeLine(profile_points[i], profile_points[i + 1])
        edges.append(edge)

    wire = Part.Wire(edges)

    # Z축 주위 회전체 생성
    washer = wire.revolve(
        FreeCAD.Vector(0, 0, 0),    # 회전 중심점
        FreeCAD.Vector(0, 0, 1),    # 회전 축
        360                           # 회전 각도
    )

    # 위치 이동
    if z_offset != 0:
        washer.translate(FreeCAD.Vector(0, 0, z_offset))

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = washer
    obj.ViewObject.ShapeColor = color

    obj.addProperty("App::PropertyString", "WasherSpec", "Info", "와셔 규격")
    obj.WasherSpec = name.split("_")[0]

    return obj

# ============================================================
# 6. 플랜지 와셔 (Fender Washer) 생성 함수
# ============================================================
def create_fender_washer(name, spec, color=(0.7, 0.7, 0.7), z_offset=0):
    """
    플랜지 와셔 (넓은 와셔) 를 생성합니다.
    평와셔보다 바깥 직경이 크고, 하단에 돔형 베이스가 있습니다.

    매개변수:
        name  (str)  : 객체 이름
        spec  (dict) : 와셔 규격 (outer_diameter가 1.5배)
        color (tuple): RGB 색상
        z_offset(float): Z축 위치 오프셋

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    # 플랜지 와셔는 일반 와셔보다 바깥 직경이 1.5배
    outer_r = spec["outer_diameter"] * 0.75
    inner_r = spec["inner_diameter"] / 2
    thickness = spec["thickness"] * 1.5

    disk = Part.makeCylinder(outer_r, thickness)
    hole = Part.makeCylinder(inner_r, thickness + 2)
    hole.translate(FreeCAD.Vector(0, 0, -1))
    washer = disk.cut(hole)

    # 하단 모서리 둥글게 (Chamfer)
    try:
        bottom_edges = [e for e in washer.Edges
                       if any(abs(v.Point.z) < 0.01 for v in e.Vertexes)]
        if bottom_edges:
            washer = washer.makeChamfer(0.5, bottom_edges)
    except:
        pass

    if z_offset != 0:
        washer.translate(FreeCAD.Vector(0, 0, z_offset))

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = washer
    obj.ViewObject.ShapeColor = color

    obj.addProperty("App::PropertyString", "WasherSpec", "Info", "와셔 규격")
    obj.WasherSpec = name.split("_")[0]

    return obj

# ============================================================
# 7. 규격별 평와셔 일괄 생성
# ============================================================
print("\n===== 규격별 평와셔 일괄 생성 =====")

x_offset = 0
spacing = 50

for spec_name, spec_data in WASHER_SPECS.items():
    obj = create_flat_washer(
        name=f"{spec_name}_FlatWasher",
        spec=spec_data,
        color=(0.75, 0.75, 0.75)
    )
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()

    x_offset += spacing

    print(f"  {spec_name}: 안={spec_data['inner_diameter']}mm, "
          f"바깥={spec_data['outer_diameter']}mm, "
          f"두께={spec_data['thickness']}mm")

print(f"==============================\n")

# ============================================================
# 8. 스프링 와셔 일괄 생성
# ============================================================
print("===== 스프링 와셔 생성 =====")

spring_specs = {
    "M6": WASHER_SPECS["M6"],
    "M8": WASHER_SPECS["M8"],
    "M10": WASHER_SPECS["M10"],
    "M12": WASHER_SPECS["M12"],
}

for spec_name, spec_data in spring_specs.items():
    obj = create_spring_washer(
        name=f"{spec_name}_SpringWasher",
        spec=spec_data,
        color=(0.6, 0.6, 0.7)
    )
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()
    x_offset += spacing

    print(f"  {spec_name} 스프링 와셔 생성")

print(f"==============================\n")

# ============================================================
# 9. 플랜지 와셔 생성
# ============================================================
print("===== 플랜지 와셔 생성 =====")

fender_specs = {
    "M5": WASHER_SPECS["M5"],
    "M8": WASHER_SPECS["M8"],
    "M12": WASHER_SPECS["M12"],
}

for spec_name, spec_data in fender_specs.items():
    obj = create_fender_washer(
        name=f"{spec_name}_FenderWasher",
        spec=spec_data,
        color=(0.65, 0.65, 0.6)
    )
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()
    x_offset += spacing

    print(f"  {spec_name} 플랜지 와셔 생성")

print(f"==============================\n")

# ============================================================
# 10. 스택 와셔 (여러 개 겹침) 시각화
# ============================================================
print("===== 스택 와셔 (M8 x 5개) =====")

m8_spec = WASHER_SPECS["M8"]
stack_z = 0

for i in range(5):
    obj = create_flat_washer(
        name=f"M8_Stack_{i+1}",
        spec=m8_spec,
        color=(0.7, 0.7 + i * 0.05, 0.7),
        z_offset=stack_z
    )
    stack_z += m8_spec["thickness"]

print(f"  M8 와셔 5개 스택: 총 높이={stack_z:.1f}mm")
print(f"==============================\n")

# ============================================================
# 11. 전체 와셔 목록 출력
# ============================================================
print("===== 전체 와셔 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        spec = getattr(obj, 'WasherSpec', 'N/A')
        print(f"  {obj.Name}: 규격={spec}, V={vol:.2f}mm³")

# ============================================================
# 12. STL 내보내기
# ============================================================
export_dir = os.path.join(os.path.expanduser("~"), "Downloads", "py", "output")
os.makedirs(export_dir, exist_ok=True)

for obj in doc.Objects:
    if hasattr(obj.Shape, 'exportStl'):
        filepath = os.path.join(export_dir, f"{obj.Name}.stl")
        obj.Shape.exportStl(filepath)

print(f"\n[INFO] STL 내보내기 완료 ({len(doc.Objects)}개 파일)")

# ============================================================
# 13. 뷰 조정 및 완료
# ============================================================
doc.recompute()

try:
    FreeCADGui.ActiveDocument.ActiveView.fitAll()
except:
    pass

print("\n" + "=" * 50)
print("  와셔 시리즈 완료!")
print(f"  평와셔 {len(WASHER_SPECS)}개 + 스프링 4개 + 플랜지 3개 + 스택 5개")
print("=" * 50)
print("\n다음 단계: 10_csv_driven.py — CSV 기반 설계\n")

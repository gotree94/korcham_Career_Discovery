# -*- coding: utf-8 -*-
"""
=============================================================
FreeCAD Python + AI 3D 설계 자동화 커리큘럼
Part 2 - Lesson 07: 볼트 생성기 (Bolt Generator)
=============================================================

[실행 방법]
1. FreeCAD를 엽니다.
2. Macro → Macros... → Create → "07_bolt_generator" 이름 지정
3. 이 코드를 붙여넣고 ▶ Run (또는 F5) 클릭
4. 또는 Python 콘솔에서:
   exec(open("C:/Users/Administrator/Downloads/py/src/07_bolt_generator.py").read())

[학습 목표]
- ISO 규격 볼트 치수 데이터를 Python 딕셔너리로 정의
- 규격별 볼트를 자동 생성하는 생성기 패턴
- 나사산 표현 (간이 형태)
- 볼트 헤드 (육각 소켓, 육각 외부)
- M3~M20 규격 일괄 생성
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

doc = FreeCAD.newDocument("BoltGenerator")
print("[INFO] 새 문서 생성됨: BoltGenerator")

# ============================================================
# 3. ISO 규격 볼트 치수 데이터
# ============================================================
# ISO 4014/4017 (육각머리 볼트) 기준
# 치수 단위: mm
#
# 딕셔너리 구조:
#   "규격명": {
#       "pitch": 나사 피치,
#       "head_width": 육각 머리 너비 (평면 간),
#       "head_height": 머리 높이,
#       "shaft_diameter": 축 직경,
#       "socket_width": 소켓 너비 (內육각)
#   }

BOLT_SPECS = {
    "M3": {
        "pitch": 0.5,
        "head_width": 5.5,
        "head_height": 2.0,
        "shaft_diameter": 3.0,
        "socket_width": 2.5,
    },
    "M4": {
        "pitch": 0.7,
        "head_width": 7.0,
        "head_height": 2.8,
        "shaft_diameter": 4.0,
        "socket_width": 3.0,
    },
    "M5": {
        "pitch": 0.8,
        "head_width": 8.0,
        "head_height": 3.5,
        "shaft_diameter": 5.0,
        "socket_width": 4.0,
    },
    "M6": {
        "pitch": 1.0,
        "head_width": 10.0,
        "head_height": 4.0,
        "shaft_diameter": 6.0,
        "socket_width": 5.0,
    },
    "M8": {
        "pitch": 1.25,
        "head_width": 13.0,
        "head_height": 5.3,
        "shaft_diameter": 8.0,
        "socket_width": 6.0,
    },
    "M10": {
        "pitch": 1.5,
        "head_width": 16.0,
        "head_height": 6.4,
        "shaft_diameter": 10.0,
        "socket_width": 8.0,
    },
    "M12": {
        "pitch": 1.75,
        "head_width": 18.0,
        "head_height": 7.5,
        "shaft_diameter": 12.0,
        "socket_width": 10.0,
    },
    "M16": {
        "pitch": 2.0,
        "head_width": 24.0,
        "head_height": 10.0,
        "shaft_diameter": 16.0,
        "socket_width": 12.0,
    },
    "M20": {
        "pitch": 2.5,
        "head_width": 30.0,
        "head_height": 12.5,
        "shaft_diameter": 20.0,
        "socket_width": 15.0,
    },
}

# ============================================================
# 4. 육각형 프리즘 생성 헬퍼 함수
# ============================================================
def make_hexagon_prism(width, height):
    """
    육각형 프리즘을 만듭니다.
    width: 육각형 평면 간 너비
    height: 높이
    """
    # 육각형의 꼭짓점 (평면 간 너비 기준)
    # 한 변의 길이 = width / sqrt(3) * 2 ≈ width / 1.1547
    side = width / math.sqrt(3)

    points = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        x = side * math.cos(angle)
        y = side * math.sin(angle)
        points.append(FreeCAD.Vector(x, y, 0))

    # 엣지 생성
    edges = []
    for i in range(6):
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        edges.append(Part.makeLine(p1, p2))

    wire = Part.Wire(edges)
    face = Part.Face(wire)
    prism = face.extrude(FreeCAD.Vector(0, 0, height))

    return prism

# ============================================================
# 5. 육각 소켓(内六각) 생성 함수
# ============================================================
def make_hex_socket(width, depth):
    """
    육각 소켓 (내부 육각형 구멍) 을 만듭니다.
    Allen 키(육각 렌치)용 소켓입니다.
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
        p1 = points[i]
        p2 = points[(i + 1) % 6]
        edges.append(Part.makeLine(p1, p2))

    wire = Part.Wire(edges)
    face = Part.Face(wire)
    socket = face.extrude(FreeCAD.Vector(0, 0, -depth))

    return socket

# ============================================================
# 6. 볼트 생성 함수
# ============================================================
def create_bolt(name, spec, shaft_length, color=(0.7, 0.7, 0.7)):
    """
    규격에 맞는 볼트를 생성합니다.

    매개변수:
        name         (str)  : 객체 이름
        spec         (dict) : 볼트 규격 딕셔너리
        shaft_length (float): 축 길이 (mm)
        color        (tuple): RGB 색상

    반환값:
        obj : FreeCAD Part::Feature 객체
    """
    d = spec["shaft_diameter"]
    head_h = spec["head_height"]
    head_w = spec["head_width"]
    socket_w = spec["socket_width"]

    # ---- 1. 육각 머리 생성 ----
    head = make_hexagon_prism(head_w, head_h)

    # ---- 2. 축(나사 포함) 생성 ----
    shaft = Part.makeCylinder(d / 2, shaft_length)
    shaft.translate(FreeCAD.Vector(0, 0, head_h))

    # ---- 3. 머리 + 축 합치기 ----
    bolt = head.fuse(shaft)

    # ---- 4. 육각 소켓 뚫기 ----
    socket_depth = head_h * 0.6  # 머리 높이의 60%
    socket = make_hex_socket(socket_w, socket_depth)
    socket.translate(FreeCAD.Vector(0, 0, head_h))  # 머리 윗면에 배치
    bolt = bolt.cut(socket)

    # ---- 5. 모서리 둥글게 (간이) ----
    # 머리와 축이 만나는 부분에 작은 필렛 추가
    try:
        # 필렛은 에지에 적용 — 머리 바닥 에지 선택이 어려우므로 간소화
        pass
    except:
        pass

    # ---- 6. 문서에 추가 ----
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = bolt
    obj.ViewObject.ShapeColor = color

    # 커스텀 속성
    obj.addProperty("App::PropertyString", "BoltSpec", "Info", "볼트 규격")
    obj.BoltSpec = name.split("_")[0]

    obj.addProperty("App::PropertyFloat", "ShaftLength", "Dimensions", "축 길이")
    obj.ShaftLength = shaft_length

    return obj

# ============================================================
# 7. 나사산 표현 (간이 스파이럴)
# ============================================================
# 실제 나사산은 복잡하지만, 시각적 표현을 위해
# 나선형 홈을 만듭니다.

def create_bolt_with_thread(name, spec, shaft_length, color=(0.7, 0.7, 0.7)):
    """
    나사산이 포함된 볼트를 생성합니다.
    간이 나사산: 축에 나선형 홈을 표현합니다.
    """
    d = spec["shaft_diameter"]
    pitch = spec["pitch"]
    head_h = spec["head_height"]
    head_w = spec["head_width"]
    socket_w = spec["socket_width"]

    # 육각 머리
    head = make_hexagon_prism(head_w, head_h)

    # 축
    shaft = Part.makeCylinder(d / 2, shaft_length)
    shaft.translate(FreeCAD.Vector(0, 0, head_h))

    bolt = head.fuse(shaft)

    # 소켓
    socket_depth = head_h * 0.6
    socket = make_hex_socket(socket_w, socket_depth)
    socket.translate(FreeCAD.Vector(0, 0, head_h))
    bolt = bolt.cut(socket)

    # 나사산 표현: 축에 작은 원기둥들을 나선형으로 배치
    thread_outer_r = d / 2 + 0.3  # 나사산 바깥 반지름
    thread_inner_r = d / 2 - 0.3  # 나사산 안쪽 반지름
    thread_height = 0.3            # 나사산 높이

    # 나사산 구간 (머리 바로 아래 ~ 축 끝)
    thread_start = head_h + 1
    thread_end = head_h + shaft_length - 1

    if thread_end > thread_start and pitch > 0:
        num_threads = int((thread_end - thread_start) / pitch)

        for i in range(min(num_threads, 50)):  # 최대 50회전으로 제한
            z = thread_start + i * pitch

            # 나사산을 작은 원기둥으로 표현
            thread_ring = Part.makeCylinder(
                thread_outer_r,
                pitch * 0.4,
                FreeCAD.Vector(0, 0, z),
                FreeCAD.Vector(0, 0, 1),
                math.radians(360)
            )

            # 기존 볼트에서 나사산 영역을 빼고 다시 더하기
            # (시각적 표현을 위한 간이 방법)
            bolt = bolt.fuse(thread_ring)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = bolt
    obj.ViewObject.ShapeColor = color

    obj.addProperty("App::PropertyString", "BoltSpec", "Info", "볼트 규격")
    obj.BoltSpec = name.split("_")[0]

    return obj

# ============================================================
# 8. M3~M20 규격 볼트 일괄 생성
# ============================================================
print("\n===== 규격별 볼트 일괄 생성 =====")

x_offset = 0

for spec_name, spec_data in BOLT_SPECS.items():
    # 축 길이: 규격에 비례하여 설정
    # M3은 12mm, M20은 50mm 정도
    shaft_length = spec_data["shaft_diameter"] * 2.5

    obj = create_bolt(
        name=f"{spec_name}_Bolt",
        spec=spec_data,
        shaft_length=shaft_length,
        color=(0.7, 0.7, 0.7)
    )

    # 위치 이동
    obj.Shape.translate(FreeCAD.Vector(x_offset, 0, 0))
    doc.recompute()

    # 다음 볼트 위치
    x_offset += spec_data["head_width"] + 15

    print(f"  {spec_name}: 축경={spec_data['shaft_diameter']}mm, "
          f"축길이={shaft_length:.0f}mm, "
          f"피치={spec_data['pitch']}mm, "
          f"머리={spec_data['head_width']}mm")

print(f"==============================\n")

# ============================================================
# 9. 나사산 포함 볼트 생성 (M8 예시)
# ============================================================
m8_spec = BOLT_SPECS["M8"]
threaded_bolt = create_bolt_with_thread(
    name="M8_Threaded_Bolt",
    spec=m8_spec,
    shaft_length=30,
    color=(0.6, 0.6, 0.65)
)

threaded_bolt.Shape.translate(FreeCAD.Vector(x_offset + 20, 0, 0))
doc.recompute()

print(f"[INFO] M8 나사산 볼트 생성: 축길이=30mm")

# ============================================================
# 10. 볼트 정보 출력
# ============================================================
print("\n===== 생성된 볼트 목록 =====")
for obj in doc.Objects:
    if hasattr(obj.Shape, 'Volume'):
        vol = obj.Shape.Volume
        bb = obj.Shape.BoundBox
        spec = getattr(obj, 'BoltSpec', 'N/A')
        print(f"  {obj.Name}: 규격={spec}, V={vol:.1f}mm³, "
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
print("  볼트 생성기 완료!")
print(f"  M3~M20까지 {len(BOLT_SPECS)}개 규격 볼트 생성")
print("=" * 50)
print("\n다음 단계: 08_nut_generator.py — 너트 생성기\n")

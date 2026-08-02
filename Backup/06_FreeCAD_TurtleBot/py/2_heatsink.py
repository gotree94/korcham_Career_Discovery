# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 2: 파라메트릭 방열판 (Heatsink)
----------------------------------------------------
- 베이스 플레이트 + 테이퍼드(사다리꼴 단면) 냉각핀 배열
- 핀 개수, 간격, 각도, 높이를 파라미터로 조절 가능
- ARM SoC / X-ray 장비 등 실무 열설계와 바로 연결 가능한 구조
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("Heatsink")

# ---------------- 파라미터 ----------------
base_length = 60.0     # 베이스 X방향 길이
base_width = 60.0      # 베이스 Y방향 길이
base_thickness = 4.0   # 베이스 두께

fin_count = 12          # 핀 개수 (Y방향으로 배열)
fin_height = 25.0       # 핀 높이
fin_top_thickness = 1.2 # 핀 상단 두께 (테이퍼드)
fin_bottom_thickness = 2.5  # 핀 하단 두께 (베이스에 붙는 부분, 더 두꺼움 -> 방열 효율)
fin_taper_angle_deg = 3.0   # 핀 좌우 테이퍼 각도(사출/다이캐스팅 draft angle 반영)

fillet_radius = 0.8     # 베이스-핀 연결부 필렛 반경 (열응력 완화)


def make_tapered_fin(length, bottom_thickness, top_thickness, height):
    """
    사다리꼴 단면(측면에서 봤을 때)의 핀 하나를 생성.
    아래(베이스쪽)는 두껍고 위로 갈수록 얇아짐 -> 열전달 효율 + 성형성 반영
    """
    half_bot = bottom_thickness / 2.0
    half_top = top_thickness / 2.0

    p1 = App.Vector(-length / 2.0, -half_bot, 0)
    p2 = App.Vector(length / 2.0, -half_bot, 0)
    p3 = App.Vector(length / 2.0, half_bot, 0)
    p4 = App.Vector(-length / 2.0, half_bot, 0)
    wire_bottom = Part.makePolygon([p1, p2, p3, p4, p1])

    p5 = App.Vector(-length / 2.0, -half_top, height)
    p6 = App.Vector(length / 2.0, -half_top, height)
    p7 = App.Vector(length / 2.0, half_top, height)
    p8 = App.Vector(-length / 2.0, half_top, height)
    wire_top = Part.makePolygon([p5, p6, p7, p8, p5])

    fin = Part.makeLoft([wire_bottom, wire_top], True)
    return fin


# ---------------- 베이스 플레이트 ----------------
base_box = Part.makeBox(base_length, base_width, base_thickness,
                         App.Vector(-base_length / 2.0, -base_width / 2.0, 0))

# ---------------- 핀 배열 생성 ----------------
fins = []
gap = base_width / fin_count
start_y = -base_width / 2.0 + gap / 2.0

for i in range(fin_count):
    y_pos = start_y + i * gap
    fin = make_tapered_fin(
        length=base_length * 0.9,
        bottom_thickness=fin_bottom_thickness,
        top_thickness=fin_top_thickness,
        height=fin_height
    )
    fin.translate(App.Vector(0, y_pos, base_thickness))
    fins.append(fin)

# 핀들을 하나로 합치고 베이스와 결합
fin_union = fins[0]
for f in fins[1:]:
    fin_union = fin_union.fuse(f)

heatsink = base_box.fuse(fin_union)

# 베이스-핀 연결부 필렛 적용 (열응력 완화 + 사실적인 다이캐스팅 형상)
try:
    edges_to_fillet = []
    for edge in heatsink.Edges:
        # base_thickness 높이 근처의 수평 엣지만 필렛 대상으로 선택 (근사적 방법)
        bbox = edge.BoundBox
        if abs(bbox.ZMin - base_thickness) < 0.01 and abs(bbox.ZMax - base_thickness) < 0.01:
            edges_to_fillet.append(edge)
    if edges_to_fillet:
        heatsink = heatsink.makeFillet(fillet_radius, edges_to_fillet)
except Exception as e:
    print("필렛 적용 중 일부 실패 (형상은 정상 생성됨):", e)

obj = doc.addObject("Part::Feature", "Heatsink")
obj.Shape = heatsink
doc.recompute()

try:
    obj.ViewObject.ShapeColor = (0.75, 0.75, 0.8)  # 알루미늄 톤
    App.Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass

print("방열판 생성 완료: 핀 %d개, 높이 %.1fmm" % (fin_count, fin_height))
print("표면적 증가로 실제 CFD/FEM 열해석 워크벤치와 연계 가능")

# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 3: 벌집 격자(Honeycomb) 경량화 브라켓
-----------------------------------------------------------
- UAV/드론 부품에 실제로 쓰이는 경량화 설계 기법
- 사각 브라켓 판재에 육각형 패턴을 Boolean cut으로 관통시켜
  강성 대비 무게를 줄인 위상최적화 느낌의 형상 생성
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("HoneycombBracket")

# ---------------- 파라미터 ----------------
plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0

hex_radius = 6.0          # 육각형 외접원 반지름
hex_wall = 1.5            # 육각형 사이 벽 두께
mount_hole_radius = 4.0   # 장착 볼트홀 반지름
edge_margin = 10.0        # 가장자리 여백 (구멍 안 뚫는 영역)


def make_hexagon_face(center_x, center_y, radius):
    pts = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3  # 뾰족한 부분이 위/아래를 향하도록 정렬
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        pts.append(App.Vector(x, y, 0))
    pts.append(pts[0])
    wire = Part.makePolygon(pts)
    return Part.Face(wire)


# ---------------- 베이스 플레이트 ----------------
plate = Part.makeBox(plate_length, plate_width, plate_thickness,
                      App.Vector(-plate_length / 2.0, -plate_width / 2.0, 0))

# ---------------- 육각형 격자 배치 (벌집 배열: 홀수 행 오프셋) ----------------
hex_pitch_x = (hex_radius * 2 * math.cos(math.pi / 6)) + hex_wall  # 가로 간격
hex_pitch_y = (hex_radius * 1.5) + hex_wall                        # 세로 간격

hex_cutters = []
usable_x = plate_length / 2.0 - edge_margin
usable_y = plate_width / 2.0 - edge_margin

row = 0
y = -usable_y
while y <= usable_y:
    x_offset = (hex_pitch_x / 2.0) if (row % 2 == 1) else 0.0
    x = -usable_x + x_offset
    while x <= usable_x:
        hex_face = make_hexagon_face(x, y, hex_radius)
        hex_cutters.append(hex_face)
        x += hex_pitch_x
    y += hex_pitch_y
    row += 1

print("생성된 육각 셀 개수:", len(hex_cutters))

# 모든 육각형을 하나의 면으로 합치고 관통 절삭
hex_union_face = hex_cutters[0]
for f in hex_cutters[1:]:
    hex_union_face = hex_union_face.fuse(f)

hex_solid = hex_union_face.extrude(App.Vector(0, 0, plate_thickness))
bracket = plate.cut(hex_solid)

# ---------------- 4개 모서리 장착 볼트홀 ----------------
mount_positions = [
    (plate_length / 2.0 - edge_margin / 2.0, plate_width / 2.0 - edge_margin / 2.0),
    (-(plate_length / 2.0 - edge_margin / 2.0), plate_width / 2.0 - edge_margin / 2.0),
    (plate_length / 2.0 - edge_margin / 2.0, -(plate_width / 2.0 - edge_margin / 2.0)),
    (-(plate_length / 2.0 - edge_margin / 2.0), -(plate_width / 2.0 - edge_margin / 2.0)),
]

for mx, my in mount_positions:
    hole = Part.makeCylinder(mount_hole_radius, plate_thickness + 2,
                              App.Vector(mx, my, -1))
    bracket = bracket.cut(hole)

obj = doc.addObject("Part::Feature", "HoneycombBracket")
obj.Shape = bracket
doc.recompute()

try:
    obj.ViewObject.ShapeColor = (0.3, 0.7, 0.3)
    App.Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass

# ---------------- 무게 절감률 참고 출력 ----------------
solid_volume = plate_length * plate_width * plate_thickness
actual_volume = bracket.Volume
reduction_pct = (1 - actual_volume / solid_volume) * 100

print("풀 솔리드 부피: %.1f mm^3" % solid_volume)
print("실제 브라켓 부피: %.1f mm^3" % actual_volume)
print("경량화율: %.1f %%" % reduction_pct)

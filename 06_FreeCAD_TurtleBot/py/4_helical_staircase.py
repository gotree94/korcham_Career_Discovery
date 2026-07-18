# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 4: 나선형 계단 (Helical Staircase) - 수정판
---------------------------------------------------------------
- 전체 로직을 함수 하나(build_staircase)로 감싸서
  FreeCAD Python 콘솔에 직접 복붙해도 SyntaxError가 나지 않도록 수정
- 실행 방법:
    1) exec(open('4_helical_staircase.py', encoding='utf-8').read())
    2) 또는 매크로로 등록 후 실행
    3) 콘솔에 통째로 붙여넣어도 이제 안전함 (함수 정의 후 마지막 줄에서 호출)
"""

import FreeCAD as App
import Part
import math


def build_staircase():
    doc = App.newDocument("HelicalStaircase")

    # ---------------- 파라미터 ----------------
    num_steps = 16
    total_height = 32.0
    step_rise = total_height / num_steps
    radius_inner = 3.0
    radius_outer = 45.0
    step_thickness = 1.5
    angle_per_step_deg = 27.0

    handrail_radius = 1.0
    handrail_offset = radius_outer - 2.0

    def make_step(angle_deg, z):
        angle = math.radians(angle_deg)
        span = math.radians(angle_per_step_deg * 0.9)

        pts = []
        n_arc = 6
        for i in range(n_arc + 1):
            a = angle + span * i / n_arc
            pts.append(App.Vector(radius_inner * math.cos(a), radius_inner * math.sin(a), 0))
        for i in range(n_arc, -1, -1):
            a = angle + span * i / n_arc
            pts.append(App.Vector(radius_outer * math.cos(a), radius_outer * math.sin(a), 0))
        pts.append(pts[0])

        wire = Part.makePolygon(pts)
        face = Part.Face(wire)
        step_solid = face.extrude(App.Vector(0, 0, step_thickness))
        step_solid.translate(App.Vector(0, 0, z))
        return step_solid

    # ---------------- 중심 기둥 ----------------
    spine = Part.makeCylinder(radius_inner, total_height + 5)

    # ---------------- 계단 발판 ----------------
    steps = []
    for i in range(num_steps):
        angle_deg = i * angle_per_step_deg
        z = i * step_rise + 2.0
        steps.append(make_step(angle_deg, z))

    step_union = steps[0]
    for s in steps[1:]:
        step_union = step_union.fuse(s)

    staircase = spine.fuse(step_union)

    # ---------------- 헬리컬 손잡이 ----------------
    total_turns = (angle_per_step_deg * num_steps) / 360.0
    helix_height = total_height + step_rise
    helix_pitch = helix_height / total_turns

    helix_wire = Part.makeHelix(helix_pitch, helix_height, handrail_offset)
    start_point = helix_wire.Vertexes[0].Point
    circle = Part.makeCircle(handrail_radius, start_point, App.Vector(1, 0, 0))
    circle_wire = Part.Wire(circle)

    handrail = None
    try:
        handrail = Part.Wire(helix_wire.Edges).makePipeShell([circle_wire], True, True)
    except Exception as e:
        print("손잡이(handrail) 생성 실패 - 계단 본체만 생성합니다:", e)
        handrail = None

    if handrail is not None:
        handrail.translate(App.Vector(0, 0, 2.0))
        combined = staircase.fuse(handrail)
    else:
        combined = staircase

    obj = doc.addObject("Part::Feature", "HelicalStaircase")
    obj.Shape = combined
    doc.recompute()

    try:
        obj.ViewObject.ShapeColor = (0.6, 0.4, 0.2)
        App.Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    print("나선형 계단 생성 완료: 계단 수 %d, 총 회전 %.1f 바퀴, 전체높이 %.1fmm"
          % (num_steps, total_turns, total_height))

    return obj


# 함수 정의가 끝난 뒤 바로 실행 -> 콘솔에 전체를 붙여넣어도 마지막 줄까지 문제없이 동작
build_staircase()

# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 1: 인볼류트 기어 트레인 (Involute Gear Train)
----------------------------------------------------------------
- 인볼류트 곡선 수식으로 실제 스퍼기어 치형을 생성
- 서로 다른 잇수를 가진 두 기어를 정확한 중심거리로 맞물리게 배치
- FreeCAD 실행 방법:
    1) FreeCAD 실행 -> Python 콘솔 열기
    2) exec(open('1_involute_gear_train.py', encoding='utf-8').read())
   또는 매크로로 등록 후 실행
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("InvoluteGearTrain")


def involute_point(base_radius, t):
    """인볼류트 곡선 위의 한 점 (t: 전개각 파라미터, radian)"""
    x = base_radius * (math.cos(t) + t * math.sin(t))
    y = base_radius * (math.sin(t) - t * math.cos(t))
    return App.Vector(x, y, 0)


def make_gear(module, teeth, pressure_angle_deg=20.0, thickness=8.0, bore_radius=3.0):
    """
    module: 모듈 (mm)
    teeth: 잇수
    pressure_angle_deg: 압력각 (보통 20도)
    thickness: 기어 두께
    bore_radius: 중심 축 구멍 반지름
    """
    pressure_angle = math.radians(pressure_angle_deg)

    pitch_radius = module * teeth / 2.0
    base_radius = pitch_radius * math.cos(pressure_angle)
    addendum = module          # 이끝높이
    dedendum = 1.25 * module   # 이뿌리높이
    outer_radius = pitch_radius + addendum
    root_radius = pitch_radius - dedendum

    tooth_angle = 2 * math.pi / teeth

    # 인볼류트 곡선 파라미터 t 범위 계산 (base_radius ~ outer_radius)
    t_max = math.sqrt((outer_radius / base_radius) ** 2 - 1) if outer_radius > base_radius else 0.4
    t_max = max(t_max, 0.35)

    n_pts = 12
    profile_points = []
    for i in range(n_pts + 1):
        t = t_max * i / n_pts
        profile_points.append(involute_point(base_radius, t))

    # 이 하나(치형)의 좌/우 곡선을 구성해 폐곡선(폴리곤 근사)으로 만든다
    edges = []
    all_pts = []

    for tooth_i in range(teeth):
        center_angle = tooth_i * tooth_angle

        # 치형 두께 절반 각도 (피치원에서 이 두께의 절반이 만드는 각)
        half_tooth_angle = (math.pi / teeth) * 0.5

        # 왼쪽 인볼류트 곡선 (root -> outer)
        left_pts = []
        for p in profile_points:
            r = math.hypot(p.x, p.y)
            if r < root_radius:
                r = root_radius
                ang = center_angle - half_tooth_angle
            else:
                base_ang = math.atan2(p.y, p.x)
                ang = center_angle - half_tooth_angle + base_ang
            left_pts.append(App.Vector(r * math.cos(ang), r * math.sin(ang), 0))

        # 오른쪽 인볼류트 곡선 (outer -> root), 대칭
        right_pts = []
        for p in reversed(profile_points):
            r = math.hypot(p.x, p.y)
            if r < root_radius:
                r = root_radius
                ang = center_angle + half_tooth_angle
            else:
                base_ang = math.atan2(p.y, p.x)
                ang = center_angle + half_tooth_angle - base_ang
            right_pts.append(App.Vector(r * math.cos(ang), r * math.sin(ang), 0))

        all_pts.extend(left_pts)
        all_pts.extend(right_pts)

        # 다음 이의 뿌리원 사이를 잇는 짧은 호(단순화: 직선)
        next_center_angle = center_angle + tooth_angle
        root_pt_here = App.Vector(root_radius * math.cos(center_angle + half_tooth_angle),
                                   root_radius * math.sin(center_angle + half_tooth_angle), 0)
        root_pt_next = App.Vector(root_radius * math.cos(next_center_angle - half_tooth_angle),
                                   root_radius * math.sin(next_center_angle - half_tooth_angle), 0)
        all_pts.append(root_pt_next)

    all_pts.append(all_pts[0])  # 폐곡선 닫기

    wire = Part.makePolygon(all_pts)
    face = Part.Face(wire)

    # 중심 보어(축 구멍)
    bore_wire = Part.makeCircle(bore_radius)
    bore_face = Part.Face(Part.Wire(bore_wire))
    face = face.cut(bore_face)

    gear_solid = face.extrude(App.Vector(0, 0, thickness))
    return gear_solid, pitch_radius


# --- 기어 2개 생성: 잇수 20 / 잇수 32 (모듈 동일해야 서로 맞물림) ---
module = 2.0
gear1_solid, r1 = make_gear(module=module, teeth=20, thickness=8.0, bore_radius=3.0)
gear2_solid, r2 = make_gear(module=module, teeth=32, thickness=8.0, bore_radius=4.0)

obj1 = doc.addObject("Part::Feature", "Gear_20T")
obj1.Shape = gear1_solid

# 두 번째 기어는 중심거리(r1+r2)만큼 X축으로 이동시켜 맞물리게 배치
obj2 = doc.addObject("Part::Feature", "Gear_32T")
gear2_solid.translate(App.Vector(r1 + r2, 0, 0))
obj2.Shape = gear2_solid

doc.recompute()

# 보기 좋게 색상 지정 (GUI 환경일 때만 동작)
try:
    obj1.ViewObject.ShapeColor = (0.2, 0.5, 0.9)
    obj2.ViewObject.ShapeColor = (0.9, 0.4, 0.2)
    App.Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass

print("Gear 1 pitch radius:", r1, "mm")
print("Gear 2 pitch radius:", r2, "mm")
print("Center distance:", r1 + r2, "mm")

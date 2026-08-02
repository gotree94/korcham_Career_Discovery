# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 7: 헬리컬 기어 페어 + 회전 애니메이션 검증
------------------------------------------------------------------
- 기어 2개를 정확한 중심거리(pitch_radius1 + pitch_radius2)로 배치
- 서로 반대 헬릭스각(하나는 +각, 하나는 -각)을 줘야 평행축에서 맞물림
- QTimer로 실시간 회전시켜, 기어비(잇수비)에 맞게 두 기어가
  서로 반대 방향으로 정확히 맞물려 도는지 "육안 기구학적 검증"
- 주의: 이건 접촉응력/간섭 해석이 아니라 회전 운동학적 시각화입니다.
  실제 치형 간섭 여부까지 확인하려면 FEM/충돌해석 워크벤치가 별도로 필요합니다.

실행 방법 (GUI 필요, 콘솔 붙여넣기 가능):
    exec(open('7_helical_gear_pair_animation.py', encoding='utf-8').read())
    -> 실행 후 stop_animation() 호출하면 애니메이션 정지
"""

import FreeCAD as App
import Part
import math

try:
    from PySide2 import QtCore
except ImportError:
    from PySide import QtCore


# ---------------- 헬리컬 기어 형상 생성 함수 (예제 6과 동일 로직) ----------------
def make_helical_gear_shape(module, teeth, pressure_angle_deg=20.0,
                             thickness=20.0, bore_radius=4.0,
                             helix_angle_deg=20.0, num_layers=12):
    pressure_angle = math.radians(pressure_angle_deg)
    helix_angle = math.radians(helix_angle_deg)

    pitch_radius = module * teeth / 2.0
    base_radius = pitch_radius * math.cos(pressure_angle)
    addendum = module
    dedendum = 1.25 * module
    outer_radius = pitch_radius + addendum
    root_radius = pitch_radius - dedendum

    tooth_angle = 2 * math.pi / teeth
    half_tooth_angle = (math.pi / teeth) * 0.5

    def involute_point(base_r, t):
        x = base_r * (math.cos(t) + t * math.sin(t))
        y = base_r * (math.sin(t) - t * math.cos(t))
        return (x, y)

    t_max = math.sqrt((outer_radius / base_radius) ** 2 - 1) if outer_radius > base_radius else 0.4
    t_max = max(t_max, 0.35)
    n_pts = 10
    base_profile = [involute_point(base_radius, t_max * i / n_pts) for i in range(n_pts + 1)]

    def make_layer_wire(z_offset, extra_rotation):
        all_pts = []
        for tooth_i in range(teeth):
            center_angle = tooth_i * tooth_angle + extra_rotation

            left_pts = []
            for (px, py) in base_profile:
                r = math.hypot(px, py)
                if r < root_radius:
                    r = root_radius
                    ang = center_angle - half_tooth_angle
                else:
                    base_ang = math.atan2(py, px)
                    ang = center_angle - half_tooth_angle + base_ang
                left_pts.append((r * math.cos(ang), r * math.sin(ang)))

            right_pts = []
            for (px, py) in reversed(base_profile):
                r = math.hypot(px, py)
                if r < root_radius:
                    r = root_radius
                    ang = center_angle + half_tooth_angle
                else:
                    base_ang = math.atan2(py, px)
                    ang = center_angle + half_tooth_angle - base_ang
                right_pts.append((r * math.cos(ang), r * math.sin(ang)))

            all_pts.extend(left_pts)
            all_pts.extend(right_pts)

            next_center_angle = center_angle + tooth_angle
            root_pt_next = (
                root_radius * math.cos(next_center_angle - half_tooth_angle),
                root_radius * math.sin(next_center_angle - half_tooth_angle),
            )
            all_pts.append(root_pt_next)

        vectors = [App.Vector(x, y, z_offset) for (x, y) in all_pts]
        vectors.append(vectors[0])
        return Part.makePolygon(vectors)

    total_twist = (thickness / pitch_radius) * math.tan(helix_angle)

    wires = []
    for i in range(num_layers + 1):
        frac = i / num_layers
        z = thickness * frac
        rot = total_twist * frac
        wires.append(make_layer_wire(z, rot))

    gear_shape = Part.makeLoft(wires, True, False, False)
    bore = Part.makeCylinder(bore_radius, thickness + 2, App.Vector(0, 0, -1))
    gear_shape = gear_shape.cut(bore)

    return gear_shape, pitch_radius


# ---------------- 메인 빌드 함수 ----------------
_animation_state = {"timer": None}


def build_and_verify_mesh():
    doc = App.newDocument("HelicalGearPair")

    module = 2.0
    thickness = 15.0
    helix_angle_deg = 20.0

    teeth1 = 20
    teeth2 = 32

    # 평행축에서 맞물리려면 두 기어의 헬릭스각 방향이 서로 반대여야 함
    shape1, r1 = make_helical_gear_shape(
        module=module, teeth=teeth1, thickness=thickness,
        bore_radius=3.0, helix_angle_deg=helix_angle_deg
    )
    shape2, r2 = make_helical_gear_shape(
        module=module, teeth=teeth2, thickness=thickness,
        bore_radius=4.0, helix_angle_deg=-helix_angle_deg
    )

    center_distance = r1 + r2

    obj1 = doc.addObject("Part::Feature", "DriveGear_20T")
    obj1.Shape = shape1
    obj1.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), 0))

    obj2 = doc.addObject("Part::Feature", "DrivenGear_32T")
    obj2.Shape = shape2
    # 두 번째 기어 배치: 중심거리만큼 X축 이동
    # 잇수가 짝수/홀수에 따라 초기 위상이 안 맞을 수 있어 -half_tooth_angle 만큼 보정
    initial_offset_deg = 180.0 / teeth2  # 이와 이 사이 골짜기에 맞물리도록 근사 보정
    obj2.Placement = App.Placement(App.Vector(center_distance, 0, 0),
                                    App.Rotation(App.Vector(0, 0, 1), initial_offset_deg))

    doc.recompute()

    try:
        obj1.ViewObject.ShapeColor = (0.2, 0.5, 0.9)
        obj2.ViewObject.ShapeColor = (0.9, 0.4, 0.2)
        App.Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    print("=== 헬리컬 기어 페어 생성 완료 ===")
    print("구동기어(잇수 %d) 피치반경: %.2fmm" % (teeth1, r1))
    print("피동기어(잇수 %d) 피치반경: %.2fmm" % (teeth2, r2))
    print("중심거리: %.2fmm" % center_distance)
    print("기어비 (피동/구동): %.3f  (구동기어가 %d도 돌면 피동기어는 %.2f도)"
          % (teeth1 / teeth2, 360, 360 * teeth1 / teeth2))

    # ---------------- 회전 애니메이션 (기구학적 검증) ----------------
    gear_ratio = teeth1 / float(teeth2)  # 구동기어 회전량 대비 피동기어 회전량 비율
    drive_speed_deg_per_tick = 2.0        # 틱당 구동기어 회전각(도)
    state = {"angle1": 0.0, "angle2": initial_offset_deg}

    def tick():
        state["angle1"] += drive_speed_deg_per_tick
        # 두 기어는 서로 반대방향으로 회전해야 맞물림 (외접기어)
        state["angle2"] -= drive_speed_deg_per_tick * gear_ratio

        obj1.Placement = App.Placement(App.Vector(0, 0, 0),
                                        App.Rotation(App.Vector(0, 0, 1), state["angle1"]))
        obj2.Placement = App.Placement(App.Vector(center_distance, 0, 0),
                                        App.Rotation(App.Vector(0, 0, 1), state["angle2"]))
        doc.recompute()

    timer = QtCore.QTimer()
    timer.timeout.connect(tick)
    timer.start(50)  # 50ms 간격 (초당 20프레임)
    _animation_state["timer"] = timer

    print("애니메이션 시작됨. 두 기어가 반대방향으로 기어비에 맞춰 회전합니다.")
    print("정지하려면 stop_animation() 을 호출하세요.")

    return obj1, obj2


def stop_animation():
    t = _animation_state.get("timer")
    if t is not None:
        t.stop()
        _animation_state["timer"] = None
        print("애니메이션 정지됨.")
    else:
        print("실행 중인 애니메이션이 없습니다.")


build_and_verify_mesh()

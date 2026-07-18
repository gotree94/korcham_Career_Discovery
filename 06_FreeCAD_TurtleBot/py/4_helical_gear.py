# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 6: 헬리컬 기어 (Helical Gear)
----------------------------------------------------
- 인볼류트 치형 단면을 여러 층(layer)으로 쌓아 올리면서
  각 층마다 헬릭스 각도(helix angle)에 비례해 조금씩 회전시킨 뒤 Loft
- 스퍼기어보다 소음/진동이 적고 부하 분산이 좋은 실제 헬리컬 기어의
  치형 "꼬임(twist)" 특성을 형상으로 재현
- 실행 방법:
    1) exec(open('6_helical_gear.py', encoding='utf-8').read())
    2) 매크로로 등록 후 실행
    3) 콘솔에 통째로 붙여넣어도 안전 (함수로 감싸져 있음)
"""

import FreeCAD as App
import Part
import math


def build_helical_gear():
    doc = App.newDocument("HelicalGear")

    # ---------------- 파라미터 ----------------
    module = 2.0
    teeth = 24
    pressure_angle_deg = 20.0
    thickness = 20.0          # 기어 전체 두께
    bore_radius = 4.0         # 축 구멍 반지름
    helix_angle_deg = 20.0    # 헬릭스각 (사선각). 0에 가까우면 스퍼기어와 동일
    num_layers = 14           # 두께 방향 분할 층수 (많을수록 부드러운 트위스트)

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

    def make_tooth_profile_wire(z_offset, extra_rotation):
        """
        한 층(layer)에서의 기어 전체 단면(모든 이 포함) 폐곡선을 생성.
        extra_rotation: 헬리컬 트위스트로 인한 추가 회전각(radian)
        """
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

    # ---------------- 층별 단면 와이어 생성 (트위스트 적용) ----------------
    # 전체 두께(thickness)를 지나는 동안 회전하는 총 각도:
    # tan(helix_angle) = (피치원 둘레방향 이동량) / thickness  근사로 계산
    total_twist = (thickness / pitch_radius) * math.tan(helix_angle)

    wires = []
    for i in range(num_layers + 1):
        frac = i / num_layers
        z = thickness * frac
        rot = total_twist * frac
        wires.append(make_tooth_profile_wire(z, rot))

    gear_face_shape = Part.makeLoft(wires, True, False, False)

    # ---------------- 중심 보어(축 구멍) 관통 ----------------
    bore = Part.makeCylinder(bore_radius, thickness + 2, App.Vector(0, 0, -1))
    gear_solid = gear_face_shape.cut(bore)

    obj = doc.addObject("Part::Feature", "HelicalGear")
    obj.Shape = gear_solid
    doc.recompute()

    try:
        obj.ViewObject.ShapeColor = (0.85, 0.55, 0.15)
        App.Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass

    print("헬리컬 기어 생성 완료")
    print("잇수: %d, 모듈: %.1f, 피치반경: %.2fmm" % (teeth, module, pitch_radius))
    print("헬릭스각: %.1f도, 두께: %.1fmm, 총 트위스트: %.1f도"
          % (helix_angle_deg, thickness, math.degrees(total_twist)))

    return obj


build_helical_gear()

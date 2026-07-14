# -*- coding: utf-8 -*-
"""
FreeCAD Python 예제 5: 트위스트 터빈/프로펠러 블레이드 (Twisted Airfoil Blade)
------------------------------------------------------------------------------
- NACA 4자리 익형(airfoil) 방정식으로 여러 개의 단면 프로파일 생성
- 반경(허브->팁) 방향으로 갈수록 코드 길이는 줄고 피치각(twist)은 변화
- 각 단면을 Part.makeLoft로 이어붙여 실제 공력형상에 가까운 3D 곡면 생성
- 3~4개를 원형 배열하면 프로펠러/터빈 임펠러 완성
"""

import FreeCAD as App
import Part
import math

doc = App.newDocument("TurbineBlade")

# ---------------- 파라미터 ----------------
naca_code = "2412"    # NACA 4자리 익형 (2% 캠버, 최대캠버 위치 40%, 두께 12%)
hub_radius = 5.0       # 허브(중심축) 반지름
tip_radius = 60.0      # 블레이드 팁까지의 반경
num_sections = 10      # 단면 개수 (많을수록 부드러움)

chord_root = 18.0      # 허브 쪽 코드 길이 (익형 폭)
chord_tip = 6.0        # 팁 쪽 코드 길이 (테이퍼)

twist_root_deg = 35.0  # 허브 쪽 피치각
twist_tip_deg = 8.0    # 팁 쪽 피치각 (트위스트)

num_blades = 3          # 블레이드 개수 (원형 배열)


def naca4_profile(code, chord, n_points=20):
    """NACA 4자리 익형의 좌표를 계산 (상단/하단 표면)"""
    m = int(code[0]) / 100.0   # 최대 캠버
    p = int(code[1]) / 10.0    # 최대 캠버 위치
    t = int(code[2:4]) / 100.0  # 최대 두께

    pts_upper = []
    pts_lower = []

    for i in range(n_points + 1):
        # 코사인 분포로 앞전(leading edge) 부근 점을 촘촘하게
        beta = math.pi * i / n_points
        x = (1 - math.cos(beta)) / 2.0  # 0~1

        yt = 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x**2
                       + 0.2843 * x**3 - 0.1015 * x**4)

        if p == 0:
            yc = 0.0
            dyc_dx = 0.0
        elif x < p:
            yc = m / (p ** 2) * (2 * p * x - x ** 2)
            dyc_dx = 2 * m / (p ** 2) * (p - x)
        else:
            yc = m / ((1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x - x ** 2)
            dyc_dx = 2 * m / ((1 - p) ** 2) * (p - x)

        theta = math.atan(dyc_dx)

        xu = x - yt * math.sin(theta)
        yu = yc + yt * math.cos(theta)
        xl = x + yt * math.sin(theta)
        yl = yc - yt * math.cos(theta)

        pts_upper.append((xu * chord, yu * chord))
        pts_lower.append((xl * chord, yl * chord))

    # 앞전(leading edge)에서 뒷전(trailing edge)까지: 상단 -> 하단 역순으로 이어 폐곡선 구성
    all_pts = pts_upper + list(reversed(pts_lower[:-1]))
    return all_pts


def make_blade_section_wire(radius, chord, twist_deg):
    """특정 반경 위치에서의 익형 단면 와이어 생성 (twist 적용, 3D 좌표)"""
    profile_2d = naca4_profile(naca_code, chord)
    twist = math.radians(twist_deg)

    pts_3d = []
    for (px, py) in profile_2d:
        # 익형 단면은 로컬 좌표계(x=코드방향, y=두께방향)에서 twist만큼 회전
        # 로컬 x,y를 회전시킨 뒤, 블레이드의 반경방향(radius)과 두께방향(local y')에 배치
        rx = px * math.cos(twist) - py * math.sin(twist)
        ry = px * math.sin(twist) + py * math.cos(twist)
        # 블레이드는 Z축을 회전축(허브축)으로 두고, 단면은 XY 평면에서 radius만큼 떨어진 위치에 눕힘
        # 여기서는 단면을 X-Z 평면 성격으로 배치: X=코드/두께 평면, Y=반경방향
        pts_3d.append(App.Vector(rx - chord * 0.3, radius, ry))

    pts_3d.append(pts_3d[0])
    wire = Part.makePolygon(pts_3d)
    return wire


# ---------------- 반경 방향으로 단면 생성 ----------------
wires = []
for i in range(num_sections + 1):
    frac = i / num_sections  # 0(허브) ~ 1(팁)
    radius = hub_radius + (tip_radius - hub_radius) * frac
    chord = chord_root + (chord_tip - chord_root) * frac
    twist = twist_root_deg + (twist_tip_deg - twist_root_deg) * frac
    wire = make_blade_section_wire(radius, chord, twist)
    wires.append(wire)

# ---------------- Loft로 곡면 생성 ----------------
blade_solid = Part.makeLoft(wires, True, True)

# 허브축을 Y축(반경방향)에서 실제로는 Z축(회전축) 기준으로 세우기 위해 좌표계 정리:
# 위에서 단면을 Y=radius 위치에 배치했으므로, 최종 블레이드가 Z축을 중심으로 회전하도록
# X축 기준 90도 회전시켜 "반경방향=X, 회전축=Z" 형태로 정렬
blade_solid.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)

# ---------------- 허브(중심 원통) 생성 ----------------
hub_cyl = Part.makeCylinder(hub_radius, chord_root * 0.6,
                             App.Vector(0, 0, -chord_root * 0.3))

# ---------------- 블레이드 여러 개 원형 배열 + 허브와 결합 ----------------
all_blades = []
for i in range(num_blades):
    angle = 360.0 / num_blades * i
    b = blade_solid.copy()
    b.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)
    all_blades.append(b)

rotor = hub_cyl
for b in all_blades:
    rotor = rotor.fuse(b)

obj = doc.addObject("Part::Feature", "TurbineRotor")
obj.Shape = rotor
doc.recompute()

try:
    obj.ViewObject.ShapeColor = (0.8, 0.8, 0.85)
    App.Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass

print("터빈/프로펠러 로터 생성 완료")
print("블레이드 수: %d, 허브반경: %.1fmm, 팁반경: %.1fmm" % (num_blades, hub_radius, tip_radius))
print("루트 트위스트: %.1f도, 팁 트위스트: %.1f도" % (twist_root_deg, twist_tip_deg))

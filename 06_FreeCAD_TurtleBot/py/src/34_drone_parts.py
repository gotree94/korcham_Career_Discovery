# -*- coding: utf-8 -*-
"""
Part 7 - 34: 드론 부품 설계 매크로

드론용 프레임, 프로펠러 가드, 모터 마운트, 배터리 홀더 등을
파라메트릭으로 설계하는 FreeCAD 매크로.
다양한 드론 크기에 맞춘 부품을 자동 생성.

사용법: FreeCAD에서 실행하여 드론 부품들이 자동 생성됨.
"""

import sys
import math

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)


# ============================================================
# 드론 기본 프리셋
# ============================================================

DRONE_PRESETS = {
    "마이크로드론": {
        "description": "100mm 이하 마이크로 드론",
        "frame_width": 90.0,
        "arm_length": 40.0,
        "arm_width": 8.0,
        "arm_thickness": 3.0,
        "center_plate_thickness": 3.0,
        "motor_mount_size": "0802",
        "propeller_size": "2inch",
        "battery_capacity": "300mAh",
        "prop_guard_enable": True,
        "landing_gear_enable": False,
    },
    "소형드론": {
        "description": "150~250mm 소형 드론",
        "frame_width": 200.0,
        "arm_length": 70.0,
        "arm_width": 12.0,
        "arm_thickness": 4.0,
        "center_plate_thickness": 4.0,
        "motor_mount_size": "2205",
        "propeller_size": "5inch",
        "battery_capacity": "1500mAh",
        "prop_guard_enable": True,
        "landing_gear_enable": True,
    },
    "중형드론": {
        "description": "450~600mm 중형 드론",
        "frame_width": 500.0,
        "arm_length": 200.0,
        "arm_width": 20.0,
        "arm_thickness": 6.0,
        "center_plate_thickness": 6.0,
        "motor_mount_size": "2212",
        "propeller_size": "10inch",
        "battery_capacity": "5000mAh",
        "prop_guard_enable": False,
        "landing_gear_enable": True,
    },
    "대형드론": {
        "description": "800mm 이상 대형 드론",
        "frame_width": 1000.0,
        "arm_length": 400.0,
        "arm_width": 30.0,
        "arm_thickness": 8.0,
        "center_plate_thickness": 8.0,
        "motor_mount_size": "4114",
        "propeller_size": "15inch",
        "battery_capacity": "16000mAh",
        "prop_guard_enable": True,
        "landing_gear_enable": True,
    },
}


# ============================================================
# 모터 크기 정의
# ============================================================

MOTOR_SIZES = {
    "0802": {
        "diameter": 8.0,
        "height": 2.0,
        "mount_hole_diameter": 1.0,
        "mount_hole_spacing": 6.5,
        "shaft_diameter": 1.0,
        "description": "0802 브러시레스 모터 (마이크로용)",
    },
    "1104": {
        "diameter": 11.0,
        "height": 4.0,
        "mount_hole_diameter": 1.5,
        "mount_hole_spacing": 8.0,
        "shaft_diameter": 1.5,
        "description": "1104 브러시레스 모터",
    },
    "2205": {
        "diameter": 22.0,
        "height": 5.0,
        "mount_hole_diameter": 3.0,
        "mount_hole_spacing": 16.0,
        "shaft_diameter": 3.0,
        "description": "2205 브러시레스 모터 (5인치용)",
    },
    "2212": {
        "diameter": 22.0,
        "height": 12.0,
        "mount_hole_diameter": 3.0,
        "mount_hole_spacing": 16.0,
        "shaft_diameter": 3.0,
        "description": "2212 브러시레스 모터 (10인치용)",
    },
    "4114": {
        "diameter": 41.0,
        "height": 14.0,
        "mount_hole_diameter": 4.0,
        "mount_hole_spacing": 30.0,
        "shaft_diameter": 5.0,
        "description": "4114 브러시레스 모터 (대형용)",
    },
}


# ============================================================
# 프로펠러 크기 정의
# ============================================================

PROPELLER_SIZES = {
    "2inch": {
        "diameter": 50.8,
        "pitch": 30.0,
        "hub_diameter": 5.0,
        "blade_count": 2,
        "guard_diameter": 65.0,
        "description": "2인치 프로펠러",
    },
    "3inch": {
        "diameter": 76.2,
        "pitch": 45.0,
        "hub_diameter": 6.0,
        "blade_count": 2,
        "guard_diameter": 95.0,
        "description": "3인치 프로펠러",
    },
    "5inch": {
        "diameter": 127.0,
        "pitch": 60.0,
        "hub_diameter": 8.0,
        "blade_count": 2,
        "guard_diameter": 150.0,
        "description": "5인치 프로펠러",
    },
    "10inch": {
        "diameter": 254.0,
        "pitch": 100.0,
        "hub_diameter": 12.0,
        "blade_count": 2,
        "guard_diameter": 300.0,
        "description": "10인치 프로펠러",
    },
    "15inch": {
        "diameter": 381.0,
        "pitch": 150.0,
        "hub_diameter": 16.0,
        "blade_count": 2,
        "guard_diameter": 450.0,
        "description": "15인치 프로펠러",
    },
}


# ============================================================
# 배터리 스펙 정의
# ============================================================

BATTERY_SPECS = {
    "300mAh": {"voltage": 3.7, "cell_count": 1, "weight": 8.0, "description": "1S 300mAh"},
    "1500mAh": {"voltage": 14.8, "cell_count": 4, "weight": 150.0, "description": "4S 1500mAh"},
    "5000mAh": {"voltage": 14.8, "cell_count": 4, "weight": 450.0, "description": "4S 5000mAh"},
    "16000mAh": {"voltage": 22.2, "cell_count": 6, "weight": 2500.0, "description": "6S 16000mAh"},
}


# ============================================================
# 공차 설정
# ============================================================

class ToleranceConfig:
    """드론 부품 조립 공차를 관리하는 클래스"""

    def __init__(self):
        """기본 공차 초기화"""
        self.general_tolerance = 0.2
        self.motor_mount_tolerance = 0.3
        self.screw_tolerance = 0.1
        self.prop_clearance = 3.0
        self.wire_channel_width = 2.0


# ============================================================
# 센터 플레이트 생성
# ============================================================

def create_center_plate(preset_name, tolerance=None):
    """
    드론 센터(메인) 플레이트를 생성한다.

    매개변수:
        preset_name (str): 드론 프리셋 키
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 센터 플레이트 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if preset_name not in DRONE_PRESETS:
        print(f"[오류] 알 수 없는 프리셋: {preset_name}")
        return None

    preset = DRONE_PRESETS[preset_name]
    print(f"[정보] {preset['description']} 센터 플레이트 생성 중...")

    width = preset["frame_width"]
    depth = width
    thickness = preset["center_plate_thickness"]

    # 기본 형태: 원형/사각형 중앙 플레이트
    center_x = width / 2
    center_y = depth / 2

    # 메인 플레이트 (모서리 둥근 사각형)
    corner_radius = width * 0.15
    plate = _make_rounded_rect(width, depth, thickness, corner_radius)

    # 배터리 장착 영역
    battery_key = preset["battery_capacity"]
    if battery_key in BATTERY_SPECS:
        battery = BATTERY_SPECS[battery_key]
        batt_width = battery["weight"] * 0.06 + 10.0  # 대략적 치수 추정
        batt_depth = batt_width * 0.6

        # 배터리 벨크로 스트랩 홀
        strap_width = 20.0
        slot_y1 = center_y - batt_depth / 2 - strap_width / 2
        slot_y2 = center_y + batt_depth / 2 + strap_width / 2

        for slot_y in [slot_y1, slot_y2]:
            strap_slot = Part.makeBox(
                strap_width, 5.0, thickness + 1,
                Base.Vector(center_x - strap_width / 2, slot_y - 2.5, -0.5)
            )
            plate = plate.cut(strap_slot)

    # 전선 채널 홀
    wire_channel = tolerance.wire_channel_width
    num_arms = 4 if preset["arm_length"] > 100 else 4

    for angle in range(0, 360, 90):
        rad = math.radians(angle)
        cx = center_x + math.cos(rad) * width * 0.25
        cy = center_y + math.sin(rad) * depth * 0.25

        channel_hole = Part.makeCylinder(
            wire_channel / 2, thickness + 1,
            Base.Vector(cx, cy, -0.5),
            Base.Vector(0, 0, 1)
        )
        plate = plate.cut(channel_hole)

    # 조립 나사 홀
    screw_spacing = width * 0.6
    screw_diameter = 3.0 + tolerance.screw_tolerance

    screw_positions = []
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        sx = center_x + math.cos(rad) * screw_spacing / 2
        sy = center_y + math.sin(rad) * screw_spacing / 2
        screw_positions.append(Base.Vector(sx, sy, 0))

    for pos in screw_positions:
        hole = Part.makeCylinder(
            screw_diameter / 2, thickness + 1,
            Base.Vector(pos.x, pos.y, -0.5),
            Base.Vector(0, 0, 1)
        )
        plate = plate.cut(hole)

    print(f"[정보] 센터 플레이트 생성 완료: {width}x{depth}x{thickness}mm")
    return plate


# ============================================================
# 암(팔) 생성
# ============================================================

def create_arm(preset_name, arm_index=0, tolerance=None):
    """
    드론 암(팔)을 생성한다.

    매개변수:
        preset_name (str): 드론 프리셋 키
        arm_index (int): 암 인덱스
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 암 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    preset = DRONE_PRESETS[preset_name]
    print(f"[정보] 암 {arm_index + 1} 생성 중...")

    arm_length = preset["arm_length"]
    arm_width = preset["arm_width"]
    arm_thickness = preset["arm_thickness"]

    # 암 본체
    arm = Part.makeBox(arm_length, arm_width, arm_thickness)

    # 베이스 연결부 (둥근 모서리)
    base_round = Part.makeCylinder(
        arm_width / 2, arm_thickness,
        Base.Vector(arm_width / 2, arm_width / 2, 0),
        Base.Vector(0, 0, 1)
    )
    arm = arm.fuse(base_round)

    # 모터 마운트 홀 (끝 부분)
    motor_key = preset["motor_mount_size"]
    if motor_key in MOTOR_SIZES:
        motor = MOTOR_SIZES[motor_key]
        mount_spacing = motor["mount_hole_spacing"] + tolerance.motor_mount_tolerance

        motor_center_x = arm_length - arm_width / 2
        motor_center_y = arm_width / 2

        # 모터 중앙 홀
        center_hole = Part.makeCylinder(
            motor["shaft_diameter"] / 2 + tolerance.screw_tolerance,
            arm_thickness + 1,
            Base.Vector(motor_center_x, motor_center_y, -0.5),
            Base.Vector(0, 0, 1)
        )
        arm = arm.cut(center_hole)

        # 모터 마운트 나사 홀 (4개)
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            mx = motor_center_x + math.cos(rad) * mount_spacing / 2
            my = motor_center_y + math.sin(rad) * mount_spacing / 2

            mount_hole = Part.makeCylinder(
                motor["mount_hole_diameter"] / 2 + tolerance.screw_tolerance,
                arm_thickness + 1,
                Base.Vector(mx, my, -0.5),
                Base.Vector(0, 0, 1)
            )
            arm = arm.cut(mount_hole)

    # 베이스 연결 나사 홀
    base_screw_spacing = arm_width * 0.6
    base_screw_diameter = 3.0 + tolerance.screw_tolerance

    for dy in [-base_screw_spacing / 2, base_screw_spacing / 2]:
        hole = Part.makeCylinder(
            base_screw_diameter / 2, arm_thickness + 1,
            Base.Vector(arm_width / 2, arm_width / 2 + dy, -0.5),
            Base.Vector(0, 0, 1)
        )
        arm = arm.cut(hole)

    # 경량화 캐비티 (두께가 충분할 때)
    if arm_thickness >= 4.0:
        cavity_margin = 2.0
        cavity = Part.makeBox(
            arm_length - arm_width * 2, arm_width - cavity_margin * 2,
            arm_thickness - cavity_margin * 2,
            Base.Vector(arm_width, cavity_margin, cavity_margin)
        )
        arm = arm.cut(cavity)

    print(f"[정보] 암 {arm_index + 1} 생성 완료: {arm_length}x{arm_width}x{arm_thickness}mm")
    return arm


# ============================================================
# 프로펠러 가드 생성
# ============================================================

def create_prop_guard(preset_name, tolerance=None):
    """
    프로펠러 안전 가드를 생성한다.

    매개변수:
        preset_name (str): 드론 프리셋 키
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 프로펠러 가드 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    preset = DRONE_PRESETS[preset_name]
    prop_key = preset["propeller_size"]

    if prop_key not in PROPELLER_SIZES:
        print(f"[오류] 알 수 없는 프로펠러 크기: {prop_key}")
        return None

    prop = PROPELLER_SIZES[prop_key]
    guard_diameter = prop["guard_diameter"]
    guard_height = 15.0
    guard_thickness = 2.0

    print(f"[정보] {prop['description']} 가드 생성 중...")

    # 외부 링
    outer_ring = Part.makeCylinder(
        guard_diameter / 2, guard_height
    ).cut(
        Part.makeCylinder(
            guard_diameter / 2 - guard_thickness, guard_height + 1,
            Base.Vector(0, 0, -0.5)
        )
    )

    # 내부 링 (프로펠러 회전 영역)
    inner_clearance = tolerance.prop_clearance
    inner_ring = Part.makeCylinder(
        prop["diameter"] / 2 + inner_clearance, guard_height
    ).cut(
        Part.makeCylinder(
            prop["diameter"] / 2 + inner_clearance - guard_thickness,
            guard_height + 1,
            Base.Vector(0, 0, -0.5)
        )
    )

    # 가드 합체
    guard = outer_ring.fuse(inner_ring)

    # 연결 스트럿 (외부-내부 연결)
    strut_count = 4
    strut_width = 3.0
    outer_r = guard_diameter / 2
    inner_r = prop["diameter"] / 2 + inner_clearance

    for i in range(strut_count):
        angle = math.radians(i * 360 / strut_count)
        sx = math.cos(angle) * inner_r
        sy = math.sin(angle) * inner_r
        ex = math.cos(angle) * outer_r
        ey = math.sin(angle) * outer_r

        strut_length = outer_r - inner_r
        strut = Part.makeBox(
            strut_length, strut_width, guard_height,
            Base.Vector(
                sx,
                sy - strut_width / 2,
                0
            )
        )

        # 스트럿 회전
        if angle != 0:
            strut.rotate(
                Base.Vector(sx, sy, 0),
                Base.Vector(0, 0, 1),
                math.degrees(angle)
            )

        guard = guard.fuse(strut)

    # 장착 나사 홀
    mount_spacing = guard_diameter * 0.7
    screw_diameter = 2.0 + tolerance.screw_tolerance

    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        mx = math.cos(rad) * mount_spacing / 2
        my = math.sin(rad) * mount_spacing / 2

        mount_hole = Part.makeCylinder(
            screw_diameter / 2, guard_height + 1,
            Base.Vector(mx, my, -0.5),
            Base.Vector(0, 0, 1)
        )
        guard = guard.cut(mount_hole)

    print(f"[정보] 프로펠러 가드 생성 완료 (외경={guard_diameter}mm)")
    return guard


# ============================================================
# 랜딩 기어 생성
# ============================================================

def create_landing_gear(preset_name, tolerance=None):
    """
    랜딩 기어(착지 다리)를 생성한다.

    매개변수:
        preset_name (str): 드론 프리셋 키
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 랜딩 기어 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    preset = DRONE_PRESETS[preset_name]
    print(f"[정보] 랜딩 기어 생성 중...")

    # 기어 치수 (드론 크기에 비례)
    frame_width = preset["frame_width"]
    gear_height = frame_width * 0.15
    gear_width = frame_width * 0.08
    gear_thickness = max(3.0, frame_width * 0.02)

    # 수직 다리
    leg_height = gear_height
    leg = Part.makeBox(gear_thickness, gear_width, leg_height)

    # 수평 발판
    foot_length = frame_width * 0.2
    foot = Part.makeBox(
        foot_length, gear_width + 6.0, gear_thickness,
        Base.Vector(-foot_length / 2 + gear_thickness / 2, -3.0, 0)
    )

    gear = leg.fuse(foot)

    # 장착 홀
    mount_hole = Part.makeCylinder(
        2.0 + tolerance.screw_tolerance, leg_height + 1,
        Base.Vector(gear_thickness / 2, gear_width / 2, -0.5),
        Base.Vector(0, 0, 1)
    )
    gear = gear.cut(mount_hole)

    print(f"[정보] 랜딩 기어 생성 완료 (높이={gear_height:.1f}mm)")
    return gear


# ============================================================
# 모터 마운트 브래킷 생성
# ============================================================

def create_motor_mount_bracket(motor_size_name, arm_width, tolerance=None):
    """
    모터 마운트 브래킷을 생성한다.

    매개변수:
        motor_size_name (str): 모터 크기 키
        arm_width (float): 암 너비 (mm)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 모터 마운트 브래킷 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if motor_size_name not in MOTOR_SIZES:
        print(f"[오류] 알 수 없는 모터 크기: {motor_size_name}")
        return None

    motor = MOTOR_SIZES[motor_size_name]
    print(f"[정보] {motor['description']} 마운트 브래킷 생성 중...")

    # 브래킷 치수
    bracket_size = max(motor["diameter"] + 8.0, arm_width + 4.0)
    bracket_height = 12.0
    bracket_thickness = 3.0

    # 베이스 플레이트
    base = Part.makeBox(bracket_size, bracket_size, bracket_thickness)

    # 모터 구멍
    motor_clearance = 1.0
    motor_hole = Part.makeCylinder(
        motor["diameter"] / 2 + motor_clearance, bracket_thickness + 1,
        Base.Vector(bracket_size / 2, bracket_size / 2, -0.5),
        Base.Vector(0, 0, 1)
    )
    base = base.cut(motor_hole)

    # 마운트 나사 홀
    spacing = motor["mount_hole_spacing"] + tolerance.motor_mount_tolerance
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        mx = bracket_size / 2 + math.cos(rad) * spacing / 2
        my = bracket_size / 2 + math.sin(rad) * spacing / 2

        hole = Part.makeCylinder(
            motor["mount_hole_diameter"] / 2 + tolerance.screw_tolerance,
            bracket_thickness + 1,
            Base.Vector(mx, my, -0.5),
            Base.Vector(0, 0, 1)
        )
        base = base.cut(hole)

    # 수직 월
    wall = Part.makeBox(bracket_size, bracket_thickness, bracket_height - bracket_thickness,
                        Base.Vector(0, 0, bracket_thickness))
    bracket = base.fuse(wall)

    print(f"[정보] 모터 마운트 브래킷 생성 완료")
    return bracket


# ============================================================
# 전체 드론 프레임 조립
# ============================================================

def assemble_drone_frame(preset_name, tolerance=None):
    """
    지정된 프리셋으로 전체 드론 프레임을 조립한다.

    매개변수:
        preset_name (str): 드론 프리셋 키
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        dict: 생성된 부품들의 딕셔너리
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if preset_name not in DRONE_PRESETS:
        print(f"[오류] 알 수 없는 프리셋: {preset_name}")
        return None

    preset = DRONE_PRESETS[preset_name]
    print(f"\n[정보] === {preset['description']} 조립 시작 ===")

    parts = {}

    # 1. 센터 플레이트
    print("\n[단계 1] 센터 플레이트")
    parts["center_plate"] = create_center_plate(preset_name, tolerance)

    # 2. 암 (4개)
    for i in range(4):
        print(f"\n[단계 {i + 2}] 암 {i + 1}")
        parts[f"arm_{i + 1}"] = create_arm(preset_name, i, tolerance)

    # 3. 프로펠러 가드 (4개)
    if preset["prop_guard_enable"]:
        for i in range(4):
            print(f"\n[단계 {i + 6}] 프로펠러 가드 {i + 1}")
            parts[f"prop_guard_{i + 1}"] = create_prop_guard(preset_name, tolerance)

    # 4. 랜딩 기어
    if preset["landing_gear_enable"]:
        print("\n[단계 10] 랜딩 기어")
        parts["landing_gear_1"] = create_landing_gear(preset_name, tolerance)
        parts["landing_gear_2"] = create_landing_gear(preset_name, tolerance)

    # 5. 모터 마운트 브래킷 (4개)
    for i in range(4):
        print(f"\n[단계 {i + 12}] 모터 마운트 브래킷 {i + 1}")
        parts[f"motor_mount_{i + 1}"] = create_motor_mount_bracket(
            preset["motor_mount_size"], preset["arm_width"], tolerance
        )

    print(f"\n[정보] === 조립 완료: {len(parts)}개 부품 ===")
    return parts


# ============================================================
# FreeCAD 통합 함수
# ============================================================

def add_to_freecad_document(shape, name):
    """
    형태를 FreeCAD 활성 도큐먼트에 추가한다.
    """
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("드론부품")

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()
        print(f"[정보] 도큐먼트에 '{name}' 추가 완료")
        return obj
    except Exception as e:
        print(f"[오류] 도큐먼트 추가 실패: {e}")
        return None


def export_stl(shape, filename):
    """
    형태를 STL 파일로 내보낸다.
    """
    try:
        mesh = Part.Mesh()
        if hasattr(shape, "Shapes"):
            for s in shape.Shapes:
                mesh.addMesh(s.tessellate(0.5))
        else:
            mesh.addMesh(shape.tessellate(0.5))
        mesh.write(filename)
        print(f"[정보] STL 파일 저장 완료: {filename}")
        return filename
    except Exception as e:
        print(f"[오류] STL 내보내기 실패: {e}")
        return None


# ============================================================
# 유틸리티 함수
# ============================================================

def _make_rounded_rect(length, width, height, radius):
    """
    모서리가 둥근 사각 프리즘을 생성한다.
    """
    # 기본 사각형
    box = Part.makeBox(length, width, height)

    # 모서리 둥글게 만들기 (4개 모서리에서 상자 잘라내기)
    cx, cy = length / 2, width / 2

    # 원형 코너용 실린더로 잘라내기
    for x, y in [(0, 0), (length, 0), (0, width), (length, width)]:
        corner_box = Part.makeBox(radius, radius, height,
                                  Base.Vector(
                                      x - radius if x > 0 else 0,
                                      y - radius if y > 0 else 0,
                                      0
                                  ))
        box = box.cut(corner_box)

        # 둥근 모서리 추가
        fillet = Part.makeCylinder(
            radius, height,
            Base.Vector(
                x if x > 0 else radius,
                y if y > 0 else radius,
                0
            ),
            Base.Vector(0, 0, 1)
        )
        box = box.fuse(fillet)

    return box


# ============================================================
# 메인 실행 함수
# ============================================================

def run():
    """
    메인 실행 함수.
    다양한 드론 부품을 생성하여 FreeCAD 도큐먼트에 추가한다.
    """
    print("=" * 60)
    print("  드론 부품 설계 매크로 시작")
    print("=" * 60)

    # 프리셋 목록 출력
    print("\n사용 가능한 드론 프리셋:")
    for idx, (name, info) in enumerate(DRONE_PRESETS.items(), 1):
        print(f"  {idx}. {name} - {info['description']}")

    # 모터 크기
    print("\n사용 가능한 모터 크기:")
    for name, info in MOTOR_SIZES.items():
        print(f"  - {name}: {info['description']}")

    # 프로펠러
    print("\n사용 가능한 프로펠러:")
    for name, info in PROPELLER_SIZES.items():
        print(f"  - {name}: {info['description']} ({info['diameter']}mm)")

    tolerance = ToleranceConfig()

    # 소형 드론 조립
    print(f"\n{'─' * 40}")
    parts = assemble_drone_frame("소형드론", tolerance)

    if parts:
        for name, shape in parts.items():
            add_to_freecad_document(shape, f"소형드론_{name}")

    print(f"\n{'=' * 60}")
    print("  드론 부품 설계 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()

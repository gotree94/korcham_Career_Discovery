# -*- coding: utf-8 -*-
"""
Part 7 - 35: IoT 보드 케이스 설계 매크로

Arduino, Raspberry Pi, ESP32 등 IoT 보드 보호용 인클로저를
파라메트릭으로 설계하는 FreeCAD 매크로.
보드 크기, 포트 위치, 마운트 홀에 맞춘 맞춤 케이스 자동 생성.

사용법: FreeCAD에서 실행하여 IoT 보드 케이스가 자동 생성됨.
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
# IoT 보드 프리셋 정의
# ============================================================

BOARD_DB = {
    "Arduino Uno": {
        "description": "Arduino Uno R3",
        "width": 68.88,
        "depth": 53.34,
        "hole_spacing_x": 63.5,
        "hole_spacing_y": 48.26,
        "hole_diameter": 3.2,
        "mounting_hole_count": 4,
        "ports": {
            "USB_B": {"width": 12.0, "height": 11.0, "x": -1.5, "y": 15.0, "depth_offset": 0.0},
            "DC_jack": {"width": 9.0, "height": 11.0, "x": -1.5, "y": 33.0, "depth_offset": 0.0},
            "pin_header_digital": {"width": 32.0, "height": 3.0, "x": 18.0, "y": 53.34, "depth_offset": 0.0},
            "pin_header_analog": {"width": 20.0, "height": 3.0, "x": 42.0, "y": -1.5, "depth_offset": 0.0},
            "power_header": {"width": 14.0, "height": 3.0, "x": -1.5, "y": 42.0, "depth_offset": 0.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 10.0,
        "clearance_bottom": 3.0,
    },
    "Arduino Nano": {
        "description": "Arduino Nano V3",
        "width": 45.0,
        "depth": 18.0,
        "hole_spacing_x": 40.64,
        "hole_spacing_y": 15.24,
        "hole_diameter": 3.2,
        "mounting_hole_count": 4,
        "ports": {
            "mini_USB": {"width": 8.0, "height": 3.0, "x": 18.5, "y": -1.5, "depth_offset": 0.0},
            "pin_header_left": {"width": 15.0, "height": 2.5, "x": 0.0, "y": 7.5, "depth_offset": 0.0},
            "pin_header_right": {"width": 15.0, "height": 2.5, "x": 30.0, "y": 7.5, "depth_offset": 0.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 8.0,
        "clearance_bottom": 2.0,
    },
    "ESP32_DevKit": {
        "description": "ESP32 DevKit V1",
        "width": 25.5,
        "depth": 51.5,
        "hole_spacing_x": 22.86,
        "hole_spacing_y": 48.9,
        "hole_diameter": 2.0,
        "mounting_hole_count": 4,
        "ports": {
            "micro_USB": {"width": 8.0, "height": 2.5, "x": 8.75, "y": -1.5, "depth_offset": 0.0},
            "pin_header_left": {"width": 12.0, "height": 2.5, "x": 0.0, "y": 25.0, "depth_offset": 0.0},
            "pin_header_right": {"width": 12.0, "height": 2.5, "x": 13.5, "y": 25.0, "depth_offset": 0.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 8.0,
        "clearance_bottom": 2.0,
    },
    "ESP32_S3_DevKit": {
        "description": "ESP32-S3 DevKitC-1",
        "width": 25.5,
        "depth": 60.5,
        "hole_spacing_x": 22.86,
        "hole_spacing_y": 57.9,
        "hole_diameter": 2.0,
        "mounting_hole_count": 4,
        "ports": {
            "USB_C": {"width": 9.0, "height": 3.5, "x": 8.25, "y": -1.5, "depth_offset": 0.0},
            "pin_header_left": {"width": 12.0, "height": 2.5, "x": 0.0, "y": 28.0, "depth_offset": 0.0},
            "pin_header_right": {"width": 12.0, "height": 2.5, "x": 13.5, "y": 28.0, "depth_offset": 0.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 8.0,
        "clearance_bottom": 2.0,
    },
    "Raspberry_Pi_Pico": {
        "description": "Raspberry Pi Pico",
        "width": 21.0,
        "depth": 51.0,
        "hole_spacing_x": 15.24,
        "hole_spacing_y": 46.99,
        "hole_diameter": 2.0,
        "mounting_hole_count": 2,
        "ports": {
            "micro_USB": {"width": 8.0, "height": 2.5, "x": 6.5, "y": -1.5, "depth_offset": 0.0},
            "pin_header_left": {"width": 10.0, "height": 2.5, "x": 0.0, "y": 25.0, "depth_offset": 0.0},
            "pin_header_right": {"width": 10.0, "height": 2.5, "x": 11.0, "y": 25.0, "depth_offset": 0.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 8.0,
        "clearance_bottom": 2.0,
    },
    "Raspberry_Pi_4B": {
        "description": "Raspberry Pi 4 Model B",
        "width": 85.6,
        "depth": 56.5,
        "hole_spacing_x": 58.0,
        "hole_spacing_y": 49.0,
        "hole_diameter": 2.75,
        "mounting_hole_count": 4,
        "ports": {
            "USB_C_power": {"width": 9.0, "height": 3.5, "x": -1.5, "y": 10.0, "depth_offset": 0.0},
            "USB_3": {"width": 14.0, "height": 14.0, "x": -1.5, "y": 18.0, "depth_offset": 0.0},
            "USB_2": {"width": 14.0, "height": 14.0, "x": -1.5, "y": 36.0, "depth_offset": 0.0},
            "HDMI_micro": {"width": 11.5, "height": 5.5, "x": 65.0, "y": 10.0, "depth_offset": 0.0},
            "ethernet": {"width": 16.0, "height": 14.0, "x": 65.0, "y": 30.0, "depth_offset": 0.0},
            "GPIO_header": {"width": 51.0, "height": 5.0, "x": 17.0, "y": 56.5, "depth_offset": 0.0},
            "CSI_camera": {"width": 22.0, "height": 3.0, "x": 25.0, "y": 28.0, "depth_offset": 0.0},
            "DSI_display": {"width": 22.0, "height": 3.0, "x": 25.0, "y": 42.0, "depth_offset": 0.0},
            "micro_SD": {"width": 14.0, "height": 2.5, "x": 35.0, "y": -1.5, "depth_offset": 0.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 12.0,
        "clearance_bottom": 4.0,
    },
}


# ============================================================
# 공차 설정
# ============================================================

class ToleranceConfig:
    """케이스 조립 공차를 관리하는 클래스"""

    def __init__(self):
        """기본 공차 초기화"""
        self.general_tolerance = 0.2
        self.port_clearance = 1.0
        self.screw_tolerance = 0.15
        self.wall_clearance = 0.3
        self.snap_fit_tolerance = 0.1


# ============================================================
# 하단 케이스 생성
# ============================================================

def create_bottom_case(board_name, tolerance=None):
    """
    IoT 보드용 하단 케이스(베이스)를 생성한다.

    매개변수:
        board_name (str): 보드 이름 (BOARD_DB 키)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 하단 케이스 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if board_name not in BOARD_DB:
        print(f"[오류] 알 수 없는 보드: {board_name}")
        return None

    board = BOARD_DB[board_name]
    print(f"[정보] {board['description']} 하단 케이스 생성 중...")

    # 케이스 치수
    wall_thickness = 2.5
    case_inner_width = board["width"] + tolerance.wall_clearance * 2
    case_inner_depth = board["depth"] + tolerance.wall_clearance * 2
    case_inner_height = board["clearance_bottom"] + board["board_thickness"] + 2.0

    case_width = case_inner_width + wall_thickness * 2
    case_depth = case_inner_depth + wall_thickness * 2
    case_height = case_inner_height + wall_thickness

    # 하단 케이스 본체
    case = Part.makeBox(case_width, case_depth, case_height)

    # 내부 캐비티
    cavity = Part.makeBox(
        case_inner_width, case_inner_depth, case_inner_height + 1,
        Base.Vector(wall_thickness, wall_thickness, wall_thickness)
    )
    case = case.cut(cavity)

    # 보드 장착 기둥 (스탠드오프)
    board_center_x = case_width / 2
    board_center_y = case_depth / 2

    standoff_height = board["clearance_bottom"]
    standoff_diameter = 6.0
    standoff_hole_diameter = board["hole_diameter"] + tolerance.screw_tolerance

    # 보드 홀 간격
    hx = board["hole_spacing_x"] / 2
    hy = board["hole_spacing_y"] / 2

    standoff_positions = [
        (board_center_x - hx, board_center_y - hy),
        (board_center_x + hx, board_center_y - hy),
        (board_center_x - hx, board_center_y + hy),
        (board_center_x + hx, board_center_y + hy),
    ]

    for sx, sy in standoff_positions[:board["mounting_hole_count"]]:
        # 스탠드오프 몸체
        standoff = Part.makeCylinder(
            standoff_diameter / 2, standoff_height,
            Base.Vector(sx, sy, wall_thickness),
            Base.Vector(0, 0, 1)
        )
        case = case.fuse(standoff)

        # 나사 홀
        screw_hole = Part.makeCylinder(
            standoff_hole_diameter / 2, standoff_height + 1,
            Base.Vector(sx, sy, wall_thickness - 0.5),
            Base.Vector(0, 0, 1)
        )
        case = case.cut(screw_hole)

    # 포트 슬롯 (케이스 벽면)
    for port_name, port_info in board["ports"].items():
        px = port_info["x"]
        py = port_info["y"]
        pw = port_info["width"] + tolerance.port_clearance
        ph = port_info["height"] + tolerance.port_clearance

        # 포트 위치 변환 (보드 좌표 → 케이스 좌표)
        port_case_x = wall_thickness + (px + board["width"] / 2) - pw / 2
        port_case_y = wall_thickness + (py + board["depth"] / 2) - ph / 2
        port_z_start = wall_thickness + board["clearance_bottom"]

        # 포트가 케이스 벽면을 뚫는지 확인
        if px < 0:
            # 왼쪽 벽면 포트
            slot = Part.makeBox(
                wall_thickness + 1, pw, ph,
                Base.Vector(0, port_case_y, port_z_start)
            )
            case = case.cut(slot)
        elif px + pw > board["width"]:
            # 오른쪽 벽면 포트
            slot = Part.makeBox(
                wall_thickness + 1, pw, ph,
                Base.Vector(case_width - wall_thickness - 1, port_case_y, port_z_start)
            )
            case = case.cut(slot)
        elif py < 0:
            # 앞쪽 벽면 포트
            slot = Part.makeBox(
                pw, wall_thickness + 1, ph,
                Base.Vector(port_case_x, 0, port_z_start)
            )
            case = case.cut(slot)
        elif py + ph > board["depth"]:
            # 뒤쪽 벽면 포트
            slot = Part.makeBox(
                pw, wall_thickness + 1, ph,
                Base.Vector(port_case_x, case_depth - wall_thickness - 1, port_z_start)
            )
            case = case.cut(slot)

    # 조립 나사 홀 (하단에서 상단 커버 연결)
    screw_positions = [
        (wall_thickness + 2.0, wall_thickness + 2.0),
        (case_width - wall_thickness - 2.0, wall_thickness + 2.0),
        (wall_thickness + 2.0, case_depth - wall_thickness - 2.0),
        (case_width - wall_thickness - 2.0, case_depth - wall_thickness - 2.0),
    ]

    for sx, sy in screw_positions:
        screw_hole = Part.makeCylinder(
            1.5 + tolerance.screw_tolerance, case_height + 1,
            Base.Vector(sx, sy, -0.5),
            Base.Vector(0, 0, 1)
        )
        case = case.cut(screw_hole)

    print(f"[정보] 하단 케이스 생성 완료: {case_width:.1f}x{case_depth:.1f}x{case_height:.1f}mm")
    return case


# ============================================================
# 상단 커버 생성
# ============================================================

def create_top_cover(board_name, tolerance=None):
    """
    IoT 보드용 상단 커버를 생성한다.

    매개변수:
        board_name (str): 보드 이름 (BOARD_DB 키)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 상단 커버 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if board_name not in BOARD_DB:
        print(f"[오류] 알 수 없는 보드: {board_name}")
        return None

    board = BOARD_DB[board_name]
    print(f"[정보] {board['description']} 상단 커버 생성 중...")

    wall_thickness = 2.5
    case_inner_width = board["width"] + tolerance.wall_clearance * 2
    case_inner_depth = board["depth"] + tolerance.wall_clearance * 2
    case_inner_height = board["clearance_top"]

    cover_width = case_inner_width + wall_thickness * 2
    cover_depth = case_inner_depth + wall_thickness * 2
    cover_height = case_inner_height + wall_thickness

    # 상단 커버 본체
    cover = Part.makeBox(cover_width, cover_depth, cover_height)

    # 내부 캐비티 (보드 위 공간)
    cavity = Part.makeBox(
        case_inner_width, case_inner_depth, case_inner_height,
        Base.Vector(wall_thickness, wall_thickness, 0)
    )
    cover = cover.cut(cavity)

    # 환기구 (상단)
    vent_hole_count = 4
    vent_hole_diameter = 4.0
    vent_spacing_x = case_inner_width * 0.5
    vent_spacing_y = case_inner_depth * 0.5

    board_center_x = cover_width / 2
    board_center_y = cover_depth / 2

    for i in range(vent_hole_count):
        angle = math.radians(i * 360 / vent_hole_count)
        vx = board_center_x + math.cos(angle) * vent_spacing_x / 2
        vy = board_center_y + math.sin(angle) * vent_spacing_y / 2

        vent = Part.makeCylinder(
            vent_hole_diameter / 2, wall_thickness + 1,
            Base.Vector(vx, vy, -0.5),
            Base.Vector(0, 0, 1)
        )
        cover = cover.cut(vent)

    # 조립 나사 홀
    screw_positions = [
        (wall_thickness + 2.0, wall_thickness + 2.0),
        (cover_width - wall_thickness - 2.0, wall_thickness + 2.0),
        (wall_thickness + 2.0, cover_depth - wall_thickness - 2.0),
        (cover_width - wall_thickness - 2.0, cover_depth - wall_thickness - 2.0),
    ]

    for sx, sy in screw_positions:
        screw_hole = Part.makeCylinder(
            1.5 + tolerance.screw_tolerance, cover_height + 1,
            Base.Vector(sx, sy, -0.5),
            Base.Vector(0, 0, 1)
        )
        cover = cover.cut(screw_hole)

    # LED 인디케이터 홀 (선택적)
    led_hole_diameter = 3.0
    led_x = board_center_x + case_inner_width * 0.3
    led_y = board_center_y - case_inner_depth * 0.3

    led_hole = Part.makeCylinder(
        led_hole_diameter / 2, wall_thickness + 1,
        Base.Vector(led_x, led_y, -0.5),
        Base.Vector(0, 0, 1)
    )
    cover = cover.cut(led_hole)

    print(f"[정보] 상단 커버 생성 완료: {cover_width:.1f}x{cover_depth:.1f}x{cover_height:.1f}mm")
    return cover


# ============================================================
# 벽면 마운트 브래킷 생성
# ============================================================

def create_wall_mount_bracket(board_name, tolerance=None):
    """
    벽면 설치용 마운트 브래킷을 생성한다.

    매개변수:
        board_name (str): 보드 이름 (BOARD_DB 키)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 벽면 마운트 브래킷 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if board_name not in BOARD_DB:
        print(f"[오류] 알 수 없는 보드: {board_name}")
        return None

    board = BOARD_DB[board_name]
    print(f"[정보] {board['description']} 벽면 마운트 브래킷 생성 중...")

    wall_thickness = 3.0
    bracket_width = board["width"] + 20.0
    bracket_height = board["depth"] + 30.0
    bracket_depth = 15.0

    # 메인 브래킷 플레이트
    bracket = Part.makeBox(bracket_width, bracket_depth, bracket_height)

    # 보드 고정 나사 홀
    hx = board["hole_spacing_x"] / 2
    hy = board["hole_spacing_y"] / 2
    board_center_x = bracket_width / 2
    board_center_y = bracket_depth / 2

    standoff_positions = [
        (board_center_x - hx, board_center_y),
        (board_center_x + hx, board_center_y),
    ]

    for sx, sy in standoff_positions[:board["mounting_hole_count"]]:
        screw_hole = Part.makeCylinder(
            board["hole_diameter"] / 2 + tolerance.screw_tolerance,
            bracket_depth + 1,
            Base.Vector(sx, -0.5, bracket_height / 2 - hy),
            Base.Vector(0, 1, 0)
        )
        bracket = bracket.cut(screw_hole)

    # 벽면 고정 홀
    wall_hole_spacing_x = bracket_width * 0.7
    wall_hole_spacing_y = bracket_height * 0.7
    wall_hole_diameter = 5.0

    wall_positions = [
        (board_center_x - wall_hole_spacing_x / 2, bracket_depth / 2, bracket_height / 2 - wall_hole_spacing_y / 2),
        (board_center_x + wall_hole_spacing_x / 2, bracket_depth / 2, bracket_height / 2 - wall_hole_spacing_y / 2),
        (board_center_x, bracket_depth / 2, bracket_height / 2 + wall_hole_spacing_y / 2),
    ]

    for wx, wy, wz in wall_positions:
        wall_hole = Part.makeCylinder(
            wall_hole_diameter / 2, bracket_depth + 1,
            Base.Vector(wx, wy - bracket_depth / 2, wz),
            Base.Vector(0, 1, 0)
        )
        bracket = bracket.cut(wall_hole)

    print(f"[정보] 벽면 마운트 브래킷 생성 완료: {bracket_width:.1f}x{bracket_depth:.1f}x{bracket_height:.1f}mm")
    return bracket


# ============================================================
# DIN 레일 마운트 생성
# ============================================================

def create_din_rail_mount(board_name, tolerance=None):
    """
    DIN 레일용 마운트를 생성한다.

    매개변수:
        board_name (str): 보드 이름 (BOARD_DB 키)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: DIN 레일 마운트 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if board_name not in BOARD_DB:
        print(f"[오류] 알 수 없는 보드: {board_name}")
        return None

    board = BOARD_DB[board_name]
    print(f"[정보] {board['description']} DIN 레일 마운트 생성 중...")

    # DIN 레일 표준 치수 (TH35)
    rail_width = 35.0
    rail_thickness = 1.5

    mount_width = board["width"] + 20.0
    mount_depth = board["depth"] + 20.0
    mount_height = 20.0

    # 마운트 베이스
    mount = Part.makeBox(mount_width, mount_depth, mount_height)

    # DIN 레일 클립
    clip_width = mount_width * 0.6
    clip_depth = rail_width
    clip_height = 8.0

    clip = Part.makeBox(
        clip_width, clip_depth, clip_height,
        Base.Vector(
            (mount_width - clip_width) / 2,
            (mount_depth - clip_depth) / 2,
            mount_height - clip_height
        )
    )
    mount = mount.fuse(clip)

    # DIN 레일 슬롯
    slot_width = rail_width + tolerance.snap_fit_tolerance * 2
    slot_height = rail_thickness + tolerance.snap_fit_tolerance * 2

    din_slot = Part.makeBox(
        clip_width - 4.0, slot_width, slot_height,
        Base.Vector(
            (mount_width - clip_width + 4.0) / 2,
            (mount_depth - slot_width) / 2,
            mount_height - clip_height + 1.0
        )
    )
    mount = mount.cut(din_slot)

    # 보드 장착 홀
    hx = board["hole_spacing_x"] / 2
    hy = board["hole_spacing_y"] / 2
    board_center_x = mount_width / 2
    board_center_y = mount_depth / 2

    standoff_positions = [
        (board_center_x - hx, board_center_y - hy),
        (board_center_x + hx, board_center_y - hy),
        (board_center_x - hx, board_center_y + hy),
        (board_center_x + hx, board_center_y + hy),
    ]

    for sx, sy in standoff_positions[:board["mounting_hole_count"]]:
        screw_hole = Part.makeCylinder(
            board["hole_diameter"] / 2 + tolerance.screw_tolerance,
            mount_height + 1,
            Base.Vector(sx, sy, -0.5),
            Base.Vector(0, 0, 1)
        )
        mount = mount.cut(screw_hole)

    print(f"[정보] DIN 레일 마운트 생성 완료")
    return mount


# ============================================================
# 케이스 조립
# ============================================================

def assemble_case(board_name, mount_type="desktop", tolerance=None):
    """
    IoT 보드 케이스를 조립한다.

    매개변수:
        board_name (str): 보드 이름 (BOARD_DB 키)
        mount_type (str): 마운트 유형 ("desktop", "wall", "din")
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        dict: 생성된 부품들의 딕셔너리
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if board_name not in BOARD_DB:
        print(f"[오류] 알 수 없는 보드: {board_name}")
        return None

    board = BOARD_DB[board_name]
    print(f"\n[정보] === {board['description']} 케이스 조립 시작 (마운트: {mount_type}) ===")

    parts = {}

    # 1. 하단 케이스
    print("\n[단계 1] 하단 케이스")
    parts["bottom"] = create_bottom_case(board_name, tolerance)

    # 2. 상단 커버
    print("\n[단계 2] 상단 커버")
    parts["top"] = create_top_cover(board_name, tolerance)

    # 3. 마운트 브래킷
    if mount_type == "wall":
        print("\n[단계 3] 벽면 마운트 브래킷")
        parts["mount"] = create_wall_mount_bracket(board_name, tolerance)
    elif mount_type == "din":
        print("\n[단계 3] DIN 레일 마운트")
        parts["mount"] = create_din_rail_mount(board_name, tolerance)

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
            doc = FreeCAD.newDocument("IoT케이스")

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
# 메인 실행 함수
# ============================================================

def run():
    """
    메인 실행 함수.
    다양한 IoT 보드 케이스를 생성하여 FreeCAD 도큐먼트에 추가한다.
    """
    print("=" * 60)
    print("  IoT 보드 케이스 설계 매크로 시작")
    print("=" * 60)

    # 보드 목록 출력
    print("\n사용 가능한 IoT 보드:")
    for idx, (name, info) in enumerate(BOARD_DB.items(), 1):
        print(f"  {idx}. {name} - {info['description']} ({info['width']}x{info['depth']}mm)")

    # Arduino Uno 데스크탑 케이스
    print(f"\n{'─' * 40}")
    parts = assemble_case("Arduino Uno", "desktop")

    if parts:
        for name, shape in parts.items():
            add_to_freecad_document(shape, f"Arduino_Uno_{name}")

    # ESP32 데스크탑 케이스
    print(f"\n{'─' * 40}")
    parts2 = assemble_case("ESP32_DevKit", "desktop")

    if parts2:
        for name, shape in parts2.items():
            add_to_freecad_document(shape, f"ESP32_{name}")

    # Raspberry Pi 4B 벽면 마운트
    print(f"\n{'─' * 40}")
    parts3 = assemble_case("Raspberry_Pi_4B", "wall")

    if parts3:
        for name, shape in parts3.items():
            add_to_freecad_document(shape, f"RPi4B_{name}")

    # ESP32-S3 DIN 레일 마운트
    print(f"\n{'─' * 40}")
    parts4 = assemble_case("ESP32_S3_DevKit", "din")

    if parts4:
        for name, shape in parts4.items():
            add_to_freecad_document(shape, f"ESP32_S3_{name}")

    print(f"\n{'=' * 60}")
    print("  IoT 보드 케이스 설계 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()

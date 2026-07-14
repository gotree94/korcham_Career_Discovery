# -*- coding: utf-8 -*-
"""
IoT 보드 케이스 설계 매크로

Raspberry Pi 4, Arduino Uno, ESP32 보드별 맞춤 케이스를 자동 생성하는 FreeCAD 매크로.
보드 종류별 홀 패턴, GPIO 접근 홀, USB/전원 포트 홀, 나사산 고정 홀,
벽면 마운트 홀더, 상하 커버 분리, 통풍구 등을 포함합니다.

작성자: FreeCAD 자동 매크로 생성기
버전: 1.0
"""

# ============================================================================
# imports
# ============================================================================
import sys
import os
import math

# ============================================================================
# FreeCAD 사용 가능 여부 확인 (오프라인 시뮬레이션 지원)
# ============================================================================

FREECAD_AVAILABLE = False
try:
    import FreeCAD as _fc
    import Part as _Part
    import FreeCADGui as _Gui
    from FreeCAD import Base as _Base

    FreeCAD = _fc
    Part = _Part
    Base = _Base
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False


# ============================================================================
# 오프라인 시뮬레이션용 더미 모듈
# FreeCAD가 설치되지 않은 환경에서도 전체 로직을 검증할 수 있도록 합니다.
# ============================================================================

if not FREECAD_AVAILABLE:

    class _SimVector:
        """오프라인 시뮬레이션용 벡터 더미 클래스"""

        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x = x
            self.y = y
            self.z = z

        def __repr__(self):
            return "Vector({:.2f}, {:.2f}, {:.2f})".format(self.x, self.y, self.z)

    class _SimMatrix:
        """오프라인 시뮬레이션용 행렬 더미 클래스"""

        def __init__(self, *args):
            self.values = args

        def __repr__(self):
            return "Matrix(...)"

    class _SimShape:
        """오프라인 시뮬레이션용 형상 더미 클래스"""

        def __init__(self, shape_type="box", params=None):
            self.shape_type = shape_type
            self.params = params or {}
            self._volume = 0.0
            self._bounds = ((0, 0, 0), (0, 0, 0))
            self._calc_volume()

        def _calc_volume(self):
            """체적을 계산합니다 (시뮬레이션용)"""
            if self.shape_type == "box":
                w = self.params.get("w", 0)
                h = self.params.get("h", 0)
                d = self.params.get("d", 0)
                self._volume = w * h * d
            elif self.shape_type == "cylinder":
                r = self.params.get("r", 0)
                h = self.params.get("h", 0)
                self._volume = math.pi * r * r * h
            elif self.shape_type == "compound":
                self._volume = self.params.get("volume", 0)

        def cut(self, other):
            """형상 차감 연산 (시뮬레이션)"""
            new_vol = max(0, self._volume - other._volume)
            return _SimShape("compound", {"volume": new_vol})

        def fuse(self, other):
            """형상 합체 연산 (시뮬레이션)"""
            new_vol = self._volume + other._volume
            return _SimShape("compound", {"volume": new_vol})

        def transformGeometry(self, matrix):
            """기하 변환 (시뮬레이션) - 원본 반환"""
            return _SimShape(self.shape_type, dict(self.params))

        def exportStl(self, path):
            """STL 내보내기 시뮬레이션 (더미)"""
            pass

        def exportStep(self, path):
            """STEP 내보내기 시뮬레이션 (더미)"""
            pass

        def __repr__(self):
            return "<SimShape type={} vol={:.1f}>".format(
                self.shape_type, self._volume
            )

    class _SimPart:
        """오프라인 시뮬레이션용 Part 모듈 더미"""

        @staticmethod
        def makeBox(w, h, d, vec=None):
            """상자 형상 생성 (시뮬레이션)"""
            return _SimShape("box", {"w": w, "h": h, "d": d})

        @staticmethod
        def makeCylinder(r, h, vec=None, direction=None):
            """실린더 형상 생성 (시뮬레이션)"""
            return _SimShape("cylinder", {"r": r, "h": h})

    class _SimBase:
        """오프라인 시뮬레이션용 Base 모듈 더미"""

        @staticmethod
        def Vector(x=0.0, y=0.0, z=0.0):
            """벡터 생성 (시뮬레이션)"""
            return _SimVector(x, y, z)

        @staticmethod
        def Matrix(*args):
            """행렬 생성 (시뮬레이션)"""
            return _SimMatrix(*args)

    class _SimFreeCAD:
        """오프라인 시뮬레이션용 FreeCAD 모듈 더미"""

        ActiveDocument = None

        @staticmethod
        def newDocument(name):
            """빈 문서 생성 (시뮬레이션)"""
            return _SimDocument(name)

    class _SimDocument:
        """오프라인 시뮬레이션용 문서 더미"""

        def __init__(self, name):
            self.Name = name
            self._objects = []

        def addObject(self, type_str, name):
            """오브젝트 추가 (시뮬레이션)"""
            obj = _SimObject(name)
            self._objects.append(obj)
            return obj

        def recompute(self):
            """문서 재계산 (시뮬레이션)"""
            pass

    class _SimObject:
        """오프라인 시뮬레이션용 오브젝트 더미"""

        def __init__(self, name):
            self.Name = name
            self.Shape = None

    # 더미 모듈을 전역에 바인딩
    FreeCAD = _SimFreeCAD
    Part = _SimPart
    Base = _SimBase


# ============================================================================
# 전역 상수 - 기본 치수 (단위: mm)
# ============================================================================

# 케이스 벽 두께
WALL_THICKNESS = 2.0

# 나사 직경 (M3)
SCREW_DIAMETER = 3.2
SCREW_HEAD_DIAMETER = 6.0
SCREW_HEAD_HEIGHT = 2.0

# 기본 케이스 여유 공간
DEFAULT_CLEARANCE = 1.0

# 케이스 뚜껑 두께
LID_THICKNESS = 2.0

# 통풍구 관련
VENT_SLOT_WIDTH = 3.0
VENT_SLOT_SPACING = 5.0

# 벽면 마운트 관련
WALL_MOUNT_WIDTH = 15.0
WALL_MOUNT_HEIGHT = 30.0
WALL_MOUNT_HOLE_DIAMETER = 4.0

# ============================================================================
# 보드 정의 딕셔너리
# ============================================================================

BOARD_CONFIGS = {
    "Raspberry Pi 4": {
        "board_width": 85.0,
        "board_height": 56.0,
        "board_thickness": 1.5,
        "mounting_holes": [
            {"x": 3.5, "y": 3.5},
            {"x": 61.5, "y": 3.5},
            {"x": 3.5, "y": 52.5},
            {"x": 61.5, "y": 52.5},
        ],
        "gpio_holes": {
            "x": 73.0,
            "y": 12.0,
            "width": 8.0,
            "height": 51.0,
        },
        "usb_ports": [
            {"type": "USB-C", "x": -0.5, "y": 25.5, "width": 9.0, "height": 3.5},
            {"type": "USB-A", "x": -0.5, "y": 11.0, "width": 14.0, "height": 6.0},
            {"type": "USB-A", "x": -0.5, "y": 1.0, "width": 14.0, "height": 6.0},
        ],
        "ethernet_port": {"x": -0.5, "y": 38.0, "width": 16.0, "height": 14.0},
        "hdmi_port": {"x": 52.0, "y": -0.5, "width": 11.0, "height": 6.0},
        "sd_slot": {"x": 85.5, "y": 26.0, "width": 12.0, "height": 2.0},
        "led_positions": [
            {"x": 43.0, "y": 3.0, "diameter": 1.5},
            {"x": 48.0, "y": 3.0, "diameter": 1.5},
        ],
    },
    "Arduino Uno": {
        "board_width": 68.6,
        "board_height": 53.4,
        "board_thickness": 1.6,
        "mounting_holes": [
            {"x": 15.2, "y": 2.5},
            {"x": 66.0, "y": 7.6},
            {"x": 66.0, "y": 45.7},
            {"x": 13.9, "y": 50.8},
        ],
        "gpio_holes": {
            "x": 52.0,
            "y": 6.0,
            "width": 5.0,
            "height": 45.0,
        },
        "usb_port": {"x": -0.5, "y": 18.0, "width": 12.0, "height": 11.0},
        "power_jack": {"x": -0.5, "y": 35.0, "width": 9.0, "height": 11.0},
        "analog_pins": {
            "x": 52.0,
            "y": 1.0,
            "width": 16.0,
            "height": 5.0,
        },
        "led_positions": [
            {"x": 28.0, "y": 10.0, "diameter": 2.0},
            {"x": 32.0, "y": 10.0, "diameter": 2.0},
            {"x": 36.0, "y": 10.0, "diameter": 2.0},
        ],
    },
    "ESP32": {
        "board_width": 48.0,
        "board_height": 26.0,
        "board_thickness": 1.5,
        "mounting_holes": [
            {"x": 3.0, "y": 3.0},
            {"x": 45.0, "y": 3.0},
            {"x": 3.0, "y": 23.0},
            {"x": 45.0, "y": 23.0},
        ],
        "gpio_holes": {
            "x": 0.0,
            "y": 0.0,
            "width": 48.0,
            "height": 5.0,
        },
        "usb_port": {"x": 20.0, "y": -0.5, "width": 8.0, "height": 5.0},
        "led_positions": [
            {"x": 24.0, "y": 13.0, "diameter": 1.5},
        ],
        "antenna_area": {"x": 40.0, "y": 18.0, "width": 8.0, "height": 8.0},
    },
}


# ============================================================================
# 유틸리티 함수
# ============================================================================

def get_case_dimensions(board_name, clearance=DEFAULT_CLEARANCE):
    """
    보드 이름으로부터 케이스 내부/외부 치수를 계산합니다.

    Args:
        board_name: 보드 종류 문자열 ("Raspberry Pi 4", "Arduino Uno", "ESP32")
        clearance: 보드와 케이스 벽 사이 여유 공간 (mm)

    Returns:
        dict: inner_width, inner_height, inner_depth,
              outer_width, outer_height, outer_depth 포함
    """
    config = BOARD_CONFIGS[board_name]
    inner_width = config["board_width"] + 2 * clearance
    inner_height = config["board_height"] + 2 * clearance
    # 배선 및 부품 공간 15mm 추가
    inner_depth = config["board_thickness"] + clearance + 15.0
    return {
        "inner_width": inner_width,
        "inner_height": inner_height,
        "inner_depth": inner_depth,
        "outer_width": inner_width + 2 * WALL_THICKNESS,
        "outer_height": inner_height + 2 * WALL_THICKNESS,
        "outer_depth": inner_depth + 2 * WALL_THICKNESS,
    }


def calculate_ventilation_slots(dimensions, direction="width"):
    """
    통풍구 슬롯 위치를 계산합니다.

    주어진 방향을 따라 균일 간격으로 슬롯을 배치합니다.

    Args:
        dimensions: get_case_dimensions 반환값
        direction: 슬롯 방향 ("width" 또는 "height")

    Returns:
        list: 각 슬롯의 {"start": float, "end": float} 딕셔너리 목록
    """
    slots = []
    if direction == "width":
        total = dimensions["outer_width"]
    else:
        total = dimensions["outer_height"]

    # 슬롯 수 계산 (양 끝 10mm 여유)
    usable = total - 20.0
    num_slots = int(usable / (VENT_SLOT_WIDTH + VENT_SLOT_SPACING))
    start_offset = (total - num_slots * (VENT_SLOT_WIDTH + VENT_SLOT_SPACING) + VENT_SLOT_SPACING) / 2.0

    for i in range(num_slots):
        pos = start_offset + i * (VENT_SLOT_WIDTH + VENT_SLOT_SPACING)
        slots.append({"start": pos, "end": pos + VENT_SLOT_WIDTH})

    return slots


# ============================================================================
# 케이스 기본 형상 생성 함수
# ============================================================================

def create_base_box(dimensions):
    """
    케이스 베이스(하단부) 상자를 생성합니다.

    벽면 두께만큼 벽을 세우고 내부를 비운 형태를 만듭니다.
    바닥 벽 두께는 WALL_THICKNESS이며, 측면과 상단은 동일합니다.

    Args:
        dimensions: get_case_dimensions 반환값

    Returns:
        Part.Shape: 베이스 상자 형상
    """
    outer_w = dimensions["outer_width"]
    outer_h = dimensions["outer_height"]
    outer_d = dimensions["outer_depth"]
    inner_w = dimensions["inner_width"]
    inner_h = dimensions["inner_height"]
    inner_d = dimensions["inner_depth"]

    # 외부 상자 생성
    outer_box = Part.makeBox(outer_w, outer_h, outer_d)

    # 내부 상자 (바닥 벽 두께만큼 위로 올려서 상부를 비움)
    inner_box = Part.makeBox(
        inner_w, inner_h, inner_d + WALL_THICKNESS,
        Base.Vector(WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS)
    )

    # 외부 상자에서 내부 상자 차감하여 벽 생성
    base = outer_box.cut(inner_box)
    return base


def create_lid(dimensions):
    """
    케이스 뚜껑(상단 커버)을 생성합니다.

    두께 LID_THICKNESS의 플랫한 상자 형태입니다.
    나중에 GPIO 접근 홀 등이 뚜껑에서 차감됩니다.

    Args:
        dimensions: get_case_dimensions 반환값

    Returns:
        Part.Shape: 뚜껑 형상
    """
    outer_w = dimensions["outer_width"]
    outer_h = dimensions["outer_height"]

    lid = Part.makeBox(outer_w, outer_h, LID_THICKNESS)
    return lid


# ============================================================================
# 홀 생성 함수
# ============================================================================

def create_mounting_holes(board_name, case_depth):
    """
    보드 고정 나사 홀을 생성합니다.

    각 보드의 마운팅 홀 위치에 셀프탭 나사 홀과 카운터싱크 홀을 만듭니다.

    Args:
        board_name: 보드 종류 문자열
        case_depth: 케이스 내부 깊이

    Returns:
        list: 각 나사 홀에 대한 Part.Shape 목록
    """
    config = BOARD_CONFIGS[board_name]
    holes = []

    for hole_cfg in config["mounting_holes"]:
        # 케이스 벽 두께만큼 오프셋 적용
        x = hole_cfg["x"] + WALL_THICKNESS
        y = hole_cfg["y"] + WALL_THICKNESS

        # 나사 홀: 바닥 벽 관통 + 셀프탭 깊이 5mm
        screw_hole_depth = WALL_THICKNESS + 5.0
        hole_cyl = Part.makeCylinder(
            SCREW_DIAMETER / 2.0,
            screw_hole_depth,
            Base.Vector(x, y, 0.0),
            Base.Vector(0, 0, 1)
        )
        holes.append(hole_cyl)

        # 나사 머리 카운터싱크 홀 (뚜껑 측)
        countersink = Part.makeCylinder(
            SCREW_HEAD_DIAMETER / 2.0,
            SCREW_HEAD_HEIGHT,
            Base.Vector(x, y, case_depth + WALL_THICKNESS - SCREW_HEAD_HEIGHT),
            Base.Vector(0, 0, 1)
        )
        holes.append(countersink)

    return holes


def create_gpio_access_hole(board_name):
    """
    GPIO 핀 접근 홀을 생성합니다.

    뚜껑에 GPIO 헤더 핀에 접근할 수 있는 슬롯형 홀을 냅니다.

    Args:
        board_name: 보드 종류 문자열

    Returns:
        Part.Shape: GPIO 접근 홀 형상
    """
    config = BOARD_CONFIGS[board_name]
    gpio = config["gpio_holes"]

    gpio_slot = Part.makeBox(
        gpio["width"], gpio["height"], LID_THICKNESS + 2.0,
        Base.Vector(
            gpio["x"] + WALL_THICKNESS,
            gpio["y"] + WALL_THICKNESS,
            -1.0
        )
    )
    return gpio_slot


def create_usb_port_holes(board_name):
    """
    USB/전원 포트 홀을 생성합니다.

    케이스 측면에 USB 포트, 전원 잭, 이더넷, HDMI 등 배선 포트를 위한 홀을 냅니다.

    Args:
        board_name: 보드 종류 문자열

    Returns:
        list: 각 포트 홀에 대한 Part.Shape 목록
    """
    config = BOARD_CONFIGS[board_name]
    holes = []

    # 보드별 포트 위치 데이터 키 목록
    port_keys = [
        "usb_ports", "usb_port", "power_jack",
        "ethernet_port", "hdmi_port", "sd_slot"
    ]

    for key in port_keys:
        if key not in config:
            continue
        port_data = config[key]

        # 포트가 리스트인 경우 (복수 포트: 예 - RPi4의 USB-A 2개)
        if isinstance(port_data, list):
            for port in port_data:
                hole = _make_port_hole(port)
                holes.append(hole)
        else:
            hole = _make_port_hole(port_data)
            holes.append(hole)

    return holes


def _make_port_hole(port):
    """
    개별 포트 홀 형상을 생성합니다.

    포트의 x/y 좌표 음수 여부로 측면 방향을 판단합니다.
    x < 0: X축 측면 홀, y < 0: Y축 측면 홀, 그 외: 상단 홀

    Args:
        port: 포트 딕셔너리 (x, y, width, height 포함)

    Returns:
        Part.Shape: 포트 홀 형상
    """
    depth = WALL_THICKNESS + 2.0

    # X축 방향 측면 홀 (보드 왼쪽 벽)
    if port["x"] < 0:
        hole = Part.makeBox(
            depth,
            port["height"],
            port["width"],
            Base.Vector(-1.0, port["y"] + WALL_THICKNESS, WALL_THICKNESS + 5.0)
        )
    # Y축 방향 측면 홀 (보드 아래쪽 벽)
    elif port["y"] < 0:
        hole = Part.makeBox(
            port["width"],
            depth,
            port["height"],
            Base.Vector(port["x"] + WALL_THICKNESS, -1.0, WALL_THICKNESS + 5.0)
        )
    # 상단 홀 (위에서 아래로 관통)
    else:
        hole = Part.makeBox(
            port["width"],
            port["height"],
            depth,
            Base.Vector(
                port["x"] + WALL_THICKNESS,
                port["y"] + WALL_THICKNESS,
                -1.0
            )
        )
    return hole


def create_ventilation_openings(dimensions):
    """
    케이스 측면과 상단에 통풍구를 생성합니다.

    양쪽 측면과 앞뒤에 슬롯형 통풍구를 균일 간격으로 배치합니다.
    통풍구는 케이스 높이의 30% 지점에 위치합니다.

    Args:
        dimensions: get_case_dimensions 반환값

    Returns:
        list: 통풍구 홀 형상 목록
    """
    holes = []
    outer_w = dimensions["outer_width"]
    outer_h = dimensions["outer_height"]
    inner_d = dimensions["inner_depth"]

    # 측면 통풍구 (X방향 양쪽 벽면)
    side_slots = calculate_ventilation_slots(dimensions, "width")
    for slot in side_slots:
        # 왼쪽 측면 벽
        vent_left = Part.makeBox(
            WALL_THICKNESS + 2.0,
            VENT_SLOT_WIDTH,
            4.0,
            Base.Vector(-1.0, slot["start"] + WALL_THICKNESS, inner_d * 0.3)
        )
        holes.append(vent_left)
        # 오른쪽 측면 벽
        vent_right = Part.makeBox(
            WALL_THICKNESS + 2.0,
            VENT_SLOT_WIDTH,
            4.0,
            Base.Vector(
                outer_w - WALL_THICKNESS - 1.0,
                slot["start"] + WALL_THICKNESS,
                inner_d * 0.3
            )
        )
        holes.append(vent_right)

    # 상단 통풍구 (Y방향 앞뒤 벽면)
    top_slots = calculate_ventilation_slots(dimensions, "height")
    for slot in top_slots:
        # 앞쪽 벽
        vent_front = Part.makeBox(
            VENT_SLOT_WIDTH,
            WALL_THICKNESS + 2.0,
            4.0,
            Base.Vector(slot["start"] + WALL_THICKNESS, -1.0, inner_d * 0.3)
        )
        holes.append(vent_front)
        # 뒤쪽 벽
        vent_rear = Part.makeBox(
            VENT_SLOT_WIDTH,
            WALL_THICKNESS + 2.0,
            4.0,
            Base.Vector(
                slot["start"] + WALL_THICKNESS,
                outer_h - WALL_THICKNESS - 1.0,
                inner_d * 0.3
            )
        )
        holes.append(vent_rear)

    return holes


# ============================================================================
# 벽면 마운트 홀더 생성
# ============================================================================

def create_wall_mount(dimensions, position="rear"):
    """
    벽면 마운트 홀더를 생성합니다.

    케이스 외부에 벽 고정용 플레이트를 부착합니다.
    플레이트에는 위아래 2개의 M4 나사 홀이 있습니다.

    Args:
        dimensions: get_case_dimensions 반환값
        position: 마위트 위치 ("rear", "left", "right")

    Returns:
        Part.Shape: 벽면 마운트 홀더 형상
    """
    outer_w = dimensions["outer_width"]
    outer_h = dimensions["outer_height"]
    outer_d = dimensions["outer_depth"]

    # 마운트 플레이트 기본 형상
    mount_plate = Part.makeBox(
        WALL_MOUNT_WIDTH,
        WALL_MOUNT_HEIGHT,
        WALL_THICKNESS
    )

    # 위쪽 고정 나사 홀
    screw_hole_top = Part.makeCylinder(
        WALL_MOUNT_HOLE_DIAMETER / 2.0,
        WALL_THICKNESS + 2.0,
        Base.Vector(
            WALL_MOUNT_WIDTH / 2.0,
            WALL_MOUNT_HEIGHT * 0.25,
            -1.0
        ),
        Base.Vector(0, 0, 1)
    )

    # 아래쪽 고정 나사 홀
    screw_hole_bottom = Part.makeCylinder(
        WALL_MOUNT_HOLE_DIAMETER / 2.0,
        WALL_THICKNESS + 2.0,
        Base.Vector(
            WALL_MOUNT_WIDTH / 2.0,
            WALL_MOUNT_HEIGHT * 0.75,
            -1.0
        ),
        Base.Vector(0, 0, 1)
    )

    # 플레이트에서 나사 홀 차감
    mount = mount_plate.cut(screw_hole_top).cut(screw_hole_bottom)

    # 위치에 따라 마운트를 케이스 벽면에 배치
    if position == "rear":
        # 후면 벽면 중앙 상단에 배치
        translated = mount.transformGeometry(
            Base.Matrix(
                1, 0, 0, outer_w / 2.0 - WALL_MOUNT_WIDTH / 2.0,
                0, 1, 0, outer_h - WALL_THICKNESS,
                0, 0, 1, outer_d - WALL_THICKNESS
            )
        )
    elif position == "left":
        # 왼쪽 벽면 중앙에 배치
        translated = mount.transformGeometry(
            Base.Matrix(
                0, 1, 0, -WALL_THICKNESS,
                1, 0, 0, outer_h / 2.0 - WALL_MOUNT_WIDTH / 2.0,
                0, 0, 1, outer_d - WALL_THICKNESS
            )
        )
    else:
        # 오른쪽 벽면 중앙에 배치
        translated = mount.transformGeometry(
            Base.Matrix(
                0, 1, 0, outer_w - WALL_THICKNESS,
                1, 0, 0, outer_h / 2.0 - WALL_MOUNT_WIDTH / 2.0,
                0, 0, 1, outer_d - WALL_THICKNESS
            )
        )

    return translated


# ============================================================================
# 보드별 맞춤 케이스 생성 메인 함수
# ============================================================================

def create_raspberry_pi_4_case(clearance=DEFAULT_CLEARANCE, include_lid=True,
                                include_wall_mount=True):
    """
    Raspberry Pi 4 맞춤 케이스를 생성합니다.

    포함되는 포트/인터페이스 홀:
    - USB-C 전원 포트
    - USB-A 2개 (keyboard/mouse)
    - 이더넷 RJ45 포트
    - 미니 HDMI 포트
    - MicroSD 슬롯
    - GPIO 40핀 헤더 접근 홀

    Args:
        clearance: 보드 여유 공간 (mm)
        include_lid: 뚜껑 포함 여부
        include_wall_mount: 벽면 마운트 포함 여부

    Returns:
        dict: 베이스, 뚜껑, 마운트 등의 형상 키트
    """
    board_name = "Raspberry Pi 4"
    dimensions = get_case_dimensions(board_name, clearance)

    result = {}

    # 베이스(바닥+벽면) 생성
    base = create_base_box(dimensions)

    # 나사 고정 홀 차감
    screw_holes = create_mounting_holes(board_name, dimensions["inner_depth"])
    for hole in screw_holes:
        base = base.cut(hole)

    # USB/전원/이더넷/HDMI/SD 포트 홀 차감
    port_holes = create_usb_port_holes(board_name)
    for hole in port_holes:
        base = base.cut(hole)

    result["base"] = base

    # 뚜껑 생성
    if include_lid:
        lid = create_lid(dimensions)

        # GPIO 40핀 헤더 접근 홀 차감
        gpio_hole = create_gpio_access_hole(board_name)
        lid = lid.cut(gpio_hole)

        result["lid"] = lid

    # 벽면 마운트 홀더 (후면)
    if include_wall_mount:
        mount = create_wall_mount(dimensions, "rear")
        result["wall_mount"] = mount

    return result


def create_arduino_uno_case(clearance=DEFAULT_CLEARANCE, include_lid=True,
                             include_wall_mount=True):
    """
    Arduino Uno 맞춤 케이스를 생성합니다.

    포함되는 포트/인터페이스 홀:
    - USB-B 프로그래밍 포트
    - DC 전원 잭
    - 디지털/아날로그 핀 헤더 접근 홀

    Args:
        clearance: 보드 여유 공간 (mm)
        include_lid: 뚜껑 포함 여부
        include_wall_mount: 벽면 마운트 포함 여부

    Returns:
        dict: 베이스, 뚜껑, 마운트 등의 형상 키트
    """
    board_name = "Arduino Uno"
    dimensions = get_case_dimensions(board_name, clearance)

    result = {}

    # 베이스(바닥+벽면) 생성
    base = create_base_box(dimensions)

    # 나사 고정 홀 차감
    screw_holes = create_mounting_holes(board_name, dimensions["inner_depth"])
    for hole in screw_holes:
        base = base.cut(hole)

    # USB/전원 포트 홀 차감
    port_holes = create_usb_port_holes(board_name)
    for hole in port_holes:
        base = base.cut(hole)

    result["base"] = base

    # 뚜껑 생성
    if include_lid:
        lid = create_lid(dimensions)

        # GPIO/디지털 핀 헤더 접근 홀 차감
        gpio_hole = create_gpio_access_hole(board_name)
        lid = lid.cut(gpio_hole)

        result["lid"] = lid

    # 벽면 마운트 홀더 (왼쪽)
    if include_wall_mount:
        mount = create_wall_mount(dimensions, "left")
        result["wall_mount"] = mount

    return result


def create_esp32_case(clearance=DEFAULT_CLEARANCE, include_lid=True,
                       include_wall_mount=True):
    """
    ESP32 맞춤 케이스를 생성합니다.

    포함되는 포트/인터페이스 홀:
    - 마이크로 USB 포트
    - GPIO 핀 헤더 접근 홀
    - Wi-Fi 안테나 영역 홀 (신호 투과)

    Args:
        clearance: 보드 여유 공간 (mm)
        include_lid: 뚜껑 포함 여부
        include_wall_mount: 벽면 마운트 포함 여부

    Returns:
        dict: 베이스, 뚜껑, 마운트 등의 형상 키트
    """
    board_name = "ESP32"
    dimensions = get_case_dimensions(board_name, clearance)

    result = {}

    # 베이스(바닥+벽면) 생성
    base = create_base_box(dimensions)

    # 나사 고정 홀 차감
    screw_holes = create_mounting_holes(board_name, dimensions["inner_depth"])
    for hole in screw_holes:
        base = base.cut(hole)

    # USB 포트 홀 차감
    port_holes = create_usb_port_holes(board_name)
    for hole in port_holes:
        base = base.cut(hole)

    result["base"] = base

    # 뚜껑 생성
    if include_lid:
        lid = create_lid(dimensions)

        # GPIO 핀 헤더 접근 홀 차감
        gpio_hole = create_gpio_access_hole(board_name)
        lid = lid.cut(gpio_hole)

        # Wi-Fi 안테나 영역 홀 (뚜껑에서 제거하여 신호 투과 확보)
        config = BOARD_CONFIGS[board_name]
        if "antenna_area" in config:
            ant = config["antenna_area"]
            antenna_hole = Part.makeBox(
                ant["width"], ant["height"], LID_THICKNESS + 2.0,
                Base.Vector(
                    ant["x"] + WALL_THICKNESS,
                    ant["y"] + WALL_THICKNESS,
                    -1.0
                )
            )
            lid = lid.cut(antenna_hole)

        result["lid"] = lid

    # 벽면 마운트 홀더 (오른쪽)
    if include_wall_mount:
        mount = create_wall_mount(dimensions, "right")
        result["wall_mount"] = mount

    return result


# ============================================================================
# 통풍구가 포함된 전체 케이스 조립
# ============================================================================

def assemble_case_with_vents(board_name, clearance=DEFAULT_CLEARANCE):
    """
    통풍구가 포함된 전체 케이스를 조립합니다.

    지정된 보드 종류에 따라 적절한 맞춤 케이스를 생성하고,
    베이스와 뚜껑 모두에 통풍구 홀을 적용합니다.

    Args:
        board_name: 보드 종류 문자열
        clearance: 보드 여유 공간 (mm)

    Returns:
        dict: 조립된 케이스 형상 키트 (base, lid, wall_mount 포함)
    """
    dimensions = get_case_dimensions(board_name, clearance)

    # 보드별 맞춤 케이스 생성
    if board_name == "Raspberry Pi 4":
        kit = create_raspberry_pi_4_case(clearance)
    elif board_name == "Arduino Uno":
        kit = create_arduino_uno_case(clearance)
    elif board_name == "ESP32":
        kit = create_esp32_case(clearance)
    else:
        print("[오류] 지원하지 않는 보드 종류: {}".format(board_name))
        return {}

    # 통풍구 홀 생성 및 베이스/뚜껑에 적용
    vent_holes = create_ventilation_openings(dimensions)
    for vent in vent_holes:
        kit["base"] = kit["base"].cut(vent)
        if "lid" in kit:
            kit["lid"] = kit["lid"].cut(vent)

    return kit


# ============================================================================
# STL / STEP 내보내기 함수
# ============================================================================

def export_shape_to_stl(shape, file_path):
    """
    형상을 STL 파일로 내보냅니다.

    FreeCAD 환경이면 실제 STL 파일을 저장하고,
    오프라인이면 시뮬레이션 로그를 출력합니다.

    Args:
        shape: FreeCAD Part.Shape 객체
        file_path: 저장할 STL 파일 경로

    Returns:
        bool: 내보내기 성공 여부
    """
    if not FREECAD_AVAILABLE:
        print("[시뮬레이션] STL 내보내기: {}".format(file_path))
        return True

    try:
        shape.exportStl(file_path)
        print("[성공] STL 파일 저장 완료: {}".format(file_path))
        return True
    except Exception as e:
        print("[오류] STL 내보내기 실패: {}".format(str(e)))
        return False


def export_shape_to_step(shape, file_path):
    """
    형상을 STEP 파일로 내보냅니다.

    FreeCAD 환경이면 실제 STEP 파일을 저장하고,
    오프라인이면 시뮬레이션 로그를 출력합니다.

    Args:
        shape: FreeCAD Part.Shape 객체
        file_path: 저장할 STEP 파일 경로

    Returns:
        bool: 내보내기 성공 여부
    """
    if not FREECAD_AVAILABLE:
        print("[시뮬레이션] STEP 내보내기: {}".format(file_path))
        return True

    try:
        shape.exportStep(file_path)
        print("[성공] STEP 파일 저장 완료: {}".format(file_path))
        return True
    except Exception as e:
        print("[오류] STEP 내보내기 실패: {}".format(str(e)))
        return False


def export_all_components(kit, output_dir, prefix="iot_case"):
    """
    모든 케이스 부품을 STL과 STEP으로 내보냅니다.

    Args:
        kit: assemble_case_with_vents 반환 딕셔너리
        output_dir: 출력 디렉토리 경로
        prefix: 파일 이름 접두사

    Returns:
        dict: 각 부품별 내보내기 성공/실패 결과
    """
    results = {}

    # FreeCAD 환경에서 실제 파일 저장 시 디렉토리 생성
    if FREECAD_AVAILABLE and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for name, shape in kit.items():
        stl_path = os.path.join(output_dir, "{}_{}.stl".format(prefix, name))
        step_path = os.path.join(output_dir, "{}_{}.step".format(prefix, name))
        results[name] = {
            "stl": export_shape_to_stl(shape, stl_path),
            "step": export_shape_to_step(shape, step_path),
        }

    if FREECAD_AVAILABLE:
        print("[완료] 전체 부품 내보내기 완료: {}".format(output_dir))

    return results


# ============================================================================
# FreeCAD GUI 통합 (FreeCAD Gui 환경에서 실행 시)
# ============================================================================

def add_to_document(doc, kit, case_name="IoTBoardCase"):
    """
    생성된 케이스 형상을 FreeCAD 활성 문서에 추가합니다.

    각 부품을 Part::Feature 오브젝트로 추가하여 3D 뷰어에 표시합니다.

    Args:
        doc: FreeCAD Document 객체
        kit: 케이스 형상 키트 (base, lid, wall_mount 등)
        case_name: 오브젝트 이름 접두사

    Returns:
        list: 생성된 FreeCAD 오브젝트 목록
    """
    objects = []

    for name, shape in kit.items():
        obj_name = "{}_{}".format(case_name, name)
        obj = doc.addObject("Part::Feature", obj_name)
        obj.Shape = shape
        objects.append(obj)

    return objects


# ============================================================================
# 메인 실행 함수
# ============================================================================

def main():
    """
    메인 실행 함수.

    세 가지 보드 타입별로 케이스를 생성하고 STL/STEP으로 내보냅니다.
    FreeCAD 환경에서는 3D 뷰어에 케이스를 표시하고,
    오프라인 환경에서는 시뮬레이션 모드로 동작하여 치수 정보를 출력합니다.
    """
    print("=" * 60)
    print("  IoT 보드 케이스 자동 생성 매크로")
    print("  지원 보드: Raspberry Pi 4, Arduino Uno, ESP32")
    print("=" * 60)

    output_dir = os.path.join(os.path.expanduser("~"), "Desktop", "iot_board_cases")

    # 생성할 보드 목록
    board_list = ["Raspberry Pi 4", "Arduino Uno", "ESP32"]

    for board_name in board_list:
        print("\n--- {} 케이스 생성 중 ---".format(board_name))

        # 케이스 치수 계산 및 출력
        dimensions = get_case_dimensions(board_name)
        print("  외부 치수: {:.1f} x {:.1f} x {:.1f} mm".format(
            dimensions["outer_width"],
            dimensions["outer_height"],
            dimensions["outer_depth"]
        ))
        print("  내부 치수: {:.1f} x {:.1f} x {:.1f} mm".format(
            dimensions["inner_width"],
            dimensions["inner_height"],
            dimensions["inner_depth"]
        ))

        # 케이스 조립 (통풍구 포함)
        kit = assemble_case_with_vents(board_name)

        if not kit:
            print("  [경고] {} 케이스 생성 실패".format(board_name))
            continue

        print("  생성된 부품: {}".format(", ".join(kit.keys())))

        # STL/STEP 내보내기
        prefix = board_name.replace(" ", "_").lower()
        export_all_components(kit, output_dir, prefix)

    # FreeCAD GUI 환경에서 문서에 오브젝트 추가
    if FREECAD_AVAILABLE:
        try:
            doc = FreeCAD.ActiveDocument
            if doc is None:
                doc = FreeCAD.newDocument("IoTBoardCases")

            for board_name in board_list:
                kit = assemble_case_with_vents(board_name)
                case_name = board_name.replace(" ", "_")
                add_to_document(doc, kit, case_name)

            doc.recompute()
            print("\n[FreeCAD] 모든 케이스가 문서에 추가되었습니다.")
        except Exception as e:
            print("\n[FreeCAD 오류] 문서 추가 실패: {}".format(str(e)))
    else:
        # 오프라인 시뮬레이션 모드 - 상세 정보 출력
        print("\n[시뮬레이션 모드] FreeCAD 없이 실행 중입니다.")
        print("[시뮬레이션] 생성된 케이스 정보 요약:")
        for board_name in board_list:
            dims = get_case_dimensions(board_name)
            config = BOARD_CONFIGS[board_name]
            print("  {}:".format(board_name))
            print("    보드 크기: {:.1f} x {:.1f} mm".format(
                config["board_width"], config["board_height"]
            ))
            print("    케이스 크기: {:.1f} x {:.1f} x {:.1f} mm".format(
                dims["outer_width"], dims["outer_height"], dims["outer_depth"]
            ))
            print("    고정 홀 수: {}".format(len(config["mounting_holes"])))
            vent_w = calculate_ventilation_slots(dims, "width")
            vent_h = calculate_ventilation_slots(dims, "height")
            print("    통풍구 수: {} (측면) + {} (상단)".format(
                len(vent_w) * 2, len(vent_h) * 2
            ))

    print("\n" + "=" * 60)
    print("  IoT 보드 케이스 생성 완료")
    print("=" * 60)


# ============================================================================
# FreeCAD 매크로 자동 실행 엔트리포인트
# ============================================================================

if __name__ == "__main__":
    main()
else:
    # FreeCAD 스크립트 메뉴에서 직접 실행된 경우
    main()

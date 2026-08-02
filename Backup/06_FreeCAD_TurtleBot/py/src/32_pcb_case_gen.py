# -*- coding: utf-8 -*-
"""
Part 7 - 32: PCB 케이스 생성기 매크로

PCB 치수를 입력받아 맞춤형 인클로저를 자동으로 생성하는 FreeCAD 매크로.
상하 커버 분리, 나사산 홀, 버튼/LED 홀, 환기구, 스내핑 잠금 기능 포함.

사용법: FreeCAD에서 실행하여 PCB 치수를 입력하면 케이스가 자동 생성됨.
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
# PCB 케이스 기본 프리셋
# ============================================================

PCB_PRESETS = {
    "아두이노_유니코": {
        "width": 68.6,
        "depth": 53.4,
        "description": "Arduino Uno PCB 크기",
    },
    "아두이노_나노": {
        "width": 43.2,
        "depth": 18.7,
        "description": "Arduino Nano PCB 크기",
    },
    "라즈베리파이_4B": {
        "width": 85.6,
        "depth": 56.5,
        "description": "Raspberry Pi 4B PCB 크기",
    },
    "ESP32_개발보드": {
        "width": 28.0,
        "depth": 48.0,
        "description": "ESP32 개발 보드 PCB 크기",
    },
    "ESP32_S3": {
        "width": 25.5,
        "depth": 39.5,
        "description": "ESP32-S3 개발 보드 크기",
    },
    "Raspberry_Pi_Pico": {
        "width": 51.0,
        "depth": 21.0,
        "description": "Raspberry Pi Pico 크기",
    },
    "STM32_Nucleo": {
        "width": 70.0,
        "depth": 65.0,
        "description": "STM32 Nucleo 보드 크기",
    },
    "custom": {
        "width": 100.0,
        "depth": 80.0,
        "description": "사용자 정의 PCB 크기",
    },
}


# ============================================================
# PCB 케이스 파라미터
# ============================================================

class CaseParams:
    """PCB 케이스의 파라미터를 관리하는 클래스"""

    def __init__(self):
        """기본 파라미터 초기화"""
        # 벽면/바닥 설정
        self.wall_thickness = 2.0            # 벽면 두께 (mm)
        self.floor_thickness = 2.0            # 바닥 두께 (mm)
        self.top_thickness = 2.0            # 상단 커버 두께 (mm)

        # PCB 관련
        self.pcb_clearance = 1.0             # PCB 주변 여유 공간 (mm)
        self.stand_height = 5.0          # PCB 지지 스탠드 높이 (mm)
        self.stand_outer_diameter = 6.0          # PCB 지지 스탠드 외경 (mm)

        # 나사산 홀 설정
        self.screw_hole_diameter = 3.2          # 나사 홀 지름 (mm, M3)
        self.stand_hole_diameter = 2.5        # 스탠드 홀 지름 (mm)
        self.stand_outer_dia = 6.0          # 스탠드 외경 (mm)

        # 마진
        self.assembly_margin = 0.3            # 조립 마진 (mm)

        # 스내핑
        self.snap_pin_height = 3.0        # 스내핑 핀 높이 (mm)
        self.snap_pin_diameter = 1.5        # 스내핑 핀 지름 (mm)
        self.snap_groove_depth = 0.8        # 스내핑 홈 깊이 (mm)


# ============================================================
# 하단 케이스 생성
# ============================================================

def create_bottom_case(pcb_width, pcb_depth, params=None):
    """
    PCB 케이스 하단 커버(베이스)를 생성한다.

    매개변수:
        pcb_width (float): PCB 가로 길이 (mm)
        pcb_depth (float): PCB 세로 길이 (mm)
        params (CaseParams): 케이스 파라미터

    반환값:
        Part.Shape: 하단 케이스 형태
    """
    if params is None:
        params = CaseParams()

    # 외부 치수 계산
    outer_width = pcb_width + params.wall_thickness * 2 + params.pcb_clearance * 2
    outer_depth = pcb_depth + params.wall_thickness * 2 + params.pcb_clearance * 2
    bottom_height = params.floor_thickness + params.stand_height

    print(f"[정보] PCB 치수: {pcb_width}x{pcb_depth}mm")
    print(f"[정보] 하단 케이스 외부 치수: {outer_width:.1f}x{outer_depth:.1f}x{bottom_height:.1f}mm")

    # 외부 박스 생성
    bottom = Part.makeBox(outer_width, outer_depth, bottom_height)

    # 내부 캐비티 제거
    inner_width = outer_width - params.wall_thickness * 2
    inner_depth = outer_depth - params.wall_thickness * 2
    inner_height = bottom_height - params.floor_thickness

    cavity = Part.makeBox(
        inner_width, inner_depth, inner_height,
        Base.Vector(params.wall_thickness, params.wall_thickness, params.floor_thickness)
    )
    bottom = bottom.cut(cavity)

    # PCB 지지 스탠드 생성
    bottom = _create_pcb_support_stands(bottom, pcb_width, pcb_depth, params, outer_width, outer_depth)

    # 나사산 홀 생성
    bottom = _create_screw_holes(bottom, pcb_width, pcb_depth, params, outer_width, outer_depth, bottom_height)

    # 스내핑 홈 추가
    bottom = _create_snap_grooves(bottom, outer_width, outer_depth, bottom_height, params)

    print("[정보] 하단 케이스 생성 완료")
    return bottom


def _create_pcb_support_stands(bottom, pcb_width, pcb_depth, params, outer_width, outer_depth):
    """
    PCB를 지지하는 4개의 스탠드를 생성한다.

    매개변수:
        bottom (Part.Shape): 하단 케이스
        pcb_width, pcb_depth (float): PCB 치수 (mm)
        params (CaseParams): 케이스 파라미터
        outer_width, outer_depth (float): 하단 외부 치수 (mm)

    반환값:
        Part.Shape: 스탠드가 추가된 하단 케이스
    """
    stand_positions = [
        Base.Vector(
            params.wall_thickness + params.pcb_clearance + params.stand_outer_dia / 2,
            params.wall_thickness + params.pcb_clearance + params.stand_outer_dia / 2,
            params.floor_thickness
        ),
        Base.Vector(
            outer_width - params.wall_thickness - params.pcb_clearance - params.stand_outer_dia / 2,
            params.wall_thickness + params.pcb_clearance + params.stand_outer_dia / 2,
            params.floor_thickness
        ),
        Base.Vector(
            params.wall_thickness + params.pcb_clearance + params.stand_outer_dia / 2,
            outer_depth - params.wall_thickness - params.pcb_clearance - params.stand_outer_dia / 2,
            params.floor_thickness
        ),
        Base.Vector(
            outer_width - params.wall_thickness - params.pcb_clearance - params.stand_outer_dia / 2,
            outer_depth - params.wall_thickness - params.pcb_clearance - params.stand_outer_dia / 2,
            params.floor_thickness
        ),
    ]

    for pos in stand_positions:
        # 스탠드 실린더 추가
        stand = Part.makeCylinder(
            params.stand_outer_dia / 2,
            params.stand_height,
            Base.Vector(pos.x, pos.y, pos.z),
            Base.Vector(0, 0, 1)
        )
        bottom = bottom.fuse(stand)

        # 나사 홀
        screw_hole = Part.makeCylinder(
            params.stand_hole_diameter / 2,
            params.stand_height + 0.5,
            Base.Vector(pos.x, pos.y, pos.z - 0.25),
            Base.Vector(0, 0, 1)
        )
        bottom = bottom.cut(screw_hole)

    print(f"[정보] PCB 지지 스탠드 4개 생성 완료")
    return bottom


def _create_screw_holes(case, pcb_width, pcb_depth, params, outer_width, outer_depth, height):
    """
    상하 커버를 결합하기 위한 나사산 홀을 생성한다.

    매개변수:
        case (Part.Shape): 케이스 형태
        pcb_width, pcb_depth (float): PCB 치수 (mm)
        params (CaseParams): 케이스 파라미터
        outer_width, outer_depth (float): 케이스 외부 치수 (mm)
        height (float): 케이스 높이 (mm)

    반환값:
        Part.Shape: 나사산 홀이 추가된 케이스
    """
    # 4 모서리에 나사 홀
    screw_hole_positions = [
        Base.Vector(params.wall_thickness * 2, params.wall_thickness * 2, 0),
        Base.Vector(outer_width - params.wall_thickness * 2, params.wall_thickness * 2, 0),
        Base.Vector(params.wall_thickness * 2, outer_depth - params.wall_thickness * 2, 0),
        Base.Vector(outer_width - params.wall_thickness * 2, outer_depth - params.wall_thickness * 2, 0),
    ]

    for pos in screw_hole_positions:
        hole = Part.makeCylinder(
            params.screw_hole_diameter / 2,
            height,
            Base.Vector(pos.x, pos.y, 0),
            Base.Vector(0, 0, 1)
        )
        case = case.cut(hole)

    print(f"[정보] 나사산 홀 4개 생성 완료")
    return case


def _create_snap_grooves(case, outer_width, outer_depth, height, params):
    """
    스내핑 잠금을 위한 홈을 케이스 측면에 추가한다.

    매개변수:
        case (Part.Shape): 케이스 형태
        outer_width, outer_depth (float): 케이스 외부 치수 (mm)
        height (float): 케이스 높이 (mm)
        params (CaseParams): 케이스 파라미터

    반환값:
        Part.Shape: 스내핑 홈이 추가된 케이스
    """
    groove_depth = params.snap_groove_depth
    groove_height = 1.0
    groove_z = height - groove_height - 0.5

    # 앞면에 2개의 스내핑 홈
    groove1_x = outer_width * 0.25
    groove2_x = outer_width * 0.75

    for groove_x in [groove1_x, groove2_x]:
        groove = Part.makeBox(
            3.0, groove_depth, groove_height,
            Base.Vector(groove_x - 1.5, -0.01, groove_z)
        )
        case = case.cut(groove)

    # 후면에 2개의 스내핑 홈
    for groove_x in [groove1_x, groove2_x]:
        groove = Part.makeBox(
            3.0, groove_depth, groove_height,
            Base.Vector(groove_x - 1.5, outer_depth - groove_depth + 0.01, groove_z)
        )
        case = case.cut(groove)

    print("[정보] 스내핑 홈 4개 생성 완료")
    return case


# ============================================================
# 상단 커버 생성
# ============================================================

def create_top_cover(pcb_width, pcb_depth, params=None):
    """
    PCB 케이스 상단 커버를 생성한다.

    매개변수:
        pcb_width (float): PCB 가로 길이 (mm)
        pcb_depth (float): PCB 세로 길이 (mm)
        params (CaseParams): 케이스 파라미터

    반환값:
        Part.Shape: 상단 커버 형태
    """
    if params is None:
        params = CaseParams()

    outer_width = pcb_width + params.wall_thickness * 2 + params.pcb_clearance * 2
    outer_depth = pcb_depth + params.wall_thickness * 2 + params.pcb_clearance * 2
    cover_height = params.top_thickness

    # 커버 본체
    cover = Part.makeBox(outer_width, outer_depth, cover_height)

    # 내부 리브 구조 (강도 향상)
    rib_thickness = 1.0
    rib_height = 3.0

    # 가로 리브
    rib1 = Part.makeBox(
        outer_width - params.wall_thickness * 4, rib_thickness, rib_height,
        Base.Vector(params.wall_thickness * 2, outer_depth / 2 - rib_thickness / 2, cover_height)
    )
    cover = cover.fuse(rib1)

    # 세로 리브
    rib2 = Part.makeBox(
        rib_thickness, outer_depth - params.wall_thickness * 4, rib_height,
        Base.Vector(outer_width / 2 - rib_thickness / 2, params.wall_thickness * 2, cover_height)
    )
    cover = cover.fuse(rib2)

    # 스내핑 핀 (하단 케이스 홈과 맞물리는 핀)
    snap_pin_positions = [
        Base.Vector(outer_width * 0.25, 0, 0),
        Base.Vector(outer_width * 0.75, 0, 0),
        Base.Vector(outer_width * 0.25, outer_depth, 0),
        Base.Vector(outer_width * 0.75, outer_depth, 0),
    ]

    for pos in snap_pin_positions:
        pin = Part.makeBox(
            3.0, params.wall_thickness, params.snap_pin_height,
            Base.Vector(pos.x - 1.5, pos.y - params.wall_thickness if pos.y == 0 else 0,
                       cover_height - params.snap_pin_height)
        )
        cover = cover.fuse(pin)

    print("[정보] 상단 커버 생성 완료")
    return cover


# ============================================================
# 버튼/LED 홀 기능
# ============================================================

def add_button_led_holes(shape, hole_list, params=None):
    """
    버튼과 LED를 위한 홀을 형태에 추가한다.

    매개변수:
        shape (Part.Shape): 홀을 추가할 형태
        hole_list (list): 홀 정보 목록
            각 항목: {"position": Base.Vector, "diameter": float, "type": str}
        params (CaseParams): 케이스 파라미터

    반환값:
        Part.Shape: 홀이 추가된 형태
    """
    if params is None:
        params = CaseParams()

    for hole_info in hole_list:
        position = hole_info["position"]
        diameter = hole_info.get("diameter", 3.0)
        hole_type = hole_info.get("type", "버튼")
        depth = hole_info.get("depth", params.wall_thickness + 1)

        hole = Part.makeCylinder(
            diameter / 2, depth,
            Base.Vector(position.x, position.y, position.z),
            Base.Vector(0, 1, 0)  # 앞면 방향
        )
        shape = shape.cut(hole)
        print(f"[정보] {hole_type} 홀 추가 (지름={diameter}mm)")

    return shape


# ============================================================
# 환기구 생성
# ============================================================

def add_ventilation_holes(shape, params=None):
    """
    케이스 바닥면에 환기구(통기 구멍)를 추가한다.

    매개변수:
        shape (Part.Shape): 환기구를 추가할 형태
        params (CaseParams): 케이스 파라미터

    반환값:
        Part.Shape: 환기구가 추가된 형태
    """
    if params is None:
        params = CaseParams()

    # 환기구 설정
    hole_diameter = 2.0           # 각 환기구 홀 지름 (mm)
    hole_spacing = 5.0           # 홀 간격 (mm)
    hole_region_width = 30.0         # 환기구 영역 가로 (mm)
    hole_region_depth = 20.0         # 환기구 영역 세로 (mm)
    start_x = 10.0           # 환기구 시작 x 위치
    start_y = 10.0           # 환기구 시작 y 위치

    hole_count = 0
    x = start_x
    while x < start_x + hole_region_width:
        y = start_y
        while y < start_y + hole_region_depth:
            hole = Part.makeCylinder(
                hole_diameter / 2, params.floor_thickness + 0.5,
                Base.Vector(x, y, -0.25),
                Base.Vector(0, 0, 1)
            )
            shape = shape.cut(hole)
            hole_count += 1
            y += hole_spacing
        x += hole_spacing

    print(f"[정보] 환기구 {hole_count}개 추가 완료")
    return shape


# ============================================================
# 나사 홀 상세 생성
# ============================================================

def create_detailed_screw_hole(shape, position, direction, params=None):
    """
    상세 나사 홀을 생성한다. 나사산과 팔아헤드가 있는 홀.

    매개변수:
        shape (Part.Shape): 형태
        position (Base.Vector): 홀 위치
        direction (Base.Vector): 홀 방향
        params (CaseParams): 케이스 파라미터

    반환값:
        Part.Shape: 나사 홀이 추가된 형태
    """
    if params is None:
        params = CaseParams()

    screw_diameter = 3.0          # M3 나사
    head_diameter = 5.5      # 팔아헤드 지름
    head_depth = 2.0      # 팔아헤드 깊이

    # 나사 홀
    screw_hole = Part.makeCylinder(
        screw_diameter / 2, 100,
        Base.Vector(position.x, position.y, position.z),
        Base.Vector(direction.x, direction.y, direction.z)
    )
    shape = shape.cut(screw_hole)

    # 팔아헤드 홀 (상단)
    head_hole = Part.makeCylinder(
        head_diameter / 2, head_depth,
        Base.Vector(position.x, position.y, position.z),
        Base.Vector(direction.x, direction.y, direction.z)
    )
    shape = shape.cut(head_hole)

    return shape


# ============================================================
# 조립 시각화
# ============================================================

def create_assembly_visualization(bottom, top, offset_z=50):
    """
    상단 커버를 위로 올려서 조립 상태를 시각화한다.

    매개변수:
        bottom (Part.Shape): 하단 케이스
        top (Part.Shape): 상단 커버
        offset_z (float): 상단 커버 z 방향 오프셋 (mm)

    반환값:
        list: [하단형태, 상단형태]
    """
    # 상단 커버를 z 방향으로 이동
    transform_matrix = Base.Matrix()
    transform_matrix.move(Base.Vector(0, 0, offset_z))
    top_moved = top.copy()
    top_moved = top_moved.transformGeometry(transform_matrix)

    print(f"[정보] 조립 시각화 생성 (상단 z={offset_z}mm)")
    return [bottom, top_moved]


# ============================================================
# FreeCAD 통합 함수
# ============================================================

def add_to_freecad_document(shape, name):
    """
    형태를 FreeCAD 활성 도큐먼트에 추가한다.

    매개변수:
        shape (Part.Shape): 추가할 형태
        name (str): 객체 이름

    반환값:
        Part.Feature: 추가된 FreeCAD 객체
    """
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("PCB케이스")

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()
        print(f"[정보] 도큐먼트에 '{name}' 추가 완료")
        return obj
    except Exception as e:
        print(f"[오류] 도큐먼트 추가 실패: {e}")
        return None


# ============================================================
# 메인 실행 함수
# ============================================================

def run():
    """
    메인 실행 함수.
    다양한 PCB 크기의 케이스를 생성한다.
    """
    print("=" * 60)
    print("  PCB 케이스 생성기 매크로 시작")
    print("=" * 60)

    # 프리셋 목록 출력
    print("\n사용 가능한 PCB 프리셋:")
    for idx, (name, info) in enumerate(PCB_PRESETS.items(), 1):
        print(f"  {idx}. {name} ({info['width']}x{info['depth']}mm) - {info['description']}")

    # 기본 파라미터
    params = CaseParams()

    # 테스트할 PCB 목록
    test_boards = ["아두이노_유니코", "라즈베리파이_4B", "ESP32_개발보드"]

    for board_name in test_boards:
        print(f"\n{'─' * 40}")
        print(f"[시작] {board_name} 케이스 생성")

        board = PCB_PRESETS[board_name]
        pcb_width = board["width"]
        pcb_depth = board["depth"]

        # 하단 케이스
        bottom = create_bottom_case(pcb_width, pcb_depth, params)
        add_to_freecad_document(bottom, f"{board_name}_하단")

        # 상단 커버
        top = create_top_cover(pcb_width, pcb_depth, params)
        add_to_freecad_document(top, f"{board_name}_상단")

        # 환기구를 하단에 추가
        bottom_with_vent = add_ventilation_holes(bottom, params)
        add_to_freecad_document(bottom_with_vent, f"{board_name}_하단_환기구")

        # 조립 시각화
        assembly_shapes = create_assembly_visualization(bottom, top)
        for idx, s in enumerate(assembly_shapes):
            add_to_freecad_document(s, f"{board_name}_조립_{idx}")

    print(f"\n{'=' * 60}")
    print("  PCB 케이스 생성 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()

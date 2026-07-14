# -*- coding: utf-8 -*-
"""
Part 7 - 31: 센서 하우징 자동 설계 매크로

센서 종류에 맞는 맞춤형 하우징을 자동으로 생성하는 FreeCAD 매크로.
온도, 초음파, 적외선 등 다양한 센서 템플릿을 지원하며,
PCB 홀 패턴, 케이블 홀, 벽면 두께 최적화 기능을 포함.

사용법: FreeCAD에서 실행하여 센서 종류와 치수를 입력하면 하우징이 자동 생성됨.
"""

import sys
import math

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    print("FreeCAD 내에서 스크립트를 실행하세요.")
    sys.exit(1)


# ============================================================
# 센서 종류별 기본 템플릿 정의
# ============================================================

# 센서 템플릿: (가로mm, 세로mm, 높이mm, 피치mm, 홀수, 핀수)
SENSOR_TEMPLATES = {
    "DHT11_temperature": {
        "width": 15.5,
        "depth": 12.0,
        "height": 11.5,
        "description": "DHT11 온도/습도 센서",
        "pin_count": 4,
        "pin_pitch": 2.54,
        "series": "DHT11",
    },
    "DHT22_temperature": {
        "width": 15.0,
        "depth": 25.5,
        "height": 7.7,
        "description": "DHT22/AM2302 정밀 온도/습도 센서",
        "pin_count": 4,
        "pin_pitch": 2.54,
        "series": "DHT22",
    },
    "HC_SR04_ultrasonic": {
        "width": 45.0,
        "depth": 20.0,
        "height": 15.0,
        "description": "HC-SR04 초음파 거리 센서",
        "pin_count": 4,
        "pin_pitch": 2.54,
        "transducer_diameter": 16.0,
        "series": "HC-SR04",
    },
    "GP2Y0A21_infrared": {
        "width": 18.0,
        "depth": 13.5,
        "height": 10.5,
        "description": "SHARP GP2Y0A21 적외선 거리 센서",
        "pin_count": 3,
        "pin_pitch": 2.54,
        "series": "GP2Y",
    },
    "PIR_motion": {
        "width": 32.0,
        "depth": 24.0,
        "height": 25.0,
        "description": "HC-SR501 PIR 모션 감지 센서",
        "pin_count": 3,
        "pin_pitch": 2.54,
        "lens_diameter": 23.0,
        "series": "PIR",
    },
    "BMP280_barometer": {
        "width": 13.0,
        "depth": 11.0,
        "height": 2.5,
        "description": "BMP280 기압/온도 센서",
        "pin_count": 6,
        "pin_pitch": 2.54,
        "series": "BMP280",
    },
    "custom": {
        "width": 30.0,
        "depth": 20.0,
        "height": 10.0,
        "description": "사용자 정의 센서 하우징",
        "pin_count": 4,
        "pin_pitch": 2.54,
        "series": "CUSTOM",
    },
}


# ============================================================
# 하우징 파라미터 기본값
# ============================================================

class HousingParams:
    """센서 하우징의 파라미터를 관리하는 클래스"""

    def __init__(self):
        """기본 파라미터 초기화"""
        # 기본 하우징 치수
        self.wall_thickness = 2.0           # 벽면 두께 (mm)
        self.floor_thickness = 2.0           # 바닥 두께 (mm)
        self.top_clearance = 3.0           # 상단 공간 여유 (mm)
        self.cable_hole_diameter = 4.0       # 케이블 통과 홀 지름 (mm)
        self.screw_hole_diameter = 2.5         # 나사산 홀 지름 (mm, M3 기준)
        self.screw_hole_depth = 5.0         # 나사산 홀 깊이 (mm)
        self.mount_clearance = 2.0         # 마운트 홀 여유 (mm)
        self.cable_clearance = 5.0         # 케이블 배선 여유 공간 (mm)
        self.margin = 0.5               # 조립 마진 (mm)
        self.edge_radius = 1.0         # 모서리 둥글게 처리 (mm)
        self.snap_on_pin_enabled = False      # 스내핑 핀 사용 여부


def create_sensor_housing(sensor_type, params=None):
    """
    센서 종류에 맞는 하우징을 자동 생성한다.

    매개변수:
        sensor_type (str): 센서 템플릿 키 (SENSOR_TEMPLATES의 키)
        params (HousingParams): 하우징 파라미터 객체

    반환값:
        Part.Shape: 생성된 하우징 형태
    """
    if params is None:
        params = HousingParams()

    if sensor_type not in SENSOR_TEMPLATES:
        print(f"[오류] 알 수 없는 센서 종류: {sensor_type}")
        print(f"가능한 종류: {list(SENSOR_TEMPLATES.keys())}")
        return None

    template = SENSOR_TEMPLATES[sensor_type]
    print(f"[정보] {template['description']} 하우징 생성 중...")

    # 하우징 외부 치수 계산
    outer_width = template["width"] + params.wall_thickness * 2 + params.margin * 2
    outer_depth = template["depth"] + params.wall_thickness * 2 + params.margin * 2
    outer_height = template["height"] + params.floor_thickness + params.top_clearance

    print(f"[정보] 센서 치수: {template['width']}x{template['depth']}x{template['height']}mm")
    print(f"[정보] 하우징 외부 치수: {outer_width:.1f}x{outer_depth:.1f}x{outer_height:.1f}mm")
    print(f"[정보] 벽면 두께: {params.wall_thickness}mm")

    # 하우징 본체 생성
    housing = _create_housing_body(outer_width, outer_depth, outer_height, params)

    # 센서 수용 공간 (내부 캐비티)
    housing = _create_sensor_cavity(housing, template, params, outer_height)

    # PCB 마운트 홀 패턴 생성
    housing = _create_pcb_hole_pattern(housing, template, params)

    # 케이블 홀 추가
    housing = _add_cable_holes(housing, params, outer_width, outer_depth)

    # 센서 종류별 특수 기능
    housing = _add_sensor_specific_features(housing, template, params, outer_width, outer_depth)

    print(f"[정보] 하우징 생성 완료!")
    return housing


def _create_housing_body(width, depth, height, params):
    """
    하우징의 기본 본체(상자가방)를 생성한다.

    매개변수:
        width, depth, height (float): 외부 치수 (mm)
        params (HousingParams): 하우징 파라미터

    반환값:
        Part.Shape: 하우징 본체 (캐비티 포함)
    """
    # 외부 상자 생성
    outer_box = Part.makeBox(width, depth, height)

    # 내부 캐비티 제거하여 벽면 생성
    inner_width = width - params.wall_thickness * 2
    inner_depth = depth - params.wall_thickness * 2
    inner_height = height - params.floor_thickness

    cavity_box = Part.makeBox(
        inner_width, inner_depth, inner_height,
        Base.Vector(params.wall_thickness, params.wall_thickness, params.floor_thickness)
    )

    # 모서리 둥글게 처리
    if params.edge_radius > 0:
        try:
            outer_box = outer_box.makeFillet(
                params.edge_radius,
                [
                    outer_box.Edges[0], outer_box.Edges[1],
                    outer_box.Edges[2], outer_box.Edges[3],
                    outer_box.Edges[4], outer_box.Edges[5],
                    outer_box.Edges[6], outer_box.Edges[7],
                ]
            )
        except Exception:
            # 모서리 둥글게 실패 시 원래 형태 사용
            pass

    housing = outer_box.cut(cavity_box)
    print("[정보] 하우징 본체 생성 완료")
    return housing


def _create_sensor_cavity(housing, template, params, outer_height):
    """
    센서 본체가 들어갈 캐비티空间을 만든다.
    센서 종류에 따라 추가 캐비티를 만든다.

    매개변수:
        housing (Part.Shape): 하우징 본체
        template (dict): 센서 템플릿
        params (HousingParams): 하우징 파라미터
        outer_height (float): 하우징 외부 높이 (mm)

    반환값:
        Part.Shape: 캐비티가 추가된 하우징
    """
    # 센서 장착 구역을 위한 추가 캐비티
    sensor_width = template["width"] + params.margin
    sensor_depth = template["depth"] + params.margin
    sensor_height = template["height"]

    # 센서 상단이 하우징 상단과 같은 높이가 되도록 위치 계산
    sensor_z = outer_height - sensor_height - params.top_clearance

    sensor_cavity = Part.makeBox(
        sensor_width, sensor_depth, sensor_height,
        Base.Vector(
            params.wall_thickness + params.margin / 2,
            params.wall_thickness + params.margin / 2,
            sensor_z
        )
    )

    housing = housing.cut(sensor_cavity)
    print(f"[정보] 센서 캐비티 생성 완료 (z={sensor_z:.1f}mm)")
    return housing


def _create_pcb_hole_pattern(housing, template, params):
    """
    PCB 고정을 위한 나사 홀 패턴을 자동 생성한다.

    매개변수:
        housing (Part.Shape): 하우징 본체
        template (dict): 센서 템플릿
        params (HousingParams): 하우징 파라미터

    반환값:
        Part.Shape: PCB 홀이 추가된 하우징
    """
    # PCB 고정 홀 위치 계산 (4 모서리)
    pcb_width = template["width"]
    pcb_depth = template["depth"]
    hole_spacing_x = pcb_width - params.mount_clearance * 2
    hole_spacing_y = pcb_depth - params.mount_clearance * 2

    # PCB 홀 위치 (4개 코너)
    hole_positions = [
        Base.Vector(params.wall_thickness + params.mount_clearance, params.wall_thickness + params.mount_clearance, 0),
        Base.Vector(params.wall_thickness + params.mount_clearance + hole_spacing_x, params.wall_thickness + params.mount_clearance, 0),
        Base.Vector(params.wall_thickness + params.mount_clearance, params.wall_thickness + params.mount_clearance + hole_spacing_y, 0),
        Base.Vector(params.wall_thickness + params.mount_clearance + hole_spacing_x, params.wall_thickness + params.mount_clearance + hole_spacing_y, 0),
    ]

    hole_diameter = params.screw_hole_diameter
    hole_depth = params.floor_thickness

    for pos in hole_positions:
        hole = Part.makeCylinder(
            hole_diameter / 2, hole_depth,
            Base.Vector(pos.x, pos.y, 0),
            Base.Vector(0, 0, 1)
        )
        housing = housing.cut(hole)

    print(f"[정보] PCB 고정 홀 {len(hole_positions)}개 생성 완료 (지름={hole_diameter}mm)")
    return housing


def _add_cable_holes(housing, params, outer_width, outer_depth):
    """
    케이블 통과를 위한 홀을 하우징 측면에 추가한다.

    매개변수:
        housing (Part.Shape): 하우징 본체
        params (HousingParams): 하우징 파라미터
        outer_width (float): 하우징 외부 가로 (mm)
        outer_depth (float): 하우징 외부 세로 (mm)

    반환값:
        Part.Shape: 케이블 홀이 추가된 하우징
    """
    hole_diameter = params.cable_hole_diameter
    hole_z_pos = params.floor_thickness + 2.0  # 바닥에서 약간 위

    # 후면 측면에 케이블 홀 배치
    cable_hole = Part.makeCylinder(
        hole_diameter / 2, outer_depth,
        Base.Vector(outer_width / 2, 0, hole_z_pos),
        Base.Vector(0, 1, 0)
    )
    housing = housing.cut(cable_hole)

    print(f"[정보] 케이블 홀 생성 완료 (지름={hole_diameter}mm)")
    return housing


def _add_sensor_specific_features(housing, template, params, outer_width, outer_depth):
    """
    센서 종류에 따라 특수 기능을 추가한다.
    - 초음파: 트랜스듀서 홀
    - 적외선: 적외선 투과창
    - PIR: 렌즈 홀

    매개변수:
        housing (Part.Shape): 하우징 본체
        template (dict): 센서 템플릿
        params (HousingParams): 하우징 파라미터
        outer_width (float): 하우징 외부 가로 (mm)
        outer_depth (float): 하우징 외부 세로 (mm)

    반환값:
        Part.Shape: 특수 기능이 추가된 하우징
    """
    series = template.get("series", "")

    if series == "HC-SR04":
        # 초음파 트랜스듀서 홀 (2개)
        transducer_diameter = template.get("transducer_diameter", 16.0)
        transducer_z = params.floor_thickness + template["height"] / 2

        # 트랜스듀서 홀 좌측
        hole1 = Part.makeCylinder(
            transducer_diameter / 2, params.wall_thickness + 1,
            Base.Vector(outer_width * 0.3, -0.5, transducer_z),
            Base.Vector(0, -1, 0)
        )
        # 트랜스듀서 홀 우측
        hole2 = Part.makeCylinder(
            transducer_diameter / 2, params.wall_thickness + 1,
            Base.Vector(outer_width * 0.7, -0.5, transducer_z),
            Base.Vector(0, -1, 0)
        )
        housing = housing.cut(hole1).cut(hole2)
        print("[정보] 초음파 트랜스듀서 홀 2개 추가")

    elif series == "GP2Y":
        # 적외선 투과창 홀
        window_width = 10.0
        window_depth = 5.0
        window_z = params.floor_thickness + template["height"] / 2

        ir_window = Part.makeBox(
            window_width, params.wall_thickness + 1, window_depth,
            Base.Vector(outer_width / 2 - window_width / 2, -0.5, window_z - window_depth / 2)
        )
        housing = housing.cut(ir_window)
        print("[정보] 적외선 투과창 홀 추가")

    elif series == "PIR":
        # PIR 렌즈 홀
        lens_diameter = template.get("lens_diameter", 23.0)
        lens_z = params.floor_thickness + template["height"] / 2

        lens_hole = Part.makeCylinder(
            lens_diameter / 2, params.wall_thickness + 1,
            Base.Vector(outer_width / 2, -0.5, lens_z),
            Base.Vector(0, -1, 0)
        )
        housing = housing.cut(lens_hole)
        print("[정보] PIR 렌즈 홀 추가")

    # 핀 홀 패턴 생성 (핀 수만큼)
    pin_count = template.get("pin_count", 4)
    pin_pitch = template.get("pin_pitch", 2.54)
    pin_z = 0  # 바닥에서 핀 홀 위치

    pin_total_width = (pin_count - 1) * pin_pitch
    pin_start_x = outer_width / 2 - pin_total_width / 2

    for i in range(pin_count):
        pin_x = pin_start_x + i * pin_pitch
        pin_hole = Part.makeCylinder(
            0.5, params.floor_thickness + 0.5,
            Base.Vector(pin_x, outer_depth / 2, pin_z),
            Base.Vector(0, 0, 1)
        )
        housing = housing.cut(pin_hole)

    print(f"[정보] 센서 핀 홀 {pin_count}개 생성 완료")
    return housing


def create_top_cover(outer_width, outer_depth, params):
    """
    하우징 상단 커버를 생성한다.

    매개변수:
        outer_width (float): 하우징 외부 가로 (mm)
        outer_depth (float): 하우징 외부 세로 (mm)
        params (HousingParams): 하우징 파라미터

    반환값:
        Part.Shape: 상단 커버 형태
    """
    cover_height = 3.0  # 커버 두께

    # 커버 본체
    cover = Part.makeBox(outer_width, outer_depth, cover_height)

    # 나사 홀
    hole_spacing_x = outer_width - params.mount_clearance * 4
    hole_spacing_y = outer_depth - params.mount_clearance * 4

    hole_positions = [
        Base.Vector(params.mount_clearance * 2, params.mount_clearance * 2, 0),
        Base.Vector(params.mount_clearance * 2 + hole_spacing_x, params.mount_clearance * 2, 0),
        Base.Vector(params.mount_clearance * 2, params.mount_clearance * 2 + hole_spacing_y, 0),
        Base.Vector(params.mount_clearance * 2 + hole_spacing_x, params.mount_clearance * 2 + hole_spacing_y, 0),
    ]

    for pos in hole_positions:
        screw_hole = Part.makeCylinder(
            params.screw_hole_diameter / 2, cover_height,
            Base.Vector(pos.x, pos.y, 0),
            Base.Vector(0, 0, 1)
        )
        cover = cover.cut(screw_hole)

    print("[정보] 상단 커버 생성 완료")
    return cover


def export_stl(shape, filename):
    """
    FreeCAD 형태를 STL 파일로 내보낸다.

    매개변수:
        shape (Part.Shape): 내보낼 형태
        filename (str): 저장할 파일 경로

    반환값:
        str: 저장된 파일 경로
    """
    try:
        shapes = []
        if hasattr(shape, "Shapes"):
            shapes = shape.Shapes
        else:
            shapes = [shape]

        # 메시 변환
        mesh = Part.Mesh()
        for s in shapes:
            mesh.addMesh(s.tessellate(0.5))

        mesh.write(filename)
        print(f"[정보] STL 파일 저장 완료: {filename}")
        return filename
    except Exception as e:
        print(f"[오류] STL 내보내기 실패: {e}")
        return None


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
            doc = FreeCAD.newDocument("센서하우징")

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
    샘플 센서 하우징들을 생성하여 FreeCAD 도큐먼트에 추가한다.
    """
    print("=" * 60)
    print("  센서 하우징 자동 설계 매크로 시작")
    print("=" * 60)

    # 사용 가능한 센서 종류 출력
    print("\n사용 가능한 센서 종류:")
    for idx, (name, info) in enumerate(SENSOR_TEMPLATES.items(), 1):
        print(f"  {idx}. {name} - {info['description']}")

    # 기본 파라미터로 하우징 생성
    params = HousingParams()

    # 다양한 센서 하우징 생성
    sensors_to_create = ["DHT11_temperature", "HC_SR04_ultrasonic", "GP2Y0A21_infrared", "PIR_motion"]

    for sensor_name in sensors_to_create:
        print(f"\n{'─' * 40}")
        print(f"[시작] {sensor_name} 하우징 생성")
        housing = create_sensor_housing(sensor_name, params)
        if housing:
            add_to_freecad_document(housing, f"{sensor_name}_하우징")

    # 각 하우징에 대한 상단 커버도 생성
    print(f"\n{'─' * 40}")
    for sensor_name in sensors_to_create:
        template = SENSOR_TEMPLATES[sensor_name]
        outer_width = template["width"] + params.wall_thickness * 2 + params.margin * 2
        outer_depth = template["depth"] + params.wall_thickness * 2 + params.margin * 2
        cover = create_top_cover(outer_width, outer_depth, params)
        add_to_freecad_document(cover, f"{sensor_name}_커버")

    print(f"\n{'=' * 60}")
    print("  센서 하우징 자동 설계 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    # FreeCAD 매크로로 실행 시
    run()

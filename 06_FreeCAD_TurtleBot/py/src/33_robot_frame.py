# -*- coding: utf-8 -*-
"""
Part 7 - 33: 로봇 프레임 설계 매크로

기본적인 로봇 프레임을 파라메트릭으로 설계하는 FreeCAD 매크로.
베이스 플레이트, 서보 모터 마운트, 링크 연결부를 포함하며,
공차를 적용하여 조립 가능한 프레임을 생성.

사용법: FreeCAD에서 실행하여 로봇 프레임이 자동 생성됨.
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
# 로봇 프레임 기본 프리셋
# ============================================================

ROBOT_PRESETS = {
    "미니로봇_2자유도": {
        "description": "2자유도 미니 로봇 암",
        "base_width": 60.0,
        "base_depth": 60.0,
        "base_thickness": 5.0,
        "link_lengths": [80.0, 80.0],
        "link_thickness": 5.0,
        "link_width": 25.0,
        "servo_size": "SG90",
    },
    "중형로봇_3자유도": {
        "description": "3자유도 중형 로봇 암",
        "base_width": 100.0,
        "base_depth": 100.0,
        "base_thickness": 8.0,
        "link_lengths": [120.0, 100.0, 80.0],
        "link_thickness": 6.0,
        "link_width": 35.0,
        "servo_size": "MG996R",
    },
    "대형로봇_4자유도": {
        "description": "4자유도 대형 로봇 암",
        "base_width": 150.0,
        "base_depth": 150.0,
        "base_thickness": 10.0,
        "link_lengths": [150.0, 120.0, 100.0, 80.0],
        "link_thickness": 8.0,
        "link_width": 45.0,
        "servo_size": "Dynamixel",
    },
    "직렬로봇_2자유도": {
        "description": "2자유도 직렬 구조 로봇",
        "base_width": 80.0,
        "base_depth": 80.0,
        "base_thickness": 6.0,
        "link_lengths": [100.0, 100.0],
        "link_thickness": 5.0,
        "link_width": 30.0,
        "servo_size": "MG995",
    },
}


# ============================================================
# 서보 모터 크기 정의
# ============================================================

SERVO_SIZES = {
    "SG90": {
        "width": 12.0,
        "depth": 23.0,
        "height": 22.5,
        "flange_width": 32.5,
        "flange_depth": 12.5,
        "flange_height": 2.6,
        "shaft_diameter": 5.0,
        "shaft_height": 16.5,
        "mount_hole_spacing": 27.5,
        "mount_hole_diameter": 3.0,
        "description": "SG90 미니 서보",
    },
    "MG995": {
        "width": 19.5,
        "depth": 40.7,
        "height": 42.9,
        "flange_width": 54.0,
        "flange_depth": 20.5,
        "flange_height": 3.0,
        "shaft_diameter": 6.0,
        "shaft_height": 16.5,
        "mount_hole_spacing": 49.0,
        "mount_hole_diameter": 4.0,
        "description": "MG995 표준 서보",
    },
    "MG996R": {
        "width": 19.5,
        "depth": 40.7,
        "height": 42.9,
        "flange_width": 54.0,
        "flange_depth": 20.5,
        "flange_height": 3.0,
        "shaft_diameter": 6.0,
        "shaft_height": 16.5,
        "mount_hole_spacing": 49.0,
        "mount_hole_diameter": 4.0,
        "description": "MG996R 고출력 서보",
    },
    "Dynamixel": {
        "width": 32.0,
        "depth": 50.0,
        "height": 38.0,
        "flange_width": 46.0,
        "flange_depth": 38.0,
        "flange_height": 4.0,
        "shaft_diameter": 8.0,
        "shaft_height": 20.0,
        "mount_hole_spacing": 38.0,
        "mount_hole_diameter": 4.5,
        "description": "Dynamixel 액추에이터",
    },
}


# ============================================================
# 공차 설정
# ============================================================

class ToleranceConfig:
    """로봇 프레임 조립 공차를 관리하는 클래스"""

    def __init__(self):
        """기본 공차 초기화"""
        self.general_tolerance = 0.2            # 일반 조립 공차 (mm)
        self.servo_mount_tolerance = 0.3       # 서보 마운트 공차 (mm)
        self.screw_tolerance = 0.1            # 나사 삽입 공차 (mm)
        self.link_gap = 1.0            # 링크 사이 간격 (mm)
        self.pin_tolerance = 0.15             # 힌지 핀 공차 (mm)
        self.assembly_margin = 0.5            # 전체 조립 마진 (mm)


# ============================================================
# 베이스 플레이트 생성
# ============================================================

def create_base_plate(preset_name, tolerance=None):
    """
    로봇 베이스 플레이트를 생성한다.

    매개변수:
        preset_name (str): 로봇 프리셋 키
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 베이스 플레이트 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if preset_name not in ROBOT_PRESETS:
        print(f"[오류] 알 수 없는 프리셋: {preset_name}")
        return None

    preset = ROBOT_PRESETS[preset_name]
    print(f"[정보] {preset['description']} 베이스 플레이트 생성 중...")

    width = preset["base_width"]
    depth = preset["base_depth"]
    thickness = preset["base_thickness"]

    # 베이스 플레이트 본체
    base = Part.makeBox(width, depth, thickness)

    # 중앙 서보 마운트 홀
    servo_info = SERVO_SIZES[preset["servo_size"]]
    center_x = width / 2
    center_y = depth / 2

    # 서보 플랜지 홈
    flange_x = servo_info["flange_width"] + tolerance.servo_mount_tolerance
    flange_y = servo_info["flange_depth"] + tolerance.servo_mount_tolerance
    flange_z = servo_info["flange_height"]

    flange_groove = Part.makeBox(
        flange_x, flange_y, flange_z + 1,
        Base.Vector(center_x - flange_x / 2, center_y - flange_y / 2, thickness - flange_z - 0.5)
    )
    base = base.cut(flange_groove)

    # 서보 마운트 나사 홀
    hole_spacing = servo_info["mount_hole_spacing"]
    hole_diameter = servo_info["mount_hole_diameter"] + tolerance.screw_tolerance

    screw_positions = [
        Base.Vector(center_x - hole_spacing / 2, center_y - hole_spacing / 2, 0),
        Base.Vector(center_x + hole_spacing / 2, center_y - hole_spacing / 2, 0),
        Base.Vector(center_x - hole_spacing / 2, center_y + hole_spacing / 2, 0),
        Base.Vector(center_x + hole_spacing / 2, center_y + hole_spacing / 2, 0),
    ]

    for pos in screw_positions:
        hole = Part.makeCylinder(
            hole_diameter / 2, thickness + 1,
            Base.Vector(pos.x, pos.y, -0.5),
            Base.Vector(0, 0, 1)
        )
        base = base.cut(hole)

    # 베이스 고정 홀 (테이블/프레임에 고정)
    fix_hole_spacing_x = width * 0.8
    fix_hole_spacing_y = depth * 0.8
    fix_hole_diameter = 4.0 + tolerance.screw_tolerance

    fix_positions = [
        Base.Vector(width / 2 - fix_hole_spacing_x / 2, depth / 2 - fix_hole_spacing_y / 2, 0),
        Base.Vector(width / 2 + fix_hole_spacing_x / 2, depth / 2 - fix_hole_spacing_y / 2, 0),
        Base.Vector(width / 2 - fix_hole_spacing_x / 2, depth / 2 + fix_hole_spacing_y / 2, 0),
        Base.Vector(width / 2 + fix_hole_spacing_x / 2, depth / 2 + fix_hole_spacing_y / 2, 0),
    ]

    for pos in fix_positions:
        hole = Part.makeCylinder(
            fix_hole_diameter / 2, thickness + 1,
            Base.Vector(pos.x, pos.y, -0.5),
            Base.Vector(0, 0, 1)
        )
        base = base.cut(hole)

    print(f"[정보] 베이스 플레이트 생성 완료: {width}x{depth}x{thickness}mm")
    return base


# ============================================================
# 서보 모터 마운트 생성
# ============================================================

def create_servo_mount(servo_size_name, height=None, tolerance=None):
    """
    서보 모터 마운트를 생성한다.

    매개변수:
        servo_size_name (str): 서보 크기 키 (서보크기 딕셔너리)
        height (float): 마운트 높이 (None이면 서보 높이 사용)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 서보 마운트 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if servo_size_name not in SERVO_SIZES:
        print(f"[오류] 알 수 없는 서보 크기: {servo_size_name}")
        return None

    servo = SERVO_SIZES[servo_size_name]
    print(f"[정보] {servo['description']} 마운트 생성 중...")

    # 마운트 치수
    mount_width = servo["flange_width"] + tolerance.servo_mount_tolerance * 2
    mount_depth = servo["flange_depth"] + tolerance.servo_mount_tolerance * 2
    mount_height = height if height else servo["height"]
    wall_thickness = 3.0

    # 마운트 본체 (상자가방)
    mount = Part.makeBox(mount_width, mount_depth, mount_height)

    # 서보 수용 캐비티
    cavity_width = servo["width"] + tolerance.servo_mount_tolerance * 2
    cavity_depth = servo["depth"] + tolerance.servo_mount_tolerance * 2
    cavity_height = servo["height"] + 1.0

    cavity = Part.makeBox(
        cavity_width, cavity_depth, cavity_height,
        Base.Vector(
            mount_width / 2 - cavity_width / 2,
            mount_depth / 2 - cavity_depth / 2,
            mount_height - cavity_height
        )
    )
    mount = mount.cut(cavity)

    # 서보 플랜지 장착 홈
    flange_x = servo["flange_width"] + tolerance.servo_mount_tolerance
    flange_y = servo["flange_depth"] + tolerance.servo_mount_tolerance
    flange_z = servo["flange_height"]

    flange_groove = Part.makeBox(
        flange_x, flange_y, flange_z,
        Base.Vector(
            mount_width / 2 - flange_x / 2,
            mount_depth / 2 - flange_y / 2,
            mount_height - cavity_height - flange_z
        )
    )
    mount = mount.cut(flange_groove)

    # 마운트 나사 홀
    hole_spacing = servo["mount_hole_spacing"]
    hole_diameter = servo["mount_hole_diameter"] + tolerance.screw_tolerance

    screw_positions = [
        Base.Vector(mount_width / 2 - hole_spacing / 2, mount_depth / 2 - hole_spacing / 2, 0),
        Base.Vector(mount_width / 2 + hole_spacing / 2, mount_depth / 2 - hole_spacing / 2, 0),
        Base.Vector(mount_width / 2 - hole_spacing / 2, mount_depth / 2 + hole_spacing / 2, 0),
        Base.Vector(mount_width / 2 + hole_spacing / 2, mount_depth / 2 + hole_spacing / 2, 0),
    ]

    for pos in screw_positions:
        hole = Part.makeCylinder(
            hole_diameter / 2, mount_height + 1,
            Base.Vector(pos.x, pos.y, -0.5),
            Base.Vector(0, 0, 1)
        )
        mount = mount.cut(hole)

    # 축 통과 홀
    shaft_diameter = servo["shaft_diameter"] + tolerance.pin_tolerance
    shaft_hole = Part.makeCylinder(
        shaft_diameter / 2, mount_height + 1,
        Base.Vector(mount_width / 2, mount_depth / 2, -0.5),
        Base.Vector(0, 0, 1)
    )
    mount = mount.cut(shaft_hole)

    print(f"[정보] 서보 마운트 생성 완료: {mount_width:.1f}x{mount_depth:.1f}x{mount_height:.1f}mm")
    return mount


# ============================================================
# 링크 연결부 생성
# ============================================================

def create_link_connector(link_length, link_width, link_thickness, tolerance=None):
    """
    로봇 링크(팔) 연결부를 생성한다.

    매개변수:
        link_length (float): 링크 길이 (mm)
        link_width (float): 링크 너비 (mm)
        link_thickness (float): 링크 두께 (mm)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 링크 연결부 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    print(f"[정보] 링크 연결부 생성 중 (길이={link_length}mm, 너비={link_width}mm)")

    # 힌지 축 지름
    hinge_shaft_diameter = 4.0 + tolerance.pin_tolerance * 2
    hinge_outer_diameter = hinge_shaft_diameter + 6.0  # 힌지 벽면 포함

    # 링크 본체 (원형 엔드 포함)
    # 메인 바디
    body = Part.makeBox(link_length, link_width, link_thickness)

    # 양쪽 끝에 원형 엔드 추가
    round_end1 = Part.makeCylinder(
        link_width / 2, link_thickness,
        Base.Vector(link_width / 2, link_width / 2, 0),
        Base.Vector(0, 0, 1)
    )
    round_end2 = Part.makeCylinder(
        link_width / 2, link_thickness,
        Base.Vector(link_length - link_width / 2, link_width / 2, 0),
        Base.Vector(0, 0, 1)
    )

    link = body.fuse(round_end1).fuse(round_end2)

    # 양쪽 끝에 힌지 홀
    hinge_hole1 = Part.makeCylinder(
        hinge_shaft_diameter / 2, link_thickness + 1,
        Base.Vector(link_width / 2, link_width / 2, -0.5),
        Base.Vector(0, 0, 1)
    )
    hinge_hole2 = Part.makeCylinder(
        hinge_shaft_diameter / 2, link_thickness + 1,
        Base.Vector(link_length - link_width / 2, link_width / 2, -0.5),
        Base.Vector(0, 0, 1)
    )

    link = link.cut(hinge_hole1).cut(hinge_hole2)

    # 가벼운 구조를 위한 내부 캐비티 (선택적)
    if link_thickness >= 5.0:
        cavity_clearance = 3.0
        cavity = Part.makeBox(
            link_length - link_width, link_width - cavity_clearance * 2, link_thickness - cavity_clearance * 2,
            Base.Vector(link_width / 2, cavity_clearance, cavity_clearance)
        )
        link = link.cut(cavity)
        print("[정보] 링크 내부 경량화 캐비티 추가")

    print(f"[정보] 링크 연결부 생성 완료")
    return link


# ============================================================
# 힌지 조인트 생성
# ============================================================

def create_hinge_joint(shaft_diameter, outer_diameter, width, tolerance=None):
    """
    힌지 조인트(축+베어링 하우징)를 생성한다.

    매개변수:
        shaft_diameter (float): 힌지 축 지름 (mm)
        outer_diameter (float): 힌지 하우징 외경 (mm)
        width (float): 힌지 너비 (mm)
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        Part.Shape: 힌지 조인트 형태
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    # 축 홀이 포함된 힌지 하우징
    housing = Part.makeCylinder(outer_diameter / 2, width)
    shaft_hole = Part.makeCylinder(
        shaft_diameter / 2 + tolerance.pin_tolerance, width + 1,
        Base.Vector(0, 0, -0.5),
        Base.Vector(0, 0, 1)
    )
    joint = housing.cut(shaft_hole)

    print(f"[정보] 힌지 조인트 생성 (축={shaft_diameter}mm, 외경={outer_diameter}mm)")
    return joint


# ============================================================
# 로봇 프레임 조립
# ============================================================

def assemble_robot_frame(preset_name, tolerance=None):
    """
    지정된 프리셋으로 전체 로봇 프레임을 조립한다.

    매개변수:
        preset_name (str): 로봇 프리셋 키
        tolerance (ToleranceConfig): 공차 설정

    반환값:
        dict: 생성된 부품들의 딕셔너리
    """
    if tolerance is None:
        tolerance = ToleranceConfig()

    if preset_name not in ROBOT_PRESETS:
        print(f"[오류] 알 수 없는 프리셋: {preset_name}")
        return None

    preset = ROBOT_PRESETS[preset_name]
    print(f"\n[정보] === {preset['description']} 조립 시작 ===")

    parts = {}

    # 1. 베이스 플레이트
    print("\n[단계 1] 베이스 플레이트 생성")
    parts["base"] = create_base_plate(preset_name, tolerance)

    # 2. 각 링크별 서보 마운트 및 링크 생성
    link_list = preset["link_lengths"]
    link_width = preset["link_width"]
    link_thickness = preset["link_thickness"]

    for idx in range(len(link_list)):
        link_length = link_list[idx]

        # 서보 마운트
        print(f"\n[단계 {idx * 2 + 2}] 링크 {idx + 1} 서보 마운트 생성")
        parts[f"servo_mount_{idx + 1}"] = create_servo_mount(
            preset["servo_size"], tolerance=tolerance
        )

        # 링크
        print(f"[단계 {idx * 2 + 3}] 링크 {idx + 1} 생성")
        parts[f"link_{idx + 1}"] = create_link_connector(
            link_length, link_width, link_thickness, tolerance
        )

    # 3. 힌지 조인트
    hinge_diameter = 4.0
    parts["hinge"] = create_hinge_joint(
        hinge_diameter, hinge_diameter + 6.0, link_width, tolerance
    )

    print(f"\n[정보] === 조립 완료: {len(parts)}개 부품 ===")
    return parts


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
            doc = FreeCAD.newDocument("로봇프레임")

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

    매개변수:
        shape (Part.Shape): 내보낼 형태
        filename (str): 저장할 파일 경로

    반환값:
        str: 저장된 파일 경로
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
    다양한 로봇 프레임을 생성하여 FreeCAD 도큐먼트에 추가한다.
    """
    print("=" * 60)
    print("  로봇 프레임 설계 매크로 시작")
    print("=" * 60)

    # 프리셋 목록 출력
    print("\n사용 가능한 로봇 프리셋:")
    for idx, (name, info) in enumerate(ROBOT_PRESETS.items(), 1):
        print(f"  {idx}. {name} - {info['description']}")

    # 서보 크기 목록
    print("\n사용 가능한 서보 크기:")
    for name, info in SERVO_SIZES.items():
        print(f"  - {name}: {info['description']} ({info['width']}x{info['depth']}x{info['height']}mm)")

    # 공차 설정
    tolerance = ToleranceConfig()
    print(f"\n공차 설정:")
    print(f"  일반 공차: {tolerance.general_tolerance}mm")
    print(f"  서보 마운트 공차: {tolerance.servo_mount_tolerance}mm")
    print(f"  핀 공차: {tolerance.pin_tolerance}mm")

    # 미니 로봇 프레임 생성
    print(f"\n{'─' * 40}")
    parts = assemble_robot_frame("미니로봇_2자유도", tolerance)

    if parts:
        for name, shape in parts.items():
            add_to_freecad_document(shape, f"미니로봇_{name}")

    # 중형 로봇 프레임도 생성
    print(f"\n{'─' * 40}")
    parts2 = assemble_robot_frame("중형로봇_3자유도", tolerance)

    if parts2:
        for name, shape in parts2.items():
            add_to_freecad_document(shape, f"중형로봇_{name}")

    print(f"\n{'=' * 60}")
    print("  로봇 프레임 설계 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()

# -*- coding: utf-8 -*-
"""
Part 7 - 40: 최종 프로젝트 - 3D 프린팅 파트너

IoT 보드, 로봇, 드론 부품을 통합 관리하는 최종 3D 프린팅 파트너 시스템.
보드 데이터베이스 관리, 프로젝트 생성, STL 내보내기, 버전 관리까지
모든 기능을 통합한 종합 솔루션.

사용법: FreeCAD에서 실행하여 3D 프린팅 프로젝트를 관리.
"""

import sys
import os
import time
import json

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)


# ============================================================
# 보드 데이터베이스
# ============================================================

BOARD_DB = {
    "Arduino Uno": {
        "category": "마이크로컨트롤러",
        "description": "Arduino Uno R3",
        "width": 68.88,
        "depth": 53.34,
        "hole_spacing_x": 63.5,
        "hole_spacing_y": 48.26,
        "hole_diameter": 3.2,
        "mounting_hole_count": 4,
        "ports": {
            "USB_B": {"width": 12.0, "height": 11.0, "x": -1.5, "y": 15.0},
            "DC_jack": {"width": 9.0, "height": 11.0, "x": -1.5, "y": 33.0},
        },
        "board_thickness": 1.6,
        "clearance_top": 10.0,
        "clearance_bottom": 3.0,
        "tags": ["Arduino", "마이크로컨트롤러", "教育用"],
    },
    "ESP32_DevKit": {
        "category": "마이크로컨트롤러",
        "description": "ESP32 DevKit V1",
        "width": 25.5,
        "depth": 51.5,
        "hole_spacing_x": 22.86,
        "hole_spacing_y": 48.9,
        "hole_diameter": 2.0,
        "mounting_hole_count": 4,
        "ports": {
            "micro_USB": {"width": 8.0, "height": 2.5, "x": 8.75, "y": -1.5},
        },
        "board_thickness": 1.6,
        "clearance_top": 8.0,
        "clearance_bottom": 2.0,
        "tags": ["ESP32", "Wi-Fi", "Bluetooth", "IoT"],
    },
    "Raspberry_Pi_4B": {
        "category": "싱글보드컴퓨터",
        "description": "Raspberry Pi 4 Model B",
        "width": 85.6,
        "depth": 56.5,
        "hole_spacing_x": 58.0,
        "hole_spacing_y": 49.0,
        "hole_diameter": 2.75,
        "mounting_hole_count": 4,
        "ports": {
            "USB_C_power": {"width": 9.0, "height": 3.5, "x": -1.5, "y": 10.0},
            "USB_3": {"width": 14.0, "height": 14.0, "x": -1.5, "y": 18.0},
            "USB_2": {"width": 14.0, "height": 14.0, "x": -1.5, "y": 36.0},
            "HDMI_micro": {"width": 11.5, "height": 5.5, "x": 65.0, "y": 10.0},
            "ethernet": {"width": 16.0, "height": 14.0, "x": 65.0, "y": 30.0},
            "micro_SD": {"width": 14.0, "height": 2.5, "x": 35.0, "y": -1.5},
        },
        "board_thickness": 1.6,
        "clearance_top": 12.0,
        "clearance_bottom": 4.0,
        "tags": ["Raspberry Pi", "Linux", "싱글보드", "컴퓨터"],
    },
    "ESP32_S3_DevKit": {
        "category": "마이크로컨트롤러",
        "description": "ESP32-S3 DevKitC-1",
        "width": 25.5,
        "depth": 60.5,
        "hole_spacing_x": 22.86,
        "hole_spacing_y": 57.9,
        "hole_diameter": 2.0,
        "mounting_hole_count": 4,
        "ports": {
            "USB_C": {"width": 9.0, "height": 3.5, "x": 8.25, "y": -1.5},
        },
        "board_thickness": 1.6,
        "clearance_top": 8.0,
        "clearance_bottom": 2.0,
        "tags": ["ESP32-S3", "AI", "IoT"],
    },
}


# ============================================================
# 3D 프린팅 프로젝트 클래스
# ============================================================

class PrintProject:
    """
    3D 프린팅 프로젝트를 관리하는 클래스.
    """

    def __init__(self, name, project_type="IoT케이스"):
        """
        매개변수:
            name (str): 프로젝트 이름
            project_type (str): 프로젝트 유형
        """
        self.name = name
        self.project_type = project_type
        self.created_at = time.time()
        self.updated_at = time.time()
        self.version = "1.0.0"
        self.status = "설계중"
        self.board_name = ""
        self.parts = {}
        self.notes = ""

    def add_part(self, name, shape):
        """
        부품을 추가한다.

        매개변수:
            name (str): 부품 이름
            shape (Part.Shape): 부품 형태
        """
        self.parts[name] = shape
        self.updated_at = time.time()
        print(f"[정보] 부품 '{name}' 추가됨 (총 {len(self.parts)}개)")

    def remove_part(self, name):
        """
        부품을 제거한다.

        매개변수:
            name (str): 제거할 부품 이름
        """
        if name in self.parts:
            del self.parts[name]
            self.updated_at = time.time()
            print(f"[정보] 부품 '{name}' 제거됨")
        else:
            print(f"[오류] 부품 '{name}'을(를) 찾을 수 없습니다.")

    def get_parts_info(self):
        """부품 정보를 반환한다."""
        info = {}
        for name, shape in self.parts.items():
            try:
                bb = shape.BoundBox
                info[name] = {
                    "크기": f"{bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm",
                    "부피": f"{shape.Volume:.1f} mm³",
                }
            except Exception:
                info[name] = {"크기": "알 수 없음", "부피": "알 수 없음"}
        return info

    def to_dict(self):
        """딕셔너리로 변환한다."""
        return {
            "name": self.name,
            "project_type": self.project_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "status": self.status,
            "board_name": self.board_name,
            "parts_count": len(self.parts),
            "notes": self.notes,
        }


# ============================================================
# 보드 검색기
# ============================================================

class BoardFinder:
    """
    보드 데이터베이스를 검색하는 클래스.
    """

    def __init__(self):
        """보드 DB 로드"""
        self.boards = BOARD_DB

    def search_by_tag(self, tag):
        """
        태그로 보드를 검색한다.

        매개변수:
            tag (str): 검색할 태그

        반환값:
            list: 일치하는 보드 목록
        """
        results = []
        for name, info in self.boards.items():
            if tag.lower() in [t.lower() for t in info.get("tags", [])]:
                results.append((name, info))
        return results

    def search_by_category(self, category):
        """
        카테고리로 보드를 검색한다.

        매개변수:
            category (str): 검색할 카테고리

        반환값:
            list: 일치하는 보드 목록
        """
        results = []
        for name, info in self.boards.items():
            if info.get("category", "").lower() == category.lower():
                results.append((name, info))
        return results

    def search_by_size(self, max_width, max_depth):
        """
        크기로 보드를 검색한다.

        매개변수:
            max_width (float): 최대 너비 (mm)
            max_depth (float): 최대 깊이 (mm)

        반환값:
            list: 일치하는 보드 목록
        """
        results = []
        for name, info in self.boards.items():
            if info["width"] <= max_width and info["depth"] <= max_depth:
                results.append((name, info))
        return results

    def list_all(self):
        """모든 보드를 출력한다."""
        print("\n[정보] === 보드 데이터베이스 ===")
        for name, info in self.boards.items():
            print(f"\n  {name}")
            print(f"    카테고리: {info['category']}")
            print(f"    설명: {info['description']}")
            print(f"    크기: {info['width']} x {info['depth']} mm")
            print(f"    태그: {', '.join(info.get('tags', []))}")
        print()


# ============================================================
# 케이스 생성기
# ============================================================

class CaseGenerator:
    """
    IoT 보드용 케이스를 생성하는 클래스.
    """

    def __init__(self, board_info, tolerance=None):
        """
        매개변수:
            board_info (dict): 보드 정보
        """
        self.board = board_info
        self.wall_thickness = 2.5
        self.tolerance = tolerance or 0.2

    def generate_bottom(self):
        """하단 케이스를 생성한다."""
        width = self.board["width"] + self.tolerance * 2 + self.wall_thickness * 2
        depth = self.board["depth"] + self.tolerance * 2 + self.wall_thickness * 2
        height = self.board["clearance_bottom"] + self.board["board_thickness"] + 2.0

        case = Part.makeBox(width, depth, height)

        # 내부 캐비티
        inner_w = width - self.wall_thickness * 2
        inner_d = depth - self.wall_thickness * 2
        inner_h = height - self.wall_thickness
        cavity = Part.makeBox(
            inner_w, inner_d, inner_h,
            Base.Vector(self.wall_thickness, self.wall_thickness, self.wall_thickness)
        )
        case = case.cut(cavity)

        # 스탠드오프
        cx, cy = width / 2, depth / 2
        hx = self.board["hole_spacing_x"] / 2
        hy = self.board["hole_spacing_y"] / 2

        for sx, sy in [(cx-hx, cy-hy), (cx+hx, cy-hy), (cx-hx, cy+hy), (cx+hx, cy+hy)][:self.board["mounting_hole_count"]]:
            standoff = Part.makeCylinder(
                3.0, self.board["clearance_bottom"],
                Base.Vector(sx, sy, self.wall_thickness),
                Base.Vector(0, 0, 1)
            )
            case = case.fuse(standoff)

            hole = Part.makeCylinder(
                1.5, self.board["clearance_bottom"] + 1,
                Base.Vector(sx, sy, self.wall_thickness - 0.5),
                Base.Vector(0, 0, 1)
            )
            case = case.cut(hole)

        return case

    def generate_top(self):
        """상단 커버를 생성한다."""
        width = self.board["width"] + self.tolerance * 2 + self.wall_thickness * 2
        depth = self.board["depth"] + self.tolerance * 2 + self.wall_thickness * 2
        height = self.board["clearance_top"] + self.wall_thickness

        cover = Part.makeBox(width, depth, height)

        # 내부 캐비티
        inner_w = width - self.wall_thickness * 2
        inner_d = depth - self.wall_thickness * 2
        inner_h = self.board["clearance_top"]
        cavity = Part.makeBox(
            inner_w, inner_d, inner_h,
            Base.Vector(self.wall_thickness, self.wall_thickness, 0)
        )
        cover = cover.cut(cavity)

        # 환기구
        cx, cy = width / 2, depth / 2
        for i in range(4):
            angle = __import__("math").radians(i * 90 + 45)
            vx = cx + __import__("math").cos(angle) * inner_w * 0.25
            vy = cy + __import__("math").sin(angle) * inner_d * 0.25
            vent = Part.makeCylinder(
                2.0, self.wall_thickness + 1,
                Base.Vector(vx, vy, -0.5),
                Base.Vector(0, 0, 1)
            )
            cover = cover.cut(vent)

        return cover


# ============================================================
# STL 내보내기
# ============================================================

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
# FreeCAD 통합 함수
# ============================================================

def add_to_freecad_document(shape, name):
    """
    형태를 FreeCAD 활성 도큐먼트에 추가한다.
    """
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("3D프린팅파트너")

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
    3D 프린팅 파트너 시스템을 데모한다.
    """
    print("=" * 60)
    print("  3D 프린팅 파트너 - 최종 프로젝트")
    print("=" * 60)

    # 1. 보드 검색
    finder = BoardFinder()
    finder.list_all()

    # IoT 관련 보드 검색
    print("[검색] 'IoT' 태그 보드:")
    iot_boards = finder.search_by_tag("IoT")
    for name, info in iot_boards:
        print(f"  - {name}: {info['description']}")

    # 싱글보드 컴퓨터 검색
    print("\n[검색] 싱글보드컴퓨터 카테고리:")
    sbc_boards = finder.search_by_category("싱글보드컴퓨터")
    for name, info in sbc_boards:
        print(f"  - {name}: {info['description']}")

    # 2. 프로젝트 생성
    print(f"\n{'─' * 40}")
    print("[정보] ESP32 IoT 프로젝트 생성")
    project = PrintProject("ESP32_센서케이스", "IoT케이스")
    project.board_name = "ESP32_DevKit"
    project.notes = "실내 온습도 센서용 케이스"

    # 3. 케이스 생성
    esp32_info = BOARD_DB["ESP32_DevKit"]
    generator = CaseGenerator(esp32_info)

    print("\n[생성] 하단 케이스")
    bottom = generator.generate_bottom()
    project.add_part("하단", bottom)
    add_to_freecad_document(bottom, "ESP32_하단케이스")

    print("[생성] 상단 커버")
    top = generator.generate_top()
    project.add_part("상단", top)
    add_to_freecad_document(top, "ESP32_상단커버")

    # 4. 프로젝트 정보
    print(f"\n{'─' * 40}")
    print("[정보] 프로젝트 요약:")
    info = project.to_dict()
    for key, value in info.items():
        if key != "parts_count":
            print(f"  {key}: {value}")

    print("\n[정보] 부품 상세:")
    parts_info = project.get_parts_info()
    for name, details in parts_info.items():
        print(f"  {name}:")
        for key, value in details.items():
            print(f"    {key}: {value}")

    # 5. STL 내보내기
    print(f"\n{'─' * 40}")
    export_stl(bottom, "ESP32_하단케이스.stl")
    export_stl(top, "ESP32_상단커버.stl")

    # 6. 추가 프로젝트: RPi4B 케이스
    print(f"\n{'─' * 40}")
    print("[정보] Raspberry Pi 4B 프로젝트 생성")
    project2 = PrintProject("RPi4B_케이스", "IoT케이스")
    project2.board_name = "Raspberry_Pi_4B"

    rpi_info = BOARD_DB["Raspberry_Pi_4B"]
    gen2 = CaseGenerator(rpi_info)

    bottom2 = gen2.generate_bottom()
    project2.add_part("하단", bottom2)
    add_to_freecad_document(bottom2, "RPi4B_하단케이스")

    top2 = gen2.generate_top()
    project2.add_part("상단", top2)
    add_to_freecad_document(top2, "RPi4B_상단커버")

    export_stl(bottom2, "RPi4B_하단케이스.stl")
    export_stl(top2, "RPi4B_상단커버.stl")

    print(f"\n{'=' * 60}")
    print("  3D 프린팅 파트너 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()

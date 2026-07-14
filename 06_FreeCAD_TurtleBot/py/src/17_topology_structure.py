# -*- coding: utf-8 -*-
"""
Part 4 - 알고리즘 기반 설계
第17節: 토폴로지 structure

실row_val 방법:
  FreeCAD 메뉴 > 매크로 > 매크로 실row_val... > 이 파일 line택 > 실row_val

목적:
  격자 structure를 이용한 경량화 설계를 구현합니다.
  - 3D 격자 structure 생성
  - density 기반 structure 분배
  - 경량화 bracket 예제
"""

import FreeCAD
import Part
import Math
import random


# ============================================================
# 1. 3D 격자 structure 생성
# ============================================================

def create_single_grid_node(position, size=2.0, form_type="구"):
    """
    격자 structure의 단일 node를 생성합니다.

    매개변수:
        position: FreeCAD.Vector node center position
        size: node size (mm)
        form_type: node form_type - "구", "박스", "실린더"

    반환value:
        Part.Shape: node 셰이프
    """
    if form_type == "구":
        return Part.makeSphere(size / 2.0, position)
    elif form_type == "박스":
        return Part.makeBox(size, size, size,
                            FreeCAD.Vector(position.x - size / 2, position.y - size / 2, position.z - size / 2))
    elif form_type == "실린더":
        return Part.makeCylinder(size / 2.0, size, position, FreeCAD.Vector(0, 0, 1))
    else:
        return Part.makeSphere(size / 2.0, position)


def create_grid_structure(start_position, grid_count_x, grid_count_y, grid_count_z, grid_spacing=10.0, node_size=2.0, form_type="구"):
    """
    3D 격자 structure를 생성합니다.
    각 격자 교차점에 node를 배치하고 서로 연결합니다.

    매개변수:
        start_position: FreeCAD.Vector 격자 start position
        grid_count_x: Xaxis direction 격자 수
        grid_count_y: Yaxis direction 격자 수
        grid_count_z: Zaxis direction 격자 수
        grid_spacing: 격자 간 distance (mm)
        node_size: 각 node의 size (mm)
        form_type: node form_type ("구", "박스", "실린더")

    반환value:
        Part.Shape: 격자 structure 셰이프
    """
    print(f"  3D 격자 structure 생성 start")
    print(f"    격자 수: {grid_count_x} x {grid_count_y} x {grid_count_z}")
    print(f"    격자 spacing: {grid_spacing}mm, node size: {node_size}mm")

    total_structure = None
    node_list = []
    connection_list = []

    # node 생성
    for x in range(grid_count_x):
        for y in range(grid_count_y):
            for z in range(grid_count_z):
                position = FreeCAD.Vector(
                    start_position.x + x * grid_spacing,
                    start_position.y + y * grid_spacing,
                    start_position.z + z * grid_spacing,
                )
                node = create_single_grid_node(position, node_size, form_type)
                node_list.append((position, node))

    # 연결 line(실린더) 생성 - 인접 node 간
    conn_diameter = node_size * 0.3
    for position, node in node_list:
        for other_pos, other_node in node_list:
            if position == other_pos:
                continue

            distance = position.distanceToPoint(other_pos)
            if abs(distance - grid_spacing) < 0.1:  # 인접 node만 연결
                # 두 node를 잇는 실린더 생성
                midpoint = FreeCAD.Vector(
                    (position.x + other_pos.x) / 2,
                    (position.y + other_pos.y) / 2,
                    (position.z + other_pos.z) / 2,
                )
                direction = other_pos.sub(position).normalize()
                conn_line = Part.makeCylinder(
                    conn_diameter, distance,
                    position, direction
                )
                connection_list.append(conn_line)

    # 모든 요소 결합
    total_count = 0
    for position, node in node_list:
        if total_structure is None:
            total_structure = node
        else:
            total_structure = total_structure.fuse(node)
        total_count += 1

    for conn_line in connection_list:
        if total_structure is None:
            total_structure = conn_line
        else:
            total_structure = total_structure.fuse(conn_line)
        total_count += 1

    if total_structure is None:
        print("  경고: 격자 structure가 비어있습니다.")
        return Part.makeBox(1, 1, 1)

    print(f"  격자 structure 생성 완료 - node: {len(node_list)}개, 연결: {len(connection_list)}개")
    print(f"  총 volume: {total_structure.Volume:.2f} mm³")

    return total_structure


# ============================================================
# 2. density 기반 structure 분배
# ============================================================

def create_density_map(grid_count_x, grid_count_y, grid_count_z, center_pos=None):
    """
    격자 structure combined에 대한 density 맵을 생성합니다.
    center부에 높은 density, 외곽부에 낮은 density를 배치합니다.

    매개변수:
        grid_count_x: Xaxis 격자 수
        grid_count_y: Yaxis 격자 수
        grid_count_z: Zaxis 격자 수
        center_pos: (x, y, z) 튜플 - center 좌표 (None이면 center 사용)

    반환value:
        list: 3차원 density 배col_data (0.0 ~ 1.0)
    """
    if center_pos is None:
        center_pos = (grid_count_x / 2, grid_count_y / 2, grid_count_z / 2)

    density_map = []
    max_distance = ((grid_count_x / 2) ** 2 + (grid_count_y / 2) ** 2 + (grid_count_z / 2) ** 2) ** 0.5

    for x in range(grid_count_x):
        layer = []
        for y in range(grid_count_y):
            col_data = []
            for z in range(grid_count_z):
                # center으로부터의 distance 계산
                distance = ((x - center_pos[0]) ** 2 +
                        (y - center_pos[1]) ** 2 +
                        (z - center_pos[2]) ** 2) ** 0.5

                # distance에 반비례하는 density (center 1.0, 외곽 0.0)
                if max_distance > 0:
                    density = 1.0 - (distance / max_distance)
                else:
                    density = 1.0

                # 제곱하여 center 집중도 강화
                density = density ** 2
                col_data.append(density)
            layer.append(col_data)
        density_map.append(layer)

    return density_map


def create_density_based_grid(start_position, grid_count_x, grid_count_y, grid_count_z,
                         grid_spacing=10.0, max_node_size=3.0, density_threshold=0.1,
                         density_map=None):
    """
    density 맵을 기반으로 격자 structure를 생성합니다.
    density가 높은 곳에는 큰 node, 낮은 곳에는 작은 node 또는 node 없음.

    매개변수:
        start_position: FreeCAD.Vector 격자 start position
        grid_count_x, grid_count_y, grid_count_z: 격자 수
        grid_spacing: 격자 간 distance (mm)
        max_node_size: 최대 node size (mm)
        density_threshold: 이 value 이하의 density에서는 node 생성 안 함
        density_map: density 기반 배col_data (None이면 기본 density 맵 생성)

    반환value:
        Part.Shape: density 기반 격자 structure
    """
    if density_map is None:
        density_map = create_density_map(grid_count_x, grid_count_y, grid_count_z)

    print(f"  density 기반 격자 structure 생성 start")
    print(f"    임계value: {density_threshold}")

    total_structure = None
    created_nodes = 0
    conn_diameter_default = max_node_size * 0.2

    for x in range(grid_count_x):
        for y in range(grid_count_y):
            for z in range(grid_count_z):
                density = density_map[x][y][z]

                # density가 임계value 이하면 node 생성 스킵
                if density < density_threshold:
                    continue

                position = FreeCAD.Vector(
                    start_position.x + x * grid_spacing,
                    start_position.y + y * grid_spacing,
                    start_position.z + z * grid_spacing,
                )

                # density에 비례한 node size
                node_size = max_node_size * density
                node = Part.makeSphere(node_size / 2.0, position)

                if total_structure is None:
                    total_structure = node
                else:
                    total_structure = total_structure.fuse(node)
                created_nodes += 1

                # 인접 node 연결 (density에 비례한 두께)
                for dx, dy, dz in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if (0 <= nx < grid_count_x and
                            0 <= ny < grid_count_y and
                            0 <= nz < grid_count_z):

                        adj_density = density_map[nx][ny][nz]
                        if adj_density < density_threshold:
                            continue

                        conn_diameter = conn_diameter_default * min(density, adj_density)
                        adj_position = FreeCAD.Vector(
                            start_position.x + nx * grid_spacing,
                            start_position.y + ny * grid_spacing,
                            start_position.z + nz * grid_spacing,
                        )
                        conn_line = Part.makeCylinder(
                            conn_diameter, position.distanceToPoint(adj_position),
                            position, adj_position.sub(position).normalize()
                        )

                        if total_structure is None:
                            total_structure = conn_line
                        else:
                            total_structure = total_structure.fuse(conn_line)

    print(f"  density 기반 격자 생성 완료 - 생성된 node: {created_nodes}개")

    if total_structure is None:
        return Part.makeBox(1, 1, 1)

    print(f"  총 volume: {total_structure.Volume:.2f} mm³")
    return total_structure


# ============================================================
# 3. 경량화 bracket 예제
# ============================================================

def create_lightweight_bracket(width=60, depth=40, height=40, wall_thickness=3.0,
                         grid_spacing=8.0, density_intensity=2.0):
    """
    격자 structure를 이용한 경량화 bracket을 생성합니다.
    기존 솔리드 bracket을 격자 structure로 대체하여 무게를 줄입니다.

    매개변수:
        width: bracket width size (mm)
        depth: bracket depth size (mm)
        height: bracket height (mm)
        wall_thickness: 외곽 wall 두께 (mm)
        grid_spacing: 격자 structure의 spacing (mm)
        density_intensity: density 분포의 강도 (높을수록 center 집중)

    반환value:
        Part.Shape: 경량화된 bracket 셰이프
    """
    print(f"  경량화 bracket 생성 start")
    print(f"    size: {width} x {depth} x {height} mm")

    # 1단계: 기본 bracket form_type 생성 (외곽 wall)
    wall_width = width
    wall_depth = depth
    wall_height = height

    # floor 판
    floor = Part.makeBox(wall_width, wall_depth, wall_thickness)
    # perpendicular wall 1 (뒤)
    back_wall = Part.makeBox(wall_width, wall_thickness, wall_height,
                         FreeCAD.Vector(0, 0, wall_thickness))
    # perpendicular wall 2 (옆)
    side_wall = Part.makeBox(wall_thickness, wall_depth, wall_height,
                         FreeCAD.Vector(0, 0, wall_thickness))

    outer_structure = floor.fuse(back_wall).fuse(side_wall)

    # 2단계: 내부 영역에 격자 structure 생성
    inner_start_x = wall_thickness + 1
    inner_start_y = wall_thickness + 1
    inner_start_z = wall_thickness + 1

    grid_count_x = max(1, int((width - 2 * wall_thickness - 2) / grid_spacing))
    grid_count_y = max(1, int((depth - 2 * wall_thickness - 2) / grid_spacing))
    grid_count_z = max(1, int((height - wall_thickness - 2) / grid_spacing))

    if grid_count_x > 0 and grid_count_y > 0 and grid_count_z > 0:
        # density 맵 생성 (floor과 back_wall 쪽에 높은 density)
        density_map = []
        for x in range(grid_count_x):
            layer = []
            for y in range(grid_count_y):
                col_data = []
                for z in range(grid_count_z):
                    # floor 근처 + back_wall 근처 = 높은 density
                    floor_distance = z / max(grid_count_z - 1, 1)
                    back_wall_distance = y / max(grid_count_y - 1, 1)

                    density = (1.0 - floor_distance * 0.5) * (1.0 - back_wall_distance * 0.3)
                    density = density ** (1.0 / density_intensity) if density_intensity > 0 else density
                    density = max(0.0, min(1.0, density))
                    col_data.append(density)
                layer.append(col_data)
            density_map.append(layer)

        inner_grid = create_density_based_grid(
            FreeCAD.Vector(inner_start_x, inner_start_y, inner_start_z),
            grid_count_x, grid_count_y, grid_count_z,
            grid_spacing=grid_spacing,
            max_node_size=grid_spacing * 0.4,
            density_threshold=0.1,
            density_map=density_map,
        )

        # 외곽 wall과 격자 structure 결합
        result = outer_structure.fuse(inner_grid)
    else:
        print("  경고: 격자 구수가 0입니다. 외곽 wall만 생성합니다.")
        result = outer_structure

    print(f"  경량화 bracket 생성 완료 - volume: {result.Volume:.2f} mm³")

    # 원래 솔리드 bracket 대비 경량화율 계산
    original_volume = width * depth * height  # 완전 솔리드 기준
    lightweight_ratio = (1 - result.Volume / original_volume) * 100
    print(f"  경량화 ratio_val: {lightweight_ratio:.1f}% (완전 솔리드 대비)")

    return result


def create_original_bracket(width=60, depth=40, height=40):
    """
    비교용 원본 솔리드 bracket을 생성합니다.

    매개변수:
        width, depth, height: bracket size (mm)

    반환value:
        Part.Shape: 솔리드 bracket
    """
    # L자 form_type bracket
    floor = Part.makeBox(width, depth, 5)
    perpendicular = Part.makeBox(5, depth, height - 5, FreeCAD.Vector(0, 0, 5))

    return floor.fuse(perpendicular)


# ============================================================
# 4. 격자 structure stats_val analysis_val
# ============================================================

def analyze_grid_structure(grid_structure):
    """
    격자 structure의 stats_val를 analysis_val합니다.

    매개변수:
        grid_structure: analysis_val할 Part.Shape

    반환value:
        dict: analysis_val result
    """
    bb = grid_structure.BoundBox
    bbox_volume = bb.XLength * bb.YLength * bb.ZLength

    analysis_val = {
        " volume": grid_structure.Volume,
        " area_val": grid_structure.Area,
        " bbox_volume": bbox_volume,
        " density": grid_structure.Volume / bbox_volume if bbox_volume > 0 else 0,
        " specific_area": grid_structure.Area / grid_structure.Volume if grid_structure.Volume > 0 else 0,
    }

    return analysis_val


# ============================================================
# 5. 메인 실row_val 함수
# ============================================================

def main_run():
    """
    토폴로지 structure 메인 실row_val 함수입니다.
    3D 격자 structure, density 기반 분배, 경량화 bracket을 순차적으로 시연합니다.
    """
    print("=" * 60)
    print("  Part 4 - 토폴로지 structure")
    print("  격자 structure를 이용한 경량화 설계")
    print("=" * 60)

    # ----------------------------------------------------------
    # 시나리오 1: 기본 3D 격자 structure
    # ----------------------------------------------------------
    print("\n[시나리오 1] 기본 3D 격자 structure 생성")
    print("-" * 50)

    basic_grid = create_grid_structure(
        start_position=FreeCAD.Vector(0, 0, 0),
        grid_count_x=4,
        grid_count_y=3,
        grid_count_z=3,
        grid_spacing=10.0,
        node_size=3.0,
        form_type="구",
    )

    basic_analysis = analyze_grid_structure(basic_grid)
    print(f"\n  [기본 격자 analysis_val]")
    for key, value in basic_analysis.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
        else:
            print(f"    {key}: {value}")

    # ----------------------------------------------------------
    # 시나리오 2: density 기반 격자 structure
    # ----------------------------------------------------------
    print("\n[시나리오 2] density 기반 격자 structure")
    print("-" * 50)

    # density 맵 생성 및 check
    density_map = create_density_map(5, 4, 4)
    print("  density 맵 샘플 (z=2 layer):")
    for x in range(5):
        row_val = ""
        for y in range(4):
            row_val += f"  {density_map[x][y][2]:.2f}"
        print(f"    {row_val}")

    density_grid = create_density_based_grid(
        start_position=FreeCAD.Vector(0, 0, 0),
        grid_count_x=5,
        grid_count_y=4,
        grid_count_z=4,
        grid_spacing=10.0,
        max_node_size=3.5,
        density_threshold=0.15,
        density_map=density_map,
    )

    density_analysis = analyze_grid_structure(density_grid)
    print(f"\n  [density 기반 격자 analysis_val]")
    for key, value in density_analysis.items():
        if isinstance(value, float):
            print(f"    {key}: {value:.4f}")
        else:
            print(f"    {key}: {value}")

    # ----------------------------------------------------------
    # 시나리오 3: 경량화 bracket
    # ----------------------------------------------------------
    print("\n[시나리오 3] 경량화 bracket 예제")
    print("-" * 50)

    # 원본 bracket
    original_bracket = create_original_bracket(width=60, depth=40, height=40)
    print(f"  원본 bracket volume: {original_bracket.Volume:.2f} mm³")

    # 경량화 bracket (다양한 격자 spacing)
    spacing_list = [6.0, 8.0, 10.0]
    for spacing in spacing_list:
        lightweight_bracket = create_lightweight_bracket(
            width=60, depth=40, height=40,
            wall_thickness=3.0, grid_spacing=spacing, density_intensity=2.0,
        )
        analysis_val = analyze_grid_structure(lightweight_bracket)
        print(f"    spacing {spacing}mm: volume {lightweight_bracket.Volume:.2f} mm³, "
              f"density {analysis_val[' density']:.3f}")

    # ----------------------------------------------------------
    # FreeCAD doc에 result 표시
    # ----------------------------------------------------------
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("토폴로지_structure")

        # 기본 격자
        obj1 = doc.addObject("Part::Feature", "basic_grid_structure")
        obj1.Shape = basic_grid

        # density 기반 격자 (position moved)
        obj2 = doc.addObject("Part::Feature", "density_기반_격자")
        density_moved = density_grid.copy()
        density_moved.translate(FreeCAD.Vector(70, 0, 0))
        obj2.Shape = density_moved

        # 경량화 bracket (position moved)
        lightweight_final = create_lightweight_bracket(width=60, depth=40, height=40)
        obj3 = doc.addObject("Part::Feature", "경량화_bracket")
        lightweight_moved = lightweight_final.copy()
        lightweight_moved.translate(FreeCAD.Vector(150, 0, 0))
        obj3.Shape = lightweight_moved

        # 원본 bracket 비교 (position moved)
        obj4 = doc.addObject("Part::Feature", "original_bracket")
        original_moved = original_bracket.copy()
        original_moved.translate(FreeCAD.Vector(150, 50, 0))
        obj4.Shape = original_moved

        doc.recompute()
        print("\n  FreeCAD doc에 result가 추가되었습니다.")
        print("  브라우저에서 각 model_val을 check하세요.")
    except Exception as e:
        print(f"\n  FreeCAD doc 작업 FAIL: {e}")

    print("\n" + "=" * 60)
    print("  토폴로지 structure 생성 완료!")
    print("=" * 60)


# ============================================================
# 스크립트 실row_val 진입점
# ============================================================
if __name__ == "__main__":
    main_run()
else:
    main_run()

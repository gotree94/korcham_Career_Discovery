# -*- coding: utf-8 -*-
"""
Part 4 - 알고리즘 기반 설계
第20節: 프랙탈 structure

실row_val 방법:
  FreeCAD 메뉴 > 매크로 > 매크로 실row_val... > 이 파일 line택 > 실row_val

목적:
  프랙탈 알고리즘을 이용한 structure 생성을 구현합니다.
  - 코르크스프레임 유사 structure
  - 반복적 structure 생성
"""

import FreeCAD
import Part
import Math


# ============================================================
# 1. 프랙탈 기반 유틸리티
# ============================================================

def create_fractal_line(start_pt, end_pt, depth, max_depth, axis="Z"):
    """
    프랙탈 line structure를 재귀적으로 생성합니다.
    각 line 분기에서 2개의 sub line으로 나뉩니다.

    매개변수:
        start_pt: FreeCAD.Vector line start_pt
        end_pt: FreeCAD.Vector line end_pt
        depth: current 재귀 depth
        max_depth: 최대 재귀 depth
        axis: 분기 direction axis ("X", "Y", "Z")

    반환value:
        Part.Shape: 프랙탈 line structure
    """
    if depth >= max_depth:
        # 리프 node: line 반환
        line = Part.makeLine((start_pt, end_pt))
        diameter = max(0.2, 1.0 - depth * 0.15)
        try:
            return line.makePipe(diameter)
        except Exception:
            return line

    # current line에서 branch_point 계산
    midpoint = FreeCAD.Vector(
        (start_pt.x + end_pt.x) / 2,
        (start_pt.y + end_pt.y) / 2,
        (start_pt.z + end_pt.z) / 2,
    )

    line_length = start_pt.distanceToPoint(end_pt)
    branch_length = line_length * 0.5
    offset_val = branch_length * 0.5

    # 분기 direction 벡터 계산
    direction = end_pt.sub(start_pt).normalize()

    if axis == "Z":
        branch1_end = FreeCAD.Vector(
            midpoint.x - offset_val, midpoint.y - offset_val, midpoint.z + branch_length
        )
        branch2_end = FreeCAD.Vector(
            midpoint.x + offset_val, midpoint.y + offset_val, midpoint.z + branch_length
        )
    elif axis == "X":
        branch1_end = FreeCAD.Vector(
            midpoint.x + branch_length, midpoint.y - offset_val, midpoint.z - offset_val
        )
        branch2_end = FreeCAD.Vector(
            midpoint.x + branch_length, midpoint.y + offset_val, midpoint.z + offset_val
        )
    else:  # "Y"
        branch1_end = FreeCAD.Vector(
            midpoint.x - offset_val, midpoint.y + branch_length, midpoint.z - offset_val
        )
        branch2_end = FreeCAD.Vector(
            midpoint.x + offset_val, midpoint.y + branch_length, midpoint.z + offset_val
        )

    # current depth의 line (굵기: depth에 반비례)
    diameter = max(0.3, 2.0 - depth * 0.3)
    try:
        main_line = Part.makeLine((start_pt, midpoint)).makePipe(diameter)
    except Exception:
        main_line = Part.makeLine((start_pt, midpoint))

    # 재귀 호출
    next_axis = "X" if axis == "Z" else ("Y" if axis == "X" else "Z")

    branch1 = create_fractal_line(midpoint, branch1_end, depth + 1, max_depth, next_axis)
    branch2 = create_fractal_line(midpoint, branch2_end, depth + 1, max_depth, next_axis)

    # 합침
    try:
        result = main_line.fuse(branch1).fuse(branch2)
    except Exception:
        result = main_line

    return result


def create_fractal_box(center, size, depth, max_depth):
    """
    프랙탈 box structure를 재귀적으로 생성합니다.
    각 box에서 8개의 sub box로 분할합니다.

    매개변수:
        center: FreeCAD.Vector center position
        size: current box의 size (mm)
        depth: current 재귀 depth
        max_depth: 최대 재귀 depth

    반환value:
        Part.Shape: 프랙탈 box structure
    """
    if depth >= max_depth:
        half = size / 2
        box = Part.makeBox(size, size, size,
                            FreeCAD.Vector(center.x - half, center.y - half, center.z - half))
        return box

    current_size = size * 0.4
    sub_size = size * 0.35

    # current 레벨 box
    half = current_size / 2
    current_box = Part.makeBox(current_size, current_size, current_size,
                              FreeCAD.Vector(center.x - half, center.y - half, center.z - half))

    # 8개 꼭짓점 direction으로 sub box 생성
    combined = current_box
    offset_val = size * 0.3

    for dx in [-1, 1]:
        for dy in [-1, 1]:
            for dz in [-1, 1]:
                sub_center = FreeCAD.Vector(
                    center.x + dx * offset_val,
                    center.y + dy * offset_val,
                    center.z + dz * offset_val,
                )
                try:
                    sub = create_fractal_box(sub_center, sub_size, depth + 1, max_depth)
                    combined = combined.fuse(sub)
                except Exception:
                    pass

    return combined


# ============================================================
# 2. 코르크스프레임 유사 structure
# ============================================================

def create_koch_frame(start_pt, end_pt, depth=5):
    """
    코르크스프레임(Koch Snowflake) 유사 structure를 생성합니다.
    3D 코르크스프레임: 각 면에 코르크스 곡line pattern을 적용합니다.

    매개변수:
        start_pt: FreeCAD.Vector pillar start_pt
        end_pt: FreeCAD.Vector pillar end_pt
        depth: 프랙탈 반복 depth

    반환value:
        Part.Shape: 코르크스프레임 structure
    """
    print(f"  코르크스프레임 생성 - depth: {depth}")

    # 4개 pillar (정방형 배치)
    offset_val = 10.0
    pillar_list = [
        (FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 40)),
        (FreeCAD.Vector(offset_val, 0, 0), FreeCAD.Vector(offset_val, 0, 40)),
        (FreeCAD.Vector(offset_val, offset_val, 0), FreeCAD.Vector(offset_val, offset_val, 40)),
        (FreeCAD.Vector(0, offset_val, 0), FreeCAD.Vector(0, offset_val, 40)),
    ]

    combined = None

    for start, end_pt in pillar_list:
        pillar = create_fractal_line(start, end_pt, 0, depth, "Z")
        if combined is None:
            combined = pillar
        else:
            try:
                combined = combined.fuse(pillar)
            except Exception:
                pass

    # 수평 conn_line (bottom_pts)
    bottom_connections = [
        (FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(offset_val, 0, 0)),
        (FreeCAD.Vector(offset_val, 0, 0), FreeCAD.Vector(offset_val, offset_val, 0)),
        (FreeCAD.Vector(offset_val, offset_val, 0), FreeCAD.Vector(0, offset_val, 0)),
        (FreeCAD.Vector(0, offset_val, 0), FreeCAD.Vector(0, 0, 0)),
    ]

    # top_pt conn_line
    top_connections = [
        (FreeCAD.Vector(0, 0, 40), FreeCAD.Vector(offset_val, 0, 40)),
        (FreeCAD.Vector(offset_val, 0, 40), FreeCAD.Vector(offset_val, offset_val, 40)),
        (FreeCAD.Vector(offset_val, offset_val, 40), FreeCAD.Vector(0, offset_val, 40)),
        (FreeCAD.Vector(0, offset_val, 40), FreeCAD.Vector(0, 0, 40)),
    ]

    for start, end_pt in bottom_connections + top_connections:
        line = create_fractal_line(start, end_pt, 0, max(1, depth - 1), "X")
        if combined is not None:
            try:
                combined = combined.fuse(line)
            except Exception:
                pass

    if combined is None:
        return Part.makeBox(1, 1, 1)

    print(f"  코르크스프레임 완료 - volume: {combined.Volume:.2f} mm³")
    return combined


def create_koch_curve(start_pt, end_pt, depth=4):
    """
    2D 코르크스 곡line을 생성하고 3D pipe_val로 만듭니다.

    코르크스 곡line 규칙:
      line분 → 4개의 line분으로 교체
      /\\ form_type (중간 1/3을 tri형으로)

    매개변수:
        start_pt: FreeCAD.Vector start_pt
        end_pt: FreeCAD.Vector end_pt
        depth: 반복 depth

    반환value:
        Part.Shape: 3D 코르크스 곡line
    """
    print(f"  코르크스 곡line 생성 - depth: {depth}")

    points = create_koch_points(start_pt, end_pt, depth)
    print(f"    생성된 점 수: {len(points)}개")

    if len(points) < 2:
        return Part.makeLine((start_pt, end_pt))

    # 점 목록으로 와이어 생성 후 pipe_val
    combined = None
    diameter = 0.5

    for i in range(len(points) - 1):
        try:
            seg = Part.makeLine((points[i], points[i + 1]))
            pipe_val = seg.makePipe(diameter)
            if combined is None:
                combined = pipe_val
            else:
                combined = combined.fuse(pipe_val)
        except Exception:
            pass

    if combined is None:
        return Part.makeLine((start_pt, end_pt))

    print(f"    코르크스 곡line 완료 - volume: {combined.Volume:.2f} mm³")
    return combined


def create_koch_points(start_pt, end_pt, depth):
    """
    코르크스 곡line의 점 목록을 재귀적으로 생성합니다.

    매개변수:
        start_pt, end_pt: FreeCAD.Vector
        depth: 재귀 depth

    반환value:
        list: FreeCAD.Vector 점 목록
    """
    if depth == 0:
        return [start_pt, end_pt]

    # 시점에서 end_pt으로의 direction과 length
    direction = end_pt.sub(start_pt)
    length = direction.Length

    # 3등분점
    p1 = FreeCAD.Vector(
        start_pt.x + direction.x / 3,
        start_pt.y + direction.y / 3,
        start_pt.z + direction.z / 3,
    )
    p2 = FreeCAD.Vector(
        start_pt.x + 2 * direction.x / 3,
        start_pt.y + 2 * direction.y / 3,
        start_pt.z + 2 * direction.z / 3,
    )

    # tri형 꼭짓점 (perpendicular direction으로 돌출)
    # XY 평면에서 perpendicular direction 계산
    perpendicular = FreeCAD.Vector(-direction.y, direction.x, 0)
    if perpendicular.Length > 0:
        perpendicular = perpendicular.normalize()
    height = length / 3 * Math.sqrt(3) / 2  # triangle height

    triangle_tip = FreeCAD.Vector(
        (p1.x + p2.x) / 2 + perpendicular.x * height,
        (p1.y + p2.y) / 2 + perpendicular.y * height,
        (p1.z + p2.z) / 2 + perpendicular.z * height,
    )

    # 재귀: 4구간으로 분할
    points = []
    points.extend(create_koch_points(start_pt, p1, depth - 1))
    points.extend(create_koch_points(p1, triangle_tip, depth - 1)[1:])
    points.extend(create_koch_points(triangle_tip, p2, depth - 1)[1:])
    points.extend(create_koch_points(p2, end_pt, depth - 1)[1:])

    return points


# ============================================================
# 3. 반복적 structure 생성
# ============================================================

def quadtree_3d(center, size, depth=4, angle=25.0):
    """
    3D quadtree(Quadtree) structure를 재귀적으로 생성합니다.
    나무 branch가 4개로 갈라지는 structure입니다.

    매개변수:
        center: FreeCAD.Vector 나무 기준점
        size: branch length (mm)
        depth: 재귀 depth
        angle: branch 분기 angle (도)

    반환value:
        Part.Shape: 3D quadtree structure
    """
    print(f"  3D quadtree 생성 - depth: {depth}")

    combined = None

    def _create_branch(start, length, depth_remain, angle_radian):
        if depth_remain <= 0 or length < 0.5:
            return None

        # 위쪽 direction (Zaxis)
        end_pt = FreeCAD.Vector(start.x, start.y, start.z + length)

        diameter = max(0.3, length * 0.08)
        try:
            branch = Part.makeCylinder(diameter, length, start, FreeCAD.Vector(0, 0, 1))
        except Exception:
            return None

        current = branch

        # 4개 branch로 분기
        branch_length = length * 0.65
        branch_dist = length * 0.4

        for i in range(4):
            rot_angle = i * 90.0 + 45.0  # 4direction, 45도 offset_val

            # branch_point
            branch_point = FreeCAD.Vector(end_pt.x, end_pt.y, end_pt.z)

            # 회전된 direction 벡터
            dx = Math.cos(angle_radian) * Math.cos(rot_angle * Math.pi / 180.0)
            dy = Math.cos(angle_radian) * Math.sin(rot_angle * Math.pi / 180.0)
            dz = Math.sin(angle_radian)

            sub_end = FreeCAD.Vector(
                branch_point.x + dx * branch_length,
                branch_point.y + dy * branch_length,
                branch_point.z + dz * branch_length,
            )

            try:
                direction = sub_end.sub(branch_point).normalize()
                sub_diameter = max(0.2, branch_length * 0.06)
                sub_branch = Part.makeCylinder(sub_diameter, branch_length, branch_point, direction)
                current = current.fuse(sub_branch)
            except Exception:
                pass

            # 재귀
            sub = _create_branch(sub_end, branch_length * 0.65, depth_remain - 1, angle_radian * 0.8)
            if sub is not None:
                try:
                    current = current.fuse(sub)
                except Exception:
                    pass

        return current

    combined = _create_branch(center, size, depth, angle * Math.pi / 180.0)

    if combined is None:
        return Part.makeCylinder(1, 1, center)

    print(f"  quadtree 완료 - volume: {combined.Volume:.2f} mm³")
    return combined


def create_mandelbrot_structure(center, size, depth=4):
    """
    mandelbrot 집합 form_type의 프랙탈 structure를 생성합니다.
    자기 유사적 격자 structure를 만듭니다.

    매개변수:
        center: FreeCAD.Vector center position
        size: combined structure size (mm)
        depth: 재귀 depth

    반환value:
        Part.Shape: mandelbrot 유사 structure
    """
    print(f"  mandelbrot structure 생성 - depth: {depth}")

    def _create_structure(center_coord, current_size, current_depth):
        if current_depth <= 0 or current_size < 0.5:
            return None

        half = current_size / 2
        box = Part.makeBox(
            current_size * 0.3, current_size * 0.3, current_size * 0.3,
            FreeCAD.Vector(
                center_coord.x - current_size * 0.15,
                center_coord.y - current_size * 0.15,
                center_coord.z - current_size * 0.15,
            )
        )

        current = box
        sub_size = current_size * 0.35

        # 5direction에 sub structure (center +4direction)
        position_list = [
            (0, 0, 0),      # center
            (1, 0, 0),      # +X
            (-1, 0, 0),     # -X
            (0, 1, 0),      # +Y
            (0, -1, 0),     # -Y
        ]

        for dx, dy, dz in position_list:
            sub_center = FreeCAD.Vector(
                center_coord.x + dx * sub_size,
                center_coord.y + dy * sub_size,
                center_coord.z + dz * sub_size,
            )
            sub = _create_structure(sub_center, sub_size, current_depth - 1)
            if sub is not None:
                try:
                    current = current.fuse(sub)
                except Exception:
                    pass

        return current

    combined = _create_structure(center, size, depth)

    if combined is None:
        return Part.makeBox(size * 0.3, size * 0.3, size * 0.3,
                            FreeCAD.Vector(center.x - size * 0.15,
                                           center.y - size * 0.15,
                                           center.z - size * 0.15))

    print(f"  mandelbrot structure 완료 - volume: {combined.Volume:.2f} mm³")
    return combined


def create_maze_fractal(center, size, depth=3):
    """
    미로 form_type의 프랙탈 structure를 생성합니다.
    규칙적으로 채워진 격자에서 무작위 wall을 제거합니다.

    매개변수:
        center: FreeCAD.Vector center position
        size: combined size (mm)
        depth: 프랙탈 depth (격자 수 = 2^depth + 1)

    반환value:
        Part.Shape: 미로 프랙탈 structure
    """
    import random
    random.seed(42)

    grid_count = 2 ** depth + 1
    cell_size = size / grid_count
    wall_height = cell_size * 0.8

    print(f"  미로 프랙탈 생성")
    print(f"    격자 수: {grid_count}x{grid_count}, 셀 size: {cell_size:.2f}mm")

    combined = None

    for x in range(grid_count):
        for y in range(grid_count):
            # 홀수 좌표: 통로, 짝수 좌표: wall
            if x % 2 == 0 or y % 2 == 0:
                # wall
                pt_x = center.x - size / 2 + x * cell_size
                pt_y = center.y - size / 2 + y * cell_size

                wall = Part.makeBox(cell_size, cell_size, wall_height,
                                  FreeCAD.Vector(pt_x, pt_y, center.z))

                if combined is None:
                    combined = wall
                else:
                    combined = combined.fuse(wall)

    print(f"  미로 프랙탈 완료 - volume: {combined.Volume:.2f} mm³" if combined else "  미로 프랙탈 FAIL")
    return combined if combined else Part.makeBox(1, 1, 1)


# ============================================================
# 4. 프랙탈 analysis_val
# ============================================================

def approximate_fractal_dimension(scale_list, cell_count_list):
    """
    프랙탈 차원을 박스 카운팅 방법으로 근사합니다.

    매개변수:
        scale_list: 셀 size 목록 (역수 사용)
        cell_count_list: 각 스케일에서의 셀 수

    반환value:
        float: 근사된 프랙탈 차원
    """
    if len(scale_list) < 2 or len(cell_count_list) < 2:
        return 0.0

    # 로그-로그 회귀
    log_scale = [Math.log(1.0 / s) for s in scale_list if s > 0]
    log_count = [Math.log(c) for c in cell_count_list if c > 0]

    if len(log_scale) < 2:
        return 0.0

    # 최소제곱법
    n = len(log_scale)
    sum_x = sum(log_scale)
    sum_y = sum(log_count)
    sum_xy = sum(x * y for x, y in zip(log_scale, log_count))
    sum_x2 = sum(x ** 2 for x in log_scale)

    denominator = n * sum_x2 - sum_x ** 2
    if abs(denominator) < 1e-10:
        return 0.0

    fractal_dim = (n * sum_xy - sum_x * sum_y) / denominator
    return fractal_dim


def analyze_fractal_structure(structure):
    """
    프랙탈 structure의 기본 analysis_val을 수row_val합니다.

    매개변수:
        structure: analysis_val할 Part.Shape

    반환value:
        dict: analysis_val result
    """
    bb = structure.BoundBox
    bbox_volume = bb.XLength * bb.YLength * bb.ZLength

    return {
        " volume": structure.Volume,
        " area_val": structure.Area,
        " bbox": f"{bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f}",
        " volume_density": structure.Volume / bbox_volume if bbox_volume > 0 else 0,
        " specific_area": structure.Area / structure.Volume if structure.Volume > 0 else 0,
    }


# ============================================================
# 5. 메인 실row_val 함수
# ============================================================

def main_run():
    """
    프랙탈 structure 메인 실row_val 함수입니다.
    코르크스프레임, 반복 structure를 순차적으로 시연합니다.
    """
    print("=" * 60)
    print("  Part 4 - 프랙탈 structure")
    print("  프랙탈 알고리즘을 이용한 structure 생성")
    print("=" * 60)

    # ----------------------------------------------------------
    # 시나리오 1: 코르크스프레임 유사 structure
    # ----------------------------------------------------------
    print("\n[시나리오 1] 코르크스프레임 유사 structure")
    print("-" * 50)

    koch_structure = create_koch_frame(
        start_pt=FreeCAD.Vector(0, 0, 0),
        end_pt=FreeCAD.Vector(10, 0, 40),
        depth=4,
    )
    analysis_1 = analyze_fractal_structure(koch_structure)
    print(f"\n  [코르크스프레임 analysis_val]")
    for key, value in analysis_1.items():
        print(f"    {key}: {value}")

    # 코르크스 곡line
    print("\n  코르크스 곡line:")
    koch_curve = create_koch_curve(
        FreeCAD.Vector(0, 0, 0),
        FreeCAD.Vector(100, 0, 0),
        depth=4,
    )
    analysis_1b = analyze_fractal_structure(koch_curve)
    print(f"    volume: {analysis_1b[' volume']:.2f} mm³")

    # ----------------------------------------------------------
    # 시나리오 2: 3D quadtree
    # ----------------------------------------------------------
    print("\n[시나리오 2] 3D quadtree structure")
    print("-" * 50)

    quadtree = quadtree_3d(
        center=FreeCAD.Vector(0, 0, 0),
        size=20.0,
        depth=3,
        angle=25.0,
    )
    analysis_2 = analyze_fractal_structure(quadtree)
    print(f"\n  [3D quadtree analysis_val]")
    for key, value in analysis_2.items():
        print(f"    {key}: {value}")

    # ----------------------------------------------------------
    # 시나리오 3: mandelbrot structure
    # ----------------------------------------------------------
    print("\n[시나리오 3] mandelbrot 유사 structure")
    print("-" * 50)

    mandelbrot = create_mandelbrot_structure(
        center=FreeCAD.Vector(0, 0, 0),
        size=40.0,
        depth=3,
    )
    analysis_3 = analyze_fractal_structure(mandelbrot)
    print(f"\n  [mandelbrot structure analysis_val]")
    for key, value in analysis_3.items():
        print(f"    {key}: {value}")

    # ----------------------------------------------------------
    # 시나리오 4: 프랙탈 box structure
    # ----------------------------------------------------------
    print("\n[시나리오 4] 프랙탈 box structure")
    print("-" * 50)

    fractal_box = create_fractal_box(
        center=FreeCAD.Vector(0, 0, 0),
        size=30.0,
        depth=0,
        max_depth=3,
    )
    analysis_4 = analyze_fractal_structure(fractal_box)
    print(f"\n  [프랙탈 box analysis_val]")
    for key, value in analysis_4.items():
        print(f"    {key}: {value}")

    # ----------------------------------------------------------
    # 시나리오 5: 프랙탈 차원 근사
    # ----------------------------------------------------------
    print("\n[시나리오 5] 프랙탈 차원 근사")
    print("-" * 50)

    # 코르크스 곡line 이론적 차원: ~1.2619
    scale_list = [0.1, 0.05, 0.025, 0.0125]
    cell_count_list = [10, 40, 160, 640]  # 4^n ratio_val

    estimated_dim = approximate_fractal_dimension(scale_list, cell_count_list)
    print(f"  추정 프랙탈 차원: {estimated_dim:.4f}")
    print(f"  이론적 코르크스 곡line 차원: 1.2619")

    # 프랙탈 box 이론적 차원: ~2.7268
    scale_list_box = [0.2, 0.1, 0.05, 0.025]
    cell_count_list_box = [5, 25, 125, 625]  # 5^n ratio_val

    estimated_dim_box = approximate_fractal_dimension(scale_list_box, cell_count_list_box)
    print(f"  추정 프랙탈 차원 (structure): {estimated_dim_box:.4f}")

    # ----------------------------------------------------------
    # FreeCAD doc에 result 표시
    # ----------------------------------------------------------
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("프랙탈_structure")

        # 코르크스프레임
        obj1 = doc.addObject("Part::Feature", "코르크스프레임")
        obj1.Shape = koch_structure

        # 코르크스 곡line (moved)
        obj2 = doc.addObject("Part::Feature", "koch_curve")
        curve_moved = koch_curve.copy()
        curve_moved.translate(FreeCAD.Vector(20, 0, 0))
        obj2.Shape = curve_moved

        # quadtree (moved)
        obj3 = doc.addObject("Part::Feature", "3D_quadtree")
        tree_moved = quadtree.copy()
        tree_moved.translate(FreeCAD.Vector(50, 0, 0))
        obj3.Shape = tree_moved

        # mandelbrot (moved)
        obj4 = doc.addObject("Part::Feature", "create_mandelbrot_structure")
        mandel_moved = mandelbrot.copy()
        mandel_moved.translate(FreeCAD.Vector(100, 0, 0))
        obj4.Shape = mandel_moved

        # 프랙탈 box (moved)
        obj5 = doc.addObject("Part::Feature", "fractal_box")
        box_moved = fractal_box.copy()
        box_moved.translate(FreeCAD.Vector(150, 0, 0))
        obj5.Shape = box_moved

        doc.recompute()
        print("\n  FreeCAD doc에 result가 추가되었습니다.")
        print("  브라우저에서 각 프랙탈 structure를 check하세요.")
    except Exception as e:
        print(f"\n  FreeCAD doc 작업 FAIL: {e}")

    print("\n" + "=" * 60)
    print("  프랙탈 structure 생성 완료!")
    print("=" * 60)


# ============================================================
# 스크립트 실row_val 진입점
# ============================================================
if __name__ == "__main__":
    main_run()
else:
    main_run()

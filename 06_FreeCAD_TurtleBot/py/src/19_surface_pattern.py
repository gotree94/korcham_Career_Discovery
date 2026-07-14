# -*- coding: utf-8 -*-
"""
Part 4 - 알고리즘 기반 설계
第19節: 곡면 pattern

실row_val 방법:
  FreeCAD 메뉴 > 매크로 > 매크로 실row_val... > 이 파일 line택 > 실row_val

목적:
  곡면 위에 pattern을 생성하는 알고리즘을 구현합니다.
  - 벌집 pattern
  - 물결 pattern
  - bump pattern
"""

import FreeCAD
import Part
import Math
import random


# ============================================================
# 1. 벌집 pattern (Hexagonal Pattern)
# ============================================================

def create_hexagon(center_x, center_y, radius, thickness=0.5, height=2.0):
    """
    단일 육각형을 생성합니다.

    매개변수:
        center_x, center_y: 육각형 center 좌표 (mm)
        radius: 육각형 외접 원 radius (mm)
        두께: wall 두께 (mm)
        height: 육각형 height (mm)

    반환value:
        Part.Shape: 육각형 셰이프
    """
    # 외부 육각형
    outer_pts = []
    inner_pts = []
    for i in range(6):
        angle = i * 60.0  # 도
        rad = angle * Math.pi / 180.0

        outer_pts.append(FreeCAD.Vector(
            center_x + radius * Math.cos(rad),
            center_y + radius * Math.sin(rad),
            0,
        ))

        inner_radius = radius - thickness
        if inner_radius < 0:
            inner_radius = 0
        inner_pts.append(FreeCAD.Vector(
            center_x + inner_radius * Math.cos(rad),
            center_y + inner_radius * Math.sin(rad),
            0,
        ))

    # 육각형 와이어 생성
    outer_wire = Part.makePolygon(outer_pts + [outer_pts[0]])
    outer_face = Part.Face(outer_wire)

    if radius - thickness > 0.1:
        inner_wire = Part.makePolygon(inner_pts + [inner_pts[0]])
        inner_face = Part.Face(inner_wire)
        profile = outer_face.cut(inner_face)
    else:
        profile = outer_face

    # height 적용 (익스트루드)
    result = profile.extrude(FreeCAD.Vector(0, 0, height))
    return result


def create_honeycomb_pattern(start_x, start_y, cols, rows, radius=5.0,
                    thickness=0.5, height=2.0, offset_rows=True):
    """
    벌집(육각형) 격자 pattern을 생성합니다.

    매개변수:
        start_x, start_y: pattern start 좌표
        cols: width direction 육각형 수
        rows: depth direction 육각형 수
        radius: 육각형 size (mm)
        두께: wall 두께 (mm)
        height: 육각형 height (mm)
        offset_rows: 홀수 줄을 offset_val할지 여부 (진짜 벌집 form_type)

    반환value:
        Part.Shape: 벌집 pattern 셰이프
    """
    print(f"  벌집 pattern 생성")
    print(f"    배col_data: {cols} x {rows} = {cols * rows}개")
    print(f"    radius: {radius}mm, 두께: {thickness}mm, height: {height}mm")

    total_pattern = None
    created_count = 0

    # 육각형 spacing 계산
    horiz_spacing = radius * Math.sqrt(3)  # 육각형 수평 spacing
    vert_spacing = radius * 1.5            # 육각형 perpendicular spacing

    for row in range(rows):
        for col in range(cols):
            # Y 좌표 계산
            current_y = start_y + row * vert_spacing

            # 홀수 줄 offset_val
            current_x = start_x
            if offset_rows and row % 2 == 1:
                current_x += horiz_spacing / 2

            current_x += col * horiz_spacing

            try:
                hexagon = create_hexagon(current_x, current_y, radius, thickness, height)
                if total_pattern is None:
                    total_pattern = hexagon
                else:
                    total_pattern = total_pattern.fuse(hexagon)
                created_count += 1
            except Exception as e:
                print(f"    육각형 생성 FAIL ({col}, {row}): {e}")

    print(f"    생성된 육각형: {created_count}개")

    if total_pattern is None:
        return Part.makeBox(1, 1, 1)

    print(f"    pattern volume: {total_pattern.Volume:.2f} mm³")
    return total_pattern


def create_honeycomb_on_surface(start_x, start_y, cols, rows, radius=5.0,
                    thickness=0.5, surface_height=20.0, surface_type="파라볼라"):
    """
    곡면 위에 벌집 pattern을 배치합니다.

    매개변수:
        start_x, start_y: pattern start 좌표
        cols, rows: 육각형 수
        radius: 육각형 size (mm)
        두께: wall 두께 (mm)
        surface_height: 곡면의 최대 height (mm)
        surface_type: "파라볼라", "사인", "원추"

    반환value:
        Part.Shape: 곡면 위 벌집 pattern
    """
    print(f"  곡면 위 벌집 pattern 생성 - form_type: {surface_type}")

    total_pattern = None
    horiz_spacing = radius * Math.sqrt(3)
    vert_spacing = radius * 1.5

    total_x = cols * horiz_spacing
    total_y = rows * vert_spacing

    for row in range(rows):
        for col in range(cols):
            current_y = start_y + row * vert_spacing
            current_x = start_x
            if row % 2 == 1:
                current_x += horiz_spacing / 2
            current_x += col * horiz_spacing

            # 정규화된 좌표 (0 ~ 1)
            if total_x > 0:
                norm_x = (current_x - start_x) / total_x
            else:
                norm_x = 0
            if total_y > 0:
                norm_y = (current_y - start_y) / total_y
            else:
                norm_y = 0

            # 곡면 height 계산
            if surface_type == "파라볼라":
                # 원점 center 파라볼라: z = h * (1 - r²)
                r_squared = (norm_x - 0.5) ** 2 + (norm_y - 0.5) ** 2
                current_height = surface_height * max(0, 1.0 - 4.0 * r_squared)
            elif surface_type == "사인":
                # 사인 파형: z = h * sin(π*x) * sin(π*y)
                current_height = surface_height * (
                    Math.sin(Math.pi * norm_x) * Math.sin(Math.pi * norm_y)
                )
            elif surface_type == "원추":
                # 원추형: z = h * (1 - r)
                r = ((norm_x - 0.5) ** 2 + (norm_y - 0.5) ** 2) ** 0.5
                current_height = surface_height * max(0, 1.0 - 2.0 * r)
            else:
                current_height = surface_height * 0.5

            try:
                hexagon = create_hexagon(current_x, current_y, radius, thickness, max(0.5, current_height))
                if total_pattern is None:
                    total_pattern = hexagon
                else:
                    total_pattern = total_pattern.fuse(hexagon)
            except Exception:
                pass

    if total_pattern is None:
        return Part.makeBox(1, 1, 1)

    print(f"    곡면 벌집 pattern 완료 - volume: {total_pattern.Volume:.2f} mm³")
    return total_pattern


# ============================================================
# 2. 물결 pattern (Wave Pattern)
# ============================================================

def create_wave_curve(start_x, end_x, amplitude=5.0, wavelength=20.0, point_count=100, Z=0):
    """
    2D 물결 곡line을 생성합니다.

    매개변수:
        start_x, end_x: 곡line의 Xaxis 범위
        amplitude: 물결 amplitude (mm)
        wavelength: 물결 wavelength (mm)
        point_count: 곡line을 구성하는 점의 수
        Z: Zaxis 좌표

    반환value:
        list: FreeCAD.Vector 점 목록
    """
    points = []
    for i in range(point_count):
        t = i / (point_count - 1)
        x = start_x + t * (end_x - start_x)
        y = amplitude * Math.sin(2 * Math.pi * x / wavelength)
        points.append(FreeCAD.Vector(x, y, Z))
    return points


def create_wave_pattern(start_x, start_y, width=100.0, depth=60.0,
                    amplitude=5.0, wavelength=20.0, line_spacing=8.0,
                    line_thickness=1.0, height=3.0):
    """
    물결 pattern을 생성합니다.
    여러 개의 물결 곡line을 겹쳐서 pattern을 만듭니다.

    매개변수:
        start_x, start_y: pattern start 좌표
        width: pattern width size (mm)
        depth: pattern depth size (mm)
        amplitude: 물결 amplitude (mm)
        wavelength: 물결 wavelength (mm)
        line_spacing: 물결 line 간 spacing (mm)
        line_thickness: 물결 line 두께 (mm)
        height: 물결 line height (mm)

    반환value:
        Part.Shape: 물결 pattern 셰이프
    """
    print(f"  물결 pattern 생성")
    print(f"    size: {width} x {depth} mm")
    print(f"    amplitude: {amplitude}mm, wavelength: {wavelength}mm")

    total_pattern = None
    line_count = int(depth / line_spacing) + 1

    for i in range(line_count):
        current_y = start_y + i * line_spacing

        # 각 줄의 phase diff (자연스러운 물결 효과)
        phase = i * 30.0  # 도

        points = []
        point_count = 200
        for j in range(point_count):
            t = j / (point_count - 1)
            x = start_x + t * width
            y = current_y + amplitude * Math.sin(2 * Math.pi * x / wavelength + phase * Math.pi / 180.0)
            z = 0
            points.append(FreeCAD.Vector(x, y, z))

        # 점 목록으로 와이어 생성
        try:
            wire = Part.makePolygon(points)
            # 와이어를 두께 있는 form_type로 변환 (스위프)
            end_pt_val = points[-1]
            perpendicular_direction = FreeCAD.Vector(0, 0, height)

            # 각 점에 작은 원을 만들어 스위프
            circle_profile = None
            for k in range(0, len(points), max(1, len(points) // 20)):
                pt = points[k]
                small_circle = Part.makeCircle(line_thickness / 2, pt, FreeCAD.Vector(0, 0, 1))
                if circle_profile is None:
                    circle_profile = small_circle
                else:
                    circle_profile = circle_profile.fuse(small_circle)

            # 간단한 rod으로 대체
            rod = None
            for k in range(len(points) - 1):
                seg = Part.makeLine((points[k], points[k + 1]))
                circular_rod = seg.makePipe(line_thickness / 2)
                if rod is None:
                    rod = circular_rod
                else:
                    rod = rod.fuse(circular_rod)

            if rod is not None:
                if total_pattern is None:
                    total_pattern = rod
                else:
                    total_pattern = total_pattern.fuse(rod)
        except Exception as e:
            print(f"    물결 line {i} 생성 FAIL: {e}")

    if total_pattern is None:
        # FAIL 시 간단한 rod으로 대체
        print("    상세 물결 생성 FAIL - 단순화된 물결로 대체")
        return create_wave_simple(start_x, start_y, width, depth, amplitude, wavelength, line_spacing, line_thickness, height)

    print(f"    물결 pattern 완료 - volume: {total_pattern.Volume:.2f} mm³")
    return total_pattern


def create_wave_simple(start_x, start_y, width=100.0, depth=60.0,
                    amplitude=5.0, wavelength=20.0, line_spacing=8.0,
                    line_thickness=1.0, height=3.0):
    """
    단순화된 물결 pattern을 생성합니다.
    pipe_val 스위프 없이 실린더 seg먼트로 물결을 표현합니다.

    매개변수:
        create_wave_pattern과 동일

    반환value:
        Part.Shape: 단순화된 물결 pattern
    """
    print(f"  단순화된 물결 pattern 생성")

    total_pattern = None
    line_count = int(depth / line_spacing) + 1

    for i in range(line_count):
        current_y = start_y + i * line_spacing
        phase = i * 30.0

        segment_count = 50
        for j in range(segment_count):
            t1 = j / segment_count
            t2 = (j + 1) / segment_count

            x1 = start_x + t1 * width
            x2 = start_x + t2 * width
            y1 = current_y + amplitude * Math.sin(2 * Math.pi * x1 / wavelength + phase * Math.pi / 180.0)
            y2 = current_y + amplitude * Math.sin(2 * Math.pi * x2 / wavelength + phase * Math.pi / 180.0)

            start_pt = FreeCAD.Vector(x1, y1, 0)
            end_pt = FreeCAD.Vector(x2, y2, 0)
            seg_length = start_pt.distanceToPoint(end_pt)

            if seg_length < 0.001:
                continue

            direction = end_pt.sub(start_pt).normalize()

            try:
                seg = Part.makeCylinder(
                    line_thickness / 2, seg_length,
                    start_pt, direction
                )
                if total_pattern is None:
                    total_pattern = seg
                else:
                    total_pattern = total_pattern.fuse(seg)
            except Exception:
                pass

    if total_pattern is None:
        return Part.makeBox(width, depth, height)

    print(f"    단순 물결 완료 - volume: {total_pattern.Volume:.2f} mm³")
    return total_pattern


def create_wave_surface(width=100.0, depth=80.0, resolution=50,
                      amplitude=8.0, wavelength_x=30.0, wavelength_y=25.0, thickness=1.0):
    """
    물결 모양의 서피스(표면)를 생성합니다.

    매개변수:
        width: 서피스 width size (mm)
        depth: 서피스 depth size (mm)
        resolution: 메시 resolution
        amplitude: 물결 amplitude (mm)
        wavelength_x: Xaxis direction wavelength (mm)
        wavelength_y: Yaxis direction wavelength (mm)
        두께: 서피스 두께 (mm)

    반환value:
        Part.Shape: 물결 서피스
    """
    print(f"  물결 서피스 생성 - resolution: {resolution}x{resolution}")

    # 점 격자로 물결 서피스 생성
    point_grid = []
    for i in range(resolution + 1):
        row_val = []
        for j in range(resolution + 1):
            x = i * width / resolution
            y = j * depth / resolution
            z = (amplitude * Math.sin(2 * Math.pi * x / wavelength_x) *
                 Math.sin(2 * Math.pi * y / wavelength_y))
            row_val.append(FreeCAD.Vector(x, y, z))
        point_grid.append(row_val)

    # tri형 메시로 서피스 구성
    faces = []
    for i in range(resolution):
        for j in range(resolution):
            p1 = point_grid[i][j]
            p2 = point_grid[i + 1][j]
            p3 = point_grid[i + 1][j + 1]
            p4 = point_grid[i][j + 1]

            try:
                tri1 = Part.Face(Part.makePolygon([p1, p2, p3, p1]))
                tri2 = Part.Face(Part.makePolygon([p1, p3, p4, p1]))
                faces.append(tri1)
                faces.append(tri2)
            except Exception:
                pass

    if not faces:
        return Part.makeBox(width, depth, thickness)

    # 합침
    combined = faces[0]
    for f in faces[1:]:
        try:
            combined = combined.fuse(f)
        except Exception:
            pass

    # 두께 적용 (위쪽으로 moved하여 병합)
    try:
        top_part = combined.copy()
        top_part.translate(FreeCAD.Vector(0, 0, thickness))
        result = combined.fuse(top_part)
    except Exception:
        result = combined

    print(f"    물결 서피스 완료 - volume: {result.Volume:.2f} mm³")
    return result


# ============================================================
# 3. bump pattern (Bump Pattern)
# ============================================================

def create_bump_pattern(base_face_size=100.0, bump_diameter=5.0, bump_height=3.0,
                    grid_count=8, spacing=12.0, form_type="원뿔", random_height=False):
    """
    bump(boss/dimple) pattern을 생성합니다.
    표면 위에 규칙적으로 bump를 배치합니다.

    매개변수:
        base_face_size: 기본 판 size (mm)
        bump_diameter: bump 직경 (mm)
        bump_height: bump height (mm)
        grid_count: 격자당 bump 수
        spacing: bump 간 spacing (mm)
        form_type: bump form_type - "원뿔", "구", "실린더", "피라미드"
        random_height: height를 무작위로 변경할지 여부

    반환value:
        Part.Shape: bump pattern이 적용된 셰이프
    """
    print(f"  bump pattern 생성")
    print(f"    form_type: { form_type}, 격자: {grid_count}x{grid_count}")
    print(f"    bump diameter: {bump_diameter}mm, height: {bump_height}mm")

    # 기본 판 생성
    start_position = FreeCAD.Vector(0, 0, 0)
    substrate = Part.makeBox(base_face_size, base_face_size, 1.0, start_position)

    total_pattern = substrate

    for i in range(grid_count):
        for j in range(grid_count):
            # bump position
            x = spacing / 2 + i * spacing
            y = spacing / 2 + j * spacing
            z = 1.0  # substrate 위

            # height 결정
            current_height = bump_height
            if random_height:
                current_height = bump_height * (0.5 + random.random() * 1.0)

            center = FreeCAD.Vector(x, y, z)

            try:
                if form_type == "원뿔":
                    # 원뿔형 bump: bottom_pts radius에서 top_pt 점으로
                    bump = Part.makeCone(
                        bump_diameter / 2, 0.5, current_height,
                        center, FreeCAD.Vector(0, 0, 1)
                    )
                elif form_type == "구":
                    # 반구형 bump
                    bump = Part.makeSphere(
                        bump_diameter / 2,
                        FreeCAD.Vector(x, y, z + bump_diameter / 4)
                    )
                elif form_type == "실린더":
                    # 원통형 bump
                    bump = Part.makeCylinder(
                        bump_diameter / 2, current_height,
                        center, FreeCAD.Vector(0, 0, 1)
                    )
                elif form_type == "피라미드":
                    # 사각 피라미드
                    bottom_pts = [
                        FreeCAD.Vector(x - bump_diameter / 2, y - bump_diameter / 2, z),
                        FreeCAD.Vector(x + bump_diameter / 2, y - bump_diameter / 2, z),
                        FreeCAD.Vector(x + bump_diameter / 2, y + bump_diameter / 2, z),
                        FreeCAD.Vector(x - bump_diameter / 2, y + bump_diameter / 2, z),
                    ]
                    top_pt = FreeCAD.Vector(x, y, z + current_height)

                    # 4개 tri면 + 밑면
                    faces = []
                    # 밑면
                    faces.append(Part.Face(Part.makePolygon(bottom_pts + [bottom_pts[0]])))
                    # 옆면
                    for k in range(4):
                        tri = [bottom_pts[k], bottom_pts[(k + 1) % 4], top_pt]
                        faces.append(Part.Face(Part.makePolygon(tri + [tri[0]])))

                    bump = faces[0]
                    for f in faces[1:]:
                        bump = bump.fuse(f)
                else:
                    bump = Part.makeCylinder(
                        bump_diameter / 2, current_height,
                        center, FreeCAD.Vector(0, 0, 1)
                    )

                total_pattern = total_pattern.fuse(bump)
            except Exception as e:
                print(f"    bump ({i},{j}) 생성 FAIL: {e}")

    print(f"    bump pattern 완료 - volume: {total_pattern.Volume:.2f} mm³")
    return total_pattern


def create_circular_bump_pattern(diameter=80.0, bump_diameter=4.0, bump_height=2.5,
                    ring_count=5, bumps_per_ring=12, form_type="원뿔"):
    """
    원형 배col_data로 bump pattern을 생성합니다.

    매개변수:
        diameter: 원형 substrate 직경 (mm)
        bump_diameter: bump 직경 (mm)
        bump_height: bump height (mm)
        ring_count: 원형 고리 수
        bumps_per_ring: 각 고리의 bump 수
        form_type: bump form_type

    반환value:
        Part.Shape: 원형 bump pattern
    """
    print(f"  원형 bump pattern 생성")
    print(f"    substrate diameter: {diameter}mm, ring 수: {ring_count}")

    # 원형 substrate
    substrate = Part.makeCylinder(diameter / 2, 1.0)

    total_pattern = substrate

    for ring in range(1, ring_count + 1):
        current_radius = (diameter / 2) * ring / (ring_count + 1)
        current_bump_count = max(4, int(bumps_per_ring * ring / ring_count))

        for i in range(current_bump_count):
            angle = i * 360.0 / current_bump_count
            rad = angle * Math.pi / 180.0

            x = current_radius * Math.cos(rad)
            y = current_radius * Math.sin(rad)
            z = 1.0

            center = FreeCAD.Vector(x, y, z)

            try:
                if form_type == "원뿔":
                    bump = Part.makeCone(bump_diameter / 2, 0.3, bump_height,
                                          center, FreeCAD.Vector(0, 0, 1))
                elif form_type == "구":
                    bump = Part.makeSphere(bump_diameter / 2,
                                            FreeCAD.Vector(x, y, z + bump_diameter / 4))
                else:
                    bump = Part.makeCylinder(bump_diameter / 2, bump_height,
                                              center, FreeCAD.Vector(0, 0, 1))

                total_pattern = total_pattern.fuse(bump)
            except Exception:
                pass

    print(f"    원형 bump pattern 완료 - volume: {total_pattern.Volume:.2f} mm³")
    return total_pattern


# ============================================================
# 4. pattern analysis_val
# ============================================================

def analyze_pattern(pattern):
    """
    생성된 pattern의 stats_val를 analysis_val합니다.

    매개변수:
        pattern: analysis_val할 Part.Shape

    반환value:
        dict: pattern stats_val
    """
    bb = pattern.BoundBox
    bbox_volume = bb.XLength * bb.YLength * bb.ZLength

    return {
        " volume": pattern.Volume,
        " area_val": pattern.Area,
        " bbox": f"{bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f}",
        " volume_density": pattern.Volume / bbox_volume if bbox_volume > 0 else 0,
        " specific_area": pattern.Area / pattern.Volume if pattern.Volume > 0 else 0,
    }


# ============================================================
# 5. 메인 실row_val 함수
# ============================================================

def main_run():
    """
    곡면 pattern 메인 실row_val 함수입니다.
    벌집, 물결, bump pattern을 순차적으로 시연합니다.
    """
    random.seed(42)  # 재현성 확보

    print("=" * 60)
    print("  Part 4 - 곡면 pattern")
    print("  곡면 위에 pattern을 생성하는 알고리즘")
    print("=" * 60)

    # ----------------------------------------------------------
    # 시나리오 1: 벌집 pattern
    # ----------------------------------------------------------
    print("\n[시나리오 1] 벌집 pattern")
    print("-" * 50)

    # 평면 벌집 pattern
    honeycomb_flat = create_honeycomb_pattern(
        start_x=0, start_y=0,
        cols=6, rows=5,
        radius=5.0, thickness=0.5, height=3.0,
        offset_rows=True,
    )
    analysis_1 = analyze_pattern(honeycomb_flat)
    print(f"  [평면 벌집 pattern analysis_val]")
    for key, value in analysis_1.items():
        print(f"    {key}: {value}")

    # 곡면 벌집 pattern
    print("\n  곡면 벌집 pattern (파라볼라):")
    honeycomb_curved = create_honeycomb_on_surface(
        start_x=0, start_y=0,
        cols=6, rows=5,
        radius=5.0, thickness=0.5,
        surface_height=15.0, surface_type="파라볼라",
    )
    analysis_1b = analyze_pattern(honeycomb_curved)
    print(f"    volume: {analysis_1b[' volume']:.2f} mm³")
    print(f"    area_val: {analysis_1b[' area_val']:.2f} mm²")

    # ----------------------------------------------------------
    # 시나리오 2: 물결 pattern
    # ----------------------------------------------------------
    print("\n[시나리오 2] 물결 pattern")
    print("-" * 50)

    # 단순 물결
    wave_pattern = create_wave_simple(
        start_x=0, start_y=0,
        width=100.0, depth=50.0,
        amplitude=5.0, wavelength=20.0,
        line_spacing=8.0, line_thickness=1.5, height=2.0,
    )
    analysis_2 = analyze_pattern(wave_pattern)
    print(f"  [물결 pattern analysis_val]")
    for key, value in analysis_2.items():
        print(f"    {key}: {value}")

    # 물결 서피스
    print("\n  물결 서피스:")
    wave_surf = create_wave_surface(
        width=80.0, depth=60.0, resolution=30,
        amplitude=5.0, wavelength_x=25.0, wavelength_y=20.0, thickness=1.0,
    )
    analysis_2b = analyze_pattern(wave_surf)
    print(f"    volume: {analysis_2b[' volume']:.2f} mm³")
    print(f"    area_val: {analysis_2b[' area_val']:.2f} mm²")

    # ----------------------------------------------------------
    # 시나리오 3: bump pattern
    # ----------------------------------------------------------
    print("\n[시나리오 3] bump pattern")
    print("-" * 50)

    # 사각 격자 bump - 다양한 form_type
    form_type_list = ["원뿔", "구", "실린더", "피라미드"]
    for form_type in form_type_list:
        print(f"\n  >> bump form_type: {form_type}")
        bump_pattern = create_bump_pattern(
            base_face_size=60.0,
            bump_diameter=4.0,
            bump_height=2.5,
            grid_count=5,
            spacing=12.0,
            form_type=form_type,
            random_height=False,
        )
        analysis_val = analyze_pattern(bump_pattern)
        print(f"    volume: {analysis_val[' volume']:.2f} mm³, area_val: {analysis_val[' area_val']:.2f} mm²")

    # 원형 bump
    print(f"\n  >> 원형 bump pattern:")
    circ_bump = create_circular_bump_pattern(
        diameter=60.0, bump_diameter=3.5, bump_height=2.0,
        ring_count=4, bumps_per_ring=10, form_type="원뿔",
    )
    analysis_3b = analyze_pattern(circ_bump)
    print(f"    volume: {analysis_3b[' volume']:.2f} mm³, area_val: {analysis_3b[' area_val']:.2f} mm²")

    # ----------------------------------------------------------
    # FreeCAD doc에 result 표시
    # ----------------------------------------------------------
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("곡면_pattern")

        # 벌집 pattern
        obj1 = doc.addObject("Part::Feature", "벌집_pattern")
        obj1.Shape = honeycomb_flat

        # 물결 pattern (moved)
        obj2 = doc.addObject("Part::Feature", "wave_pattern")
        wave_moved = wave_pattern.copy()
        wave_moved.translate(FreeCAD.Vector(0, 70, 0))
        obj2.Shape = wave_moved

        # bump pattern (moved)
        obj3 = doc.addObject("Part::Feature", "bump_pattern")
        bump_moved = create_bump_pattern(form_type="원뿔").copy()
        bump_moved.translate(FreeCAD.Vector(120, 0, 0))
        obj3.Shape = bump_moved

        doc.recompute()
        print("\n  FreeCAD doc에 result가 추가되었습니다.")
    except Exception as e:
        print(f"\n  FreeCAD doc 작업 FAIL: {e}")

    print("\n" + "=" * 60)
    print("  곡면 pattern 생성 완료!")
    print("=" * 60)


# ============================================================
# 스크립트 실row_val 진입점
# ============================================================
if __name__ == "__main__":
    main_run()
else:
    main_run()

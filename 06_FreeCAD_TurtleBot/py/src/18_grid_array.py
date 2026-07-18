# -*- coding: utf-8 -*-
"""
Part 4 - 알고리즘 기반 설계
第18節: 해시/그리드 배col_data

실row_val 방법:
  FreeCAD 메뉴 > 매크로 > 매크로 실row_val... > 이 파일 line택 > 실row_val

목적:
  부품을 규칙적으로 배col_data하는 알고리즘을 구현합니다.
  - 직사각형 격자 배col_data
  - 원형 격자 배col_data
  - 임의 배col_data
"""

import FreeCAD
import Part
import Math
import random


# ============================================================
# 1. 직사각형 격자 배col_data
# ============================================================

def rectangular_grid_array(base_part, cols=5, rows=3,
                       x_spacing=20.0, y_spacing=20.0,
                       start_position=None, fuse_all=False):
    """
    부품을 직사각형 격자 form_type로 배col_data합니다.

    매개변수:
        base_part: 배col_data할 Part.Shape
        cols: Xaxis direction 배치 수
        rows: Yaxis direction 배치 수
        x_spacing: Xaxis direction spacing (mm)
        y_spacing: Yaxis direction spacing (mm)
        start_position: FreeCAD.Vector start position
        fuse_all: True이면 모든 부품을 하나의 셰이프로 합침

    반환value:
        Part.Shape 또는 list: 배col_data된 부품(들)
    """
    if start_position is None:
        start_position = FreeCAD.Vector(0, 0, 0)

    print(f"  직사각형 격자 배col_data 생성")
    print(f"    배col_data: {cols} x {rows} = {cols * rows}개")
    print(f"    spacing: X={x_spacing}mm, Y={y_spacing}mm")

    array_list = []
    bb = base_part.BoundBox
    part_width = bb.XLength
    part_depth = bb.YLength

    for row in range(rows):
        for col in range(cols):
            # 새 position 계산
            new_x = start_position.x + col * (part_width + x_spacing)
            new_y = start_position.y + row * (part_depth + y_spacing)
            new_z = start_position.z

            # 부품 copy 및 moved
            copy = base_part.copy()
            copy.translate(FreeCAD.Vector(new_x, new_y, new_z))
            array_list.append(copy)

    print(f"    생성된 부품 수: {len(array_list)}개")

    if fuse_all:
        total_array = array_list[0]
        for item in array_list[1:]:
            total_array = total_array.fuse(item)
        print(f"    combined 부품 합침 완료 - volume: {total_array.Volume:.2f} mm³")
        return total_array

    return array_list


def rectangular_grid_array_2d(base_part, grid_info_list, start_position=None, fuse_all=False):
    """
    2D 좌표 목록을 이용하여 부품을 자유롭게 격자에 배치합니다.

    매개변수:
        base_part: 배col_data할 Part.Shape
        grid_info_list: [(col, row), ...] 배치할 격자 좌표 목록
        start_position: FreeCAD.Vector start position
        fuse_all: True이면 하나의 셰이프로 합침

    반환value:
        Part.Shape 또는 list: 배col_data된 부품(들)
    """
    if start_position is None:
        start_position = FreeCAD.Vector(0, 0, 0)

    print(f"  2D 격자 배치 - 지정된 좌표에만 배치")
    print(f"    배치 position 수: {len(grid_info_list)}개")

    bb = base_part.BoundBox
    part_width = bb.XLength
    part_depth = bb.YLength

    array_list = []
    for col, row in grid_info_list:
        new_x = start_position.x + col * part_width
        new_y = start_position.y + row * part_depth

        copy = base_part.copy()
        copy.translate(FreeCAD.Vector(new_x, new_y, start_position.z))
        array_list.append(copy)

    if fuse_all and len(array_list) > 0:
        combined = array_list[0]
        for item in array_list[1:]:
            combined = combined.fuse(item)
        return combined

    return array_list


# ============================================================
# 2. 원형 격자 배col_data
# ============================================================

def circular_grid_array(base_part, count=8, radius=50.0,
                   center_pos=None, base_angle=0.0, vary_height=False, fuse_all=False):
    """
    부품을 원형(방사형)으로 배col_data합니다.

    매개변수:
        base_part: 배col_data할 Part.Shape
        count: 원형으로 배치할 수
        radius: 원의 radius (mm)
        center_pos: FreeCAD.Vector center 좌표
        base_angle: start angle (도, 0 = +Xaxis)
        vary_height: True이면 각 부품의 height를 서서히 변경
        fuse_all: True이면 하나의 셰이프로 합침

    반환value:
        Part.Shape 또는 list: 배col_data된 부품(들)
    """
    if center_pos is None:
        center_pos = FreeCAD.Vector(0, 0, 0)

    print(f"  원형 격자 배col_data 생성")
    print(f"    배치 수: {count}개, radius: {radius}mm")

    array_list = []
    bb = base_part.BoundBox
    angle_step = 360.0 / count if count > 0 else 0

    for i in range(count):
        # angle 계산 (rad)
        angle_deg = base_angle + i * angle_step
        angle_radian = angle_deg * Math.pi / 180.0

        # position 계산
        new_x = center_pos.x + radius * Math.cos(angle_radian)
        new_y = center_pos.y + radius * Math.sin(angle_radian)
        new_z = center_pos.z

        # height 변경 (스piral form_type)
        if vary_height:
            new_z += i * 5.0

        # 부품 copy 및 moved
        copy = base_part.copy()
        copy.translate(FreeCAD.Vector(new_x - (bb.XMin + bb.XLength / 2),
                                       new_y - (bb.YMin + bb.YLength / 2),
                                       new_z - bb.ZMin))

        # center을 기준으로 회전
        rot_axis = FreeCAD.Vector(0, 0, 1)
        rot_point = FreeCAD.Vector(new_x, new_y, new_z)
        copy.rotate(new_x, new_y, angle_deg, FreeCAD.Vector(0, 0, 1))

        array_list.append(copy)

    print(f"    생성된 부품 수: {len(array_list)}개")

    if fuse_all and len(array_list) > 0:
        combined = array_list[0]
        for item in array_list[1:]:
            combined = combined.fuse(item)
        print(f"    합침 완료 - volume: {combined.Volume:.2f} mm³")
        return combined

    return array_list


def spiral_array(base_part, count=20, base_radius=20.0,
                radius_inc=5.0, height_inc=3.0, center_pos=None, fuse_all=False):
    """
    부품을 나line형으로 배col_data합니다.

    매개변수:
        base_part: 배col_data할 Part.Shape
        count: 나line형으로 배치할 수
        base_radius: 나line의 start radius (mm)
        radius_inc: 각 단계별 radius 증가량 (mm)
        height_inc: 각 단계별 height 증가량 (mm)
        center_pos: FreeCAD.Vector center 좌표
        fuse_all: True이면 하나의 셰이프로 합침

    반환value:
        Part.Shape 또는 list: 배col_data된 부품(들)
    """
    if center_pos is None:
        center_pos = FreeCAD.Vector(0, 0, 0)

    print(f"  나line형 배col_data 생성")
    print(f"    배치 수: {count}개")
    print(f"    radius: {base_radius}mm → {base_radius + count * radius_inc}mm")

    array_list = []
    bb = base_part.BoundBox
    angle_step = 360.0 / 10  # 10회전당 360도

    for i in range(count):
        current_radius = base_radius + i * radius_inc
        current_height = center_pos.z + i * height_inc
        angle_deg = i * angle_step
        angle_radian = angle_deg * Math.pi / 180.0

        new_x = center_pos.x + current_radius * Math.cos(angle_radian)
        new_y = center_pos.y + current_radius * Math.sin(angle_radian)

        copy = base_part.copy()
        copy.translate(FreeCAD.Vector(
            new_x - (bb.XMin + bb.XLength / 2),
            new_y - (bb.YMin + bb.YLength / 2),
            current_height - bb.ZMin,
        ))

        array_list.append(copy)

    print(f"    생성된 부품 수: {len(array_list)}개")

    if fuse_all and len(array_list) > 0:
        combined = array_list[0]
        for item in array_list[1:]:
            combined = combined.fuse(item)
        return combined

    return array_list


# ============================================================
# 3. 임의 배col_data
# ============================================================

def random_array(base_part, count=10,
              range_x=(0, 100), range_y=(0, 80), range_z=(0, 50),
              seed=None, allow_overlap=True, min_distance=0.0, fuse_all=False):
    """
    부품을 임의의 position에 배치합니다.

    매개변수:
        base_part: 배col_data할 Part.Shape
        count: 배치할 수
        range_x, range_y, range_z: (최소, 최대) 배치 범위 (mm)
        seed: 랜덤 seed (재현성 확보용)
        allow_overlap: 동일 position 중복 허용 여부
        min_distance: 부품 간 최소 distance (mm)
        fuse_all: True이면 하나의 셰이프로 합침

    반환value:
        Part.Shape 또는 list: 배col_data된 부품(들)
    """
    if seed is not None:
        random.seed(seed)

    print(f"  임의 배col_data 생성")
    print(f"    배치 수: {count}개")
    print(f"    배치 범위: X[{range_x[0]}, {range_x[1]}], "
          f"Y[{range_y[0]}, {range_y[1]}], "
          f"Z[{range_z[0]}, {range_z[1]}]")

    bb = base_part.BoundBox
    part_size_x = bb.XLength
    part_size_y = bb.YLength
    part_size_z = bb.ZLength

    placed_positions = []
    array_list = []
    attempts = 0
    max_attempts = count * 100

    while len(array_list) < count and attempts < max_attempts:
        attempts += 1

        # 임의 position 생성
        new_x = random.uniform(range_x[0], range_x[1] - part_size_x)
        new_y = random.uniform(range_y[0], range_y[1] - part_size_y)
        new_z = random.uniform(range_z[0], range_z[1] - part_size_z)

        new_pos = FreeCAD.Vector(new_x, new_y, new_z)

        # 중복 검사
        if not allow_overlap:
            collision = False
            for existing_pos in placed_positions:
                if new_pos.distanceToPoint(existing_pos) < min_distance:
                    collision = True
                    break
            if collision:
                continue

        copy = base_part.copy()
        copy.translate(FreeCAD.Vector(new_x - bb.XMin, new_y - bb.YMin, new_z - bb.ZMin))

        # 임의 회전 추가
        rot_x = random.uniform(0, 360)
        rot_y = random.uniform(0, 360)
        rot_z = random.uniform(0, 360)

        center_x = new_x + part_size_x / 2
        center_y = new_y + part_size_y / 2
        center_z = new_z + part_size_z / 2

        copy.rotate(center_x, center_y, center_z, FreeCAD.Vector(1, 0, 0), rot_x)
        copy.rotate(center_x, center_y, center_z, FreeCAD.Vector(0, 1, 0), rot_y)
        copy.rotate(center_x, center_y, center_z, FreeCAD.Vector(0, 0, 1), rot_z)

        array_list.append(copy)
        placed_positions.append(new_pos)

    print(f"    성공적으로 배치된 수: {len(array_list)}개 (시도: {attempts}회)")

    if fuse_all and len(array_list) > 0:
        combined = array_list[0]
        for item in array_list[1:]:
            combined = combined.fuse(item)
        print(f"    합침 완료 - volume: {combined.Volume:.2f} mm³")
        return combined

    return array_list


def weighted_random_array(base_part, count=20,
                    range_x=(0, 100), range_y=(0, 80),
                    weight_center=None, weight_intensity=2.0,
                    seed=None, fuse_all=False):
    """
    가중치를 적용하여 특정 position에 부품을 더 밀집시킵니다.

    매개변수:
        base_part: 배col_data할 Part.Shape
        count: 배치할 수
        range_x, range_y: 배치 범위
        weight_center: (x, y) 가중치 center 좌표
        weight_intensity: center 집중 강도 (높을수록 집중)
        seed: 랜덤 seed
        fuse_all: True이면 하나의 셰이프로 합침

    반환value:
        Part.Shape 또는 list: 배col_data된 부품(들)
    """
    if seed is not None:
        random.seed(seed)
    if weight_center is None:
        weight_center = ((range_x[0] + range_x[1]) / 2, (range_y[0] + range_y[1]) / 2)

    print(f"  가중 임의 배col_data 생성")
    print(f"    배치 수: {count}개")
    print(f"    가중 center: ({weight_center[0]:.1f}, {weight_center[1]:.1f})")

    bb = base_part.BoundBox
    array_list = []

    for _ in range(count):
        while True:
            # 균등 분포 position
            x = random.uniform(range_x[0], range_x[1] - bb.XLength)
            y = random.uniform(range_y[0], range_y[1] - bb.YLength)
            z = 0

            # 가중치 기반 수락/거부
            distance = ((x - weight_center[0]) ** 2 + (y - weight_center[1]) ** 2) ** 0.5
            max_distance = ((range_x[1] - range_x[0]) ** 2 + (range_y[1] - range_y[0]) ** 2) ** 0.5
            accept_prob = max(0, 1.0 - (distance / max_distance)) ** weight_intensity

            if random.random() < accept_prob + 0.01:
                copy = base_part.copy()
                copy.translate(FreeCAD.Vector(x - bb.XMin, y - bb.YMin, z - bb.ZMin))
                array_list.append(copy)
                break

    print(f"    생성된 부품 수: {len(array_list)}개")

    if fuse_all and len(array_list) > 0:
        combined = array_list[0]
        for item in array_list[1:]:
            combined = combined.fuse(item)
        return combined

    return array_list


# ============================================================
# 4. 유틸리티 함수
# ============================================================

def array_statistics(array_list):
    """
    배col_data된 부품들의 stats_val를 계산합니다.

    매개변수:
        array_list: Part.Shape 리스트

    반환value:
        dict: stats_val info_val
    """
    if not array_list:
        return {"총 부품 수": 0}

    total_volume = sum(item.Volume for item in array_list)
    total_area = sum(item.Area for item in array_list)

    position_list = []
    for item in array_list:
        bb = item.BoundBox
        position_list.append(FreeCAD.Vector(
            bb.XMin + bb.XLength / 2,
            bb.YMin + bb.YLength / 2,
            bb.ZMin + bb.ZLength / 2,
        ))

    # 부품 간 평균 distance 계산
    total_distance = 0
    pair_count = 0
    for i in range(len(position_list)):
        for j in range(i + 1, len(position_list)):
            total_distance += position_list[i].distanceToPoint(position_list[j])
            pair_count += 1

    avg_distance = total_distance / pair_count if pair_count > 0 else 0

    # combined 바운딩 박스
    if len(array_list) > 0:
        all_x = [item.BoundBox.XMin for item in array_list] + [item.BoundBox.XMax for item in array_list]
        all_y = [item.BoundBox.YMin for item in array_list] + [item.BoundBox.YMax for item in array_list]
        all_z = [item.BoundBox.ZMin for item in array_list] + [item.BoundBox.ZMax for item in array_list]

        total_size = (
            max(all_x) - min(all_x),
            max(all_y) - min(all_y),
            max(all_z) - min(all_z),
        )
    else:
        total_size = (0, 0, 0)

    stats_val = {
        "총 부품 수": len(array_list),
        "총 volume": total_volume,
        "총 area_val": total_area,
        "평균 부품 간 distance": avg_distance,
        "combined size (XxYxZ)": total_size,
    }

    return stats_val


# ============================================================
# 5. 메인 실row_val 함수
# ============================================================

def main_run():
    """
    해시/그리드 배col_data 메인 실row_val 함수입니다.
    직사각형, 원형, 임의 배col_data을 순차적으로 시연합니다.
    """
    print("=" * 60)
    print("  Part 4 - 해시/그리드 배col_data")
    print("  부품을 규칙적으로 배col_data하는 알고리즘")
    print("=" * 60)

    # ----------------------------------------------------------
    # 기본 부품 생성
    # ----------------------------------------------------------
    print("\n  기본 부품 생성: 10x10x5 mm 박스")
    base_part = Part.makeBox(10, 10, 5)
    print(f"    volume: {base_part.Volume:.2f} mm³")

    # ----------------------------------------------------------
    # 시나리오 1: 직사각형 격자 배col_data
    # ----------------------------------------------------------
    print("\n[시나리오 1] 직사각형 격자 배col_data")
    print("-" * 50)

    # 기본 직사각형 격자
    arr_col_1 = rectangular_grid_array(
        base_part,
        cols=5, rows=4,
        x_spacing=5.0, y_spacing=5.0,
        start_position=FreeCAD.Vector(0, 0, 0),
        fuse_all=True,
    )
    stats_1 = array_statistics(rectangular_grid_array(
        base_part, cols=5, rows=4,
        x_spacing=5.0, y_spacing=5.0,
    ))
    print(f"  직사각형 격자 stats_val:")
    for key, value in stats_1.items():
        print(f"    {key}: {value}")

    # 2D 좌표 기반 배치
    print("\n  2D 좌표 기반 배치:")
    coord_list = [(0, 0), (1, 0), (2, 0), (3, 0),
                  (0, 1), (2, 1), (4, 1),
                  (1, 2), (3, 2)]
    arr_col_2 = rectangular_grid_array_2d(
        base_part, coord_list,
        start_position=FreeCAD.Vector(0, 60, 0),
        fuse_all=True,
    )
    print(f"    배치된 수: {len(coord_list)}개")

    # ----------------------------------------------------------
    # 시나리오 2: 원형 격자 배col_data
    # ----------------------------------------------------------
    print("\n[시나리오 2] 원형 격자 배col_data")
    print("-" * 50)

    # 기본 원형 배col_data
    arr_col_3 = circular_grid_array(
        base_part,
        count=8,
        radius=40.0,
        center_pos=FreeCAD.Vector(150, 50, 0),
        fuse_all=True,
    )

    # 스플 form_type 원형 배col_data
    print("\n  나line형 원형 배col_data:")
    arr_col_4 = circular_grid_array(
        base_part,
        count=12,
        radius=30.0,
        center_pos=FreeCAD.Vector(150, 130, 0),
        vary_height=True,
        fuse_all=False,
    )
    print(f"    생성된 부품 수: {len(arr_col_4)}개")

    # 나line형 배col_data
    print("\n  나line형 배col_data:")
    arr_col_5 = spiral_array(
        base_part,
        count=15,
        base_radius=10.0,
        radius_inc=3.0,
        height_inc=2.0,
        center_pos=FreeCAD.Vector(250, 50, 0),
        fuse_all=True,
    )

    # ----------------------------------------------------------
    # 시나리오 3: 임의 배col_data
    # ----------------------------------------------------------
    print("\n[시나리오 3] 임의 배col_data")
    print("-" * 50)

    # 균등 임의 배col_data
    arr_col_6 = random_array(
        base_part,
        count=15,
        range_x=(0, 100), range_y=(0, 80), range_z=(0, 30),
        seed=42,
        fuse_all=False,
    )
    print(f"  균등 임의 배col_data: {len(arr_col_6)}개 부품")

    # 가중 임의 배col_data
    arr_col_7 = weighted_random_array(
        base_part,
        count=20,
        range_x=(0, 120), range_y=(0, 80),
        weight_center=(30, 20),
        weight_intensity=3.0,
        seed=42,
        fuse_all=False,
    )
    print(f"  가중 임의 배col_data: {len(arr_col_7)}개 부품")

    # ----------------------------------------------------------
    # FreeCAD doc에 result 표시
    # ----------------------------------------------------------
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("해시그리드_배col_data")

        # 직사각형 격자
        obj1 = doc.addObject("Part::Feature", "직사각형_격자")
        obj1.Shape = arr_col_1

        # 원형 격자
        obj2 = doc.addObject("Part::Feature", "원형_격자")
        if isinstance(arr_col_3, list):
            circular_fused = arr_col_3[0]
            for item in arr_col_3[1:]:
                circular_fused = circular_fused.fuse(item)
            obj2.Shape = circular_fused
        else:
            obj2.Shape = arr_col_3

        # 나line형
        obj3 = doc.addObject("Part::Feature", "spiral_array")
        if isinstance(arr_col_5, list):
            spiral_fused = arr_col_5[0]
            for item in arr_col_5[1:]:
                spiral_fused = spiral_fused.fuse(item)
            obj3.Shape = spiral_fused
        else:
            obj3.Shape = arr_col_5

        doc.recompute()
        print("\n  FreeCAD doc에 result가 추가되었습니다.")
    except Exception as e:
        print(f"\n  FreeCAD doc 작업 FAIL: {e}")

    print("\n" + "=" * 60)
    print("  해시/그리드 배col_data 생성 완료!")
    print("=" * 60)


# ============================================================
# 스크립트 실row_val 진입점
# ============================================================
if __name__ == "__main__":
    main_run()
else:
    main_run()

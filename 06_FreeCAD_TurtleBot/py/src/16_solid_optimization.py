# -*- coding: utf-8 -*-
"""
Part 4 - 알고리즘 기반 설계
第16節: 졸리드 바디 최적화

실row_val 방법:
  FreeCAD 메뉴 > 매크로 > 매크로 실row_val... > 이 파일 line택 > 실row_val

목적:
  volume 대비 강도를 고려한 최적화 알고리즘을 구현합니다.
  - 바운딩 박스 기반 최적화
  - 불필요한 material_val 제거 알고리즘
  - structure적 efficiency 계산
"""

import FreeCAD
import Part
import Math
import random


# ============================================================
# 1. 바운딩 박스 기반 최적화
# ============================================================

def analyze_bounding_box(shape):
    """
    셰이프의 바운딩 박스를 analysis_val하여 volume efficiency을 계산합니다.

    매개변수:
        shape: analysis_val할 Part.Shape obj

    반환value:
        dict: 바운딩 박스 info_val와 efficiency 지표
    """
    bb = shape.BoundBox
    bbox_volume = bb.XLength * bb.YLength * bb.ZLength

    # 실제 셰이프 volume 계산 (간접 계산법 사용)
    actual_volume = shape.Volume

    if bbox_volume > 0:
        volume_efficiency = actual_volume / bbox_volume
    else:
        volume_efficiency = 0.0

    result = {
        " minX": bb.XMin,
        " minY": bb.YMin,
        " minZ": bb.ZMin,
        " maxX": bb.XMax,
        " maxY": bb.YMax,
        " maxZ": bb.ZMax,
        " XLength": bb.XLength,
        " YLength": bb.YLength,
        " ZLength": bb.ZLength,
        " bbox_volume": bbox_volume,
        " actual_volume": actual_volume,
        " volume_efficiency": volume_efficiency,
    }
    return result


def optimize_bounding_box(shape, margin_ratio=0.1):
    """
    셰이프를 바운딩 박스에 맞게 최적화합니다.
    불필요한 돌출부를 제거하고 더 컴팩트한 form_type로 만듭니다.

    매개변수:
        shape: 최적화할 Part.Shape obj
        margin_ratio: 바운딩 박스 대비 여유 공간 ratio_val (0.0 ~ 0.5)

    반환value:
        Part.Shape: 최적화된 셰이프
    """
    bb = shape.BoundBox

    # 여유 공간 적용한 axis소 바운딩 박스 계산
    margin_x = bb.XLength * margin_ratio
    margin_y = bb.YLength * margin_ratio
    margin_z = bb.ZLength * margin_ratio

    optimized_box = Part.makeBox(
        bb.XLength - 2 * margin_x,
        bb.YLength - 2 * margin_y,
        bb.ZLength - 2 * margin_z,
        FreeCAD.Vector(bb.XMin + margin_x, bb.YMin + margin_y, bb.ZMin + margin_z),
    )

    # 원래 셰이프와의 교차로 최적화된 form_type 생성
    try:
        result = shape.common(optimized_box)
        print(f"  바운딩 박스 최적화 완료 - axis소된 바운딩 박스로 교차 연산 수row_val")
        return result
    except Exception as e:
        print(f"  최적화 FAIL: {e}")
        return shape


# ============================================================
# 2. 불필요한 material_val 제거 알고리즘
# ============================================================

def calculate_equivalent_diameter(shape):
    """
    셰이프의 단면을 기반으로 등가 diameter을 계산합니다.
    강도 추정에 사용됩니다.

    매개변수:
        shape: analysis_val할 Part.Shape obj

    반환value:
        float: 등가 diameter (단위: mm)
    """
    area_val = shape.Area
    if area_val > 0:
        # 원형 단면의 등가 diameter: D = 2 * sqrt(A / pi)
        equiv_diameter = 2.0 * (area_val / Math.pi) ** 0.5
        return equiv_diameter
    return 0.0


def remove_material_algorithm(shape, min_thickness=1.0, void_ratio=0.3):
    """
    셰이프에서 불필요한 내부 material_val를 제거합니다.
    지정된 최소 두께 이하의 부위를 hollow 처리합니다.

    매개변수:
        shape: 원본 Part.Shape obj
        min_thickness: 유지할 최소 wall 두께 (mm)
        void_ratio: 제거할 공백 영역의 ratio_val

    반환value:
        Part.Shape: material_val가 제거된 셰이프
    """
    bb = shape.BoundBox

    # 내부 박스 생성 (material_val 제거 영역)
    inner_start_x = bb.XMin + min_thickness + (bb.XLength - 2 * min_thickness) * void_ratio * 0.5
    inner_start_y = bb.YMin + min_thickness + (bb.YLength - 2 * min_thickness) * void_ratio * 0.5
    inner_start_z = bb.ZMin + min_thickness + (bb.ZLength - 2 * min_thickness) * void_ratio * 0.5

    inner_length_x = (bb.XLength - 2 * min_thickness) * (1.0 - void_ratio)
    inner_length_y = (bb.YLength - 2 * min_thickness) * (1.0 - void_ratio)
    inner_length_z = (bb.ZLength - 2 * min_thickness) * (1.0 - void_ratio)

    # 최소 size check_val
    if inner_length_x <= 0 or inner_length_y <= 0 or inner_length_z <= 0:
        print("  경고: 최소 두께가 바운딩 박스보다 큽니다. 제거 불가.")
        return shape

    inner_box = Part.makeBox(
        inner_length_x, inner_length_y, inner_length_z,
        FreeCAD.Vector(inner_start_x, inner_start_y, inner_start_z),
    )

    # 원래 셰이프에서 내부 박스 차단 (불리안 뺄셈)
    try:
        result = shape.cut(inner_box)
        print(f"  material_val 제거 완료 - 원래 volume: {shape.Volume:.2f}mm³ → {result.Volume:.2f}mm³")
        print(f"  제거된 material_val ratio_val: {(1 - result.Volume / shape.Volume) * 100:.1f}%")
        return result
    except Exception as e:
        print(f"  material_val 제거 FAIL: {e}")
        return shape


def iterative_material_removal(shape, removal_count=3, step_void=0.1):
    """
    반복적으로 material_val를 제거하여 점진적으로 경량화합니다.

    매개변수:
        shape: 원본 Part.Shape obj
        removal_count: material_val 제거 반복 횟수
        step_void: 각 단계에서 추가할 공백 ratio_val

    반환value:
        Part.Shape: 최종 경량화된 셰이프
    """
    current_shape = shape
    print(f"  반복적 material_val 제거 start - 반복 횟수: {removal_count}")

    for i in range(removal_count):
        void_ratio = step_void * (i + 1)
        prev_volume = current_shape.Volume

        current_shape = remove_material_algorithm(
            current_shape, min_thickness=0.5, void_ratio=void_ratio
        )

        print(f"    단계 {i + 1}: 공백 {void_ratio * 100:.0f}% → volume: {current_shape.Volume:.2f}mm³")

        # volume 변화가 미미하면 조기 종료
        if prev_volume > 0 and abs(prev_volume - current_shape.Volume) / prev_volume < 0.01:
            print(f"    단계 {i + 1}에서 수렴 - 조기 종료")
            break

    return current_shape


# ============================================================
# 3. structure적 efficiency 계산
# ============================================================

def calculate_structural_efficiency(shape):
    """
    셰이프의 structure적 efficiency을 종합적으로 계산합니다.

    평가 항목:
      - volume efficiency: 실제 volume / 바운딩 박스 volume
      - area_val efficiency: area_val / volume
      - 단면 균일성: 단면 변화율
      - 종합 efficiency score_val

    매개변수:
        shape: analysis_val할 Part.Shape obj

    반환value:
        dict: structure적 efficiency 지표
    """
    bb = shape.BoundBox
    bbox_volume = bb.XLength * bb.YLength * bb.ZLength

    # 1. volume efficiency
    volume_efficiency = shape.Volume / bbox_volume if bbox_volume > 0 else 0.0

    # 2. area_val 대 volume ratio_val (specific_area - 높을수록 가벼운 structure)
    if shape.Volume > 0:
        specific_area = shape.Area / shape.Volume
    else:
        specific_area = 0.0

    # 3. form_type 계수 (공학적 form_type 복잡도 추정)
    #    완전 구형: 1.0, 긴 rod: 높은 value
    max_val = max(bb.XLength, bb.YLength, bb.ZLength)
    min_val = min(bb.XLength, bb.YLength, bb.ZLength)

    if max_val > 0:
        form_ratio = max_val / min_val
    else:
        form_ratio = 1.0

    # form_type 계수: 1에 가까울수록 balance_val 잡힌 form_type
    form_factor = 1.0 / form_ratio if form_ratio > 0 else 0.0

    # 4. 종합 efficiency score_val (0 ~ 100)
    overall_score = (
        volume_efficiency * 40       # volume efficiency 40%
        + form_factor * 30       # form_type balance_val 30%
        + min(specific_area / 10, 1.0) * 30  # specific_area score_val 30%
    )
    overall_score = min(overall_score, 100.0)

    result = {
        " volume efficiency": volume_efficiency,
        " specific_area": specific_area,
        " form_ratio": form_ratio,
        " form_factor": form_factor,
        " overall_score": overall_score,
    }

    return result


def generate_optimization_report(original_shape, optimized_shape):
    """
    최적화 전후의 비교 report를 생성합니다.

    매개변수:
        original_shape: 최적화 전 Part.Shape
        optimized_shape: 최적화 후 Part.Shape

    반환value:
        str: 비교 report 텍스트
    """
    original_efficiency = calculate_structural_efficiency(original_shape)
    optimized_efficiency = calculate_structural_efficiency(optimized_shape)

    report = []
    report.append("=" * 50)
    report.append("  졸리드 바디 최적화 report")
    report.append("=" * 50)
    report.append(f"  원본 volume:       {original_shape.Volume:>12.2f} mm³")
    report.append(f"  최적화 후 volume:  {optimized_shape.Volume:>12.2f} mm³")
    report.append(f"  volume 감소율:     {(1 - optimized_shape.Volume / original_shape.Volume) * 100:>11.1f} %")
    report.append(f"  원본 area_val:     {original_shape.Area:>12.2f} mm²")
    report.append(f"  최적화 후 area_val:{optimized_shape.Area:>12.2f} mm²")
    report.append("-" * 50)
    report.append(f"  원본 종합 score_val:   {original_efficiency[' overall_score']:>10.1f}")
    report.append(f"  최적화 종합 score_val: {optimized_efficiency[' overall_score']:>10.1f}")
    report.append(f"  efficiency 향상:      {optimized_efficiency[' overall_score'] - original_efficiency[' overall_score']:>+10.1f}")
    report.append("=" * 50)

    return "\n".join(report)


# ============================================================
# 4. 시연용 예제 생성
# ============================================================

def create_example_box(width=40, depth=30, height=50):
    """
    시연용 박스 model_val을 생성합니다.

    매개변수:
        width: Xaxis direction size (mm)
        depth: Yaxis direction size (mm)
        height: Zaxis direction size (mm)

    반환value:
        Part.Shape: 박스 셰이프
    """
    return Part.makeBox(width, depth, height)


def create_example_column(diameter=20, height=60):
    """
    시연용 원형 pillar model_val을 생성합니다.

    매개변수:
        diameter: pillar 직경 (mm)
        height: pillar height (mm)

    반환value:
        Part.Shape: 원형 pillar 셰이프
    """
    return Part.makeCylinder(diameter / 2.0, height)


def create_example_steel_bracket():
    """
    시연용 강철 bracket을 생성합니다.
    L자 form_type의 bracket에 구멍이 있는 structure입니다.

    반환value:
        Part.Shape: bracket 셰이프
    """
    # 수평 판
    horizontal_plate = Part.makeBox(60, 40, 5)
    # perpendicular 판
    vertical_plate = Part.makeBox(5, 40, 40, FreeCAD.Vector(0, 0, 5))

    # bracket 결합
    bracket = horizontal_plate.fuse(vertical_plate)

    # 수평 판에 구멍 추가
    horizontal_hole = Part.makeCylinder(5, 5, FreeCAD.Vector(30, 20, -1), FreeCAD.Vector(0, 0, 1))
    bracket = bracket.cut(horizontal_hole)

    # perpendicular 판에 구멍 추가
    vertical_hole = Part.makeCylinder(4, 5, FreeCAD.Vector(2.5, 20, 25), FreeCAD.Vector(0, 1, 0))
    bracket = bracket.cut(vertical_hole)

    return bracket


# ============================================================
# 5. 메인 실row_val 함수
# ============================================================

def main_run():
    """
    졸리드 바디 최적화 메인 실row_val 함수입니다.
    모든 최적화 알고리즘을 순차적으로 실row_val하고 result를 표시합니다.
    """
    print("=" * 60)
    print("  Part 4 - 졸리드 바디 최적화")
    print("  알고리즘 기반 설계 시리즈")
    print("=" * 60)

    # ----------------------------------------------------------
    # 시나리오 1: 바운딩 박스 기반 최적화
    # ----------------------------------------------------------
    print("\n[시나리오 1] 바운딩 박스 기반 최적화")
    print("-" * 50)

    original_box = create_example_box(width=40, depth=30, height=50)
    analysis_result = analyze_bounding_box(original_box)

    print(f"  원본 박스 size: {analysis_result[' XLength']:.0f} x {analysis_result[' YLength']:.0f} x {analysis_result[' ZLength']:.0f} mm")
    print(f"  원본 volume: {analysis_result[' actual_volume']:.2f} mm³")
    print(f"  volume efficiency: {analysis_result[' volume_efficiency'] * 100:.1f}%")

    # 최적화 수row_val
    optimized_box = optimize_bounding_box(original_box, margin_ratio=0.15)
    optimization_analysis = analyze_bounding_box(optimized_box)
    print(f"  최적화 후 volume: {optimization_analysis[' actual_volume']:.2f} mm³")
    print(f"  최적화 후 efficiency: {optimization_analysis[' volume_efficiency'] * 100:.1f}%")

    # ----------------------------------------------------------
    # 시나리오 2: 불필요한 material_val 제거
    # ----------------------------------------------------------
    print("\n[시나리오 2] 불필요한 material_val 제거 알고리즘")
    print("-" * 50)

    original_column = create_example_column(diameter=20, height=60)
    print(f"  원본 pillar volume: {original_column.Volume:.2f} mm³")

    # 단일 material_val 제거
    print("\n  >> 단일 material_val 제거:")
    lightweight_column = remove_material_algorithm(original_column, min_thickness=2.0, void_ratio=0.4)

    # 반복적 material_val 제거
    print("\n  >> 반복적 material_val 제거:")
    iterative_lightweight_column = iterative_material_removal(original_column, removal_count=3, step_void=0.15)

    # ----------------------------------------------------------
    # 시나리오 3: bracket 최적화
    # ----------------------------------------------------------
    print("\n[시나리오 3] bracket 최적화")
    print("-" * 50)

    original_bracket = create_example_steel_bracket()
    print(f"  원본 bracket volume: {original_bracket.Volume:.2f} mm³")
    print(f"  원본 bracket area_val: {original_bracket.Area:.2f} mm²")

    optimized_bracket = remove_material_algorithm(original_bracket, min_thickness=1.5, void_ratio=0.2)

    # ----------------------------------------------------------
    # 시나리오 4: structure적 efficiency 종합 평가
    # ----------------------------------------------------------
    print("\n[시나리오 4] structure적 efficiency 종합 평가")
    print("-" * 50)

    test_model_list = [
        ("원본 박스", original_box),
        ("최적화 박스", optimized_box),
        ("원본 pillar", original_column),
        ("경량화 pillar", iterative_lightweight_column),
        ("원본 bracket", original_bracket),
        ("최적화 bracket", optimized_bracket),
    ]

    for name, model_val in test_model_list:
        efficiency = calculate_structural_efficiency(model_val)
        print(f"\n  [{name}]")
        print(f"    volume: {model_val.Volume:>10.2f} mm³")
        print(f"    area_val: {model_val.Area:>10.2f} mm²")
        print(f"    volume efficiency: {efficiency[' volume efficiency'] * 100:>8.1f}%")
        print(f"    form_type 계수: {efficiency[' form_factor']:>12.3f}")
        print(f"    종합 score_val: {efficiency[' overall_score']:>10.1f}")

    # ----------------------------------------------------------
    # 최적화 report
    # ----------------------------------------------------------
    print("\n")
    report = generate_optimization_report(original_bracket, optimized_bracket)
    print(report)

    # ----------------------------------------------------------
    # FreeCAD doc에 result 표시 (FreeCAD 실row_val 시)
    # ----------------------------------------------------------
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("solid_optimization")

        # 원본 bracket
        obj_original = doc.addObject("Part::Feature", "original_bracket")
        obj_original.Shape = original_bracket

        # 최적화된 bracket (position moved)
        obj_optimized = doc.addObject("Part::Feature", "optimized_bracket")
        optimized_bracket_moved = optimized_bracket.copy()
        optimized_bracket_moved.translate(FreeCAD.Vector(80, 0, 0))
        obj_optimized.Shape = optimized_bracket_moved

        # 경량화 pillar
        obj_pillar = doc.addObject("Part::Feature", "lightweight_column")
        opt_pillar_moved = iterative_lightweight_column.copy()
        opt_pillar_moved.translate(FreeCAD.Vector(160, 0, 0))
        obj_pillar.Shape = opt_pillar_moved

        doc.recompute()
        print("\n  FreeCAD doc에 result model_val이 추가되었습니다.")
        print("  브라우저에서 'original_bracket', 'optimized_bracket', 'lightweight_column'을 check하세요.")
    except Exception as e:
        print(f"\n  FreeCAD doc 작업 FAIL (매크로 환경이 아닐 수 있음): {e}")

    print("\n" + "=" * 60)
    print("  졸리드 바디 최적화 완료!")
    print("=" * 60)


# ============================================================
# 스크립트 실row_val 진입점
# ============================================================
if __name__ == "__main__":
    main_run()
else:
    # FreeCAD 매크로로 실row_val될 때
    main_run()

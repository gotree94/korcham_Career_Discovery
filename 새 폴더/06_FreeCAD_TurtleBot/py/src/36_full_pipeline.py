# -*- coding: utf-8 -*-
"""
Part 7 - 36: 전체 설계 파이프라인 매크로

설계 요구사항 분석부터 STL 내보내기까지의 전체 과정을 자동화하는 매크로.
사용자의 설계 요건을 입력받아 적합한 프리셋을 선택하고,
부품을 생성한 후 조립 및 검증까지 수행.

사용법: FreeCAD에서 실행하여 전체 설계 파이프라인이 자동 실행됨.
"""

import sys
import math
import time

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)


# ============================================================
# 설계 요건 정의
# ============================================================

class DesignRequirements:
    """
    설계 요건을 관리하는 클래스.

    사용자의 요구사항을 체계적으로 정의하고 검증한다.
    """

    def __init__(self):
        """기본 요건 초기화"""
        self.product_type = ""
        self.board_name = ""
        self.mount_type = "desktop"
        self.robot_preset = ""
        self.drone_preset = ""
        self.cooling_required = False
        self.waterproof = False
        self.custom_dimensions = None
        self.output_format = "STL"

    def validate(self):
        """
        설계 요건의 유효성을 검증한다.

        반환값:
            tuple: (유효여부, 오류메시지)
        """
        if not self.product_type:
            return False, "제품 유형이 지정되지 않았습니다."

        valid_types = ["IoT케이스", "로봇프레임", "드론부품", "센서하우징", "PCB케이스"]
        if self.product_type not in valid_types:
            return False, f"알 수 없는 제품 유형: {self.product_type}"

        if self.product_type == "IoT케이스" and not self.board_name:
            return False, "IoT 보드 이름이 지정되지 않았습니다."

        if self.product_type == "로봇프레임" and not self.robot_preset:
            return False, "로봇 프리셋이 지정되지 않았습니다."

        if self.product_type == "드론부품" and not self.drone_preset:
            return False, "드론 프리셋이 지정되지 않았습니다."

        return True, ""


# ============================================================
# 프리셋 선택 로직
# ============================================================

def select_preset(requirements):
    """
    설계 요건에 따라 적합한 프리셋을 선택한다.

    매개변수:
        requirements (DesignRequirements): 설계 요건

    반환값:
        dict: 선택된 프리셋 정보
    """
    print(f"\n[정보] 프리셋 선택 중... (제품: {requirements.product_type})")

    preset = {
        "type": requirements.product_type,
        "name": "",
        "description": "",
        "parameters": {},
    }

    if requirements.product_type == "IoT케이스":
        preset["name"] = requirements.board_name
        preset["description"] = f"{requirements.board_name}용 인클로저"
        preset["parameters"] = {
            "mount_type": requirements.mount_type,
            "cooling": requirements.cooling_required,
            "waterproof": requirements.waterproof,
        }

    elif requirements.product_type == "로봇프레임":
        preset["name"] = requirements.robot_preset
        preset["description"] = f"{requirements.robot_preset} 로봇 프레임"
        preset["parameters"] = {
            "custom_dimensions": requirements.custom_dimensions,
        }

    elif requirements.product_type == "드론부품":
        preset["name"] = requirements.drone_preset
        preset["description"] = f"{requirements.drone_preset} 드론 프레임"
        preset["parameters"] = {
            "custom_dimensions": requirements.custom_dimensions,
        }

    print(f"[정보] 선택된 프리셋: {preset['description']}")
    return preset


# ============================================================
# 부품 생성 파이프라인
# ============================================================

def create_parts(preset, requirements):
    """
    프리셋에 따라 부품을 생성한다.

    매개변수:
        preset (dict): 프리셋 정보
        requirements (DesignRequirements): 설계 요건

    반환값:
        dict: 생성된 부품들의 딕셔너리
    """
    parts = {}
    product_type = requirements.product_type

    print(f"\n[정보] === 부품 생성 시작 ({product_type}) ===")

    if product_type == "IoT케이스":
        import importlib
        try:
            iot_module = importlib.import_module("35_iot_board_case")
            print(f"[정보] IoT 보드 케이스 모듈 로드 성공")
        except ImportError:
            iot_module = None
            print("[정보] IoT 모듈 로드 실패, 기본 케이스 생성")

        if iot_module:
            parts = iot_module.assemble_case(
                requirements.board_name,
                requirements.mount_type
            )
        else:
            board_name = requirements.board_name
            print(f"[정보] {board_name} 기본 케이스 생성")
            parts = _create_basic_case(board_name)

    elif product_type == "로봇프레임":
        import importlib
        try:
            robot_module = importlib.import_module("33_robot_frame")
            parts_dict = robot_module.assemble_robot_frame(requirements.robot_preset)
            if parts_dict:
                parts = parts_dict
        except ImportError:
            print("[정보] 로봇 프레임 모듈 로드 실패")
            parts = _create_basic_robot_frame(requirements.robot_preset)

    elif product_type == "드론부품":
        import importlib
        try:
            drone_module = importlib.import_module("34_drone_parts")
            parts_dict = drone_module.assemble_drone_frame(requirements.drone_preset)
            if parts_dict:
                parts = parts_dict
        except ImportError:
            print("[정보] 드론 부품 모듈 로드 실패")
            parts = _create_basic_drone_frame(requirements.drone_preset)

    elif product_type == "센서하우징":
        print("[정보] 센서 하우징 생성")
        parts = _create_basic_sensor_housing(requirements.custom_dimensions)

    elif product_type == "PCB케이스":
        print("[정보] PCB 케이스 생성")
        parts = _create_basic_pcb_case(requirements.custom_dimensions)

    print(f"[정보] === 부품 생성 완료: {len(parts)}개 ===")
    return parts


# ============================================================
# 기본 부품 생성 함수 (모듈 없을 때 대체)
# ============================================================

def _create_basic_case(board_name):
    """기본 케이스를 생성한다 (모듈 미로드 시)."""
    print(f"[정보] 기본 케이스 생성: {board_name}")

    width, depth, height = 70.0, 55.0, 25.0
    wall = 2.5

    case = Part.makeBox(width, depth, height)
    cavity = Part.makeBox(
        width - wall * 2, depth - wall * 2, height - wall,
        Base.Vector(wall, wall, wall)
    )
    case = case.cut(cavity)

    return {"basic_case": case}


def _create_basic_robot_frame(preset_name):
    """기본 로봇 프레임을 생성한다."""
    print(f"[정보] 기본 로봇 프레임 생성: {preset_name}")

    base = Part.makeBox(80.0, 80.0, 5.0)
    arm1 = Part.makeBox(80.0, 25.0, 5.0, Base.Vector(27.5, 27.5, 5.0))
    arm2 = Part.makeBox(60.0, 20.0, 5.0, Base.Vector(37.5, 30.0, 10.0))

    return {"base": base, "arm_1": arm1, "arm_2": arm2}


def _create_basic_drone_frame(preset_name):
    """기본 드론 프레임을 생성한다."""
    print(f"[정보] 기본 드론 프레임 생성: {preset_name}")

    center = Part.makeBox(100.0, 100.0, 4.0)

    arms = {}
    for i in range(4):
        angle = math.radians(i * 90)
        cx = 50.0 + math.cos(angle) * 60.0
        cy = 50.0 + math.sin(angle) * 60.0
        arm = Part.makeBox(50.0, 12.0, 4.0,
                          Base.Vector(cx - 25.0, cy - 6.0, 0.0))
        arms[f"arm_{i + 1}"] = arm

    result = {"center": center}
    result.update(arms)
    return result


def _create_basic_sensor_housing(dimensions):
    """기본 센서 하우징을 생성한다."""
    if dimensions:
        w, d, h = dimensions.get("width", 40.0), dimensions.get("depth", 30.0), dimensions.get("height", 20.0)
    else:
        w, d, h = 40.0, 30.0, 20.0

    housing = Part.makeBox(w, d, h)
    cavity = Part.makeBox(w - 4.0, d - 4.0, h - 2.0, Base.Vector(2.0, 2.0, 2.0))
    housing = housing.cut(cavity)

    return {"housing": housing}


def _create_basic_pcb_case(dimensions):
    """기본 PCB 케이스를 생성한다."""
    if dimensions:
        w, d, h = dimensions.get("width", 80.0), dimensions.get("depth", 60.0), dimensions.get("height", 20.0)
    else:
        w, d, h = 80.0, 60.0, 20.0

    case = Part.makeBox(w, d, h)
    cavity = Part.makeBox(w - 4.0, d - 4.0, h - 2.0, Base.Vector(2.0, 2.0, 2.0))
    case = case.cut(cavity)

    return {"case": case}


# ============================================================
# 조립 파이프라인
# ============================================================

def assembly_pipeline(parts, preset):
    """
    부품들을 조립 위치에 배치한다.

    매개변수:
        parts (dict): 생성된 부품들
        preset (dict): 프리셋 정보

    반환값:
        dict: 배치된 부품들의 딕셔너리
    """
    print("\n[정보] === 조립 파이프라인 시작 ===")
    assembled = {}

    for name, shape in parts.items():
        assembled[name] = shape
        print(f"[정보] 부품 '{name}' 배치 완료")

    print(f"[정보] === 조립 파이프라인 완료: {len(assembled)}개 부품 ===")
    return assembled


# ============================================================
# 검증 파이프라인
# ============================================================

def validation_pipeline(parts, requirements):
    """
    생성된 부품들의 유효성을 검증한다.

    매개변수:
        parts (dict): 조립된 부품들
        requirements (DesignRequirements): 설계 요건

    반환값:
        list: 검증 결과 목록
    """
    print("\n[정보] === 검증 파이프라인 시작 ===")
    results = []

    # 1. 부품 존재 확인
    if len(parts) == 0:
        results.append(("오류", "생성된 부품이 없습니다."))
    else:
        results.append(("통과", f"{len(parts)}개 부품 생성됨"))

    # 2. 각 부품의 바운딩 박스 검사
    for name, shape in parts.items():
        if shape is None:
            results.append(("오류", f"부품 '{name}'이(가) None입니다."))
            continue

        try:
            bbox = shape.BoundBox
            if bbox.XLength <= 0 or bbox.YLength <= 0 or bbox.ZLength <= 0:
                results.append(("경고", f"부품 '{name}'의 크기가 0 이하입니다."))
            else:
                results.append(("통과", f"부품 '{name}': {bbox.XLength:.1f}x{bbox.YLength:.1f}x{bbox.ZLength:.1f}mm"))
        except Exception as e:
            results.append(("오류", f"부품 '{name}' 검증 실패: {e}"))

    # 3. 제품 유형별 특수 검증
    product_type = requirements.product_type

    if product_type == "IoT케이스":
        if "bottom" not in parts:
            results.append(("경고", "하단 케이스가 없습니다."))
        if "top" not in parts:
            results.append(("경고", "상단 커버가 없습니다."))

    elif product_type == "로봇프레임":
        if "base" not in parts:
            results.append(("경고", "베이스 플레이트가 없습니다."))

    elif product_type == "드론부품":
        if "center_plate" not in parts:
            results.append(("경고", "센터 플레이트가 없습니다."))

    # 결과 출력
    error_count = sum(1 for status, _ in results if status == "오류")
    warning_count = sum(1 for status, _ in results if status == "경고")
    pass_count = sum(1 for status, _ in results if status == "통과")

    print(f"\n[정보] 검증 결과: {pass_count} 통과, {warning_count} 경고, {error_count} 오류")

    for status, message in results:
        icon = "✓" if status == "통과" else "⚠" if status == "경고" else "✗"
        print(f"  [{icon}] {message}")

    print(f"[정보] === 검증 파이프라인 완료 ===")
    return results


# ============================================================
# 내보내기 파이프라인
# ============================================================

def export_pipeline(parts, output_format, requirements):
    """
    부품들을 지정된 형식으로 내보낸다.

    매개변수:
        parts (dict): 조립된 부품들
        output_format (str): 출력 형식
        requirements (DesignRequirements): 설계 요건

    반환값:
        list: 내보내기 결과 목록
    """
    print(f"\n[정보] === 내보내기 파이프라인 시작 ({output_format}) ===")
    results = []

    product_type = requirements.product_type
    safe_name = product_type.replace("케이스", "_case").replace("프레임", "_frame")

    for name, shape in parts.items():
        if shape is None:
            results.append((name, False, "부품이 None입니다."))
            continue

        filename = f"{safe_name}_{name}.stl"
        try:
            mesh = Part.Mesh()
            if hasattr(shape, "Shapes"):
                for s in shape.Shapes:
                    mesh.addMesh(s.tessellate(0.5))
            else:
                mesh.addMesh(shape.tessellate(0.5))
            mesh.write(filename)
            results.append((name, True, filename))
            print(f"[정보] '{name}' → {filename}")
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"[오류] '{name}' 내보내기 실패: {e}")

    success = sum(1 for _, ok, _ in results if ok)
    print(f"[정보] === 내보내기 완료: {success}/{len(results)} 성공 ===")
    return results


# ============================================================
# 전체 파이프라인 실행
# ============================================================

def run_full_pipeline(requirements):
    """
    전체 설계 파이프라인을 실행한다.

    매개변수:
        requirements (DesignRequirements): 설계 요건

    반환값:
        dict: 파이프라인 실행 결과
    """
    start_time = time.time()
    print("=" * 60)
    print("  전체 설계 파이프라인 시작")
    print("=" * 60)

    # 1. 요건 검증
    print("\n[단계 1] 요건 검증")
    valid, error_msg = requirements.validate()
    if not valid:
        print(f"[오류] 요건 검증 실패: {error_msg}")
        return {"success": False, "error": error_msg}

    # 2. 프리셋 선택
    print("\n[단계 2] 프리셋 선택")
    preset = select_preset(requirements)

    # 3. 부품 생성
    print("\n[단계 3] 부품 생성")
    parts = create_parts(preset, requirements)

    # 4. 조립
    print("\n[단계 4] 조립")
    assembled = assembly_pipeline(parts, preset)

    # 5. 검증
    print("\n[단계 5] 검증")
    validation_results = validation_pipeline(assembled, requirements)

    # 6. FreeCAD 도큐먼트에 추가
    print("\n[단계 6] FreeCAD 도큐먼트 추가")
    for name, shape in assembled.items():
        if shape is not None:
            try:
                doc = FreeCAD.ActiveDocument
                if doc is None:
                    doc = FreeCAD.newDocument("설계파이프라인")
                obj = doc.addObject("Part::Feature", f"{requirements.product_type}_{name}")
                obj.Shape = shape
                doc.recompute()
            except Exception as e:
                print(f"[오류] 도큐먼트 추가 실패 ({name}): {e}")

    # 7. 내보내기
    print("\n[단계 7] STL 내보내기")
    export_results = export_pipeline(assembled, requirements.output_format, requirements)

    # 결과 요약
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print("  파이프라인 실행 완료!")
    print(f"  소요 시간: {elapsed:.1f}초")
    print(f"  생성 부품: {len(assembled)}개")
    print(f"{'=' * 60}")

    return {
        "success": True,
        "parts_count": len(assembled),
        "elapsed_time": elapsed,
        "validation": validation_results,
        "export": export_results,
    }


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
            doc = FreeCAD.newDocument("설계파이프라인")

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
    예제 설계 요건으로 전체 파이프라인을 테스트한다.
    """
    print("=" * 60)
    print("  전체 설계 파이프라인 테스트")
    print("=" * 60)

    # 예제 1: IoT 케이스
    print("\n[예제 1] IoT 케이스 설계")
    req1 = DesignRequirements()
    req1.product_type = "IoT케이스"
    req1.board_name = "ESP32_DevKit"
    req1.mount_type = "desktop"
    req1.cooling_required = True
    run_full_pipeline(req1)

    # 예제 2: 로봇 프레임
    print("\n\n[예제 2] 로봇 프레임 설계")
    req2 = DesignRequirements()
    req2.product_type = "로봇프레임"
    req2.robot_preset = "중형로봇_3자유도"
    run_full_pipeline(req2)

    # 예제 3: 드론 프레임
    print("\n\n[예제 3] 드론 프레임 설계")
    req3 = DesignRequirements()
    req3.product_type = "드론부품"
    req3.drone_preset = "소형드론"
    run_full_pipeline(req3)

    print(f"\n{'=' * 60}")
    print("  전체 설계 파이프라인 테스트 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()

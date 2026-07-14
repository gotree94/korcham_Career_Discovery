# -*- coding: utf-8 -*-
"""
파일 25: AI 검수
=================
설계된 모델을 AI에게 검수 요청하여 검증과 개선점을 확인합니다.

학습 목표:
- FreeCAD 모델의 치수/형태 정보 추출
- 설계 규칙 검증 (호환성, 최소 치수, 공차)
- AI 기반 개선점 제안
- 검수 리포트 자동 생성

사용 방법:
1. FreeCAD에서 모델을 열고 이 파일을 실행
2. 또는 FreeCAD 모델 없이 샘플 데이터로 검수 연습
3. 검수 결과를 바탕으로 설계 개선

필요한 패키지: openai (선택사항)
"""

import sys
import os
import math
import datetime

print("=" * 60)
print("파일 25: AI 검수")
print("=" * 60)

# openai 라이브러리 확인
try:
    import openai
    has_openai = True
except ImportError:
    has_openai = False

# API 설정
api_key = os.environ.get("OPENAI_API_KEY", "")
client = None
if has_openai and api_key:
    try:
        client = openai.OpenAI(api_key=api_key)
        print("[정보] AI API 연결됨")
    except Exception:
        pass

if not client:
    print("[정보] 오프라인 모드 - 규칙 기반 검수로 동작")


# ============================================================
# 1단계: FreeCAD 모델 정보 추출
# ============================================================

print()
print("-" * 60)
print("1단계: FreeCAD 모델 정보 추출")
print("-" * 60)


class ModelInfo:
    """
    FreeCAD 모델의 정보를 저장하는 클래스입니다.
    FreeCAD 환경에서는 실제로 모델에서 정보를 추출하고,
    오프라인에서는 샘플 데이터를 사용합니다.
    """

    def __init__(self):
        self.doc_name = "미정"
        self.object_list = []
        self.total_volume = 0.0
        self.total_area = 0.0
        self.bounding_box = None

    def extract_from_freecad(self):
        """
        FreeCAD 환경에서 현재 활성 문서의 모델 정보를 추출합니다.
        FreeCAD가 아닌 환경에서는 False를 반환합니다.
        """
        try:
            import FreeCAD
            import FreeCADGui

            doc = FreeCAD.ActiveDocument
            if doc is None:
                print("[정보] 활성 FreeCAD 문서가 없습니다.")
                return False

            self.doc_name = doc.Name
            print(f"[FreeCAD] 문서: {self.doc_name}")

            total_vol = 0.0
            total_area = 0.0
            obj_list = []

            for obj in doc.Objects:
                if hasattr(obj, "Shape"):
                    shape = obj.Shape
                    obj_info = {
                        "name": obj.Name,
                        "type": obj.TypeId,
                        "volume": shape.Volume if hasattr(shape, "Volume") else 0,
                        "area": shape.Area if hasattr(shape, "Area") else 0,
                    }

                    # 바운딩박스 정보
                    if hasattr(shape, "BoundBox"):
                        bb = shape.BoundBox
                        obj_info["bbox"] = {
                            "width": bb.XLength,
                            "depth": bb.YLength,
                            "height": bb.ZLength
                        }

                    # 속성 정보
                    props = {}
                    for prop in obj.PropertiesList:
                        if prop in ["Length", "Width", "Height", "Radius",
                                   "Radius1", "Radius2", "Angle"]:
                            try:
                                props[prop] = getattr(obj, prop)
                            except Exception:
                                pass
                    obj_info["props"] = props

                    obj_list.append(obj_info)
                    total_vol += obj_info["volume"]
                    total_area += obj_info["area"]

            self.object_list = obj_list
            self.total_volume = total_vol
            self.total_area = total_area

            print(f"  - 객체 수: {len(obj_list)}")
            print(f"  - 전체 부피: {total_vol:.2f} mm3")
            print(f"  - 전체 표면적: {total_area:.2f} mm2")

            return True

        except ImportError:
            print("[정보] FreeCAD 환경이 아닙니다.")
            return False
        except Exception as e:
            print(f"[오류] 모델 추출 실패: {e}")
            return False

    def create_sample_data(self):
        """FreeCAD 없이 테스트용 샘플 데이터를 생성합니다."""
        print("[정보] 샘플 모델 데이터를 사용합니다.")

        self.doc_name = "샘플_설계"
        self.object_list = [
            {
                "name": "상자_본체",
                "type": "Part::Box",
                "volume": 200 * 100 * 50,  # 200x100x50 mm
                "area": 2 * (200 * 100 + 100 * 50 + 200 * 50),
                "bbox": {"width": 200, "depth": 100, "height": 50},
                "props": {"Length": 200, "Width": 100, "Height": 50}
            },
            {
                "name": "실린더_기둥",
                "type": "Part::Cylinder",
                "volume": math.pi * 25 ** 2 * 100,
                "area": 2 * math.pi * 25 ** 2 + math.pi * 50 * 100,
                "bbox": {"width": 50, "depth": 50, "height": 100},
                "props": {"Radius": 25, "Height": 100}
            },
            {
                "name": "구멍",
                "type": "Part::Cylinder",
                "volume": math.pi * 5 ** 2 * 50,
                "area": 2 * math.pi * 5 ** 2 + math.pi * 10 * 50,
                "bbox": {"width": 10, "depth": 10, "height": 50},
                "props": {"Radius": 5, "Height": 50}
            }
        ]
        self.total_volume = sum(obj["volume"] for obj in self.object_list)
        self.total_area = sum(obj["area"] for obj in self.object_list)

        print(f"  - 문서명: {self.doc_name}")
        print(f"  - 객체 수: {len(self.object_list)}")
        for obj in self.object_list:
            print(f"    - {obj['name']}: {obj['type']}, 부피 {obj['volume']:.1f}mm3")


# 모델 정보 추출 시도
model = ModelInfo()
is_freecad = model.extract_from_freecad()

if not is_freecad:
    model.create_sample_data()


# ============================================================
# 2단계: 설계 규칙 정의
# ============================================================

print()
print("-" * 60)
print("2단계: 설계 규칙 정의")
print("-" * 60)


class DesignRules:
    """
    설계 검수에 사용되는 규칙들을 정의합니다.
    """

    def __init__(self):
        # 최소 치수 규칙
        self.min_thickness_mm = 1.0         # 최소 벽 두께
        self.min_diameter_mm = 2.0          # 최소 구멍 지름
        self.min_fillet_radius_mm = 0.5     # 최소 모서리 R
        self.max_aspect_ratio = 10.0            # 최대 장단 비율

        # 공차 규칙
        self.general_tolerance_mm = 0.1          # 일반 공차
        self.precision_tolerance_mm = 0.01         # 정밀 공차

        # 형상 규칙
        self.min_rib_thickness_mm = 2.0      # 최소 리브 두께
        self.max_rib_height_mm = 50.0     # 최대 리브 높이
        self.rib_spacing_mm = 100.0   # 리브 간격

        # 재료 규칙
        self.min_wall_steel = 1.5        # 강재 최소 벽 두께
        self.min_wall_aluminum = 2.0  # 알루미늄 최소 벽 두께
        self.min_wall_plastic = 1.0  # 플라스틱 최소 벽 두께

    def print_rules(self):
        """현재 설정된 규칙을 출력합니다."""
        print("[적용된 설계 규칙]")
        print(f"  - 최소 두께: {self.min_thickness_mm} mm")
        print(f"  - 최소 구멍 지름: {self.min_diameter_mm} mm")
        print(f"  - 최대 장단 비율: {self.max_aspect_ratio}:1")
        print(f"  - 일반 공차: +/- {self.general_tolerance_mm} mm")
        print(f"  - 정밀 공차: +/- {self.precision_tolerance_mm} mm")


rules = DesignRules()
rules.print_rules()


# ============================================================
# 3단계: 규칙 기반 검수 (오프라인)
# ============================================================

print()
print("-" * 60)
print("3단계: 규칙 기반 검수")
print("-" * 60)


def rule_based_review(model_info, design_rules):
    """
    정의된 설계 규칙에 따라 모델을 검수합니다.

    검수 항목:
    1. 형상 규칙 검증
    2. 치수 합리성 검증
    3. 구조적 건전성 검증
    4. 제작 가능성 검증
    5. 최적화 가능성 검토

    매개변수:
        model_info (ModelInfo): 모델의 정보
        design_rules (DesignRules): 설계 규칙

    반환값:
        list: 검수 결과 목록
    """
    review_results = []

    # 1. 형상 규칙 검증
    for obj in model_info.object_list:
        obj_name = obj["name"]

        # 바운딩박스 기반 검사
        if "bbox" in obj:
            bb = obj["bbox"]
            width = bb.get("width", 0)
            depth = bb.get("depth", 0)
            height = bb.get("height", 0)

            # 장단 비율 검사
            dims = [width, depth, height]
            if max(dims) > 0 and min(dims) > 0:
                ratio = max(dims) / min(dims)
                if ratio > design_rules.max_aspect_ratio:
                    review_results.append({
                        "grade": "경고",
                        "item": "장단 비율",
                        "object": obj_name,
                        "message": f"장단 비율 {ratio:.1f}:1 (허용: {design_rules.max_aspect_ratio}:1)",
                        "improvement": "리브 추가 또는 형상 변경 검토"
                    })
                else:
                    review_results.append({
                        "grade": "통과",
                        "item": "장단 비율",
                        "object": obj_name,
                        "message": f"비율 {ratio:.1f}:1 - 적합",
                        "improvement": ""
                    })

        # 속성 기반 검사
        props = obj.get("props", {})

        # 원통 객체 검사
        if "Radius" in props:
            radius = props["Radius"]
            diameter = radius * 2
            if diameter < design_rules.min_diameter_mm:
                review_results.append({
                    "grade": "오류",
                    "item": "최소 치수",
                    "object": obj_name,
                    "message": f"지름 {diameter}mm < 최소 {design_rules.min_diameter_mm}mm",
                    "improvement": f"지름을 {design_rules.min_diameter_mm}mm 이상으로 증가"
                })

            # 원통의 길이/지름 비율
            h = props.get("Height", 0)
            if h > 0 and diameter > 0:
                aspect = h / diameter
                if aspect > 20:
                    review_results.append({
                        "grade": "경고",
                        "item": "세로비 검사",
                        "object": obj_name,
                        "message": f"세로비 {aspect:.1f} - 가늘고 긴 형태",
                        "improvement": "지지 구조 추가 또는 직경 증가 검토"
                    })

        # 상자 객체 검사
        if obj["type"] == "Part::Box":
            length = props.get("Length", 0)
            width_val = props.get("Width", 0)
            height_val = props.get("Height", 0)

            # 최소 두께 검사 (높이가 벽 두께로 가정)
            if height_val > 0 and height_val < design_rules.min_thickness_mm:
                review_results.append({
                    "grade": "경고",
                    "item": "최소 두께",
                    "object": obj_name,
                    "message": f"높이(두께) {height_val}mm < 최소 {design_rules.min_thickness_mm}mm",
                    "improvement": f"두께를 {design_rules.min_thickness_mm}mm 이상으로 증가"
                })

            # 체적 대비 표면적 비율 (공정 복잡도 지표)
            if length > 0 and width_val > 0 and height_val > 0:
                vol = length * width_val * height_val
                area = 2 * (length * width_val + width_val * height_val + length * height_val)
                if vol > 0:
                    ratio = area / vol
                    if ratio > 0.5:
                        review_results.append({
                            "grade": "정보",
                            "item": "공정 복잡도",
                            "object": obj_name,
                            "message": f"표면적/체적 비율 {ratio:.3f} - 얇은 벽 구조",
                            "improvement": "제작 비용 확인 필요"
                        })

    # 전체 모델 검사
    # 객체 간 간격 검사 (간소화된 버전)
    if len(model_info.object_list) > 1:
        review_results.append({
            "grade": "정보",
            "item": "객체 간 간격",
            "object": "전체",
            "message": f"객체 {len(model_info.object_list)}개 간 간격 검증 필요",
            "improvement": "FreeCAD에서 간접 충돌 검사 실행 권장"
        })

    return review_results


# 검수 실행
print("[실행] 규칙 기반 검수...")
rule_result = rule_based_review(model, rules)

# 결과 출력
print("\n[검수 결과]")
print("=" * 55)
print(f"  {'등급':<6} {'항목':<14} {'객체':<16} {'메시지'}")
print(f"  {'-'*6} {'-'*14} {'-'*16} {'-'*30}")

for result in rule_result:
    grade_display = f"[{result['grade']}]"
    print(f"  {grade_display:<6} {result['item']:<14} {result['object']:<16} {result['message']}")
    if result['improvement']:
        print(f"         -> 개선 제안: {result['improvement']}")

# 통계
error_count = sum(1 for r in rule_result if r["grade"] == "오류")
warning_count = sum(1 for r in rule_result if r["grade"] == "경고")
pass_count = sum(1 for r in rule_result if r["grade"] == "통과")
info_count = sum(1 for r in rule_result if r["grade"] == "정보")

print(f"\n[검수 통계]")
print(f"  - 오류: {error_count}건")
print(f"  - 경고: {warning_count}건")
print(f"  - 통과: {pass_count}건")
print(f"  - 정보: {info_count}건")


# ============================================================
# 4단계: AI 기반 검수
# ============================================================

print()
print("-" * 60)
print("4단계: AI 기반 검수")
print("-" * 60)


def ai_review(model_info):
    """
    AI에게 모델 정보를 전달하여 전문적인 검수를 요청합니다.

    AI에게 전달하는 정보:
    - 모델의 형상 및 치수 정보
    - 기존 규칙 기반 검수 결과
    - 추가 검수 요청 사항

    매개변수:
        model_info (ModelInfo): 모델의 정보

    반환값:
        str: AI 검수 결과
    """
    if not client:
        print("[정보] API 미연결 - 규칙 기반 검수 결과를 참고하세요.")
        return None

    try:
        # 모델 정보를 텍스트로 변환
        model_text = f"문서명: {model_info.doc_name}\n"
        model_text += f"객체 수: {len(model_info.object_list)}\n"
        model_text += f"전체 부피: {model_info.total_volume:.2f} mm3\n"
        model_text += f"전체 표면적: {model_info.total_area:.2f} mm2\n\n"

        for obj in model_info.object_list:
            model_text += f"객체: {obj['name']}\n"
            model_text += f"  유형: {obj['type']}\n"
            model_text += f"  부피: {obj['volume']:.2f} mm3\n"
            if "bbox" in obj:
                bb = obj["bbox"]
                model_text += f"  크기: {bb['width']:.1f} x {bb['depth']:.1f} x {bb['height']:.1f} mm\n"
            if "props" in obj:
                for key, val in obj["props"].items():
                    model_text += f"  {key}: {val}\n"
            model_text += "\n"

        # 규칙 기반 검수 결과도 전달
        rule_result_text = ""
        for result in rule_result:
            rule_result_text += f"- [{result['grade']}] {result['item']}: {result['message']}\n"

        user_prompt = f"""다음 FreeCAD 설계 모델을 검수해주세요:

=== 모델 정보 ===
{model_text}

=== 규칙 기반 검수 결과 ===
{rule_result_text}

다음 항목을 포함하여 검수해주세요:
1. 형상 적합성 검토
2. 치수 합리성 검토
3. 구조적 안전성 검토
4. 제작 가능성 검토
5. 개선점 및 최적화 제안
6. 설계 등급 평가 (A/B/C/D)

한국어로 답변해주세요."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 25년 경력의 CAD 설계 검수 전문가입니다. "
                        "기계설계, 재료공학, 제조공학 전문 지식을 보유하고 있으며, "
                        "설계 검수, DFMA(설계/제조/조립성 분석), "
                        "공차 분석 등을 수행합니다. "
                        "구체적이고 실용적인 개선 제안을 한국어로 제공합니다."
                    )
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        ai_result = response.choices[0].message.content

        print("[AI 검수 결과]")
        print("=" * 55)
        print(ai_result)
        print("=" * 55)

        return ai_result

    except Exception as e:
        print(f"[오류] AI 검수 실패: {e}")
        return None


# AI 검수 실행
print("[실행] AI 검수 요청 중...")
ai_review_result = ai_review(model)


# ============================================================
# 5단계: 검수 리포트 생성
# ============================================================

print()
print("-" * 60)
print("5단계: 검수 리포트 생성")
print("-" * 60)


def generate_review_report(model_info, rule_results, ai_result=None):
    """
    검수 결과를 종합적인 리포트로 생성합니다.

    매개변수:
        model_info (ModelInfo): 모델 정보
        rule_results (list): 규칙 기반 검수 결과
        ai_result (str): AI 검수 결과 (선택)

    반환값:
        str: 검수 리포트 전체 텍스트
    """
    now = datetime.datetime.now()

    report = []
    report.append("=" * 60)
    report.append("FreeCAD 설계 검수 리포트")
    report.append("=" * 60)
    report.append(f"작성일: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"문서명: {model_info.doc_name}")
    report.append("")

    # 모델 개요
    report.append("1. 모델 개요")
    report.append("-" * 40)
    report.append(f"  객체 수: {len(model_info.object_list)}")
    report.append(f"  전체 부피: {model_info.total_volume:.2f} mm3")
    report.append(f"  전체 표면적: {model_info.total_area:.2f} mm2")
    report.append("")

    for obj in model_info.object_list:
        report.append(f"  [{obj['name']}] {obj['type']}")
        if "bbox" in obj:
            bb = obj["bbox"]
            report.append(f"    크기: {bb['width']:.1f} x {bb['depth']:.1f} x {bb['height']:.1f} mm")
        report.append(f"    부피: {obj['volume']:.2f} mm3")
    report.append("")

    # 규칙 기반 검수 결과
    report.append("2. 규칙 기반 검수 결과")
    report.append("-" * 40)
    report.append(f"  검수 항목 수: {len(rule_results)}")
    report.append(f"  오류: {sum(1 for r in rule_results if r['grade'] == '오류')}건")
    report.append(f"  경고: {sum(1 for r in rule_results if r['grade'] == '경고')}건")
    report.append(f"  통과: {sum(1 for r in rule_results if r['grade'] == '통과')}건")
    report.append("")

    for result in rule_results:
        if result["grade"] != "통과":
            report.append(f"  [{result['grade']}] {result['item']} ({result['object']})")
            report.append(f"    {result['message']}")
            if result["improvement"]:
                report.append(f"    개선: {result['improvement']}")
            report.append("")

    # AI 검수 결과
    if ai_result:
        report.append("3. AI 전문가 검수 결과")
        report.append("-" * 40)
        report.append(ai_result)
        report.append("")

    # 종합 판정
    report.append("4. 종합 판정")
    report.append("-" * 40)

    err_count = sum(1 for r in rule_results if r["grade"] == "오류")
    warn_count = sum(1 for r in rule_results if r["grade"] == "경고")

    if err_count > 0:
        grade = "D (재설계 필요)"
        comment = f"오류 {err_count}건 발견. 치수 및 형상 전면 재검토 필요."
    elif warn_count > 3:
        grade = "C (보정 필요)"
        comment = f"경고 {warn_count}건. 주요 항목 보정 후 재검수 권장."
    elif warn_count > 0:
        grade = "B (양호)"
        comment = f"경고 {warn_count}건. 선택적 개선으로 설계 완성 가능."
    else:
        grade = "A (우수)"
        comment = "모든 검수 항목 통과. 설계 우수."

    report.append(f"  등급: {grade}")
    report.append(f"  코멘트: {comment}")
    report.append("")
    report.append("=" * 60)

    report_text = "\n".join(report)

    print(report_text)

    return report_text


# 리포트 생성
print("[실행] 검수 리포트 생성 중...")
report = generate_review_report(model, rule_result, ai_review_result)


# ============================================================
# 6단계: 개선된 설계 제안
# ============================================================

print()
print("-" * 60)
print("6단계: 개선된 설계 제안")
print("-" * 60)


def suggest_improved_design(model_info, rule_results):
    """
    검수 결과를 바탕으로 개선된 설계를 제안합니다.

    매개변수:
        model_info (ModelInfo): 원본 모델 정보
        rule_results (list): 규칙 기반 검수 결과

    반환값:
        str: 개선된 설계의 FreeCAD 스크립트
    """
    script = '# -*- coding: utf-8 -*-\n'
    script += '# 검수 결과 기반 개선된 설계\n'
    script += f'# 생성일: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
    script += f'# 원본 문서: {model_info.doc_name}\n\n'
    script += 'import FreeCAD\n'
    script += 'import Part\n\n'

    # 검수 결과에서 개선 사항 수집
    improvements = []
    for result in rule_results:
        if result["grade"] in ["오류", "경고"] and result["improvement"]:
            improvements.append(result)

    script += f'# 검수에서 발견된 문제: {len(improvements)}건\n\n'
    script += 'doc = FreeCAD.newDocument("개선된_설계")\n\n'

    # 각 객체에 대해 개선 적용
    for obj in model_info.object_list:
        obj_name = obj["name"]
        obj_type = obj["type"]
        props = obj.get("props", {})
        bb = obj.get("bbox", {})

        if obj_type == "Part::Box":
            length = props.get("Length", bb.get("width", 100))
            width_val = props.get("Width", bb.get("depth", 50))
            height_val = props.get("Height", bb.get("height", 25))

            # 개선: 최소 두께 보장
            if height_val < rules.min_thickness_mm:
                height_val = rules.min_thickness_mm
                script += f'# [개선] {obj_name}: 두께를 {rules.min_thickness_mm}mm로 증가\n'

            script += f'{obj_name} = doc.addObject("Part::Box", "{obj_name}")\n'
            script += f'{obj_name}.Length = {length}\n'
            script += f'{obj_name}.Width = {width_val}\n'
            script += f'{obj_name}.Height = {height_val}\n\n'

        elif obj_type == "Part::Cylinder":
            radius = props.get("Radius", bb.get("width", 10) / 2)
            height_val = props.get("Height", bb.get("height", 50))

            # 개선: 최소 지름 보장
            diameter = radius * 2
            if diameter < rules.min_diameter_mm:
                radius = rules.min_diameter_mm / 2
                script += f'# [개선] {obj_name}: 지름을 {rules.min_diameter_mm}mm로 증가\n'

            script += f'{obj_name} = doc.addObject("Part::Cylinder", "{obj_name}")\n'
            script += f'{obj_name}.Radius = {radius}\n'
            script += f'{obj_name}.Height = {height_val}\n\n'

    script += 'FreeCAD.ActiveDocument.recompute()\n'
    script += 'print("[성공] 개선된 설계 생성 완료")\n'

    print("[개선된 설계 스크립트]")
    print("-" * 40)
    print(script)
    print("-" * 40)

    return script


# 개선 설계 제안
print("[실행] 개선된 설계 제안 중...")
improved_script = suggest_improved_design(model, rule_result)


# ============================================================
# 7단계: 검수 체크리스트
# ============================================================

print()
print("-" * 60)
print("7단계: 검수 체크리스트")
print("-" * 60)

print("""
FreeCAD 설계 검수 체크리스트:

 [ ] 기본 검수
   [ ] 치수 호환성 확인
   [ ] 공차 적절성 확인
   [ ] 재료 선택 적합성
   [ ] 표면 마감 요구사항

 [ ] 구조 검수
   [ ] 하중 충족 여부
   [ ] 안전율 확보
   [ ] 피로 수명 고려
   [ ] 진동/공진 회피

 [ ] 제작 검수
   [ ] 가공 가능성
   [ ] 조립 순서 용이성
   [ ] 용접성/접합 방법
   [ ] 표면 처리 가능성

 [ ] 기능 검수
   [ ] 동작 간섭 없음
   [ ] 케이블/배관 경로
   [ ] 정비 접근성
   [ ] 교체 용이성

 [ ] 경제성 검수
   [ ] 재료 비용 적정
   [ ] 가공 시간 적정
   [ ] 대량 생산성
   [ ] 표준 부품 활용

 [ ] 안전 검수
   [ ] 모서리 라운딩
   [ ] 고정 방법 확보
   [ ] 과부하 보호
   [ ] 안전 마크/표시
""")


# ============================================================
# 최종 요약
# ============================================================

print()
print("=" * 60)
print("파일 25 학습 완료!")
print("=" * 60)
print("""
 학습한 내용:
  1. FreeCAD 모델 정보 추출 (FreeCAD 환경 및 샘플)
  2. 설계 규칙 정의 (치수, 형상, 공차)
  3. 규칙 기반 자동 검수
  4. AI 기반 전문가 검수
  5. 검수 리포트 자동 생성
  6. 개선된 설계 제안
  7. 검수 체크리스트 활용

 검수 등급 기준:
  A (우수): 모든 항목 통과
  B (양호): 경고 0~2건, 선택적 개선
  C (보정필요): 경고 3건 이상
  D (재설계): 오류 발견

 Part 5 (AI 통합 기초) 전체 완료!
""")

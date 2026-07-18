# -*- coding: utf-8 -*-
"""
파일 23: 치수 추천 AI
======================
AI가 설계 조건을 분석하여 최적의 치수를 추천합니다.

학습 목표:
- 하중 조건 입력 및 분석
- 재료 특성 기반 치수 계산
- AI 추천과 공학적 검증 결합
- 추천 결과의 시각적 확인

사용 방법:
1. FreeCAD에서 이 파일 열고 실행
2. AI API 키가 있으면 AI 추천, 없으면 공학적 계산으로 동작
3. 추천 결과를 FreeCAD 모델에 자동 적용

필요한 패키지: openai (선택사항)
"""

import sys
import os
import math

print("=" * 60)
print("파일 23: 치수 추천 AI")
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
    print("[정보] 오프라인 모드 - 공학적 계산으로 동작")


# ============================================================
# 1단계: 재료 데이터베이스
# ============================================================

print()
print("-" * 60)
print("1단계: 재료 데이터베이스")
print("-" * 60)

# 공학적 계산에 사용되는 재료 특성 데이터
# 실제 공학 데이터를 기반으로 한 참고용 값입니다
material_db = {
    "탄소강": {
        "파괴응력_MPa": 400,        # 인장 파괴 응력 (MPa)
        "타선응력_MPa": 250,         # 항복 응력 (MPa)
        "탄성계수_GPa": 200,         # 영의 탄성계수 (GPa)
        "밀도_gcm3": 7.85,           # 밀도 (g/cm3)
        "가격상대": 1.0,             # 상대적 가격
        "용접성": "양호",
        "내식성": "보통",
        "최대사용온도_C": 450,
        "설명": "일반 구조용 강재. 가장 범용적."
    },
    "합금강": {
        "파괴응력_MPa": 600,
        "타선응력_MPa": 400,
        "탄성계수_GPa": 210,
        "밀도_gcm3": 7.85,
        "가격상대": 2.5,
        "용접성": "양호",
        "내식성": "보통",
        "최대사용온도_C": 500,
        "설명": "고강도 필요 부품. 높은 피로 강도."
    },
    "알루미늄_6061": {
        "파괴응력_MPa": 310,
        "타선응력_MPa": 276,
        "탄성계수_GPa": 68.9,
        "밀도_gcm3": 2.70,
        "가격상대": 3.0,
        "용접성": "양호",
        "내식성": "우수",
        "최대사용온도_C": 200,
        "설명": "경량 부품. 항공우주, 자동차 분야."
    },
    "스테인리스_304": {
        "파괴응력_MPa": 505,
        "타선응력_MPa": 215,
        "탄성계수_GPa": 193,
        "밀도_gcm3": 7.93,
        "가격상대": 4.0,
        "용접성": "양호",
        "내식성": "우수",
        "최대사용온도_C": 870,
        "설명": "내식성 요구 부품. 식품, 의료, 화학."
    },
    "구리": {
        "파괴응력_MPa": 210,
        "타선응력_MPa": 70,
        "탄성계수_GPa": 117,
        "밀도_gcm3": 8.96,
        "가격상대": 5.0,
        "용접성": "보통",
        "내식성": "양호",
        "최대사용온도_C": 200,
        "설명": "전기/열 전도성 부품. 배선, 냉각."
    },
    "티타늄": {
        "파괴응력_MPa": 900,
        "타선응력_MPa": 830,
        "탄성계수_GPa": 114,
        "밀도_gcm3": 4.51,
        "가격상대": 20.0,
        "용접성": "어려움",
        "내식성": "우수",
        "최대사용온도_C": 600,
        "설명": "초경량 고강도. 항공우주, 의료 임플란트."
    },
    "PLA_플라스틱": {
        "파괴응력_MPa": 50,
        "타선응력_MPa": 35,
        "탄성계수_GPa": 3.5,
        "밀도_gcm3": 1.24,
        "가격상대": 0.5,
        "용접성": "불가",
        "내식성": "양호",
        "최대사용온도_C": 60,
        "설명": "3D 프린팅용. 프로토타입."
    },
    "나일론": {
        "파괴응력_MPa": 85,
        "타선응력_MPa": 60,
        "탄성계수_GPa": 3.0,
        "밀도_gcm3": 1.14,
        "가격상대": 1.5,
        "용접성": "불가",
        "내식성": "양호",
        "최대사용온도_C": 120,
        "설명": "자연윤활 부품. 기어, 베어링."
    }
}

print("[재료 데이터베이스]")
print(f"  등록된 재료 수: {len(material_db)}개")
for name, data in material_db.items():
    print(f"  - {name}: 파괴응력 {data['파괴응력_MPa']}MPa, "
          f"밀도 {data['밀도_gcm3']}g/cm3")


# ============================================================
# 2단계: 설계 조건 입력
# ============================================================

print()
print("-" * 60)
print("2단계: 설계 조건 입력")
print("-" * 60)


class DesignCondition:
    """
    부품 설계 조건을 저장하는 클래스입니다.

    속성:
        load_N (float): 작용 하중 (뉴턴)
        safety_factor (float): 안전 계수 (일반적으로 1.5 ~ 3.0)
        material_name (str): 선택된 재료 이름
        part_type (str): 부품의 종류 (plate, beam, shaft, cylinder 등)
        length_mm (float): 부품의 주요 길이
        diameter_mm (float): 부품의 지름 (해당 시)
        temperature_C (float): 사용 온도
        environment (str): 사용 환경 (실내, 실외, 해양, 화학 등)
    """

    def __init__(self):
        self.load_N = 1000.0           # 기본 하중: 1000N (약 100kg)
        self.safety_factor = 2.0              # 기본 안전율: 2.0
        self.material_name = "탄소강"          # 기본 재료
        self.part_type = "plate"        # 기본: 판재
        self.length_mm = 100.0           # 기본 길이
        self.diameter_mm = 20.0            # 기본 지름
        self.temperature_C = 25.0             # 기본 온도 (상온)
        self.environment = "실내"              # 기본 환경

    def display(self):
        """설계 조건을 출력합니다."""
        print(f"  - 하중: {self.load_N} N (약 {self.load_N / 9.81:.1f} kgf)")
        print(f"  - 안전율: {self.safety_factor}")
        print(f"  - 재료: {self.material_name}")
        print(f"  - 부품유형: {self.part_type}")
        print(f"  - 길이: {self.length_mm} mm")
        print(f"  - 지름: {self.diameter_mm} mm")
        print(f"  - 온도: {self.temperature_C} C")
        print(f"  - 환경: {self.environment}")


# 샘플 설계 조건 생성
print("[기본 조건 설정]")
condition = DesignCondition()
condition.load_N = 5000.0       # 5000N (약 510kg)
condition.safety_factor = 2.5           # 안전율 2.5
condition.material_name = "탄소강"
condition.part_type = "plate"     # 판재(plate)
condition.length_mm = 200.0
condition.temperature_C = 25.0
condition.environment = "실내"

print("[설계 조건]")
condition.display()


# ============================================================
# 3단계: 공학적 치수 계산 (오프라인)
# ============================================================

print()
print("-" * 60)
print("3단계: 공학적 치수 계산")
print("-" * 60)


def calc_plate_thickness(cond):
    """
    단순 지지 판재의 최소 두께를 계산합니다.

    공식: sigma = F / (b * t)
    => t = F * safety_factor / (b * 허용응력)

    매개변수:
        cond (DesignCondition): 설계 조건

    반환값:
        dict: 계산 결과
    """
    # 재료 특성 가져오기
    mat = material_db.get(cond.material_name)
    if not mat:
        print(f"[오류] '{cond.material_name}' 재료를 찾을 수 없습니다.")
        return None

    allowable_stress = mat["타선응력_MPa"]  # 항복 응력 사용
    safe_stress = allowable_stress / cond.safety_factor  # 허용 응력 (안전율 적용)

    # 판재 폭을 길이의 1/10으로 가정 (지지 조건에 따라 다름)
    width_mm = cond.length_mm / 10.0

    # 최소 두께 계산
    # sigma = F / (b * t) => t = F / (b * sigma)
    min_thickness_mm = (cond.load_N / (width_mm * safe_stress))

    # 반올림 (실제 제작 고려, 0.5mm 단위)
    rec_thickness_mm = math.ceil(min_thickness_mm * 2) / 2.0

    # 최소 두께 보장 (구조적 최소 두께)
    if rec_thickness_mm < 1.0:
        rec_thickness_mm = 1.0

    result = {
        "calc_type": "판재 두께",
        "material": cond.material_name,
        "allowable_stress_MPa": allowable_stress,
        "safe_stress_MPa": safe_stress,
        "load_N": cond.load_N,
        "width_mm": width_mm,
        "min_thickness_mm": min_thickness_mm,
        "rec_thickness_mm": rec_thickness_mm,
        "verified_stress_MPa": cond.load_N / (width_mm * rec_thickness_mm)
    }

    return result


def calc_cylinder_diameter(cond):
    """
    축이나 실린더의 최소 지름을 계산합니다.

    공식: sigma = F / (pi * r^2)
    => r = sqrt(F * safety_factor / (pi * 허용응력))

    매개변수:
        cond (DesignCondition): 설계 조건

    반환값:
        dict: 계산 결과
    """
    mat = material_db.get(cond.material_name)
    if not mat:
        return None

    allowable_stress = mat["타선응력_MPa"]
    safe_stress = allowable_stress / cond.safety_factor

    # 인장 하중 기준 최소 지름
    # sigma = F / A = F / (pi * r^2)
    # r = sqrt(F / (pi * sigma))
    min_radius = math.sqrt(cond.load_N / (math.pi * safe_stress))
    min_diameter = min_radius * 2

    # 반올림 (1mm 단위)
    rec_diameter = math.ceil(min_diameter)

    # 최소 지름 보장
    if rec_diameter < 5.0:
        rec_diameter = 5.0

    # 실제 응력 검증
    area = math.pi * (rec_diameter / 2) ** 2
    actual_stress = cond.load_N / area

    result = {
        "calc_type": "원통 지름",
        "material": cond.material_name,
        "allowable_stress_MPa": allowable_stress,
        "safe_stress_MPa": safe_stress,
        "load_N": cond.load_N,
        "min_diameter_mm": min_diameter,
        "rec_diameter_mm": rec_diameter,
        "actual_stress_MPa": actual_stress,
        "safety_factor_verified": allowable_stress / actual_stress
    }

    return result


def calc_beam_section(cond):
    """
    단순 지지 빔의 최소 단면 계수를 계산합니다.

    공식: M = F * L / 4 (중앙 하중)
          sigma = M / S
          S = b * h^2 / 6 (직사각형 단면)

    매개변수:
        cond (DesignCondition): 설계 조건

    반환값:
        dict: 계산 결과
    """
    mat = material_db.get(cond.material_name)
    if not mat:
        return None

    allowable_stress = mat["타선응력_MPa"]
    safe_stress = allowable_stress / cond.safety_factor

    # 최대 굽힘 모멘트 (중앙 하중, 단순 지지)
    moment_Nmm = cond.load_N * cond.length_mm / 4.0

    # 단면계수: S = M / sigma
    min_section_mod = moment_Nmm / safe_stress

    # 폭/높이 비율 1:2 가정 (h = 2b)
    # S = b * h^2 / 6 = b * (2b)^2 / 6 = 4b^3 / 6 = 2b^3 / 3
    # b = (3S/2)^(1/3)
    min_width = (3 * min_section_mod / 2) ** (1.0 / 3.0)
    min_height = min_width * 2

    # 반올림
    rec_width = math.ceil(min_width)
    rec_height = math.ceil(min_height)

    # 검증
    verified_section_mod = rec_width * rec_height ** 2 / 6.0
    verified_stress = moment_Nmm / verified_section_mod

    result = {
        "calc_type": "빔 단면",
        "material": cond.material_name,
        "allowable_stress_MPa": allowable_stress,
        "moment_Nmm": moment_Nmm,
        "min_section_mod_mm3": min_section_mod,
        "rec_width_mm": rec_width,
        "rec_height_mm": rec_height,
        "verified_stress_MPa": verified_stress,
        "safety_factor_verified": allowable_stress / verified_stress
    }

    return result


# 계산 실행
print("[판재 두께 계산]")
plate_result = calc_plate_thickness(condition)
if plate_result:
    print(f"  - 재료: {plate_result['material']}")
    print(f"  - 허용응력: {plate_result['allowable_stress_MPa']} MPa")
    print(f"  - 최소 두께: {plate_result['min_thickness_mm']:.2f} mm")
    print(f"  - 권장 두께: {plate_result['rec_thickness_mm']} mm")
    print(f"  - 검증 응력: {plate_result['verified_stress_MPa']:.2f} MPa")

print()
print("[원통 지름 계산]")
# 축용 조건
shaft_cond = DesignCondition()
shaft_cond.load_N = 3000.0
shaft_cond.safety_factor = 3.0
shaft_cond.material_name = "합금강"
shaft_cond.part_type = "shaft"

cylinder_result = calc_cylinder_diameter(shaft_cond)
if cylinder_result:
    print(f"  - 재료: {cylinder_result['material']}")
    print(f"  - 최소 지름: {cylinder_result['min_diameter_mm']:.2f} mm")
    print(f"  - 권장 지름: {cylinder_result['rec_diameter_mm']} mm")
    print(f"  - 실제 응력: {cylinder_result['actual_stress_MPa']:.2f} MPa")
    print(f"  - 검증 안전율: {cylinder_result['safety_factor_verified']:.2f}")

print()
print("[빔 단면 계산]")
beam_result = calc_beam_section(condition)
if beam_result:
    print(f"  - 재료: {beam_result['material']}")
    print(f"  - 굽힘 모멘트: {beam_result['moment_Nmm']:.1f} Nmm")
    print(f"  - 권장 폭: {beam_result['rec_width_mm']} mm")
    print(f"  - 권장 높이: {beam_result['rec_height_mm']} mm")
    print(f"  - 검증 응력: {beam_result['verified_stress_MPa']:.2f} MPa")


# ============================================================
# 4단계: AI 기반 치수 추천
# ============================================================

print()
print("-" * 60)
print("4단계: AI 기반 치수 추천")
print("-" * 60)


def ai_dimension_recommendation(cond):
    """
    AI에게 설계 조건을 전달하여 최적 치수를 추천받습니다.

    AI에게 전달하는 정보:
    - 하중 조건
    - 재료 특성
    - 부품 유형
    - 사용 환경

    매개변수:
        cond (DesignCondition): 설계 조건

    반환값:
        dict: AI 추천 결과
    """
    if not client:
        print("[정보] API 미연결 - 공학적 계산 결과를 사용합니다.")
        return None

    try:
        # 재료 정보 가져오기
        mat = material_db.get(cond.material_name, {})

        # AI에게 전달할 프롬프트 구성
        user_prompt = f"""다음 조건에서 최적의 부품 치수를 추천해주세요:

설계 조건:
- 부품 유형: {cond.part_type}
- 작용 하중: {cond.load_N} N (약 {cond.load_N / 9.81:.1f} kgf)
- 안전율: {cond.safety_factor}
- 재료: {cond.material_name}
  - 파괴응력: {mat.get('파괴응력_MPa', 'N/A')} MPa
  - 항복응력: {mat.get('타선응력_MPa', 'N/A')} MPa
  - 탄성계수: {mat.get('탄성계수_GPa', 'N/A')} GPa
- 길이: {cond.length_mm} mm
- 사용 온도: {cond.temperature_C} C
- 사용 환경: {cond.environment}

다음을 답변해주세요:
1. 권장 치수 (두께, 지름, 단면 등)
2. 계산 근거
3. 주의사항
4. 대체 재료 제안

한국어로 답변해주세요."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 20년 경력의 기계설계 엔지니어입니다. "
                        "재료역학과 구조해석 전문 지식을 보유하고 있으며, "
                        "항상 안전율을 고려하여 설계합니다. "
                        "계산 과정을 상세히 한국어로 설명합니다."
                    )
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        recommend_text = response.choices[0].message.content

        print("[AI 치수 추천 결과]")
        print("-" * 40)
        print(recommend_text)
        print("-" * 40)

        return {"recommendation_text": recommend_text}

    except Exception as e:
        print(f"[오류] AI 추천 실패: {e}")
        return None


# AI 추천 실행
print("[실행] AI 치수 추천 요청 중...")
ai_result = ai_dimension_recommendation(condition)


# ============================================================
# 5단계: 추천 결과 검증
# ============================================================

print()
print("-" * 60)
print("5단계: 추천 결과 검증")
print("-" * 60)


def verify_recommendation(cond, calc_result):
    """
    공학적 계산 결과를 검증하고 리포트를 생성합니다.

    검증 항목:
    1. 응력 검증: 실제 응력 < 허용 응력
    2. 안전율 검증: 실제 안전율 >= 요구 안전율
    3. 온도 검증: 사용 온도 < 최대 사용 온도
    4. 변형 검증: 허용 변형량 이내

    매개변수:
        cond (DesignCondition): 설계 조건
        calc_result (dict): 계산 결과

    반환값:
        dict: 검증 결과
    """
    if not calc_result:
        return {"passed": False, "message": "계산 결과가 없습니다."}

    mat = material_db.get(cond.material_name, {})
    verification_results = []

    # 1. 응력 검증
    allowable_stress = mat.get("타선응력_MPa", 0)
    if "verified_stress_MPa" in calc_result:
        actual_stress = calc_result["verified_stress_MPa"]
    elif "actual_stress_MPa" in calc_result:
        actual_stress = calc_result["actual_stress_MPa"]
    else:
        actual_stress = 0

    if allowable_stress > 0 and actual_stress > 0:
        if actual_stress < allowable_stress:
            verification_results.append({
                "item": "응력 검증",
                "passed": True,
                "message": f"OK: {actual_stress:.1f} MPa < {allowable_stress} MPa"
            })
        else:
            verification_results.append({
                "item": "응력 검증",
                "passed": False,
                "message": f"실패: {actual_stress:.1f} MPa >= {allowable_stress} MPa"
            })

    # 2. 안전율 검증
    if "safety_factor_verified" in calc_result:
        actual_sf = calc_result["safety_factor_verified"]
        if actual_sf >= cond.safety_factor:
            verification_results.append({
                "item": "안전율 검증",
                "passed": True,
                "message": f"OK: {actual_sf:.2f} >= {cond.safety_factor}"
            })
        else:
            verification_results.append({
                "item": "안전율 검증",
                "passed": False,
                "message": f"실패: {actual_sf:.2f} < {cond.safety_factor}"
            })

    # 3. 온도 검증
    max_temp = mat.get("최대사용온도_C", 9999)
    if cond.temperature_C <= max_temp:
        verification_results.append({
            "item": "온도 검증",
            "passed": True,
            "message": f"OK: {cond.temperature_C}C <= {max_temp}C"
        })
    else:
        verification_results.append({
            "item": "온도 검증",
            "passed": False,
            "message": f"실패: {cond.temperature_C}C > {max_temp}C"
        })

    # 4. 재료 호환성 검증
    corrosion_resist = mat.get("내식성", "보통")
    env_ok = True
    if cond.environment == "해양" and corrosion_resist not in ["우수"]:
        env_ok = False
    if cond.environment == "화학" and corrosion_resist not in ["우수"]:
        env_ok = False

    if env_ok:
        verification_results.append({
            "item": "환경 적합성",
            "passed": True,
            "message": f"OK: {cond.environment} 환경에서 {corrosion_resist} 내식성"
        })
    else:
        verification_results.append({
            "item": "환경 적합성",
            "passed": False,
            "message": f"경고: {cond.environment} 환경에 {corrosion_resist} 내식성 부적합"
        })

    # 결과 출력
    print("[검증 리포트]")
    print("=" * 40)
    all_passed = True
    for vr in verification_results:
        status = "[통과]" if vr["passed"] else "[실패]"
        print(f"  {status} {vr['item']}: {vr['message']}")
        if not vr["passed"]:
            all_passed = False

    print("=" * 40)
    if all_passed:
        print("  [결과] 모든 검증을 통과했습니다.")
    else:
        print("  [결과] 일부 검증에 실패했습니다. 설계를 검토해 주세요.")

    return {"passed": all_passed, "verification_list": verification_results}


# 검증 실행
print("[실행] 추천 결과 검증 중...")
if plate_result:
    verification = verify_recommendation(condition, plate_result)


# ============================================================
# 6단계: FreeCAD 모델 자동 적용
# ============================================================

print()
print("-" * 60)
print("6단계: FreeCAD 모델 자동 적용")
print("-" * 60)


def freecad_model_apply(cond, calc_result):
    """
    계산된 치수를 FreeCAD 모델에 자동 적용합니다.

    매개변수:
        cond (DesignCondition): 설계 조건
        calc_result (dict): 계산 결과

    반환값:
        str: 실행할 FreeCAD 스크립트
    """
    script = '# -*- coding: utf-8 -*-\n'
    script += '# AI 추천 치수 기반 FreeCAD 모델\n'
    script += f'# 재료: {cond.material_name}\n'
    script += f'# 하중: {cond.load_N} N\n'
    script += f'# 안전율: {cond.safety_factor}\n\n'
    script += 'import FreeCAD\n'
    script += 'import Part\n\n'
    script += 'doc = FreeCAD.newDocument("AI추천부품")\n\n'

    if calc_result and calc_result.get("calc_type") == "판재 두께":
        thick = calc_result["rec_thickness_mm"]
        length = cond.length_mm
        width = calc_result["width_mm"]
        script += f'# 판재: {length}x{width}x{thick} mm\n'
        script += f'plate = doc.addObject("Part::Box", "판재")\n'
        script += f'plate.Length = {length}\n'
        script += f'plate.Width = {width}\n'
        script += f'plate.Height = {thick}\n'

    elif calc_result and calc_result.get("calc_type") == "원통 지름":
        diam = calc_result["rec_diameter_mm"]
        length = cond.length_mm
        script += f'# 원통: 지름 {diam}mm, 길이 {length}mm\n'
        script += f'cyl = doc.addObject("Part::Cylinder", "원통")\n'
        script += f'cyl.Radius = {diam / 2}\n'
        script += f'cyl.Height = {length}\n'

    elif calc_result and calc_result.get("calc_type") == "빔 단면":
        width = calc_result["rec_width_mm"]
        height = calc_result["rec_height_mm"]
        length = cond.length_mm
        script += f'# 빔: {width}x{height}x{length} mm\n'
        script += f'beam = doc.addObject("Part::Box", "빔")\n'
        script += f'beam.Length = {length}\n'
        script += f'beam.Width = {width}\n'
        script += f'beam.Height = {height}\n'

    else:
        script += '# 기본 상자\n'
        script += 'box = doc.addObject("Part::Box", "상자")\n'
        script += 'box.Length = 50\n'
        script += 'box.Width = 50\n'
        script += 'box.Height = 50\n'

    script += '\nFreeCAD.ActiveDocument.recompute()\n'
    script += 'print("[성공] AI 추천 치수로 모델 생성 완료")\n'

    print("[생성된 스크립트]")
    print("-" * 40)
    print(script)
    print("-" * 40)

    return script


# FreeCAD 모델 적용
if plate_result:
    freecad_script = freecad_model_apply(condition, plate_result)


# ============================================================
# 7단계: 비교 분석
# ============================================================

print()
print("-" * 60)
print("7단계: 재료별 치수 비교 분석")
print("-" * 60)


def compare_materials(cond):
    """
    같은 하중 조건에서 재료별로 필요한 치수를 비교합니다.

    매개변수:
        cond (DesignCondition): 기본 설계 조건

    반환값:
        list: 재료별 계산 결과 목록
    """
    comparison_results = []

    print("[재료별 두께 비교]")
    print(f"  하중: {cond.load_N} N, 안전율: {cond.safety_factor}")
    print(f"  폭: {cond.length_mm / 10:.1f} mm (길이의 1/10)")
    print()
    print(f"  {'재료':<15} {'허용응력':>8} {'권장두께':>8} {'상대가격':>8}")
    print(f"  {'-'*15} {'-'*8} {'-'*8} {'-'*8}")

    for name, data in material_db.items():
        temp_cond = DesignCondition()
        temp_cond.load_N = cond.load_N
        temp_cond.safety_factor = cond.safety_factor
        temp_cond.material_name = name
        temp_cond.length_mm = cond.length_mm

        result = calc_plate_thickness(temp_cond)
        if result:
            comparison_results.append({
                "material": name,
                "thickness": result["rec_thickness_mm"],
                "cost": data["가격상대"]
            })
            print(f"  {name:<15} {data['타선응력_MPa']:>6}MPa "
                  f"{result['rec_thickness_mm']:>6}mm {data['가격상대']:>7.1f}x")

    return comparison_results


comparison = compare_materials(condition)


# ============================================================
# 최종 요약
# ============================================================

print()
print("=" * 60)
print("파일 23 학습 완료!")
print("=" * 60)
print("""
 학습한 내용:
  1. 재료 데이터베이스 구축 및 활용
  2. 설계 조건 (하중, 안전율, 환경) 입력
  3. 공학적 치수 계산 (판재, 원통, 빔)
  4. AI 기반 치수 추천
  5. 추천 결과 검증 (응력, 안전율, 온도, 환경)
  6. FreeCAD 모델 자동 적용
  7. 재료별 비교 분석

 공학적 계산 공식:
  - 판재: t = F / (b * sigma)
  - 원통: r = sqrt(F / (pi * sigma))
  - 빔: S = M / sigma, S = b*h^2/6

 다음 파일: 24_ai_material.py (재료 추천 AI)
""")

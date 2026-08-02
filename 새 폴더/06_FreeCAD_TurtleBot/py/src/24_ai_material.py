# -*- coding: utf-8 -*-
"""
파일 24: 재료 추천 AI
======================
용도에 따라 적합한 재료를 AI가 추천합니다.

학습 목표:
- 사용 조건 (온도, 하중, 환경) 입력
- 재료 데이터베이스 활용
- AI 추천과 근거 제시
- 다중 후보 비교 및 선택

사용 방법:
1. FreeCAD에서 이 파일 열고 실행
2. 설계 조건을 입력하면 AI가 최적 재료 추천
3. 추천 근거와 함께 대안 제시

필요한 패키지: openai (선택사항)
"""

import sys
import os

print("=" * 60)
print("파일 24: 재료 추천 AI")
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
    print("[정보] 오프라인 모드 - 규칙 기반 추천으로 동작")


# ============================================================
# 1단계: 재료 데이터베이스
# ============================================================

print()
print("-" * 60)
print("1단계: 재료 데이터베이스")
print("-" * 60)

# 재료 속성 데이터베이스
material_db = {
    "탄소강_S45C": {
        "분류": "금속",
        "파괴응력_MPa": 570,
        "항복응력_MPa": 305,
        "탄성계수_GPa": 205,
        "밀도_gcm3": 7.85,
        "가열온도_max_C": 500,
        "내식성": "낮음",
        "용접가능": True,
        "가공성": "보통",
        "비용등급": 1,
        "열처리": "가능 (경화, 질화)",
        "사용예": "축, 기어, 볼트, 공구"
    },
    "합금강_SCM440": {
        "분류": "금속",
        "파괴응력_MPa": 900,
        "항복응력_MPa": 750,
        "탄성계수_GPa": 210,
        "밀도_gcm3": 7.85,
        "가열온도_max_C": 550,
        "내식성": "낮음",
        "용접가능": True,
        "가공성": "어려움",
        "비용등급": 3,
        "열처리": "가능 (질화 포함)",
        "사용예": "고강도 축, 베어링 축, 고하중 볼트"
    },
    "스테인리스_304": {
        "분류": "금속",
        "파괴응력_MPa": 505,
        "항복응력_MPa": 215,
        "탄성계수_GPa": 193,
        "밀도_gcm3": 7.93,
        "가열온도_max_C": 870,
        "내식성": "높음",
        "용접가능": True,
        "가공성": "보통",
        "비용등급": 4,
        "열처리": "불가 (냉간 가공만 가능)",
        "사용예": "식품기기, 의료기기, 화학설비"
    },
    "스테인리스_316": {
        "분류": "금속",
        "파괴응력_MPa": 485,
        "항복응력_MPa": 205,
        "탄성계수_GPa": 193,
        "밀도_gcm3": 7.99,
        "가열온도_max_C": 870,
        "내식성": "매우높음",
        "용접가능": True,
        "가공성": "보통",
        "비용등급": 5,
        "열처리": "불가",
        "사용예": "해양설비, 의료임플란트, 화학반응기"
    },
    "알루미늄_6061_T6": {
        "분류": "금속",
        "파괴응력_MPa": 310,
        "항복응력_MPa": 276,
        "탄성계수_GPa": 69,
        "밀도_gcm3": 2.70,
        "가열온도_max_C": 200,
        "내식성": "높음",
        "용접가능": True,
        "가공성": "쉬움",
        "비용등급": 3,
        "열처리": "가능 (T6 처리)",
        "사용예": "경량부품, 프레임, 히트싱크"
    },
    "알루미늄_7075_T6": {
        "분류": "금속",
        "파괴응력_MPa": 570,
        "항복응력_MPa": 505,
        "탄성계수_GPa": 72,
        "밀도_gcm3": 2.81,
        "가열온도_max_C": 150,
        "내식성": "보통",
        "용접가능": False,
        "가공성": "보통",
        "비용등급": 6,
        "열처리": "가능",
        "사용예": "항공부품, 고성능 레이싱"
    },
    "티타늄_Ti6Al4V": {
        "분류": "금속",
        "파괴응력_MPa": 950,
        "항복응력_MPa": 880,
        "탄성계수_GPa": 114,
        "밀도_gcm3": 4.43,
        "가열온도_max_C": 400,
        "내식성": "매우높음",
        "용접가능": True,
        "가공성": "어려움",
        "비용등급": 15,
        "열처리": "가능",
        "사용예": "항공엔진, 의료임플란트, 핵심부품"
    },
    "구리_C1100": {
        "분류": "금속",
        "파괴응력_MPa": 220,
        "항복응력_MPa": 70,
        "탄성계수_GPa": 117,
        "밀도_gcm3": 8.96,
        "가열온도_max_C": 200,
        "내식성": "보통",
        "용접가능": True,
        "가공성": "쉬움",
        "비용등급": 5,
        "열처리": "불가",
        "사용예": "전기단자, 열교환기, 배관"
    },
    "황동_C2801": {
        "분류": "금속",
        "파괴응력_MPa": 450,
        "항복응력_MPa": 150,
        "탄성계수_GPa": 105,
        "밀도_gcm3": 8.47,
        "가열온도_max_C": 300,
        "내식성": "높음",
        "용접가능": True,
        "가공성": "쉬움",
        "비용등급": 4,
        "열처리": "불가",
        "사용예": "밸브, 피팅, 장식품"
    },
    "PEEK_플라스틱": {
        "분류": "플라스틱",
        "파괴응력_MPa": 100,
        "항복응력_MPa": 90,
        "탄성계수_GPa": 3.6,
        "밀도_gcm3": 1.31,
        "가열온도_max_C": 260,
        "내식성": "높음",
        "용접가능": False,
        "가공성": "보통",
        "비용등급": 10,
        "열처리": "불가",
        "사용예": "고온 화학설비, 반도체, 의료"
    },
    "나일론_PA66": {
        "분류": "플라스틱",
        "파괴응력_MPa": 85,
        "항복응력_MPa": 60,
        "탄성계수_GPa": 3.0,
        "밀도_gcm3": 1.14,
        "가열온도_max_C": 120,
        "내식성": "보통",
        "용접가능": False,
        "가공성": "쉬움",
        "비용등급": 1,
        "열처리": "불가",
        "사용예": "기어, 베어링, 캐리어"
    },
    "PLA": {
        "분류": "플라스틱",
        "파괴응력_MPa": 50,
        "항복응력_MPa": 35,
        "탄성계수_GPa": 3.5,
        "밀도_gcm3": 1.24,
        "가열온도_max_C": 60,
        "내식성": "보통",
        "용접가능": False,
        "가공성": "쉬움",
        "비용등급": 0.5,
        "열처리": "불가",
        "사용예": "프로토타입, 모형, 교육용"
    },
    "탄소섬유_CFRP": {
        "분류": "복합재료",
        "파괴응력_MPa": 600,
        "항복응력_MPa": 500,
        "탄성계수_GPa": 70,
        "밀도_gcm3": 1.55,
        "가열온도_max_C": 150,
        "내식성": "높음",
        "용접가능": False,
        "가공성": "어려움",
        "비용등급": 12,
        "열처리": "불가",
        "사용예": "항공기, 레이싱카, 스포츠용품"
    },
    "세라믹_Al2O3": {
        "분류": "세라믹",
        "파괴응력_MPa": 300,
        "항복응력_MPa": 0,
        "탄성계수_GPa": 380,
        "밀도_gcm3": 3.95,
        "가열온도_max_C": 1700,
        "내식성": "매우높음",
        "용접가능": False,
        "가공성": "매우어려움",
        "비용등급": 8,
        "열처리": "소intering",
        "사용예": "절삭공구, 내마모부품, 절연체"
    }
}

# 등록된 재료 수 출력
metal_count = sum(1 for v in material_db.values() if v["분류"] == "금속")
plastic_count = sum(1 for v in material_db.values() if v["분류"] == "플라스틱")
other_count = len(material_db) - metal_count - plastic_count

print(f"[재료 데이터베이스 현황]")
print(f"  - 총 재료 수: {len(material_db)}개")
print(f"  - 금속: {metal_count}개")
print(f"  - 플라스틱: {plastic_count}개")
print(f"  - 기타: {other_count}개")
print()
for name, props in material_db.items():
    print(f"  - {name}: {props['분류']}, 응력 {props['파괴응력_MPa']}MPa, "
          f"비용 {props['비용등급']}등급")


# ============================================================
# 2단계: 사용 조건 입력
# ============================================================

print()
print("-" * 60)
print("2단계: 사용 조건 입력")
print("-" * 60)


class UsageCondition:
    """
    부품의 사용 환경과 요구 조건을 정의하는 클래스입니다.
    """

    def __init__(self):
        self.part_name = "미정"
        self.description = ""
        self.max_load_N = 1000.0
        self.operating_temp_C = 25.0
        self.environment = "실내"
        self.requirements = []
        self.excluded_materials = []

    def set_conditions(self, part_name, description, load, temp, environment, requirements=None, excluded=None):
        """조건을 한번에 설정합니다."""
        self.part_name = part_name
        self.description = description
        self.max_load_N = load
        self.operating_temp_C = temp
        self.environment = environment
        self.requirements = requirements or []
        self.excluded_materials = excluded or []

    def display(self):
        """설정된 조건을 출력합니다."""
        print(f"  부품명: {self.part_name}")
        print(f"  설명: {self.description}")
        print(f"  최대 하중: {self.max_load_N} N (약 {self.max_load_N / 9.81:.1f} kgf)")
        print(f"  작동 온도: {self.operating_temp_C} C")
        print(f"  사용 환경: {self.environment}")
        if self.requirements:
            print(f"  특수 요구사항: {', '.join(self.requirements)}")
        if self.excluded_materials:
            print(f"  제외 재료: {', '.join(self.excluded_materials)}")


# 샘플 사용 조건
print("[설정된 사용 조건]")
conditions = UsageCondition()
conditions.set_conditions(
    part_name="식품 가공용 교반 날개",
    description="식품 반죽을 교반하는 날개 부품. 위생과 내식성이 중요.",
    load=2000.0,
    temp=80.0,
    environment="식품",
    requirements=["위생적", "세척 가능", "내식성 우수"],
    excluded=["구리", "황동"]
)
conditions.display()


# ============================================================
# 3단계: 규칙 기반 재료 추천 (오프라인)
# ============================================================

print()
print("-" * 60)
print("3단계: 규칙 기반 재료 추천 (오프라인)")
print("-" * 60)


def rule_based_material_recommendation(cond):
    """
    정의된 규칙에 따라 적합한 재료를 추천합니다.

    필터링 규칙:
    1. 최대 사용 온도 확인
    2. 내식성 요구 확인
    3. 하중에 필요한 최소 응력 확인
    4. 제외 재료 처리
    5. 비용 효율성 점수 계산

    매개변수:
        cond (UsageCondition): 사용 조건

    반환값:
        list: 추천 재료 목록 (점수 순 정렬)
    """
    candidates = []

    for name, props in material_db.items():
        score = 0
        reasons = []

        # 제외 재료 검사
        if name in cond.excluded_materials or any(excl in name for excl in cond.excluded_materials):
            continue

        # 1. 온도 검증
        if cond.operating_temp_C > props["가열온도_max_C"]:
            continue  # 온도 초과 - 후보에서 제외

        if cond.operating_temp_C > props["가열온도_max_C"] * 0.8:
            score -= 10
            reasons.append("온도 여유 부족")
        else:
            score += 10
            reasons.append("온도 적합")

        # 2. 하중 검증 (최소 항복응력 기준)
        # 안전율 2.0 적용한 최소 응력 요구
        min_required_stress = cond.max_load_N / 100.0  # 대략적 면적 가정
        if props["항복응력_MPa"] >= min_required_stress:
            score += 15
            reasons.append("하중 충족")
        else:
            continue  # 하중 미충족

        # 3. 환경별 내식성 검증
        if cond.environment in ["해양", "화학", "식품", "의료"]:
            if props["내식성"] == "매우높음":
                score += 20
                reasons.append("내식성 매우 우수")
            elif props["내식성"] == "높음":
                score += 10
                reasons.append("내식성 우수")
            elif props["내식성"] == "보통":
                score -= 5
                reasons.append("내식성 보통")
            else:
                score -= 15
                reasons.append("내식성 부족")

        # 4. 특수 요구사항 평가
        for req in cond.requirements:
            if req in ["위생적", "세척 가능"]:
                if props["내식성"] in ["높음", "매우높음"]:
                    score += 10
                    reasons.append(f"'{req}' 충족")
            if req in ["경량"]:
                if props["밀도_gcm3"] < 3.0:
                    score += 15
                    reasons.append("경량 재료")
            if req in ["고강도"]:
                if props["항복응력_MPa"] > 500:
                    score += 15
                    reasons.append("고강도 재료")
            if req in ["전기전도"]:
                if props["분류"] == "금속" and "구리" in name:
                    score += 15
                    reasons.append("전기전도성 우수")

        # 5. 비용 효율성 (저비용 보너스)
        if props["비용등급"] <= 2:
            score += 5
            reasons.append("경제적")
        elif props["비용등급"] >= 10:
            score -= 5
            reasons.append("고비용")

        # 6. 가공성
        if props["가공성"] == "쉬움":
            score += 5
            reasons.append("가공 용이")
        elif props["가공성"] == "매우어려움":
            score -= 5
            reasons.append("가공 어려움")

        candidates.append({
            "material_name": name,
            "props": props,
            "score": score,
            "reasons": reasons
        })

    # 점수 순 정렬
    candidates.sort(key=lambda x: x["score"], reverse=True)

    return candidates


# 규칙 기반 추천 실행
print("[규칙 기반 추천 실행]")
rule_result = rule_based_material_recommendation(conditions)

if rule_result:
    print(f"\n[추천 결과 - 상위 5개]")
    print(f"  {'순위':<4} {'재료명':<22} {'점수':>4} {'사유'}")
    print(f"  {'-'*4} {'-'*22} {'-'*4} {'-'*30}")
    for i, result in enumerate(rule_result[:5], 1):
        reasons_str = ", ".join(result["reasons"])
        print(f"  {i:<4} {result['material_name']:<22} {result['score']:>4} {reasons_str}")
else:
    print("  [결과] 조건에 맞는 재료가 없습니다.")


# ============================================================
# 4단계: AI 기반 재료 추천
# ============================================================

print()
print("-" * 60)
print("4단계: AI 기반 재료 추천")
print("-" * 60)


def ai_material_recommendation(cond):
    """
    AI에게 사용 조건을 전달하여 최적 재료를 추천받습니다.

    AI에게 전달하는 정보:
    - 부품 용도 및 설명
    - 하중, 온도, 환경 조건
    - 특수 요구사항
    - 재료 데이터베이스 요약

    매개변수:
        cond (UsageCondition): 사용 조건

    반환값:
        str: AI 추천 결과 텍스트
    """
    if not client:
        print("[정보] API 미연결 - 규칙 기반 추천을 참고하세요.")
        return None

    try:
        # 재료 DB를 텍스트로 요약
        db_summary = ""
        for name, props in material_db.items():
            db_summary += (f"- {name}: {props['분류']}, "
                       f"응력 {props['파괴응력_MPa']}MPa, "
                       f"온도 {props['가열온도_max_C']}C까지, "
                       f"내식성 {props['내식성']}, "
                       f"비용 {props['비용등급']}등급, "
                       f"{props['사용예']}\n")

        user_prompt = f"""다음 부품에 적합한 재료를 추천해주세요:

부품 정보:
- 부품명: {cond.part_name}
- 설명: {cond.description}
- 최대 하중: {cond.max_load_N} N
- 작동 온도: {cond.operating_temp_C} C
- 사용 환경: {cond.environment}
- 특수 요구사항: {', '.join(cond.requirements) or '없음'}
- 제외 재료: {', '.join(cond.excluded_materials) or '없음'}

사용 가능한 재료:
{db_summary}

다음을 포함하여 답변해주세요:
1. 1순위 추천 재료와 이유
2. 2순위 대안 재료와 이유
3. 각 재료의 장단점 비교
4. 주의사항"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 재료공학 전문가입니다. 30년 이상의 "
                        "재료 선택 경험을 보유하고 있으며, "
                        "설계 조건에 최적화된 재료를 추천합니다. "
                        "추천 시 반드시 공학적 근거를 제시하고, "
                        "한국어로 명확하게 답변합니다."
                    )
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=1500
        )

        ai_recommendation = response.choices[0].message.content

        print("[AI 재료 추천 결과]")
        print("=" * 50)
        print(ai_recommendation)
        print("=" * 50)

        return ai_recommendation

    except Exception as e:
        print(f"[오류] AI 추천 실패: {e}")
        return None


# AI 추천 실행
print("[실행] AI 재료 추천 요청 중...")
ai_recommendation = ai_material_recommendation(conditions)


# ============================================================
# 5단계: 여러 시나리오 비교
# ============================================================

print()
print("-" * 60)
print("5단계: 여러 시나리오 비교")
print("-" * 60)


def scenario_comparison():
    """
    여러 사용 시나리오에서 재료 추천 결과를 비교합니다.
    """
    scenario_list = [
        {
            "name": "시나리오 1: 실내 기계 프레임",
            "cond": ("일반 기계 프레임", "설비를 지지하는 골조", 5000, 30, "실내", ["경량"], []),
        },
        {
            "name": "시나리오 2: 해양 밸브 부품",
            "cond": ("밸브 본체", "바닷물 접촉 밸브", 3000, 60, "해양", ["내식성 우수"], []),
        },
        {
            "name": "시나리오 3: 고온 오븐 지지대",
            "cond": ("오븐 내부 지지대", "고온에서 구조 지지", 1000, 400, "실내", ["고온 내성"], []),
        },
        {
            "name": "시나리오 4: 의료 수술 도구",
            "cond": ("수술용 핸들", "의료 수술 도구", 200, 121, "의료", ["위생적", "세척 가능"], []),
        },
    ]

    print("[시나리오별 추천 비교]\n")

    for scenario in scenario_list:
        print(f"[{scenario['name']}]")
        cond = UsageCondition()
        cond.part_name = scenario["cond"][0]
        cond.description = scenario["cond"][1]
        cond.max_load_N = scenario["cond"][2]
        cond.operating_temp_C = scenario["cond"][3]
        cond.environment = scenario["cond"][4]
        cond.requirements = scenario["cond"][5]
        cond.excluded_materials = scenario["cond"][6]

        result = rule_based_material_recommendation(cond)

        if result:
            best = result[0]
            print(f"  추천 1순위: {best['material_name']} (점수: {best['score']})")
            print(f"    사유: {', '.join(best['reasons'])}")
            if len(result) > 1:
                second = result[1]
                print(f"  추천 2순위: {second['material_name']} (점수: {second['score']})")
        else:
            print(f"  추천: 없음")
        print()


scenario_comparison()


# ============================================================
# 6단계: 재료 비교표 생성
# ============================================================

print()
print("-" * 60)
print("6단계: 재료 비교표 생성")
print("-" * 60)


def material_comparison_table(material_list):
    """
    여러 재료의 속성을 표 형태로 비교합니다.

    매개변수:
        material_list (list): 비교할 재료명 목록
    """
    print("[재료 비교표]")
    print()

    # 헤더
    header = f"  {'속성':<16}"
    for name in material_list:
        header += f" {name[:12]:>12}"
    print(header)
    print(f"  {'-' * (16 + 14 * len(material_list))}")

    # 속성별 비교
    comparison_items = [
        ("분류", "분류"),
        ("파괴응력(MPa)", "파괴응력_MPa"),
        ("항복응력(MPa)", "항복응력_MPa"),
        ("탄성계수(GPa)", "탄성계수_GPa"),
        ("밀도(g/cm3)", "밀도_gcm3"),
        ("최대온도(C)", "가열온도_max_C"),
        ("내식성", "내식성"),
        ("가공성", "가공성"),
        ("비용등급", "비용등급"),
        ("용접가능", "용접가능"),
    ]

    for display_name, key in comparison_items:
        row = f"  {display_name:<16}"
        for name in material_list:
            val = material_db.get(name, {}).get(key, "N/A")
            if isinstance(val, bool):
                val = "가능" if val else "불가"
            row += f" {str(val):>12}"
        print(row)

    print()
    print("[가격 대비 성능 지수 (단위 비용당 응력)]")
    for name in material_list:
        mat = material_db.get(name, {})
        cost = mat.get("비용등급", 1)
        stress = mat.get("항복응력_MPa", 0)
        if cost > 0:
            index = stress / cost
            print(f"  {name}: {index:.1f} MPa/비용단위")


# 주요 금속재료 비교
print("[주요 금속재료 비교]")
metal_materials = ["탄소강_S45C", "합금강_SCM440", "스테인리스_304",
             "알루미늄_6061_T6", "티타늄_Ti6Al4V"]
material_comparison_table(metal_materials)


# ============================================================
# 7단계: FreeCAD 적용 스크립트 생성
# ============================================================

print()
print("-" * 60)
print("7단계: FreeCAD 적용 안내")
print("-" * 60)


def freecad_material_info(material_name):
    """
    추천된 재료의 FreeCAD 재료 속성을 생성합니다.

    매개변수:
        material_name (str): 추천된 재료명

    반환값:
        str: FreeCAD 재료 설정 스크립트
    """
    mat = material_db.get(material_name)
    if not mat:
        return "# 재료 정보를 찾을 수 없습니다."

    script = f'# -*- coding: utf-8 -*-\n'
    script += f'# 추천 재료: {material_name}\n'
    script += f'# 분류: {mat["분류"]}\n'
    script += f'# 용도: {mat["사용예"]}\n\n'

    script += 'import FreeCAD\n\n'

    script += f'# 재료 정보 출력\n'
    script += f'print("추천 재료: {material_name}")\n'
    script += f'print("파괴응력: {mat["파괴응력_MPa"]} MPa")\n'
    script += f'print("항복응력: {mat["항복응력_MPa"]} MPa")\n'
    script += f'print("탄성계수: {mat["탄성계수_GPa"]} GPa")\n'
    script += f'print("밀도: {mat["밀도_gcm3"]} g/cm3")\n'
    script += f'print("최대 사용 온도: {mat["가열온도_max_C"]} C")\n'
    script += f'print("내식성: {mat["내식성"]}")\n'
    script += f'print("용도: {mat["사용예"]}")\n'

    return script


# 추천 재료 정보 출력
if rule_result:
    best_material = rule_result[0]["material_name"]
    print(f"\n[최종 추천] {best_material}")
    print(freecad_material_info(best_material))


# ============================================================
# 최종 요약
# ============================================================

print()
print("=" * 60)
print("파일 24 학습 완료!")
print("=" * 60)
print("""
 학습한 내용:
  1. 재료 데이터베이스 구축 (금속, 플라스틱, 복합재료, 세라믹)
  2. 사용 조건 정의 (하중, 온도, 환경, 요구사항)
  3. 규칙 기반 재료 추천 알고리즘
  4. AI 기반 재료 추천
  5. 여러 시나리오 비교 분석
  6. 재료 비교표 작성
  7. FreeCAD 적용 정보 생성

 재료 선택 핵심 원칙:
  1. 기계적 요구사항 충족 (하중, 응력)
  2. 환경 적합성 (온도, 부식)
  3. 경제성 (비용 대비 성능)
  4. 제작 가능성 (가공성, 용접성)
  5. 안전율 확보

 다음 파일: 25_ai_review.py (AI 검수)
""")

# -*- coding: utf-8 -*-
"""
파일 21: FreeCAD에서 AI API 호출하기
=====================================
OpenAI API를 FreeCAD 매크로에서 호출하는 방법을 학습합니다.

학습 목표:
- openai 라이브러리 설치 및 사용법 이해
- API 키 관리 및 보안 처리
- 기본 completion 호출 방법
- FreeCAD 스크립트 생성 요청 방법

사용 방법:
1. 터미널에서 pip install openai 실행
2. OpenAI API 키 발급 (https://platform.openai.com)
3. 환경변수에 API 키 설정 또는 스크립트에 직접 입력
4. FreeCAD에서 이 파일 열고 실행

필요한 패키지: openai
설치 명령: pip install openai
"""

import sys
import os

# ============================================================
# 1단계: openai 라이브러리 확인 및 안내
# ============================================================

print("=" * 60)
print("파일 21: FreeCAD에서 AI API 호출하기")
print("=" * 60)

# openai 라이브러리 존재 여부 확인
try:
    import openai
    print("[성공] openai 라이브러리가 설치되어 있습니다.")
    print(f"  - 라이브러리 버전: {openai.__version__}")
except ImportError:
    print("[오류] openai 라이브러리가 설치되어 있지 않습니다.")
    print("  - 설치 명령: pip install openai")
    print("  - 또는: pip3 install openai")
    print("  - FreeCAD 자체 Python에서도 설치 가능:")
    print("    FreeCAD 설치경로/bin/python -m pip install openai")
    print()
    print("설치 후 다시 실행해 주세요.")
    sys.exit(1)


# ============================================================
# 2단계: API 키 관리
# ============================================================

print()
print("-" * 60)
print("2단계: API 키 관리")
print("-" * 60)

# API 키 설정 방법 설명
print("""
API 키 관리 방법 (보안 순서대로):

방법 1 (권장): 환경변수 사용
  - Windows PowerShell: $env:OPENAI_API_KEY = "your-key-here"
  - 또는 시스템 환경변수로 영구 설정

방법 2: .env 파일 사용
  - 프로젝트 루트에 .env 파일 생성
  - 내용: OPENAI_API_KEY=your-key-here
  - python-dotenv 라이브러리로 로드

방법 3 (학습용): 코드에 직접 입력 (실무에서는 절대 사용 금지)
""")

# 환경변수에서 API 키 읽기
api_key = os.environ.get("OPENAI_API_KEY", "")

# 환경변수가 없으면 로컬 설정 파일 시도
if not api_key:
    try:
        # .env 파일에서 로드 시도
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENAI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        print("[정보] .env 파일에서 API 키를 로드했습니다.")
                        break
    except Exception as e:
        print(f"[경고] .env 파일 읽기 실패: {e}")

if api_key:
    print(f"[정보] API 키가 설정되었습니다. (키 앞 8자리: {api_key[:8]}...)")
    print("[보안] API 키는 전체가 출력되지 않도록 마스킹됩니다.")
else:
    print("[경고] API 키가 설정되지 않았습니다.")
    print("  - 환경변수 OPENAI_API_KEY를 설정해 주세요.")
    print("  - API 키 없이도 코드 구조는 학습할 수 있습니다.")


# ============================================================
# 3단계: OpenAI 클라이언트 생성
# ============================================================

print()
print("-" * 60)
print("3단계: OpenAI 클라이언트 생성")
print("-" * 60)

# OpenAI 클라이언트 초기화
client = None
if api_key:
    try:
        client = openai.OpenAI(api_key=api_key)
        print("[성공] OpenAI 클라이언트가 생성되었습니다.")
    except Exception as e:
        print(f"[오류] 클라이언트 생성 실패: {e}")
else:
    print("[정보] API 키가 없어 클라이언트를 생성하지 않습니다.")
    print("  - 아래 코드 구조를 참고하여 직접 실행해 보세요.")


# ============================================================
# 4단계: 기본 Completion 호출
# ============================================================

print()
print("-" * 60)
print("4단계: 기본 Completion 호출")
print("-" * 60)


def basic_call_example():
    """
    기본적인 Chat Completion API 호출 예제입니다.
    가장 단순한 형태의 AI 요청을 보여줍니다.
    """
    if not client:
        print("[건너뜀] API 키가 없어 기본 호출을 건너뜁니다.")
        print("  - 아래 코드를 참고하여 직접 실행해 보세요.")
        print()
        print("  # 직접 실행 예제:")
        print('  response = client.chat.completions.create(')
        print('      model="gpt-3.5-turbo",')
        print('      messages=[')
        print('          {"role": "system", "content": "당신은 FreeCAD 전문가입니다."},')
        print('          {"role": "user", "content": "FreeCAD에서 상자를 만드는 법을 알려주세요."}')
        print('      ],')
        print('      temperature=0.7')
        print('  )')
        print('  print(response.choices[0].message.content)')
        return None

    try:
        # Chat Completion API 호출
        response = client.chat.completions.create(
            # 모델 선택 (gpt-3.5-turbo는 빠르고 저렴, gpt-4는 더 정확)
            model="gpt-3.5-turbo",
            # 대화 메시지 목록
            messages=[
                # 시스템 메시지: AI의 역할과 페르소나를 설정
                {
                    "role": "system",
                    "content": (
                        "당신은 FreeCAD Python 매크로 전문가입니다. "
                        "FreeCAD 스크립트 작성법을 잘 알고 있으며, "
                        "한국어로 명확하게 답변합니다."
                    )
                },
                # 사용자 메시지: 실제 질문이나 요청
                {
                    "role": "user",
                    "content": "FreeCAD에서 상자(Box)를 만드는 기본 Python 코드를 보여주세요."
                }
            ],
            # temperature: 출력의 무작위성 조절 (0.0 ~ 2.0)
            # 0.0 = 가장 정확한 답변, 1.0 = 창의적인 답변
            temperature=0.7,
            # 최대 토큰 수 (응답 길이 제한)
            max_tokens=500
        )

        # 응답에서 텍스트 추출
        response_text = response.choices[0].message.content
        print("[응답] AI 기본 호출 결과:")
        print("-" * 40)
        print(response_text)
        print("-" * 40)

        # 사용량 정보 출력
        if response.usage:
            print(f"  - 프롬프트 토큰: {response.usage.prompt_tokens}")
            print(f"  - 완료 토큰: {response.usage.completion_tokens}")
            print(f"  - 총 토큰: {response.usage.total_tokens}")

        return response_text

    except openai.AuthenticationError:
        print("[오류] API 키가 유효하지 않습니다. 키를 확인해 주세요.")
    except openai.RateLimitError:
        print("[오류] API 호출 한도를 초과했습니다. 잠시 후 다시 시도해 주세요.")
    except openai.APIError as e:
        print(f"[오류] API 호출 중 오류 발생: {e}")
    except Exception as e:
        print(f"[예상치 못한 오류] {e}")

    return None


# 기본 호출 실행
basic_call_example()


# ============================================================
# 5단계: FreeCAD 스크립트 생성 요청
# ============================================================

print()
print("-" * 60)
print("5단계: FreeCAD 스크립트 생성 요청")
print("-" * 60)


def script_generation_request(request_desc):
    """
    AI에게 FreeCAD Python 스크립트를 생성하도록 요청합니다.

    매개변수:
        request_desc (str): 생성할 스크립트에 대한 설명

    반환값:
        str: 생성된 Python 스크립트 코드
    """
    if not client:
        print("[건너뜀] API 키가 없어 스크립트 생성을 건너뜁니다.")
        print("  - 아래 프롬프트 구조를 참고하세요.")
        return None

    try:
        # FreeCAD 스크립트 전용 시스템 프롬프트
        system_prompt = """당신은 FreeCAD Python 매크로 작성 전문가입니다.
다음 규칙을 반드시 따라주세요:
1. import 문은 import FreeCAD, import Part 만 사용합니다
2. 모든 코드는 FreeCAD 호환 버전 0.20 이상을 기준으로 작성합니다
3. 코드에 주석을 한국어로 작성합니다
4. 실행 가능한 완전한 스크립트만 반환합니다
5. 추가 설명 없이 코드만 반환합니다
6. 코드는 ```python과 ```로 감싸주세요"""

        # 사용자 요청
        user_request = f"FreeCAD에서 다음 부품을 만드는 Python 스크립트를 작성해 주세요:\n{request_desc}"

        # API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_request}
            ],
            temperature=0.3,  # 스크립트 생성은 낮은 temperature 사용
            max_tokens=2000
        )

        answer = response.choices[0].message.content

        # 코드 블록 추출 (마크다운 코드 블록에서)
        if "```python" in answer:
            # ```python과 ``` 사이의 코드만 추출
            start_pos = answer.find("```python") + len("```python")
            end_pos = answer.find("```", start_pos)
            if end_pos != -1:
                code = answer[start_pos:end_pos].strip()
            else:
                code = answer[start_pos:].strip()
        elif "```" in answer:
            start_pos = answer.find("```") + 3
            end_pos = answer.find("```", start_pos)
            if end_pos != -1:
                code = answer[start_pos:end_pos].strip()
            else:
                code = answer[start_pos:].strip()
        else:
            code = answer.strip()

        print("[생성된 스크립트]")
        print("=" * 40)
        print(code)
        print("=" * 40)

        return code

    except openai.AuthenticationError:
        print("[오류] API 키가 유효하지 않습니다.")
    except Exception as e:
        print(f"[오류] 스크립트 생성 실패: {e}")

    return None


# 스크립트 생성 요청 예제
print("[요청] M10 육각 볼트 (길이 30mm) 스크립트 생성 요청 중...")
result = script_generation_request("M10 육각 볼트, 나사 길이 30mm, 피치 1.5mm")


# ============================================================
# 6단계: 여러 모델 비교 호출
# ============================================================

print()
print("-" * 60)
print("6단계: 여러 모델 비교 호출")
print("-" * 60)


def model_comparison_call(question):
    """
    여러 AI 모델에게 같은 질문을 하여 결과를 비교합니다.

    매개변수:
        question (str): AI에게 할 질문

    반환값:
        dict: 모델별 응답 결과
    """
    if not client:
        print("[건너뜀] API 키가 없어 모델 비교를 건너뜁니다.")
        return {}

    # 비교할 모델 목록
    model_list = [
        ("gpt-3.5-turbo", "GPT-3.5 Turbo (빠름, 저렴)"),
        ("gpt-4", "GPT-4 (정확, 비쌈)"),
    ]

    result = {}

    for model_name, desc in model_list:
        print(f"\n  [호출] {desc}...")
        try:
            import time
            start_time = time.time()

            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "FreeCAD 전문가입니다."},
                    {"role": "user", "content": question}
                ],
                temperature=0.5,
                max_tokens=500
            )

            end_time = time.time()
            elapsed_time = end_time - start_time

            answer = response.choices[0].message.content
            token_count = response.usage.total_tokens if response.usage else 0

            result[model_name] = {
                "response": answer,
                "elapsed_time": elapsed_time,
                "token_count": token_count
            }

            print(f"  - 소요 시간: {elapsed_time:.2f}초")
            print(f"  - 사용 토큰: {token_count}")
            print(f"  - 응답 미리보기: {answer[:100]}...")

        except Exception as e:
            print(f"  [오류] {model_name} 호출 실패: {e}")
            result[model_name] = {"error": str(e)}

    return result


# 모델 비교 실행
print("[실행] 같은 질문으로 여러 모델 비교...")
comparison_result = model_comparison_call("FreeCAD에서 실린더를 만드는 코드를 한 줄로 요약해주세요.")


# ============================================================
# 7단계: API 사용 팁 및 주의사항
# ============================================================

print()
print("-" * 60)
print("7단계: API 사용 팁 및 주의사항")
print("-" * 60)

print("""
 FreeCAD에서 AI API를 사용할 때 알아두면 유용한 팁:

 1. 토큰 관리
    - GPT 모델은 토큰 단위로 과금됩니다
    - 프롬프트를 효율적으로 작성하여 토큰을 절약하세요
    - 시스템 프롬프트는 간결하게 작성하세요

 2. Temperature 설정
    - 0.0 ~ 0.3: 정확한 답변이 필요할 때 (코드 생성, 데이터 추출)
    - 0.5 ~ 0.7: 일반적인 대화 (설명, 분석)
    - 0.8 ~ 1.0: 창의적인 답변이 필요할 때 (아이디어 생성)

 3. FreeCAD 통합 시 주의사항
    - AI가 생성한 코드는 반드시 검증 후 실행하세요
    - import 문이 FreeCAD 호환인지 확인하세요
    - exec()나 eval()로 실행하지 마세요 (보안 위험)
    - 생성된 코드를 파일로 저장 후 검토하세요

 4. 에러 처리
    - API 호출 시 반드시 try/except로 감싸세요
    - RateLimitError 처리: 시간차 두고 재시도
    - AuthenticationError: API 키 확인

 5. 오프라인 대안
    - API 사용이 어려운 경우 사전 정의된 규칙 기반 로직 사용
    - 조건문과 수학 공식으로 충분히 자동화 가능
    - 오픈소스 모델 (ollama + codellama) 활용 가능
""")


# ============================================================
# 8단계: 실전 예제 - FreeCAD 부품 설명 생성
# ============================================================

print()
print("-" * 60)
print("8단계: 실전 예제 - FreeCAD 부품 설명 생성")
print("-" * 60)


def part_description_generation(part_name, params):
    """
    AI에게 부품 정보를 전달하여 상세 설명을 생성합니다.

    매개변수:
        part_name (str): 부품의 이름
        params (dict): 부품의 치수 및 속성

    반환값:
        str: AI가 생성한 부품 설명
    """
    if not client:
        # API 없이도 동작하는 기본 설명 생성
        description = f"[기본 설명] {part_name}\n"
        for key, value in params.items():
            description += f"  - {key}: {value}\n"
        description += "\n[참고] API 키를 설정하면 AI의 상세 설명을 받을 수 있습니다."
        print(description)
        return description

    try:
        # 매개변수를 텍스트로 변환
        params_text = "\n".join(
            f"  - {key}: {value}" for key, value in params.items()
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 기계 설계 전문가입니다. 부품에 대한 전문적이고 상세한 설명을 한국어로 작성합니다."
                },
                {
                    "role": "user",
                    "content": (
                        f"다음 부품에 대해 상세히 설명해주세요:\n"
                        f"부품명: {part_name}\n"
                        f"매개변수:\n{params_text}\n\n"
                        f"다음 항목을 포함해주세요:\n"
                        f"1. 부품의 용도\n"
                        f"2. 주요 치수 설명\n"
                        f"3. FreeCAD에서 제작 시 주의사항\n"
                        f"4. 관련 표준 (KS, ISO 등)"
                    )
                }
            ],
            temperature=0.5,
            max_tokens=800
        )

        description = response.choices[0].message.content
        print(f"[부품 설명] {part_name}")
        print("-" * 40)
        print(description)
        return description

    except Exception as e:
        print(f"[오류] 부품 설명 생성 실패: {e}")
        return None


# 부품 설명 생성 실행
part_description_generation(
    part_name="M10 육각 볼트",
    params={
        "크기": "M10",
        "길이": "30mm",
        "나사 피치": "1.5mm",
        "머리 높이": "7mm",
        "모양": "육각 머리"
    }
)


# ============================================================
# 최종 요약
# ============================================================

print()
print("=" * 60)
print("파일 21 학습 완료!")
print("=" * 60)
print("""
 학습한 내용:
  1. openai 라이브러리 설치 및 확인
  2. API 키 관리 (환경변수, .env 파일)
  3. OpenAI 클라이언트 생성
  4. 기본 Chat Completion API 호출
  5. FreeCAD 스크립트 생성 요청
  6. 여러 모델 비교 호출
  7. API 사용 팁 및 보안 주의사항
  8. 실전 예제: 부품 설명 자동 생성

 다음 파일: 22_text_to_script.py (텍스트에서 스크립트 변환)
""")

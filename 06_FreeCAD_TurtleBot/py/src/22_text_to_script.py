# -*- coding: utf-8 -*-
"""
파일 22: 텍스트에서 스크립트 변환
==================================
자연어 텍스트를 입력하면 AI가 FreeCAD Python 스크립트를 생성합니다.

학습 목표:
- 자연어 → FreeCAD 스크립트 자동 변환
- "M10 볼트, 길이 30mm" 같은 텍스트 입력 처리
- AI가 생성한 스크립트의 안전한 실행 방법
- eval(), exec() 보안 위험 이해 및 대안

사용 방법:
1. 파일 21에서 openai 설치 완료 필요
2. OpenAI API 키 설정 필요
3. FreeCAD에서 이 파일 열고 실행

필요한 패키지: openai
"""

import sys
import os
import re
import tempfile

print("=" * 60)
print("파일 22: 텍스트에서 스크립트 변환")
print("=" * 60)

# openai 라이브러리 확인
try:
    import openai
    has_openai = True
    print("[정보] openai 라이브러리 사용 가능")
except ImportError:
    has_openai = False
    print("[정보] openai 라이브러리가 없습니다.")
    print("  - 설치: pip install openai")
    print("  - 오프라인 모드(규칙 기반)로 동작합니다.")


# ============================================================
# 1단계: API 설정
# ============================================================

print()
print("-" * 60)
print("1단계: API 설정")
print("-" * 60)

# API 키 로드
api_key = os.environ.get("OPENAI_API_KEY", "")
client = None

if has_openai and api_key:
    try:
        client = openai.OpenAI(api_key=api_key)
        print("[성공] OpenAI 클라이언트 연결됨")
    except Exception as e:
        print(f"[오류] 클라이언트 생성 실패: {e}")
elif not api_key:
    print("[정보] API 키 미설정 - 오프라인 모드로 동작")
else:
    print("[정보] openai 미설치 - 오프라인 모드로 동작")


# ============================================================
# 2단계: 텍스트 파서 (오프라인 규칙 기반)
# ============================================================

print()
print("-" * 60)
print("2단계: 텍스트 파서 (규칙 기반 변환)")
print("-" * 60)


def 텍스트_파싱(텍스트):
    """
    사용자 입력 텍스트를 분석하여 부품 정보를 추출합니다.
    AI 없이도 동작하는 규칙 기반 파서입니다.

    지원하는 패턴:
    - M10, M8 같은 나사 크기
    - 길이, 높이, 두께 등 치수
    - 볼트, 너트, 와셔 같은 부품 유형
    - 실린더, 상자, 구 같은 기본 형상

    매개변수:
        텍스트 (str): 사용자가 입력한 설명 텍스트

    반환값:
        dict: 파싱된 부품 정보
    """
    파싱_결과 = {
        "부품유형": "알수없음",
        "크기": {},
        "형상": [],
        "재료": "알수없음",
        "원본텍스트": 텍스트
    }

    텍스트_소문자 = 텍스트.lower()

    # --- 부품 유형 검출 ---
    볼트_패턴 = re.compile(r'(m\d+)\s*(?:볼트|bolt|나사|스 crew)', re.IGNORECASE)
    볼트_매치 = 볼트_패턴.search(텍스트)
    if 볼트_매치:
        파싱_결과["부품유형"] = "볼트"
        파싱_결과["크기"]["나사크기"] = 볼트_매치.group(1).upper()
    elif "너트" in 텍스트 or "nut" in 텍스트_소문자:
        파싱_결과["부품유형"] = "너트"
    elif "와셔" in 텍스트 or "washer" in 텍스트_소문자:
        파싱_결과["부품유형"] = "와셔"
    elif "축" in 텍스트 or "shaft" in 텍스트_소문자:
        파싱_결과["부품유형"] = "축"
    elif "기어" in 텍스트 or "gear" in 텍스트_소문자:
        파싱_결과["부품유형"] = "기어"
    elif "베어링" in 텍스트 or "bearing" in 텍스트_소문자:
        파싱_결과["부품유형"] = "베어링"

    # --- 치수 추출 ---
    # 길이 패턴: "길이 30mm", "30mm", "30 mm"
    길이_패턴 = re.compile(r'(?:길이|length|long|높이|height)\s*[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|cm|m)', re.IGNORECASE)
    길이_매치 = 길이_패턴.search(텍스트)
    if 길이_매치:
        파싱_결과["크기"]["길이"] = float(길이_매치.group(1))

    # 직접 치수 입력: "30mm"
    mm_패턴 = re.compile(r'(\d+(?:\.\d+)?)\s*mm')
    mm_매치 = mm_패턴.findall(텍스트)
    if mm_매치 and "길이" not in 파싱_결과["크기"]:
        파싱_결과["크기"]["치수_mm"] = [float(m) for m in mm_매치]

    # 지름 패턴
    지름_패턴 = re.compile(r'(?:지름|diameter|Ø|D)\s*[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|cm)?', re.IGNORECASE)
    지름_매치 = 지름_패턴.search(텍스트)
    if 지름_매치:
        파싱_결과["크기"]["지름"] = float(지름_매치.group(1))

    # 두께 패턴
    두께_패턴 = re.compile(r'(?:두께|thickness|t)\s*[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|cm)?', re.IGNORECASE)
    두께_매치 = 두께_패턴.search(텍스트)
    if 두께_매치:
        파싱_결과["크기"]["두께"] = float(두께_매치.group(1))

    # --- 형상 검출 ---
    if "원형" in 텍스트 or "원" in 텍스트 or "circle" in 텍스트_소문자:
        파싱_결과["형상"].append("원")
    if "상자" in 텍스트 or "직사각" in 텍스트 or "box" in 텍스트_소문자:
        파싱_결과["형상"].append("상자")
    if "실린더" in 텍스트 or "원통" in 텍스트 or "cylinder" in 텍스트_소문자:
        파싱_결과["형상"].append("실린더")
    if "구" in 텍스트 or "sphere" in 텍스트_소문자:
        파싱_결과["형상"].append("구")

    # --- 재료 추출 ---
    if "강" in 텍스트 or "steel" in 텍스트_소문자:
        파싱_결과["재료"] = "강"
    elif "알루미늄" in 텍스트 or "aluminum" in 텍스트_소문자:
        파싱_결과["재료"] = "알루미늄"
    elif "플라스틱" in 텍스트 or "plastic" in 텍스트_소문자:
        파싱_결과["재료"] = "플라스틱"
    elif "구리" in 텍스트 or "copper" in 텍스트_소문자:
        파싱_결과["재료"] = "구리"

    return 파싱_결과


# 파싱 테스트
print("[테스트] 텍스트 파싱 기능 테스트")
테스트_텍스트들 = [
    "M10 볼트, 길이 30mm",
    "지름 50mm 실린더, 높이 100mm",
    "두께 5mm 알루미늄 상자, 가로 200mm 세로 100mm",
    "M8 너트",
    "강철 축, 지름 20mm, 길이 150mm"
]

for 텍스트 in 테스트_텍스트들:
    결과 = 텍스트_파싱(텍스트)
    print(f"\n  입력: \"{텍스트}\"")
    print(f"  결과: 부품유형={결과['부품유형']}, 크기={결과['크기']}, 재료={결과['재료']}")


# ============================================================
# 3단계: 규칙 기반 스크립트 생성 (오프라인)
# ============================================================

print()
print("-" * 60)
print("3단계: 규칙 기반 스크립트 생성 (오프라인)")
print("-" * 60)


def 규칙_스크립트_생성(파싱정보):
    """
    파싱된 정보를 바탕으로 규칙에 따라 FreeCAD 스크립트를 생성합니다.
    AI 없이도 동작하는 오프라인 방식입니다.

    매개변수:
        파싱정보 (dict): 텍스트_파싱() 함수의 반환값

    반환값:
        str: 생성된 FreeCAD Python 스크립트
    """

    스크립트 = '# -*- coding: utf-8 -*-\n'
    스크립트 += '# 자동 생성된 FreeCAD 스크립트\n'
    스크립트 += f'# 원본 텍스트: {파싱정보["원본텍스트"]}\n'
    스크립트 += '# 생성 방법: 규칙 기반 자동 생성\n\n'
    스크립트 += 'import FreeCAD\n'
    스크립트 += 'import Part\n\n'

    부품유형 = 파싱정보["부품유형"]
    크기 = 파싱정보["크기"]

    if 부품유형 == "볼트":
        나사크기 = 크기.get("나사크기", "M10")
        # 나사 크기에서 숫자 추출
        숫자_매치 = re.search(r'(\d+)', 나사크기)
        나사_지름 = float(숫자_매치.group(1)) if 숫자_매치 else 10.0
        길이 = 크기.get("길이", 30.0)

        스크립트 += f'# 볼트 생성 - {나사크기}, 길이 {길이}mm\n'
        스크립트 += 'doc = FreeCAD.newDocument("볼트")\n\n'
        스크립트 += f'# 볼트 몸체 (실린더)\n'
        스크립트 += f'몸체 = doc.addObject("Part::Cylinder", "몸체")\n'
        스크립트 += f'몸체.Radius = {나사_지름 / 2}\n'
        스크립트 += f'몸체.Height = {길이}\n\n'
        스크립트 += f'# 육각 머리\n'
        스크립트 += f'머리 = doc.addObject("Part::Cylinder", "머리")\n'
        스크립트 += f'머리.Radius = {나사_지름 * 0.8}\n'
        스크립트 += f'머리.Height = {나사_지름 * 0.7}\n'
        스크립트 += f'머리.Placement = FreeCAD.Placement(\n'
        스크립트 += f'    FreeCAD.Vector(0, 0, {길이}),\n'
        스크립트 += f'    FreeCAD.Rotation(0, 0, 0)\n'
        스크립트 += f')\n\n'
        스크립트 += f'FreeCAD.ActiveDocument.recompute()\n'
        스크립트 += f'print("[성공] 볼트 생성 완료")\n'

    elif 부품유형 == "축":
        지름 = 크기.get("지름", 20.0)
        길이 = 크기.get("길이", 100.0)

        스크립트 += f'# 축 생성 - 지름 {지름}mm, 길이 {길이}mm\n'
        스크립트 += 'doc = FreeCAD.newDocument("축")\n\n'
        스크립트 += '축 = doc.addObject("Part::Cylinder", "축")\n'
        스크립트 += f'축.Radius = {지름 / 2}\n'
        스크립트 += f'축.Height = {길이}\n\n'
        스크립트 += 'FreeCAD.ActiveDocument.recompute()\n'
        스크립트 += 'print("[성공] 축 생성 완료")\n'

    elif "실린더" in 파싱정보["형상"] or 부품유형 == "알수없음" and "지름" in 크기:
        지름 = 크기.get("지름", 50.0)
        길이 = 크기.get("길이", 크기.get("치수_mm", [100.0])[0] if 크기.get("치수_mm") else 100.0)

        스크립트 += f'# 실린더 생성 - 지름 {지름}mm, 높이 {길이}mm\n'
        스크립트 += 'doc = FreeCAD.newDocument("실린더")\n\n'
        스크립트 += '실린더 = doc.addObject("Part::Cylinder", "실린더")\n'
        스크립트 += f'실린더.Radius = {지름 / 2}\n'
        스크립트 += f'실린더.Height = {길이}\n\n'
        스크립트 += 'FreeCAD.ActiveDocument.recompute()\n'
        스크립트 += 'print("[성공] 실린더 생성 완료")\n'

    elif "상자" in 파싱정보["형상"]:
        두께 = 크기.get("두께", 5.0)
        가로 = 크기.get("치수_mm", [200.0])[0] if 크기.get("치수_mm") else 200.0
        세로 = 크기.get("치수_mm", [0.0, 100.0])[1] if len(크기.get("치수_mm", [])) > 1 else 100.0
        높이 = 크기.get("길이", 50.0)

        스크립트 += f'# 상자 생성 - {가로}x{세로}x{높이}mm\n'
        스크립트 += 'doc = FreeCAD.newDocument("상자")\n\n'
        스크립트 += '상자 = doc.addObject("Part::Box", "상자")\n'
        스크립트 += f'상자.Length = {가로}\n'
        스크립트 += f'상자.Width = {세로}\n'
        스크립트 += f'상자.Height = {높이}\n\n'
        스크립트 += 'FreeCAD.ActiveDocument.recompute()\n'
        스크립트 += 'print("[성공] 상자 생성 완료")\n'

    else:
        # 기본 상자 생성
        스크립트 += '# 기본 형상 생성\n'
        스크립트 += 'doc = FreeCAD.newDocument("자동생성")\n\n'
        스크립트 += '상자 = doc.addObject("Part::Box", "상자")\n'
        스크립트 += '상자.Length = 50.0\n'
        스크립트 += '상자.Width = 50.0\n'
        스크립트 += '상자.Height = 50.0\n\n'
        스크립트 += 'FreeCAD.ActiveDocument.recompute()\n'
        스크립트 += 'print("[정보] 기본 상자 생성 - 치수를 지정해 주세요")\n'

    return 스크립트


# 규칙 기반 스크립트 생성 테스트
print("[테스트] 규칙 기반 스크립트 생성")
테스트_입력 = "지름 50mm 실린더, 높이 100mm"
파싱 = 텍스트_파싱(테스트_입력)
스크립트 = 규칙_스크립트_생성(파싱)
print(f"\n입력 텍스트: \"{테스트_입력}\"")
print("생성된 스크립트:")
print("-" * 40)
print(스크립트)
print("-" * 40)


# ============================================================
# 4단계: AI 기반 스크립트 생성 (온라인)
# ============================================================

print()
print("-" * 60)
print("4단계: AI 기반 스크립트 생성 (온라인)")
print("-" * 60)


def AI_스크립트_생성(텍스트_입력):
    """
    AI에게 자연어 텍스트를 전달하여 FreeCAD 스크립트를 생성합니다.
    API 키가 없으면 규칙 기반 생성으로 자동 전환됩니다.

    매개변수:
        텍스트_입력 (str): 사용자의 자연어 설명

    반환값:
        str: FreeCAD Python 스크립트
    """
    if not client:
        print("[정보] API 미연결 - 규칙 기반 생성 사용")
        파싱 = 텍스트_파싱(텍스트_입력)
        return 규칙_스크립트_생성(파싱)

    try:
        # AI에게 전달할 시스템 프롬프트
        시스템_프롬프트 = """당신은 FreeCAD Python 스크립트 생성 전문가입니다.

규칙:
1. 사용자가 부품을 텍스트로 설명하면 FreeCAD Python 코드를 생성합니다
2. import 문은 반드시 import FreeCAD, import Part 만 사용합니다
3. 모든 주석은 한국어로 작성합니다
4. 코드만 반환하고 설명은 포함하지 않습니다
5. 코드는 ```python과 ```로 감싸주세요
6. doc = FreeCAD.newDocument()로 시작합니다
7. FreeCAD.ActiveDocument.recompute()로 끝납니다"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 시스템_프롬프트},
                {"role": "user", "content": f"다음 설명을 FreeCAD Python 스크립트로 변환해주세요:\n{텍스트_입력}"}
            ],
            temperature=0.2,
            max_tokens=1500
        )

        응답 = response.choices[0].message.content

        # 코드 블록 추출
        코드 = 코드_블록_추출(응답)

        print(f"[AI 생성] 입력: \"{텍스트_입력}\"")
        print("생성된 스크립트:")
        print("-" * 40)
        print(코드)
        print("-" * 40)

        return 코드

    except Exception as e:
        print(f"[오류] AI 스크립트 생성 실패: {e}")
        print("[대체] 규칙 기반 생성으로 전환합니다.")
        파싱 = 텍스트_파싱(텍스트_입력)
        return 규칙_스크립트_생성(파싱)


def 코드_블록_추출(텍스트):
    """
    마크다운 텍스트에서 Python 코드 블록을 추출합니다.

    매개변수:
        텍스트 (str): 마크다운 형식의 텍스트

    반환값:
        str: 추출된 Python 코드
    """
    if "```python" in 텍스트:
        시작 = 텍스트.find("```python") + len("```python")
        끝 = 텍스트.find("```", 시작)
        return 텍스트[시작:끝].strip() if 끝 != -1 else 텍스트[시작:].strip()
    elif "```" in 텍스트:
        시작 = 텍스트.find("```") + 3
        끝 = 텍스트.find("```", 시작)
        return 텍스트[시작:끝].strip() if 끝 != -1 else 텍스트[시작:].strip()
    return 텍스트.strip()


# AI 스크립트 생성 실행
AI_스크립트_생성("M12 볼트, 길이 40mm, 육각 머리")


# ============================================================
# 5단계: 안전한 스크립트 실행 방법
# ============================================================

print()
print("-" * 60)
print("5단계: 안전한 스크립트 실행 방법")
print("-" * 60)

print("""
 [중요] 보안 규칙:

  절대 하지 말 것:
  - exec(코드) : 위험! 임의 코드 실행 가능
  - eval(코드) : 위험! 표현식 실행 가능
  - import os; os.system(명령어) : 위험! 시스템 명령 실행

  안전한 방법:
  1. 코드를 파일로 저장 후 FreeCAD에서 열기
  2. FreeCAD의 매크로 실행 기능 사용
  3. 코드 검증 후 실행
""")


def 안전한_스크립트_검증(스크립트_텍스트):
    """
    생성된 스크립트를 안전성 관점에서 검증합니다.

    검증 항목:
    - 위험한 함수 호출 여부
    - 허용되지 않은 import 여부
    - 시스템 명령 실행 여부

    매개변수:
        스크립트_텍스트 (str): 검증할 스크립트

    반환값:
        tuple: (통과여부: bool, 메시지: str)
    """
    위험_패턴들 = [
        (r'\bexec\s*\(', "exec() 호출 감지 - 코드 실행 위험"),
        (r'\beval\s*\(', "eval() 호출 감지 - 표현식 실행 위험"),
        (r'\bos\.system\s*\(', "os.system() 호출 감지 - 시스템 명령 위험"),
        (r'\bsubprocess\.', "subprocess 사용 감지 - 프로세스 실행 위험"),
        (r'\b__import__\s*\(', "__import__() 감지 - 동적 import 위험"),
        (r'\bcompile\s*\(', "compile() 감지 - 동적 컴파일 위험"),
        (r'open\s*\(.+["\']w', "파일 쓰기 감지 - 파일 시스템 변경 위험"),
    ]

    허용_import = {'FreeCAD', 'Part', 'FreeCADGui', 'Drawing', 'Sketcher',
                    'Mesh', 'Spreadsheet', 'math', 're', 'datetime'}

    경고_목록 = []

    # 위험 패턴 검사
    for 패턴, 설명 in 위험_패턴들:
        if re.search(패턴, 스크립트_텍스트):
            경고_목록.append(f"  [위험] {설명}")

    # import 검사
    import_패턴 = re.compile(r'^import\s+(\w+)', re.MULTILINE)
    for 매치 in import_패턴.finditer(스크립트_텍스트):
        모듈명 = 매치.group(1)
        if 모듈명 not in 허용_import:
            경고_목록.append(f"  [주의] 허용되지 않은 import: {모듈명}")

    if 경고_목록:
        print("[검증 결과] ⚠️ 주의사항 발견:")
        for 경고 in 경고_목록:
            print(경고)
        return False, "안전하지 않은 코드가 포함되어 있습니다."

    print("[검증 결과] 안전성 검증 통과")
    return True, "안전합니다."


# 검증 테스트
print("[테스트] 스크립트 안전성 검증")
좋은_스크립트 = """import FreeCAD
import Part
doc = FreeCAD.newDocument("테스트")
상자 = doc.addObject("Part::Box", "상자")
상자.Length = 50
FreeCAD.ActiveDocument.recompute()
"""

나쁜_스크립트 = """import os
os.system("rm -rf /")
"""

print("\n좋은 스크립트 검증:")
안전한_스크립트_검증(좋은_스크립트)

print("\n나쁜 스크립트 검증:")
안전한_스크립트_검증(나쁜_스크립트)


# ============================================================
# 6단계: 파일로 저장하고 FreeCAD에서 실행
# ============================================================

print()
print("-" * 60)
print("6단계: 파일 저장 및 FreeCAD 실행 안내")
print("-" * 60)


def 스크립트_파일_저장(스크립트_텍스트, 파일명="auto_generated.py"):
    """
    스크립트를 파일로 저장합니다.
    저장 후 FreeCAD에서 열어 실행할 수 있습니다.

    매개변수:
        스크립트_텍스트 (str): 저장할 스크립트
        파일명 (str): 저장할 파일명

    반환값:
        str: 저장된 파일의 전체 경로
    """
    # 현재 디렉토리에 저장
    저장_경로 = os.path.join(os.path.dirname(__file__) or ".", 파일명)

    try:
        with open(저장_경로, "w", encoding="utf-8") as f:
            f.write(스크립트_텍스트)
        print(f"[저장] 파일이 저장되었습니다: {저장_경로}")
        print(f"  - FreeCAD에서 파일 > 열기 로 이 파일을 열어주세요")
        print(f"  - 또는 FreeCAD 콘솔에서 실행 가능합니다")
        return 저장_경로
    except Exception as e:
        print(f"[오류] 파일 저장 실패: {e}")
        # 대체 경로: 임시 디렉토리
        try:
            임시_경로 = os.path.join(tempfile.gettempdir(), 파일명)
            with open(임시_경로, "w", encoding="utf-8") as f:
                f.write(스크립트_텍스트)
            print(f"[저장] 임시 경로에 저장됨: {임시_경로}")
            return 임시_경로
        except Exception as e2:
            print(f"[오류] 임시 저장도 실패: {e2}")
            return None


# 생성된 스크립트 저장
저장_결과 = 스크립트_파일_저장(스크립트, "generated_cylinder.py")


# ============================================================
# 7단계: 전체 변환 파이프라인
# ============================================================

print()
print("-" * 60)
print("7단계: 전체 변환 파이프라인")
print("-" * 60)


def 전체_변환_파이프라인(텍스트_입력):
    """
    텍스트 입력부터 스크립트 실행까지의 전체 과정을 수행합니다.

    단계:
    1. 텍스트 파싱 (규칙 기반)
    2. AI 스크립트 생성 (API 있으면) 또는 규칙 기반 생성
    3. 안전성 검증
    4. 파일 저장
    5. FreeCAD 실행 안내

    매개변수:
        텍스트_입력 (str): 사용자의 자연어 설명

    반환값:
        dict: 전체 처리 결과
    """
    print(f"\n[파이프라인 시작] 입력: \"{텍스트_입력}\"")
    print("=" * 40)

    # 1단계: 파싱
    print("\n[1/5] 텍스트 파싱 중...")
    파싱_정보 = 텍스트_파싱(텍스트_입력)
    print(f"  - 부품유형: {파싱_정보['부품유형']}")
    print(f"  - 크기: {파싱_정보['크기']}")
    print(f"  - 형상: {파싱_정보['형상']}")
    print(f"  - 재료: {파싱_정보['재료']}")

    # 2단계: 스크립트 생성
    print("\n[2/5] 스크립트 생성 중...")
    스크립트 = AI_스크립트_생성(텍스트_입력)

    if not 스크립트:
        print("[실패] 스크립트 생성 실패")
        return None

    # 3단계: 안전성 검증
    print("\n[3/5] 안전성 검증 중...")
    통과, 메시지 = 안전한_스크립트_검증(스크립트)

    if not 통과:
        print(f"[경고] 검증 실패: {메시지}")
        print("  - 생성된 코드를 수동으로 검토해 주세요")

    # 4단계: 파일 저장
    print("\n[4/5] 파일 저장 중...")
    안전한_이름 = re.sub(r'[^\w]', '_', 텍스트_입력[:20])
    파일경로 = 스크립트_파일_저장(스크립트, f"generated_{안전한_이름}.py")

    # 5단계: 실행 안내
    print("\n[5/5] 실행 안내")
    print("  FreeCAD에서 실행하는 방법:")
    print("  1. FreeCAD를 엽니다")
    print(f"  2. 파일 > 열기 로 '{파일경로 or '생성된 파일'}'을 엽니다")
    print("  3. 또는 FreeCAD 콘솔(Macro > Execute)에서 실행합니다")
    print("  4. 실행 전 코드를 반드시 검토해 주세요")

    print("\n[파이프라인 완료]")
    print("=" * 40)

    return {
        "원본텍스트": 텍스트_입력,
        "파싱정보": 파싱_정보,
        "스크립트": 스크립트,
        "검증결과": (통과, 메시지),
        "파일경로": 파일경로
    }


# 전체 파이프라인 실행
결과 = 전체_변환_파이프라인("지름 30mm 실린더, 높이 80mm")


# ============================================================
# 최종 요약
# ============================================================

print()
print("=" * 60)
print("파일 22 학습 완료!")
print("=" * 60)
print("""
 학습한 내용:
  1. 자연어 텍스트 파싱 (정규표현식 기반)
  2. 규칙 기반 스크립트 생성 (오프라인)
  3. AI 기반 스크립트 생성 (온라인)
  4. 코드 블록 추출 방법
  5. 스크립트 안전성 검증
  6. 파일 저장 및 FreeCAD 실행 방법
  7. 전체 변환 파이프라인 구성

 보안 핵심:
  - 절대 exec()나 eval()로 AI 코드를 실행하지 마세요
  - 반드시 코드를 파일로 저장하고 검토 후 실행하세요
  - 허용되지 않은 import는 차단하세요

 다음 파일: 23_ai_dimension.py (치수 추천 AI)
""")

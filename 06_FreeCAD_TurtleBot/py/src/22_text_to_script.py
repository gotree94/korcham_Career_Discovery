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


def text_parsing(text):
    """
    사용자 입력 텍스트를 분석하여 부품 정보를 추출합니다.
    AI 없이도 동작하는 규칙 기반 파서입니다.

    지원하는 패턴:
    - M10, M8 같은 나사 크기
    - 길이, 높이, 두께 등 치수
    - 볼트, 너트, 와셔 같은 부품 유형
    - 실린더, 상자, 구 같은 기본 형상

    매개변수:
        text (str): 사용자가 입력한 설명 텍스트

    반환값:
        dict: 파싱된 부품 정보
    """
    parse_result = {
        "part_type": "알수없음",
        "size": {},
        "shape": [],
        "material": "알수없음",
        "original_text": text
    }

    text_lower = text.lower()

    # --- 부품 유형 검출 ---
    bolt_pattern = re.compile(r'(m\d+)\s*(?:볼트|bolt|나사|스 crew)', re.IGNORECASE)
    bolt_match = bolt_pattern.search(text)
    if bolt_match:
        parse_result["part_type"] = "볼트"
        parse_result["size"]["thread_size"] = bolt_match.group(1).upper()
    elif "너트" in text or "nut" in text_lower:
        parse_result["part_type"] = "너트"
    elif "와셔" in text or "washer" in text_lower:
        parse_result["part_type"] = "와셔"
    elif "축" in text or "shaft" in text_lower:
        parse_result["part_type"] = "축"
    elif "기어" in text or "gear" in text_lower:
        parse_result["part_type"] = "기어"
    elif "베어링" in text or "bearing" in text_lower:
        parse_result["part_type"] = "베어링"

    # --- 치수 추출 ---
    # 길이 패턴: "길이 30mm", "30mm", "30 mm"
    length_pattern = re.compile(r'(?:길이|length|long|높이|height)\s*[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|cm|m)', re.IGNORECASE)
    length_match = length_pattern.search(text)
    if length_match:
        parse_result["size"]["length"] = float(length_match.group(1))

    # 직접 치수 입력: "30mm"
    mm_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*mm')
    mm_match = mm_pattern.findall(text)
    if mm_match and "length" not in parse_result["size"]:
        parse_result["size"]["dimensions_mm"] = [float(m) for m in mm_match]

    # 지름 패턴
    diameter_pattern = re.compile(r'(?:지름|diameter|Ø|D)\s*[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|cm)?', re.IGNORECASE)
    diameter_match = diameter_pattern.search(text)
    if diameter_match:
        parse_result["size"]["diameter"] = float(diameter_match.group(1))

    # 두께 패턴
    thickness_pattern = re.compile(r'(?:두께|thickness|t)\s*[:\s]*(\d+(?:\.\d+)?)\s*(?:mm|cm)?', re.IGNORECASE)
    thickness_match = thickness_pattern.search(text)
    if thickness_match:
        parse_result["size"]["thickness"] = float(thickness_match.group(1))

    # --- 형상 검출 ---
    if "원형" in text or "원" in text or "circle" in text_lower:
        parse_result["shape"].append("원")
    if "상자" in text or "직사각" in text or "box" in text_lower:
        parse_result["shape"].append("상자")
    if "실린더" in text or "원통" in text or "cylinder" in text_lower:
        parse_result["shape"].append("실린더")
    if "구" in text or "sphere" in text_lower:
        parse_result["shape"].append("구")

    # --- 재료 추출 ---
    if "강" in text or "steel" in text_lower:
        parse_result["material"] = "강"
    elif "알루미늄" in text or "aluminum" in text_lower:
        parse_result["material"] = "알루미늄"
    elif "플라스틱" in text or "plastic" in text_lower:
        parse_result["material"] = "플라스틱"
    elif "구리" in text or "copper" in text_lower:
        parse_result["material"] = "구리"

    return parse_result


# 파싱 테스트
print("[테스트] 텍스트 파싱 기능 테스트")
test_texts = [
    "M10 볼트, 길이 30mm",
    "지름 50mm 실린더, 높이 100mm",
    "두께 5mm 알루미늄 상자, 가로 200mm 세로 100mm",
    "M8 너트",
    "강철 축, 지름 20mm, 길이 150mm"
]

for text in test_texts:
    result = text_parsing(text)
    print(f"\n  입력: \"{text}\"")
    print(f"  결과: 부품유형={result['part_type']}, 크기={result['size']}, 재료={result['material']}")


# ============================================================
# 3단계: 규칙 기반 스크립트 생성 (오프라인)
# ============================================================

print()
print("-" * 60)
print("3단계: 규칙 기반 스크립트 생성 (오프라인)")
print("-" * 60)


def rule_based_script_generation(parse_info):
    """
    파싱된 정보를 바탕으로 규칙에 따라 FreeCAD 스크립트를 생성합니다.
    AI 없이도 동작하는 오프라인 방식입니다.

    매개변수:
        parse_info (dict): text_parsing() 함수의 반환값

    반환값:
        str: 생성된 FreeCAD Python 스크립트
    """

    script = '# -*- coding: utf-8 -*-\n'
    script += '# 자동 생성된 FreeCAD 스크립트\n'
    script += f'# 원본 텍스트: {parse_info["original_text"]}\n'
    script += '# 생성 방법: 규칙 기반 자동 생성\n\n'
    script += 'import FreeCAD\n'
    script += 'import Part\n\n'

    part_type = parse_info["part_type"]
    size = parse_info["size"]

    if part_type == "볼트":
        thread_size = size.get("thread_size", "M10")
        # 나사 크기에서 숫자 추출
        number_match = re.search(r'(\d+)', thread_size)
        thread_diameter = float(number_match.group(1)) if number_match else 10.0
        length = size.get("length", 30.0)

        script += f'# 볼트 생성 - {thread_size}, 길이 {length}mm\n'
        script += 'doc = FreeCAD.newDocument("볼트")\n\n'
        script += f'# 볼트 몸체 (실린더)\n'
        script += f'body = doc.addObject("Part::Cylinder", "몸체")\n'
        script += f'body.Radius = {thread_diameter / 2}\n'
        script += f'body.Height = {length}\n\n'
        script += f'# 육각 머리\n'
        script += f'head = doc.addObject("Part::Cylinder", "머리")\n'
        script += f'head.Radius = {thread_diameter * 0.8}\n'
        script += f'head.Height = {thread_diameter * 0.7}\n'
        script += f'head.Placement = FreeCAD.Placement(\n'
        script += f'    FreeCAD.Vector(0, 0, {length}),\n'
        script += f'    FreeCAD.Rotation(0, 0, 0)\n'
        script += f')\n\n'
        script += f'FreeCAD.ActiveDocument.recompute()\n'
        script += f'print("[성공] 볼트 생성 완료")\n'

    elif part_type == "축":
        diameter = size.get("diameter", 20.0)
        length = size.get("length", 100.0)

        script += f'# 축 생성 - 지름 {diameter}mm, 길이 {length}mm\n'
        script += 'doc = FreeCAD.newDocument("축")\n\n'
        script += 'shaft = doc.addObject("Part::Cylinder", "축")\n'
        script += f'shaft.Radius = {diameter / 2}\n'
        script += f'shaft.Height = {length}\n\n'
        script += 'FreeCAD.ActiveDocument.recompute()\n'
        script += 'print("[성공] 축 생성 완료")\n'

    elif "실린더" in parse_info["shape"] or part_type == "알수없음" and "diameter" in size:
        diameter = size.get("diameter", 50.0)
        length = size.get("length", size.get("dimensions_mm", [100.0])[0] if size.get("dimensions_mm") else 100.0)

        script += f'# 실린더 생성 - 지름 {diameter}mm, 높이 {length}mm\n'
        script += 'doc = FreeCAD.newDocument("실린더")\n\n'
        script += 'cylinder = doc.addObject("Part::Cylinder", "실린더")\n'
        script += f'cylinder.Radius = {diameter / 2}\n'
        script += f'cylinder.Height = {length}\n\n'
        script += 'FreeCAD.ActiveDocument.recompute()\n'
        script += 'print("[성공] 실린더 생성 완료")\n'

    elif "상자" in parse_info["shape"]:
        thickness_val = size.get("thickness", 5.0)
        width = size.get("dimensions_mm", [200.0])[0] if size.get("dimensions_mm") else 200.0
        depth = size.get("dimensions_mm", [0.0, 100.0])[1] if len(size.get("dimensions_mm", [])) > 1 else 100.0
        height = size.get("length", 50.0)

        script += f'# 상자 생성 - {width}x{depth}x{height}mm\n'
        script += 'doc = FreeCAD.newDocument("상자")\n\n'
        script += 'box = doc.addObject("Part::Box", "상자")\n'
        script += f'box.Length = {width}\n'
        script += f'box.Width = {depth}\n'
        script += f'box.Height = {height}\n\n'
        script += 'FreeCAD.ActiveDocument.recompute()\n'
        script += 'print("[성공] 상자 생성 완료")\n'

    else:
        # 기본 상자 생성
        script += '# 기본 형상 생성\n'
        script += 'doc = FreeCAD.newDocument("자동생성")\n\n'
        script += 'box = doc.addObject("Part::Box", "상자")\n'
        script += 'box.Length = 50.0\n'
        script += 'box.Width = 50.0\n'
        script += 'box.Height = 50.0\n\n'
        script += 'FreeCAD.ActiveDocument.recompute()\n'
        script += 'print("[정보] 기본 상자 생성 - 치수를 지정해 주세요")\n'

    return script


# 규칙 기반 스크립트 생성 테스트
print("[테스트] 규칙 기반 스크립트 생성")
test_input = "지름 50mm 실린더, 높이 100mm"
parsed = text_parsing(test_input)
script = rule_based_script_generation(parsed)
print(f"\n입력 텍스트: \"{test_input}\"")
print("생성된 스크립트:")
print("-" * 40)
print(script)
print("-" * 40)


# ============================================================
# 4단계: AI 기반 스크립트 생성 (온라인)
# ============================================================

print()
print("-" * 60)
print("4단계: AI 기반 스크립트 생성 (온라인)")
print("-" * 60)


def ai_script_generation(text_input):
    """
    AI에게 자연어 텍스트를 전달하여 FreeCAD 스크립트를 생성합니다.
    API 키가 없으면 규칙 기반 생성으로 자동 전환됩니다.

    매개변수:
        text_input (str): 사용자의 자연어 설명

    반환값:
        str: FreeCAD Python 스크립트
    """
    if not client:
        print("[정보] API 미연결 - 규칙 기반 생성 사용")
        parsed = text_parsing(text_input)
        return rule_based_script_generation(parsed)

    try:
        # AI에게 전달할 시스템 프롬프트
        system_prompt = """당신은 FreeCAD Python 스크립트 생성 전문가입니다.

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
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"다음 설명을 FreeCAD Python 스크립트로 변환해주세요:\n{text_input}"}
            ],
            temperature=0.2,
            max_tokens=1500
        )

        answer = response.choices[0].message.content

        # 코드 블록 추출
        code = code_block_extraction(answer)

        print(f"[AI 생성] 입력: \"{text_input}\"")
        print("생성된 스크립트:")
        print("-" * 40)
        print(code)
        print("-" * 40)

        return code

    except Exception as e:
        print(f"[오류] AI 스크립트 생성 실패: {e}")
        print("[대체] 규칙 기반 생성으로 전환합니다.")
        parsed = text_parsing(text_input)
        return rule_based_script_generation(parsed)


def code_block_extraction(text):
    """
    마크다운 텍스트에서 Python 코드 블록을 추출합니다.

    매개변수:
        text (str): 마크다운 형식의 텍스트

    반환값:
        str: 추출된 Python 코드
    """
    if "```python" in text:
        start_pos = text.find("```python") + len("```python")
        end_pos = text.find("```", start_pos)
        return text[start_pos:end_pos].strip() if end_pos != -1 else text[start_pos:].strip()
    elif "```" in text:
        start_pos = text.find("```") + 3
        end_pos = text.find("```", start_pos)
        return text[start_pos:end_pos].strip() if end_pos != -1 else text[start_pos:].strip()
    return text.strip()


# AI 스크립트 생성 실행
ai_script_generation("M12 볼트, 길이 40mm, 육각 머리")


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


def safe_script_verification(script_text):
    """
    생성된 스크립트를 안전성 관점에서 검증합니다.

    검증 항목:
    - 위험한 함수 호출 여부
    - 허용되지 않은 import 여부
    - 시스템 명령 실행 여부

    매개변수:
        script_text (str): 검증할 스크립트

    반환값:
        tuple: (통과여부: bool, 메시지: str)
    """
    danger_patterns = [
        (r'\bexec\s*\(', "exec() 호출 감지 - 코드 실행 위험"),
        (r'\beval\s*\(', "eval() 호출 감지 - 표현식 실행 위험"),
        (r'\bos\.system\s*\(', "os.system() 호출 감지 - 시스템 명령 위험"),
        (r'\bsubprocess\.', "subprocess 사용 감지 - 프로세스 실행 위험"),
        (r'\b__import__\s*\(', "__import__() 감지 - 동적 import 위험"),
        (r'\bcompile\s*\(', "compile() 감지 - 동적 컴파일 위험"),
        (r'open\s*\(.+["\']w', "파일 쓰기 감지 - 파일 시스템 변경 위험"),
    ]

    allowed_imports = {'FreeCAD', 'Part', 'FreeCADGui', 'Drawing', 'Sketcher',
                    'Mesh', 'Spreadsheet', 'math', 're', 'datetime'}

    warning_list = []

    # 위험 패턴 검사
    for pattern, desc in danger_patterns:
        if re.search(pattern, script_text):
            warning_list.append(f"  [위험] {desc}")

    # import 검사
    import_pattern = re.compile(r'^import\s+(\w+)', re.MULTILINE)
    for match in import_pattern.finditer(script_text):
        module_name = match.group(1)
        if module_name not in allowed_imports:
            warning_list.append(f"  [주의] 허용되지 않은 import: {module_name}")

    if warning_list:
        print("[검증 결과] ⚠️ 주의사항 발견:")
        for warning in warning_list:
            print(warning)
        return False, "안전하지 않은 코드가 포함되어 있습니다."

    print("[검증 결과] 안전성 검증 통과")
    return True, "안전합니다."


# 검증 테스트
print("[테스트] 스크립트 안전성 검증")
good_script = """import FreeCAD
import Part
doc = FreeCAD.newDocument("테스트")
box = doc.addObject("Part::Box", "상자")
box.Length = 50
FreeCAD.ActiveDocument.recompute()
"""

bad_script = """import os
os.system("rm -rf /")
"""

print("\n좋은 스크립트 검증:")
safe_script_verification(good_script)

print("\n나쁜 스크립트 검증:")
safe_script_verification(bad_script)


# ============================================================
# 6단계: 파일로 저장하고 FreeCAD에서 실행
# ============================================================

print()
print("-" * 60)
print("6단계: 파일 저장 및 FreeCAD 실행 안내")
print("-" * 60)


def save_script_to_file(script_text, filename="auto_generated.py"):
    """
    스크립트를 파일로 저장합니다.
    저장 후 FreeCAD에서 열어 실행할 수 있습니다.

    매개변수:
        script_text (str): 저장할 스크립트
        filename (str): 저장할 파일명

    반환값:
        str: 저장된 파일의 전체 경로
    """
    # 현재 디렉토리에 저장
    save_path = os.path.join(os.path.dirname(__file__) or ".", filename)

    try:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(script_text)
        print(f"[저장] 파일이 저장되었습니다: {save_path}")
        print(f"  - FreeCAD에서 파일 > 열기 로 이 파일을 열어주세요")
        print(f"  - 또는 FreeCAD 콘솔에서 실행 가능합니다")
        return save_path
    except Exception as e:
        print(f"[오류] 파일 저장 실패: {e}")
        # 대체 경로: 임시 디렉토리
        try:
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(script_text)
            print(f"[저장] 임시 경로에 저장됨: {temp_path}")
            return temp_path
        except Exception as e2:
            print(f"[오류] 임시 저장도 실패: {e2}")
            return None


# 생성된 스크립트 저장
save_result = save_script_to_file(script, "generated_cylinder.py")


# ============================================================
# 7단계: 전체 변환 파이프라인
# ============================================================

print()
print("-" * 60)
print("7단계: 전체 변환 파이프라인")
print("-" * 60)


def full_conversion_pipeline(text_input):
    """
    텍스트 입력부터 스크립트 실행까지의 전체 과정을 수행합니다.

    단계:
    1. 텍스트 파싱 (규칙 기반)
    2. AI 스크립트 생성 (API 있으면) 또는 규칙 기반 생성
    3. 안전성 검증
    4. 파일 저장
    5. FreeCAD 실행 안내

    매개변수:
        text_input (str): 사용자의 자연어 설명

    반환값:
        dict: 전체 처리 결과
    """
    print(f"\n[파이프라인 시작] 입력: \"{text_input}\"")
    print("=" * 40)

    # 1단계: 파싱
    print("\n[1/5] 텍스트 파싱 중...")
    parse_info = text_parsing(text_input)
    print(f"  - 부품유형: {parse_info['part_type']}")
    print(f"  - 크기: {parse_info['size']}")
    print(f"  - 형상: {parse_info['shape']}")
    print(f"  - 재료: {parse_info['material']}")

    # 2단계: 스크립트 생성
    print("\n[2/5] 스크립트 생성 중...")
    gen_script = ai_script_generation(text_input)

    if not gen_script:
        print("[실패] 스크립트 생성 실패")
        return None

    # 3단계: 안전성 검증
    print("\n[3/5] 안전성 검증 중...")
    passed, message = safe_script_verification(gen_script)

    if not passed:
        print(f"[경고] 검증 실패: {message}")
        print("  - 생성된 코드를 수동으로 검토해 주세요")

    # 4단계: 파일 저장
    print("\n[4/5] 파일 저장 중...")
    safe_name = re.sub(r'[^\w]', '_', text_input[:20])
    file_path = save_script_to_file(gen_script, f"generated_{safe_name}.py")

    # 5단계: 실행 안내
    print("\n[5/5] 실행 안내")
    print("  FreeCAD에서 실행하는 방법:")
    print("  1. FreeCAD를 엽니다")
    print(f"  2. 파일 > 열기 로 '{file_path or '생성된 파일'}'을 엽니다")
    print("  3. 또는 FreeCAD 콘솔(Macro > Execute)에서 실행합니다")
    print("  4. 실행 전 코드를 반드시 검토해 주세요")

    print("\n[파이프라인 완료]")
    print("=" * 40)

    return {
        "original_text": text_input,
        "parse_info": parse_info,
        "script": gen_script,
        "verification": (passed, message),
        "file_path": file_path
    }


# 전체 파이프라인 실행
pipeline_result = full_conversion_pipeline("지름 30mm 실린더, 높이 80mm")


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

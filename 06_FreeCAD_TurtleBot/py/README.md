# FreeCAD Python + AI 3D 설계 자동화 커리큘럼

> Python으로 FreeCAD를 제어하고, AI와 결합하여 3D 설계를 자동화하는 완성 교육 과정

---

## 소개

본 커리큘럼은 **FreeCAD Python API**를 활용하여 3D 모델링을 스크립트로 자동화하고,
**AI(대규모 언어 모델, GAN, 강화학습)**와 결합하여 차세대 설계 파이프라인을 구축하는 과정입니다.

모든 코드는 **FreeCAD 매크로 에디터**에서 바로 실행할 수 있는 완성된 Python 스크립트이며,
각 스크립트에는 동작 원리를 설명하는 상세한 한국어 주석이 포함되어 있습니다.

---

## 대상 학습자

| 대상 | 설명 |
|------|------|
| Python 초보자 | 프로그래밍 기초가 있지만 3D CAD 자동화를 처음 접하는 분 |
| FreeCAD 사용자 | GUI 작업에 익숙하지만 스크립트 자동화를 원하는 분 |
| STM32 / Arduino 개발자 | 하드웨어 프로젝트에 맞는 인클로저, 하우징을 자동 설계하고 싶은 분 |
| 3D 프린팅 메이커 | 반복적인 부품 설계를 자동화하고 양산에 대비하는 분 |
| AI / ML 업무 종사자 | CAD + AI 융합 기술을 실무에 적용하고 싶은 분 |

---

## 사전 요구사항

| 항목 | 요구 버전 / 조건 |
|------|-----------------|
| FreeCAD | **0.20 이상** ( recommand: 1.0+ ) |
| Python | **3.8 이상** (FreeCAD 내장 또는 시스템 Python) |
| OpenAI API Key | 선택 사항 (Part 5~8에서 AI 기능 사용 시) |
| 운영체제 | Windows 10+, macOS, Linux |
| 3D 프린터 (선택) | STL 내보내기 후 출력 테스트용 |

---

## 커리큘럼 개요

총 **8개 파트, 40개 레슨**으로 구성되어 있습니다.

### Part 1. FreeCAD Python 기초 (01~05)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 01 | `01_first_cube.py` | 첫 번째 큐브 생성, 문서 관리, STL 내보내기 |
| 02 | `02_cylinder.py` | 원기둥 생성, 반지름/높이 파라메트릭 설정 |
| 03 | `03_sphere.py` | 구 생성, 반지름 변경 |
| 04 | `04_cone.py` | 원뿔 생성, 상단/하단 반경 제어 |
| 05 | `05_compound.py` | 복합도형 — fuse, cut, 일반화된 봉인체 조합 |

### Part 2. 파라메트릭 설계 자동화 (06~10)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 06 | `06_parametric_bracket.py` | 파라메트릭 L-브라켓, 함수 기반 치수 입력 |
| 07 | `07_bolt_generator.py` | M3~M20 규격별 볼트 자동 생성기 |
| 08 | `08_nut_generator.py` | 규격별 육각너트 생성기 |
| 09 | `09_washer_series.py` | 규격별 와셔 시리즈 일괄 생성 |
| 10 | `10_csv_driven.py` | CSV 데이터 읽기 → 부품 자동 생성 |

### Part 3. 배치 처리와 파일 관리 (11~15)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 11 | `11_stl_batch_export.py` | STL 파일 일괄 내보내기 |
| 12 | `12_step_batch_convert.py` | STEP ↔ 라인 변환 배치 처리 |
| 13 | `13_catalog_auto.py` | 부품 카탈로그 자동 생성 |
| 14 | `14_dimension_check.py` | 디멘션 검증 자동화 |
| 15 | `15_report_auto.py` | 설계 보고서 자동 생성 |

### Part 4. 알고리즘 기반 설계 (16~20)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 16 | `16_solid_optimization.py` | 졸리드 바디 최적화 알고리즘 |
| 17 | `17_topology_structure.py` | 토폴로지 구조 설계 |
| 18 | `18_hash_grid_array.py` | 해시/그리드 배열 패턴 |
| 19 | `19_surface_pattern.py` | 곡면 패턴 생성 |
| 20 | `20_fractal_structure.py` | 프랙탈 구조 생성 |

### Part 5. AI 통합 기초 (21~25)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 21 | `21_ai_api_call.py` | FreeCAD에서 OpenAI API 호출 |
| 22 | `22_text_to_script.py` | 텍스트 → FreeCAD 스크립트 변환 |
| 23 | `23_ai_dimension.py` | AI 기반 치수 추천 |
| 24 | `24_ai_material.py` | AI 기반 재료 추천 |
| 25 | `25_ai_review.py` | AI 설계 검수 |

### Part 6. AI 기반 생성 설계 (26~30)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 26 | `26_llm_macro_gen.py` | LLM으로 FreeCAD 매크로 생성 |
| 27 | `27_ai_param_optim.py` | AI 파라메트릭 최적화 |
| 28 | `28_gan_form_gen.py` | GAN 기반 형태 생성 |
| 29 | `29_rl_path_design.py` | 강화학습 경로 설계 |
| 30 | `30_ai_model_valid.py` | AI 모델 검증 파이프라인 |

### Part 7. 로보틱스 / IoT 실무 (31~35)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 31 | `31_sensor_housing.py` | 센서 하우징 자동 설계 |
| 32 | `32_pcb_case.py` | PCB 케이스 생성기 |
| 33 | `33_robot_frame.py` | 로봇 프레임 설계 |
| 34 | `34_drone_parts.py` | 드론 부품 설계 |
| 35 | `35_iot_board_case.py` | IoT 보드 케이스 자동 생성 |

### Part 8. 고급 AI + CAD 파이프라인 (36~40)

| 레슨 | 파일명 | 내용 |
|------|--------|------|
| 36 | `36_full_pipeline.py` | 전체 자동화 파이프라인 구축 |
| 37 | `37_ai_design_review.py` | AI 디자인 리뷰 시스템 |
| 38 | `38_version_control.py` | FreeCAD 버전 관리 |
| 39 | `39_cloud_integration.py` | 클라우드 스토리지 통합 |
| 40 | `40_final_project.py` | 최종 종합 프로젝트 |

---

## FreeCAD에서 스크립트 실행하는 방법

### 방법 1: 메뉴에서 실행

1. FreeCAD를 엽니다.
2. 상단 메뉴: **Macro → Macros...** 를 클릭합니다.
3. **Create** 를 클릭하여 새 매크로를 만들거나, **Browse** 로 기존 `.py` 파일을 선택합니다.
4. **Run** 을 클릭하여 실행합니다.

### 방법 2: 매크로 에디터에서 직접 실행

1. **Macro → Macro...** 를 열고 매크로를 만듭니다.
2. 에디터에 코드를 붙여넣습니다.
3. 툴바의 **▶ Run** 버튼(또는 `F5`)을 누릅니다.

### 방법 3: 명령줄에서 실행 ( FreeCADCmd )

```bash
# Windows
"C:\Program Files\FreeCAD 1.0\bin\FreeCADCmd.exe" "C:\path\to\script.py"

# macOS
/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd /path/to/script.py

# Linux
freecadcmd /path/to/script.py
```

### 방법 4: Python 콘솔에서 실행

FreeCAD 하단의 **Python 콘솔**에서 직접 입력할 수 있습니다:

```python
exec(open("C:/Users/Administrator/Downloads/py/src/01_first_cube.py").read())
```

---

## 디렉토리 구조

```
py/
├── README.md                          # 본 문서
└── src/
    ├── 01_first_cube.py               # Part 1 - 첫 큐브
    ├── 02_cylinder.py                 # Part 1 - 원기둥
    ├── 03_sphere.py                   # Part 1 - 구
    ├── 04_cone.py                     # Part 1 - 원뿔
    ├── 05_compound.py                 # Part 1 - 복합도형
    ├── 06_parametric_bracket.py       # Part 2 - 파라메트릭 브라켓
    ├── 07_bolt_generator.py           # Part 2 - 볼트 생성기
    ├── 08_nut_generator.py            # Part 2 - 너트 생성기
    ├── 09_washer_series.py            # Part 2 - 와셔 시리즈
    ├── 10_csv_driven.py              # Part 2 - CSV 기반 설계
    ├── ...                            # Part 3~8 (추후 추가)
    └── 40_final_project.py           # Part 8 - 최종 프로젝트
```

---

## 최종 목표

이 커리큘럼을 완료하면 다음을 할 수 있게 됩니다:

1. **FreeCAD Python API** 로 기본 도형부터 복잡한 기계 부품까지 스크립트로 생성
2. **파라메트릭 설계** 를 함수/클래스로 모듈화하여 재사용 가능한 설계 자동화 시스템 구축
3. **배치 처리** 로 수백 개의 부품을 한 번에 내보내고 검증
4. **알고리즘 기반 설계** 로 최적화된 구조물, 패턴, 프랙탈 생성
5. **AI API 통합** 으로 자연어에서 3D 모델을 생성하는 파이프라인 구축
6. **로보틱스/IoT 실무** 에 바로 적용 가능한 하우징, 케이스, 프레임 자동 설계
7. **End-to-End 자동화 파이프라인** 으로 아이디어 → 3D 모델 → 검증 → 출력의 전체 과정 자동화

---

## 라이선스

본 교육 자료는 학습 목적으로 자유롭게 사용하실 수 있습니다.

## 문의

이슈는 GitHub Issues 에 등록해 주세요.

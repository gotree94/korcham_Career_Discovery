# OrCAD Capture + Allegro PCB Editor 회로 설계 과정 (2일, 총 14시간)

## 개요

| 항목 | 내용 |
|------|------|
| **툴** | Cadence OrCAD Capture 16.6 / Allegro PCB Designer |
| **참고 하드웨어** | ROBOTIS OpenCR (STM32F746ZG 기반 제어보드) |
| **교육 시간** | 2일 (1일 7시간, 총 14시간) |
| **난이도** | 중급 (기초 전자회로 지식 필요) |
| **산출물** | OrCAD Capture Schematic (.DSN), Allegro PCB Board (.BRD), Gerber, BOM |

## OrCAD / Allegro 소개

Cadence OrCAD Capture + Allegro PCB Editor는 **업계 표준 ECAD(Electronic CAD) 툴체인**으로, 전 세계 대부분의 PCB 설계 회사에서 사용합니다.

| 툴 | 역할 |
|----|------|
| **OrCAD Capture** | 회로도(Schematic) 작성. 부품 배치, Net 연결, DRC 검증 |
| **Allegro PCB Editor** | PCB 레이아웃 설계. 배치(Routing), 평면(Power/GND Plane), Gerber 출력 |

### 라이선스 안내

- **상용 소프트웨어**이며, Cadence 사이트를 통해 라이선스 구매 필요
- **교육 기관** (대학, 연구소)의 경우 Cadence Academic Network을 통해 접근 가능
- 일부 기업에서는 OrCAD/Allegro **Free Viewer**로 설계 파일 검토 가능
- **원본 OpenCR** 설계는 OrCAD Capture 16.6에서 작성됨

### OrCAD Capture vs Allegro PCB Editor Workflow

```
OrCAD Capture (회로도)
    │
    ├─ 부품 배치 (Place Part)
    ├─ 배선 (Wire, Net Alias)
    ├─ Annotate (Refdes 자동 할당)
    ├─ DRC (Design Rules Check)
    ├─ Netlist 생성
    │
    ▼
Allegro PCB Editor (PCB 레이아웃)
    │
    ├─ Netlist Import
    ├─ 부품 배치 (Placement)
    ├─ 배선 (Routing)
    ├─ Copper Pour
    ├─ DRC + Database Check
    ├─ Gerber + NC Drill 출력
    │
    ▼
PCB 제작 (Fabrication)
```

## 과정 구조

| Day | 시간 | 주제 |
|----|------|------|
| **Day 1** | 7h (09:00-17:00) | **회로도 (Schematic)** — OrCAD Capture |
| **Day 2** | 7h (09:00-17:00) | **PCB 레이아웃** — Allegro PCB Editor |

### Day 1: Schematic (7h)

| Step | 시간 | 내용 |
|------|------|------|
| Step 1 | 40min | OrCAD Capture 시작 및 프로젝트 생성 |
| Step 2 | 1h 20min | 부품 라이브러리 및 심볼 생성 |
| Step 3 | 1h 30min | 전원부 회로도 작성 |
| Step 4 | 1h 30min | MCU STM32F746 주변회로 |
| Step 5 | 1h | 모터 드라이버 + 통신 인터페이스 |
| Step 6 | 1h | 커넥터 + 종합 검토 |

### Day 2: PCB Layout (7h)

| Step | 시간 | 내용 |
|------|------|------|
| Step 7 | 1h 30min | Allegro PCB Editor 시작 및 설정 |
| Step 8 | 1h 30min | Netlist Import + 부품 배치 |
| Step 9 | 1h 30min | PCB 배선 (Routing) |
| Step 10 | 1h | DRC + 거버 출력 |
| Step 11 | 1h | 3D 시각화 + 설계 검토 |
| Step 12 | 30min | 최종 발표 + 리뷰 |

## OpenCR 보드 (Reference Design)

| 구성 | 부품 |
|------|------|
| MCU | STM32F746ZGT6 (LQFP-144, ARM Cortex-M7 216MHz) |
| IMU | ICM-20648 (QFN-24) |
| 전원 | LM5175PWPR (HTSSOP-28) Buck-Boost → XL4005 (TO-263-5) → AZ1117H-3.3 / IL1117-5.0 |
| 모터 | A3906SESTR-T ×2 (QFN-20) |
| 통신 | TJF1051T/3 (CAN), MAX3443ECSA+ (RS-485) |
| USB | STMPS2141STR + EMIF02-USB03F2 |
| 크기 | 105×75mm, 4-layer PCB |
| 수동부품 | MLCC 0402/0603, Resistor 0402/0603 |

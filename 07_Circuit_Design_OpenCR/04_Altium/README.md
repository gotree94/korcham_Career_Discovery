# Altium Designer를 활용한 OpenCR 회로 설계 과정

## 개요

Altium Designer는 **업계 표준**의 PCB 설계 EDA 도구로, 회로도(Schematic) 설계부터 PCB 레이아웃, 3D 시각화, BOM 관리, 제조 출력까지 **단일 통합 환경**에서 제공합니다. 본 과정에서는 **OpenCR** 레퍼런스 하드웨어를 기반으로 STM32F746 MCU, 전원부, 모터 드라이버, 통신 인터페이스가 통합된 4층 PCB를 실제로 설계합니다.

> **참고:** Altium Designer는 **상용 소프트웨어**입니다. 교육용 라이선스(Educational License, 연간 $195~395)를 통해 학생/교육 기관에서 합법적으로 사용할 수 있으며, Altium에서 제공하는 30일 무료 평가판도 활용 가능합니다.

## Altium Designer 주요 기능

| 기능 | 설명 |
|------|------|
| **통합 설계 환경** | 회로도- PCB 간 양방향 동기화 (ECO) |
| **3D 시각화** | STEP 모델 매핑, 보드 두께 표현, 케이블 간섭 확인 |
| **ActiveBOM** | 실시간 부품 가격, 재고, 대체 부품 추천 |
| **Multi-board** | 여러 PCB를 하나의 프로젝트로 통합 설계 |
| **Differential Pair** | 고속 신호(USB, HDMI) 차동쌍 라우팅 지원 |
| **Signal Integrity** | 임피던스 계산, 반사/크로스토크 분석 |
| **제조 출력** | Gerber, NC Drill, ODB++, Pick & Place 일괄 출력 |

## 과정 구성 (총 14시간)

### Day 1: 회로도 설계 (7시간)

| Step | 주제 | 시간 |
|------|------|------|
| 1 | Altium 설치 및 프로젝트 생성 | 40min |
| 2 | 부품 라이브러리 및 심볼 생성 | 1h 20min |
| 3 | 전원부 회로도 작성 | 1h 30min |
| 4 | MCU STM32F746 주변회로 | 1h 30min |
| 5 | 모터 드라이버 + 통신 인터페이스 | 1h |
| 6 | 커넥터 + 종합 검토 (ERC/Annotate) | 1h |

### Day 2: PCB 레이아웃 설계 (7시간)

| Step | 주제 | 시간 |
|------|------|------|
| 7 | PCB 변환 및 레이어 설정 | 1h 30min |
| 8 | 부품 배치 (Placement) | 1h 30min |
| 9 | PCB 배선 (Routing) | 1h 30min |
| 10 | DRC + 거버 출력 | 1h |
| 11 | 3D 시각화 + 설계 검토 | 1h |
| 12 | 최종 발표 + 리뷰 | 30min |

## OpenCR 레퍼런스 사양

| 항목 | 사양 |
|------|------|
| **MCU** | STM32F746ZGT6 (LQFP-144, ARM Cortex-M7 216MHz) |
| **IMU** | ICM-20648 (QFN-24, 6축 자이로/가속도) |
| **전원** | LM5175PWPR buck-boost (5~24V→12V) + XL4005 (12V→5V) + IL1117-5.0 (5V) + AZ1117H-3.3 (3.3V) |
| **모터 드라이버** | A3906SESTR-T x2 (QFN-20, 듀얼 DC 모터) |
| **CAN** | TJF1051T/3 (SOP-8) |
| **RS-485** | MAX3443ECSA+ (SOP-8) |
| **USB** | STMPS2141STR (전원 스위치) + EMIF02-USB03F2 (EMI 필터) |
| **퓨즈** | 0453010 (10A, 125V) |
| **커넥터** | JST B3B-EH-A (3핀), B4B-EH-A (4핀), 20010WS-04, ZX62D-B-5P8 (Micro-B) |
| **크리스탈** | 25MHz (SX-32), 32.768kHz (CM315) |
| **보드 크기** | 105×75mm, 4층 PCB (Top/GND/PWR/Bottom) |
| **수동부품** | MLCC 0402/0603, Resistor 0402/0603 |

## 예상 결과물

- 회로도 파일: `OpenCR_REVH.SchDoc`
- PCB 파일: `OpenCR_REVH.PcbDoc`
- 출력물: Gerber RS-274X, NC Drill (Excellon), BOM (CSV), Pick & Place, 3D PDF, ODB++
- 리포트: Smart PDF, ActiveBOM, DRC Report

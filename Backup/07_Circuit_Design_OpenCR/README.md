# 회로 설계 — OpenCR 기반 4가지 EDA 도구 과정

https://www.robotis.com/shop/item.php?it_id=903-0257-000

## 개요

> ROBOTIS OpenCR 하드웨어를 예시로 **5가지 EDA 도구**를 각각 2일(14h) 동안 학습한다.
> 동일한 회로(OpenCR REV H)를 도구별로 설계하며, 각 EDA의 특징과 워크플로우를 비교 체험한다.

## 대상 보드: OpenCR 1.0 (REV H)

| 항목 | 사양 |
|------|------|
| MCU | STM32F746ZGT6 (ARM Cortex-M7, 216MHz) |
| IMU | ICM-20648 (6축) |
| 입력 전원 | 5~24V (USB / 배터리 / SMPS) |
| 전원 관리 | LM5175PWPR (벅-부스트) + LDO 3.3V/5V |
| 모터 드라이버 | A3906SESTR-T × 2 |
| 통신 | TTL 3ch, RS-485 3ch, CAN 1ch, UART 2ch, USB OTG |
| 보드 크기 | 105 × 75mm |
| PCB 층 수 | 4층 (추정) |
| 원본 툴 | OrCAD Capture 16.6 |

## 과정 구성

| 과정 | EDA 도구 | 라이선스 | 난이도 |
|:----:|----------|:--------:|:------:|
| 01_KiCAD | KiCAD 8 | 무료 (오픈소스) | ★★☆ |
| 02_EasyEDA | EasyEDA (Web) | 무료 (클라우드) | ★☆☆ |
| 03_OrCAD_Allegro | OrCAD Capture + Allegro PCB Editor | 상용 (고가) | ★★★ |
| 04_Altium | Altium Designer | 상용 (고가) | ★★★ |
| 05_PADS | PADS Logic + PADS Layout (Siemens EDA) | 상용 (중간) | ★★☆ |

## 각 과정의 Day 구성

```
Day 1 (7h) — 회로도(Schematic) 설계
├── Step 1: Tool 설치 및 프로젝트 생성  (40min)
├── Step 2: 부품 라이브러리 / 심볼 생성  (1h 20min)
├── Step 3: 전원부 회로도 — LM5175 + LDO  (1h 30min)
├── Step 4: MCU STM32F746 주변회로  (1h 30min)
├── Step 5: 모터 드라이버 + 통신 I/F  (1h)
└── Step 6: 커넥터 + 종합 검토  (1h)

Day 2 (7h) — PCB 레이아웃 설계
├── Step 7: PCB 설정 및 풋프린트  (1h 30min)
├── Step 8: 부품 배치 (Placement)  (1h 30min)
├── Step 9: PCB 배선 (Routing)  (1h 30min)
├── Step 10: DRC + 거버(Gerber) 출력  (1h)
├── Step 11: 3D 시각화 + 설계 검토  (1h)
└── Step 12: 최종 발표 + 리뷰  (30min)
```

## 참고 자료

- OpenCR Hardware Repo: https://github.com/ROBOTIS-GIT/OpenCR-Hardware
- OpenCR 회로도 PDF: https://github.com/ROBOTIS-GIT/OpenCR-Hardware/blob/master/Schematic/OpenCR_REVH.pdf
- OpenCR BOM: https://github.com/ROBOTIS-GIT/OpenCR-Hardware/blob/master/BOM/OpenCR_REVH_BOM.xls
- OpenCR PCB 레이아웃 PDF: https://github.com/ROBOTIS-GIT/OpenCR-Hardware/blob/master/Layout/OpenCR_REVH.pdf

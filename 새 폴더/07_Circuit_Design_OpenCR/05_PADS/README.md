# PADS (Siemens EDA) — OpenCR 회로 설계

## 개요

> Siemens EDA의 **PADS Professional**을 이용하여 OpenCR 제어 보드 회로를 설계한다.
> PADS Logic(회로도) + PADS Layout(PCB) + PADS Router(배선) 워크플로우 체험

## PADS vs 타 EDA 도구

| 항목 | PADS | KiCAD | EasyEDA | OrCAD/Allegro | Altium |
|------|:----:|:-----:|:-------:|:-------------:|:------:|
| 라이선스 | 상용 | 무료 | 무료 | 상용 | 상용 |
| 난이도 | ★★☆ | ★★☆ | ★☆☆ | ★★★ | ★★★ |
| PCB 제한 | 없음 | 없음 | 제한有 | 없음 | 없음 |
| 아시아 점유율 | 중견기업 ↑ | 취미/스타트업 | 취미/중국 | 대기업 | 중견기업 |
| 학습 곡선 | 완만 | 보통 | 쉬움 | 가파름 | 보통 |

## PADS 제품군

| 제품 | 역할 | 파일 확장자 |
|------|------|:----------:|
| **PADS Logic** | 회로도(Schematic) 작성 | .sch |
| **PADS Layout** | PCB 레이아웃 + 라우팅 | .pcb |
| **PADS Router** | 고속/차동 배선 전용 | (.pcb 내부) |
| **PADS Library** | 부품 라이브러리 관리 | .pt9 / .pd9 |

## 과정 구성

```
Day 1 (7h) — 회로도 (PADS Logic)
├── Step 1: PADS 설치 및 프로젝트 생성  (40min)
├── Step 2: CAE 심볼 + 부품 라이브러리  (1h 20min)
├── Step 3: 전원부 회로도 — LM5175 + LDO  (1h 30min)
├── Step 4: MCU STM32F746 주변회로  (1h 30min)
├── Step 5: 모터 드라이버 + 통신 I/F  (1h)
└── Step 6: 커넥터 + 종합 검토  (1h)

Day 2 (7h) — PCB (PADS Layout + Router)
├── Step 7: PCB 설정 및 풋프린트  (1h 30min)
├── Step 8: 부품 배치 (Placement)  (1h 30min)
├── Step 9: PCB 배선 — PADS Router  (1h 30min)
├── Step 10: DRC + 거버 출력  (1h)
├── Step 11: 3D 시각화 + 검토  (1h)
└── Step 12: 최종 발표 + 리뷰  (30min)
```

## 참고 자료

- OpenCR Hardware: https://github.com/ROBOTIS-GIT/OpenCR-Hardware
- Siemens PADS: https://eda.sw.siemens.com/en-US/pcb/pads/

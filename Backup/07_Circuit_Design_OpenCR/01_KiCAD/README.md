# KiCAD 8 회로 설계 입문 과정 — OpenCR Reference

## 📌 KiCAD 8 개요

**KiCAD**는 전 세계에서 가장 널리 사용되는 **오픈소스 EDA (Electronic Design Automation)** 도구입니다.

| 항목 | 내용 |
|------|------|
| 라이선스 | **GPL v3 / Free Software** — 완전 무료, 상업적 사용 가능 |
| 플랫폼 | **Windows / macOS / Linux** 크로스플랫폼 지원 |
| 공식 사이트 | [https://www.kicad.org](https://www.kicad.org) |
| 다운로드 | [https://www.kicad.org/download/windows/](https://www.kicad.org/download/windows/) |
| 최신 버전 | **KiCAD 8.0** (2024 Release) |
| 주요 기능 | 회로도 편집 (Eeschema), PCB 편집 (Pcbnew), 3D 뷰어, Gerber 출력, BOM 생성, SPICE 시뮬레이션 |

### KiCAD만의 장점

- **무료** — Altium, OrCAD 대비 라이선스 비용 0원
- **방대한 라이브러리** — 공식 + 커뮤니티 심볼/풋프린트 50만+
- **Git 연동** — 텍스트 기반 파일 포맷 (설계 히스토리 관리 용이)
- **스크립팅** — Python API로 자동화 가능
- **액티브 커뮤니티** — 포럼, StackExchange, GitHub 활발

---

## 📐 참고 하드웨어: OpenCR

| 항목 | 사양 |
|------|------|
| Reference Version | **OpenCR REV H** |
| MCU | STM32F746ZGT6 (ARM Cortex-M7, 216MHz, LQFP-144) |
| IMU | ICM-20648 (6축, QFN-24) |
| Power | LM5175PWPR buck-boost + XL4005 + IL1117-5.0 + AZ1117H-3.3 |
| Motor Driver | A3906SESTR-T × 2 (QFN-20) |
| CAN | TJF1051T/3 (SOP-8) |
| RS-485 | MAX3443ECSA+ (SOP-8) |
| USB | STMPS2141STR + EMIF02-USB03F2 |
| Board Size | **105mm × 75mm, 4-layer PCB** |
| Connectors | JST B3B-EH-A, B4B-EH-A, 20010WS-04, ZX62D-B-5P8 |

---

## 🗓️ 과정 일정 (총 14시간, 2일)

### Day 1 — 회로도 설계 Schematic (7시간)

| Step | 주제 | 시간 |
|------|------|------|
| **1** | KiCAD 설치 및 프로젝트 생성 | 40min |
| **2** | 부품 라이브러리 및 심볼 생성 | 1h 20min |
| **3** | 전원부 회로도 작성 | 1h 30min |
| **4** | MCU STM32F746 주변회로 | 1h 30min |
| **5** | 모터 드라이버 + 통신 인터페이스 | 1h |
| **6** | 커넥터 + 종합 검토 (ERC) | 1h |

### Day 2 — PCB 설계 (7시간)

| Step | 주제 | 시간 |
|------|------|------|
| **7** | PCB 설정 및 풋프린트 할당 | 1h 30min |
| **8** | 부품 배치 (Placement) | 1h 30min |
| **9** | PCB 배선 (Routing) | 1h 30min |
| **10** | DRC + 거버 출력 | 1h |
| **11** | 3D 시각화 + 설계 검토 | 1h |
| **12** | 최종 발표 + 리뷰 | 30min |

---

## 📁 과정 디렉토리 구조

```
01_KiCAD/
├── README.md                  ← 이 파일
├── Day1_회로도.md             ← Day 1 수업 자료
├── Day2_PCB.md                ← Day 2 수업 자료
└── OpenCR_KiCAD/              ← 실습 프로젝트
    ├── OpenCR_KiCAD.kicad_pro
    ├── OpenCR_KiCAD.kicad_sch
    ├── OpenCR_KiCAD.kicad_pcb
    ├── symbols/               ← 사용자 심볼
    ├── footprints/            ← 사용자 풋프린트
    └── output/                ← 출력물 (PDF, Gerber, BOM)
```

---

## ⚙️ 사전 준비

| 항목 | 설명 |
|------|------|
| PC 사양 | CPU i5 이상, RAM 8GB 이상, SSD 20GB 여유공간 |
| OS | Windows 10/11 (64bit) 권장 |
| KiCAD | **KiCAD 8.0** 이상 설치 |
| 자료 | OpenCR REV H 회로도 PDF, Datasheets (STM32F746, LM5175 등) |
| 참고 | [KiCAD 공식 문서](https://docs.kicad.org/) / [KiCAD 포럼](https://forum.kicad.info/) |

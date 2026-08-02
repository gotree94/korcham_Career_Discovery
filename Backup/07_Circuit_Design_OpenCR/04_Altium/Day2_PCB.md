# Day 2: PCB 레이아웃 설계 — 7시간

---

## Step 7: PCB 변환 및 레이어 설정 (1h 30min)

### 7.1 PCB 문서 생성

**방법 A — Blank PCB 생성 (권장):**

| 단계 | 조작 |
|------|------|
| 새 PCB | `File → New → PCB` |
| 저장 | `Save As → OpenCR_REVH.PcbDoc` (Source Documents 폴더) |
| 프로젝트 추가 | `Right-click Project → Add Existing to Project → OpenCR_REVH.PcbDoc` |

**방법 B — PCB Wizard 사용 (초보자):**

1. `File → New → PCB Board Wizard`
2. Board Shape: **Rectangular**
3. Dimensions: **105mm × 75mm**
4. Layer Count: **4**
5. Via Style: **Thru-hole vias only**
6. Component type: **Surface Mount**
7. Default Track Width: **0.2mm**

### 7.2 Layer Stack Manager 설정

| 단계 | 조작 |
|------|------|
| 실행 | `Design → Layer Stack Manager` |
| 레이어 수 | 2-click → **4-Layer** 선택 |

**4-Layer Stack 구성:**

```
Layer Stack: OpenCR_REVH (4-Layer, 1.6mm)

┌─────────────────────────────────────────────────┐
│ Top Layer (Signal)       │ 1oz (35µm) Copper    │
├─────────────────────────────────────────────────┤
│ Prepreg                  │ 0.2mm (8mil) FR4     │
├─────────────────────────────────────────────────┤
│ Internal Plane 1 (GND)   │ 0.5oz (18µm) Copper  │
├─────────────────────────────────────────────────┤
│ Core                     │ 0.5mm (20mil) FR4    │
├─────────────────────────────────────────────────┤
│ Internal Plane 2 (PWR)   │ 0.5oz (18µm) Copper  │
├─────────────────────────────────────────────────┤
│ Prepreg                  │ 0.2mm (8mil) FR4     │
├─────────────────────────────────────────────────┤
│ Bottom Layer (Signal)    │ 1oz (35µm) Copper    │
└─────────────────────────────────────────────────┘
Total: 1.6mm (62.99mil)
```

**레이어 상세 설정:**

| Layer | Type | 두께 | Copper | 용도 |
|-------|------|------|--------|------|
| Top Layer | Signal | 0.035mm | 1oz | 신호 + 부품 |
| Internal Plane 1 | Plane | 0.018mm | 0.5oz | **GND** (완전 평면) |
| Internal Plane 2 | Plane | 0.018mm | 0.5oz | **PWR** (12V/5V/3.3V Split) |
| Bottom Layer | Signal | 0.035mm | 1oz | 신호 + 부품 (LDO 등) |

**Stack 설정 세부:**

| 파라미터 | 값 | 비고 |
|----------|-----|------|
| Material | FR4 | 표준 PCB 재질 |
| Dielectric Constant (Er) | 4.5 | FR4 기준 |
| Loss Tangent | 0.02 | 일반적인 FR4 |
| Copper Resistivity | 1.72E-8 Ω·m | 표준 구리 |
| Thermal Conductivity | 0.3 W/m·K | FR4 |

> **Tip:** 임피던스 제어가 필요한 Differential Pair(USB D+/D-, 90Ω)의 경우, Layer Stack에 따라 Trace Width/Gap을 계산해야 합니다. Altium의 `Tools → Impedance Calculator`를 활용하세요.

**임피던스 계산 (USB 90Ω Differential):**

| 파라미터 | Top Layer | Internal Layer |
|----------|-----------|----------------|
| Trace Width | 0.35mm | 0.2mm |
| Trace Gap | 0.2mm | 0.15mm |
| Impedance (Differential) | ~90Ω | ~90Ω |
| Reference Plane | GND (Layer 2) | GND (Layer 2) |

### 7.3 Design Rules 설정

| 메뉴 | 경로 |
|------|------|
| Rules | `Design → Rules` |

**Electrical Rules:**

| 규칙 | Min | Preferred | Max | 적용 |
|------|-----|-----------|-----|------|
| Clearance | 0.15mm | 0.2mm | - | All to All |
| Short-Circuit | - | - | - | Allowed = False |
| Un-Routed Net | - | - | - | Report = True |
| Un-Connected Pin | - | - | - | Report = True |

**Routing Rules:**

| 규칙 | Min | Preferred | Max | 적용 |
|------|-----|-----------|-----|------|
| Width - Signal | 0.15mm | 0.2mm | 0.5mm | All |
| Width - 12V Power | 1.5mm | 2.0mm | 3.0mm | InNet('VCC_12V') |
| Width - 5V Power | 1.0mm | 1.5mm | 2.5mm | InNet('VCC_5V') |
| Width - 3.3V Power | 0.5mm | 0.8mm | 1.5mm | InNet('VCC_3V3') |
| Width - GND | 0.5mm | 1.0mm | 2.0mm | InNet('GND') |
| Routing Topology | - | Shortest | - | All |
| Routing Priority | 5 (12V) - 3 (Signal) | 1 (lowest) | | |

**SMT Rules:**

| 규칙 | 값 | 설명 |
|------|-----|------|
| SMD to Corner | 0.5mm | SMD 패드에서 PCB 모서리 거리 |
| SMD to Plane | 0.3mm | SMD 패드에서 내부 평면까지 거리 |
| SMD Neck-Down | 50% | SMD 패드에서 트레이스 폭 축소 비율 |

**Via Rules:**

| 규칙 | Min | Preferred | Max |
|------|-----|-----------|-----|
| Via Diameter | 0.6mm | 0.8mm | 1.2mm |
| Via Hole Size | 0.3mm | 0.4mm | 0.6mm |
| Via to Via Clearance | 0.2mm | 0.3mm | - |

**Plane Rules:**

| 규칙 | 값 |
|------|-----|
| Power Plane Clearance | 0.3mm |
| Power Plane Connect Style | Relief Connect (4 spokes, 0.3mm width) |

**Polygon Rules:**

| 규칙 | 값 |
|------|-----|
| Clearance (Poly to Pad) | 0.2mm |
| Clearance (Poly to Poly) | 0.3mm |
| Remove Dead Copper | True |
| Pour Over All Same Net | True |

### 7.4 Board Shape 정의

| 단계 | 조작 |
|------|------|
| Board Shape | `Design → Board Shape → Redefine Board Shape` |
| Snap Grid | `View → Grid → Snap Grid → 1mm` |
| 모서리 좌표 | 키보드로 정확한 좌표 입력 |

**좌표 입력 방법:**

1. `Design → Board Shape → Redefine Board Shape` 실행
2. 첫 번째 점 클릭 → `Tab` → X: 0, Y: 0
3. 두 번째 점 클릭 → `Tab` → X: 105, Y: 0
4. 세 번째 점 클릭 → `Tab` → X: 105, Y: 75
5. 네 번째 점 클릭 → `Tab` → X: 0, Y: 75
6. 우클릭 → 종료

**Board Shape 확인:**

| 확인 항목 | 방법 |
|-----------|------|
| 보드 크기 | `Reports → Measure Board Size` → 105mm × 75mm |
| 모서리 좌표 | `Design → Board Shape → Move Board Shape` → 좌상단 (0,0) |
| 보드 두께 | Layer Stack Manager에서 1.6mm 확인 |

### 7.5 Import Changes (Schematic → PCB)

| 단계 | 조작 |
|------|------|
| ECO 실행 | `Design → Import Changes From OpenCR_Altium.PrjPcb` |
| Validate | `Validate Changes` 버튼 → 모든 변경 사항 초록색 체크 |
| Execute | `Execute Changes` → PCB에 부품/네트 로드 |
| Close | 완료 후 Close |

**문제 해결:**

| 오류 | 원인 | 해결 |
|------|------|------|
| Footprint not found | 심볼에 풋프린트 미연결 | Properties → Models → Add Footprint |
| Component not found | 라이브러리 누락 | Libraries 패널에서 재검색 |
| Duplicate designator | Annotate 누락 | Tools → Annotate Schematics 재실행 |
| Net not found | 와이어 연결 오류 | 회로도로 돌아가 수정 후 재시도 |

**Import 후 확인:**

- 모든 부품이 Board Shape 내에 배치되었는가? (Room 임시 영역 확인)
- Rooms 자동 생성 → 불필요한 Room은 삭제 (`Del`)
- 모든 Net이 PCB에 로드되었는가? → `Panels → PCB → Nets` 확인

### 7.6 PCB 뷰 설정

| 설정 | 경로 | 값 |
|------|------|-----|
| Measurement | `View → Toggle Units` (Ctrl+Q) | **mm** (Metric) |
| Grid | `View → Grid → Snap Grid` | **0.1mm** (배치), **0.05mm** (라우팅) |
| Display | `View → Board Planning Mode` (1) | 2D 레이아웃 |
| Color | `View → Board Planning Color` | Top=Red, Bottom=Blue |

---

## Step 8: 부품 배치 (Placement) (1h 30min)

### 8.1 배치 전략 개요

**OpenCR 보드 영역 구분 (105×75mm):**

```
┌─────────────────────────────────────────────────┐
│ 상단 (Y=70~75): DYNAMIXEL 커넥터 (J6, J8, J25)  │
│   J15~J17 (RS-485), J18~J20 (CAN/UART)         │
├─────────────────────────────────────────────────┤
│ 좌측 (X=0~30): 전원부                            │
│   LM5175, XL4005, LDO, 인덕터, 벌크 캡           │
├─────────────────────────────────────────────────┤
│ 중앙 (X=30~70): STM32F746 MCU                   │
│   크리스탈(좌), 바이패스 캡, Ferrite Bead        │
├─────────────────────────────────────────────────┤
│ 우측 (X=70~105): 모터 드라이버 + IMU             │
│   A3906 x2, ICM-20648, 모터 출력 커넥터          │
├─────────────────────────────────────────────────┤
│ 하단 (Y=0~10): USB, 통신 인터페이스               │
│   ZX62D-B-5P8, STMPS2141, EMIF02              │
└─────────────────────────────────────────────────┘
```

### 8.2 Room 배치 활용

Room을 활용한 자동 배치:

| 단계 | 조작 |
|------|------|
| Room 생성 | `Design → Rooms → Create Room from Component` → 특정 부품 선택 |
| Room 분류 | 전원부/MCU/통신 등 기능별 Room 생성 |
| Room 이동 | Room 클릭 → 드래그 → 배치 영역 지정 |

**Room 배치 예시:**

```
Room_Power: LM5175, XL4005, IL1117, AZ1117, F1, inductor, bulk caps
Room_MCU: STM32F746, crystal Y1/Y2, SWD header
Room_Motor: A3906 x2, motor terminal connectors
Room_Comm: TJF1051, MAX3443, ICM-20648
Room_USB: ZX62D, STMPS2141, EMIF02
Room_DXL: J6, J8, J25, J15~J17, J18~J20
```

### 8.3 배치 도구

| 도구 | 단축키 | 설명 |
|------|--------|------|
| Move | `M-C` (Click) | 부품 클릭 후 이동 |
| Rotate | `Space` | 90° 회전 |
| Flip | `F` | 부품을 Bottom 레이어로 플립 |
| Align | `Edit → Align` | 좌/우/상/하 정렬 |
| Distribute | `Edit → Align → Distribute` | 균등 간격 배치 |
| Position | `M-S` (Snap Grid) | 그리드에 스냅 |
| Arrange | `Tools → Component Placement` | 자동 배치 (참고용) |

**정렬 유용 단축키:**

| 단축키 | 기능 |
|--------|------|
| `Ctrl+L` | Align Left |
| `Ctrl+R` | Align Right |
| `Ctrl+T` | Align Top |
| `Ctrl+B` | Align Bottom |
| `Ctrl+Shift+H` | Distribute Horizontally |
| `Ctrl+Shift+V` | Distribute Vertically |

### 8.4 부품 상세 배치 가이드

#### 전원부 배치 (좌측 X=0~30mm)

**LM5175PWPR (U4):**

```
        ┌──────────────────┐
        │   LM5175PWPR     │
        │  (10 × 10mm)     │
        └──────────────────┘

  입력측 (좌): C3(10uF), C4(0.1uF), 입력 커넥터
  상단: L1(4.7uH, XAL6060) → 최단 거리 배치 (SW 노드 최소화)
  하단: R5(15k) + C9(10nF) → COMP 핀 근접
  우측: 출력 캡 C7(22uF × 2), C8(0.1uF)
  하단: FB 분압 저항 R3(49.9k), R4(4.99k) → FB 핀 3mm 이내
```

**XL4005 (U5):**

```
  VIN: C11(100uF) XL4005 근접
  SW: L2(10uH) → D2(Schottky) → 출력 캡
  FB: R9(4.7k), R10(1.5k) → FB 핀 직근
  GND: PGND → GND plane via stitch
```

**LDO (U6, U7):**

```
  IL1117-5.0: USB 5V 입력 측에 배치
  AZ1117H-3.3: XL4005 출력 측에 배치 (5V → 3.3V)
  입/출력 캡: 각 LDO 핀 5mm 이내
  열 방출: GND pad → thermal via array (4×4)
```

#### MCU 배치 (중앙 X=30~70mm)

**STM32F746ZGT6 (U1, LQFP-144, 20×20mm):**

```
  ┌──────────────────────────────────┐
  │         STM32F746ZGT6            │
  │          (20×20mm)               │
  └──────────────────────────────────┘

  좌측 (X=30): Y1(25MHz), Y2(32.768kHz) → MCU 좌측 5mm 이내
  상단: DYNAMIXEL TX/RX 신호 → 상단 커넥터
  하단: USB, CAN 신호 → 하단 커넥터
  우측: IMU I2C, 모터 PWM → 우측
  VCAP1/VCAP2: C18/C19(2.2uF) → 핀 3mm 이내, GND via 직근
  NRST: SW1 + R11(10k) pull-up → MCU 우측 하단
  SWD: 5핀 헤더 → MCU 우측 (PA13/PA14 접근 용이)
```

**크리스탈 배치 (중요!):**

```
  ┌─── 25MHz ──┐
  │   Y1(SX-32)│ ← MCU PE0/PE1에서 5mm 이내
  │  Guard Ring│ ← GND via guard ring으로 감싸기
  └────────────┘
  C21(22pF) C22(22pF)
      │         │
     GND via  GND via
```

- 크리스탈 하단에 **다른 신호 트레이스 배치 금지**
- Guard Ring: Y1 주변을 GND via로 감싸서 EMI 차폐
- 32.768kHz(Y2)도 동일한 원칙, 단 거리는 덜 민감

#### 통신/모터 배치 (우측 X=70~105mm)

**A3906 x2 (U2, U3):**

```
  ┌──────────────────┐
  │   A3906 (U2)     │
  │  모터 1 (우상)    │
  └──────────────────┘
  좌측: IN1(PB0), IN2(PB1), PWM(PA0), SLEEP(PC0)
  상단: OUT1, OUT2 → 모터 출력 커넥터로 최단 거리
  하단: VREF sense → R15(0.1Ω) → PGND
  우측: VM → VCC_12V via array (전류 2A 이상)
```

**ICM-20648 (U6, QFN-24, 4×4mm):**

```
  ┌──────────┐
  │ICM-20648 │ ← MCU 우측, I2C 라인 최단 거리
  └──────────┘
  상단: VDD/VIO → C30(100nF), C32(100nF) 직근
  좌측: SDA(PB9), SCL(PB8) → R18/R19(4.7k) pull-up to 3.3V
  하단: INT(PE0) → MCU 방향
  중심: GND pad → thermal via (1개)
  I2C 라인: 0.2mm, 5mm 이내로 유지
```

#### 커넥터 배치 (가장자리)

| 커넥터 | 위치 | 방향 | 비고 |
|--------|------|------|------|
| J6/J8/J25 (B3B-EH-A) | 상단 Y=74, X=10~90 | 위쪽 | TTL DYNAMIXEL |
| J15~J17 (B4B-EH-A) | 상단 Y=74, X=10~90 | 위쪽 | RS-485 DYNAMIXEL |
| J18~J20 (20010WS-04) | 상단 Y=74, X=10~90 | 위쪽 | CAN/UART |
| J1 (ZX62D-B-5P8) | 하단 Y=1, X=45~65 | 아래쪽 | Micro-B USB |
| F1 (0453010) | 좌측 X=2, Y=40 | - | 퓨즈 |
| SW1 | 우측 X=90, Y=40 | - | 리셋 버튼 |

### 8.5 바이패스 캡 배치 규칙

**핵심 원칙: 각 VDD 핀 → 100nF 캡 → GND via**

```
   ┌──── VDD 핀 ──── 100nF ──── GND via ────┐
   │         <── 2mm 이내 ──>                │
   │                                          │
   └────────── 루프 면적 최소화 ─────────────┘
```

**QC (Quality Check):**
- 각 100nF 캡은 VDD 핀에서 **2mm 이내** 배치
- VDD 핀 → 캡 → GND via 순서로 배선
- 동일 전원 그룹의 bulk cap(10µF)은 1~2개 추가

### 8.6 배치 후 검증

| 도구 | 경로 | 확인 사항 |
|------|------|-----------|
| Cross Probe | `Tools → Cross Probe` | 회로도 핀 → PCB 부품 강조 |
| Component Clearance | `Tools → Design Rule Check` | 부품 간 간격 위반 확인 |
| Measure | `Reports → Measure Distance` | 실제 거리 측정 |
| Density Map | `View → Density Map` | 배치 밀도 시각화 (빨간색 = 밀집) |

---

## Step 9: PCB 배선 (Routing) (1h 30min)

### 9.1 Interactive Routing 기초

| 조작 | 단축키 | 설명 |
|------|--------|------|
| 라우팅 시작 | `P-T` 또는 `Ctrl+W` | Interactive Routing 모드 |
| 클릭 | Left Click | 트레이스 시작/코너/종료 |
| 더블클릭 | Left Double Click | 트레이스 종료 (연결까지) |
| 우클릭 | Right Click | 취소 / 모드 종료 |
| Track Width | `Shift+W` | 너비 선택 창 |
| Via 추가 | `2` (숫자) | 클릭 위치에 via 삽입 |
| 레이어 전환 | `*` (별표) | via 삽입 + 레이어 변경 |
| Routing Mode | `~` (틸데) | Walkaround / Push / Avoid / Hug |
| Snap | `Ctrl` | 그리드 무시 자유 각도 |
| Undo | `Ctrl+Z` | 마지막 동작 취소 |

**Routing Mode 설명:**

| 모드 | 설명 | 사용 시기 |
|------|------|-----------|
| **Walkaround** | 장애물을 자동으로 우회 | 복잡한 배선 영역 |
| **Push** | 기존 트레이스를 밀어내며 배선 | 밀집 구역 |
| **Avoid** | 기존 트레이스와 거리 유지 | 신호 무결성 중요 |
| **Hug** | 기존 트레이스에 밀착 | 공간 절약 |

### 9.2 라우팅 우선순위

**신호 중요도별 라우팅 순서:**

| 순위 | 신호 | 규칙 | 특이사항 |
|------|------|------|----------|
| 1 | **크리스탈 25MHz** | 최단 거리, guard ring | HSE, 1mm 이내 |
| 2 | **크리스탈 32.768kHz** | 최단 거리, guard ring | LSE, 2mm 이내 |
| 3 | **USB D+/D-** | Differential Pair 90Ω | 길이 정합 ±1mm |
| 4 | **전원 12V** | 폭 2mm, via array | 4.5A 전류 용량 |
| 5 | **전원 5V** | 폭 1.5mm, via array | 4A 전류 용량 |
| 6 | **전원 3.3V** | 폭 0.8mm | 0.5A 이하 |
| 7 | **SDIO** | 0.2mm, 길이 정합 | 클럭 30mm 이내 |
| 8 | **I2C (IMU)** | 0.2mm, pull-up 근접 | 50mm 이내 |
| 9 | **UART** | 0.2mm | 100mm 이하 |
| 10 | **GPIO** | 0.2mm | 자유 배선 |

### 9.3 크리스탈 라우팅 (1순위)

**25MHz 크리스탈 (Y1):**

```
   ┌─────────────────────────────────┐
   │ Guard Ring (GND via chain)      │
   │    ┌─── Y1 ───┐                │
   │    │           │   <── 5mm      │
   │    C21    C22  │                │
   │    │       │   │                │
   └────┴───────┴───┴────────────────┘
         │       │
        GND     GND
         │       │
   PE0 ──┤      ├── PE1
   (OSC_IN)    (OSC_OUT)

   - 트레이스 길이: 3mm 이내
   - 트레이스 폭: 0.2mm
   - 45° 코너 사용 (90° 금지)
   - 하단 레이어(GND/PWR)에 크리스탈 직하 배선 금지
```

### 9.4 USB Differential Pair 라우팅 (3순위)

| 단계 | 조작 |
|------|------|
| Differential Pair | `Route → Interactive Differential Pair Routing` |
| Pair 선택 | Net1 = USB_DP(PA12), Net2 = USB_DM(PA11) |
| Width/Gap | 0.35mm / 0.2mm (Top Layer, 90Ω) |
| 클릭 | 시작점 → 끝점까지 단일 클릭으로 라우팅 |

**Differential Pair 라우팅 규칙:**

| 규칙 | 값 | 설명 |
|------|-----|------|
| Physical Width | 0.35mm | 각 트레이스 폭 |
| Physical Gap | 0.2mm | 쌍 간 간격 |
| Impedance | 90Ω ±10% | USB 2.0 High Speed |
| Max Length | 50mm | MCU → USB 커넥터 |
| Length Tolerance | ±1mm | 길이 정합 |
| Layer | Top Layer | GND plane 참조 |

**EMIF02-USB03F2 라우팅:**

```
  MCU(PA11) ── 0.35mm ──► EMIF02(IN1) ── OUT1 ── 0.35mm ──► ZX62D(D+)
  MCU(PA12) ── 0.35mm ──► EMIF02(IN2) ── OUT2 ── 0.35mm ──► ZX62D(D-)
                              │
                            GND via (직근)
```

### 9.5 전원 트레이스 (4~6순위)

**12V 트레이스 (2mm 폭, 최대 4.5A):**

| 전류 | PCB 폭 (1oz) | PCB 폭 (2oz) |
|------|-------------|-------------|
| 1A | 0.3mm | 0.15mm |
| 2A | 0.7mm | 0.35mm |
| 3A | 1.2mm | 0.6mm |
| **4.5A** | **2.0mm** | **1.0mm** |

**전원 트레이스 전략:**

```
  LM5175 SW ─── 2mm ──► L1(4.7uH) ── 2mm ──► D1(Schottky) ──► VCC_12V
                    │                              │
                Via array(×4)                 Via array(×4)
                    │                              │
                PWR Plane(Layer 3)           PWR Plane(Layer 3)
```

**Via 전류 용량:**

| Via 크기 | 전류 (1oz) | 비고 |
|----------|-----------|------|
| 0.6mm/0.3mm (via/hole) | 0.5A | 표준 via |
| 0.8mm/0.4mm | 0.8A | 전원 via |
| 1.0mm/0.5mm | 1.2A | 고전류 via |

**12V 4.5A → 0.5A/via → 최소 9개의 via 필요**
→ **Via array (4×3 = 12개의 via)** 권장

### 9.6 Polygons (Copper Pour)

| 단계 | 조작 |
|------|------|
| Polygon Pour | `Place → Polygon Pour` |
| Net | GND |
| Layer | Top Layer (Bottom에도 진행) |
| Remove Dead Copper | ✅ ON |
| Pour Over Same Net | ✅ ON (패드 위로 덮기) |
| Thermal Relief | Relief Connect (4 spokes, 0.3mm) |
| Min Width | 0.3mm |
| Grid | 0.5mm (Hatch mode) or Solid |

**GND Polygon Pour 순서:**

1. Top Layer GND polygon → 보드 전체 영역
2. Bottom Layer GND polygon → 보드 전체 영역
3. **GND via stitching** → MCU 주변, 전원부, 모서리 등에 GND via 배치
4. **Thermal Relief 확인** → GND 패드의 방열 연결 확인

**PWR Split Plane (Layer 3 Internal Plane 2):**

| 단계 | 조작 |
|------|------|
| Split Plane | `Design → Split Plane` |
| Layer | Internal Plane 2 (PWR) |
| Net | VCC_12V → 영역 지정 (좌상단 전원부) |
| Net | VCC_5V → 영역 지정 (우상단) |
| Net | VCC_3V3 → 영역 지정 (MCU 영역) |

**Split Plane 영역:**

```
┌─────────────────────────────────────┐
│  VCC_12V (좌상단)                    │
│    ┌────────────────┐               │
│    │ LM5175, XL4005 │  VCC_5V       │
│    │  12V 영역       │  (우상단)     │
│    └────────────────┘  LDO, USB     │
│                         ┌───────────┤
│                         │ VCC_3V3   │
│                         │ (중앙)    │
│                         │ MCU, IMU  │
│                         └───────────┤
│    ──── Split Line (0.5mm gap) ────│
└─────────────────────────────────────┘
```

### 9.7 PCB 배선 완료 체크

**라우팅 완료 기준:**
- 모든 신호선 연결 완료 (Un-Routed Net = 0)
- 전원 트레이스 폭 준수 (12V=2mm, 5V=1.5mm, 3.3V=0.8mm)
- 크리스탈 최단 거리 + guard ring
- USB Differential Pair 90Ω + 길이 정합
- I2C 라인 50mm 이내
- Polygons pour 완료
- GND via stitching 배치

---

## Step 10: DRC + 거버 출력 (1h)

### 10.1 Design Rule Check (DRC)

| 단계 | 조작 |
|------|------|
| DRC 실행 | `Tools → Design Rule Check → Run DRC` |
| Rules To Check | 모든 규칙 활성화 (Electrical, Routing, SMT, Plane) |
| Violations 표시 | Messages 패널에서 확인 |

**DRC Violations 해결:**

| 위반 유형 | 원인 | 해결 방법 |
|-----------|------|-----------|
| Clearance Violation | 트레이스/패드 간 간격 부족 | 트레이스 재배치 또는 폭 축소 |
| Un-Routed Net | 연결되지 않은 신호 | 누락된 트레이스 연결 |
| Un-Connected Pin | 납땜되지 않은 핀 | 핀 연결 또는 No Connect 마커 |
| Width Violation | 규정 폭 미달 | 트레이스 폭 수정 |
| SMD Neck-Down | SMD 패드에서 트레이스 폭 급감 | 트레이스 폭 균일화 |
| Via Hole Size | 비아 홀 규격 위반 | 비아 교체 |
| Polygon Violation | Polygons 간 간격 부족 | Polygon 재작성 |

**DRC 출력 확인:**

| 항목 | 조건 |
|------|------|
| Total Violations | **0** (모든 규칙 통과) |
| Un-Routed Nets | **0** |
| Un-Connected Pins | **0** (의도적 미연결 제외) |
| Clearance Errors | **0** |

### 10.2 Polygon Manage

| 단계 | 조작 |
|------|------|
| Polygon 관리 | `Tools → Polygon Pours → Pour All` |
| 재계산 | 모든 Polygon 재계산 → air gap 확인 |
| 충돌 확인 | Polygon 가장자리가 트레이스/패드와 충분한 이격 확인 |

### 10.3 Gerber 출력 (RS-274X)

| 단계 | 조작 |
|------|------|
| Gerber 실행 | `File → Fabrication Outputs → Gerber Files` |
| **General** | Format: **2:5** (0.01µm resolution), RS-274X |
| **Layers** | Plot Layers: |
| | ☑ Top Layer (GTL) |
| | ☑ GND Layer (GPL) |
| | ☑ PWR Layer (GPL) |
| | ☑ Bottom Layer (GBL) |
| | ☑ Top Overlay (GTO) |
| | ☑ Bottom Overlay (GBO) |
| | ☑ Top Paste (GTP) — SMD stencil |
| | ☑ Bottom Paste (GBP) |
| | ☑ Top Solder Mask (GTS) |
| | ☑ Bottom Solder Mask (GBS) |
| | ☑ Board Outline (GKO) |
| **Drill Drawing** | ☑ Plot used drill pairs |
| **Film** | Generate → Output 폴더에 저장 |

**Gerber 파일 목록:**

| 확장자 | 설명 |
|--------|------|
| .GTL | Top Layer |
| .GTS | Top Solder Mask |
| .GTO | Top Overlay (Silkscreen) |
| .GTP | Top Paste (Stencil) |
| .G1 | Internal Plane 1 (GND) |
| .G2 | Internal Plane 2 (PWR) |
| .GBL | Bottom Layer |
| .GBS | Bottom Solder Mask |
| .GBO | Bottom Overlay |
| .GBP | Bottom Paste |
| .GKO | Board Outline |
| .GM1~.GMn | Mechanical Layers |
| .GD1 | Drill Drawing |
| .GG1 | Drill Guide |
| .TXT | NC Drill (Excellon) |

### 10.4 NC Drill 출력

| 단계 | 조작 |
|------|------|
| NC Drill 실행 | `File → Fabrication Outputs → NC Drill Files` |
| Format | **2:5** (Inches) 또는 **4:4** (Metric) |
| Units | **Millimeters** |
| Leading/Trailing | **Suppress Leading Zeros** |
| Excellon | **Yes** (Excellon format) |

### 10.5 Pick & Place 출력

| 단계 | 조작 |
|------|------|
| Pick & Place | `File → Assembly Outputs → Generates pick and place files` |
| Format | **CSV** |
| Units | **mm** |
| Top/Bottom | 개별 파일 생성 |

**CSV 파일 내용 예시:**
```
Designator, Mid X, Mid Y, Layer, Rotation
R1, 25.4, 30.5, Top, 0
C1, 30.2, 28.1, Top, 90
U1, 35.0, 40.0, Top, 0
```

### 10.6 출력 파일 ZIP 압축

제조사에 전달할 출력물을 ZIP으로 일괄 압축:

```
OpenCR_REVH_Manufacturing/
├── Gerber/
│   └── OpenCR_REVH.zip (모든 Gerber + NC Drill)
├── Assembly/
│   ├── OpenCR_REVH_TopPos.csv
│   └── OpenCR_REVH_BottomPos.csv
├── BOM/
│   └── OpenCR_REVH_BOM.xlsx
├── 3D/
│   └── OpenCR_REVH.step
└── OpenCR_REVH_RevH_Schematic.pdf
```

---

## Step 11: 3D 시각화 + 설계 검토 (1h)

### 11.1 3D 모드 전환

| 조작 | 단축키 | 설명 |
|------|--------|------|
| 2D → 3D | `2` | 2D 레이아웃에서 3D로 전환 |
| 3D → 2D | `3` 또는 `Shift+2` | 3D에서 2D로 복귀 |
| 회전 | `Shift + 마우스 우클릭 드래그` | 자유 각도 회전 |
| 확대/축소 | `Ctrl + 마우스 휠` | 줌 인/아웃 |
| 이동 | `Ctrl + Shift + 마우스 우클릭` | 화면 팬 |
| Top View | `5` | 상단 직교 뷰 |
| Bottom View | `6` | 하단 직교 뷰 |
| 와이어프레임 | `W` | Solid ↔ Wireframe 토글 |
| 부품 선택 | 3D 상태에서 부품 클릭 | Properties 패널 표시 |

### 11.2 STEP 모델 매핑

**3D Body 추가:**

| 단계 | 조작 |
|------|------|
| Footprint Manager | `Tools → Footprint Manager` |
| 풋프린트 선택 | 모든 IC 풋프린트 선택 |
| 3D Body | View → 3D Body → Create |
| STEP 모델 | `Embedded` 또는 `Linked` STEP 파일 지정 |
| 위치 보정 | X/Y/Z Offset, Rotation 조정 |

**부품별 STEP 모델:**

| 부품 | 3D 모델 출처 | 패키지 형상 |
|------|-------------|-----------|
| STM32F746ZGT6 | Altium MPS 내장 / 3D ContentCentral | LQFP-144 (20x20mm, 높이 1.4mm) |
| LM5175PWPR | Altium 라이브러리 | HTSSOP-28 (9.7x4.4mm) |
| A3906SESTR-T | 제조사 STEP 요청 | QFN-20 (4x4mm) |
| ICM-20648 | TDK/InvenSense 제공 | QFN-24 (4x4mm) |
| XL4005 | 유사 TO-263 모델 활용 | TO-263-5 |
| ZX62D-B-5P8 | Hirose 공식 모델 | Micro-B (7.1x2.5mm) |

### 11.3 PCB 3D 모델 표현

| 설정 | 경로 | 값 |
|------|------|-----|
| 보드 두께 | `Layer Stack Manager → 3D View` | 1.6mm 반영 |
| 보드 색상 | `View → Board Planning Color → 3D Board` | Green (FR4) |
| 구리 두께 | 3D 설정에서 표현 | 1oz = 0.035mm |
| 솔더 마스크 | 기본 설정 | 초록색 |

### 11.4 설계 검토

**3D 설계 검토 체크리스트:**

| 검토 항목 | 확인 방법 | 기준 |
|-----------|-----------|------|
| 보드 두께 | 3D 측정 도구 | 1.6mm (±10%) |
| 커넥터 높이 | Z축 확인 | 케이블 삽입 공간 확보 |
| 부품 간섭 | Clash Detection | 부품 간 물리적 충돌 없음 |
| 열 방출 | 전원부 thermal via | LM5175 주변 via 8개 이상 |
| 리플로우 가능성 | 부품 간격 | QFN 0.5mm pitch → 솔더 페이스트 적정 |
| 보드 가장자리 | 커넥터 위치 | 보드 외곽 2mm 이내 커넥터 배치 |
| 기구 간섭 | 케이싱 STEP 오버레이 | 나사 구멍/기둥 위치 확인 |

**3D Clash Detection:**

| 단계 | 조작 |
|------|------|
| Clash 실행 | `Tools → 3D Body Manager → Check Clash` |
| 해석 범위 | 모든 3D Body |
| 결과 | 충돌 부품 리스트 → 간격 또는 위치 조정 |

### 11.5 ActiveBOM (BOM 자동 생성)

| 단계 | 조작 |
|------|------|
| ActiveBOM 생성 | `Project → ActiveBOM` |
| BOM Items | 모든 부품의 Part Number, Manufacturer 자동 매핑 |
| 가격 확인 | Live Price (Altium 계정 필요) |
| 재고 확인 | Live Stock (Octopart 연동) |
| Alternate 부품 | Equivalent 부품 추천 및 추가 |

**ActiveBOM 리포트 예시:**

| Item | Designator | Value | Manufacturer | MFR Part # | Qty | Price (1k) |
|------|-----------|-------|-------------|------------|-----|-----------|
| 1 | U1 | STM32F746ZGT6 | STMicro | STM32F746ZGT6 | 1 | $12.50 |
| 2 | U4 | LM5175PWPR | TI | LM5175PWPR | 1 | $3.20 |
| 3 | U2, U3 | A3906SESTR-T | Allegro | A3906SESTR-T | 2 | $2.80 |
| 4 | U6 | ICM-20648 | TDK | ICM-20648 | 1 | $4.50 |
| 5 | R1~R30 | Various 0402/0603 | - | - | 30 | $0.01 |

**BOM 출력:** `Reports → Bill of Materials` → Format: **Excel(.xlsx)** 또는 **CSV**

### 11.6 3D PDF / STEP 내보내기

| 포맷 | 메뉴 | 용도 |
|------|------|------|
| STEP 3D | `File → Export → STEP 3D` | 기구 설계 전달 (.step) |
| 3D PDF | `File → Export → PDF3D` (Parasolid) | 리뷰/발표용 (.pdf) |
| IDF | `File → Export → IDF` | 기구 툴 전달 (.emn/.emp) |

---

## Step 12: 최종 발표 + 리뷰 (30min)

### 12.1 Altium 설계 산출물 정리

**필수 산출물 목록:**

| 산출물 | 생성 방법 | 파일명 |
|--------|-----------|--------|
| ✅ Schematic PDF | `File → Smart PDF` | `OpenCR_REVH_Schematic.pdf` |
| ✅ Gerber RS-274X | `File → Fabrication → Gerber` | `OpenCR_REVH.zip` |
| ✅ NC Drill | `File → Fabrication → NC Drill` | `OpenCR_REVH.TXT` |
| ✅ BOM | `Reports → Bill of Materials` | `OpenCR_REVH_BOM.xlsx` |
| ✅ Pick & Place | `File → Assembly → Pick & Place` | `OpenCR_REVH_TopPos.csv` |
| ✅ 3D PDF | `File → Export → PDF3D` | `OpenCR_REVH_3D.pdf` |
| ✅ STEP 3D | `File → Export → STEP 3D` | `OpenCR_REVH.step` |
| ✅ ODB++ | `File → Fabrication → ODB++` | `OpenCR_REVH.odb` |
| ✅ ActiveBOM | `Project → ActiveBOM → Report` | `OpenCR_REVH_ActiveBOM.xlsx` |

### 12.2 설계 리뷰 체크리스트

**Schematic (회로도) 검토:**

| 체크 항목 | 상태 |
|-----------|------|
| DRC (ERC) Violations = 0 | ☐ |
| 모든 부품 Designator 할당 | ☐ |
| Net Label 오타/중복 없음 | ☐ |
| Power Port 네트 올바름 | ☐ |
| Floating 핀 처리 (NC 마커) | ☐ |
| 크리스탈 Load Cap 적절함 | ☐ |
| 바이패스 캡 개수/값 적절함 | ☐ |
| Pull-up/Pull-down 저항 누락 없음 | ☐ |

**PCB Layout 검토:**

| 체크 항목 | 기준 | 상태 |
|-----------|------|------|
| DRC Violations | **0** | ☐ |
| Un-Routed Nets | **0** | ☐ |
| Un-Connected Pins | **0** | ☐ |
| Differential Pair Impedance | 90Ω ±10% | ☐ |
| 12V Power Trace Width | ≥ 2mm (4.5A) | ☐ |
| 5V Power Trace Width | ≥ 1.5mm (4A) | ☐ |
| GND Via Stitching | MCU 주변, 전원부 | ☐ |
| Power Plane Split | VCC_12V / 5V / 3.3V 분리 | ☐ |
| Decoupling Cap 위치 | VDD 핀 2mm 이내 | ☐ |
| Crystal Guard Ring | 완전 감싸기 | ☐ |
| Crystal 하단 배선 금지 | 다른 신호 없음 | ☐ |
| USB D+/D- 길이 정합 | ±1mm 이내 | ☐ |
| 커넥터 방향 | 외부 접근 용이 | ☐ |
| Board Shape | 105×75mm | ☐ |
| Silkscreen 가독성 | 겹침 없음 | ☐ |

### 12.3 설계 개선 포인트 (참고)

| 영역 | 제안 사항 |
|------|-----------|
| EMC | 크리스탈 guard ring 추가, GND plane 완전성, ferrite bead |
| 열 관리 | LM5175 패드 thermal via (4×4), XL4005 TO-263 방열판 |
| 신호 무결성 | USB 90Ω impedance control, I2C pull-up 4.7k |
| 제조성 | 0402 패드 디자인 규칙, Solder mask expansion |
| 테스트 | SWD + UART test points (TP1~TP10) |

### 12.4 팀 발표 가이드

**발표 구성 (5분):**

1. **설계 개요 (30초)**
   - OpenCR 하드웨어 개요, Altium Designer 사용 목적

2. **회로도 설계 (1분)**
   - 전원 체인 (buck-boost → buck → LDO)
   - MCU 주변회로 (전원/클럭/디버그)
   - 통신 인터페이스 (CAN, RS-485, I2C)

3. **PCB 레이아웃 (1분 30초)**
   - 배치 전략 (기능별 영역 분할)
   - 4층 Stack (Top/GND/PWR/Bottom)
   - Differential Pair 라우팅 (USB 90Ω)

4. **설계 검증 (1분)**
   - DRC 결과 (Violations 0)
   - 3D 시각화 (부품 간섭 없음)
   - ActiveBOM (부품 가용성 확인)

5. **소감 / 어려웠던 점 (1분)**
   - 가장 도전적이었던 부분
   - Altium Designer 사용 경험
   - 추후 개선하고 싶은 부분

### 12.5 Altium Designer 경험 소감 (참고)

**장점:**
- 회로도-PCB **양방향 동기화** (ECO)로 실수 방지
- Manufacturer Part Search로 부품 검색 및 라이브러리 생성 자동화
- 3D 시각화로 기구 간섭 사전 확인
- ActiveBOM으로 부품 단가/재고 실시간 확인
- 직관적인 Differential Pair 라우팅

**주의할 점:**
- Commercial software → Educational license 적극 활용
- 초기 학습 곡선이 있음 (단축키 암기 필요)
- 대형 프로젝트에서는 라이브러리 관리 중요
- 정기적인 Backup 필수 (프로젝트 전체 압축 저장)

### 12.6 참고 자료

| 자료 | 링크 / 설명 |
|------|------------|
| Altium Documentation | https://www.altium.com/documentation |
| Altium Live Training | https://www.altium.com/live-training |
| Altium YouTube | https://www.youtube.com/AltiumOfficial |
| STM32F746 Datasheet | STMicroelectronics 웹사이트 (RM0385) |
| OpenCR HW Reference | ROBOTIS OpenCR 공식 저장소 |

---

**축하합니다! 2일 과정을 완료했습니다.** 🎉

이 과정을 통해 여러분은 **Altium Designer**를 활용한 **전문 PCB 설계 워크플로우**를 경험했습니다. OpenCR 레퍼런스 하드웨어를 기반으로 회로도 설계부터 PCB 레이아웃, 제조 출력까지 전 과정을 실습했습니다.

이 경험을 바탕으로 자신만의 임베디드 시스템 프로젝트를 설계해보세요!

# Day 2: PCB 설계 (PCB Layout) — 7시간

---

## Step 7: PCB 설정 및 풋프린트 할당 (1시간 30분)

### 7.1 PCB Editor (Pcbnew) 열기

1. **Schematic Editor**에서 `Tools → Open PCB Editor` (단축키: 도구모음 PCB 아이콘)
2. 또는 Project Manager에서 **PCB Editor** 아이콘 클릭
3. **첫 실행 시** — 회로도와 PCB 동기화 확인 대화상자 → **Yes**

> **📸 Screenshot:** Pcbnew 초기 화면 — 빈 PCB 캔버스 + 좌측 툴바 + 우측 레이어 패널

### 7.2 Board Setup (보드 설정)

`File → Board Setup` (또는 우측 Properties 패널에서 **Board Settings** 아이콘)

#### (1) Layers — 4층 설정

`Board Stackup → Layers`에서 다음 레이어 활성화:

| 레이어 | 타입 | 용도 |
|:---|:---|:---|
| **F.Cu** | Signal (Top) | 주요 신호 배선 (horizontal) |
| **In1.Cu** | Signal (Inner) | **GND Plane** (solid copper pour) |
| **In2.Cu** | Signal (Inner) | **Power Plane** (3.3V / 5V / 12V split) |
| **B.Cu** | Signal (Bottom) | 보조 신호 배선 (vertical) |

- In1.Cu, In2.Cu를 추가하려면 `Add Layer` 버튼 클릭
- 각 레이어 이름 더블클릭 → 사용자 지정 이름: `In1.GND`, `In2.PWR`

#### (2) Stackup — 두께 설정

| 층 | 재질 | 두께 |
|:---|:---|:---:|
| Top Solder Mask | LPI | 0.025mm |
| **F.Cu** | Copper | **0.035mm (1oz)** |
| Prepreg | FR4 | 0.2mm |
| **In1.GND** | Copper | **0.035mm (1oz)** |
| Core | FR4 | 1.0mm |
| **In2.PWR** | Copper | **0.035mm (1oz)** |
| Prepreg | FR4 | 0.2mm |
| **B.Cu** | Copper | **0.035mm (1oz)** |
| Bottom Solder Mask | LPI | 0.025mm |
| **총 두께** | | **1.6mm** |

#### (3) Design Rules — 기본 규칙

| 항목 | 값 | 설명 |
|:---|:---:|:---|
| **Clearance** | `0.15mm` | 최소 이격 거리 (6mil) |
| **Track Width** | `0.15mm` (min) | 일반 신호선 폭 |
| **Via Diameter** | `0.7mm` | 비아 외경 |
| **Via Hole** | `0.4mm` | 비아 드릴 구경 |
| **Clearance (same net)** | `0.0mm` | 동일 네트워크는 제약 없음 |
| **Edge Clearance** | `0.3mm` | 보드 가장자리 이격 |

> **⚠️ 참고:** 0.15mm clearance는 일반 PCB 제조사 사양 (6mil 규칙). 저렴한 제조사의 경우 0.2mm (8mil) 권장.

### 7.3 Footprint Assignment (풋프린트 할당)

1. **Schematic Editor**에서 `Tools → Assign Footprints` (또는 Pcbnew에서 `Tools → Assign Footprints`)
2. 각 부품에 풋프린트 지정 (3열: Symbol / Footprint / Library)

| 심볼 (Value) | 풋프린트 | 라이브러리 경로 |
|:---|:---|:---|
| **STM32F746ZGT6** | `LQFP-144_20x20mm_P0.5mm` | `Package_QFP` |
| **LM5175PWPR** | `HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.4x6.1mm` | `Package_SO` |
| **XL4005** | `TO-263-5_TabPin3` | `Package_TO_SOT_SMD` |
| **AZ1117H-3.3** | `SOT-223-3_TabPin2` | `Package_TO_SOT_SMD` |
| **IL1117-5.0** | `SOT-223-3_TabPin2` | `Package_TO_SOT_SMD` |
| **A3906** | `QFN-20-1EP_4x4mm_P0.5mm_EP2.7x2.7mm` | `Package_DFN_QFN` |
| **ICM-20648** | `QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm` | `Package_DFN_QFN` |
| **TJF1051T/3** | `SOIC-8_3.9x4.9mm_P1.27mm` | `Package_SO` |
| **MAX3443ECSA+** | `SOIC-8_3.9x4.9mm_P1.27mm` | `Package_SO` |
| **STMPS2141STR** | `SOT-23-5` | `Package_TO_SOT_SMD` |
| **EMIF02-USB03F2** | `QFN-8-1EP_2x2mm_P0.5mm` | `Package_DFN_QFN` |
| **JST B3B-EH-A** | `JST_EH_B3B-EH-A` | `Connector_JST` |
| **JST B4B-EH-A** | `JST_EH_B4B-EH-A` | `Connector_JST` |
| **20010WS-04** | `PinHeader_1x04_P2.54mm_Vertical` | `Connector_PinHeader_2.54mm` |
| **ZX62D-B-5P8** | `USB_Micro-B_Zx62D` | `Connector_USB` |
| **0453010 (Fuse)** | `Fuse_2512_6332Metric` | `Fuse` |
| **0402 R / C** | `R_0402_1005Metric` / `C_0402_1005Metric` | `Resistor_SMD` / `Capacitor_SMD` |
| **0603 R / C** | `R_0603_1608Metric` / `C_0603_1608Metric` | `Resistor_SMD` / `Capacitor_SMD` |
| **SX-32 (25MHz)** | `Crystal_SMD_3225-4pin_3.2x2.5mm` | `Crystal` |
| **CM315 (32.768kHz)** | `Crystal_SMD_3215-2pin_3.2x1.5mm` | `Crystal` |

3. **Mapping 방법:**
   - 각 행 더블클릭 → Footprint Browser 열림
   - 검색창에 키워드 입력 (예: `LQFP-144`)
   - 미리보기로 핀 배열 확인
   - 선택 후 `OK`

> **📸 Screenshot:** Footprint Assignment 대화상자 — STM32F746ZGT6에 LQFP-144 할당 중인 화면

### 7.4 Footprint Editor — 누락 풋프린트 직접 생성

공식 라이브러리에 없는 풋프린트는 직접 생성합니다.

**예: XL4005 TO-263-5 풋프린트 만들기**

1. `Tools → Footprint Editor`
2. `File → New Footprint`
3. **Name:** `TO-263-5_Handsoldering`
4. **패드 생성:**
   - `Place → Pad` (단축키 `P`)
   - Pad 1 (좌측): 위치 (0, 0), Size 1.5×2.0mm, Shape Rounded Rect
   - Pad 2~4: 2.54mm 간격
   - Pad 5 (Tab): 중심 (5.08, 0), Size 3.5×3.0mm (열 방출용)
   - **Layer:** `F.Cu`
5. **Courtyard 추가:**
   - `Place → Graphic Shape` → Rectangle
   - 부품 외곽에 0.25mm clearance 유지한 사각형
6. **3D 모델 연결:**
   - 우측 Properties → 3D Models → 폴더 아이콘
   - KiCAD 기본 3D 라이브러리에서 `TO-263-5` 검색
7. `File → Save` → 프로젝트 풋프린트 라이브러리에 저장

> **💡 Tip:** 풋프린트 생성 시 Datasheet의 **Package Mechanical Drawing**을 반드시 참고하세요. 패드 위치와 크기는 IPC-7351 규격을 권장합니다.

---

## Step 8: 부품 배치 (Placement) — 1시간 30분

### 8.1 Board Outline 생성

1. **레이어 선택:** `Edge.Cuts` (드롭다운에서 선택)
2. `Place → Rectangle` (또는 `Graphic Polygon`)
3. **좌표 입력 (105mm × 75mm):**
   - 시작점: (0, 0)
   - 끝점: (105, 75)
4. 또는 `Place → Line`으로 4변을 각각 그림:
   - (0,0) → (105,0) → (105,75) → (0,75) → (0,0)
5. 보드 원점 설정: `Place → Drill/Place Offset` → (0,0) 기준

> **📸 Screenshot:** Edge.Cuts에 105×75mm 직사각형 보드 외곽선이 그려진 화면

### 8.2 Mounting Holes (장착 구멍)

1. **풋프린트 추가:** `Place → Footprint` (단축키 `O`)
2. `MountingHole:MountingHole_3.2mm` 검색 및 배치
3. 4개 모서리 위치 (보드 가장자리에서 5mm 안쪽):

| 구멍 | X | Y |
|:---:|:---:|:---:|
| MH1 | 5 | 5 |
| MH2 | 100 | 5 |
| MH3 | 5 | 70 |
| MH4 | 100 | 70 |

### 8.3 부품 배치 전략 (OpenCR 기준)

**Zone 분할:**

```
┌─────────────────────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  │
│  │ 전원부    │  │ MCU      │  │ 모터    │  │ 커넥터  │  │
│  │ LM5175   │  │ STM32F7  │  │ A3906   │  │ JST B3  │  │
│  │ XL4005   │  │ 주변회로  │  │ x2      │  │ JST B4  │  │
│  │ LDO      │  │ 크리스탈  │  │         │  │ 20010WS │  │
│  └──────────┘  └──────────┘  └─────────┘  └─────────┘  │
│                                        ┌──────────────┐ │
│                                        │ USB (ZX62D)  │ │
│                                        └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

#### (1) 전원부 배치 (보드 좌측)

| 순서 | 부품 | 배치 기준 |
|:---:|:---|:---|
| 1 | DC Jack (J1) | 좌측 하단 가장자리 |
| 2 | Fuse (F1) | DC Jack 바로 우측 |
| 3 | TVS (D1) + C1~C3 | Fuse 우측 (입력 필터) |
| 4 | **LM5175PWPR (U2)** | 입력단 우측, 12V 영역 |
| 5 | L2 (4.7µH) | U2 우측 (SW 노드 최단) |
| 6 | **XL4005 (U3)** | LM5175 우측, 5V 영역 |
| 7 | **AZ1117 (U4)**, **IL1117 (U5)** | XL4005 우측 (3.3V 영역) |

**키 포인트:**
- 전원부는 **입력에서 출력 방향**으로 직선 배치 (좌→우)
- 전력 경로 (Vin → Buck-boost → LDO)를 짧게 유지
- LM5175 주변 SW 노드는 **넓은 copper 영역** 확보
- 인덕터 L2, L3는 서로 수직 배치 → **자기 결합 방지**

#### (2) MCU 배치 (보드 중앙)

| 부품 | 위치 |
|:---|:---|
| STM32F746 (U1) | 보드 중앙 (X=52.5, Y=37.5) |
| 25MHz Crystal (X1) | U1 좌측 상단 (최대 10mm 이내) |
| 32.768kHz (X2) | U1 좌측 하단 |
| SWD (J2) | U1 우측 하단 (보드 가장자리) |
| Reset SW (SW1) | U1 상단 (사용자 접근 용이) |

**키 포인트:**
- MCU는 **보드 중앙**에 위치 → 모든 주변 IC까지 배선 길이 균등
- 크리스탈은 MCU와 **10mm 이내**, 다른 신호선과 격리
- 바이패스 캡은 **각 VDD 핀 바로 옆** (최대 3mm 이내)
- SWD 커넥터는 **보드 가장자리** (프로그래밍 케이블 접근 용이)

#### (3) 모터 드라이버 배치 (보드 우측)

| 부품 | 위치 |
|:---|:---|
| A3906 #1 (U7) | 보드 우측 상단 |
| A3906 #2 (U8) | 보드 우측 중앙 |
| 모터 출력 캡 | U7, U8 근처 (VBB 바이패스) |

**키 포인트:**
- 모터 드라이버는 **모터 커넥터 가까이** (출력 트레이스 최단)
- VBB (모터 전원) 트레이스: **2mm 이상** (고전류)
- SENSE 저항은 드라이버 바로 옆 (Kelvin connection 고려)

#### (4) 커넥터 배치 (보드 가장자리)

| 부품 | 위치 |
|:---|:---|
| JST B3B-EH-A (J5~J7) | **보드 상단** (DYNAMIXEL 케이블 연결) |
| JST B4B-EH-A (J8~J10) | **보드 상단** (RS-485 케이블 연결) |
| 20010WS-04 (J11~J13) | **보드 우측 or 하단** |
| USB Micro-B (J14) | **보드 하단 중앙** |

#### (5) IMU 배치 (MCU 근접)

| 부품 | 위치 |
|:---|:---|
| ICM-20648 (U10) | MCU 우측 상단, **10mm 이내** |

**키 포인트:**
- I2C 라인 (SDA/SCL) 최단 거리 유지
- IMU는 **보드 진동 최소 지점** (모서리보다 중앙 근처)
- IMU 아래 GND copper pour (노이즈 차폐)

### 8.4 배치 후 3D 뷰어 확인

1. `View → 3D Viewer` (단축키: `Alt+3`)
2. **회전:** 마우스 좌클릭 드래그
3. **확대/축소:** 마우스 휠
4. **이동:** Ctrl + 마우스 좌클릭 드래그
5. 확인 사항:
   - 모든 부품이 Board Outline 안에 있는가?
   - 부품 간 충돌 (겹침) 없는가?
   - 커넥터 방향이 보드 바깥쪽을 향하는가?
   - 높이 간섭 있는 부품 확인 (특히 LDO 방열판)

> **📸 Screenshot:** 3D 뷰어에서 부품 배치 완료된 OpenCR 보드 — 전원부(좌측), MCU(중앙), 모터 드라이버(우측)

---

## Step 9: PCB 배선 (Routing) — 1시간 30분

### 9.1 4층 스택 라우팅 전략

| 레이어 | 배선 방향 | 용도 | 비고 |
|:---|:---:|:---|:---|
| **F.Cu** (Top) | ↔ **Horizontal** (수평) | 주요 신호, 고속 신호 | 크리스탈, USB, SWD |
| **In1.GND** | — (Solid pour) | **GND Plane** | 노이즈 차폐, 리턴 경로 |
| **In2.PWR** | — (Split pour) | **전원 분할 평면** | 3.3V / 5V / 12V 분할 |
| **B.Cu** (Bottom) | ↕ **Vertical** (수직) | 보조 신호, GND pour | |

**수평/수직 교차 배선 원칙:**
- F.Cu는 수평, B.Cu는 수직으로 배선하여 **크로스토크 최소화**
- 레이어 변경은 **Via**로 연결

### 9.2 배선 규칙 (Track Width)

| 신호 종류 | 폭 (Width) | 최대 전류 | 예시 |
|:---|:---:|:---:|:---|
| **12V 전원** | **2.0mm** | 4.5A | 모터 전원, VBB |
| **5V 전원** | **1.5mm** | 4.0A | XL4005 출력, USB VBUS |
| **3.3V 전원** | **0.5mm ~ 1.0mm** | 0.5A | MCU VDD, LDO 출력 |
| **GND** | Copper pour | — | 전체 면 |
| **일반 신호** | **0.2mm (8mil)** | — | GPIO, I2C, UART |
| **고속 신호** | **0.25mm** | — | 크리스탈, CAN |
| **USB DP/DN** | **0.3mm** | — | Differential pair, 90Ω |
| **SWD** | **0.2mm** | — | SWDIO, SWCLK |

### 9.3 Interactive Routing

1. **Route tracks 도구:** `Place → Route tracks` (단축키 `X`)
2. **설정:** 우측 Properties 패널에서:
   - **Track width:** `0.2mm` (일반) / **Via size:** `0.7/0.4mm`
   - **Routing mode:** `Shove` (Push and Shove)
   - **Mouse to set:** 시작점 클릭 → 경로 클릭 → 종점 더블클릭

#### 단축키 모음 (배선 중):

| 단축키 | 기능 |
|:---:|:---|
| `V` | Via 삽입 (레이어 전환) |
| `B` | Shove 모드 토글 |
| `/` | 레이어 전환 (F.Cu ↔ B.Cu) |
| `Backtick` | 라우팅 완료 |
| `Ctrl+Z` | Undo |
| `W` | 트레이스 폭 변경 (실시간) |

### 9.4 전원 배선 (Power Routing)

**12V 전원 (2.0mm):**
```
LM5175 SW 노드 → L2(4.7µH) → 12V 출력 → XL4005 VIN
                                → 모터 VBB (각 A3906)
                                → DYNAMIXEL TTL 커넥터
```

- **SW 노드:** LM5175 (HO1/LO1 → L2) 구간은 **넓은 copper**
- **In2.PWR 레이어:** 12V 영역을 polygon pour로 할당 (다른 전압과 split)

**5V 전원 (1.5mm):**
```
XL4005 출력 → 5V 라인 → IL1117 VIN
                        → AZ1117 VIN (통해 3.3V)
                        → UART/CAN 커넥터
```

**3.3V 전원 (0.5~1.0mm):**
```
AZ1117 출력 → STM32F746 모든 VDD 핀
            → ICM-20648 VDD/VI0
            → TJF1051 VCC
            → MAX3443 VCC
```

- **각 LDO 출력 → MCU VDD 핀:** 방사형(Fan-out) 배선
- **In2.PWR 레이어:** 3.3V와 5V를 polygon pour로 분할

### 9.5 고속 신호 배선

#### (1) 25MHz 크리스탈 (최단 배선)

```
X1(OSC_IN) ──── (0.2mm, 3mm max) ──── MCU(OSC_IN)
X1(OSC_OUT) ─── (0.2mm, 3mm max) ──── MCU(OSC_OUT)
```

- **Guard Ring:** 크리스탈 주변을 GND via로 감싸기
- **아래 레이어:** In1.GND (크리스탈 아래에 다른 신호선 배치 금지)
- **Load cap (C16, C17):** 크리스탈과 MCU 사이, 가능한 가깝게

#### (2) USB Differential Pair (DP/DN)

| 파라미터 | 값 |
|:---|:---:|
| **임피던스** | **90Ω differential** |
| **트레이스 폭** | **0.3mm** |
| **갭 (간격)** | **0.2mm** |
| **길이 매칭** | ±1mm 이내 |
| **레이어** | F.Cu (연속, via 금지) |

**배선 룰:**
```
EMIF02(D+) ──── (DP, 0.3/0.2mm) ──── MCU_PA11(OTG_DP)
EMIF02(D-) ──── (DN, 0.3/0.2mm) ──── MCU_PA12(OTG_DN)
```

- **Differential pair 도구:** `Place → Differential Pair Route`
- 길이 차이 보정: 더 긴 쪽에 **Meander (구불구불)** 추가

#### (3) CAN 버스 (TJF1051)

```
MCU(PB9/TX) ─── (0.25mm) ─── TJF1051(TXD)
MCU(PB8/RX) ─── (0.25mm) ─── TJF1051(RXD)
TJF1051(CANH) ── (0.5mm) ─── J13(CANH)
TJF1051(CANL) ── (0.5mm) ─── J13(CANL)
120Ω 종단 저항: CANH와 CANL 사이, 커넥터 가까이
```

### 9.6 일반 신호 배선 (Fan-out)

**STM32F746 LQFP-144 Fan-out 전략:**

1. **Breakout (핀에서 Via까지):**
   - 각 핀에서 0.2mm 트레이스로 외곽 via까지 연결
   - Via는 IC 본체에서 2~3mm 이내 배치
   - Via-to-pin: 45° 각도로 나오기

2. **Inner route (Via 이후):**
   - F.Cu에서 B.Cu로 via 전환 후 배선 완료
   - In1.GND와 In2.PWR은 via로 연결하지 않음 (plane 유지)

> **💡 Tip:** LQFP-144의 핀 피치가 0.5mm로 좁습니다. **2개의 핀 사이로 1개 트레이스**만 통과 가능합니다. 핀 사이로 배선이 어려우면 **via-in-pad**나 **B.Cu**를 적극 활용하세요.

### 9.7 Via Stitching (GND Plane 연결)

1. **GND via stitching:** 보드 전체에 GND via를 규칙적으로 배치
2. **배치 방법:**
   - `Tools → Via Stitching` (또는 수동 배치)
   - 격자 간격: 5mm (고주파 영역은 2~3mm)
   - 각 GND via: `0.7mm 외경 / 0.4mm 내경`
3. **효과:**
   - F.Cu GND pour ↔ In1.GND plane 연결
   - EMI 저감 (리턴 전류 경로 최단)
   - 방열 효과

> **📸 Screenshot:** PCB 배선 완료 화면 — F.Cu(빨강) 수평 배선, B.Cu(파랑) 수직 배선, In1.GND(진한 초록) solid pour

---

## Step 10: DRC + 거버 출력 (1시간)

### 10.1 Design Rule Check (DRC)

1. `Inspect → Design Rules Checker` (단축키: `Ctrl+D`)
2. **DRC 실행: `Run DRC` 버튼**

**DRC 검사 항목:**

| 항목 | 설명 | 기준 |
|:---|:---|:---:|
| **Clearance violations** | 트레이스/패드 간 간격 위반 | 0건 |
| **Unconnected items** | 미연결 핀, 스터브 | 0건 |
| **Track width violations** | 최소 트레이스 폭 위반 | 0건 |
| **Via size violations** | 최소 비아 크기 위반 | 0건 |
| **Hole size violations** | 최소 드릴 구경 위반 | 0건 |
| **Silkscreen clearance** | 실크스크린과 패드 간섭 | 0건 |

**오류 해결 예시:**

| 오류 | 원인 | 해결 |
|:---|:---|:---|
| `Clearance violation: 0.12mm < 0.15mm` | 트레이스 간 거리 부족 | 간격 확보 or track 재배치 |
| `Unconnected items: Pad X on Net Y` | 핀 미연결 | 배선 추가 or via 연결 |
| `Track width < min: 0.1mm < 0.15mm` | 너무 가는 트레이스 | width 0.15mm로 수정 |
| `Broken track` | 배선 단절 | 재연결 |

### 10.2 Copper Pour (구리 면)

1. **F.Cu GND pour:**
   - `Place → Zone` (단축키: `Ctrl+Z`)
   - **Layer:** `F.Cu`
   - **Net:** `GND`
   - **Zone Fill Mode:** `Solid`
   - **Thermal Relief:** `Yes` (패드/비아 연결부만 방사형)
   - 보드 외곽선 따라 zone 영역 지정 → `Fill All Zones` (단축키: `B`)

2. **B.Cu GND pour:**
   - 동일한 방법으로 B.Cu에도 GND zone 추가

3. **In2.PWR Split pour:**
   - 각 전압 영역 (12V, 5V, 3.3V)을 polygon으로 분할
   - `Place → Zone` → Net: `VCC_12V` → 영역 지정
   - 반복: `VCC_5V`, `VCC_3V3`
   - 영역 간 clearance: `0.25mm` (전압 절연)

**Keepout 영역:**
- 안테나, RF 부품 아래 → `Place → Zone Keepout`
- 커넥터 실크스크린 영역 → GND pour 제외

4. **Zone Fill 후 확인:**
   - `Tools → Zone Fill Manager` (단축키: `B`)
   - `Fill All Zones` 클릭
   - DRC 다시 실행 (Zone fill로 발생한 위반 검사)

> **📸 Screenshot:** Copper Pour 완료 화면 — F.Cu GND pour (빨강 해치), In2.PWR split planes (3색 영역)

### 10.3 Gerber 출력 (PCB 제조 파일)

1. `File → Plot` (또는 `File → Fabrication Outputs → Gerbers`)

**Plot 레이어 선택:**

| 레이어 | 포함 | 포맷 |
|:---|:---|:---:|
| ✅ **F.Cu** | Top copper | RS-274X |
| ✅ **B.Cu** | Bottom copper | RS-274X |
| ✅ **In1.Cu** | Inner GND plane | RS-274X |
| ✅ **In2.Cu** | Inner PWR plane | RS-274X |
| ✅ **Edge.Cuts** | Board outline | RS-274X |
| ✅ **F.Silkscreen** | Top silkscreen (부품번호) | RS-274X |
| ✅ **B.Silkscreen** | Bottom silkscreen | RS-274X |
| ✅ **F.Mask** | Top solder mask | RS-274X |
| ✅ **B.Mask** | Bottom solder mask | RS-274X |
| ❌ **F.Paste** | Top paste (선택, 리플로우용) | RS-274X |
| ❌ **B.Paste** | Bottom paste (선택) | RS-274X |
| ❌ **F.Adhesive / B.Adhesive** | 접착제 (미사용) | — |

**Plot 설정:**
- **Format:** `Gerber RS-274X`
- **Output directory:** `output/gerber/`
- **Options:**
  - ✅ `Plot footprint values` (부품 값 포함)
  - ✅ `Plot footprint references` (RefDes 포함)
  - ✅ `Exclude PCB edge layers from other plots`
  - ✅ `Use extended X2 format` (호환성)
  - ✅ `Include netlist attributes` (IPC-2581 네트워크 정보)

**Plot 버튼 클릭 → 각 레이어별 `.gbr` 파일 생성**

### 10.4 Drill Files (드릴 파일)

1. `File → Drill` (또는 `File → Fabrication Outputs → Drill Files`)

**Drill 설정:**
- **Output format:** `Gerber X2`
- **Drill units:** `Millimeters`
- **Zeros format:** `Suppress leading zeros`
- **Output directory:** `output/gerber/`

**Generate Drill File → `.drl` 파일 생성**

### 10.5 Gerber ZIP 압축

```powershell
# PowerShell에서 ZIP 압축
Compress-Archive -Path "output/gerber/*" -DestinationPath "output/gerber.zip"
```

**Gerber 파일 목록 (예시):**
```
OpenCR_KiCAD-F_Cu.gbr
OpenCR_KiCAD-B_Cu.gbr
OpenCR_KiCAD-In1_Cu.gbr
OpenCR_KiCAD-In2_Cu.gbr
OpenCR_KiCAD-Edge_Cuts.gbr
OpenCR_KiCAD-F_Silkscreen.gbr
OpenCR_KiCAD-B_Silkscreen.gbr
OpenCR_KiCAD-F_Mask.gbr
OpenCR_KiCAD-B_Mask.gbr
OpenCR_KiCAD.drl
OpenCR_KiCAD.drl-NPTH.drl  (비도금 홀)
```

---

## Step 11: 3D 시각화 + 설계 검토 (1시간)

### 11.1 3D 뷰어

1. `View → 3D Viewer` (단축키: `Alt+3`)
2. **조작 방법:**
   - **회전:** 마우스 좌클릭 + 드래그
   - **확대:** 마우스 휠 (또는 우클릭 + 상하 드래그)
   - **이동:** Ctrl + 좌클릭 + 드래그
   - **초점 맞춤:** `Home` 키
3. **보기 옵션:**
   - `View → Realistic mode` (실제 색상)
   - `View → Transparent mode` (내부 레이어 확인)
   - `View → Show board body` (보드 본체 ON/OFF)

> **📸 Screenshot:** 3D 뷰어에서 OpenCR PCB — 모든 부품 3D 모델이 표시된 실제 보드 모습

### 11.2 보드 통계 확인

1. `Tools → PCB Calculator` → `Board Statistics` 탭
2. 확인 사항:
   - **Total tracks:** 배선 완료된 트레이스 수
   - **Total vias:** 배치된 비아 수
   - **Unconnected pads:** 미연결 패드 수 (0이어야 함)
   - **Footprints total:** 전체 부품 수
   - **Board area:** `105mm × 75mm = 7,875mm²`

### 11.3 설계 검토 — 상세 체크리스트

#### (1) 전원부 검토
- [ ] 전원 입력 역전압 보호 (TVS 다이오드) 배치됨?
- [ ] LM5175 SW 노드 copper 영역 충분한가?
- [ ] 피드백 저항 (R2, R3) 값이 계산값과 일치?
- [ ] XL4005 출력 캐패시터 (100µF) 충분한가?
- [ ] LDO 입/출력 캡 (10µF) 배치됨?
- [ ] 각 전원 Plane 분할 (In2.PWR) 완료?

#### (2) MCU 검토
- [ ] 모든 VDD 핀에 바이패스 캡 (100nF) 배치됨?
- [ ] VCAP_1/VCAP_2에 2.2µF 캡 연결됨?
- [ ] VDDA + VREF+ 필터 회로 (Ferrite bead + cap) 구성됨?
- [ ] NRST 풀업 10kΩ + 스위치 연결됨?
- [ ] BOOT0 풀다운 10kΩ 처리됨?
- [ ] SWD 10핀 커넥터 올바르게 연결?

#### (3) 고속 신호 검토
- [ ] 25MHz 크리스탈 트레이스 최단 거리 (10mm 이내)?
- [ ] 크리스탈 주변 GND guard ring 배치?
- [ ] USB DP/DN differential pair (90Ω, 길이 매칭)?
- [ ] 각 크리스탈 아래 In1.GND plane (다른 신호선 없음)?

#### (4) 일반 검토
- [ ] DRC 오류 0건?
- [ ] 모든 부품에 풋프린트 할당됨?
- [ ] 실크스크린 텍스트 가독성 (크기, 위치)?
- [ ] 커넥터 방향 (보드 외부 접근 용이)?
- [ ] Mounting hole (4곳, Φ3.2mm) 배치됨?
- [ ] 보드 크기 105×75mm 준수?

### 11.4 열 설계 검토

| 부품 | 발열량 | 방열 대책 |
|:---|:---:|:---|
| **LM5175PWPR** | ~1.5W | HTSSOP Exposed Pad → GND via array + In1.GND plane |
| **XL4005** | ~2W | TO-263 Tab via → In2.PWR (5V plane) |
| **A3906 × 2** | 각 ~0.5W | QFN Exposed Pad → GND via array |
| **AZ1117 / IL1117** | ~0.3W | SOT-223 Tab → GND copper pour |
| **Ferrite Bead (L1)** | ~0.1W | 주변 GND via |

**열 via 배치 권장:**
- Exposed Pad IC 아래: **6~9개의 thermal via** (0.4mm hole, 0.7mm outer)
- Via는 반대편 GND plane과 연결하여 열 확산

### 11.5 신호 무결성 점검

| 항목 | 기준 | 확인 방법 |
|:---|:---|:---|
| 크리스탈 트레이스 길이 | 10mm 이내 | 거리 측정 도구 |
| USB DP/DN 길이 차이 | ±1mm 이내 | 길이 측정 |
| 크리스탈 아래 plane | Solid GND (no split) | 레이어별 확인 |
| IC 간 신호선 | 병렬 배선 최소화 | 시각 검사 |
| Power/GND via 간격 | Power via 1개당 GND via 1개 | 비아 배치 검토 |

> **📸 Screenshot:** 3D 뷰어 투명 모드 — 내부 In1.GND plane이 보이는 상태

---

## Step 12: 최종 발표 + 리뷰 (30분)

### 12.1 KiCAD 설계 산출물 정리

#### (1) Schematic PDF 출력

1. Schematic Editor에서 `File → Plot` (또는 `File → Export → PDF`)
2. **Options:**
   - **PDF color:** `Color` (or `B/W` for print)
   - **Pages:** `All sheets`
   - **Output directory:** `output/pdf/`
3. `Plot` 버튼 → `OpenCR_KiCAD_Schematic.pdf`

#### (2) BOM CSV 생성

1. Schematic Editor에서 `Tools → Generate BOM`
2. **BOM Plugin 선택:**
   - `bom_csv_grouped_by_value` (권장 — 값별 그룹화)
   - 또는 `bom_csv_sorted_by_ref` (RefDes 정렬)
3. `Generate` 버튼 → `output/bom/OpenCR_KiCAD_BOM.csv`

**BOM 예시:**
```
RefDes,Qty,Value,Footprint,Manufacturer
C1,C2,C3,3,10µF 25V MLCC,C_0603_1608Metric,Samsung
C4,C5,2,100nF 25V MLCC,C_0402_1005Metric,Samsung
R1,1,0.01Ω 1% 1W,R_2512_6332Metric,Vishay
U1,1,STM32F746ZGT6,LQFP-144_20x20mm_P0.5mm,ST
U2,1,LM5175PWPR,HTSSOP-28-1EP,Texas Instruments
...
```

#### (3) Gerber ZIP

- 최종 Gerber 파일: `output/gerber.zip`
- 포함 내용: 9개 Gerber 레이어 + 1개 Drill 파일

#### (4) 3D STEP 파일

1. PCB Editor에서 `File → Export → STEP`
2. **Options:**
   - **STEP format:** `AP214 (ISO 10303)` (호환성 최고)
   - **Include 3D models:** ✅ (부품 3D 모델 포함)
   - **Output file:** `output/step/OpenCR_KiCAD.step`
3. `Export` 버튼

### 12.2 설계 리뷰 체크리스트 (최종)

| 번호 | 체크 항목 | 상태 |
|:---:|:---|:---:|
| 1 | Schematic ERC 오류 0건 | `___ / 0` |
| 2 | PCB DRC 오류 0건 | `___ / 0` |
| 3 | 모든 부품 풋프린트 할당 완료 | `___ / ___` |
| 4 | 모든 핀 연결 완료 (미연결 0개) | `___ / 0` |
| 5 | 각 전원 레일 바이패스 캡 배치 | `___ / 11` |
| 6 | 크리스탈 트레이스 최단 (10mm 이내) | `___ mm` |
| 7 | USB differential pair 90Ω | `___ Ω` |
| 8 | 보드 크기 105×75mm | `___ × ___` |
| 9 | 4층 스택업 설정 완료 | `___ / 4` |
| 10 | Gerber 출력 정상 생성 | `___ / 10` |

### 12.3 팀별 발표 (15분)

**발표 주제 (선택 1):**
1. **전원 설계 과정:** LM5175 buck-boost 설계 시 고려사항, 발열 해결 방법
2. **MCU 주변회로:** 크리스탈 레이아웃 시 문제점과 해결
3. **PCB 배선 전략:** 4층 스택업의 장점, differential pair 배선 경험

**발표 내용 구성:**
- **도입:** 설계 목표 (OpenCR 호환 보드)
- **본론:** 주요 설계 결정과 그 이유
  - ex) "LM5175 SW 노드의 Copper 면적을 넓게 확보한 이유는..."
  - ex) "크리스탈을 MCU에서 5mm 이내에 배치한 이유는..."
- **문제 해결:** DRC 오류, 배선 충돌, 풋프린트 누락 등
- **결론:** 최종 설계 결과 + 향후 개선 사항

### 12.4 향후 학습 로드맵

| 단계 | 주제 | 추천 자료 |
|:---:|:---|:---|
| 1 | **KiCAD 고급 기능** | Python Scripting, SPICE Simulation |
| 2 | **고속 신호 설계** | DDR3/4, HDMI, PCIe 라우팅 |
| 3 | **RF 설계** | 50Ω impedance, Antenna matching |
| 4 | **열 설계 심화** | 열 시뮬레이션, Heatsink 설계 |
| 5 | **PCB 제조 공정** | Panelization, Impedance control, DFM |

---

## 📝 Day 2 요약

| 학습 항목 | 키워드 |
|:---|:---|
| PCB 설정 | 4층 Stackup, Design Rules, Impedance |
| 풋프린트 | LQFP-144, HTSSOP, QFN, SOIC, SOT-223 |
| 부품 배치 | Zone 분할, Fan-out, 열 관리 |
| 배선 (Routing) | Horizontal/Vertical, Differential Pair, Power Width |
| 검증 (DRC) | Clearance, Unconnected, Copper Pour |
| 출력 | Gerber RS-274X, Drill, STEP, BOM CSV |

> **🎯 최종 목표:** 2일 과정을 마치면, 여러분은 KiCAD 8로 **4층 PCB 보드**의 회로도 설계부터 PCB 레이아웃, Gerber 출력까지 **전 과정을 독자적으로 수행**할 수 있습니다!

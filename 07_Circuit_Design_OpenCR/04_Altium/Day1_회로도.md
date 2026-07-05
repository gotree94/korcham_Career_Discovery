# Day 1: 회로도 (Schematic) 설계 — 7시간

---

## Step 1: Altium Designer 설치 및 프로젝트 생성 (40min)

### 1.1 Altium Designer 설치

1. [Altium 공식 사이트](https://www.altium.com/products/downloads) 방문 → **Altium Designer** 다운로드
2. 설치 실행 → Next → 라이선스 동의 → 설치 경로 확인 (C:\Program Files\Altium\AD2x)
3. 라이선스 등록:
   - **Educational License**: 학생/교사 → Altium 계정 생성 → My Altium → License Management → Sign In
   - **Trial License**: 30일 무료 평가판 (기능 제한 없음)
   - **On-Demand License**: 회사 라이선스 서버 접속
4. 설치 완료 후 **Preferences** 초기 설정:
   - `DXP → Preferences → Schematic → General` → Default Units: **Metric (mm)**
   - `DXP → Preferences → Schematic → Grid` → Grid Range: **10** (0.1mm grid)
   - `DXP → Preferences → PCB Editor → General` → Measurement Unit: **Metric**

### 1.2 새 프로젝트 생성

| 단계 | 조작 |
|------|------|
| 프로젝트 생성 | `File → New → Project → PCB Project` |
| 프로젝트 이름 설정 | Project 이름: `OpenCR_Altium`, Location: 원하는 폴더 |
| 프로젝트 저장 | `File → Save Project As → OpenCR_Altium.PrjPcb` |

프로젝트 폴더 구조 권장:
```
OpenCR_Altium/
├── OpenCR_Altium.PrjPcb
├── Source Documents/
│   ├── OpenCR_REVH.SchDoc
│   └── OpenCR_REVH.PcbDoc
├── Libraries/
│   └── OpenCR_SchLib.SchLib
└── Output/
```

### 1.3 회로도(Schematic) 문서 생성

| 단계 | 조작 |
|------|------|
| 새 회로도 | `Right-click 프로젝트 → Add New to Project → Schematic` |
| 파일명 | Save As → `OpenCR_REVH.SchDoc` |
| 페이지 설정 | `Design → Document Options → Sheet Options` |
| 용지 크기 | **A3** (297×420mm, landscape) |
| Grid 설정 | Visible Grid: **10** (가시 그리드), Snap Grid: **5** (스냅 그리드) |

### 1.4 인터페이스 둘러보기

| 패널 | 위치 / 단축키 | 용도 |
|------|---------------|------|
| **Projects** | 하단 탭 / `View → Panels → Projects` | 프로젝트 파일 트리 |
| **Libraries** | 우측 탭 / `View → Panels → Components` | 부품 검색 및 배치 |
| **Properties** | 우측 탭 / `View → Panels → Properties` | 선택 객체 속성 편집 |
| **SCH Inspector** | 우측 탭 / `View → Panels → SCH Inspector` | 핀/부품 속성 일괄 편집 |
| **Messages** | 하단 탭 | 컴파일/DRC 결과 표시 |

### 1.5 기본 단축키 (필수 암기)

| 단축키 | 기능 |
|--------|------|
| `P-W` | Place → Wire (와이어 연결) |
| `P-P` | Place → Part (부품 배치) |
| `P-N` | Place → Net Label (네트 레이블) |
| `P-O` | Place → Power Port (VCC/GND) |
| `P-T` | Place → Harness (버스 연결) |
| `P-R` | Place → Port (계층 포트) |
| `P-S` | Place → Sheet Symbol (계층 블록) |
| `N` | Net Label 생성 (단축) |
| `T-D` | Tools → Design Rule Check (DRC) |
| `Ctrl+S` | 저장 |
| `Ctrl+C` / `Ctrl+V` | 복사 / 붙여넣기 |
| `Space` | 회전 (배치 중) |
| `Tab` | 속성 편집 (배치 중) |
| `X` / `Y` | X축 / Y축 반전 |
| `Del` | 삭제 |
| `F11` | SCH Inspector 표시 |

### 1.6 Preferences 상세 설정

| 메뉴 경로 | 설정 항목 | 값 |
|-----------|-----------|-----|
| `Preferences → Schematic → General` | Default Power Object Style | **Bar** (또는 VCC/GND) |
| `Preferences → Schematic → General` | Default Pin Designator | **1** |
| `Preferences → Schematic → Graphical Editing` | Always Drag | **Enable** |
| `Preferences → Schematic → Compiler` | Error Reporting | **Fatal Error on duplicate net names** |
| `Preferences → PCB Editor → General` | Measurement Unit | **Metric (mm)** |
| `Preferences → PCB Editor → Display` | DirectX | **Enable (3D 성능 향상)** |

---

## Step 2: 부품 라이브러리 및 심볼 생성 (1h 20min)

### 2.1 Altium 내장 라이브러리 활용

Altium은 **Manufacturer Part Search (MPS)** 플러그인을 통해 6억 개 이상의 부품 데이터를 실시간 검색할 수 있습니다.

1. **Panels → Components** (우측 패널)
2. 상단 검색창에 `STM32F746ZGT6` 입력
3. 결과 선택 → **STMicroelectronics STM32F746ZGT6** 클릭
4. **Download** 버튼 → 심볼, 풋프린트, 3D STEP 모델, 데이터시트 URL이 **자동 로드**
5. 프로젝트 라이브러리에 추가: 우클릭 → `Add to My Library`

> **MPS로 부품을 가져올 경우 심볼 생성 시간을 80% 절약할 수 있습니다.**
> 단, 교육 목적으로는 **직접 심볼을 생성**하여 핀 배치의 논리적 구조를 이해하는 것을 권장합니다.

### 2.2 직접 라이브러리 생성 (.SchLib)

| 단계 | 조작 |
|------|------|
| 라이브러리 생성 | `File → New → Library → Schematic Library` |
| 파일 저장 | `OpenCR_SchLib.SchLib` (Libraries/ 폴더에 저장) |
| 첫 심볼 생성 | `Tools → New Component` → 이름: `STM32F746ZGT6` |
| 라이브러리 패널 | `View → Panels → SCH Library` (컴포넌트 관리) |

### 2.3 STM32F746ZGT6 심볼 생성 (144핀)

핀을 효율적으로 배치하려면 **IEEE Symbol 도구**와 **Pin Editor**를 활용합니다.

#### 핀 배치 전략

MCU 심볼은 **기능별 블록**으로 그룹핑하여 가독성을 높입니다:

```
┌────────────────────────────────────────┐
│  [VDD/VSS]  [VDDA]  [VCAP]   [VREF]   │  ← 상단: 전원 그룹
│                                        │
│  [OSC_IN/OUT]  [NRST]  [BOOT0]        │
│                                        │
│  [I2C1_SCL/SDA]  [UART_TX/RX]         │
│  [SPI_SCK/MISO/MOSI]  [SDIO]          │
│  [FDCAN1_RX/TX]  [USB_D+/D-]          │
│  [PWM(PA0~)]  [GPIO(PB0~PF15)]        │
│                                        │
│  [SWDIO/SWCLK]  [JTAG]                │  ← 하단: 디버그
└────────────────────────────────────────┘
```

#### 핀 위저드(Pin Editor) 사용

| 단계 | 조작 |
|------|------|
| Pin Editor 열기 | `Tools → Component Properties → Pin Editor` (좌측 하단 Edit Pins) |
| 핀 데이터 입력 | Display Name, Designator, Electrical Type, Pin Length 지정 |
| Electrical Type 종류 | **Input**, **Output**, **I/O**, **Power**, **GND**, **Passive**, **Open Collector**, **Open Emitter** |
| Pin Length | Power/GND: 20mil, Signal: 15mil, Clock: 25mil |

**주요 핀 목록 (일부):**

| 핀 번호 | 핀 이름 | 타입 | 비고 |
|---------|---------|------|------|
| 1 | PE0 | I/O | OSC_IN (25MHz) |
| 2 | PE1 | I/O | OSC_OUT (25MHz) |
| 13 | PC14 | I/O | OSC32_IN (32.768kHz) |
| 14 | PC15 | I/O | OSC32_OUT (32.768kHz) |
| 7 | NRST | Input | Reset, 10kΩ pull-up |
| 37 | PA13 | I/O | SWDIO |
| 39 | PA14 | I/O | SWCLK |
| 44 | PB9 | I/O | I2C1_SDA |
| 45 | PB8 | I/O | I2C1_SCL |
| 50 | PB2 | I/O | BOOT0 |
| 77 | PA0 | I/O | PWM_M1 |
| 78 | PA1 | I/O | PWM_M2 |
| 84 | PB0 | I/O | M1_IN1 |
| 85 | PB1 | I/O | M1_IN2 |
| 24 | PD0 | I/O | FDCAN1_RX |
| 25 | PD1 | I/O | FDCAN1_TX |
| 94 | PA11 | I/O | USB_DM |
| 95 | PA12 | I/O | USB_DP |
| 96 | PA10 | I/O | USB_ID |

> **Tip:** 모든 144핀을 입력하려면 Datasheet의 Pin Description 표를 CSV로 추출 → `Import from CSV` 기능(Pin Editor 우클릭) 사용

#### 핀 그룹화 (IEEE Symbol)

| 심볼 | 적용 핀 | 핀 모양 |
|------|---------|---------|
| **Clock** | PE0(OSC_IN), PC14(OSC32_IN) | 삼각형 |
| **Input** | NRST, BOOT0 | 오른쪽 화살표 |
| **Output** | PE1(OSC_OUT), PC15(OSC32_OUT) | 왼쪽 화살표 |
| **Tri-State** | PA13(SWDIO), PA14(SWCLK) | 화살표 + 삼각형 |
| **Power** | VDD, VDDA, VREF+ | 막대 모양 (Bar) |
| **Ground** | VSS, VSSA | GND 기호 |

핀 모양 변경: 핀 더블클릭 → `Graphical → Pin Shape` (Clock/Input/Output)

### 2.4 LM5175PWPR 심볼 생성 (28핀 HTSSOP-28)

1. `Tools → New Component` → Name: `LM5175PWPR`
2. **핀 배치 (열 기준):**

| 좌측 (1~14) | 우측 (15~28) |
|-------------|--------------|
| 1 EN (Input) | 28 VIN (Power) |
| 2 VCC (Power) | 27 UVLO (Input) |
| 3 SS (Input) | 26 RT (Input) |
| 4 COMP (Output) | 25 DIODE (Output) |
| 5 FB (Input) | 24 SW (Output) |
| 6 AGND (GND) | 23 PGND (GND) |
| 7~14 (NC) | 15~22 (NC) |

3. 전원/드라이버 핀은 **20mil 길이**로, 신호 핀은 **15mil**로 설정
4. **Parameters** 탭: Manufacturer = `Texas Instruments`, PartNumber = `LM5175PWPR`, DatasheetURL 추가

### 2.5 A3906SESTR-T 심볼 생성 (20핀 QFN-20)

```
         ┌───── 1 20 ─────┐
         │                 │
         │   A3906SESTR   │
         │                 │
         └───── 10 11 ────┘
```

| 핀 | 이름 | 타입 | 비고 |
|----|------|------|------|
| 1 | IN1 | Input | 모터 A 방향 제어 |
| 2 | IN2 | Input | 모터 A 방향 제어 |
| 3 | PWM | Input | 모터 A PWM 속도 |
| 4 | SLEEP | Input | 슬립 모드 (Active Low) |
| 5 | VREF | Input | 전류 기준 |
| 6 | VCC | Power | 5V |
| 7 | VM | Power | 12V 모터 전원 |
| 8 | OUT1 | Output | 모터 A 출력 1 |
| 9 | OUT2 | Output | 모터 A 출력 2 |
| 10 | PGND | Power | 전원 GND |
| 11~20 | (미러링) | - | 모터 B |

### 2.6 커넥터 심볼 생성

**B3B-EH-A (3핀, JST):**
- Pin1: TXD (Signal, 15mil)
- Pin2: RXD (Signal, 15mil)
- Pin3: GND (Power, 20mil)

**B4B-EH-A (4핀, JST):**
- Pin1: 485+ (Signal)
- Pin2: 485- (Signal)
- Pin3: VCC_12V (Power)
- Pin4: GND (Power)

### 2.7 심볼에 Model 연결

1. Properties 패널 → `Models` 섹션 → `Add → Footprint`
2. Footprint 모델 선택: `LQFP-144.pcbLib` (Altium 내장)
3. 또는 직접 생성: `File → New → Library → PCB Library` → LQFP-144 풋프린트 생성
4. **3D Model** 연결: `Add → 3D Model` → STEP 파일 경로 설정

### 2.8 심볼 작성 시 주의사항

- **Pin Visibility OFF**: 전원 핀은 숨김 처리하고 심볼 내부에서 Power Port 연결
- **Designator Prefix**: U? (IC), R? (Resistor), C? (Capacitor), J? (Connector)
- **IEEE Symbol**: Clock/Input/Output 핀 모양을 구분하면 가독성 향상
- **Pin Number vs Pin Name**: Pin Number는 반드시 실제 패키지 번호와 일치
- **Duplicate 핀 허용**: NC(No Connect) 핀은 Electrical Type = `Passive`로 설정

---

## Step 3: 전원부 회로도 작성 (1h 30min)

### 3.1 부품 배치 기본

| 조작 | 방법 |
|------|------|
| 부품 배치 | `P-P` 또는 `Components` 패널에서 드래그 |
| 와이어 연결 | `P-W` → 클릭 시작 → 클릭 종료 (더블클릭: 와이어 끝) |
| Net Label | `P-N` → 네트 이름 입력 → 와이어 위에 클릭 |
| Power Port | `P-O` → 원하는 스타일 선택 (VCC/GND) |
| Bus 연결 | `P-B` (버스 라인) + `P-B` (버스 엔트리) |
| 이동 | 클릭+드래그 또는 `Edit → Move → Move` |
| 회전 | `Space` (90°), `Space+Shift` (45°) |
| 복사 | `Ctrl+C` → 기준점 클릭 → `Ctrl+V` |

### 3.2 전원 체인 전체 구성

```
DC 입력 (5~24V)
    │
    ├─ F1 0453010 (10A) ─┬─ TVS 다이오드 ── GND
    │                     │
    ▼                     ▼
LM5175PWPR (Buck-Boost)   XL4005 (Buck)
    │                        │
    12V 출력                 5V 출력
    │                        │
    ├─ IL1117-5.0 ── 5V     ├─ AZ1117H-3.3 ── 3.3V
    │  (USB 5V 입력)         │
    │                        │
    ▼                        ▼
    Motor Driver             MCU/IMU/통신
```

### 3.3 DC 입력단

1. **Header 2 (2핀 전원 입력)**
   - 부품: Header 2 (J1)
   - Pin1: DC_IN (Power Port: VCC)
   - Pin2: GND

2. **Fuse + 보호 회로**
   - F1: `0453010` (10A, 125V) → J1 Pin1 직렬 연결
   - TVS1: `SMBJ24A` (24V clamp) → F1 출력 to GND
   - C1: 47uF/50V 전해 커패시터 (입력 벌크)
   - C2: 0.1uF/50V MLCC (고주파 바이패스)

### 3.4 LM5175PWPR Buck-Boost 회로 (5~24V → 12V / 4.5A)

LM5175PWPR은 넓은 입력 전압 범위에서 안정적인 12V 출력을 생성합니다.

```
┌─────────────────────────────────────────────────────┐
│                      LM5175PWPR                     │
│                                                      │
│  VIN ─┬───────────────────────────┬── VIN(28)       │
│       │                           │                 │
│       C3(10uF)  C4(0.1uF)       C5(4.7uF)          │
│       │                           │                 │
│       GND                         GND               │
│                                                      │
│  EN ─┬── R1(100k) ─┬── VCC_3V3     SW(24) ── L1 ─┬─ 12V_OUT │
│       │              │               4.7uH          │          │
│      R2(33k)        │                 (XAL6060)     │          │
│       │              │                              │          │
│       GND            │              DIODE(25)       │          │
│                      │                │             │          │
│  SS(3) ── C6(10nF) ─┤                D1(Schottky)  │          │
│                      │                │             │          │
│  FB(5) ─┬── R3(49.9k) ─── 12V_OUT    GND           │          │
│          │                                          │          │
│         R4(4.99k)                        C7(22uF x2) C8(0.1uF) │
│          │                                          │          │
│          GND                                       GND        │
│                                                      │
│  COMP(4) ── R5(15k) ── C9(10nF) ── C10(470pF) ── GND       │
│                                                              │
│  RT(26) ── R6(121k) ── GND  (fSW = 400kHz)                  │
│                                                              │
│  UVLO(27) ── R7(100k) ─┬── VIN                             │
│                         │                                   │
│                        R8(10k)                               │
│                         │                                   │
│                        GND                                   │
└─────────────────────────────────────────────────────────────┘
```

**주요 부품:**

| 부품 | 값 | 사이즈 | 설명 |
|------|-------|--------|------|
| L1 | 4.7µH | XAL6060 | 인덕터 (6×6mm) |
| D1 | Schottky 3A/40V | SMC | 부트스트랩 다이오드 |
| C6 (SS) | 10nF | 0603 | Soft-start 시간 설정 |
| R5 + C9 (COMP) | 15k + 10nF | 0603 | 보상 네트워크 (Type II) |
| R7/R8 (UVLO) | 100k / 10k | 0603 | 5V 언더볼tage 록아웃 |
| R3/R4 (FB) | 49.9k / 4.99k | 0603 | VOUT = 0.8 × (1 + 49.9k/4.99k) = 12V |

**출력 커패시터:** 22µF/25V MLCC x2 + 0.1µF MLCC — 세라믹 DC 바이어스 특성 고려하여 2개 병렬

### 3.5 XL4005 Buck 컨버터 (12V → 5V / 4A)

```
                    XL4005
                    ┌─────┐
  12V_IN ──────────►│VIN  │
                    │     │
  EN ─── 100k ────►│EN   │
                    │     │
  FB ◄─── R9(4.7k)─┤     ├── SW ──┬── D2(Schottky) ── GND
          │        └─────┘        │
         R10(1.5k)               L2(10uH)
          │                       │
         GND                     C11(100uF) C12(0.1uF)
                                 │
                                GND

  VOUT = 0.8 × (1 + 4.7k/1.5k) = 5.0V ✅
```

| 부품 | 값 | 설명 |
|------|-------|------|
| L2 | 10µH | 파워 인덕터 |
| D2 | SS34 (Schottky 3A/40V) | 프리휠링 다이오드 |
| C11 | 100µF/16V 전해 | 출력 벌크 |
| C12 | 0.1µF | 출력 바이패스 |

### 3.6 LDO 레귤레이터

**IL1117-5.0ET (USB 5V → 5V):**
```
USB_5V ─── C13(10uF) ─┬── VIN ─── VOUT ──┬── C14(10uF) ── VCC_5V
                       │   IL1117-5.0     │
                      GND                 GND
```

**AZ1117H-3.3TRG1 (5V → 3.3V):**
```
VCC_5V ─── C15(10uF) ─┬── VIN ─── VOUT ──┬── C16(10uF) ─┬── VCC_3V3
                       │   AZ1117H-3.3    │              │
                      GND                GND        C17(0.1uF)
                                                      │
                                                     GND
```

### 3.7 Net Label 규칙

| Net Name | 전압 | 용도 |
|----------|------|------|
| `VCC_12V` | 12V | 모터 전원 (VM), XL4005 입력 |
| `VCC_5V` | 5V | IL1117 출력, A3906 VCC, XL4005 출력 |
| `VCC_3V3` | 3.3V | MCU, IMU, 통신 IC 전원 |
| `AGND` | 0V | 아날로그 GND (VDDA 귀환) |
| `GND` | 0V | 디지털/전원 GND |
| `VDDA` | 3.3V | MCU 아날로그 전원 (Ferrite Bead 분리) |
| `VREF+` | 3.3V | MCU ADC 기준 전압 |

### 3.8 Power Port 심볼 설정

| 전원 | 스타일 | 네트 |
|------|--------|------|
| VCC | Bar (Horizontal bar) | VCC_12V / VCC_5V / VCC_3V3 |
| GND | Power Ground (삼각형 3선) | GND |
| AGND | Signal Ground (삼각형 1선) | AGND |
| VCC | Arrow (화살표) | VDDA, VREF+ |

`P-O` → `Tab` → 스타일 선택 후 배치. 각 전원 Port는 해당 Net을 지정해야 함.

---

## Step 4: MCU STM32F746 주변회로 (1h 30min)

### 4.1 STM32F746ZGT6 배치

1. `P-P` → Library 선택 → `STM32F746ZGT6` → 클릭 배치
2. Properties 패널: Designator = `U1`, Comment = `STM32F746ZGT6`
3. 심볼을 전원부 우측에 배치 (A3 시트 중앙)

### 4.2 MCU 전원 핀 그룹

**디지털 전원 (VDD1~VDD11, VSS):**

| 핀 그룹 | 핀 번호 | 연결 | 캐패시터 | 위치 요구사항 |
|---------|---------|------|---------|-------------|
| VDD1 | 19 | VCC_3V3 | 100nF | 핀 2mm 이내 |
| VDD2 | 31 | VCC_3V3 | 100nF | |
| VDD3 | 40 | VCC_3V3 | 100nF | |
| VDD4 | 54 | VCC_3V3 | 100nF | |
| VDD5 | 66 | VCC_3V3 | 100nF | |
| VDD6 | 73 | VCC_3V3 | 100nF | |
| VDD7 | 82 | VCC_3V3 | 100nF | |
| VDD8 | 91 | VCC_3V3 | 100nF | |
| VDD9 | 99 | VCC_3V3 | 100nF | |
| VDD10 | 106 | VCC_3V3 | 100nF | |
| VDD11 | 112 | VCC_3V3 | 100nF | |
| VDD12~15 (VDDA) | 11, 28, 48, 52 | VDDA | 10uF + 100nF | Analog domain |
| VSS | 20, 32, 41, 53, 65, 72, 81, 90, 100, 105, 111 | GND | - | |
| VSSA | 12, 29, 47, 51 | AGND | - | Analog domain |

**VCAP 핀 (내부 레귤레이터 출력):**
```
VCAP1 (핀 22) ─── C18(2.2uF) ─── GND
VCAP2 (핀 67) ─── C19(2.2uF) ─── GND
```

> ⚠️ VCAP 핀은 반드시 2.2µF 세라믹 커패시터를 GND에 연결해야 MCU가 정상 동작합니다.

**VREF+ (핀 10):**
```
VREF+ ──┬── C20(100nF) ─── AGND
        │
        └── Ferrite Bead(FB1) ── VCC_3V3
```

### 4.3 클럭 회로

**Y1: 25MHz 메인 클럭 (HSE)**

```
                    ┌───── 25MHz ─────┐
                    │     Y1(SX-32)   │
                    │                  │
  PE0(OSC_IN) ──────┤1                3├────── PE1(OSC_OUT)
                    │                  │
                    C21(22pF)    C22(22pF)
                        │            │
                       GND          GND
```

**Y2: 32.768kHz RTC 클럭 (LSE)**

```
                     ┌──32.768kHz──┐
                     │ Y2(CM315)   │
                     │             │
  PC14(OSC32_IN) ────┤1           2├─── PC15(OSC32_OUT)
                     │             │
                     C23(12.5pF)  C24(12.5pF)
                        │            │
                       GND          GND
```

**부품 선택:**

| 크리스탈 | 주파수 | Load Cap | 패키지 | 제조사 |
|----------|--------|----------|--------|--------|
| Y1 | 25MHz | 18pF (external 22pF) | SX-32 | NDK |
| Y2 | 32.768kHz | 6pF (external 12.5pF) | CM315 | Citizen |

Load Capacitance 계산:
- C_load = (C21 × C22) / (C21 + C22) + C_stray ≈ 22pF || 22pF + 5pF ≈ 16pF (25MHz에 적합)
- RTC: C23 = C24 = 12.5pF, C_load ≈ 12.5pF || 12.5pF + 5pF ≈ 11.25pF

### 4.4 리셋 회로 (NRST)

```
                    VCC_3V3
                      │
                    R11(10k)
                      │
    100nF ──┬── SW1 ──┤
            │   │     │
           GND ─┤    NRST(핀 7)
                │
                │
               GND
```

- R11: 10kΩ pull-up to VCC_3V3 (외부 리셋 Watchdog 고려)
- SW1: Tactile switch → NRST to GND
- C25: 100nF debounce capacitor (노이즈 필터링)

### 4.5 BOOT0 회로

```
                    PB2(BOOT0, 핀 50)
                      │
                      ├── R12(10k) ── GND (기본: Flash 부트)
                      │
                      └── Jumper ── VCC_3V3 (System Loader)
```

- 기본: 10kΩ pull-down → Flash 메모리 부트
- Jumper 연결 시: System Loader (UART/USB DFU)

### 4.6 SWD 디버그 인터페이스

SWD 5핀 헤더 (SW1 또는 Tag-Connect):

```
  Pin1: VCC_3V3 ────┬── R13(10k) ─── SWDIO(PA13, 핀 37)
  Pin2: SWCLK ────── R14(10k) ─── GND (pull-down)
  Pin3: GND
  Pin4: SWDIO
  Pin5: NRST
```

| 핀 | MCU 핀 | 기능 | 연결 |
|----|--------|------|------|
| SWDIO | PA13 (핀 37) | 데이터 I/O | 10kΩ pull-up to 3.3V |
| SWCLK | PA14 (핀 39) | 클럭 | 10kΩ pull-down to GND |
| NRST | NRST (핀 7) | 리셋 | 10kΩ pull-up (공유) |

### 4.7 Ferrite Bead 분리 (VDDA)

아날로그 전원(VDDA)은 디지털 노이즈로부터 분리:

```
VCC_3V3 ──┬── FB1(120Ω @ 100MHz) ──┬── VDDA
          │                         │
     Bulk cap                C26(10uF) ── AGND
     (생략 가능)              C27(0.1uF) ── AGND
```

- FB1: ferrite bead (예: BLM18AG121SN1, 120Ω @ 100MHz)
- VDDA와 VSSA는 VDD/VSS와 별도로 AGND로 귀환

### 4.8 바이패스 커패시터 요약

| 캡 타입 | 위치 | 값 | 개수 | 비고 |
|---------|------|-----|------|------|
| Bulk | Near VDD group | 10µF | 2~3 | 0603 |
| High-freq | 각 VDD pin | 100nF | 11 | 0402, 2mm 이내 배치 |
| Analog bulk | VDDA | 10µF | 1 | 0603 |
| Analog HF | VDDA | 100nF | 1 | 0402 |
| VCAP | VCAP1/VCAP2 | 2.2µF | 2 | 0603, X5R or X7R |

---

## Step 5: 모터 드라이버 + 통신 인터페이스 (1h)

### 5.1 A3906 모터 드라이버 x2

**모터 1 (U2, A3906):**

```
MCU_GPIO ─────────► IN1(PB0)      OUT1 ──┬── J2(Motor1)
MCU_GPIO ─────────► IN2(PB1)       │      │
                                       │      │
MCU_PWM ──────────► PWM(PA0)     OUT2 ──┘      │
                                                  │
MCU_GPIO ──────────► SLEEP(PC0)                ┌──┘
                                       │      │
VREF ── R15(0.1Ω) ── GND              GND    Motor
                             │
VCC_5V ── C28(10uF) ─┬── VCC(6)
                      │    │
                     GND  VM(7) ──┬── VCC_12V
                                  │
                              C29(10uF/25V) ── GND
```

**모터 2 (U3, A3906):**
- IN1(PB2), IN2(PB3), PWM(PA1), SLEEP(PC1)
- 나머지 구성은 U2와 동일

**A3906 진리표:**

| IN1 | IN2 | PWM | SLEEP | OUT1 | OUT2 | 모터 상태 |
|-----|-----|-----|-------|------|------|-----------|
| 1 | 0 | 1 | 1 | H | L | 정회전 |
| 0 | 1 | 1 | 1 | L | H | 역회전 |
| 1 | 1 | 1 | 1 | L | L | 브레이크 |
| 0 | 0 | 1 | 1 | Hi-Z | Hi-Z | 코스트 |
| X | X | X | 0 | Hi-Z | Hi-Z | 슬립 |

### 5.2 CAN 버스 인터페이스 (TJF1051T/3)

```
                   TJF1051T/3 (U4)
                 ┌─────────────┐
  VCC_3V3 ──────►│VCC         │
                 │             │
  PD1(FDCAN1_TX)─►│TXD    CANH ├───┬── J3(CAN)
                 │             │   │
  PD0(FDCAN1_RX)◄─┤RXD    CANL ├───┤
                 │             │   │
  PC2 ──────────►│STBY         │   R16(120Ω) ── CANH─CANL
                 │             │   │
  GND ───────────┤GND          │  GND
                 └─────────────┘
```

**CAN 종단 저항:**
- R16: 120Ω (1% precision) — CANH-CANL 사이에 배치
- J3 커넥터 (20010WS-04): Pin1=CANH, Pin2=CANL, Pin3=GND (or VCC_12V)

| 핀 | MCU 연결 | 기능 |
|----|----------|------|
| TXD | PD1 (핀 25) | FDCAN1_TX |
| RXD | PD0 (핀 24) | FDCAN1_RX |
| STBY | PC2 (GPIO) | L=Normal, H=Standby |

### 5.3 RS-485 인터페이스 (MAX3443ECSA+)

```
                     MAX3443ECSA+ (U5)
                  ┌──────────────────┐
  VCC_3V3 ───────►│VCC              │
                  │                  │
  PB11 ──────────►│RO               │
  PB10 ◄──────────┤DI               │
  PB12 ──────────►│RE               │
  PB13 ──────────►│DE               │
                  │                  │
  R17(120Ω) ──┬──┤A ──┬── J4(485)  │
              │  │    │   (B4B-EH-A)│
              │  │B ──┤             │
              │  │    │   Pin1: A(+)│
              └──┤    │   Pin2: B(-)│
                 │    │   Pin3: 12V │
                 │    │   Pin4: GND │
  GND ──────────►│GND               │
                 └──────────────────┘
```

**점퍼 선택 가능 종단:**
- R17: 120Ω (옵션, 점퍼로 연결/해제)

### 5.4 IMU ICM-20648 (QFN-24)

```
                    ICM-20648 (U6)
                  ┌──────────────────┐
  VCC_3V3 ────────►VDD              │
                  │                  │
  VCC_3V3 ────────►VIO              │
                  │                  │
  PB9(I2C1_SDA)◄──┤SDA              │
  PB8(I2C1_SCL)──►│SCL              │
                  │                  │
  PE0 ───────────►│INT(핀 12)       │
                  │                  │
  ┌── AD0(핀 24) ─┬── GND → 0x68   │
  │               │                 │
  GND             └── VCC → 0x69   │
                  │                 │
  C30(100nF) ──┬──┤VDD ─┬── C31(0.1uF)
               │  │     │          │
              GND │    GND        GND
                  │
  C32(100nF) ──┬──┤VIO
               │
              GND
```

**I2C Pull-up 저항:**
```
VCC_3V3
   │
  R18(4.7k) ──── SDA(PB9)
  R19(4.7k) ──── SCL(PB8)
```

**IMU 레지스터 맵 (참고):**

| Register | Address | 기능 |
|----------|---------|------|
| WHO_AM_I | 0x00 | 디바이스 ID (0xEC) |
| PWR_MGMT_1 | 0x06 | Sleep 모드 해제 |
| ACCEL_CONFIG | 0x09 | 가속도 풀스케일 (±2/4/8/16g) |
| GYRO_CONFIG | 0x0A | 자이로 풀스케일 (±250/500/1000/2000dps) |
| CONFIG | 0x0B | Digital Low-Pass Filter |

### 5.5 USB OTG 인터페이스

**전원 스위치 — STMPS2141STR (U7):**

```
                   STMPS2141STR
                 ┌──────────────┐
  USB_VBUS ─────►│VIN          │
                 │              │
  PG0 ─────────►│EN        FLG ├──► PG1 (Fault flag)
                 │              │
  C33(1uF) ──┬──┤OUT ──┬── J1 │
             │  │      │   │  │
            GND │    C34(1uF) │
                │      │      │
               GND   GND    │
                             │
                    ZX62D-B-5P8 (Micro-B, J1)
                    ┌─────────────────┐
                    │ Pin1: VBUS      │
                    │ Pin2: D+ (PA11) │
                    │ Pin3: D- (PA12) │
                    │ Pin4: ID (PA10) │
                    │ Pin5: GND       │
                    └─────────────────┘
```

**EMI/ESD 필터 — EMIF02-USB03F2 (U8):**

```
                        EMIF02-USB03F2
                  ┌──────────────────────┐
  D+(PA11) ──────►│IN1              OUT1 ├──► J1_D+
                  │                      │
  D-(PA12) ──────►│IN2              OUT2 ├──► J1_D-
                  │                      │
  VBUS ──────────►│IN_VBUS        OUT_VBUS├──► J1_VBUS
                  │                      │
  GND ────────────┤GND                   │
                  └──────────────────────┘
```

- EMIF02-USB03F2는 **공통 모드 필터 + ESD 보호** 일체형 부품
- USB Differential Pair (90Ω)은 PCB 라우팅에서 관리

---

## Step 6: 커넥터 + 종합 검토 (1h)

### 6.1 DYNAMIXEL 커넥터

**TTL DYNAMIXEL (JST B3B-EH-A) — x3개:**

| 커넥터 | Designator | 신호 | 대상 DYNAMIXEL |
|--------|--------|------|----------------|
| J6 | UART1 | TX(PB6), RX(PB7), GND | DXL_1 |
| J8 | UART2 | TX(PD5), RX(PD6), GND | DXL_2 |
| J25 | UART6 | TX(PC6), RX(PC7), GND | DXL_3 |

```
J6 (B3B-EH-A):
  Pin1(좌): TX ──┬── R20(100) ── PB6(UART1_TX)
  Pin2(중): RX ──┬── R21(100) ── PB7(UART1_RX)
  Pin3(우): GND
```

**RS-485 DYNAMIXEL (JST B4B-EH-A) — x3개:**

| 커넥터 | Designator | 신호 |
|--------|--------|------|
| J15 | UART4_485 | 485+, 485-, VCC_12V, GND |
| J16 | UART5_485 | 485+, 485-, VCC_12V, GND |
| J17 | UART7_485 | 485+, 485-, VCC_12V, GND |

```
J15 (B4B-EH-A):
  Pin1: 485+
  Pin2: 485-
  Pin3: VCC_12V
  Pin4: GND
```

**UART/CAN 혼합 (20010WS-04) — x3개:**

| 커넥터 | Designator | 신호 | 사용 |
|--------|--------|------|------|
| J18 | CAN1 | CANH, CANL, VCC_12V, GND | CAN DYNAMIXEL |
| J19 | UART3 | TX(PB10), RX(PB11), VCC_12V, GND | 외부 UART |
| J20 | UART8 | TX(PE0), RX(PE1), VCC_12V, GND | 외부 UART |

### 6.2 ERC (Electrical Rule Check)

1. **Error Reporting 설정:** `Project → Project Options → Error Reporting`
   - Duplicate Net Names → **Fatal Error**
   - Unconnected Pin → **Warning**
   - No ERC Marker → **Warning**
   - Off-grid Object → **Warning**

2. **ERC 실행:** `Tools → Electrical Rule Check`
   - Scope: Entire Sheet
   - Options: 모든 체크박스 활성화
   - `Report` 버튼 실행

3. **Messages 패널**에서 각 오류 확인 및 수정:
   - Unconnected pins → 연결 또는 No ERC 마커 (`P-I`) 추가
   - Floating net labels → 와이어와 연결 확인
   - Duplicate designators → 재할당

### 6.3 Annotate (부품 번호 자동 할당)

| 단계 | 조작 |
|------|------|
| Annotate 실행 | `Tools → Annotate Schematics` |
| Order of Processing | **Across then Down** (좌→우, 상→하) |
| Matching Options | Match By Parameters |
| Update Changes List | 변경 사항 미리보기 |
| Accept Changes | ECO 실행 → Designators 재할당 |

**Annotate 결과 예시:**
```
U1 → STM32F746ZGT6
U2 → A3906 (Motor1)
U3 → A3906 (Motor2)
U4 → TJF1051T/3
U5 → MAX3443ECSA+
U6 → ICM-20648
U7 → STMPS2141STR
R1~R30 → Resistors
C1~C50 → Capacitors
J1~J20 → Connectors
```

### 6.4 Compile Project

| 단계 | 조작 |
|------|------|
| Compile | `Project → Compile PCB Project OpenCR_Altium.PrjPcb` |
| 오류 확인 | Messages 패널에서 Error/Warning 검토 |
| Netlist 생성 | Project Outputs 폴더에 .net 파일 자동 생성 |

**Compile 오류 해결 체크리스트:**
- [ ] 모든 부품이 배치되었는가?
- [ ] 중복 Net Name이 없는가?
- [ ] Floating Input 핀이 없는가?
- [ ] Power Port의 Net이 올바른가? (VCC_3V3 vs VCC_5V 구분)
- [ ] Bus 연결이 올바른가?
- [ ] 계층 구조가 있다면 Port-Sheet Symbol 연결이 일치하는가?

### 6.5 ERC/Compile 통과 결과

```
[Info] Compiler: compiling OpenCR_REVH.SchDoc...
[Info] Compiler: 0 Errors, 2 Warnings
[Warning] Unconnected Pin: U1-22(VCAP1) — check
[Warning] Unconnected Pin: U1-67(VCAP2) — check
```

→ VCAP 핀은 회로도 레벨에서는 캐시퍼터 연결로 경고 해소

### 6.6 Day 1 완료 체크리스트

- [ ] Altium Designer 설치 및 Preferences 설정 완료
- [ ] PCB Project 생성 → `OpenCR_Altium.PrjPcb`
- [ ] Schematic Sheet 생성 → `OpenCR_REVH.SchDoc` (A3)
- [ ] STM32F746ZGT6 심볼 생성 완료 (144핀)
- [ ] LM5175PWPR, A3906, TJF1051, MAX3443, ICM-20648 심볼 생성
- [ ] 커넥터 심볼 (B3B, B4B, 20010WS, Micro-B) 생성
- [ ] 전원부 완성: DC 입력 → LM5175 → XL4005 → LDO
- [ ] MCU 전원/클럭/리셋/디버그 연결 완료
- [ ] 모터 드라이버 회로 완성
- [ ] CAN/RS-485 인터페이스 완성
- [ ] IMU I2C 연결 완성
- [ ] USB OTG 회로 완성
- [ ] 모든 DYNAMIXEL 커넥터 연결 완료
- [ ] ERC 통과 (0 Error)
- [ ] Annotate 완료
- [ ] Project Compile 성공

---

**→ Day 2에서 PCB 레이아웃 설계를 진행합니다.**

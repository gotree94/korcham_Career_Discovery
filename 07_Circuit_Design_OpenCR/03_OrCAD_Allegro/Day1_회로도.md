# Day 1: OrCAD Capture 회로도 설계 (7h)

## Step 1: OrCAD Capture 시작 및 프로젝트 생성 (40min)

### 1.1 OrCAD Capture 실행

- Windows **Start → Cadence → OrCAD Capture** (또는 Capture CIS)
- 최초 실행 시 라이선스 선택 창 → **Allegro PCB Designer** 또는 **OrCAD PCB Designer** 선택
- 실행 후 빈 Capture 창 확인 (메뉴바, 툴바, 작업영역)

### 1.2 새 프로젝트 생성

```
File → New → Project
```

| 필드 | 입력값 |
|------|--------|
| Name | `OpenCR_OrCAD` |
| Location | `C:\Users\...\OpenCR_OrCAD\` (적절한 위치) |
| Project Type | **PC Board Wizard** 선택 |
| Create Blank Project | 체크 (템플릿 없이 시작) |

> **참고:** PC Board Wizard를 선택하면 Allegro 연동 설정이 자동 구성됨. 이후 Allegro Netlist 생성 시 필요.

### 1.3 Page Size 설정

- 빈 Schematic Sheet에서 우클릭 → **Schematic Page Properties**
- 또는 메뉴: `Options → Schematic Page Properties`
- Page Size: **A3** (297×420mm) — OpenCR 회로도 규모에 적합
  - 또는 **D** (558.8×863.6mm) — 대형 회로도에 사용
- Grid: **Grid Reference** → Horizontal/Vertical 모두 5 divisions

### 1.4 인터페이스 구성

| 영역 | 설명 |
|------|------|
| **Project Manager** (좌측) | 프로젝트 트리: .DSN 파일, Page, Library, Output |
| **Schematic Page Editor** (중앙) | 회로도 작성 영역 |
| **Tool Palette** (우측) | 배치/배선/심볼 도구 모음 |
| **Command Window** (하단) | 명령어 입력 및 알림 표시 |

### 1.5 기본 단축키 (필수 암기)

| 단축키 | 명령 | 설명 |
|--------|------|------|
| **W** | Wire | 배선 연결 |
| **N** | Net Alias | 네트워크 이름 부여 |
| **P** | Place Part | 부품 배치 |
| **I** | Zoom In | 확대 (드래그) |
| **O** | Zoom Out | 축소 |
| **R** | Rotate | 부품 회전 (90°) |
| **E** | End Mode | 현재 동작 종료 |
| **Ctrl+A** | Select All | 전체 선택 |
| **Delete** | Delete | 선택 삭제 |
| **Ctrl+C/V** | Copy/Paste | 복사/붙여넣기 |
| **F5** | Redraw | 화면 갱신 |
| **H** | Pan | 화면 이동 |
| **F** | Fit All | 모든 객체 화면에 맞춤 |

---

## Step 2: 부품 라이브러리 및 심볼 생성 (1h 20min)

### 2.1 Capture CIS 라이브러리 이해

- OrCAD Capture 부품은 **.olb** 파일 (Library)에 저장됨
- 각 .olb 파일 안에 여러 **Part** (부품 심볼)가 포함됨
- 심볼은 **Pin**으로 구성되며, 각 Pin에 **PCB Footprint** 속성 연결 가능
- 부품 배치 시 `.olb` 파일을 프로젝트에 **Add Library**로 등록

### 2.2 기존 라이브러리 추가

```
Place → Part (단축키 P) → Add Library (버튼)
```

기본 제공 라이브러리 예:
- `C:\Cadence\SPB_16.6\tools\capture\library\` (기본 라이브러리 경로)

주요 기본 라이브러리:
| 라이브러리 | 포함 부품 |
|-----------|----------|
| `discrete.olb` | R, C, L 기본 수동소자 |
| `connector.olb` | 각종 커넥터 |
| `source.olb` | VCC, GND, 전원 심볼 |
| `cap.olb` | Capacitor |
| `res.olb` | Resistor |
| `transistor.olb` | Transistor, FET |

> **주의:** OpenCR 부품은 대부분 기본 라이브러리에 없으므로 **직접 생성**해야 함.

### 2.3 직접 심볼 생성 — 기본 절차

#### 2.3.1 새 라이브러리 파일 생성

```
File → New → Library
```

- Project Manager의 **Library** 폴더에 `library1.olb` 생성됨
- 우클릭 → **Save As** → `OpenCR_Parts.olb` (저장)

#### 2.3.2 새 Part 생성

```
OpenCR_Parts.olb 우클릭 → New Part
```

| 필드 | 설명 |
|------|------|
| **Name** | 부품명 (예: STM32F746ZGT6) |
| **PCB Footprint** | PCB 풋프린트명 (예: LQFP-144) |
| **Part Reference Prefix** | Refdes 접두사 (예: U) |
| **Part per Pkg** | 패키지당 파트 수 (1 = 단일) |
| **Homogeneous / Heterogeneous** | 다중 파트 시 핀 구성 방식 |

#### 2.3.3 핀 배치 규칙

- **왼쪽:** 전원/제어 핀 (VDD, VSS, NRST, BOOT)
- **위쪽:** 데이터 입력 (OSC_IN, OSC_OUT, PLL)
- **오른쪽:** GPIO, 통신 핀 (PA0-PI15, PBx)
- **아래쪽:** ADC, 아날로그 입력
- **핀 간격:** Grid (기본 0.1 inch)에 맞춰 배치

#### 2.3.4 핀 속성 설정

핀 배치 후 더블클릭 → **Pin Properties**:

| 속성 | 설명 | 예시 |
|------|------|------|
| **Name** | 핀 이름 | VDD, PA0, SDA |
| **Number** | 핀 번호 | 1, 2, 144 |
| **Shape** | 핀 모양 | Line, Clock, Dot (반전) |
| **Type** | 핀 타입 | Input, Output, Bidirectional, Power, GND |

### 2.4 주요 부품 심볼 생성 실습

#### 2.4.1 STM32F746ZGT6 (LQFP-144)

- **Part Name:** STM32F746ZGT6
- **PCB Footprint:** LQFP-144
- **Pin count:** 144핀 (단일 Part, Homogeneous)
- **핀 그룹화** (총 144핀을 기능별 분할):

| 그룹 | 핀 번호 (예시) | 설명 |
|------|---------------|------|
| Power | VDD_1~VDD_11, VSS_1~VSS_11, VDDA, VSSA, VREF+ | 3.3V 전원 |
| Clock | OSC_IN(14), OSC_OUT(15), PC14(OSC32_IN), PC15(OSC32_OUT) | 크리스탈 |
| Control | NRST(20), BOOT0(142) | 리셋, 부트 |
| SWD | PA13(SWDIO), PA14(SWCLK) | 디버그 |
| UART | PB6(UART1_TX), PB7(UART1_RX) | 시리얼 |
| I2C | PB8(SCL), PB9(SDA) | IMU |
| GPIO | PA0~PA15, PB0~PB15, PC0~PC15, PD0~PD15, ... | 범용 |
| USB | PA11(USB_DM), PA12(USB_DP) | USB OTG |

> **팁:** 100핀 이상은 **Array 배치** 사용:
> 핀 속성 창에서 **Array** 탭 → Starting Pin #, Increment, Count, Pin Spacing 설정 → 한 번에 여러 핀 생성

#### 2.4.2 LM5175PWPR (HTSSOP-28)

| 핀 # | 이름 | Type | 설명 |
|------|------|------|------|
| 1 | VIN | Power | 입력 전압 |
| 2 | EN | Input | Enable (divider) |
| 3 | FB | Input | Feedback (출력 전압 설정) |
| 4 | COMP | Output | Compensation |
| 5~10 | SW | Output | Switching Node |
| 11~15 | PGND | Power | 전원 GND |
| 16~28 | 기타 | — | CT, RT, SS, etc. |

#### 2.4.3 A3906SESTR-T (QFN-20)

- 2채널 모터 드라이버
- 핀: IN1, IN2, PWM, EN per channel + OUT1, OUT2

#### 2.4.4 JST B3B-EH-A (3핀 커넥터)

- **PCB Footprint:** B3B-EH-A
- Pin 배열: 1-TX, 2-RX, 3-GND
- 간단한 Header 심볼로 생성 (Pin Number 1~3)

### 2.5 Package Properties 설정

부품 심볼에서 더블클릭 → **User Properties**:

| 속성 | 값 |
|------|-----|
| **PCB Footprint** | LQFP-144 (Allegro 풋프린트명과 일치) |
| **Value** | STM32F746ZGT6 |
| **Part Number** | 부품 주문 번호 |
| **Manufacturer** | STMicroelectronics |

> **중요:** PCB Footprint 필드 값은 **Allegro PCB Editor의 풋프린트명과 정확히 일치**해야 함. 대소문자 구분.

---

## Step 3: 전원부 회로도 작성 (1h 30min)

### 3.1 전원부 개요

OpenCR 전원 구성:
```
DC Input (12V/5A) ─┬─ Fuse 10A ── TVS ── LM5175PWPR (Buck-Boost) ── 12V ── XL4005 (Buck) ── 5V
                   │                                                    │
                   └── IL1117-5.0 ── 5V (USB)                        AZ1117H-3.3 ── 3.3V
```

### 3.2 부품 배치 (Place Part)

1. **단축키 P** → Place Part 창 열기
2. Add Library → `OpenCR_Parts.olb` 등록
3. 부품 선택 후 Schematic Page에 클릭 배치

| 부품 | Refdes | Library |
|------|--------|---------|
| DC Jack (2 pin header) | J1 | connector.olb / 직접 생성 |
| Fuse 0453010 10A | F1 | 직접 생성 |
| TVS Diode | D1 | 직접 생성 |
| LM5175PWPR | U1 | 직접 생성 |
| XL4005 | U2 | 직접 생성 |
| AZ1117H-3.3TRG1 | U3 | 직접 생성 |
| IL1117-5.0ET | U4 | 직접 생성 |
| Inductor XAL6060-472MEB | L1, L2 | 직접 생성 |

### 3.3 배선 (Wire) — 단축키 W

- **W** 키 → Wire 모드 시작
- 부품 핀에서 클릭 → 드래그 → 연결할 핀에서 클릭
- 종료: **E** 키 (End Mode) 또는 우클릭 → End Wire
- Wire 위에 **Net Alias** 부여 (단축키 N)

### 3.4 Net Alias (단축키 N)

- **N** 키 → Net Alias 창 열기
- 주요 네트워크명:

| Net Alias | 설명 |
|-----------|------|
| VCC_12V | LM5175 출력 (12V) |
| VCC_5V | XL4005 / IL1117 출력 (5V) |
| VCC_3V3 | AZ1117 출력 (3.3V) |
| VIN_DC | DC 입력 |
| GND | 디지털 GND |
| AGND | 아날로그 GND (IMU, ADC) |

### 3.5 LM5175PWPR 회로도

```
[VIN_DC] ── F1 ── TVS ──┬── L1 (4.7uH) ──┬── [VCC_12V]
                         │                │
                    C1 (10uF)        C2 (22uF)
                         │                │
                        GND              GND
```

LM5175 주요 연결:
- **VIN pin** → VIN_DC (입력)
- **EN pin** → voltage divider (R1, R2로 설정)
- **FB pin** → feedback divider (R3, R4로 12V 출력 설정)
- **COMP pin** → R5 + C3 series (compensation network)
- **SW pin** → L1 (4.7uH inductor)
- **PGND** → GND (thermal via 다수)

**Feedback Resistor 계산:**
```
VOUT = VFB × (1 + R3/R4)
VFB = 1.5V (LM5175 reference)
VOUT = 12V → R3/R4 = 7 → R3 = 70k, R4 = 10k (예시)
```

### 3.6 XL4005 회로도

```
[VCC_12V] ──┬── L2 ──┬── [VCC_5V]
            │        │
        C4(10uF)  C5(22uF) + C6(100nF)
            │        │
           GND      GND
```

XL4005 주요 연결:
- **VIN** → VCC_12V
- **EN** → VCC_12V (pull-up)
- **FB** → feedback divider → 5V 설정
- **SW** → L2 (inductor)
- **Output** → 22uF + 100nF ceramic caps

### 3.7 LDO 회로도

**AZ1117H-3.3 (3.3V LDO):**

```
[VCC_5V] ──┬── IN ── OUT ──┬── [VCC_3V3]
            │               │
        C7(10uF)       C8(10uF) + C9(100nF)
            │               │
           GND             GND
```

**IL1117-5.0 (5V LDO):**

```
[VIN_DC] ──┬── IN ── OUT ──┬── [VCC_5V_USB]
           │               │
       C10(10uF)      C11(10uF) + C12(100nF)
           │               │
          GND             GND
```

### 3.8 Power Symbol 배치

```
Place → Power (또는 단축키 F7)
```

- VCC (VCC_ARROW): 표준 VCC 심볼
- GND (EARTH / GND): 접지 심볼
- Power symbol은 **net name과 연결**되어야 함 (더블클릭 → Name 변경)

### 3.9 Off-Page Connector

다중 페이지 설계 시:

```
Place → Off-Page Connector
```

- Page 간 동일한 Net 연결에 사용
- 왼쪽/오른쪽 방향 선택 가능

---

## Step 4: MCU STM32F746 주변회로 (1h 30min)

### 4.1 STM32F746ZGT6 배치

- **단축키 P** → OpenCR_Parts.olb → STM32F746ZGT6 선택
- Schematic Page 중앙에 배치 (이후 배선 공간 확보)

### 4.2 전원 핀 연결

**VDD (3.3V) 핀 — 11개:**

```
각 VDD 핀 → VCC_3V3 (Power symbol)
각 VDD 핀 근처 → 100nF MLCC (C13~C23) to GND
```

> **Decoupling capacitor 배치:** 각 VDD 핀 바로 옆에 100nF 캡을 배치 (최대한 가깝게)

**VDDA (Analog 3.3V):**

```
VCC_3V3 ── Ferrite Bead FB1 ──┬── VDDA
                              │
                          C24(10uF)
                              │
                          C25(100nF)
                              │
                             GND
```

**VREF+:**

- VDDA에 직결 (또는 외부 precision reference IC 연결)

**VSSA / VSS:**

```
VSSA ── GND
VSS 핀 (각각) ── GND
```

**VCAP1, VCAP2 — 내부 LDO 출력:**

```
VCAP1(핀 17) ── C26(2.2uF) ── GND
VCAP2(핀 18) ── C27(2.2uF) ── GND
```

> **주의:** VCAP 핀은 반드시 2.2uF MLCC로 bypass해야 MCU가 정상 동작함

### 4.3 Clock 회로

**HSE (25MHz Main Clock):**

```
STM32F746
OSC_IN(14) ──┬── Y1 (25MHz, SX-32) ──┬── OSC_OUT(15)
             │                        │
         C28(22pF)               C29(22pF)
             │                        │
            GND                      GND
```

- Y1 옆에 GND guard ring 배치 (Schematic상 표시)
- GND via 양옆 배치

**LSE (32.768kHz RTC Clock):**

```
PC14(OSC32_IN, 6) ──┬── Y2 (32.768kHz, CM315) ──┬── PC15(OSC32_OUT, 7)
                     │                           │
                 C30(12.5pF)                C31(12.5pF)
                     │                           │
                    GND                         GND
```

### 4.4 Reset 회로

```
VCC_3V3 ── R39(10k) ──┬── NRST(20, STM32F746)
                       │
                    SW1 (Reset Button)
                       │
                    C32(100nF)
                       │
                      GND
```

- R39: Pull-up (10k to 3.3V) — NRST는 Active Low
- SW1: Tactile switch (Reset)
- C32: Debouncing capacitor (100nF)

### 4.5 BOOT 회로

```
VCC_3V3 ──┬── SW2 (Boot Button) ──┬── BOOT0(142, STM32F746)
          │                        │
          │                    R40(10k)
          │                        │
          │                       GND
     (Jump to boot mode)
```

- BOOT0 = High → System Memory (ISP)
- BOOT0 = Low → Flash (Normal)

### 4.6 SWD (Serial Wire Debug) — 5핀 헤더

| 핀 | 신호 | 연결 |
|----|------|------|
| 1 | VCC_3V3 | 타겟 전원 |
| 2 | SWDIO | PA13 |
| 3 | SWCLK | PA14 |
| 4 | NRST | Reset (옵션) |
| 5 | GND | 접지 |

```
Header 5×1 (J2):
Pin1: VCC_3V3
Pin2: PA13(SWDIO)
Pin3: PA14(SWCLK)
Pin4: NRST
Pin5: GND
```

---

## Step 5: 모터 드라이버 + 통신 인터페이스 (1h)

### 5.1 UART1 — DYNAMIXEL TTL (3채널)

**STM32F746 핀맵:**

| 신호 | MCU 핀 | Alternate Function |
|------|--------|-------------------|
| UART1_TX | PB6 | AF7 (USART1) |
| UART1_RX | PB7 | AF7 (USART1) |

**3채널 DYNAMIXEL TTL:**

```
PB6(TX) ──┬── J3(B3B-EH-A, Pin1-TX) ── DYNAMIXEL #1
          ├── J4(B3B-EH-A, Pin1-TX) ── DYNAMIXEL #2
          └── J5(B3B-EH-A, Pin1-TX) ── DYNAMIXEL #3

PB7(RX) ──┬── J3(Pin2-RX)
          ├── J4(Pin2-RX)
          └── J5(Pin2-RX)

GND ──────┬── J3(Pin3-GND)
          ├── J4(Pin3-GND)
          └── J5(Pin3-GND)
```

**TVS Protection (SM712 per channel):**

```
TX ── SM712 ── GND
RX ── SM712 ── GND
```

### 5.2 RS-485 — DYNAMIXEL 3핀 (×3)

**MAX3443ECSA+ (SOP-8):**

| 핀 | 신호 | MCU 연결 |
|----|------|---------|
| 1 | RO | PB11 (USART3_RX) |
| 2 | RE | PB12 (GPIO) — Active Low |
| 3 | DE | PB13 (GPIO) |
| 4 | DI | PB10 (USART3_TX) |
| 5 | GND | GND |
| 6 | A | RS-485 A (B4B-EH-A Pin2) |
| 7 | B | RS-485 B (B4B-EH-A Pin3) |
| 8 | VCC | VCC_3V3 |

**회로도:**

```
MAX3443ECSA+
  RO(PB11) ── USART3_RX
  DI(PB10) ── USART3_TX
  RE(PB12) ── GPIO (0 = Receive enable)
  DE(PB13) ── GPIO (1 = Drive enable)
  A ──┬── J6(B4B-EH-A, Pin2)
  B ──┬── J6(B4B-EH-A, Pin3)
```

**120Ω Termination:**

```
A ── Rterm(120Ω) ── B
```

- 종단 저항은 커넥터 근처에 배치
- 통신 거리에 따라 선택적으로 장착 (DNP 가능)

### 5.3 CAN 통신 — TJF1051T/3 (SOP-8)

| 핀 | 신호 | MCU 연결 |
|----|------|---------|
| 1 | TXD | PB6 (CAN1_TX, AF9) |
| 2 | GND | GND |
| 3 | VCC | VCC_3V3 |
| 4 | RXD | PB7 (CAN1_RX, AF9) |
| 5 | SPLIT | VIO/2 (옵션) |
| 6 | CANL | CAN Low |
| 7 | CANH | CAN High |
| 8 | STB | GND (Normal mode) |

**회로도:**

```
TJF1051T/3
  TXD(PB6) ─── CAN1_TX
  RXD(PB7) ─── CAN1_RX
  STB(GND) ─── Normal mode
  CANH ─┬─ J7(20010WS-04)
  CANL ─┘
  Rterm(120Ω) ── CANH ── CANL (옵션)
```

### 5.4 A3906 모터 드라이버 (×2)

**A3906SESTR-T (QFN-20) — Channel 1:**

| 핀 | 신호 | MCU 연결 |
|----|------|---------|
| 1 | IN1 | PB0 (GPIO) |
| 2 | IN2 | PB1 (GPIO) |
| 3 | PWM | PA0 (TIM2_CH1) |
| 4 | EN | PC0 (GPIO) — Active Low |
| 5 | OUT1 | Motor Connector J8(+) |
| 6 | OUT2 | Motor Connector J8(-) |
| 7 | VBB | VCC_12V |
| 8 | GND | GND |

**A3906SESTR-T — Channel 2:**

| 핀 | 신호 | MCU 연결 |
|----|------|---------|
| 1 | IN1 | PB2 (GPIO) |
| 2 | IN2 | PB3 (GPIO) |
| 3 | PWM | PA1 (TIM2_CH2) |
| 4 | EN | PC1 (GPIO) — Active Low |
| 5 | OUT1 | Motor Connector J9(+) |
| 6 | OUT2 | Motor Connector J9(-) |
| 7 | VBB | VCC_12V |
| 8 | GND | GND |

**Bypass Capacitor (각 드라이버):**

```
VBB ── C33(10uF) ── GND
VBB ── C34(100nF) ── GND
```

### 5.5 IMU ICM-20648

**ICM-20648 (QFN-24) I2C 연결:**

| 핀 | 신호 | MCU 연결 |
|----|------|---------|
| 1 | VDD | VCC_3V3 |
| 2 | VIO | VCC_3V3 |
| 3 | GND | GND |
| 4 | SDA | PB9 (I2C1_SDA) |
| 5 | SCL | PB8 (I2C1_SCL) |
| 6 | INT | PE0 (GPIO — EXTI) |
| 7 | AD0 | GND (I2C addr LSB = 0) |
| 8 | nCS | VCC_3V3 (SPI 미사용) |

**Bypass:**

```
VDD ── C35(100nF) ── GND
VDD ── C36(4.7uF) ── GND
VIO ── C37(100nF) ── GND
```

> **배치 주의:** IMU는 MCU 가까이 배치 (I2C 라인 최소화). I2C pull-up 저항 (2.2k, R41, R42) SDA/SCL에 추가.

### 5.6 USB OTG

**STMicroelectronics STMPS2141STR (Power Switch):**

| 핀 | 신호 | MCU 연결 |
|----|------|---------|
| 1 | EN | PG0 (GPIO) |
| 2 | IN | VCC_5V |
| 3 | OUT | USB VBUS |
| 4 | FLG | PG1 (GPIO) — Fault flag |
| 5 | GND | GND |

**EMIF02-USB03F2 (EMI Filter + ESD):**

- D+, D- 라인에 직렬 배치
- VBUS, GND 연결

**ZX62D-B-5P8 (Micro-B USB Connector):**

| 핀 | 신호 |
|----|------|
| 1 | VBUS (STMPS2141STR OUT) |
| 2 | D- (EMIF02 → PA11) |
| 3 | D+ (EMIF02 → PA12) |
| 4 | ID (GND for OTG Host) |
| 5 | GND |

**USB Differential Pair:**

```
PA11(USB_DM) ── EMIF02 ── ZX62D-B-5P8 D-
PA12(USB_DP) ── EMIF02 ── ZX62D-B-5P8 D+
```

---

## Step 6: 커넥터 + 종합 검토 (1h)

### 6.1 커넥터 전체 배치 및 네트워크 연결

Schematic Page에서 모든 커넥터를 **Page 가장자리**로 배치:

| 커넥터 | 위치 방향 | 설명 |
|--------|----------|------|
| J1 (DC Input) | 좌측 상단 | 전원 입력 |
| J2 (SWD 5pin) | 좌측 하단 | 디버그 |
| J3~J5 (B3B-EH-A) | 상단 | DYNAMIXEL TTL ×3 |
| J6 (B4B-EH-A) | 상단 | RS-485 |
| J7 (20010WS-04) | 우측 | CAN |
| J8, J9 (Motor) | 우측 하단 | 모터 출력 |
| J10 (Micro-B) | 하단 | USB |

### 6.2 Off-Page Connector (다중 페이지)

회로도가 여러 Page로 분할된 경우:

```
Place → Off-Page Connector
```

- Page 1 ~ Page N 간 네트워크 연결
- 같은 이름의 Off-Page Connector는 자동으로 연결됨

### 6.3 Annotate — Refdes 자동 할당

```
Tools → Annotate
```

| 옵션 | 설정 |
|------|------|
| Scope | Update Entire Design |
| Action | Incremental Reference Update |
| Combined property | Part Reference |
| Reset parts to ? | 체크 안 함 (부분 업데이트) |
| Include non-printed parts | 체크 |

- Annotate 실행 후 Refdes가 **U1, R1, C1, J1...** 순으로 자동 할당
- **Packaging** 탭: Gate/Swap 정리

### 6.4 Design Rules Check (DRC)

```
Tools → Design Rules Check
```

#### Electrical Rules 탭:

| 체크 항목 | 설명 |
|-----------|------|
| Check single node nets | 단일 노드 네트만 검사 (미연결) |
| Check unconnected pins | 연결 안 된 핀 검사 |
| Check no driving source | 드라이버 없는 Net 검사 |
| Check duplicate net names | 중복 Net 이름 검사 |
| Check VCC/GND short | VCC/GND 단락 검사 |

#### Physical Rules 탭:

| 체크 항목 | 설명 |
|-----------|------|
| Check off-page connector | Off-Page 페이지 간 연결 검증 |
| Check hierarchical port | 계층 구조 포트 연결 검증 |

#### DRC 실행:

1. 모든 옵션 체크
2. **Run DRC** 버튼 클릭
3. 결과: Session Log에 출력 (오류/경고)
4. 각 오류 더블클릭 → 해당 위치 자동 이동
5. **모든 오류 수정 후 DRC 재실행** (오류 0까지)

> **일반적인 DRC 오류:**
> - Single Node Net: Net이 연결되지 않음 → Wire 또는 Net Alias 추가
> - Unconnected Pin: 핀이 배선 안 됨 → 핀 연결 또는 No Connect 심볼 (X) 부착
> - Duplicate Net: 같은 Net 이름 중복 → 이름 확인 및 통일

### 6.5 Cross Reference 출력

```
Tools → Cross Reference
```

- 리포트 형식: **HTML** 또는 **Text**
- 리포트 내용: 부품 Refdes, Value, PCB Footprint, Location(X,Y)
- Parts per Page: 페이지별 부품 리스트

### 6.6 Bill of Materials (BOM) 출력

```
Tools → Bill of Materials
```

| 항목 | 설정 |
|------|------|
| Header | Item, Quantity, Reference, Value, PCB Footprint, Manufacturer |
| Combine | 동일 Value/Footprint 부품 통합 |
| Report Format | CSV (Excel 호환) |
| Output File | `OpenCR_OrCAD_BOM.csv` |

**BOM 출력 예시:**

```
Item, Qty, Reference, Value, PCB Footprint, Manufacturer
1, 11, C1,C2,..., VCC 100nF, C0402, Samsung
2, 3, R1,R2,R3, 10k, R0402, Yageo
3, 1, U1, STM32F746ZGT6, LQFP-144, STMicroelectronics
...
```

### 6.7 Schematic PDF 출력

```
File → Export → PDF
```

- **Page Setup:** A3, 1:1 scale
- **PDF Options:** 모든 페이지 포함, Bookmark 생성
- 출력 파일: `OpenCR_OrCAD_Schematic.pdf`

### 6.8 최종 점검 체크리스트

- [ ] 모든 부품 Refdes가 고유한가?
- [ ] 모든 핀이 연결되었는가? (NC 핀은 No Connect 심볼 부착)
- [ ] Power/GND 심볼이 올바른 Net에 연결되었는가?
- [ ] DRC 오류가 0인가?
- [ ] BOM에 모든 부품이 출력되었는가?
- [ ] PCB Footprint 속성이 누락된 부품은 없는가?
- [ ] Off-Page Connector가 올바르게 매칭되는가?
- [ ] 모든 Datasheet 참조 핀맵과 일치하는가?

---

## Day 1 핵심 요약

```
1. OrCAD Capture 프로젝트 생성 (PC Board Wizard)
2. 부품 심볼 생성 (.olb) — STM32F746, LM5175, A3906, 커넥터
3. 전원부 회로 — LM5175(Buck-Boost) → XL4005(Buck) → LDO(3.3V)
4. MCU 주변회로 — Clocks, Reset, Boot, SWD, Decoupling
5. 인터페이스 — UART, RS-485, CAN, Motor Driver, IMU I2C, USB
6. 최종 검증 — Annotate, DRC, BOM, PDF Export
```

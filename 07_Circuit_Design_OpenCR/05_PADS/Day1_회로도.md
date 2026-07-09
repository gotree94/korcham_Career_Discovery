# Day 1 — PADS Logic 회로도 설계 (7h)

> OpenCR REV H의 전원부, MCU, 모터 드라이버, 통신 인터페이스를 PADS Logic으로 회로도 작성

---

## Step 1: PADS 설치 및 프로젝트 생성 (40min)

### 1.1 PEDS 설치

Siemens EDA 공식 사이트 또는 교육 기관 라이선스로 설치:

```
Siemens EDA → PADS Professional → 설치
- PADS Logic, PADS Layout, PADS Router, PADS Library 모두 포함
- License Server 설정 (또는 Node-Locked 라이선스)
```

### 1.2 PADS Logic 실행

```
Start → Siemens EDA → PADS Logic
또는 바탕화면 PADS Logic 아이콘
```

### 1.3 새 프로젝트 생성

```
PADS Logic은 파일 단위 (별도 프로젝트 파일 없음)

1. File → New
2. Design: "OpenCR_PADS"
3. Sheet Size: File → Page Setup → A3 (420×297mm)
4. Grid: Setup → Preferences → Grid → Design Grid 100mil
5. 저장: File → Save As → "OpenCR_REVH.sch"
```

### 1.4 PADS Logic 인터페이스

```
┌──────────────────────────────────────────────┐
│  [타이틀바] OpenCR_REVH.sch — PADS Logic      │
├──────┬───────────────────────────────────────┤
│ [도구]│  [디자인 영역]                         │
│ 모음  │                                       │
│  바  │                                       │
│      │                                       │
├──────┤───────────────────────────────────────┤
│ 상태 표시줄 │ 좌표: X  Y    Grid: 100         │
└──────┴───────────────────────────────────────┘
```

| 영역 | 설명 |
|------|------|
| **디자인 도구모음 (Design Toolbar)** | 부품 배치, 와이어, 네트워크, 버스 |
| **선택 도구모음 (Selection Toolbar)** | 선택/필터 모드 |
| **클립보드 (Clipboard)** | 오른쪽 패널 — 부품 검색/배치 |
| **상태 표시줄** | 좌표, 그리드, 레이어 정보 |

### 1.5 기본 단축키

| 단축키 | 기능 |
|:------:|------|
| `Ctrl+W` | 와이어 (Wire) 모드 |
| `Ctrl+I` | 줌 인 |
| `Ctrl+O` | 줌 아웃 |
| `F5` | 화면 새로고침 |
| `Home` | 전체 보기 |
| `R` | 부품 회전 (배치 중) |
| `X` | 부품 미러 |
| `Ctrl+C / V` | 복사/붙여넣기 |
| `Delete` | 삭제 |

> **PADS 핵심 개념**: 모든 명령은 **모달(Modal)** 방식 → 단축키 누르면 해당 모드 진입, `Esc`로 해제

---

## Step 2: CAE 심볼 + 부품 라이브러리 (1h 20min)

### 2.1 PADS 라이브러리 구조 이해

PADS 라이브러리는 세 가지 파일로 구성된다:

| 파일 | 확장자 | 설명 |
|:----:|:------:|------|
| **라이브러리** | .pt9 | 파트 타입 (심볼 + 풋프린트 + 전기적 특성 통합) |
| **CAE 심볼** | .cae | 회로도용 논리 심볼 |
| **PCB 풋프린트** | .pcb | PCB용 패턴 (동일 .pt9에 포함 가능) |

> KiCAD/Altium과 달리, PADS는 **Part Type**이라는 단위로 심볼과 풋프린트를 함께 관리한다.

### 2.2 라이브러리 관리자 실행

```
Tools → Library Manager
또는 단축키: Ctrl+L
```

### 2.3 기존 라이브러리 추가

```
Library Manager → Libraries → Add
- C:\MentorGraphics\PADS\SDD_HOME\Libraries\ 에 있는 기본 라이브러리 추가
- misc.pt9, discrete.pt9, gate.pt9, connector.pt9 등
```

### 2.4 새 Part Type 생성 — LM5175PWPR

CAE 심볼과 PCB 풋프린트를 포함한 Part Type을 생성한다.

#### CAE 심볼 생성

```
1. Tools → Library Manager → CAE Decal → New
2. Name: "LM5175PWPR"
3. Editor 창:
   - Options → Grid: 100mil
   - 2D Line 도구로 직사각형 본체 (Width 400mil, Height 500mil)
   - 핀 배치: Terminal 도구 (Pin)
     * Pin Number / Pin Name 입력
     * Left side: VIN(1), EN(2), FB(3), COMP(4), SS(5)
     * Top: SW(6), BST(7)
     * Right: PGND(8), SGND(9), VCC(10)
     * Bottom: VSNS+(11), VSNS-(12), ILIM(13), RT(14)
   - 핀 유형: Pin Properties → Electrical Type (IN/OUT/PWR/GND/BI)
4. 저장: File → Return to Library Manager
```

#### PCB 풋프린트 설정

```
1. Library Manager → PCB Decal → New
2. Name: "HTSSOP-28"
3. Wizard 사용: Tools → Decal Wizard
   - Package Type: SOIC
   - Pin Count: 28
   - Pitch: 0.65mm
   - Body Width: 4.4mm, Body Length: 9.7mm
   - Pad Width: 0.3mm, Pad Length: 1.0mm
4. 열 패드 추가: Exposed Pad (중앙, 8.0×3.5mm)
5. 저장
```

#### Part Type 연결

```
1. Library Manager → Part Type → New
2. Name: "LM5175PWPRTK"
3. General 탭: 
   - Logic Family: "IC"
   - Part Number: "LM5175PWPR"
   - Manufacturer: "Texas Instruments"
4. PCB Decal 탭: HTSSOP-28 선택
5. Gates 탭:
   - CAE Decal: LM5175PWPR 선택
   - Pin Mapping: CAE 핀 번호 ↔ PCB 핀 번호 매핑
6. 저장
```

### 2.5 주요 부품 Part Type 생성 목록

| 부품 | Part Type | CAE Decal | PCB Decal |
|------|-----------|-----------|-----------|
| STM32F746ZGT6 | STM32F746ZGT6TK | LQFP-144_CAE | LQFP-144 |
| LM5175PWPR | LM5175PWPRTK | HTSSOP-28_CAE | HTSSOP-28 |
| XL4005 | XL4005TK | TO263-5_CAE | TO263-5 |
| AZ1117H-3.3 | AZ1117HTK | SOT223_CAE | SOT223 |
| A3906SESTR-T | A3906TK | QFN20_CAE | QFN20 |
| TJF1051T/3 | TJF1051TK | SOP8_CAE | SOP8 |
| ICM-20648 | ICM20648TK | QFN24_CAE | QFN24 |
| B3B-EH-A | JST3_CAE | 3PIN_CAE | JST-EH-3 |

> **팁**: PADS Library는 `Filter` 기능으로 부품명 검색. 기본 라이브러리에 유사 부품이 있으면 복사 후 수정하는 방식이 효율적

### 2.6 부품 검색 및 배치 준비

```
Clipboard 패널 (오른쪽) → Parts 검색
또는 Design Toolbar → Add Part 버튼 → Library 검색
```

### 2.7 라이브러리 파일 저장

```
File → Library → Save All Changes
→ 내 라이브러리: "OpenCR_Lib.pt9"
```

---

## Step 3: 전원부 회로도 작성 (1h 30min)

### 3.1 부품 배치

```
Design Toolbar → Add Part (Ctrl+P)
또는 Clipboard → Parts → LM5175PWPRTK 검색 → 더블클릭 → 배치

같은 방식으로 다음 부품 순서 배치:
1. F1: 0453010 (Fuse, Library: discrete → fuse)
2. L2: XAL6060-472MEB (4.7uH Inductor)
3. C1~C6: Capacitor (Library: discrete → cap)
4. R1~R6: Resistor (Library: discrete → res)
5. U4: LM5175PWPR
6. U5: XL4005
7. U6: IL1117-5.0
8. U23: AZ1117H-3.3
```

### 3.2 와이어 연결

```
Design Toolbar → Wire (Ctrl+W)
→ 클릭으로 시작, 클릭으로 꺾기, 더블클릭으로 종료
→ 와이어 위에서 우클릭 → Add Vertex: 꺾는 점 추가
```

### 3.3 전원 네트워크 할당

```
1. 와이어 위에서 우클릭 → Add Net Name
   (또는 Design Toolbar → Net)
2. 이름 입력: "VCC_12V" → OK
3. Net Name 표시 위치 지정

주요 네트워크:
- VCC_12V (LM5175 출력 → XL4005 입력)
- VCC_5V (XL4005 출력 → AZ1117 입력)
- VCC_3V3 (AZ1117 출력 → MCU VDD)
- VUSB (USB VBUS → IL1117 입력)
- GND, AGND, PGND
```

### 3.4 전원부 상세 연결

#### LM5175PWPR (벅-부스트, 5-24V → 12V)

```
VIN: DC 입력 (5~24V) + C1(10uF) + C2(100nF)
EN: R1(100k) to VIN + R2(47k) to GND (분배기, 3.3V enable)
FB: R3(10k) to VCC_12V + R4(1k) to GND → FB 핀
   VOUT = 0.8V × (1 + R3/R4) = 0.8 × (1 + 10/1) = 8.8V
   → 12V 출력 위해 R3=15k, R4=1.15k 조정
SW: L2(XAL6060-472MEB, 4.7uH) → VCC_12V
COMP: R5(15k) + C3(10nF) 직렬 → C4(470pF) 병렬 → GND
SS: C5(10nF) to GND (Soft Start)
BST: C6(100nF) between BST and SW
RT: R6(100k) to GND (Switching Frequency 설정)
PGND: 직접 GND plane 연결
SGND: AGND 분리
VCC: C7(1uF) to GND
```

#### XL4005 (12V → 5V)

```
VIN: 12V + C8(10uF)
EN: 100k pull-up to VIN (항상 켜짐)
FB: R7(10k) to 5V + R8(1k) to GND (5V 설정)
SW: D1(Schottky) + L3(10uH) → 5V 출력
  출력: C9(22uF) + C10(100nF)
```

#### AZ1117H-3.3 (5V → 3.3V)

```
VIN: 5V + C11(10uF) + C12(100nF)
VOUT: 3.3V + C13(10uF) + C14(100nF)
GND: 직접 GND
```

#### IL1117-5.0 (USB 5V LDO)

```
VIN: VUSB + C15(10uF)
VOUT: 5V + C16(10uF)
GND: GND
```

### 3.5 전원 계층 구조

전원 네트워크를 체계적으로 연결한다:

```
DC_IN (5~24V)
  └── F1 ─┬── VCC_12V (LM5175 벅-부스트 출력)
           │
           └── XL4005 ── VCC_5V ──┬── AZ1117H-3.3 ── VCC_3V3
                                  │
                                  └── IL1117-5.0 ── VCC_5V_USB
```

### 3.6 Power Symbol 배치

```
Design Toolbar → Power (Ctrl+Shift+P)
→ VCC/VDD/GND 심볼 선택 → 배치

혹은:
Design Toolbar → Add Part → "GND" 검색 → 배치
```

### 3.7 전원부 완성 확인

```
- 모든 IC에 전원(VIN/VCC/VDD) 연결됨
- 모든 GND 핀 연결됨 (PGND/SGND/AGND 구분)
- 모든 바이패스 커패시터 배치됨
- Feedback divider 정확한 출력 전압 설정
```

---

## Step 4: MCU STM32F746 주변회로 (1h 30min)

### 4.1 MCU 배치

```
Add Part → STM32F746ZGT6 (LQFP-144) 배치
→ 중앙 위치, 우측 90° 회전 (필요시 R 키)
```

### 4.2 전원 핀 연결

MCU 전원 핀을 배선한다. VDD 그룹별로 처리:

```
VDD1~VDD11 그룹 → VCC_3V3
  각 VDD 핀 근처에 100nF 바이패스 캡 배치 (C17~C27)
  10uF bulk cap 1개 추가 (C28)

VDDA → VCC_3V3 + Ferrite Bead (FB1)
  C29(10uF) + C30(100nF) to GND

VREF+ → VDDA (직결)
VREF- → GND

VCAP1 → C31(2.2uF) → GND
VCAP2 → C32(2.2uF) → GND

VSS1~VSS11 → GND (각각 GND via)
VSSA → GND (분리)
```

### 4.3 크리스탈 회로

#### 25MHz 메인 크리스탈

```
Y1 (25MHz, SX-32):
  Pin1: OSC_IN (PE0) → MCU
  Pin2: OSC_OUT (PE1) → MCU
  Load caps: C33(22pF) OSC_IN→GND, C34(22pF) OSC_OUT→GND
  GND guard ring: 크리스탈 주변 GND copper pour
```

#### 32.768kHz RTC 크리스탈

```
Y2 (32.768kHz, CM315):
  Pin1: PC14 (OSC32_IN) → MCU
  Pin2: PC15 (OSC32_OUT) → MCU
  Load caps: C35(12.5pF) each → GND
```

### 4.4 Reset 회로

```
SW1 (Tactile Switch):
  → NRST (MCU 핀)
  → R9(10k) pull-up to VCC_3V3
  → C36(100nF) to GND (debounce)
```

### 4.5 BOOT 회로

```
SW2 (Jumper or Switch):
  → BOOT0 (PB2, MCU 핀)
  → R10(10k) pull-down to GND
  → R11(10k) 점퍼 통해 VCC_3V3 연결 (선택)
```

### 4.6 SWD 프로그래밍 인터페이스

```
J2 (Header 5P, 2.54mm pitch):
  Pin1: VCC_3V3
  Pin2: SWDIO (PA13, MCU)
  Pin3: SWCLK (PA14, MCU)
  Pin4: NRST
  Pin5: GND
```

### 4.7 기타 필수 핀 처리

```
PDR_ON: Pull-up to VCC_3V3 (10k)
   (내부 전압 조정기 활성화)

VBAT: C37(100nF) to GND + CR2032 배터리 홀더 (옵션)
```

---

## Step 5: 모터 드라이버 + 통신 인터페이스 (1h)

### 5.1 A3906 모터 드라이버 x2

#### U7 (Motor 1)

```
Add Part → A3906SESTR-T 배치

핀 연결:
  IN1(PB0), IN2(PB1), PWM(PA0), SLEEP(PC0)
  VREF: R12(0.1Ω) → GND (전류 감지)
  VCC: VCC_5V
  VM: VCC_12V (모터 전원)
  OUT1 → JP1-1 (모터 커넥터)
  OUT2 → JP1-2 (모터 커넥터)
  GND → GND
  Charge pump: C38(100nF) between CP+ and VM
```

#### U14 (Motor 2)

```
Motor 1과 동일한 연결:
  IN1(PB2), IN2(PB3), PWM(PA1), SLEEP(PC1)
  OUT1 → JP2-1
  OUT2 → JP2-2

> **팁**: U7 블록 선택 → Ctrl+C → Ctrl+V → 핀만 재연결
```

### 5.2 CAN 인터페이스

```
U9: TJF1051T/3

핀 연결:
  TXD(PD1) → MCU FDCAN1_TX
  RXD(PD0) → MCU FDCAN1_RX
  CANH → R13(120Ω) → CANH_Conn
  CANL → R13(120Ω) → CANL_Conn
  VCC → VCC_3V3
  GND → GND
  S (Silent): GND (Normal mode)

커넥터: J3 (20010WS-04)
  Pin1: CANH
  Pin2: CANL
  Pin3: VCC_12V
  Pin4: GND
```

### 5.3 RS-485 인터페이스

```
U11: MAX3443ECSA+

핀 연결:
  RO(PB11) → MCU UART_RX
  DI(PB10) → MCU UART_TX
  RE(PB12) → MCU GPIO (Active Low)
  DE(PB13) → MCU GPIO
  A → J4-1 (B4B-EH-A)
  B → J4-2
  VCC → VCC_3V3
  GND → GND

종단 저항: R14(120Ω) between A and B (점퍼 선택)
```

### 5.4 IMU 센서

```
U16: ICM-20648

핀 연결:
  SDA(PB9) → MCU I2C1_SDA
  SCL(PB8) → MCU I2C1_SCL
  INT(PE0) → MCU EXTI0
  AD0 → GND (I2C address 0x68)
  nCS → VCC_3V3 (SPI 모드 비활성화)
  VDD → VCC_3V3
  VIO → VCC_3V3
  GND → GND
  BYP → C39(100nF) to GND
  REGOUT → C40(1uF) to GND

I2C pull-up: R15(4.7k) SDA to VCC_3V3, R16(4.7k) SCL to VCC_3V3
```

### 5.5 USB OTG

```
U21: STMPS2141STR (USB 전원 스위치)

핀 연결:
  EN(PG0) → MCU GPIO
  FLG(PG1) → MCU GPIO (Fault flag)
  IN → VUSB
  OUT → J1 VBUS pin
  GND → GND

U17: EMIF02-USB03F2 (EMI + ESD 필터)
  D+ → J1 DP → MCU PA11
  D- → J1 DM → MCU PA12
  GND → GND

J1: ZX62D-B-5P8 (Micro-B USB)
  Pin1: VBUS
  Pin2: D-
  Pin3: D+
  Pin4: ID (PA10, MCU)
  Pin5: GND
  Shield: GND (via array for EMC)
```

---

## Step 6: 커넥터 + 종합 검토 (1h)

### 6.1 DYNAMIXEL TTL 커넥터 (JST B3B-EH-A)

```
J6, J8, J25: TTL DYNAMIXEL 3채널

핀 배열 (B3B-EH-A):
  Pin1: TX (MCU UART TX)
  Pin2: RX (MCU UART RX)
  Pin3: GND

보호: 각 라인에 SM712 TVS 다이오드 (U2, U12, U24)
  → 신호 라인과 GND 사이에 ESD 보호
```

### 6.2 DYNAMIXEL RS-485 커넥터 (JST B4B-EH-A)

```
J15, J16, J17: RS-485 DYNAMIXEL 3채널

핀 배열 (B4B-EH-A):
  Pin1: 485+
  Pin2: 485-
  Pin3: VCC_12V (모터 전원)
  Pin4: GND
```

### 6.3 범용 UART/CAN 커넥터

```
J18, J19, J20: 20010WS-04

핀 배열:
  Pin1: TX/UART
  Pin2: RX/UART
  Pin3: VCC_3V3
  Pin4: GND
```

### 6.4 배선 검증

```
Tools → Verify Design (Ctrl+Alt+V)
→ Check: Unconnected Pins, Single Pin Nets, Shorts
→ Report 확인
```

### 6.5 리포트 생성

```
Tools → Reports → Netlist Report
→ 모든 네트워크 연결 목록 확인

Tools → Reports → Part List Report
→ 모든 부품 목록 (Reference, Part Type, Value)
```

### 6.6 ERC (Electrical Rule Check) — PADS 방식

PADS Logic은 별도의 ERC 명령 대신 **Verify Design**으로 검사:

```
1. Tools → Verify Design
2. Check:
   [x] Single Pin Nets (1핀만 연결된 네트워크)
   [x] Unconnected Pins (연결 안 된 핀)
   [x] Duplicate Net Names (중복 네트워크명)
   [x] Bus Errors
   [x] Power Pin Errors
3. OK → Results 패널에 오류 표시
4. 각 오류 더블클릭 → 해당 위치로 이동 → 수정
5. Clear → Verify 재실행 → 오류 0 확인
```

### 6.7 저장 및 백업

```
1. File → Save (Ctrl+S)
2. Tools → Archive → Create Archive
   → "OpenCR_REVH_Backup.zip" (모든 라이브러리 포함)
```

### Step 6 체크리스트

- [ ] 모든 커넥터 핀맵이 OpenCR 원본과 일치한다
- [ ] TVS 보호 다이오드가 통신 라인에 추가되었다
- [ ] Verify Design 오류가 0이다
- [ ] Netlist Report가 정상 출력된다
- [ ] Part List Report가 정상 출력된다
- [ ] Archive 파일로 백업되었다

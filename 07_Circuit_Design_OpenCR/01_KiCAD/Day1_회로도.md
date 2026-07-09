# Day 1: 회로도 설계 (Schematic Design) — 7시간

---

## Step 1: KiCAD 설치 및 프로젝트 생성 (40분)

### 1.1 KiCAD 8 다운로드 및 설치

1. **브라우저**를 열고 [https://www.kicad.org/download/windows/](https://www.kicad.org/download/windows/) 접속
2. **Windows Installer** (`kicad-8.0.x-x86_64.exe`) 다운로드
3. 설치 파일 실행 → **기본 설치 (Full Install)** 선택
   - _참고: Full Install 시 모든 라이브러리(심볼, 풋프린트, 3D 모델)가 함께 설치됨_
4. 설치 완료 후 KiCAD 실행 확인

> **📸 Screenshot:** KiCAD 8 시작 화면 — 프로젝트 매니저 (왼쪽: 최근 프로젝트 목록, 오른쪽: 독립 도구 아이콘)

### 1.2 프로젝트 생성

1. **KiCAD 실행** → 메인 윈도우 (Project Manager)
2. `File → New → Project` 또는 **Ctrl+N**
3. 프로젝트 이름: `OpenCR_KiCAD`
4. 저장 위치: `01_KiCAD/OpenCR_KiCAD/`
5. **자동 생성 파일:**
   - `OpenCR_KiCAD.kicad_pro` — 프로젝트 설정
   - `OpenCR_KiCAD.kicad_sch` — 회로도
   - `OpenCR_KiCAD.kicad_pcb` — PCB (빈 파일)
   - `OpenCR_KiCAD.kicad_prl` — 로컬 설정

### 1.3 Schematic Editor (Eeschema) 열기

1. Project Manager에서 **Schematic Editor** 아이콘 클릭 (또는 `.kicad_sch` 파일 더블클릭)
2. 편집기 레이아웃 확인:
   - **상단:** 메뉴바 + 툴바 (파일, 편집, 배치, 배선, 검사)
   - **좌측:** 도구 팔레트 (부품 선택, 배선, 라벨 등)
   - **중앙:** 캔버스 (그리드 표시)
   - **우측:** Properties 패널 (선택한 객체 속성)
   - **하단:** 명령어 로그 + 좌표 표시줄

### 1.4 Page Settings 설정

1. `File → Page Settings` (또는 우측 Properties 패널에서)
2. **Paper Size:** `A3` (297mm × 420mm) — OpenCR 회로도 크기에 적합
3. **Title Block** 입력:
   - **Title:** `OpenCR Rev.H Reference Schematic`
   - **Date:** `2026-07-05`
   - **Revision:** `1.0`
   - **Company:** `(소속 기관명)`
   - **Comment 1:** `Day 1 - KiCAD Training`

> **💡 Tip:** A3를 선택하는 이유 — LQFP-144 MCU와 여러 전원 IC를 한 장에 배치하려면 넉넉한 공간이 필요합니다.

> **📸 Screenshot:** Page Settings 대화상자 — A3 선택, Title Block 작성된 모습

---

## Step 2: 부품 라이브러리 및 심볼 생성 (1시간 20분)

### 2.1 Symbol Libraries 관리

1. `Preferences → Manage Symbol Libraries` (또는 Shift+Ctrl+L)
2. **Global Libraries** 탭:
   - 모든 프로젝트에서 공통으로 사용
   - KiCAD 설치 시 기본 라이브러리 자동 등록
3. **Project Libraries** 탭:
   - 현재 프로젝트 전용 라이브러리
   - 실습에서는 **Project Libraries**에 추가

### 2.2 필수 공식 라이브러리 추가 (Project Libraries)

| 라이브러리 이름 | 설명 |
|:---|:---|
| `MCU_STM32F7` | STM32F746 심볼 포함 |
| `Power_Management` | 전원 IC (LM5175 계열) |
| `Sensor_Motion` | IMU 센서 (ICM-20648 등) |
| `Interface_CAN_LIN` | CAN 트랜시버 (TJF1051) |
| `Interface_UART` | RS-485 트랜시버 |
| `Connector` | 각종 커넥터 심볼 |
| `Device` | 기본 수동소자 (R, C, L, LED 등) |
| `Amplifier_Audio` | OP-AMP 계열 포괄 |

**추가 방법:**
1. `Manage Symbol Libraries` → `Project Libraries` 탭
2. **폴더 아이콘 (⊕)** 클릭
3. 설치 경로 예: `C:\Program Files\KiCAD\8.0\share\kicad\symbols\MCU_STM32F7.kicad_sym`
4. 라이브러리 리스트에 추가된 것 확인
5. **OK** 버튼

> **⚠️ 중요:** KiCAD Global Libraries 경로는 설치 버전에 따라 다를 수 있습니다. `Preferences → Configure Paths`에서 `KICAD8_SYMBOL_DIR` 값 확인

### 2.3 직접 심볼 생성 — STM32F746ZGT6 (LQFP-144)

공식 라이브러리에 STM32F746ZG가 없거나 핀 배열이 다른 경우 직접 생성합니다.

1. **Symbol Editor** 열기: `Tools → Symbol Editor` (또는 아이콘 클릭)
2. `File → New Symbol`
3. `Create new symbol from current sheet?` → **No**
4. 입력:
   - **Name:** `STM32F746ZGT6`
   - **Library:** 프로젝트 라이브러리 선택 (또는 `OpenCR_Symbols` 새로 생성)
   - **Symbol type:** `Component`
5. **Pin Count:** `144` 입력
6. Symbol Properties 패널:
   - **Reference Prefix:** `U`
   - **Datasheet:** `https://www.st.com/resource/en/datasheet/stm32f746zg.pdf`

#### 핀 배치 전략 (LQFP-144)

144핀을 효율적으로 배치하기 위해 **Power Logic (Unit) 분할** 사용:

| Unit | 핀 번호 | 내용 |
|:---|:---:|:---|
| **U1A** | 1~48 | 좌측: 전원, 리셋, 클록 (VDD, VDDA, VCAP, RST, OSC) |
| **U1B** | 49~96 | 하단: GPIO Port A~G 중 일부 (UART, I2C, SPI) |
| **U1C** | 97~144 | 우측: GPIO Port G~I, CAN, USB, SDMMC, FMC |

**핀 추가 방법:**
1. `Place → Pin` (단축키 `P`)
2. 핀 속성 입력:
   - **Name:** `PA0` (핀 이름)
   - **Pin Number:** `24` (핀 번호 — Datasheet 기준)
   - **Electrical Type:** `Bidirectional` / `Input` / `Output` / `Power I/O`
   - **Graphic Style:** `Line` (기본)

**Datasheet 참고 핀 예시 (STM32F746ZG):**

| 핀 번호 | 핀 이름 | 전기적 타입 | 비고 |
|:---:|:---|:---|:---|
| 24 | PA0 | Bidirectional | GPIO |
| 41 | PA13 (SWDIO) | Bidirectional | SWD |
| 42 | PA14 (SWCLK) | Input | SWD |
| 8 | NRST | Input | Reset |
| 12 | OSC_IN | Input | 25MHz |
| 13 | OSC_OUT | Output | 25MHz |
| 14 | OSC32_IN | Input | 32.768kHz |
| 15 | OSC32_OUT | Output | 32.768kHz |
| 16~21 | VDD_1~VDD_11 | Power Input | 각 3.3V |
| 22 | VDDA | Power Input | Analog 3.3V |
| 32~34 | VSS_1~VSS_11 | Power Input | GND |
| 35, 36 | VCAP_1, VCAP_2 | Passive | 2.2µF |
| 46~48 | VREF+, VREF-, VSSA | Power Input | ADC 기준전압 |

### 2.4 직접 심볼 생성 — LM5175PWPR (HTSSOP-28)

1. Symbol Editor에서 `File → New Symbol`
2. **Name:** `LM5175PWPR`, **Pin Count:** `28`
3. Unit 분할: **Single Unit** (28핀 한 화면에 배치 가능)

**주요 핀 배치:**

| 좌측 (입력/제어) | 우측 (출력/전력) |
|:---|:---|
| 1: EN | 28: VCC |
| 2: SS | 27: HO1 |
| 3: RT | 26: SW1 |
| 4: FB | 25: LO1 |
| 5: COMP | 24: PGND |
| 6: PGOOD | 23: LO2 |
| 7: SYNC | 22: SW2 |
| 8: DITHER | 21: HO2 |
| 9: ILIM | 20: BOOT2 |
| 10: UVLO | 19: VIN |
| 11: SLOPE | 18: BIAS |
| 12: MODE | 17: AGND |
| 13: DEMB | 16: BOOT1 |
| 14: NC | 15: CS |

### 2.5 직접 심볼 생성 — A3906SESTR-T (QFN-20)

1. **Name:** `A3906SESTR-T`, **Pin Count:** `20`
2. Grid 사이즈 **2.54mm (100mil)** 기준으로 핀 배치

**핀 구성:**
- **좌측:** IN1A, IN1B, PWM1, EN1, MODE1
- **하단:** VBB1, VBB2, GND, CP1, CP2
- **우측:** OUT1A, OUT1B, OUT2A, OUT2B, SENSE1
- **상단:** IN2A, IN2B, PWM2, EN2, MODE2

### 2.6 커넥터 심볼 생성

**JST B3B-EH-A (3핀):**
1. `Name:` `JST_B3B-EH-A`, `Pin Count:` `3`
2. 핀 1~3: `VCC`, `DATA`, `GND` (또는 `1`, `2`, `3`)
3. 심볼 타입: **Passive** (커넥터는 수동 소자)

**JST B4B-EH-A (4핀):**
1. `Name:` `JST_B4B-EH-A`, `Pin Count:` `4`
2. 핀 1~4: `VCC`, `DATA+`, `DATA-`, `GND`

**20010WS-04 (4핀):**
1. `Name:` `20010WS-04`, `Pin Count:` `4`
2. 용도: UART/CAN 신호 커넥터

### 2.7 Symbol Fields 입력 (필수)

각 심볼에는 **반드시 4가지 필드**를 입력해야 PCB 작업이 가능합니다:

| 필드 | 내용 | 예시 |
|:---|:---|:---|
| **Reference** | 부품 식별자 (자동 할당) | `U?`, `R?`, `C?` |
| **Value** | 부품 값 또는 모델명 | `STM32F746ZGT6` |
| **Footprint** | 풋프린트 라이브러리 경로 | `Package_QFP:LQFP-144_20x20mm_P0.5mm` |
| **Datasheet** | 데이터시트 URL | `https://www.st.com/...` |

> **📸 Screenshot:** Symbol Editor에서 STM32F746ZGT6의 144핀 배치 완료 화면 (4개의 Unit 탭)

---

## Step 3: 전원부 회로도 작성 (1시간 30분)

### 3.1 부품 배치 — 입력단

1. `Place → Symbol` (단축키 `A`)
2. 라이브러리 브라우저에서 다음 부품 검색 및 배치:

| 부품 | 심볼 | RefDes | Value |
|:---|:---|:---:|:---|
| 퓨즈 | `Device:Fuse` | `F1` | `0453010` (10A, 125V) |
| 입력 커넥터 | `Connector:Conn_02x01_Pin` | `J1` | `DC_JACK` |
| TVS 다이오드 | `Device:TVS` | `D1` | `SMBJ24A` |
| 입력 캡 | `Device:C` | `C1, C2, C3` | `10µF, 0.1µF, 0.01µF` |

3. 배치 위치: Page 좌측 상단 (입력단 → 전원 IC 순서)

### 3.2 LM5175PWPR Buck-Boost 회로 (Vin 5~24V → Vout 12V)

1. `LM5175PWPR` 심볼 배치 — RefDes `U2`
2. 주변 부품 배치 및 배선:

```
[LM5175PWPR 주요 회로]

VIN (5-24V) ──┬── C4(10µF) ── GND
              └── C5(0.1µF) ── GND
              └── 19(VIN) ────────────── 15(CS) ── R1(0.01Ω, 2512) ── L2(4.7µH) ── VOUT(12V)

VOUT(12V) ──┬── C6(22µF) × 3 ── GND
            └── R2(10kΩ) ── 4(FB) ─── R3(10kΩ) ── GND
            └── R4(100kΩ) ── 6(PGOOD)

EN ──── R5(100kΩ) ── VIN (Enable 항상 ON)
RT ──── R6(100kΩ) ── GND (fSW = 400kHz 설정)
```

**피드백 저항 계산 (Vout = 12V):**
```
Vout = VFB × (1 + R3/R2)
12V = 0.8V × (1 + R3/10kΩ)
R3 = (12/0.8 - 1) × 10kΩ = 140kΩ

→ R2 = 10kΩ, R3 = 140kΩ (또는 110kΩ + 30kΩ 직렬)
```

> **💡 Tip:** LM5175PWPR 데이터시트의 "Typical Application Circuit" 페이지를 참고하세요.

### 3.3 XL4005 회로 (12V → 5V, 4A)

1. 심볼 배치: `U3` — XL4005 (직접 생성한 심볼 또는 `Power_Management`에서 유사 심볼 활용)
2. 회로 구성:

```
12V ──┬── C7(100µF) ── GND
      └── 1(VIN) XL4005 ── 2(SW) ── L3(33µH) ── 5V_OUT
                                   └── D2(SS54) ── GND (Schottky)
3(FB) ── R7(10kΩ) ── 5V_OUT
      └── R8(2kΩ) ── GND
4(EN) ── 5V_OUT (내부 풀업)

5V_OUT ──┬── C8(100µF) ── GND
         └── C9(0.1µF) ── GND
```

**피드백 저항:**
```
Vout = 0.8V × (1 + R7/R8)
5V = 0.8V × (1 + 10kΩ/R8)
R8 = 0.8V × 10kΩ / (5V - 0.8V) = 1.9kΩ → 2kΩ (표준값)
```

### 3.4 AZ1117H-3.3 LDO (5V → 3.3V)

1. 심볼 배치: `U4` — `AZ1117H-3.3TRG1`
2. RefDes `U4` (SOT-223 패키지)

```
1(IN) ── C10(10µF) ── GND
2(OUT) ──┬── C11(10µF) ── GND
         └── C12(0.1µF) ── GND
3(GND) ── GND
```

### 3.5 IL1117-5.0 LDO (USB 5V)

1. 심볼 배치: `U5` — `IL1117-5.0ET`
2. USB VBUS 입력 → 5V 출력 (동일한 LDO 회로)
3. 입력 캡 `C13(10µF)`, 출력 캡 `C14(10µF) + C15(0.1µF)`

### 3.6 Power Flag 연결

1. `Place → Power Port` (단축키 `P`)

| Power Flag | Symbol |
|:---|:---|
| `VCC_12V` | `Power_Flag` or `PWR_FLAG` |
| `VCC_5V` | `Power_Flag` |
| `VCC_3V3` | `Power_Flag` |
| `GND` | `GND` (Power symbol) |
| `AGND` | `GND` (Analog — 분리 필요시 별도 심볼) |

2. **배치 방법:**
   - 각 전원 출력 노드에 `PWR_FLAG` 심볼 연결
   - ERC에서 `Power input not driven` 경고 방지
   - 전원 계층: `VIN_5-24V` → `VCC_12V` → `VCC_5V` → `VCC_3V3`

> **📸 Screenshot:** 전원부 전체 회로도 — 좌측 VIN 입력, LM5175, XL4005, LDO 순서로 3단 전원 계층 구조

### 3.7 키 포인트 — 수동소자 값 설정

| RefDes | Value | 비고 |
|:---:|:---:|:---|
| R1 | `0.01Ω 1%` | 전류 감지 (2512 size, 1W 이상) |
| R2, R7 | `10kΩ 1%` | FB 하단 저항 |
| R3 | `140kΩ 1%` | FB 상단 저항 (Vout=12V) |
| R4, R5 | `100kΩ 1%` | PGOOD, EN 풀업 |
| L2 | `4.7µH` | Buck-boost 인덕터 |
| L3 | `33µH` | XL4005 인덕터 |
| C4, C7 | `10µF, 100µF` | 입력 바이패스 |
| C6 | `22µF × 3` | 12V 출력 캡 |
| C10, C11 | `10µF` | LDO 입/출력 캡 |

---

## Step 4: MCU STM32F746 주변회로 (1시간 30분)

### 4.1 STM32F746ZGT6 심볼 배치

1. `Place → Symbol` (단축키 `A`)
2. `STM32F746ZGT6` 검색 → 배치 위치: **회로도 중앙**
3. 단위 선택: `U1A` (전원/클록), `U1B` (GPIO), `U1C` (통신) 순서로 배치

### 4.2 25MHz 메인 크리스탈

1. 부품 배치:
   - `X1`: `Device:Crystal` → `25MHz` (SX-32 패키지)
   - `C16, C17`: `Device:C` → `22pF` (Load Capacitor)

2. 배선:

```
MCU_12(OSC_IN) ──── X1(25MHz) ──── MCU_13(OSC_OUT)
                      │                │
                     C16              C17
                    22pF             22pF
                      │                │
                     GND              GND
```

**Load Capacitance 계산:**
```
CL = (C16 × C17) / (C16 + C17) + Cstray
  = (22pF × 22pF) / (44pF) + 5pF
  = 11pF + 5pF = 16pF (25MHz crystal CL=18pF에 근접, OK)
```

### 4.3 32.768kHz RTC 크리스탈

1. 부품 배치:
   - `X2`: `Device:Crystal` → `32.768kHz` (CM315 패키지)
   - `C18, C19`: `Device:C` → `12.5pF`

2. 배선:

```
MCU_14(OSC32_IN) ──── X2(32.768kHz) ──── MCU_15(OSC32_OUT)
                        │                    │
                       C18                  C19
                      12.5pF              12.5pF
                        │                    │
                       GND                  GND
```

> **⚠️ 크리스탈 배선 주의사항:**
> - 크리스탈과 MCU 사이 트레이스는 **가능한 짧게** (10mm 이내)
> - 주변에 다른 신호선 배치 금지
> - GND guard ring으로 감싸기 (PCB 단계)

### 4.4 Reset 회로

1. 부품:
   - `R9`: `Device:R` → `10kΩ` (풀업 저항)
   - `SW1`: `Device:SW_Push` → `Reset_Switch`

2. 배선:

```
VCC_3V3 ──┬── R9(10kΩ) ── MCU_8(NRST)
          └── SW1 ── GND
```

- **동작:** SW1 누르면 NRST=LOW → MCU 리셋
- **참고:** NRST는 내부 풀업 저항이 있지만, 외부 10kΩ 추가 권장

### 4.5 BOOT0 회로

1. 부품:
   - `R10`: `Device:R` → `10kΩ` (풀다운 저항)
   - `JP1`: `Device:Jumper` → `BOOT0_JUMPER`

2. 배선:

```
MCU_??(BOOT0) ──┬── R10(10kΩ) ── GND
                └── JP1(1-2) ── VCC_3V3
```

- **Normal boot:** BOOT0 = LOW (R10 풀다운)
- **System boot (DFU):** JP1 점퍼로 BOOT0 = HIGH

### 4.6 VDDA / VREF+ 필터 회로

```
VCC_3V3 ──┬── L1(Ferrite Bead, 600Ω@100MHz) ── VDDA
          │                                     │
          └── C20(0.1µF) ── GND                └── C21(1µF) ── GND

VREF+ ────┬── C22(0.1µF) ── GND
          └── C23(1µF) ── GND

VREF- ──── GND (or AGND)
VSSA ───── GND (or AGND)
```

### 4.7 VDD 바이패스 커패시터 (필수!)

STM32F746ZG는 **11개의 VDD 핀**이 있습니다. 각 VDD 핀마다 **100nF MLCC**를 **핀 바로 옆**에 배치:

| VDD 핀 | 바이패스 캡 |
|:---:|:---:|
| VDD_1 (pin 16) | C24 (100nF) |
| VDD_2 (pin 27) | C25 (100nF) |
| VDD_3 (pin 39) | C26 (100nF) |
| VDD_4 (pin 50) | C27 (100nF) |
| VDD_5 (pin 62) | C28 (100nF) |
| VDD_6 (pin 76) | C29 (100nF) |
| VDD_7 (pin 89) | C30 (100nF) |
| VDD_8 (pin 101) | C31 (100nF) |
| VDD_9 (pin 113) | C32 (100nF) |
| VDD_10 (pin 125) | C33 (100nF) |
| VDD_11 (pin 137) | C34 (100nF) |

**추가 Bulk Capacitor:**
- C35: `10µF` (MLCC, 0603 or 0805) — VDD 그룹당 1개

### 4.8 VCAP 핀

```
VCAP_1 (pin 35) ── C36(2.2µF) ── GND
VCAP_2 (pin 36) ── C37(2.2µF) ── GND
```

- VCAP은 내부 LDO 출력 핀으로 **반드시 2.2µF 이상의 저ESR 캐패시터** 연결
- 탄탈 or MLCC 권장 (전압 정격 6.3V 이상)

### 4.9 SWD/JTAG 디버그 커넥터

1. 심볼 배치: `Connector:Conn_02x05_Pin` → 10핀 헤더
2. RefDes: `J2`, Value: `ARM_SWD_10PIN`

| 핀 | 신호 | MCU 연결 |
|:---:|:---|:---|
| 1 | VCC_3V3 | 3.3V 전원 |
| 2 | SWDIO | PA13 |
| 3 | GND | GND |
| 4 | SWCLK | PA14 |
| 5 | GND | GND |
| 6 | SWO | PB3 (선택) |
| 7 | NC | - |
| 8 | NC | - |
| 9 | GND | GND |
| 10 | RESET | NRST |

> **📸 Screenshot:** STM32F746ZGT6 주변회로 전체 — 중앙 MCU, 좌측 크리스탈, 하단 SWD, 우측 GPIO

---

## Step 5: 모터 드라이버 + 통신 인터페이스 (1시간)

### 5.1 UART1 / DYNAMIXEL TTL (MAX3443ECSA+)

1. 심볼 배치: `U6` — `MAX3443ECSA+` (RS-485 트랜시버)

```
MCU_TX1(PA9)  ── 4(DI) MAX3443 ── 6(A) ── JST_DATA+
MCU_RX1(PA10) ── 3(RO)          ── 7(B) ── JST_DATA-
MCU_DIR(PA8)  ── 2(DE) + 5(/RE) ── (RS-485 방향 제어)
VCC_3V3       ── 1(VCC)
                ── 8(GND)
```

### 5.2 A3906 모터 드라이버 × 2

**A3906 #1 (U7):**

```
MCU_PA0(IN1A)  ── 1(IN1A)   A3906_U7
MCU_PA1(IN1B)  ── 2(IN1B)   16(IN2A) ── MCU_PA4
MCU_PA2(PWM1)  ── 3(PWM1)   15(IN2B) ── MCU_PA5
MCU_PA3(EN1)   ── 4(EN1)    14(PWM2) ── MCU_PA6
                ── 5(MODE1)  13(EN2)  ── MCU_PA7

VBB(모터전원) ──┬── 7(VBB1)  19(OUT1A) ── M1_A+
                └── 8(VBB2)  20(OUT1B) ── M1_B+
                9(GND) ── GND
                6(SENSE1) ── R11(0.1Ω) ── GND
```

**A3906 #2 (U8):** — 동일한 구성, GPIO만 다르게 연결

```
MCU_PB0(IN1A)  ── 1(IN1A)   A3906_U8
MCU_PB1(IN1B)  ── 2(IN1B)   16(IN2A) ── MCU_PB4
MCU_PB2(PWM1)  ── 3(PWM1)   15(IN2B) ── MCU_PB5
MCU_PB3(EN1)   ── 4(EN1)    14(PWM2) ── MCU_PB6
                ── 5(MODE1)  13(EN2)  ── MCU_PB7
```

### 5.3 CAN 인터페이스 (TJF1051T/3)

1. 심볼 배치: `U9` — `TJF1051T/3`

```
MCU_CAN1_TX(PB9)  ── 1(TXD)  TJF1051
MCU_CAN1_RX(PB8)  ── 4(RXD)
VCC_3V3           ── 2(VCC)
                   ── 3(GND)
CANH              ── 7(CANH) ──── J4_1
CANL              ── 6(CANL) ──── J4_2
```

2. CAN 종단 저항:

```
CANH ── R12(120Ω) ── CANL  (버스 종단, 커넥터 근처 배치)
```

### 5.4 IMU — ICM-20648 (I2C)

1. 심볼 배치: `U10` — `ICM-20648` (`Sensor_Motion` 라이브러리)

```
VCC_3V3 ──┬── 1(VDD)   ICM-20648
          └── 12(VI0)  (I/O 전압: 3.3V)
          2(GND) ── GND
          9(CS)  ── VCC_3V3 (SPI 모드 비활성화, I2C 모드)
          10(SCL) ── MCU_PB6(I2C1_SCL)
          11(SDA) ── MCU_PB7(I2C1_SDA)
          7(INT)  ── MCU_PC6(EXTI)
          8(AD0)  ── GND (I2C address: 0x68)

VCC_3V3 ── R13(4.7kΩ) ── SDA (I2C 풀업)
VCC_3V3 ── R14(4.7kΩ) ── SCL (I2C 풀업)
```

### 5.5 USB OTG (STMPS2141STR + EMIF02-USB03F2)

1. 심볼 배치: `U11` — `STMPS2141STR` (전원 스위치)

```
VBUS(5V) ── 1(IN)  STMPS2141
            2(OUT) ── C38(4.7µF) ── GND
                      └── VCC_USB
MCU_PA2(EN) ── 3(EN)
GND ── 4(GND)
             5(FLT) ── MCU_PC5 (오류 플래그)
```

2. 심볼 배치: `U12` — `EMIF02-USB03F2` (EMI 필터, ESD 보호)

```
D_P(USB_DP) ── 1(D_P_IN) ── 6(D_P_OUT) ── MCU_PA11(OTG_DP)
D_N(USB_DN) ── 3(D_N_IN) ── 4(D_N_OUT) ── MCU_PA12(OTG_DN)
ID ── 5(ID) ── GND (OTG Host 모드 고정)
GND ── 2(GND)
```

> **📸 Screenshot:** 통신 인터페이스 회로도 — 상단 RS-485, 중앙 CAN + 모터 드라이버, 하단 USB + IMU

---

## Step 6: 커넥터 + 종합 검토 (1시간)

### 6.1 DYNAMIXEL TTL 커넥터 (JST B3B-EH-A) × 3

| RefDes | 위치 | 신호 |
|:---:|:---|:---|
| `J5` | DYNAMIXEL 1 | `VCC_12V`, `TTL_DATA`, `GND` |
| `J6` | DYNAMIXEL 2 | `VCC_12V`, `TTL_DATA`, `GND` |
| `J7` | DYNAMIXEL 3 | `VCC_12V`, `TTL_DATA`, `GND` |

```
J5(JST B3B-EH-A)
┌───┬───┬───┐
│ 1 │ 2 │ 3 │
└───┴───┴───┘
 │   │   └── GND
 │   └────── TTL_DATA
 └────────── VCC_12V
```

### 6.2 DYNAMIXEL RS-485 커넥터 (JST B4B-EH-A) × 3

| RefDes | 핀 배열 |
|:---:|:---|
| `J8` | `VCC_12V`, `DATA+(B)`, `DATA-(A)`, `GND` |
| `J9` | `VCC_12V`, `DATA+(B)`, `DATA-(A)`, `GND` |
| `J10` | `VCC_12V`, `DATA+(B)`, `DATA-(A)`, `GND` |

### 6.3 UART/CAN 커넥터 (20010WS-04) × 3

| RefDes | 용도 | 신호 |
|:---:|:---|:---|
| `J11` | UART2 | `VCC_5V`, `TX2`, `RX2`, `GND` |
| `J12` | UART3 | `VCC_5V`, `TX3`, `RX3`, `GND` |
| `J13` | CAN | `VCC_5V`, `CANH`, `CANL`, `GND` |

### 6.4 Micro-B USB 커넥터 (ZX62D-B-5P8)

| RefDes | 핀 | 신호 | MCU 연결 |
|:---:|:---:|:---|:---|
| `J14` | 1 | VBUS | USB_5V (IL1117-5.0 출력) |
| | 2 | D- | MCU PA11 (via EMIF02) |
| | 3 | D+ | MCU PA12 (via EMIF02) |
| | 4 | ID | GND (Host) |
| | 5 | GND | GND |

### 6.5 ERC (Electrical Rule Check)

1. `Inspect → Electrical Rules Checker` (단축키: `Ctrl+E`)
2. **ERC 실행:**
   - 입력 핀 연결 안 됨 → 네트워크 레이블 추가
   - 전원 출력 미연결 → PWR_FLAG 추가
   - 플로팅 핀 → NC 마킹 또는 풀업/풀다운

**ERC 오류 예시 및 해결:**

| 오류 메시지 | 원인 | 해결 |
|:---|:---|:---|
| `Pin not connected (Warning)` | NC 핀 방치 | 핀에 "NC" 심볼 부착 |
| `Power input not driven` | PWR_FLAG 누락 | 출력 노드에 PWR_FLAG 추가 |
| `Output pin not connected` | IC 출력 핀 미연결 | 불필요시 NC 마킹 |
| `Unconnected wire` | 배선 중단 | 배선 완료 or 레이블 연결 |
| `Net label conflict` | 동일한 이름의 네트워크 상충 | 레이블 이름 통일 |

### 6.6 Annotation (RefDes 자동 할당)

1. `Tools → Annotate Schematic` (단축키: `Tools → A`)
2. 설정:
   - **Order:** `By X position` (좌→우 순서)
   - **Start from:** `1`
   - **Schematic sheets:** `All sheets`
3. `Annotate` 버튼 → 모든 부품에 `R1, R2, ...`, `C1, C2, ...`, `U1, U2, ...` 자동 할당
4. `Close` 후 결과 확인

> **📸 Screenshot:** ERC 결과 — 오류 0, 경고 0인 창 / Annotation 완료 후 회로도 (모든 부품에 RefDes 표시)

### 6.7 최종 회로도 검토 체크리스트

- [ ] 모든 IC에 전원 핀(VDD/VCC) 연결됨?
- [ ] 모든 GND 핀에 GND 심볼 연결됨?
- [ ] NC 핀은 NC 마킹 or 적절히 처리?
- [ ] 모든 바이패스 캡 배치됨?
- [ ] PWR_FLAG 누락 없음?
- [ ] ERC 오류/경고 0건?
- [ ] Annotation 완료?
- [ ] 네트워크 레이블 철자 일치?

---

## 📝 Day 1 요약

| 학습 항목 | 키워드 |
|:---|:---|
| 프로젝트 생성 | `.kicad_pro`, Page Settings, A3 |
| 심볼 생성 | Symbol Editor, Pin Table, Electrical Types |
| 전원 회로 | Buck-boost, LDO, Feedback Divider, Power Flag |
| MCU 회로 | Crystal, Reset, BOOT, VDDA Filter, Bypass Cap |
| 통신 인터페이스 | RS-485, CAN, I2C, USB OTG, EMI Filter |
| 검증 | ERC, Annotation, Netlist Consistency |

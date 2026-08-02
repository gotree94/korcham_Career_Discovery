# Day 1: 회로도 (Schematic) 작성 — 7시간

> OpenCR 보드를 예제로 EasyEDA에서 회로도를 작성합니다.

---

## Step 1: EasyEDA 시작 및 프로젝트 생성 (40min)

### 1.1 EasyEDA 접속

1. 브라우저에서 [https://easyeda.com](https://easyeda.com) 접속
2. 우측 상단 **Sign In** → **Sign up now** 클릭
3. **Continue with Google** 또는 **Continue with GitHub**로 간편 가입
   - 이메일 가입도 가능하나 Google 연동이 빠릅니다
4. 가입 완료 후 **Editor** 버튼 클릭 → EasyEDA Editor 실행

### 1.2 새 프로젝트 생성

```
Editor 화면 진입 → 상단 메뉴: File → New → Project
프로젝트 이름: OpenCR_EasyEDA
Description: OpenCR reference board design in EasyEDA
```

- 프로젝트가 생성되면 좌측 **Projects** 패널에 `OpenCR_EasyEDA` 표시됨

### 1.3 인터페이스 둘러보기

| 영역 | 설명 |
|------|------|
| **상단 메뉴바** | File, Edit, Tools, Design, Fabrication 등 |
| **좌측 패널** | Projects (프로젝트 트리), Libraries (부품 검색) |
| **중앙 캔버스** | Schematic / PCB / 3D 탭으로 전환 |
| **우측 패널** | Properties (선택 속성), Design Manager |
| **하단 상태바** | 좌표, 그리드, 스냅 설정 |

**3가지 탭 이해하기**:
- **Schematic** — 회로도 편집
- **PCB** — PCB 아트웍 (Day 2)
- **3D** — 3D 미리보기

### 1.4 필수 단축키

| 단축키 | 기능 |
|--------|------|
| **W** | Wire (와이어 연결) |
| **R** | Rotate (회전, 90°) |
| **Ctrl + S** | 저장 (수시로 저장!) |
| **Ctrl + D** | 복제 (Duplicated) |
| **Ctrl + Z** | 실행 취소 |
| **Ctrl + Y** | 다시 실행 |
| **Space** | 부품 배치 중 회전 |
| **Esc** | 현재 도구 종료 |
| **F** | Fit to screen (전체 보기) |
| **Ctrl + 휠** | 확대/축소 |
| **G** | 그리드 온/오프 |
| **Delete** | 선택 삭제 |
| **Ctrl + A** | 전체 선택 |

### 1.5 Schematic Editor 열기

- 하단 탭에서 **Schematic** 선택 (기본 선택됨)
- 검정 바탕의 캔버스가 열리면 준비 완료
- `Ctrl + S` 눌러 첫 저장

> **Tip**: EasyEDA는 클라우드 자동 저장이 되지만, 수동 저장(Ctrl+S) 습관을 들이세요.

---

## Step 2: 부품 라이브러리 및 심볼 추가 (1h 20min)

### 2.1 EasyEDA 라이브러리 시스템 이해

- **Libraries 패널** (좌측): 검색창에 부품명 입력
- **LCSC Parts**: 실제 재고가 있는 부품 (가격, 재고 수량 표시)
- **User Contributions**: 커뮤니티가 만든 심볼
- **Official**: EasyEDA 공식 라이브러리

> LCSC 검색 결과는 **심볼 + 풋프린트 + 3D 모델**이 한 번에 로드됩니다!

### 2.2 부품 검색 및 추가

#### 메인 MCU
```
Libraries 패널 검색창 → "STM32F746ZGT6" 입력 → Enter
→ LCSC Parts 탭에서 결과 선택
→ "STM32F746ZGT6" 클릭 → Place 버튼
→ 캔버스에 클릭하여 배치
```

- LQFP-144 패키지, 심볼과 풋프린트 함께 로드됨
- 144핀이라 핀이 많음 → Zoom In해서 확인

#### 전원부 부품들
```
"LM5175PWPR" 검색 → Place (HTSSOP-28)
"XL4005" 검색 → Place (TO-263-5)
"IL1117-5.0ET" 검색 → Place (SOT-223)
"AZ1117H-3.3TRG1" 검색 → Place (SOT-223)
```

#### 모터 드라이버
```
"A3906SESTR-T" 검색 → Place (QFN-20)
→ 2개 필요하므로 한 번 더 Place 또는 Ctrl+D 복제
```

#### 통신 IC
```
"TJF1051T/3" 검색 → Place (SOP-8)
"MAX3443ECSA+" 검색 → Place (SOP-8)
```

#### IMU 센서
```
"ICM-20648" 검색 → Place (QFN-24)
```

#### USB 관련
```
"STMPS2141STR" 검색 → Place (SOT-23-5)
"EMIF02-USB03F2" 검색 → Place
```

#### 퓨즈
```
"0453010" 검색 → Place
```

#### 커넥터
```
"B3B-EH-A" 검색 → Place (JST 3pin)
"B4B-EH-A" 검색 → Place (JST 4pin)
"20010WS-04" 검색 → Place
"ZX62D-B-5P8" 검색 → Place (Micro-B USB)
```

### 2.3 라이브러리에 없는 부품 — Custom Symbol 만들기

LCSC에 없는 부품이거나 검색이 안 되는 경우 직접 심볼을 만듭니다.

**Symbol Wizard 사용법**:
1. **Tools → Symbol Wizard** 선택
2. 속성 입력:
   - **Part Number**: LM5175PWPR (직접 입력)
   - **Manufacturer**: Texas Instruments
   - **Package**: HTSSOP-28
   - **Datasheet URL**: (선택, 있으면 입력)
3. 핀 수 지정 (28) → Generate
4. 심볼이 생성되면 핀 이름/번호 편집 (Properties 패널)
5. 저장 후 프로젝트의 Libraries > My Own에 추가됨

**직접 그리기**:
1. **Tools → Create Symbol** (또는 단축키 `Shift + N`)
2. 사각형 도구로 Body 그리기
3. **Pin 도구** (P)로 핀 추가
4. 각 Pin의 Name, Number, Direction 설정
5. 완료되면 **Save** → 라이브러리에 저장

### 2.4 배치 팁

- 부품을 대략적으로 캔버스에 펼쳐 놓습니다 (아직 와이어 연결 전)
- 큰 부품(MCU)은 중앙에, 전원부는 좌측에 배치
- `R` 키로 회전, `Space`로 배치 중 회전
- **Align 도구**: 여러 부품 선택 → 우클릭 → Align → Left/Center/Right

> **주의**: LCSC 검색 결과는 주기적으로 업데이트됩니다. 검색이 안 되면 철자나 대시(-) 유무를 확인하세요. 예: "A3906SESTR-T"와 "A3906SESTR T" 차이.

---

## Step 3: 전원부 회로도 작성 (1h 30min)

### 3.1 전원 아키텍처 이해

```
외부 DC 5~24V → [0453010 10A Fuse] → [LM5175 Buck-Boost] → 12V
                                                          ↓
                                                    [XL4005 DC-DC] → 5V
                                                                   ↓
                                                          [AZ1117H-3.3] → 3.3V
                         USB 5V → [IL1117-5.0 LDO] → 5V (VUSB)
```

### 3.2 입력 회로

1. **DC Jack 심볼 배치** (Power > VHDR 또는 직접 생성)
2. F1: **0453010** 직렬 연결 (10A, 125V)
3. TVS 다이오드 추가 (역전압 보호, SMAJ12A 추천)
4. 입력 커패시터: 10uF / 100V + 100nF

**배선**:
```
W 키 → DC Jack(+) → F1 → TVS Anode → LM5175 VIN
DC Jack(-) → GND
```

### 3.3 LM5175PWPR Buck-Boost (12V 출력)

**핀 연결**:

| LM5175 핀 | 연결 |
|-----------|------|
| VIN | 입력 5~24V (Fuse 후단) |
| EN | 100k pull-up to VIN |
| FB | 피드백 저항 분배기 (12V 설정) |
| SW | 인덕터 → 12V 출력 |
| COMP | 보상 네트워크 (RC 직렬) |
| RT | 주파수 설정 저항 (200k → 300kHz) |
| SS | 소프트 스타트 커패시터 (0.1uF) |
| PGND | GND |
| AGND | GND (분리 권장, star 연결) |

**피드백 저항 계산 (12V 출력)**:
```
VOUT = 0.8V × (1 + R1/R2)
12V = 0.8 × (1 + R1/R2)
R1/R2 = 14
→ R1 = 140k, R2 = 10k (또는 R1=143k, R2=10.2k)
```

**인덕터**: XAL6060-472MEB (4.7uH, 고전류) 심볼 배치

**출력 커패시터**: 22uF x 2 + 100nF

**Net Label**:
- LM5175 출력 노드에 `VCC_12V` Net Label 추가
- `P` 단축키로 Net Label 도구 선택 후 클릭

### 3.4 XL4005 DC-DC (12V → 5V)

**핀 연결**:

| XL4005 핀 | 연결 |
|-----------|------|
| VIN | VCC_12V |
| EN | 100k pull-up to VIN |
| FB | 피드백 (5V 설정) |
| SW | 인덕터 (10uH) → 5V 출력 |
| GND | GND |

**출력**: `VCC_5V` Net Label

### 3.5 LDO — 3.3V 생성 (AZ1117H-3.3TRG1)

| 핀 | 연결 |
|----|------|
| IN | VCC_5V |
| OUT | VCC_3V3 (Net Label) |
| GND | GND |
| 출력 캡 | 10uF + 100nF (OUT-GND) |

### 3.6 LDO — 5V USB (IL1117-5.0ET)

| 핀 | 연결 |
|----|------|
| IN | VUSB (USB 5V) |
| OUT | VCC_5V_USB (Net Label) |
| GND | GND |

### 3.7 전원 플래그 심볼 연결

**EasyEDA Power Ports** (상단 도구 모음):
- **GND**: `P` → Port 탭 → GND 선택 → 배치
- **VCC**: `P` → Port 탭 → VCC 선택 → 배치 (전압 레벨 설정 필요)
- 또는 Net Label로 직접 연결

> **Tip**: Power Port와 Net Label 둘 다 사용 가능. Net Label이 가독성이 좋습니다.

---

## Step 4: MCU STM32F746 주변회로 (1h 30min)

### 4.1 STM32F746ZGT6 배치

- 중앙에 큰 MCU 심볼 배치
- Properties 패널에서 **Designator**: `U1` 설정
- 핀 배열 보기: View → Fit All (F)

### 4.2 클록 회로

#### 주 클록: 25MHz (HSE)

| 부품 | 값 | 연결 |
|------|----|------|
| Y1 | 25MHz (SX-32) | OSC_IN(PH0), OSC_OUT(PH1) |
| C1, C2 | 22pF MLCC 0402 | Y1 양단 → GND |
| R1 | 1MΩ | 병렬 (Y1 양단, 발진 안정화) |

**배선**:
```
W 키 → PH0 → Y1 좌측
PH1 → Y1 우측
C1 → Y1 좌측, 반대쪽 GND
C2 → Y1 우측, 반대쪽 GND
```

#### RTC 클록: 32.768kHz (LSE)

| 부품 | 값 | 연결 |
|------|----|------|
| Y2 | 32.768kHz (CM315) | OSC32_IN(PC14), OSC32_OUT(PC15) |
| C3, C4 | 12.5pF MLCC 0402 | Y2 양단 → GND |

### 4.3 리셋 회로

```
VCC_3V3 → [R2: 10k] → NRST (핀 29)
NRST → [Tactile Switch] → GND
```

- 리셋 핀은 기본 HIGH (3.3V), 스위치 누르면 LOW
- 100nF cap (NRST-GND) 노이즈 필터 선택 사항

### 4.4 BOOT 모드

```
BOOT0 (핀 131) → [R3: 10k] → GND (기본: Flash boot)
BOOT0 → 점퍼(선택) → VCC_3V3 (시스템 메모리 boot)
```

- 기본은 10k pull-down: Flash 메모리 부팅
- 점퍼로 3.3V 연결 시 시스템 메모리 부팅 (DFU 모드)

### 4.5 MCU 전원 핀

#### VDDA / VREF+ (아날로그 전원)

```
VCC_3V3 → [Ferrite Bead (BLM18PG471)] → VDDA (핀 12)
VREF+ (핀 13) → VDDA와 함께 연결
VDDA → C5: 10uF + C6: 100nF → GND
```

#### VDD 핀 (디지털 전원)

STM32F746은 여러 VDD 핀 그룹이 있습니다:
- VDD1~VDD4 (핀 19, 48, 74, 100)
- VDD5~VDD11 (핀 6, 28, 42, 64, 80, 94, 118)
- VDD12~VDD14 (핀 132, 140, 144)

**각 VDD 핀마다 100nF bypass cap 필수!**
```
각 VDD → 100nF (0402) → 가장 가까운 GND 핀
VDD 그룹당 하나의 bulk cap (10uF) 추가
```

> **중요**: 바이패스 캡은 **각 VDD 핀마다 1개**, 핀에서 3mm 이내 배치가 원칙입니다. 회로도에서 빠뜨리지 않도록 주의하세요.

#### VCAP 핀

| VCAP 핀 | 연결 |
|---------|------|
| VCAP1 (핀 36) | 2.2uF → GND |
| VCAP2 (핀 41) | 2.2uF → GND |

VCAP는 내부 LDO 출력으로 **반드시** 캡을 연결해야 MCU가 동작합니다.

### 4.6 SWD 디버그 헤더

5핀 헤더 (20010WS-04 또는 별도 SWD 커넥터):

| SWD 핀 | MCU 핀 |
|--------|--------|
| SWDIO | PA13 (핀 108) |
| SWCLK | PA14 (핀 109) |
| NRST | NRST (핀 29) |
| 3.3V | VCC_3V3 |
| GND | GND |

**연결**:
```
PA13 → SWDIO
PA14 → SWCLK
VCC_3V3 → SWD_VCC (10k 직렬 권장)
```

---

## Step 5: 모터 드라이버 + 통신 인터페이스 (1h)

### 5.1 A3906 모터 드라이버 x2

#### M1 (Motor 1) — U5

| A3906 핀 | MCU 연결 | 설명 |
|----------|----------|------|
| IN1 | PB0 (핀 121) | 방향 제어 |
| IN2 | PB1 (핀 122) | 방향 제어 |
| PWM | PA0 (핀 23) | 속도 제어 (PWM) |
| EN | PC0 (핀 46) | Enable (Active High) |
| OUT1, OUT2 | JST 커넥터 (M1 출력) | 모터 연결 |
| VBB | VCC_12V | 모터 전원 |
| VDD | VCC_5V | 로직 전원 |
| GND | GND | |

#### M2 (Motor 2) — U6

| A3906 핀 | MCU 연결 | 설명 |
|----------|----------|------|
| IN1 | PB2 (핀 123) | 방향 제어 |
| IN2 | PB3 (핀 124) | 방향 제어 |
| PWM | PA1 (핀 24) | 속도 제어 |
| EN | PC1 (핀 47) | Enable |

**출력 커넥터**: 각 모터 출력에 JST B2B-EH-A 또는 핀헤더 연결

**바이패스 캡**:
```
VCC_12V → 10uF + 100nF (각 모터 드라이버 VBB 근처)
VCC_5V → 100nF (VDD 근처)
```

### 5.2 CAN 인터페이스 — TJF1051T/3

| TJF1051 핀 | 연결 | 설명 |
|------------|------|------|
| TXD | PB6 (핀 134) | CAN TX (MCU) |
| RXD | PB7 (핀 135) | CAN RX (MCU) |
| CANH | CANH 커넥터 | CAN High |
| CANL | CANL 커넥터 | CAN Low |
| VCC | VCC_5V | 5V 전원 |
| GND | GND | |
| S | GND (High Speed 모드) | Standby 제어 |

**120Ω 종단 저항**:
```
CANH ── R: 120Ω ── CANL
```
- 버스 양 끝에만 배치 (OpenCR에서는 선택 가능하도록 점퍼 배치)

**Net Label**: CAN_H, CAN_L

### 5.3 RS-485 인터페이스 — MAX3443ECSA+

| MAX3443 핀 | 연결 | 설명 |
|------------|------|------|
| RO | PB11 (핀 137) | Receiver Output |
| DI | PB10 (핀 136) | Driver Input |
| RE | PB12 (핀 140) | Receiver Enable (LOW) |
| DE | PB13 (핀 141) | Driver Enable (HIGH) |
| A | 485A 커넥터 | Non-inverting |
| B | 485B 커넥터 | Inverting |
| VCC | VCC_5V | |
| GND | GND | |

**Net Label**: RS485_A, RS485_B

### 5.4 IMU — ICM-20648

| ICM-20648 핀 | 연결 | 설명 |
|-------------|------|------|
| SDA | PB9 (핀 129) | I2C1 Data |
| SCL | PB8 (핀 128) | I2C1 Clock |
| INT | PE0 (핀 97) | Interrupt 출력 |
| VDD | VCC_3V3 | 메인 전원 |
| VIO | VCC_3V3 | I/O 전원 |
| AD0 | GND (기본) | I2C 주소 LSB |
| GND | GND | |
| REGOUT | 10uF + 100nF → GND | 내부 LDO 출력 |

**I2C Pull-up 저항**:
```
SCL ── R: 4.7k ── VCC_3V3
SDA ── R: 4.7k ── VCC_3V3
```

### 5.5 USB OTG — STMPS2141STR + EMIF

**STMPS2141STR (전원 스위치)**:

| 핀 | 연결 |
|----|------|
| EN | PG0 (핀 101) — USB 전원 Enable |
| FLG | PG1 (핀 102) — Fault 플래그 (OC) |
| IN | VUSB (USB VBUS) |
| OUT | USB_VBUS (커넥터로) |

**EMIF02-USB03F2 (EMI 필터)**:

| 핀 | 연결 |
|----|------|
| D+, D- | USB D+/D- 라인 직렬 |
| VBUS, GND | USB 전원 필터 |

---

## Step 6: 커넥터 + ERC 검증 (1h)

### 6.1 DYNAMIXEL 커넥터

#### TTL DYNAMIXEL (3핀 JST B3B-EH-A) x3

| 핀 | 신호 | 설명 |
|---|------|------|
| 1 | TX | MCU USART TX |
| 2 | RX | MCU USART RX |
| 3 | GND | |

- 커넥터 x3개: 각각 다른 USART 할당
  - USART1: TX(PA9), RX(PA10)
  - USART2: TX(PD5), RX(PD6)
  - USART3: TX(PD8), RX(PD9)

#### RS-485 DYNAMIXEL (4핀 JST B4B-EH-A) x3

| 핀 | 신호 |
|---|------|
| 1 | 485A |
| 2 | 485B |
| 3 | VCC (VCC_12V, 각각 퓨즈/리셋블 퓨즈) |
| 4 | GND |

#### UART/CAN (4핀 20010WS-04) x3

| 핀 | 신호 |
|---|------|
| 1 | TX (또는 CAN_H) |
| 2 | RX (또는 CAN_L) |
| 3 | VCC |
| 4 | GND |

### 6.2 Micro-B USB 커넥터 — ZX62D-B-5P8

| 핀 | 신호 | 연결 |
|---|------|------|
| 1 | VBUS | STMPS2141 OUT → USB_VBUS |
| 2 | D- | EMIF02-USB03F2 D- → MCU PA11(OTG_FS_DM) |
| 3 | D+ | EMIF02-USB03F2 D+ → MCU PA12(OTG_FS_DP) |
| 4 | ID | GND (Host 모드) 또는 NC |
| 5 | GND | GND |

쉴드: GND (0Ω 저항 또는 ferrite bead 통해)

### 6.3 Net Label 일관성 검토

회로도 전체에서 Net Label이 일관적인지 확인:

| Net Label | 전압 | 사용처 |
|-----------|------|--------|
| VCC_12V | 12V | LM5175 출력, XL4005 입력, A3906 VBB |
| VCC_5V | 5V | XL4005 출력, TJF1051, MAX3443 |
| VCC_3V3 | 3.3V | AZ1117H 출력, MCU, IMU |
| VUSB | 5V (USB) | USB VBUS, IL1117-5.0 입력 |
| GND | 0V | 전체 공통 |
| AGND | 0V (아날로그) | VDDA, VREF+ (GND와 ferrite bead/starnetwork) |

### 6.4 Electrical Rule Check (ERC)

**실행**:
```
메뉴: Design → Electrical Rule Check (단축키: Shift + E)
```

**ERC 검사 항목**:
- ✅ Floating nets (연결 안 된 네트)
- ✅ Short circuits (단락)
- ✅ Unconnected pins
- ✅ Unconnected wires
- ✅ Bus connection errors

**ERC 결과 해석**:
| 상태 | 색상 | 대응 |
|------|------|------|
| Error | 빨간색 ❌ | 반드시 수정 |
| Warning | 노란색 ⚠ | 확인 후 무시 가능 (NC 핀 등) |

**주의사항**:
- NC(No Connect) 핀은 Properties에서 Electrical Type = "Not Connected" 설정
- Power 핀은 반드시 Power Port로 연결
- GND 연결이 빠진 부품 없는지 확인

### 6.5 어노테이션 (참조번호 자동 할당)

```
Tools → Annotation → Re-annotate
→ All parts → OK
```

- R1, R2 ... R99 / C1, C2 ... C99 / U1, U2 ... 등의 참조번호 자동 정리
- 수동으로 할당한 것과 충돌나면 다시 실행

### 6.6 최종 검토 체크리스트

- [ ] 모든 부품이 배치되었는가?
- [ ] VDD/VCC/GND 연결이 빠진 핀은 없는가?
- [ ] 바이패스 캡이 모든 VDD 핀에 있는가?
- [ ] VCAP1, VCAP2에 2.2uF 연결되었는가?
- [ ] 크리스탈 부하 캡 값이 올바른가? (25MHz → 22pF, 32.768kHz → 12.5pF)
- [ ] ERC에 Error가 없는가?
- [ ] Net Label 이름이 일관적인가?
- [ ] 모든 부품에 Designator가 할당되었는가?

---

**Day 1 완료!** 이제 회로도 작성이 끝났습니다. `Ctrl + S` 저장 후 Day 2로 넘어갑니다.

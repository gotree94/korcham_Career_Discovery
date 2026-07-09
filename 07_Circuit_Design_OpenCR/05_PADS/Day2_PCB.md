# Day 2 — PADS Layout + PADS Router PCB 설계 (7h)

> OpenCR PCB를 PADS Layout으로 4층 기판 설계, PADS Router로 고속 배선, Gerber 출력까지

---

## Step 7: PCB 설정 및 풋프린트 (1h 30min)

### 7.1 PADS Layout 실행

```
Start → Siemens EDA → PADS Layout
또는 PADS Logic에서 Tools → PADS Layout 연동
```

### 7.2 Netlist 가져오기

PADS Logic에서 작성한 회로도를 PADS Layout으로 전송한다.

```
PADS Logic 메뉴:
  Tools → PADS Layout → Link → Send Netlist

또는:
1. PADS Logic: File → Export → "OpenCR_REVH.asc" (ASCII Netlist)
2. PADS Layout: File → Import → OpenCR_REVH.asc
```

### 7.3 레이어 스택 설정

```
Setup → Layer Definition

Layer Stack (4층):
┌─────────┬──────────────────┬──────────┐
│ Layer   │ Type             │ Thickness│
├─────────┼──────────────────┼──────────┤
│ 1 (Top) │ Signal/Plane     │ 1oz (35μm) │
│ 2 (GND) │ Plane (GND)      │ 1oz      │
│ 3 (PWR) │ Plane (Split)    │ 1oz      │
│ 4 (Bot) │ Signal/Plane     │ 1oz      │
└─────────┴──────────────────┴──────────┘
Total thickness: 1.6mm
Prepreg: 0.2mm (Top-GND, Bot-PWR)
Core: 0.5mm (GND-PWR)

설정:
1. Layer 1: Name = "Top" → Electrical Layer
2. Layer 2: Name = "GND" → Plane Layer → Net: GND
3. Layer 3: Name = "PWR" → Plane Layer → Net: (Split)
4. Layer 4: Name = "Bottom" → Electrical Layer
5. Thickness: Tools → Stackup → Enter values
```

### 7.4 Design Rules 설정

```
Setup → Design Rules → Default Rules

Clearance:
  Trace to Trace: 0.15mm (5.9mil)
  Trace to Pad: 0.15mm
  Pad to Pad: 0.15mm
  Trace to Via: 0.15mm
  Via to Via: 0.15mm

Routing:
  Default Trace Width: 0.2mm (8mil)
  Minimum Trace Width: 0.15mm
  Via Diameter: 0.5mm (20mil)
  Via Hole: 0.25mm (10mil)
  Microvia: off
```

### 7.5 보드 아웃라인 생성

```
Drafting Toolbar → Board Outline (또는 2D Line)

1. Grid: 1mm (Setup → Design Grid)
2. 2D Line 도구 → Rectangle 모드
3. 시작점: (0, 0)
4. 끝점: (105mm, 75mm) → 정확한 좌표 입력

장착 홀 (4곳, 모서리):
  1. 각 모서리에서 5mm 안쪽에 배치
  2. Drafting → Hole → Φ3.2mm
  3. 좌표: (5,5), (100,5), (5,70), (100,70)
```

### 7.6 풋프린트 매핑 확인

```
Tools → Library Manager → Parts
→ 각 Part Type에 PCB Decal이 올바르게 연결되었는지 확인

주요 풋프린트 검증:
  STM32F746ZGT6 → LQFP-144 (0.5mm pitch)
  LM5175PWPR → HTSSOP-28
  0402 R/C → RES0402 / CAP0402
  0603 R/C → RES0603 / CAP0603
  JST B3B-EH-A → JST_EH-3PIN
```

### 7.7 ECO 실행

PADS Layout은 ECO(Engineering Change Order)로 변경사항을 반영한다:

```
Tools → ECO → ECO Options
→ Design Rules, Layer Definition, Netlist 변경 시 자동 반영
```

---

## Step 8: 부품 배치 (Placement) (1h 30min)

### 8.1 부품 배치 기본

```
선택 모드 (Select Mode):
  디자인 도구모음 → Select (Ctrl+E)

부품 이동:
  부품 선택 → 드래그 (Move, Ctrl+E)
  우클릭 → Rotate (Ctrl+R)
  우클릭 → Flip Side (Ctrl+F) → Top/Bottom 전환
```

### 8.2 배치 전략 — Zone 기반

OpenCR 105×75mm 보드의 Zone 배치:

```
┌────────────────────────────────────────────┐
│  [전원부]                         [커넥터] │
│  LM5175 XL4005 LDO              JST x6    │
│  L2 inductor                     RS-485    │
│  bulk caps                       │         │
├────────────────────────────────────────────┤
│  [MCU]                           [모터]    │
│  STM32F746                       A3906 x2  │
│  크리스탈 25MHz+32k             모터출력   │
│  SWD                             │         │
├────────────────────────────────────────────┤
│  [IMU]       [USB]     [CAN]   [UART]     │
│  ICM-20648   Micro-B   TJF1051             │
│              전원스위치                      │
└────────────────────────────────────────────┘
```

### 8.3 Zone별 상세 배치

#### 전원부 (좌측 영역)

```
LM5175PWPR (U4): 좌측 상단 1/4 지점
  L2 (4.7uH): LM5175 SW 핀 바로 옆 (최단 거리)
  C1~C7: LM5175 주변, 각 핀 근처
  R1~R6: LM5175 좌측/하단

XL4005 (U5): LM5175 우측
  L3 (10uH): XL4005 SW 핀 옆
  D1: Schottky diode, XL4005 근처

AZ1117H-3.3 (U23), IL1117-5.0 (U6): 보드 좌측 하단
  bulk caps: 각 LDO 입력/출력 근처
```

#### MCU 영역 (중앙)

```
STM32F746 (U3): 보드 정중앙

Y1 (25MHz): U3 좌측, 트레이스 5mm 이내
  C33, C34: Y1 양쪽, GND via 바로 옆
Y2 (32kHz): U3 하단
  C35: Y2 옆

C17~C32: 각 VDD 핀 2mm 이내 (바이패스 캡)
  각 캡 GND 핀 → GND via (길이 최소)

SW1 (Reset): 보드 가장자리 (사용자 접근)
SW2 (Boot): SW1 옆
J2 (SWD): U3 우측 가장자리
```

#### 모터 드라이버 (우측 영역)

```
A3906 (U7, U14): 보드 우측 상단/중앙
  C38: charge pump cap → U7 근처
  JP1, JP2: 모터 출력 커넥터 → 보드 우측 가장자리
```

#### 커넥터 (가장자리)

```
DYNAMIXEL JST (J6, J8, J25): 보드 상단 가장자리
DYNAMIXEL RS-485 (J15-17): 상단, JST 옆
CAN/UART (J18-20): 보드 하단
USB Micro-B (J1): 보드 하단 중앙
  U21 (STMPS2141): J1 근처
  U17 (EMIF02): J1 D+/D- 라인 근처
```

#### IMU (MCU 근처)

```
ICM-20648 (U16): MCU 우측, 10mm 이내
  R15, R16 (I2C pull-up): U16 옆
```

### 8.4 배치 검증

```
1. View → 3D Preview (단축키: Alt+3)
   → 보드 회전하며 부품 간섭 확인

2. Tools → Verify Design → Placement Check
   → 부품 간 최소 거리 위반 확인
```

### 8.5 배치 완료 후

```
File → Save → "OpenCR_REVH.pcb"
```

---

## Step 9: PCB 배선 — PADS Router (1h 30min)

### 9.1 PADS Router 실행

PADS Layout 내장 라우터:

```
Start → PADS Router
또는 PADS Layout → Tools → PADS Router
```

PADS Router는 고속/차동/밀집 배선에 특화된 별도 애플리케이션이다.

### 9.2 PADS Router 인터페이스

```
1. PADS Layout에서 File → Export → "OpenCR_REVH.asc"
2. PADS Router에서 File → Import → OpenCR_REVH.asc
3. 혹은 PADS Layout에서 Tools → PADS Router → 직접 링크
```

### 9.3 라우팅 전략

PADS Router에서 Layer별 방향 설정:

```
Setup → Layer → Routing Direction
  Top: Vertical (수직 배선)
  Bottom: Horizontal (수평 배선)
  GND: Plane (via stitching 자동)
  PWR: Plane (power split)
```

### 9.4 라우팅 기본 조작

```
Route 도구 (Ctrl+Alt+R):
  - 클릭: track 시작
  - 클릭: 꺾는 점 (corner)
  - 더블클릭: track 종료
  - Shift+클릭: via 추가
  - 우클릭 → Add Via: via 수동 추가
  - 우클릭 → Complete (Ctrl+D): 자동으로 끝까지 배선

Track Width 변경:
  우클릭 → Select Net → Properties → Width 변경
  또는 단축키: 'W' + 숫자 (예: W20 = 20mil)
```

### 9.5 배선 우선순위

#### 1순위: 크리스탈 (25MHz + 32.768kHz)

```
25MHz 트레이스:
  - 길이: 10mm 이내 (MCU 핀 바로 옆)
  - Width: 0.2mm
  - GND guard ring: 크리스탈 주변 GND track (Setup → Guard Ring)
  - Via 금지: 크리스탈 아래 GND via만 허용
  - 동일 레이어: 모든 라인 Top 레이어 유지

32.768kHz 트레이스:
  - 보다 느슨한 제약 (저주파)
  - 길이 20mm 이내
```

#### 2순위: USB D+/D- (Differential Pair)

```
PADS Router 차동 배선:
  Route → Differential Pair → Select Nets
  → D+ (USB_DP), D- (USB_DM) 선택
  → Impedance: 90Ω (Setup → Differential Pair → Impedance)

  Width: 0.3mm
  Gap: 0.2mm (일정 간격 유지)
  Max Length Mismatch: 1mm 이내
  GND reference plane: 연속적인 GND (Layer 2)

  배선 방법:
  1. 두 핀 선택 → Route → Differential Pair
  2. 라우팅 경로 그리기 (동시 배선)
  3. 길이 매칭 확인: Route → Tune → Differential Pair
```

#### 3순위: 전원 트레이스

| 네트워크 | 전류 | Width | 비고 |
|----------|:----:|:-----:|------|
| VCC_12V | 4.5A | 2.0mm (80mil) | LM5175→XL4005 |
| VCC_5V | 4A | 1.5mm (60mil) | XL4005→전체 |
| VCC_3V3 | 800mA | 0.5mm (20mil) | LDO→MCU |
| VUSB | 1.5A | 1.0mm (40mil) | USB→LDO |

```
전원 트레이스 배선:
  - 짧고 두껍게
  - Thermal via: 전원부 아래 GND via 여러 개 (방열)
  - Star topology: 각 부하에 개별 분기
```

#### 4순위: 일반 신호선

```
Width: 0.2mm (8mil)
Via: 0.5mm pad / 0.25mm hole
최대 길이 제한은 없으나, 가능한 짧게
```

### 9.6 Bus 배선

동일한 신호 그룹(데이터 버스)은 병렬 배선:

```
Route → Bus → Select Nets
→ 여러 신호선 선택 → 일괄 배선 시작

예: CAN_H + CAN_L 한 쌍, UART_TX + RX 한 쌍
```

### 9.7 배선 완료 기준

```
Table of Contents:
  Total Nets: XXX
  Routed: XXX (100%)
  Partially Routed: 0
  Unrouted: 0
```

---

## Step 10: DRC + 거버 출력 (1h)

### 10.1 DRC 실행

```
Tools → Verify Design (Ctrl+Alt+V)

Check 항목:
  [x] Clearance (간격 위반)
  [x] Connectivity (연결 안 된 넷)
  [x] High Speed (고속 신호 규칙)
  [x] Plane (Plane 연결 누락)
  [x] Fabrication (제조 관련 규칙)

Run → Error 목록 표시
  → 각 Error 더블클릭 → 해당 위치 이동 → 수정
  → Clear → 재실행 → 0 errors 확인
```

### 10.2 일반 DRC 오류 수정

| 오류 | 원인 | 해결 |
|------|------|------|
| Clearance violation | 트레이스/패드 간격 부족 | 트레이스 이동 또는 Design Rule 완화 |
| Unrouted net | 배선 안 됨 | PADS Router에서 배선 완료 |
| Plane void | Plane 영역 부족 | Plane void area 해제 |
| Junction | T점 납땜불량 | Teardrop 추가 (Tools → Teardrops) |
| Copper pour warning | Pour에 고립 구리 | Remove Island Copper |

### 10.3 Copper Pour

GND Copper Pour를 Top/Bottom 레이어에 추가한다:

```
Drafting → Copper Pour (또는 Coppers)

1. Layer: Top
2. Draw outline: 보드 전체 영역 (장착 홀 제외)
3. Properties → Net: GND
4. Options:
   - Remove Isolated Copper: ON
   - Copper Flood Over Vias: Thermal
   - Copper Flood Over Pads: Thermal (or Direct for high current)
5. OK → Tools → Flood (Ctrl+B) → 모든 Pour 재계산

Bottom Layer에도 동일한 작업 반복

> **주의**: 크리스탈 아래는 Copper pour 제외 (Guard ring)
```

### 10.4 Plane 할당 (Inner Layer)

```
Setup → Layer Definition → Layer 3 (PWR)
→ Assign Net(s): VCC_12V, VCC_5V, VCC_3V3 (Split Plane)

Split Plane:
  Drafting → Split Plane → Layer 3
  → 각 전원 영역을 Polygon으로 분할
  → 각 영역에 Net 할당 (VCC_12V, VCC_5V, VCC_3V3)
```

### 10.5 Gerber 출력

```
File → CAM → CAM Documents → Add

Gerber 설정:
  Document Name: "OpenCR_Top"
  Output Device: Gerber RS274X
  Layer Association: Top (Layer 1)
  → OK

다음 파일들 각각 생성:
┌─────────┬────────────────────────┬──────────────┐
│ 파일명  │ 내용                   │ 레이어       │
├─────────┼────────────────────────┼──────────────┤
│ Top     │ Top Signal + Pad       │ Layer 1      │
│ GND     │ GND Plane              │ Layer 2      │
│ PWR     │ Power Plane            │ Layer 3      │
│ Bottom  │ Bottom Signal + Pad    │ Layer 4      │
│ Silktop │ Top Silkscreen         │ Top Silkscr. │
│ Silkbot │ Bottom Silkscreen      │ Bot Silkscr. │
│ MaskTop │ Top Solder Mask        │ Top Mask     │
│ MaskBot │ Bottom Solder Mask     │ Bot Mask     │
│ Outline │ Board Outline          │ Board Outline│
│ Drills  │ Drill Drawing          │ Drill        │
└─────────┴────────────────────────┴──────────────┘

Preference 설정:
  Format: 2:5 (0.01mm resolution)
  Embedded Apertures: ON
  Excellon Drill: ON
```

### 10.6 NC Drill 파일

```
File → CAM → Add → NC Drill
  Document Name: "OpenCR_Drill"
  Unit: Metric, Format: 2:5
  Excellon Format: ON
  Generate
```

### 10.7 최종 확인

Gerber 파일을 Gerber 뷰어(CAM350, GC-Prevue)로 열어 검증:

```
1. 각 레이어 순서대로 로드
2. Top + Soldermask 정렬 확인
3. Top Silkscreen + Bottom Silkscreen 확인
4. Drill 파일과 레이어 일치 확인
5. Edge.Cuts 올바른지 확인

모든 파일 ZIP 압축:
  "OpenCR_REVH_Gerber.zip"
```

---

## Step 11: 3D 시각화 + 설계 검토 (1h)

### 11.1 3D 뷰

```
PADS Layout → View → 3D Preview (Alt+3)

PADS의 3D 기능:
  - 실시간 3D 렌더링
  - 부품 회전/이동 상태 확인
  - 섀도우/투명도 조절
```

### 11.2 3D 검토 항목

```
1. 부품 간 간섭 확인
   - IC 상호 간격: 최소 1mm
   - 커넥터: 케이블 접근성 확보
   
2. 높이 검토
   - 최대 높이 부품: 커넥터, 인덕터
   - 케이스 장착 시 간섭 없음

3. 열 설계
   - LM5175 주변: 방열 via 확인
   - XL4005: 방열판 패턴 확인
   - 전원부: 공기 순환 경로 확보

4. 조립성 검토
   - 모든 부품이 솔더링 가능한 위치
   - 리플로우 프로필 준수
   - 수동 납땜 부품 접근성
```

### 11.3 PADS 3D STEP 내보내기

```
File → Export → STEP 3D
→ "OpenCR_REVH.step" 저장

용도:
  - 기구 설계 팀과 협업 (FreeCAD 등에서 조립 검증)
  - 케이스/인클로저 설계 참조
  - 열 시뮬레이션 입력
```

### 11.4 설계 검토 체크리스트

| 항목 | 확인 |
|------|:----:|
| 모든 네트워크 배선 완료 | [ ] |
| DRC 오류 0 | [ ] |
| USB Differential Pair 90Ω 적합 | [ ] |
| 크리스탈 트레이스 10mm 이내 | [ ] |
| 각 VDD 핀에 바이패스 캡 배치 | [ ] |
| GND Copper Pour 완료 | [ ] |
| 전원 Split Plane 설정 완료 | [ ] |
| Thermal via 전원부 배치 | [ ] |
| 장착 홀 Φ3.2mm × 4 | [ ] |
| 보드 크기 105×75mm | [ ] |

---

## Step 12: 최종 발표 + 리뷰 (30min)

### 12.1 PADS 설계 산출물 정리

```
OpenCR_PADS_Output/
├── OpenCR_REVH.sch          ← PADS Logic 회로도
├── OpenCR_REVH.pcb          ← PADS Layout PCB
├── OpenCR_REVH_Gerber.zip   ← 거버 파일
│   ├── Top.pho
│   ├── GND.pho
│   ├── PWR.pho
│   ├── Bottom.pho
│   ├── Silktop.pho
│   ├── Silkbot.pho
│   ├── MaskTop.pho
│   ├── MaskBot.pho
│   ├── BoardOutline.pho
│   └── Drills.drl
├── OpenCR_REVH.step         ← 3D STEP 모델
├── OpenCR_REVH_BOM.xls      ← BOM (File → Reports → BOM)
└── OpenCR_REVH_Schematic.pdf ← 회로도 PDF
```

### 12.2 BOM 출력

```
Tools → Reports → Bill of Materials
→ Format: Spreadsheet (.xls)
→ Include: Reference, Part Number, Value, Footprint, Qty
→ Generate
```

### 12.3 설계 리뷰 포인트

```
1. 회로도 설계 리뷰
   - 전원 체인 올바른가 (5-24V → 12V → 5V → 3.3V)
   - MCU 모든 핀 연결 완료
   - 풀업/풀다운 저항 값 검토

2. PCB 설계 리뷰
   - 4층 스택업 적절한가
   - 크리스탈 라우팅 최단 거리
   - USB 차동 임피던스 90Ω
   - 전원 트레이스 전류 용량 충분
   - 열 방출 설계

3. 제조 리뷰
   - 거버 파일 정상
   - 최소 트레이스/간격 PCB 제조사 스펙 내
   - 어셈블리 용이성
```

### 12.4 PADS vs 타 EDA 도구 비교

| 항목 | PADS | KiCAD | EasyEDA | OrCAD | Altium |
|------|:----:|:-----:|:-------:|:-----:|:------:|
| 학습 난이도 | ★★☆ | ★★☆ | ★☆☆ | ★★★ | ★★☆ |
| 라이선스 비용 | 중간 | 무료 | 무료 | 높음 | 높음 |
| 아시아 적용 | 중견 | 스타트업 | 중국 | 대기업 | 중견 |
| 라이브러리 품질 | 좋음 | 보통 | LCSC 연동 | 좋음 |非常好 |
| 배선 엔진 | PADS Router | 표준 | 표준 | Allegro | Altium |

### 12.5 팀 발표

```
1. PADS Logic 회로도 설계 경험 (3분)
   - Part Type 생성 방식이 타 EDA와 다른 점
   - 가장 어려웠던 부품과 해결 방법

2. PADS Layout 배선 경험 (2분)
   - PADS Router의 장점/단점
   - Differential pair 배선 경험

3. 종합 소감 (2분)
   - PADS의 특징
   - 다른 EDA 도구와 비교
   - 앞으로 더 배우고 싶은 점
```

### Step 12 체크리스트

- [ ] 모든 설계 산출물이 생성되었다
- [ ] Gerber ZIP이 정상 압축되었다
- [ ] STEP 3D 파일이 정상 생성되었다
- [ ] BOM이 정상 출력되었다
- [ ] 설계 리뷰 체크리스트를 완료했다
- [ ] 팀 발표를 완료했다

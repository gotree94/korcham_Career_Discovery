# Day 2: Allegro PCB Editor PCB 레이아웃 설계 (7h)

## Step 7: Allegro PCB Editor 시작 및 설정 (1h 30min)

### 7.1 Allegro PCB Editor 실행

- Windows **Start → Cadence → Allegro PCB Designer** (또는 **PCB Editor**)
- 실행 시 **Product Selection** 창:
  - **Allegro PCB Designer** (또는 Allegro PCB Design XL) 선택
  - 라이선스 유형 선택

### 7.2 새 Board 생성

```
File → New → Board
```

| 항목 | 설정값 |
|------|--------|
| **Drawing Type** | Board |
| **Board Name** | `OpenCR_Allegro.brd` |
| **Board Template** | `default` (C:\Cadence\SPB_16.6\share\pcb\text\default_board.dlt) |

> **참고:** Template 선택 시 기본 Design Rule, Layer Stack이 적용됨. 필요시 수정.

### 7.3 Layer Stack 설정

```
Setup → Cross Section (또는 부재료: Stack-Up)
```

**OpenCR 4-Layer Stack 설계:**

| Layer | Type | Material | Thickness | Copper Weight |
|-------|------|----------|-----------|---------------|
| **TOP** | Conductor | Copper | 35μm | 1 oz |
| Dielectric | FR-4 | 0.2mm | — |
| **GND** | Plane | Copper | 35μm | 1 oz |
| Dielectric | FR-4 | 1.0mm | — |
| **PWR** | Plane | Copper | 35μm | 1 oz |
| Dielectric | FR-4 | 0.2mm | — |
| **BOTTOM** | Conductor | Copper | 35μm | 1 oz |

**Total Board Thickness:** 약 1.6mm (0.062 inch)

**Plane 설정:**
- **GND Layer:** Negative Plane으로 설정 (Etch 불필요)
  - Subclass: `GND_PLANE`
  - Net 할당: GND
- **PWR Layer:** Negative 또는 Positive Plane
  - Subclass: `PWR_PLANE`
  - 주요 전압: VCC_12V, VCC_5V, VCC_3V3
  - Split Plane으로 분할 필요

### 7.4 Design Constraints 설정

```
Setup → Constraints → Constraint Manager
```

#### Spacing Constraints (간격 규칙):

| 구분 | 최소값 | 설명 |
|------|--------|------|
| Line to Line | 0.15mm | 신호선 간격 |
| Line to Pad | 0.15mm | 선과 패드 간격 |
| Pad to Pad | 0.15mm | 패드 간격 |
| Line to Via | 0.15mm | 선과 Via 간격 |
| Via to Via | 0.2mm | Via 간격 |

#### Physical Constraints (물리 규칙):

| 구분 | 최소 | Default | 설명 |
|------|------|---------|------|
| Line Width | 0.15mm | 0.2mm | 신호선 폭 |
| Line to Line | 0.15mm | 0.2mm | |
| Neck Width | 0.1mm | — | Narrow 허용 구간 |
| Via Pad | 0.5mm | — | Via 외경 |
| Via Hole | 0.25mm | — | Via 내경 (드릴) |

#### 전원선 별도 규칙 (Physical → Custom):

| Net Class | Line Width | 설명 |
|-----------|-----------|------|
| VCC_12V | 2.0mm | 4.5A 전류 대응 |
| VCC_5V | 1.5mm | 4A 전류 대응 |
| VCC_3V3 | 0.5mm | 800mA 전류 대응 |
| DEFAULT | 0.2mm | 일반 신호선 |

> **Constraint Manager 팁:**
> - 왼쪽 트리: **Physical → All Layers** / **Spacing → All Layers**
> - Net Class 생성: Objects → Create → Net Class → Signal
> - Net Class에 Net 할당: Net 목록에서 드래그
> - Differential Pair도 여기서 생성

### 7.5 Board Outline 설정

```
Setup → Outline → Board Outline
```

1. **Command 창**에 `x 0 0` 입력 (원점 설정)
2. **Rectangle** 그리기 모드 → `x 105 75` 입력 (OpenCR 크기)
3. 좌표 기준:
   - 좌하단: (0, 0)
   - 우상단: (105mm, 75mm)

> **단위 설정 확인:** `Setup → Design Parameters → Display` → **User Units = Millimeters**

### 7.6 Mounting Hole 배치

```
Add → Pin
```

| 항목 | 설정값 |
|------|--------|
| **Padstack** | `HOLE3_2mm` (또는 직접 생성) |
| **Number** | 1 |
| **X, Y** | 각 모서리 좌표 |

**Mounting Hole 좌표 (4개):**

| Hole | X | Y |
|------|---|---|
| 1 | 5mm | 5mm |
| 2 | 100mm | 5mm |
| 3 | 5mm | 70mm |
| 4 | 100mm | 70mm |

**Padstack 생성 (필요시):**

```
Setup → Padstack → Padstack Designer
```

- Through hole pad: Top/GND/PWR/Bottom 각 3.2mm
- Drill hole: 3.0mm or 3.2mm
- Soldermask: Top/Bottom 각 4.0mm

### 7.7 Grid 설정

```
Setup → Grids
```

| Grid | Spacing |
|------|---------|
| Non-Etch | 1.0mm |
| All Etch (TOP) | 0.1mm (배선용) |
| All Etch (BOTTOM) | 0.1mm |

---

## Step 8: Netlist Import + 부품 배치 (1h 30min)

### 8.1 Netlist Import 절차

**OrCAD Capture에서 Netlist 생성:**

1. OrCAD Capture로 전환
2. `Tools → Create Netlist`
3. **PCB Editor** 탭:
   - **PCB Footprint:** 체크 (속성 확인)
   - **Create PCB Editor Netlist:** 체크
   - **Netlist File:** `OpenCR_OrCAD.net` (자동 생성)

**Allegro PCB Editor에서 Import:**

```
File → Import → Logic
```

| 항목 | 설정 |
|------|------|
| Import From | **Capture CIS** |
| Place Changed Components | Always |
| Import netlist | 열기 → `OpenCR_OrCAD.net` 선택 |
| Board file | Associate with current board |

- Import 완료 후 **Session Log** 확인:
  - Net 수, Component 수, Error/Warning
  - 오류 시 PCB Footprint 미스매치 확인

> **일반적인 Import 오류:**
> - "Footprint not found": Allegro에 해당 풋프린트 없음 → 경로 확인
> - "Pin mismatch": Symbol pin 수 ≠ PCB footprint pin 수
> - "Net not found": Net 이름 불일치

### 8.2 QuickPlace (초기 배치)

```
Place → QuickPlace
```

| 옵션 | 설정 |
|------|------|
| Placement | All Components |
| Board Outline | Place within board outline |
| Edge | 0.5mm from edge |
| Room | (옵션) Enable |

- QuickPlace 실행: 모든 부품이 Board 내에 자동 배치
- 이후 **수동 배치**로 세부 조정

### 8.3 Room 할당 (효율적 배치)

Room = 부품 그룹을 특정 영역에 할당하는 기능

```
Setup → Room Definition → Create Room
```

| Room Name | 부품 그룹 | 위치 |
|-----------|----------|------|
| ROOM_PWR | U1(LM5175), U2(XL4005), U3(AZ1117), U4(IL1117), L1, L2 | 좌측 영역 |
| ROOM_MCU | U5(STM32F746) | 중앙 |
| ROOM_MOTOR | U6, U7(A3906) | 우측 |
| ROOM_IMU | U8(ICM-20648) | MCU 우측 |
| ROOM_CONN | J1~J10 | 가장자리 |

### 8.4 수동 배치 (Manual Placement)

**기본 배치 단축키:**

| 단축키 | 명령 | 설명 |
|--------|------|------|
| **F2** | Move | 부품 이동 |
| **F3** | Rotate | 부품 회전 |
| **F4** | Mirror | 부품 미러 (BOTTOM 이동) |
| **Alt+F5** | Mirror (Reflect) | 부품 반전 |

**배치 순서:**

1. **전원부 (좌측)** — 가장 먼저 배치
   - LM5175PWPR (U1): 좌측 상단
   - XL4005 (U2): LM5175 우측
   - AZ1117H-3.3 (U3): XL4005 하단
   - IL1117-5.0 (U4): 좌측 하단
   - Inductor L1, L2: 각 DC-DC 가까이
   - Capacitors: 각 IC 주변 (최대한 근접)

2. **MCU (중앙)**
   - STM32F746ZGT6 (U5): 보드 중앙
   - Crystal Y1(25MHz): MCU 좌측 (5mm 이내)
   - Crystal Y2(32.768kHz): MCU 좌측 하단
   - Decoupling caps: 각 VDD 핀 주변 (반경 3mm)
   - Reset/Boot buttons: MCU 하단

3. **모터 드라이버 (우측)**
   - A3906 x2 (U6, U7): 우측 영역
   - 모터 커넥터: 가장 우측 가장자리

4. **IMU (MCU 우측 근접)**
   - ICM-20648 (U8): MCU 우측 5mm 이내
   - I2C pull-up 저항: IMU 가까이

5. **통신 IC**
   - MAX3443ECSA+ (U9, RS-485): 상단
   - TJF1051T/3 (U10, CAN): 우측

6. **커넥터 (가장자리)**
   - B3B-EH-A (J3~J5): 상단 (DYNAMIXEL)
   - B4B-EH-A (J6): 상단 (RS-485)
   - 20010WS-04 (J7): 우측 (CAN)
   - ZX62D-B-5P8 (J10): 하단 (USB)
   - SWD Header (J2): 좌측 하단

### 8.5 배치 검증

- **Show Element (F5)**: 부품 좌표 확인
- **Place → Autoplace**: 참고용 (수동 배치 권장)
- **Highlight Net (F6)**: 특정 Net 강조 표시
- **Dehighlight (Shift+F7)**: 강조 해제

**배치 완료 후 확인 사항:**

- [ ] 전원부 인덕터/커패시터가 IC에 근접했는가?
- [ ] 크리스탈이 MCU에 5mm 이내인가?
- [ ] IMU가 MCU에 근접 (I2C 라인 단거리) 했는가?
- [ ] 디커플링 캡이 각 VDD 핀 근처에 있는가?
- [ ] 모든 커넥터가 보드 가장자리에 정렬되었는가?
- [ ] 부품 간 간섭(overlap)이 없는가?

### 8.6 Place Replicate (반복 배치)

동일한 부품 블록 복사:

```
Place → Replicate
```

- A3906 QFN-20 드라이버 회로 복사에 활용
- 배선까지 함께 복사 가능 (Template 기반)

---

## Step 9: PCB 배선 (Routing) (1h 30min)

### 9.1 라우팅 전략 (4-Layer OpenCR)

| Layer | 용도 | 방향 | 주요 네트 |
|-------|------|------|----------|
| **TOP** | 주요 신호선 | **수직** (Vertical) | GPIO, 통신, 데이터 |
| **GND** | 접지 평면 | Solid Plane | GND |
| **PWR** | 전원 평면 | Split Plane | VCC_12V, 5V, 3V3 |
| **BOTTOM** | 보조 신호선 | **수평** (Horizontal) | 나머지 신호 |

**라우팅 순서:**
1. **Power Net** 우선 (두꺼운 트레이스)
2. **고속 신호** (USB, Crystal)
3. **통신 라인** (I2C, UART, CAN, RS-485)
4. **GPIO/기타 신호**
5. **Copper Pour** (GND/PWR Plane)

### 9.2 Add Connect (단축키 F6)

```
Add Connect (단축키 F6)
```

**기본 조작:**
1. **F6** → 연결할 핀 클릭
2. 마우스 이동 → 트레이스 그려짐 (Gloss On-the-fly)
3. **좌클릭** → Via 삽입
4. **더블클릭** → 라우팅 종료
5. **우클릭** → 옵션 메뉴 (Route Options)

**라우팅 옵션 (Options 탭):**

| 옵션 | 설명 |
|------|------|
| **Act** | Line / Arc / Line & Arc |
| **Line Width** | 현재 Net Class 기본값 |
| **Via** | Via padstack 선택 |
| **Net** | 현재 라우팅 Net 표시 |
| **Bubble** | Shove / Hug only / Off |
| **Snap to Connect Pin** | 체크 |

### 9.3 Power Routing

전원 라인은 전류 용량에 맞게 **트레이스 폭** 설정:

**트레이스 폭 vs 전류 (1oz copper, 10°C 상승):**

| 전류 | 필요 폭 | 사용 Net |
|------|---------|---------|
| 4.5A | 2.0mm | VCC_12V |
| 4A | 1.5mm | VCC_5V |
| 800mA | 0.5mm | VCC_3V3 |
| 200mA | 0.25mm | 기타 전원 |

**Power Routing 방법:**

1. **LM5175 → XL4005 (12V):**
   ```
   LM5175 SW → L1(4.7uH) → C2 → XL4005 VIN
   Width: 2.0mm, multiple via (4~6 vias) for thermal
   ```

2. **XL4005 → AZ1117 (5V → 3.3V):**
   ```
   XL4005 SW → L2 → C5 → AZ1117 IN
   Width: 1.5mm (5V), 0.5mm (3.3V)
   ```

3. **Bypass Capacitor Routing:**
   ```
   각 VDD 핀 → Capacitor pad → GND via
   트레이스 길이 최소화 (3mm 이내)
   Via를 핀 근처에 배치 (return path 최소화)
   ```

### 9.4 Signal Routing

**기본 신호 (UART, I2C, SPI, GPIO):**

| 항목 | 값 |
|------|-----|
| Width | 0.2mm |
| Spacing | 0.15mm 이상 |
| Max Length | 보드 크기 내 자유 |

**I2C (IMU) 라우팅:**

```
PB8(SCL) ── R41(2.2k) ── ICM-20648 SCL
PB9(SDA) ── R42(2.2k) ── ICM-20648 SDA
```

- 길이: 30mm 이하 (MCU ~ IMU 근접)
- GND guard trace 추가 (옆에 GND 트레이스 동반)
- 다른 고속 신호와 이격

**Crystal 라우팅 (25MHz):**

```
MCU OSC_IN ─── C28 ── Y1 ── C29 ── MCU OSC_OUT
```

- **최단 거리** (10mm 이내)
- GND guard ring: 크리스탈 주변 GND 트레이스로 감싸기
- 아래층(GND/PWR)에 다른 신호선 배치 금지
- 크리스탈 바로 아래에 Via 배치 금지
- 각 capacitor → GND via (최단 거리)

**RS-485 / CAN 라우팅:**

```
MAX3443 A ── 120Ω ── MAX3443 B
TJF1051 CANH ── 120Ω ── TJF1051 CANL
```

- 차동 신호는 평행 배선 (parallel)
- 길이 차이 5mm 이내
- GND reference plane 위로 라우팅

### 9.5 Differential Pair Routing (USB)

**USB D+/D- 설정:**

```
Setup → Constraints → Constraint Manager → Electrical → Differential Pair
```

| 항목 | 값 |
|------|-----|
| Net1 | USB_DP (PA12) |
| Net2 | USB_DM (PA11) |
| Width | 0.3mm |
| Spacing (Gap) | 0.2mm |
| Impedance | 90Ω differential |

**라우팅 방법:**

1. **Route → Create Differential Pair**
2. D+ 핀 클릭 → D- 핀 클릭 → 함께 라우팅
3. 자동으로 width/gap 유지

**USB 라우팅 규칙:**
- 길이 차이(mismatch) **2mm 이내**
- ESD 보호 IC (EMIF02-USB03F2)를 커넥터 가까이
- **90° 꺾임 금지** → 45° or Arc
- GND plane 위로만 라우팅 (plane cut 금지)

### 9.6 Gloss — 라인 최적화

```
Route → Gloss → Parameterized Gloss
```

**Gloss 설정:**

| 항목 | 설명 |
|------|------|
| Line Smoothing | 45° bend → Arc 변환 |
| Eliminate 90° | 90° bend 제거 |
| Miters | 모서리 chamfering |
| Line Fattening | 트레이스 폭 조정 |

- Gloss 실행 후 **F5** (Redraw)로 결과 확인
- 필요시 Undo (Ctrl+Z) → 파라미터 재조정

### 9.7 Copper Pour (Shape)

```
Shape → Add Rect (또는 Shape → Add Polygon)
```

**Top Layer GND Copper Pour:**

1. **Add Rect** 실행
2. Board Outline 따라 사각형 그리기
3. **Options 탭:**
   - **Layer:** TOP
   - **Net:** GND
   - **Shape Fill:** Dynamic Copper (또는 Static)
   - **Assign Net:** GND
4. 우클릭 → **Done**

**Thermal Relief 설정:**

```
Setup → Design Parameters → Shape
```

| 항목 | 설정 |
|------|------|
| Dynamic Fill | Smooth |
| Thermal Relief Width | 0.25mm |
| Thermal Relief Gap | 0.15mm |
| Spoke Count | 4 |

> **Thermal Relief:** Copper Pour가 Pad에 직접 연결되지 않고 4개의 spoke로 연결됨 → 납땜 시 열 전달 용이

**PWR Layer Split Plane:**

PWR Layer에 VCC_12V / VCC_5V / VCC_3V3 각각 Shape 배치:

```
Shape → Add Rect (Layer: PWR, Net: VCC_12V) → 영역 지정
Shape → Add Rect (Layer: PWR, Net: VCC_5V) → 영역 지정
Shape → Add Rect (Layer: PWR, Net: VCC_3V3) → 영역 지정
```

- 각 전압 영역이 **물리적으로 분리**되도록 배치
- 영역 간 간격: 0.3mm 이상 (Isolation)
- 변경 시 **Shape → Update Shapes** 실행

---

## Step 10: DRC + 거버 출력 (1h)

### 10.1 Design Rule Check (DRC)

```
Setup → Constraints → DRC
```

**DRC 실행:**

| 옵션 | 설정 |
|------|------|
| Check | All Constraints |
| Online DRC | Enable (실시간) |
| Batch DRC | Run (전체 검사) |
| DRC Browser | Results 표시 |

**DRC Browser:**

- **Display → DRC Browser** (또는 **F9**)
- 위반 사항 목록:
  | 심각도 | 설명 | 조치 |
  |--------|------|------|
  | Error | 선/패드 간격 위반 | 트레이스 이동 |
  | Warning | 권장 규칙 위반 | 필요시 Waive |
  | Clearance | 간격 규칙 위반 | DRC 자동 수정 도구 사용 |
  | Soldermask | 솔더마스크 간격 | 마스크 확장 |

**DRC 위반 해결 도구:**

```
Setup → Constraints → DRC → Waive (오류 무시)
Edit → Delete → DRC Errors (선택 삭제)
Route → Custom Smooth (트레이스 재조정)
```

### 10.2 Z-DRC (Via 불필요 검사)

```
Tools → Database Check → Z-DRC
```

- Update DRC 체크
- **Zero-length via**: 불필요한 via 제거
- **Unconnected via**: 연결 없는 via 확인

### 10.3 Database Check

```
Tools → Database Check
```

| 항목 | 설명 |
|------|------|
| Update Shapes | Dynamic shape 재계산 |
| Check DRC | DRC 다시 실행 |
| Update DRC | DRC 결과 갱신 |
| Purge unused | 미사용 객체 삭제 |

- **OK** → 실행
- 오류 시 Session Log 확인 → 수정 후 재실행

### 10.4 Gerber 파일 출력

```
Manufacture → Artwork
```

#### Film Control 설정:

| Film 이름 | 포함 Layer | Type |
|-----------|-----------|------|
| **TOP** | ETCH/TOP, PIN/TOP, VIA/TOP | Positive |
| **GND** | ETCH/GND, PIN/GND, VIA/GND | Negative (Plane) |
| **PWR** | ETCH/PWR, PIN/PWR, VIA/PWR | Negative (Plane) |
| **BOTTOM** | ETCH/BOTTOM, PIN/BOTTOM, VIA/BOTTOM | Positive |
| **SOLDERT_TOP** | SOLDERMASK/TOP | Positive |
| **SOLDERT_BOTTOM** | SOLDERMASK/BOTTOM | Positive |
| **SILK_TOP** | SILKSCREEN/TOP | Positive |
| **PASTEMASK_TOP** | PASTEMASK/TOP (옵션) | Positive |
| **BOARD_OUTLINE** | BOARD GEOMETRY/OUTLINE | Positive |

**Film 생성 절차:**

1. **Manufacture → Artwork**
2. **Add Film** → Film 이름 입력 (예: TOP)
3. **Select all** → 포함할 Subclass 체크
4. **Film Options:**
   - **Plot mode:** Positive (신호층) / Negative (Plane층)
   - **Mirror:** 체크 안 함
   - **Offset:** 0
   - **Under/Over:** Under
   - **Suppress:** unconnected pads, unused shapes 체크
5. 모든 Film 생성 후 **Create Artwork**

> **참고:** Negative Plane은 GND와 PWR Layer에서 사용. Copper가 없는 영역을 노출. 파일 크기 감소.

#### Gerber 형식 설정:

**Film Options → General Parameters:**

| 항목 | 설정 |
|------|------|
| Format | RS-274X (Extended Gerber) |
| Decimal | 3.5 (Highest) |
| Leading Zero | Suppress |
| Coordinate | Absolute |

### 10.5 NC Drill 생성

```
Manufacture → NC Drill
```

**NC Drill Parameters:**

| 항목 | 설정 |
|------|------|
| File | `OpenCR_Allegro.drl` |
| Format | 3.5 |
| Leading Zero | Suppress |
| Excellon Format | 2 |
| Output Unit | Millimeters |

**NC Legend (드릴 심볼 범례):**

```
Manufacture → NC Drill → NC Legend
```

- Board에 드릴 심볼 표시
- Template: `default-mil.dlt` 또는 `default-mm.dlt`

### 10.6 IPC-356 Netlist 출력

```
Manufacture → IPC-356
```

- Net connectivity test data
- PCB 제조사에서 E-test에 사용

### 10.7 최종 출력 파일 목록

| 파일 | 설명 |
|------|------|
| `*.art` (TOP, GND, PWR, BOTTOM, ...) | Gerber 데이터 |
| `*.drl` | NC Drill 데이터 |
| `*.rou` | Router 데이터 |
| `*.ipc` | IPC-356 Netlist |
| `*.tgz` / `*.zip` | 단일 압축 파일로 제출 |

---

## Step 11: 3D 시각화 + 설계 검토 (1h)

### 11.1 3D View 실행

```
View → 3D View
```

- Allegro PCB 내장 3D 뷰어 실행
- 기본 3D 모델은 Padstack 높이 기반 (단순 블록 형태)
- 마우스 드래그: 회전, 휠: 확대/축소

### 11.2 STEP Model 연동

**STEP Packaging Mapping:**

```
Setup → Step Packaging Mapping
```

1. 각 부품에 실제 3D STEP 모델 할당
2. **Add Mapping:**
   - **PCB Footprint:** LQFP-144
   - **STEP Model:** `STM32F746ZGT6.step` (별도 다운로드)

**STEP 모델 출처:**
- 3D ContentCentral (https://www.3dcontentcentral.com)
- SnapEDA (https://www.snapeda.com)
- Ultra Librarian (https://www.ultralibrarian.com)
- 부품 제조사 웹사이트

**매핑 예시:**

| PCB Footprint | STEP Model 파일 |
|---------------|----------------|
| LQFP-144 | STM32F746ZGT6.step |
| HTSSOP-28 | LM5175PWPR.step |
| QFN-20 | A3906SESTR-T.step |
| SOP-8 | TJF1051T_3.step |
| QFN-24 | ICM-20648.step |

> **TIP:** STEP 모델이 없는 부품은 **Allegro 3D 기본 모델**로 대체 가능.

### 11.3 3D 검토 항목

**회전 검토 (360° 시각화):**

| 검토 항목 | 설명 |
|-----------|------|
| **부품 높이 충돌** | TOP/BOTTOM 부품 간 간섭 확인 |
| **커넥터 접근성** | 케이블 삽입 공간 확보 |
| **조립 간섭** | Mounting hole 주변 부품 확인 |
| **방열** | 전원부 IC 주변 airflow 확보 |

### 11.4 열 방출 검토

**전원부 Thermal Via 추가:**

```
Setup → Thermal → Add Thermal Via
```

- LM5175 PWPR 아래: **6~9개 thermal via** (GND plane 연결)
- XL4005 TO-263 tab: **4개 thermal via**
- 각 LDO: **2~3개 thermal via**

**Thermal Via 규격:**

| 항목 | 값 |
|------|-----|
| Pad Diameter | 0.5mm |
| Hole Diameter | 0.3mm |
| Pitch | 0.8~1.0mm |
| Layer | TOP → GND (→ PWR → BOTTOM 선택) |

### 11.5 신호 무결성 검토

**고속 신호 라인 길이 Matching:**

| 신호 | 길이 | Matching |
|------|------|----------|
| USB D+/D- | < 50mm | 2mm 이내 |
| CAN H/L | < 100mm | 5mm 이내 |
| RS-485 A/B | < 100mm | 5mm 이내 |

**길이 Matching 도구:**

```
Route → Delay Tune (Net 길이 조정)
Route → Phase Tune (위상 조정)
```

**Crystal 신호 무결성:**
- OSC_IN/OUT 길이: 5~15mm (최단)
- GND guard ring 적용
- 크리스탈 아래 다른 신호선 금지

### 11.6 전원 무결성 검토

**Decoupling Capacitor 거리 확인:**
- 100nF 캡: 각 VDD 핀에서 **3mm 이내**
- 10uF 캡: IC 주변 5mm 이내
- GND via: 캡 바로 옆 (loop 면적 최소화)

**전원부 시뮬레이션 (Power Integrity - 옵션):**

```
Analysis → Power Integrity → PDN Analyzer
```

> **참고:** PI 시뮬레이션은 Allegro PCB Designer 고급 라이선스 필요

### 11.7 설계 검토 체크리스트

- [ ] 모든 Net이 라우팅되었는가? (Unrouted Net = 0)
- [ ] GND Copper Pour가 완전히 연결되었는가?
- [ ] Thermal Via가 전원부에 충분한가?
- [ ] USB D+/D- differential pair impendance matching?
- [ ] I2C 라인이 고속 신호에서 분리되었는가?
- [ ] 크리스탈 라인이 최단 거리인가?
- [ ] 모든 DRC 위반이 해결되었는가?
- [ ] Board Outline이 정확한가?
- [ ] Silkscreen이 부품 번호를 가리지 않는가?

---

## Step 12: 최종 발표 + 리뷰 (30min)

### 12.1 OrCAD/Allegro 산출물 정리

**최종 출력 폴더 구조:**

```
OpenCR_OrCAD/
├── Schematic/
│   ├── OpenCR_OrCAD.dsn          # OrCAD 원본 파일
│   ├── OpenCR_OrCAD_Schematic.pdf # PDF 회로도
│   ├── OpenCR_OrCAD_BOM.csv       # BOM 파일
│   └── OpenCR_OrCAD_CrossRef.html # Cross Reference
│
├── PCB/
│   ├── OpenCR_Allegro.brd         # Allegro 원본 파일
│   ├── OpenCR_Allegro_TOP.art     # Gerber (Top)
│   ├── OpenCR_Allegro_GND.art     # Gerber (GND)
│   ├── OpenCR_Allegro_PWR.art     # Gerber (PWR)
│   ├── OpenCR_Allegro_BOTTOM.art  # Gerber (Bottom)
│   ├── OpenCR_Allegro_SOLDERT_TOP.art
│   ├── OpenCR_Allegro_SOLDERT_BOTTOM.art
│   ├── OpenCR_Allegro_SILK_TOP.art
│   ├── OpenCR_Allegro.drl         # NC Drill
│   ├── OpenCR_Allegro.ipc         # IPC-356 Netlist
│   └── OpenCR_Allegro_Placement.txt # Placement Report
│
└── Documentation/
    └── OpenCR_Layout_Report.pdf   # 설계 리뷰 문서
```

### 12.2 GERBER 확인 (Free Viewer)

Gerber 파일 검토는 **무료 Gerber Viewer**로 가능:

- **Gerbv** (오픈소스)
- **GC-Prevue** (Generic, 무료)
- **Altium 365 Viewer** (웹기반)
- **CAM350** (업계 표준, commercial)

### 12.3 원본 OpenCR 설계와 비교

**OpenCR 원본 OrCAD DSN 파일과 설계 비교:**

| 항목 | OpenCR 원본 | 본 과정 결과 | 차이 |
|------|------------|------------|------|
| MCU | STM32F746ZGT6 | 동일 | — |
| Power | LM5175 + XL4005 + LDO | 동일 | — |
| Layout | 105×75mm 4-layer | 동일 | — |
| Connectors | JST, Micro-B 등 | 동일 | — |
| Decoupling | 각 VDD 100nF | 동일 | — |

**차이점 분석:**
- 원본과 같은 부품, 같은 규격으로 설계
- 배치/배선은 설계자에 따라 다를 수 있음 (정답 없음)
- 중요한 것은 **DRC 0, 모든 Net 연결, 전원 무결성**

### 12.4 설계 리뷰 체크리스트

| 번호 | 체크 항목 | 상태 |
|------|-----------|------|
| 1 | Schematic DRC 통과 (0 error) | ☐ |
| 2 | PCB DRC 통과 (0 error) | ☐ |
| 3 | 모든 Net 연결 완료 | ☐ |
| 4 | 전원부 올바른 전압 설정 | ☐ |
| 5 | Decoupling cap 배치 적절 | ☐ |
| 6 | Crystal 라우팅 최단 거리 | ☐ |
| 7 | USB Differential Pair 매칭 | ☐ |
| 8 | GND Copper Pour 연결 완료 | ☐ |
| 9 | Thermal Via 배치 완료 | ☐ |
| 10 | Gerber 파일 생성 완료 | ☐ |
| 11 | BOM 출력 완료 | ☐ |
| 12 | 3D 검토 완료 (간섭 없음) | ☐ |

### 12.5 팀 발표 — OrCAD/Allegro 경험 소감

**발표 주제 (5분 발표):**

1. **설계 목표:** 어떤 보드를 설계했는가? (OpenCR)
2. **구성:** 주요 부품, 전원 구조, 인터페이스
3. **회로도:** OrCAD Capture 경험 — 심볼 생성, DRC
4. **PCB:** Allegro 경험 — 배치 전략, 라우팅, Copper Pour
5. **산출물:** Gerber, BOM, PDF
6. **소감:** 어려웠던 점, 배운 점, 개선할 점

**발표 팁:**
- **불필요한 설명 자제** — 핵심만 발표
- 실제 화면 캡처 활용 (Schematic, PCB, 3D View)
- DRC 오류 해결 경험 공유 (많이 배우는 포인트)

---

## Day 2 핵심 요약

```
1. Allegro PCB Editor 설정 — Layer Stack, Constraint, Board Outline
2. Netlist Import + 부품 배치 — 전원부/MCU/커넥터/IMU
3. Routing — Power(2mm), Signal(0.2mm), USB Diff Pair(90Ω)
4. Copper Pour — GND Solid, PWR Split Plane
5. DRC + Gerber — Batch DRC, Film 생성, NC Drill
6. 3D 검토 — STEP 연동, 간섭 확인, Thermal Via
7. 최종 리뷰 — 산출물 정리, 발표
```

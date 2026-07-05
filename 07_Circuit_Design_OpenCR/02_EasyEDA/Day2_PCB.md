# Day 2: PCB 아트웍 (Layout) — 7시간

> Day 1에서 완성한 회로도를 기반으로 4층 PCB를 설계합니다.

---

## Step 7: PCB 변환 및 레이어 설정 (1h 30min)

### 7.1 Schematic → PCB 변환

```
회로도 탭에서 → Design → Convert to PCB (단축키: Alt + 1)
→ 새 PCB 문서가 생성됨
→ 하단 탭: PCB (PRJ1_PCB) 선택
```

- 모든 부품이 캔버스 우측에 **배치 안 된 상태**로 로드됨
- footprint가 없는 부품은 빨간색 느낌표 표시

### 7.2 풋프린트 확인

**Design → Footprint Manager**:
- 각 부품의 Footprint가 매핑되었는지 확인
- LCSC 부품은 자동 매핑됨
- 매핑 안 된 것은 검색 또는 수동 선택
  - `Search` 버튼으로 EasyEDA 라이브러리에서 풋프린트 검색
  - 같은 핀 수/패키지의 풋프린트 선택

> **자주 누락되는 풋프린트**:
> - 크리스탈 SX-32 → SMD 크리스탈 풋프린트 검색
> - 커넥터 JST 시리즈 → JST 라이브러리에서 선택
> - Tactile switch → 4pin SMD 스위치 풋프린트

### 7.3 Layer Stack 설정

**Design → Layer Stack Manager**:

| Layer | 역할 | 두께 | 비고 |
|-------|------|------|------|
| Top (Signal) | 주요 신호 배선 | 0.035mm (1oz) | 수직 배선 위주 |
| Inner GND | Ground 평면 | 0.035mm | 구리 도금 (Via Stitching) |
| Inner PWR | 전원 분할 | 0.035mm | 12V / 5V / 3.3V 분할 |
| Bottom (Signal) | 보조 신호 배선 | 0.035mm | 수평 배선 위주 |

**보드 두께**: 1.6mm (기본값)

**설정 방법**:
```
Layer Stack Manager 열기
→ 기존 2-layer를 4-layer로 변경
→ "Add Layer" 두 번 클릭
→ Layer 이름: GND (Inner), PWR (Inner)
→ 각 동박 두께: 0.035mm
→ Prepeg: 0.2mm
→ Core: 0.71mm
→ OK
```

### 7.4 Board Outline 설정

**Tools → Set Board Outline → Rectangle**:

| 항목 | 값 |
|------|-----|
| Width | 105mm |
| Height | 75mm |
| X | 0 |
| Y | 0 |

**또는 수동**: Track 도구로 보드 외곽선 그리고 → 모든 Track 선택 → **Tools → Convert to Board Outline**

### 7.5 Design Rules 설정

**Design → Design Rule**:

| 규칙 | 최소값 | 권장값 |
|------|--------|--------|
| Min Clearance | 0.15mm | 0.2mm |
| Min Track Width | 0.15mm | Signal: 0.2mm, Power: 0.5mm |
| Min Via Diameter | 0.4mm | 0.5mm |
| Min Via Hole | 0.2mm | 0.25mm |
| Min Silk Width | 0.15mm | 0.2mm |

**전원 트레이스 규칙 추가**:
- Net Class: `VCC_12V` → Width: 1.5mm
- Net Class: `VCC_5V` → Width: 1.0mm
- Net Class: `VCC_3V3` → Width: 0.5mm

### 7.6 Import Changes

**Design → Import Changes from Schematic**:
```
→ "Import Changes" 버튼
→ 변경 목록 확인 (부품 목록, Net 목록)
→ "Execute" (Apply Changes)
```

팝업 창에서 모든 항목이 **초록색 체크**인지 확인하세요. 빨간색이 있으면 footprint 문제입니다.

---

## Step 8: 부품 배치 (Placement) (1h 30min)

> 배치는 PCB 설계의 **가장 중요한 단계**입니다. 배치가 잘못되면 배선이 어려워지고 성능이 저하됩니다.

### 8.1 장착 홀 배치

4개의 장착 홀 (Φ3.2mm) 모서리 배치:

```
Place → Hole → Diameter: 3.2mm
위치: (5, 5), (100, 5), (5, 70), (100, 70)  (단위: mm)
```

> 보드 가장자리에서 5mm 이상 여백 확보

### 8.2 Zone 배치 계획

```
┌─────────────────────────────────────────────────┐
│  [DYNAMIXEL TTL x3]  [DYNAMIXEL 485 x3]         │  ← 상단: 커넥터
│                                                  │
│  [전원부]            [MCU STM32F746]   [IMU]     │
│  LM5175              LQFP-144         ICM-20648 │
│  XL4005              [크리스탈 25MHz]  [크리스탈]│
│  LDO x2                                        │
│  인덕터                                         │
│                                                  │
│  [A3906 M1]          [A3906 M2]                 │  ← 우측: 모터
│                                                  │
│  [USB] [CAN] [UART]  [SWD]                      │  ← 하단: 커넥터
└─────────────────────────────────────────────────┘
```

### 8.3 순서대로 배치하기

#### 1단계: 전원부 (좌측 하단)

```
LM5175PWPR → 좌측 중앙 (입력부 근처)
인덕터 XAL6060 → LM5175 SW 핀 근처 (3~5mm 이내)
XL4005 → LM5175 우측 (12V 라인 최단)
AZ1117H-3.3 → XL4005 우측 (5V 라인 최단)
IL1117-5.0 → USB VBUS 근처

Bulk Cap: 각 DC-DC 출력 근처
- LM5175 출력: 22uF x 2 → VCC_12V 노드
- XL4005 출력: 22uF → VCC_5V 노드
- AZ1117H 출력: 10uF → VCC_3V3 노드
```

**전원부 배치 팁**:
- 전원 IC는 방열을 위해 주변에 구리 면적 충분히 확보
- 인덕터는 IC에서 가능한 가깝게 (스위칭 노드 루프 최소화)
- 고전류 경로 단축 (12V, 5V)

#### 2단계: MCU (중앙)

```
STM32F746ZGT6 → 보드 중앙
회전(R)하여 핀 1이 좌측 상단 오도록 배치
```

#### 3단계: 크리스탈 (MCU 근처)

```
25MHz 크리스탈 → PH0, PH1 핀 근처 (3~5mm)
22pF 캡 → 크리스탈과 GND 사이 최단 거리
32.768kHz 크리스탈 → PC14, PC15 핀 근처

⚠ 크리스탈은 디지털 신호선(특히 고속)에서 떨어뜨리기
⚠ 크리스탈 아래층(GND)에는 다른 신호선 배치 금지
```

#### 4단계: IMU (MCU 근처)

```
ICM-20648 → MCU I2C 핀(PB8, PB9) 근처
→ INT(PE0) 배선 고려
→ 가능하면 MCU와 IMU 사이 배선 최단
```

#### 5단계: 모터 드라이버 (우측)

```
A3906 x2 → 우측 상단/하단
모터 출력 커넥터 → A3906 바로 옆 (출력 배선 최단)
VCC_12V, VCC_5V 바이패스 캡 → 각 A3906 바로 옆
```

#### 6단계: 커넥터 (상단/하단)

```
상단: JST B3B-EH-A (TTL) x3 → 좌에서 우로
상단: JST B4B-EH-A (485) x3 → TTL 다음
하단: USB Micro-B (ZX62D-B-5P8)
하단: 20010WS-04 (UART/CAN) x3
하단: SWD 헤더
```

### 8.4 바이패스 캡 배치 (중요!)

**규칙**: 각 VDD 핀에서 **3mm 이내**에 100nF 캡 배치

```
Power → GND loop 최소화
Via를 통해 Inner GND로 직접 연결
같은 VDD 그룹은 Bulk cap(10uF) 공유
```

**방법**:
1. MCU의 각 VDD 핀 확인 (데이터시트 참조)
2. 해당 핀 근처에 100nF 0402 캡 배치
3. VDD → Cap → GND 순서로 배선 준비

### 8.5 배치 후 검증

**3D 보기로 확인**:
```
Design → 3D Preview (Shift + 1)
회전(Zoom)하여 부품 간섭 확인
특히 높이가 높은 부품 (인덕터, 전해캡, 커넥터) 확인
```

- 부품 간 거리: 최소 0.5mm 이상
- 커넥터 방향: 케이블 연결에 지장 없는지
- 장착 홀과 부품 간섭 없음

### 8.6 Array 배치 (반복 부품)

같은 부품 여러 개 배치 시:

1. 첫 번째 부품 배치
2. `Ctrl + D` 복제 → 2번째, 3번째 생성
3. 여러 개 선택 후 **Align** 도구로 정렬
   - 우클릭 → Alignment → Distribute Horizontally

---

## Step 9: PCB 배선 (Routing) (1h 30min)

### 9.1 라우팅 전략

| Layer | 역할 | 방향 | 비고 |
|-------|------|------|------|
| **Top Layer** | 주요 신호선 | **수직** (Vertical) | 고속 신호, 전원 |
| **Inner GND** | GND 평면 | Copper Pour | Via Stitching |
| **Inner PWR** | 전원 분할 평면 | Copper Pour 영역 | 12V/5V/3.3V 분할 |
| **Bottom Layer** | 보조 신호선 | **수평** (Horizontal) | 남은 신호 |

**Top/Bottom 직교 배선 원칙**: 신호 간 간섭(Crosstalk) 최소화

### 9.2 라우팅 우선순위

#### 1순위: 크리스탈 배선 (25MHz, 32.768kHz)

```
Track Width: 0.2mm
길이: 최대한 짧게 (5mm 이내)
다른 신호선과 0.5mm 이상 이격
GPIO 바로 아래 배선 금지
크리스탈 주변에 Guard Ring (GND via) 배치
```

**Guard Ring 만드는 법**:
```
크리스탈 주변에 Track으로 GND 루프
Via를 Inner GND에 연결
→ 노이즈 차폐
```

#### 2순위: USB D+/D- (Differential Pair)

```
Track Width: 0.2mm
Pair 간격: 0.2mm (일정하게)
길이 매칭: D+와 D- 길이 차이 1mm 이내
다른 신호와 1mm 이상 이격
Via 사용 자제 (Top layer에서만 배선)
임피던스: 90Ω differential (4층 PCB에서 적절)
```

**Differential Pair 라우팅**:
```
Route → Differential Pair (또는 D+ 먼저, D- 동일하게)
Shift + W → Track Width, Gap 설정
```

#### 3순위: 전원 트레이스

| Net | Track Width | 비고 |
|-----|-------------|------|
| VCC_12V | 1.5~2.0mm | LM5175 출력 → XL4005, A3906 |
| VCC_5V | 1.0~1.5mm | XL4005 출력 → LDO, IC들 |
| VCC_3V3 | 0.5~0.8mm | MCU, IMU, 풀업저항 |
| VUSB | 0.5mm | USB VBUS |

**전원 배선 방법**:
```
Power Net 선택 → 우클릭 → Route → Net
또는 W 키로 수동 배선
중간에 Via → Inner PWR 레이어로
```

#### 4순위: 일반 신호선

| 신호 | Track Width | 비고 |
|------|-------------|------|
| 일반 GPIO | 0.2mm | 대부분 0.2mm로 충분 |
| I2C (SCL, SDA) | 0.25mm | 400kHz, 노이즈 고려 |
| SWD (SWDIO, SWCLK) | 0.3mm | 디버그 신호 |
| CAN (CAN_H, CAN_L) | 0.3mm | 120Ω termination 근처 |
| RS-485 (A, B) | 0.3mm | Differential pair |

### 9.3 라우팅 도구 사용법

**Route Track (W 키) 사용법**:
```
W 키 누르고 시작점 클릭
→ 방향 이동 (클릭으로 꺾기)
→ 우클릭 + Shift: 모드 변경
→ Push mode ON: 기존 트랙 밀어내기 (기본)
```

| 모드 | 단축키 | 설명 |
|------|--------|------|
| Push | Shift + Push | 기존 트랙 밀어내기 |
| Wall | Shift + Wall | 기존 트랙 차단 |
| Hug | Shift + Hug | 기존 트랙 따라가기 |
| Auto | — | 자동 회피 |

**Via 삽입**: 라우팅 중 `Ctrl + LMB` 또는 키보드 `*` (별표)

### 9.4 수동 배선 순서

1. **MCU → 크리스탈** (1순위)
2. **MCU → USB** (D+, D- differential pair)
3. **전원부 배선**: LM5175 → XL4005 → LDO
4. **MCU → 전원** (VDD, VDDA)
5. **MCU → 모터 드라이버** (PB0~PB3, PA0, PA1, PC0, PC1)
6. **MCU → 통신 IC** (CAN, RS-485)
7. **MCU → IMU** (I2C, INT)
8. **MCU → 커넥터** (USART 등)
9. **나머지 신호** (SWD, 리셋, BOOT)

### 9.5 Auto Route (선택 사항)

```
Route → Auto Route
→ 전체 또는 선택 Net 지정
→ Run Auto Route
```

> **교육용**: 먼저 수동 배선을 시도하고, 안 되는 부분만 Auto Route 사용을 권장합니다.
> Auto Route 결과는 항상 검토가 필요합니다.

### 9.6 Copper Pour

**Top/Bottom Layer GND Copper Pour**:
```
Tools → Copper Pour (단축키: Shift + G)
→ Pour 영역: 보드 전체 (Board Outline 내부)
→ Net: GND
→ Clearance: 0.2mm
→ Thermal Relief: via에 적용
```

**Inner PWR Layer 분할 Pour**:
```
PWR Layer 선택
Copper Pour x 3:
  1. VCC_12V 영역 (LM5175 출력 부근)
  2. VCC_5V 영역 (XL4005 출력 부근)
  3. VCC_3V3 영역 (MCU 주변)
각 Pour 여백: 0.3mm 이상 (다른 전압과 분리)
```

**Inner GND Layer Pour**:
```
GND Layer 선택 → 전체 보드 GND Pour
→ Thermal Relief: Via에만 적용
→ Stitching Vias: 10~15mm 간격으로 배치
```

**Via Stitching**:
```
Top GND → Via → Inner GND
Bottom GND → Via → Inner GND
10~15mm 격자로 Via 배치 (Tools → Via Stitching)
```

---

## Step 10: DRC + 거버 출력 (1h)

### 10.1 Design Rule Check (DRC)

```
Design → Design Rule Check (단축키: Shift + D)
→ "Check All Rules" 체크
→ "Run DRC" 버튼
```

**DRC 항목**:

| 항목 | 설명 |
|------|------|
| **Clearance** | 트랙 간 최소 거리 위반 |
| **Track Width** | 설정값보다 가느다란 트랙 |
| **Via Size** | Via 직경/홀 규칙 위반 |
| **Hole Size** | 드릴 홀 규칙 위반 |
| **Unrouted Net** | 배선 안 된 Net |
| **Power Plane** | 전원 평면 연결 문제 |
| **Silk to Pad** | 실크가 패드를 덮는 경우 |

**DRC 결과**:
- **Violation**을 하나씩 더블클릭 → 해당 위치로 이동
- 수정 후 다시 DRC 실행 (반복)
- 최종 DRC에서 Violation 0 목표

### 10.2 일반적인 DRC 오류와 해결

| 오류 | 원인 | 해결 |
|------|------|------|
| Unrouted Net | 배선 빠짐 | Track 도구로 연결 |
| Clearance Violation | 트랙 간 거리 부족 | 트랙 이동 또는 폭 감소 |
| Silk to Pad | 실크가 패드 위에 있음 | 실크 이동 |
| Hole Size Violation | 홀이 너무 큼/작음 | Properties에서 수정 |
| Unconnected Copper | GND Pour 연결 안 됨 | Stitching Via 추가 |

### 10.3 Copper Pour 확인

```
Design → DRC에서 Copper Pour 항목 확인
Orphan Copper: GND Pour에서 고립된 구리 조각
→ Tools → Copper Pour → "Remove Islands" 옵션
```

> **Orphan Copper**는 안테나 역할을 할 수 있으므로 반드시 제거하거나 GND로 연결해야 합니다.

### 10.4 Gerber 파일 출력

**Fabrication → Gerber**:

| 설정 | 값 |
|------|-----|
| Format | **RS-274X** |
| Layers | Top, Bottom, GND, PWR, SilkTop, SilkBottom, MaskTop, MaskBottom, BoardOutline |
| Drill | 포함 |
| Aperture | RS-274X |
| Plot Mode | Positive |
| **Generate** | 버튼 클릭 |

**Gerber 레이어 설명**:

| 레이어 | 내용 |
|--------|------|
| Top | 상단 동박 |
| Bottom | 하단 동박 |
| GND | 내부 GND 레이어 |
| PWR | 내부 전원 레이어 |
| SilkTop | 상단 실크스크린 (부품 번호, 아웃라인) |
| SilkBottom | 하단 실크스크린 |
| MaskTop | 상단 솔더 마스크 (패드 개구부) |
| MaskBottom | 하단 솔더 마스크 |
| BoardOutline | 보드 외곽선 (라우터 가이드) |

**결과**: Gerber ZIP 파일 자동 다운로드

### 10.5 Drill 파일 출력

**Fabrication → Drill**:
```
Format: Excellon
Coordinates: Absolute
Floating Point: 2:4 (2.4 format)
Unit: mm
Generate → ZIP Download
```

### 10.6 BOM 출력

**Fabrication → BOM**:
```
→ CSV Format 선택
→ Include: Part Number, Designator, Value, Package, Manufacturer, Quantity
→ Generate → CSV Download
```

BOM은 부품 구매 리스트로 활용됩니다.

### 10.7 Pick & Place 파일

**Fabrication → Pick Place**:
```
→ CSV Format
→ Coordinates: Mid X, Mid Y
→ Rotation: Absolute
→ Generate → CSV Download
```

Pick & Place는 SMT 기계에 사용되는 XY 좌표 파일입니다.

---

## Step 11: 3D 시각화 + 설계 검토 (1h)

### 11.1 3D 미리보기

**Design → 3D Preview (Shift + 1)**

3D 창에서 가능한 작업:
- **회전**: 좌클릭 드래그
- **확대/축소**: 휠
- **이동**: 우클릭 드래그
- **부품 색상**: 실제 부품과 유사한 색상 자동 렌더링

### 11.2 각도별 스크린샷 저장

```
상단(Top) 뷰 → Ctrl + PrtSc (또는 EasyEDA 내 Screenshot 기능)
하단(Bottom) 뷰 → 회전하여 저장
측면 뷰 → 커넥터 높이 확인
사시도 → 전체적인 입체감 확인
```

**저장**: 각 스크린샷을 PNG로 저장 (설계 포트폴리오용)

### 11.3 검토 항목

#### 부품 배치 검증
- [ ] 부품 간 간섭 없음 (특히 높은 부품)
- [ ] 커넥터 케이블 접근 방향 적절
- [ ] 장착 홀과 부품 간섭 없음
- [ ] 수동 납땜 가능 영역 (100nF 0402 등)

#### 열 관리
- [ ] LM5175 방열 영역 충분 (주변 구리 면적)
- [ ] XL4005 방열 패드 → GND via 연결
- [ ] LDO (AZ1117H, IL1117-5.0) 방열
- [ ] 전원부 주변에 열 방출 경로

#### 신호 무결성
- [ ] 크리스탈 배선 최단 거리
- [ ] USB D+/D- 길이 매칭
- [ ] 전원 트레이스 두께 충분
- [ ] GND via stitching 충분

### 11.4 실제 OpenCR 보드와 비교

**실제 OpenCR 사진/PDF와 비교 검토**:
```
1. 부품 위치 비교 (MCU 위치, 전원부 위치)
2. 커넥터 종류/위치 확인
3. 보드 크기 (105x75mm) 일치 확인
4. 4층 스택 구조 일치 확인
```

차이점 발견 시:
- OpenCR 원본과 다른 설계 결정 이유 파악
- 교육용으로 단순화된 부분 설명

### 11.5 최종 설계 검토 체크리스트

- [ ] DRC Violation 0
- [ ] 모든 Net이 배선됨
- [ ] Copper Pour 연결 확인 (Orphan 없음)
- [ ] BOM에 모든 부품 포함
- [ ] Gerber 파일 정상 생성
- [ ] 3D 모델 정상 표시
- [ ] 보드 크기 105x75mm
- [ ] 장착 홀 4개 배치
- [ ] 실크스크린 오타 없음

---

## Step 12: 최종 발표 + 리뷰 (30min)

### 12.1 EasyEDA 프로젝트 공유

**프로젝트 공개 설정**:
```
Projects 패널 → OpenCR_EasyEDA 우클릭
→ Properties → Public/Private 설정
```

| 옵션 | 설명 |
|------|------|
| **Private** | 나만 볼 수 있음 (무료) |
| **Public** | 모두 볼 수 있음 (EasyEDA 커뮤니티) |
| **Team** | 팀 멤버만 접근 (Team Plan 필요) |

### 12.2 협업 기능 소개

**팀 협업**:
```
상단: File → Team → Create Team
→ 팀원 초대 (이메일)
→ 실시간 공동 편집 가능
→ 댓글(Comment) 기능
→ 버전 히스토리
```

**Comment 활용**:
```
PCB 캔버스에서 → 우클릭 → Add Comment
→ 특정 위치에 피드백 표시
→ @멘션 가능
```

### 12.3 설계 산출물

| 산출물 | 파일 | 설명 |
|--------|------|------|
| **Gerber ZIP** | `Gerber_OpenCR_EasyEDA.zip` | PCB 제조용 (JLCPCB 업로드) |
| **Drill ZIP** | `Drill_OpenCR_EasyEDA.zip` | 드릴 데이터 (Excellon) |
| **BOM CSV** | `BOM_OpenCR_EasyEDA.csv` | 부품 리스트 |
| **Pick Place CSV** | `PickPlace_OpenCR_EasyEDA.csv` | SMT 배치 데이터 |
| **Schematic PDF** | `Schematic_OpenCR_EasyEDA.pdf` | 회로도 출력 |
| **3D STEP** | `OpenCR_EasyEDA.step` | 기계 설계용 3D 모델 |

**Export 방법**:
```
Schematic PDF: Export → PDF
3D STEP: Export → STEP 3D
Schematic PNG: Export → PNG
```

### 12.4 설계 리뷰 체크리스트

**팀별 리뷰 질문**:
1. EasyEDA에서 가장 편리했던 기능은?
2. 가장 어려웠던 부분은?
3. OpenCR 회로 중 이해 안 된 부분은?
4. PCB 배치에서 개선할 점은?
5. 실제 OpenCR과 비교했을 때 차이점은?

### 12.5 팀별 발표 (15min x 2팀)

**발표 내용** (5분 발표 + 10분 토론):
1. **EasyEDA 경험**: 직관성, 단축키, 라이브러리
2. **장점**: 클라우드 저장, 협업, LCSC 연계
3. **단점**: 한국어 지원 부족, 일부 심볼 누락
4. **OpenCR 설계 소감**: 복잡도, 배치 전략, 배선 어려움
5. **질의응답**

### 12.6 과정 마무리

**수료 후 학습 추천**:
- EasyEDA **Routing Tips** 문서 확인
- JLCPCB 주문 프로세스 경험 (실제 제작)
- EasyEDA **Simulation** 기능 (SPICE)
- 고속 신호 (DDR, HDMI) 라우팅 기법
- Altium / KiCad 등 다른 EDA 도구 비교

---

**축하합니다! 🎉 2일 과정을 완료했습니다.**

이제 여러분은 EasyEDA를 사용하여:
- 복잡한 MCU 기반 회로도 작성
- 4층 PCB 배치 및 배선
- 제조용 출력 파일 생성
- 클라우드 EDA 협업

을 할 수 있습니다.

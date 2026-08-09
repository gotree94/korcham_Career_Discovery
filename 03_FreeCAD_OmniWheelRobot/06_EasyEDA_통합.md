# 06. EasyEDA를 통한 PCB 설계 및 3D 통합

이 장에서는 기구부(FreeCAD) 도면을 기준으로 **PCB를 EasyEDA에서 설계**하고,
**PCB의 최종 3D 데이터를 다시 FreeCAD 어셈블리에 통합**하는 전체 흐름을 배웁니다.

---

## 6.1 전체 통합 프로세스

```
┌────────────┐  ①기구 치수  ┌────────────┐  ②실장  ┌────────────┐
│  FreeCAD   │ ───────────► │  EasyEDA   │ ──────► │  PCB 설계   │
│  기구 설계  │  (보드 외형) │  부품 배치  │         │  (배선/패턴) │
└────────────┘              └────────────┘         └────────────┘
                                    │ ③PCB 3D 데이터(STEP)
                                    ▼
                              ┌────────────┐  ④간섭검증
                              │  FreeCAD   │ ◄──────────┐
                              │ 최종 어셈블리│            │
                              └────────────┘            │
                                    │                   │
                                    ▼                   │
                              ┌────────────┐            │
                              │ 3D 검증/도면│ ───────────┘
                              │ STEP/STL   │  (수정 반영)
                              └────────────┘
```

**핵심 흐름**
1. FreeCAD에서 **PCB 외형(보드 실루엣) 치수**를 확정
2. EasyEDA에서 보드 외형을 그대로 그려 **PCB 설계**
3. EasyEDA에서 **3D 모델(STEP)** 생성/내보내기
4. FreeCAD 어셈블리에 **PCB 3D를 배치**하고 간섭 검증
5. 문제 발견 시 EasyEDA로 되돌아가 수정 (양방향 반복)

---

## 6.2 EasyEDA 설치 (간단 안내)

EasyEDA는 웹 기반과 데스크톱 버전이 있습니다.

- 웹: <https://easyeda.com> (회원 가입, 무료)
- 데스크톱: **EasyEDA Pro (Desktop)** 권장 — 큰 프로젝트/오프라인에 적합
- 다운로드: EasyEDA 공식 사이트에서 Windows용 설치

> 💡 본 교재에서는 **EasyEDA Pro (Std)** 기준으로 설명합니다.
> (회로도→PCB→3D 프리뷰→STEP 내보내기)

---

## 6.3 1단계: 기구부에서 PCB 외형 치수 확정 (FreeCAD)

### Step A. PCB 거치 위치 결정
- 05장에서 정한 **스탠드오프 좌표**를 기준으로 PCB 영역을 정의합니다.
- 예: `TOP_PCB` 100(W) × 70(H) mm, 스탠드오프 4곳 (모서리에서 5mm 안쪽)

### Step B. PCB 외형 스케치 추출
1. FreeCAD에서 `TOP_PCB.FCStd` 열기 (없으면 새 스케치)
2. PCB 외곽 스케치를 XY 평면에 작성
   - 모서리 R(라운드), 노치, 컷아웃 포함
3. **스탠드오프 좌표** 기록:
   - 홀 1: (5, 5)
   - 홀 2: (95, 5)
   - 홀 3: (95, 65)
   - 홀 4: (5, 65)
4. 기술 도면 or 치수 표로 정리

### Step C. 전송용 데이터 준비
- **DXF**로 PCB 외형 내보내기 → EasyEDA에서 보드 외형으로 사용

> 💡 실제 보드 외형은 제조사(LT: 라인 두께 등)에 맞춰 살짝 여유를 줍니다.

---

## 6.4 2단계: EasyEDA PCB 설계

### Step A. 프로젝트 생성
- EasyEDA Pro 실행 → **새 프로젝트** → 이름: `OMNI_ROBOT_TOP_PCB`

### Step B. 회로도(Schematic) 작성
- 필요한 소자 배치: MCU, 드라이버, 전원부, 센서 커넥터, Jetson Xavier NX 커넥터 등
- 배선 → 네트 목록 정리

> 💡 기구 실습이 목표이므로 회로 자체보다 **보드 외형/장착부**에 집중하세요.
> (배선은 기존 회로를 참고하거나 간단히 그리면 됩니다.)

### Step C. PCB 레이아웃
1. 회로도 완성 → **PCB 변환(Convert to PCB)**
2. **보드 외형 설정**:
   - 외곽 레이어(Board Outline)에 DXF 불러오기
   - File → Import → DXF (또는 기구에서 준 치수로 직접 그림)
3. 스탠드오프 홀 4곳 배치:
   - 보드 모서리 (5,5) 등 → **홀(MTG hole)** 규격 Ø3.2
4. 소자 배치 및 배선 (가능한 범위 내)

### Step D. 3D 확인
- 메뉴: **View → 3D** (3D 프리뷰)
- 컴포넌트 3D 모델이 보이면 보드 + 부품 형상 확인
- 부품이 보드 바깥으로 튀어나오지 않았는지 확인

---

## 6.5 3단계: PCB 3D 데이터(STEP) 내보내기 (EasyEDA)

### EasyEDA Pro에서 내보내기
1. PCB 편집 상태
2. **File → Export → STEP (3D Model)** 선택
   - 또는 메뉴: **Export → 3D → STEP**
3. 옵션:
   - 3D 모델 포함(컴포넌트 포함) / 보드만
   - 단위 mm 확인
4. 파일명: `OMNI_ROBOT_TOP_PCB.step`

> 💡 EasyEDA 버전에 따라 STEP 내보내기가 없는 경우:
> - **3D 프리뷰 → STL**로 내보낸 후 FreeCAD에서 사용
> - 또는 컴포넌트 3D 모델을 개별 STEP으로 받아 FreeCAD에서 조립

### 결과 파일
- `OMNI_ROBOT_TOP_PCB.step` ← FreeCAD에서 읽어올 파일

---

## 6.6 4단계: FreeCAD 어셈블리에 PCB 3D 통합

### Step A. STEP 가져오기
1. FreeCAD 실행 → **File → Import**
2. `OMNI_ROBOT_TOP_PCB.step` 선택
3. 모델 트리에 PCB가 도형으로 추가됨 (파라메트릭 없음)

> 💡 STEP 가져오기는 기하(Geometry)만 가져오므로 편집은 제한적입니다.
> (원점/축 정렬은 가능, 파라메트릭 피처는 아님)

### Step B. 위치 정렬
- 기구 설계에서 정한 **장착 좌표/높이**로 PCB를 이동/회전:
  - 회전: PCB가 뒤집혀 있다면 Z축 회전 180°
  - 위치: 스탠드오프 중심(5,5,8) 등으로 정렬
- 정렬 도구: **Placement(배치)** 속성에서 Position/Rotation 직접 입력
  - `Position`: X, Y, Z
  - `Rotation`: Yaw/Pitch/Roll (축-각)

### Step C. 어셈블리 추가
- Assembly 워크벤치에서 **Insert Part** → 가져온 PCB를 링크로 추가
- `Fixed`/`Coincident` 결합으로 스탠드오프 위치에 고정

```
Assembly
 ├─ Bottom_Plate1
 ├─ ... (기존 부품)
 ├─ TOP_PCB (링크: OMNI_ROBOT_TOP_PCB.step)
 │   └─ Joint (스탠드오프에 정렬)
 └─ 센서들
```

### Step D. 간섭 검사
- **간섭 검사(Interference)** 실행
- PCB가 다른 부품(배터리, 모터 케이블, LCD)과 겹치는지 확인
- 문제 시 EasyEDA에서 보드 외형/부품 위치 수정 → 다시 STEP → 재통합

---

## 6.7 5단계: 양방향 수정 반복 (통합 워크플로)

```
FreeCAD 기구 ──(보드 외형 DXF)──► EasyEDA PCB
      ▲                               │
      │                               │ (STEP)
      └─────────(간섭 수정 요청)───────▼
      ◄────────────────── FreeCAD 검증
```

| 상황 | 수정 위치 | 방법 |
| ---- | --------- | ---- |
| 보드가 스탠드오프보다 큼 | EasyEDA | 보드 외형 축소 → STEP 재출력 |
| 센서/커넥터가 케이스에 걸림 | EasyEDA | 부품 위치 이동 → 재출력 |
| 모터 홀과 PCB 홀 좌표 불일치 | FreeCAD | 기구부 홀 위치 수정 |
| PCB 두께가 이격 높이보다 큼 | EasyEDA/기구 | 스탠드오프 높이 변경 |

> 💡 반복 횟수를 줄이려면 **기구(간섭) 설계를 먼저 충분히 검증**한 뒤
> PCB 외형을 확정하는 것이 중요합니다.

---

## 6.8 최종 산출물 정리

| 산출물 | 생성 도구 | 용도 |
| ------ | --------- | ---- |
| PCB 회로도 | EasyEDA | 전기 설계 |
| PCB 아트웍(거버/드릴) | EasyEDA | PCB 제조 |
| 보드 외형 DXF | FreeCAD → EasyEDA | PCB 외곽 기준 |
| PCB 3D STEP | EasyEDA | 기구 통합/간섭 검증 |
| 전체 어셈블리 STEP | FreeCAD | 제조/협업 |
| 3D 프리뷰 이미지 | FreeCAD/EasyEDA | 리뷰 |

---

## 6.9 실습: TOP_PCB 통합 완성

### 실습 목표
- 기존 `TOP_PCB.FCStd`를 대체하는 **EasyEDA 설계 PCB**를
  기구 어셈블리에 통합합니다.

### 순서
1. FreeCAD에서 기존 `TOP_PCB` 외형 확인 → 보드 외형 DXF 추출
2. EasyEDA 새 프로젝트 → 보드 외형/스탠드오프 홀 반영
3. 핵심 소자 배치 (배선은 단순화) → 3D 확인
4. STEP 내보내기
5. FreeCAD에 가져오기 → 위치/회전 정렬
6. 어셈블리 간섭 검사 통과 확인
7. 전체 STEP 저장 → 3D 검증

### 성공 기준
- [ ] PCB가 스탠드오프 4곳에 정확히 안착
- [ ] PCB/부품이 기구부와 간섭 없음
- [ ] 케이블/커넥터 여유 공간 확보
- [ ] 전체 어셈블리 STEP 내보내기 성공

---

## 6.10 요약

- **기구(FreeCAD) → PCB(EasyEDA) → 3D 통합(FreeCAD)** 의 양방향 흐름.
- PCB 외형은 기구의 스탠드오프 좌표를 기준으로 확정.
- EasyEDA에서 보드+부품을 STEP으로 내보내 FreeCAD에 통합.
- 위치 정렬 → 간섭 검사 → 문제 시 EasyEDA로 수정 반복.
- 최종 산출물: 회로/거버/보드외형 DXF/PCB STEP/전체 STEP.

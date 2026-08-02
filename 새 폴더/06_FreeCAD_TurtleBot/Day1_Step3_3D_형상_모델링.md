# Day 1 · Step 3 — 3D 형상 만들기: Pad / Pocket / Revolution

**소요시간**: 1h 30min  
**목표**: 2D 스케치를 3D로 만드는 세 가지 핵심 기능(Pad, Pocket, Revolution)을 익히고, 터틀봇 바퀴의 3D 모델을 완성한다.

---

## 1. Pad (돌출) — 스케치 → 3D

2D 스케치를 수직 방향으로 밀어내어 입체를 만든다.

### 사용법

```
1. 스케치 선택 (조합보기 또는 3D 뷰에서)
2. Part Design → Pad 버튼 클릭
3. 대화상자 설정:
   - Length: 돌출할 길이 입력
   - Direction: 기본은 평면에 수직 (Reverse로 반대 방향)
   - Type: Dimension (지정 길이) / Through All (관통) / To Last (다음 면까지)
4. OK
```

### 실습: 2D 바퀴 스케치 → 3D 바퀴

> 이전 Step에서 만든 Φ66mm 원 + Φ6mm 원 스케치를 사용한다.

```
1. 조합보기에서 "Sketch001" (바퀴 스케치) 선택
2. Part Design → Pad
3. Length: "25mm" 입력
4. OK
```

**결과**: 직경 66mm, 폭 25mm의 원통형 바퀴 본체가 생성된다.

![Pad 결과 개념] (← 2D 원이 3D 원통이 된다)

---

## 2. Pocket (포켓/컷) — 구멍 뚫기

Pad와 반대로, 스케치 형상만큼 깎아낸다. 구멍을 뚫거나 홈을 팔 때 사용한다.

### 사용법

```
1. 면(face) 선택 → Create Sketch (선택한 면에 새로운 스케치)
2. 구멍 형상 스케치 (예: Φ6mm 원)
3. 스케치 선택 → Part Design → Pocket
4. 설정:
   - Length: 깊이 (Through All = 관통)
   - Type: Dimension / Through All
5. OK
```

### 실습: 바퀴에 살빼기 홀 추가

바퀴의 무게를 줄이고 그립감을 높이기 위해 원형 홈을 추가한다.

```
1. 바퀴 원통의 윗면 선택 → Create Sketch
2. ⚠ 면을 선택한 상태에서 Sketch 버튼을 누르면 선택한 면이 스케치 평면이 됨
3. Create Circle → 중심 (0,0) → 반지름 25mm
4. Create Circle → 중심 (0,0) → 반지름 28mm
5. (두 원 사이의 영역이 Pocket으로 깎일 영역)
```

> **Tip**: 두 개의 동심원을 그리고 바깥쪽 원과 안쪽 원 사이(링 형상)를 스케치하려면, 바깥쪽 원을 **Construction** 모드로 전환하거나 별도 접근법 사용.
>
> **대안**: 단순히 지름 50mm 원 하나를 그리고 조금 깊이 Pocket (깊이 1~2mm 정도로 폭 파기 느낌)

```
6. 스케치 선택 → Pocket
7. Length: "2mm" 입력
8. OK
```

> 결과: 바퀴 양면에 얇은 홈이 파인 형태

---

## 3. Revolution (회전) — 축 기준 회전

스케치를 회전축을 기준으로 돌려서 원형 대칭 형상을 만든다. 원통, 구, 원뿔 등에 적합하다.

### 사용법

```
1. 스케치 작성 (회전축 선 포함)
2. 스케치 선택 → Part Design → Revolution
3. 설정:
   - Axis: 회전축 선택 (스케치 안의 선 또는 외부 모서리)
   - Angle: 360° (전체 회전)
4. OK
```

### 실습: 터틀봇 타이어 트레드(접지면) 모델링

바퀴 외곽에 끼울 타이어의 단면을 Revolution으로 만들어보자.

```
1. Create Body → 새 Body 생성
2. XZ_Plane 선택 → Create Sketch
3. 타이어 단면 스케치 (폭 25mm의 바퀴 테두리를 감싸는 C자 단면):
   - 사각형: 가로 28mm × 세로 5mm
   - 위치: 바퀴 외곽 가장자리에 맞게 배치
   - (구체적 치수는 Step 4에서 상세히)
4. Revolution → Axis: Z축 (또는 수직선 선택) → Angle: 360°
```

---

## 4. 추가 기능 소개

| 기능 | 설명 | 사용 예 |
|------|------|---------|
| **Fillet** | 모서리 둥글게 | 날카로운 모서리를 R5mm로 부드럽게 |
| **Chamfer** | 모서리 깎기 | 모서리를 45°로 깎음 |
| **Linear Pattern** | 선형 배열 | 나사 구멍 여러 개 균일 간격 배치 |
| **Polar Pattern** | 원형 배열 | 바퀴의 살빼기 홀을 원형으로 배치 |
| **Mirror** | 대칭 복사 | 좌우 대칭 부품을 한 번에 |

---

## 5. 실습 과제 — 기본 형상 연습

### 과제 1: 육각 너트

```
1. XY_Plane → 스케치
2. 정육각형 → 외접원 Φ12mm
3. Pad → 5mm
4. 윗면 → 스케치 → Φ6mm 원 → Pocket → Through All
5. Fillet → 윗면/아랫면 모서리 → R1mm
```

### 과제 2: 와셔

```
1. XY_Plane → 스케치
2. Φ16mm 원 + Φ6mm 원 (동심원)
3. Pad → 2mm
```

> 이 두 과제는 Part Design의 기본기를 다지는 연습이다. 완전 구속(Fully Constrained)을 꼭 확인한다.

---

## 6. 모델 트리 구조 이해

조합보기(Combo View)의 모델 트리는 모든 작업 순서를 기록한다.

```
Unnamed#              ← 파일명
└── Body              ← 부품 (Part Design Body)
    ├── Origin        ← 원점/축/평면 (항상 표시)
    ├── Sketch        ← 2D 스케치
    ├── Pad           ← 3D 돌출
    ├── Sketch001     ← 두 번째 스케치
    └── Pocket        ← 컷 작업
```

> **특징**: 트리에서 항목을 선택/더블클릭하면 해당 작업으로 돌아가 수정할 수 있다. (Parametric Modeling)

---

## ✅ Step 3 완료 체크리스트

- [ ] Pad(돌출) 기능을 사용할 수 있다
- [ ] Pocket(컷) 기능으로 구멍을 뚫을 수 있다
- [ ] Revolution(회전) 기능을 사용할 수 있다
- [ ] Fillet/Chamfer로 모서리를 다듬을 수 있다
- [ ] 모델 트리에서 작업 이력을 확인할 수 있다
- [ ] 육각 너트 + 와셔를 완성했다

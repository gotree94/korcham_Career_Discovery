# Day 2 · Step 7 — A2plus 조립 — 터틀봇 완성

**소요시간**: 2h  
**목표**: Day 1에서 만든 모든 부품을 A2plus 워크벤치로 조립하여 하나의 완전한 터틀봇으로 만든다.

---

## 1. A2plus 워크벤치란?

A2plus는 FreeCAD에서 여러 부품을 조립(Assembly)하기 위한 확장 워크벤치다.

> 부품 간의 상대적 위치를 구속 조건(Constraint)으로 정의하여 실제 조립처럼 결합한다.

| 기능 | 설명 |
|------|------|
| Import Part | 외부 FCStd 파일의 Body를 현재 문서로 불러오기 |
| Add Constraint | 부품 간 결합 조건 추가 (동축, 동일면, 거리 등) |
| Check Interference | 부품 간 간섭(겹침) 확인 |

---

## 2. A2plus 설치

### 방법 1: Addon Manager

```
Tools → Addon Manager → A2plus 검색 → Install
```

### 방법 2: 수동 설치 (인터넷 제한 시)

```
https://github.com/kbwbe/A2plus
→ Code → Download ZIP
→ 압축 해제 → FreeCAD의 Mod 폴더에 복사
```

### A2plus 실행 확인

```
작업대 콤보박스 → "A2plus" 선택
```

---

## 3. 조립 준비

### 3-1: 새 Assembly 문서 생성

```
File → New
File → Save As → "turtlebot_assembly.FCStd"
작업대 → A2plus
```

### 3-2: 부품 불러오기

```
A2plus → Add Part (버튼: 파일 아이콘 + 초록 플러스)

다음 파일들을 순서대로 불러온다:

1. turtlebot_base.FCStd
   → 조합보기에 "Base_Plate" Body가 추가됨

2. turtlebot_wheel.FCStd
   → "Wheel_Body"와 "Tire" Body가 추가됨

3. turtlebot_mounts.FCStd
   → "Motor_Mount_L", "Motor_Mount_R", "Ball_Caster_Bracket" 추가
```

> **팁**: 각 부품은 현재 문서의 별도 Body로 임포트된다.

---

## 4. 조립 구속(Constraint) 종류

| 구속 | 설명 | 사용 예 |
|------|------|---------|
| **planeCoincident** | 두 면을 동일 평면에 맞춤 | 판과 판 결합 |
| **circularEdge** | 두 원형 모서리를 동축으로 정렬 | 축-구멍 결합 |
| **pointOnLine** | 점을 선에 일치 | 정렬 |
| **distance** | 면 사이 거리 지정 | 간격 유지 |

> A2plus 초보자는 **planeCoincident**와 **circularEdge** 두 가지만 알면 80% 조립이 가능하다.

---

## 5. 조립 순서 (순서대로)

### 5-1: 볼 캐스터 브라켓 → 베이스 플레이트

```
[준비]
- Base_Plate 선택 (조합보기에서)
- Ball_Caster_Bracket 선택

[작업]
1. A2plus → planeCoincident
   - Ball_Caster_Bracket 윗면 선택 (①)
   - Base_Plate 윗면 선택 (②)
   - Offset: "0mm" → OK
   (※ 두 면이 같은 높이로 정렬)

2. A2plus → circularEdge
   - Ball_Caster_Bracket 나사 구멍(Φ3mm) 하나 선택 (①)
   - Base_Plate의 대응 캐스터 구멍 선택 (②)
   - OK → 축이 정렬됨

   ※ 나머지 3개 나사 구멍도 동일하게 circularEdge 반복
   ※ 또는 하나만 해도 rotation까지 정렬됨
```

> **참고**: planeCoincident로 z축 위치, circularEdge로 x/y 위치 결정

### 5-2: 모터 마운트 (좌) → 베이스 플레이트

```
[준비]
Motor_Mount_L + Base_Plate 선택

1. planeCoincident
   - Motor_Mount_L 밑면 → Base_Plate 윗면 → Offset: 0

2. circularEdge
   - Motor_Mount_L의 Φ3mm 나사 구멍 하나
   - Base_Plate 좌측 모터 나사 구멍 하나

3. circularEdge (두 번째)
   - Motor_Mount_L의 다른 Φ3mm 구멍
   - Base_Plate 좌측 대응 구멍
```

### 5-3: 모터 마운트 (우) → 베이스 플레이트

좌측과 동일한 방법으로 우측 마운트를 Base_Plate 우측에 조립

### 5-4: 바퀴 + 타이어 (먼저 조립)

```
Tire + Wheel_Body 선택

1. circularEdge
   - Tire 내면 원형 모서리 선택
   - Wheel_Body 외면 원형 모서리 선택
   → 동축 정렬 + 동일 평면
```

### 5-5: 바퀴 어셈블리 → 모터 마운트

```
방금 조립한 Wheel_Body + Motor_Mount_L 선택

1. circularEdge
   - Wheel_Body의 축 구멍(Φ6.2mm 원형 모서리)
   - Motor_Mount_L의 모터 축 통과 구멍(Φ8mm)
   → 동축 정렬

2. distance
   - Wheel_Body 측면
   - Motor_Mount_L 측면
   → Distance: "1mm" (바퀴와 마운트 사이 간격)
```

### 5-6: 우측 바퀴도 동일하게 조립

### 5-7: 전체 조립 확인

```
A2plus → Check Interference

→ "No interference detected" 확인
```

> 간섭(Interference)이 발견되면 빨간색으로 표시된다.
> 간섭이 있을 경우 부품 위치나 치수를 다시 확인한다.

---

## 6. 조립 완료 모델 트리

```
turtlebot_assembly
├── Base_Plate
├── Ball_Caster_Bracket
│   └── Constraints...
├── Motor_Mount_L
│   └── Constraints...
├── Motor_Mount_R
│   └── Constraints...
├── Wheel_Body (x2)
│   └── Constraints...
├── Tire (x2)
│   └── Constraints...
└── Constraints (전체 목록)
    ├── planeCoincident001
    ├── circularEdge001
    ├── circularEdge002
    └── ...
```

---

## 7. 간섭 체크 + 수정

### 간섭이 발생했다면?

| 문제 | 원인 | 해결 |
|------|------|------|
| 구멍 크기 불일치 | 치수 오차 | 스케치 편집 → 구멍 지름 수정 |
| 부품 위치 충돌 | 조립 순서 오류 | 순서 변경 또는 다른 구속으로 재시도 |
| 부품이 안 보임 | 가시성 꺼짐 | 조합보기에서 Body 선택 → Spacebar로 전환 |

### 간섭 없는 조립이 완료되면

```
File → Save
File → Export → STEP → "turtlebot_assembly.step"
```

> STEP 파일은 다른 CAD 프로그램에서도 열 수 있는 표준 교환 형식이다.

---

## 8. 마무리 — 완성된 터틀봇 확인

3D 뷰를 회전하면서 완성된 터틀봇을 확인한다.

```
- 마우스 가운데 버튼으로 회전
- Ctrl + 휠로 확대/축소
- 각 부품이 정확히 조립되었는지 육안 확인
```

### 터틀봇 조립 완성도 체크

```
위에서 본 모습:
          ┌─────────────┐
          │  ⚽캐스터    │
          │    ↑        │
     ┌────┴────┴────┴────┐
     │    ↻     ↺        │
     │  ⬛모터  ⬛모터    │
     │   ┌──────┐        │
     │   │배선홀│        │
     │   └──────┘        │
     └───────────────────┘

옆에서 본 모습:
    ╭──────────╮
    │ 베이스   │ ═══ Base_Plate
    │ 플레이트 │
    ╰─┬──────┬─╯
      │ 바퀴 │      ═══ Wheel + Tire
      └──────┘
```

---

## ✅ Step 7 완료 체크리스트

- [ ] A2plus 워크벤치가 설치되었다
- [ ] 모든 부품을 Assembly 문서에 불러왔다
- [ ] planeCoincident로 면 정렬을 완료했다
- [ ] circularEdge로 축 정렬을 완료했다
- [ ] 좌/우 바퀴가 정확히 조립되었다
- [ ] 간섭(Interference)이 0이다
- [ ] STEP 파일로 내보냈다

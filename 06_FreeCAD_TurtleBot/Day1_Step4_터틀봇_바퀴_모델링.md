# Day 1 · Step 4 — 터틀봇 바퀴 + 타이어 모델링

**소요시간**: 1h  
**목표**: 터틀봇 구동바퀴와 타이어를 실제 치수에 맞게 모델링하고, 조립을 고려한 설계를 경험한다.

---

## 1. 터틀봇 바퀴 사양

TurtleBot3 Burger 기준 구동바퀴:

| 항목 | 값 |
|------|-----|
| 바퀴 직경 (외경) | 66mm |
| 바퀴 폭 | 25mm |
| 축 구멍 직경 | 6mm (N20 모터 축 기준) |
| 타이어 두께 | 3mm |
| 재질 (휠) | PLA 또는 ABS (3D프린터 출력) |
| 재질 (타이어) | TPU (필렌트) 또는 고무링 |

> ⚠ 조립 간격을 위해 축 구멍은 **Φ6.2mm**로 여유를 준다.

---

## 2. 바퀴 본체 모델링

### Step 2-1: 새 문서 + Body 생성

```
1. File → New
2. 작업대 → Part Design
3. 조합보기에서 Body 선택 or Create Body 버튼
   (없으면 Part Design → Create Body)
4. Body 이름: "Wheel_Body" (우클릭 → Rename)
```

### Step 2-2: 바퀴 스케치 (XY_Plane)

```
XY_Plane 선택 → Create Sketch

1. Create Circle → 중심 (0,0) → 지름 66mm
   → 원 선택 → Distance → "33mm" (반지름)
2. Create Circle → 중심 (0,0) → 지름 6.2mm (축 구멍 여유)
   → 원 선택 → Distance → "3.1mm" (반지름)

→ ✅ Fully constrained 확인
```

### Step 2-3: Pad (돌출)

```
Pad → Length: "25mm" → OK
```

### Step 2-4: 살빼기 (경량화)

바퀴 무게를 줄이기 위해 양쪽 면을 파낸다.

```
1. 바퀴 윗면 선택 → Create Sketch
2. Create Circle → 중심 (0,0) → 지름 50mm
   → Distance → "25mm" (반지름)
3. Pad → 로 돌출하지 말고 → **Pocket** 사용
4. Pocket → Length: "3mm" → Type: Dimension → OK

→ "바퀴 양면에 3mm 깊이의 홈" 완성
```

> **심화**: 대칭 작업으로 반대쪽 면도 똑같이 Pocket 하려면?
> `Mirror` 기능 또는 동일 작업 반복. (Pocket Feature 선택 → Mirror → YZ_Plane)

### Step 2-5: 모서리 Fillet

바퀴 날카로운 모서리를 둥글게 처리한다.

```
1. 바퀴 외곽 상단 모서리 선택 (3D 뷰에서 클릭)
2. Part Design → Fillet
3. Radius: "2mm"
4. 하단 모서리도 동일하게 Fillet
```

---

## 3. 타이어 모델링 (별도 Body)

타이어는 바퀴 외곽에 끼울 고무 링 형태다. 별도의 Body로 만든다.

### Step 3-1: 새 Body 생성

```
Create Body → 이름: "Tire"
```

### Step 3-2: Revolution으로 타이어 만들기

```
1. XZ_Plane 선택 → Create Sketch
2. 타이어 단면 스케치:

   좌표 기준 단면 (바퀴 폭 25mm 기준):
   ┌─────────────────────────────┐
   │            바퀴              │  ← Y축 위쪽
   │    ┌─────────────────┐      │
   │    │   타이어         │      │
   │    │  ┌───┐          │      │
   │    │  │   │ 트레드   │      │
   │    │  └───┘          │      │
   │    └─────────────────┘      │
   │                             │
   └─────────────────────────────┘

   실제 스케치:
   - 바퀴 외경 Φ66mm → 반지름 33mm
   - 타이어는 바퀴 외곽을 감싸므로:
     * 바깥 반지름: 36mm (타이어 포함 전체)
     * 타이어 두께(방사방향): 3mm
     * 타이어 폭: 27mm (바퀴 폭 25mm보다 양쪽 1mm씩 돌출)

3. 사각형 도구로 다음 좌표의 점 4개 연결:
   (33, -12.5) → (36, -12.5) → (36, 12.5) → (33, 12.5)
   
4. 또는: Create Rectangle → 첫 점 (33, -12.5) → 반대 점 (36, 12.5)

5. 닫힌 사각형 확인
```

> **중요**: 스케치가 Z축(수직) 기준으로 회전되도록 배치한다.
> Z축이 회전축이 되어 원형으로 회전된다.

```
6. Revolution 선택
7. Axis: Z축 선택 (스케치 원점의 수직선)
8. Angle: 360° → OK
```

### Step 3-3: 타이어 트레드(미끄럼 방지 홈)

선택 사항 — 타이어 외면에 간단한 홈을 추가한다.

```
1. 타이어의 Cylindrical 외면 선택 → Create Sketch
2. 작은 사각형 (가로 2mm × 세로 1mm) 하나 스케치
3. Pocket → Through All (또는 깊이 1mm)
4. Polar Pattern → Pocket 선택 → Count: 12 (12개 원형 배열)
```

---

## 4. 완성 확인

| 항목 | 값 |
|------|-----|
| Wheel Body 반지름 | 33mm (Φ66mm) |
| Wheel Body 폭 | 25mm |
| 축 구멍 | Φ6.2mm |
| 타이어 외경 | Φ72mm (바퀴+타이어) |
| 타이어 폭 | 27mm |

---

## 5. 파일 저장

```
Ctrl+S → 파일명: "turtlebot_wheel.FCStd"
```

> FCStd는 FreeCAD의 기본 파일 형식이다. 하나의 파일에 여러 Body를 저장할 수 있다.

---

## ✅ Step 4 완료 체크리스트

- [ ] 바퀴 본체(Wheel Body)를 완전 구속 스케치로 모델링했다
- [ ] 축 구멍(Φ6.2mm)이 중앙에 정확히 위치했다
- [ ] 살빼기 홈(Pocket)이 양쪽에 적용되었다
- [ ] 타이어(Tire)가 Revolution으로 생성되었다
- [ ] 파일을 저장했다 (turtlebot_wheel.FCStd)

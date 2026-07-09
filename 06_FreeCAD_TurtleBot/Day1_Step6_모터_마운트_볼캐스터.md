# Day 1 · Step 6 — 모터 마운트 + 볼 캐스터 브라켓

**소요시간**: 1h  
**목표**: N20 모터를 베이스 플레이트에 고정할 마운트와, 볼 캐스터 브라켓을 설계한다.

---

## 1. N20 모터 사양

N20 마이크로 DC 모터 (모터 드라이버 내장 또는 미포함 — 규격 위주)

| 항목 | 값 |
|------|-----|
| 본체 크기 | 37mm × 15mm × 12mm |
| 출력축 직경 | Φ6mm |
| 출력축 길이 | ~12mm |
| 장착 플랜지 | 4구, 나사 간격 26mm × 15mm |
| 장착 나사 | M2 (Φ2mm 구멍) |

> N20 모터는 다양한 감속비가 있으며, 터틀봇에는 보통 30:1 ~ 50:1 사용

---

## 2. 모터 마운트 (Motor Mount) 설계

모터 마운트는 베이스 플레이트 위에 모터를 고정하고, 바퀴 축이 베이스 아래로 나오도록 하는 브라켓이다.

### 2-1: 새 Body 생성

```
Create Body → 이름: "Motor_Mount_L" (좌측용)
```

### 2-2: 모터 플랜지 스케치 (XY_Plane)

```
XY_Plane → Create Sketch

1. Create Rectangle → 중심이 원점에 오도록:
   - 첫 점: (-18.5, -7.5)
   - 반대 점: (18.5, 7.5)
   → 가로 37mm, 세로 15mm

2. 구속 조건:
   - 가로변 → Distance: "37mm"
   - 세로변 → Distance: "15mm"
   - 사각형 중심과 원점 → Coincident (또는 Symmetric 구속)

3. 모서리 → Fillet → R3mm (4군데)

4. 모터 나사 구멍 (M2, Φ2mm):
   - Create Circle → 위치: (±13, ±7.5) → 반지름 "1mm"
   🔹 실제 N20 플랜지 나사 간격: 가로 26mm, 세로 15mm
   - 4개 원 모두 추가

5. 모터 축 통과 구멍:
   - Create Circle → 중심 (0,0) → 반지름 "4mm" (Φ8mm 여유)
```

### 2-3: Pad

```
Pad → Length: "5mm" (모터 본체 두께 12mm 중 일부)
```

### 2-4: 장착 날개 (베이스 플레이트 고정용)

```
1. 마운트 상단면 선택 → Create Sketch
2. 양쪽으로 날개 추가:
   - 사각형: (-25, -10) → (25, 10) 형태로 확장
   - 또는 기준 스케치에서 바로 포함

3. 날개 부분에 Φ3mm 구멍 (M3 볼트용):
   - 위치: (±22, 0) — 베이스 플레이트 나사 홀과 일치
   - 반지름 "1.5mm"

4. Pocket → Through All
```

### 2-5: 모터 본체 수납 공간

모터의 하단부가 마운트 속에 들어가도록 Pocket

```
1. 마운트 밑면 선택 → Create Sketch
2. Rectangle: 37mm × 12mm (모터 본체 형상)
3. Pocket → Depth: "7mm" (모터가 들어갈 공간)
```

---

## 3. 우측 모터 마운트 (Mirror)

```
1. 조합보기에서 "Motor_Mount_L" (Body) 선택
2. Part Design → Mirror
3. Mirror Plane: YZ_Plane (좌우 대칭)
4. OK → "Motor_Mount_R" 자동 생성
```

---

## 4. 볼 캐스터 브라켓

### 4-1: 볼 캐스터 규격

볼 캐스터는 로봇 하단의 세 번째 지점이다.

| 항목 | 값 |
|------|-----|
| 볼 직경 | Φ10mm |
| 장착 볼트 | M3 × 4개 (20mm × 20mm 정사각형) |
| 전체 높이 | ~18mm |
| 볼 돌출 | ~5mm |

### 4-2: Body 생성

```
Create Body → 이름: "Ball_Caster_Bracket"
```

### 4-3: 브라켓 모델링

```
1. XY_Plane → Create Sketch
2. Create Rectangle:
   - 가로 30mm × 세로 30mm
   - 중심 원점 기준 좌우 대칭
   - Distance: "30mm" 양변
3. 모서리 Fillet: R5mm
4. Pad → Length: "12mm"

5. 윗면 선택 → Create Sketch
6. 나사 구멍 4개: (±10, ±10), Φ3mm → 반지름 "1.5mm"
7. Pocket → Through All

8. 밑면 선택 → Create Sketch
9. 볼 통과 구멍: 중심 (0,0) → Φ12mm → 반지름 "6mm"
10. Pocket → Through All
```

### 4-4: 볼 하우징 (볼이 들어갈 원통형 공간)

```
11. 밑면 → Create Sketch
12. Φ14mm 원 (하우징 내경) → 중심 (0,0)
13. Pocket → Depth: "8mm" (볼 하우징 깊이)
```

---

## 5. Day 1 전체 파일 정리

### 지금까지 만든 파일 목록

| 파일명 | 내용 |
|--------|------|
| `turtlebot_wheel.FCStd` | 바퀴 본체(Wheel_Body) + 타이어(Tire) |
| `turtlebot_base.FCStd` | 베이스 플레이트(Base_Plate) |
| `turtlebot_mounts.FCStd` | 모터 마운트 2개 + 볼 캐스터 브라켓 (선택 사항) |

> 또는 하나의 파일에 모든 Body를 저장해도 된다:
> `File → Merge Project`로 다른 파일의 Body를 현재 문서에 불러오기 가능

---

## 6. Day 1 전체 복습

### 오늘 배운 것

| Step | 내용 |
|------|------|
| Step 1 | FreeCAD 설치, 인터페이스, 작업대 개념 |
| Step 2 | 2D 스케치 — 선, 원, 사각형, 구속 조건 |
| Step 3 | 3D 형상 — Pad, Pocket, Revolution |
| Step 4 | 터틀봇 바퀴 + 타이어 모델링 |
| Step 5 | 베이스 플레이트 — 모터/캐스터/배선 홀 |
| Step 6 | 모터 마운트 + 볼 캐스터 브라켓 |

### 핵심 개념 복습

```
스케치 (2D)          →  구속 조건 (치수/기하)
    ↓
Pad / Pocket        →  3D 솔리드로 변환
    ↓
Fillet / Chamfer    →  마감 처리
    ↓
Mirror / Pattern    →  대칭/배열 효율화
    ↓
조립 (Day 2)         →  부품 결합
```

---

## ✅ Step 6 완료 체크리스트

- [ ] N20 모터 마운트가 완성되었다
- [ ] Mirror 기능으로 우측 마운트를 생성했다
- [ ] 볼 캐스터 브라켓이 완성되었다
- [ ] 모든 나사 구멍(Φ3mm)과 축 구멍(Φ6.2mm)이 정확하다
- [ ] Day 1의 모든 부품 파일이 저장되었다

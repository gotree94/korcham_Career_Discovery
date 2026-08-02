# Day 2 · Step 8 — LiDAR 마운트 + 상판 모델링

**소요시간**: 1h  
**목표**: RPLiDAR A1을 장착할 마운트와 터틀봇 상판(Top Plate)을 설계하고, 전체 조립에 추가한다.

---

## 1. RPLiDAR A1 사양

| 항목 | 값 |
|------|-----|
| 직경 | Φ98mm |
| 높이 | 40mm (돔 포함) |
| 무게 | ~105g |
| 통신 | UART (3.3V) |
| 스캔 범위 | 360° / 12m |
| 장착 방식 | 밑면 나사 4개 (Φ2.5mm 구멍) |

> RPLiDAR는 상판 위에 장착되어 360도 회전하며 주변을 스캔한다.

---

## 2. LiDAR 마운트 브라켓

### 2-1: Body 생성

```
Create Body → 이름: "LiDAR_Mount"
```

### 2-2: LiDAR 장착 플레이트

```
XY_Plane → Create Sketch

1. Create Circle → 중심 (0,0) → 반지름 "55mm" (Φ110mm, LiDAR보다 약간 큼)
2. Pad → Length: "4mm"

3. 윗면 → Create Sketch
4. LiDAR 고정 나사 구멍 4개:
   - 원형 배열: 중심 (0,0) 기준 Φ85mm 원 위에 4개
   - 각 90° 간격
   - 구멍 지름: Φ3mm (실제 Φ2.5mm + 여유)
   
   방법 ①: 직접 좌표 계산
   - (42.5, 0), (0, 42.5), (-42.5, 0), (0, -42.5)
   - Create Circle → 반지름 "1.5mm"
   
   방법 ②: Polar Pattern
   - 하나의 Φ3mm 원을 (42.5, 0) 위치에 스케치
   - Pocket → Through All → OK
   - Pocket Feature 선택 → Polar Pattern
   - Axis: Z축 → Count: 4 → Angle: 360°

5. 중앙 통과 홀:
   - Create Circle → 중심 (0,0) → Φ20mm (LiDAR 케이블 통과)
   - 반지름 "10mm"
   - Pocket → Through All
```

### 2-3: 스탠드오프 기둥 (상판-마운트 연결)

LiDAR 마운트는 상판 위에 일정 높이로 떠서 설치된다.

```
1. 밑면 → Create Sketch
2. Φ6mm 원 4개 → 위치: (±40, ±40) (상판의 스탠드오프 위치와 일치)
3. Pad → Length: "20mm" (LiDAR 높이 고려 + 공기 흐름)
4. 각 기둥 윗면 → Create Sketch → Φ3mm 원 (나사 구멍)
5. Pocket → Depth: "15mm" (M3 볼트 체결용)
```

---

## 3. 상판 (Top Plate)

### 3-1: 사양

| 항목 | 값 |
|------|-----|
| 형상 | 원형 |
| 직경 | 160mm |
| 두께 | 3mm |
| 재질 | PLA 또는 아크릴 |
| 기능 | Jetson + 배터리 + LiDAR 장착 베이스 |

### 3-2: Body 생성

```
Create Body → 이름: "Top_Plate"
```

### 3-3: 상판 모델링

```
XY_Plane → Create Sketch

1. Create Circle → 중심 (0,0) → 반지름 "80mm"
2. Pad → Length: "3mm"

3. 윗면 → Create Sketch (상판 장착 구멍들)

   [스탠드오프 연결 구멍 — 베이스 플레이트와 연결]
   - Φ3mm 구멍 4개 → 위치: (±65, ±65)
   - (베이스 플레이트 모서리 기준, 130mm × 130mm 정사각형)

   [Jetson Xavier NX 장착 구멍] (선택)
   - 보드 크기: ~103mm × 90mm
   - 장착 구멍: (±45, ±35) — 4개, Φ3mm

   [배터리 케이블 통과 홀]
   - Φ10mm × 2개 → 위치: (0, ±20)

4. Pocket → Through All (모든 구멍)
```

### 3-4: 스탠드오프 기둥 (하판-상판 연결)

```
1. 밑면 → Create Sketch
2. Φ8mm 원 4개 → 위치: (±65, ±65)
3. Pad → Length: "30mm" (하판-상판 사이 간격)

4. 각 기둥 윗면 → Create Sketch → Φ3mm 원
5. Pocket → Depth: "25mm" (M3 볼트 체결용 깊이)
```

> **대안**: 스탠드오프는 별도 부품으로 만들고, 상판에는 통과 구멍만 뚫은 후 조립 시 M3 볼트 + 너트로 체결할 수도 있다.

---

## 4. 전체 조립에 추가

### 4-1: 기존 Assembly 문서 열기

```
File → Open → "turtlebot_assembly.FCStd"
```

### 4-2: 새 부품 추가

```
A2plus → Add Part → "turtlebot_top.FCStd"
A2plus → Add Part → "turtlebot_lidar.FCStd"
```

### 4-3: 상판 조립

```
[Top_Plate → Base_Plate]

1. planeCoincident
   - Top_Plate 밑면 ↔ Base_Plate 윗면 (Offset: 30mm — 스탠드오프 높이)

2. circularEdge
   - Top_Plate 스탠드오프 구멍(Φ3mm) ↔ Base_Plate 대응 구멍
   - 1개만 정렬해도 위치 결정됨
```

### 4-4: LiDAR 마운트 조립

```
[LiDAR_Mount → Top_Plate]

1. planeCoincident
   - LiDAR_Mount 밑면 ↔ Top_Plate 윗면 (Offset: 0)

2. circularEdge
   - LiDAR_Mount 구멍 ↔ Top_Plate 대응 구멍
```

---

## 5. 전체 터틀봇 최종 형상

```
      ┌─────────────┐
      │  ⊙ LiDAR    │   ← LiDAR (360° 스캐닝)
      ├─────────────┤
      │  LiDAR Mount│   ← LiDAR 마운트
      ├─────────────┤
      │  Top Plate  │   ← 상판 (Jetson + 배터리 내부)
      ├─────────────┤
      │  │    │     │   ← 스탠드오프 기둥 (30mm)
      ├─────────────┤
      │  Base Plate │   ← 하판 (모터 + 바퀴 + 캐스터)
      ╰─┬──────┬───╯
        │ 바퀴 │        ← Wheel + Tire
        └──────┘
```

---

## ✅ Step 8 완료 체크리스트

- [ ] RPLiDAR A1 규격을 확인했다
- [ ] LiDAR 마운트 브라켓이 완성되었다
- [ ] 상판(Top Plate)이 완성되었다
- [ ] 하판-상판 연결용 스탠드오프가 설계되었다
- [ ] 모든 부품이 하나의 Assembly에 추가되었다
- [ ] 최종 터틀봇 조립이 완료되었다

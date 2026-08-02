# Day 3 · Step 15 — 동적 시뮬레이션 (Motion Simulation)

**소요시간**: 1h 30min  
**목표**: Assembly4 워크벤치로 터틀봇 조립체에 구속 조건 기반 움직임을 부여하고, 바퀴 회전과 로봇 주행을 시뮬레이션한다.

---

## 1. 동적 시뮬레이션이란?

> **동적 시뮬레이션**: 조립된 부품들이 실제처럼 움직이는 모습을 컴퓨터로 구현

```
정적 모델링 (Day 1-2)  →  부품의 형태와 위치 고정
동적 시뮬레이션 (Day 3) →  부품에 움직임과 회전 부여
```

### 터틀봇 시뮬레이션 목표

```
1. 바퀴가 회전한다
2. 바퀴 속도 차이에 따라 로봇이 회전한다
3. 조립 상태에서 간섭 없이 움직인다
4. 주행 경로를 예측할 수 있다
```

---

## 2. Assembly4 워크벤치 설치

### 2-1: Assembly4 vs A2plus

| 기능 | A2plus | Assembly4 |
|------|:------:|:---------:|
| 정적 조립 | ✅ | ✅ |
| 동적 시뮬레이션 | ❌ | ✅ |
| 애니메이션 | ❌ | ✅ |
| 변수 기반 구속 | ❌ | ✅ |

> Assembly4는 FreeCAD 내장 애드온으로, 동적 시뮬레이션과 애니메이션을 지원한다.

### 2-2: 설치

```
Tools → Addon Manager → "Assembly4" 검색 → Install

작업대 → Assembly4 선택
```

---

## 3. Assembly4로 조립 불러오기

### 3-1: 새 Assembly4 문서 생성

```
File → New
작업대 → Assembly4
Assembly4 → New Assembly
→ 파일명: "turtlebot_motion.FCStd"
```

### 3-2: 부품 가져오기

```
Assembly4 → Import Part
→ turtlebot_base.FCStd 열기 (Base_Plate)
→ turtlebot_mounts.FCStd 열기 (Motor_Mount_L/R)
→ turtlebot_wheel.FCStd 열기 (Wheel_Body x2)
```

> Assembly4는 각 부품을 **App::Part** 컨테이너로 가져온다.
> 조합보기에서 각 부품의 가시성(Spacebar)을 전환할 수 있다.

### 3-3: 고정 부품 설정

```
조합보기에서 "Base_Plate" 선택
Assembly4 → Assembly → Fix (고정)
→ Base_Plate가 고정됨 (워크벤치 기준)
```

---

## 4. 구속 조건 설정 (Assembly4 방식)

### 4-1: 모터 마운트 조립

```
1. Assembly4 → Assembly → Plane
   - Motor_Mount_L의 밑면 선택
   - Base_Plate의 윗면 선택
   → Offset: 0 → OK (동일 평면)

2. Assembly4 → Assembly → AxisAlignment
   - Motor_Mount_L의 나사 구멍 선택
   - Base_Plate의 대응 나사 구멍 선택
   → OK
```

### 4-2: 바퀴 — 회전 구속 (핵심!)

```
1. Assembly4 → Assembly → AxisAlignment
   - Wheel_Body의 축 구멍 원형 모서리
   - Motor_Mount_L의 모터축 통과 구멍
   → OK (동축 정렬)

2. Assembly4 → Assembly → PlaneOffset
   - Wheel_Body 측면
   - Motor_Mount_L 측면
   → Offset: "1mm" (간격 유지)
```

### 4-3: 각도 구속으로 회전 제어

```
Assembly4 → Assembly → Angle

- Wheel_Body의 XY_Plane 선택
- Base_Plate의 XY_Plane 선택
→ Angle: "0deg" (현재 각도 고정)
```

> 이 각도 구속이 나중에 **드라이버(변수)** 가 되어 바퀴 회전을 제어한다.

---

## 5. 드라이버(변수) 설정

Assembly4는 **스프레드시트 변수**로 구속 조건 값을 제어한다.

### 5-1: 변수 생성

```
1. 조합보기에서 Assembly 루트 선택
2. Assembly4 → Assembly → New Variable
   - Name: "wheel_L_angle"
   - Value: "0 deg"
   - OK

3. 변수 추가:
   - "wheel_R_angle" → 0 deg
   - "steering" → 0 (회전 계수, -1~1)
   - "speed" → 100 (RPM)
```

### 5-2: 변수를 구속 조건에 연결

```
1. 바퀴 좌측 Angle constraint 더블클릭
2. Expression 아이콘 (fx) 클릭
3. 입력: "wheel_L_angle"
4. OK

5. 우측 바퀴도 동일:
   → Expression: "wheel_R_angle"
```

---

## 6. 애니메이션 실행

### 6-1: 수동 구동

```
1. 조합보기에서 "wheel_L_angle" 변수 선택
2. 속성창에서 Value 변경: "0 deg" → "90 deg"
3. Ctrl+R (재계산)
4. 바퀴가 90° 회전했는지 확인
```

### 6-2: 연속 애니메이션

Assembly4에 내장된 애니메이션 도구 사용:

```
Assembly4 → Animate → Animate Assembly

1. Start: "0 deg"
2. End: "360 deg"
3. Step: "10 deg"
4. Variable: "wheel_L_angle"
5. Play 버튼

→ 바퀴가 1바퀴 회전하는 모습 애니메이션
```

### 6-3: 좌우 바퀴 동시 구동

```
Assembly4 → Animate → Variables

1. Variable 1: wheel_L_angle (0 → 360)
2. Variable 2: wheel_R_angle (0 → 360)

→ Play → 두 바퀴 동시 회전 ✅

※ 우측 바퀴 속도를 절반으로:
   Variable 2: wheel_R_angle = wheel_L_angle / 2
   → 차동 회전 시뮬레이션!
```

---

## 7. 주행 시나리오 시뮬레이션

### 시나리오 1: 직진

```
wheel_L_angle: 0 → 360 (1회전)
wheel_R_angle: 0 → 360 (1회전)

→ 좌우 동일 속도 → 직진
```

### 시나리오 2: 우회전

```
wheel_L_angle: 0 → 360 (1회전)
wheel_R_angle: 0 → 180 (반회전)

→ 우측이 느리게 회전 → 우회전
```

### 시나리오 3: 제자리 회전

```
wheel_L_angle: 0 → 360 (정회전)
wheel_R_angle: 0 → -360 (역회전)

→ 좌우 반대 방향 → 제자리 회전
```

---

## 8. 간섭 없는 움직임 확인

### 8-1: 애니메이션 중 간섭 확인

```
애니메이션 재생 중 (또는 각 단계별로)
A2plus → Check Interference 실행

→ 모든 각도에서 간섭 없음 확인
```

### 8-2: 간섭 발견 시 대처

```
문제: 바퀴가 회전하면서 베이스 플레이트와 충돌

해결 ①: 바퀴와 베이스 간격 증가 (PlaneOffset → 2mm)
해결 ②: 베이스 플레이트의 바퀴 근접부 모서리 Fillet 증가
해결 ③: 모터 마운트 위치 조정
```

---

## 9. 시뮬레이션 결과 시각화

### 9-1: 경로 추적

```
1. Draft 워크벤치 전환
2. Draft → Point → 로봇 중심에 점 생성
3. 각 시뮬레이션 단계마다 점 위치 기록
4. Draft → Spline → 점들을 연결 → 주행 경로
```

### 9-2: 결과 예시

```
직진: ──────────────── (직선)
우회전: ╭────────── (곡선, 반경 165mm)
제자리 회전: ◎ (한 점에서 회전)
```

---

## 10. 핵심 요약

```
Assembly4 변수 → 구속 조건 각도 제어 → 애니메이션

1. Fix로 기준 부품 고정
2. AxisAlignment로 회전축 정렬
3. Angle로 바퀴 각도 제어
4. Variable로 회전값 입력
5. Animate로 연속 움직임
```

---

## ✅ Step 15 완료 체크리스트

- [ ] Assembly4 워크벤치가 설치되었다
- [ ] 부품을 Assembly4 문서로 가져왔다
- [ ] 바퀴에 회전 구속(AxisAlignment + Angle)을 설정했다
- [ ] 드라이버 변수(wheel_L_angle, wheel_R_angle)를 생성했다
- [ ] 변수를 구속 조건에 연결했다 (Expression)
- [ ] 직진/우회전/제자리 회전을 시뮬레이션했다
- [ ] 모든 회전 각도에서 간섭이 없음을 확인했다

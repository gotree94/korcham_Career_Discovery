# Day 2 · Step 9 — FEA 구조 해석

**소요시간**: 1h 30min  
**목표**: FreeCAD FEM 워크벤치로 모터 마운트의 구조 해석을 수행하고, 응력 집중 위치를 파악한 후 설계를 개선한다.

---

## 1. FEA(유한요소해석) 개념

> **FEA (Finite Element Analysis)** : 물체를 수만 개의 작은 요소(Element)로 나누고, 각 요소에 가해진 힘을 계산하여 전체 구조의 강도를 예측하는 방법

```
┌───┬───┬───┬───┐
│   │   │   │   │     ← 물체를 작은 사각형(요소)으로 분할
├───┼───┼───┼───┤
│   │   │   │   │     각 요소의 변형/응력을 계산
├───┼───┼───┼───┤
│   │   │   │   │     → 전체 구조의 취약점 파악
└───┴───┴───┴───┘
```

### FEA 색상 의미

| 색상 | 의미 |
|:----:|------|
| 🔵 파랑 | 응력이 낮음 (안전) |
| 🟢 초록 | 적정 수준 |
| 🟡 노랑 | 주의 필요 |
| 🔴 빨강 | 응력 집중 (위험, 보강 필요) |

> **목표**: 빨간 영역을 없애거나 줄이는 방향으로 설계 개선

---

## 2. 해석할 부품 선택

이 과정에서는 가장 많은 하중을 받는 **모터 마운트(Motor Mount)** 를 해석한다.

> 모터 마운트는 베이스 플레이트와 모터 사이에 위치하여, 모터+바퀴의 무게와 주행 충격을 지지한다.

---

## 3. FEM 준비

### 3-1: FEM 작업대로 전환

```
작업대 콤보박스 → "FEM" 선택
```

### 3-2: 해석할 Body 열기

```
File → Open → "turtlebot_mounts.FCStd"
```

또는 기존 Assembly 파일에서 Motor_Mount_L Body만 선택하여 새 문서로 복사

### 3-3: 새 FEM 해석 생성

```
조합보기에서 Motor_Mount_L Body 선택
FEM → New Analysis → "Static Analysis" 선택

→ 조합보기에 "Analysis" 컨테이너가 생성됨
```

---

## 4. 해석 설정 (순서대로)

### 4-1: 재료 할당 (Material)

```
FEM → Material → Create FEM Material for Solid

1. Material Editor 창:
   - Material: "Plastic" 카테고리 → "ABS" 선택
   - 또는 직접 입력:
     * Name: ABS
     * Young's Modulus: 2300 MPa
     * Poisson Ratio: 0.35
     * Density: 1050 kg/m^3
     * Yield Strength: 40 MPa

2. Motor_Mount_L Body 선택 (3D 뷰에서 클릭)
3. OK
```

> ABS(아크릴로니트릴 부타디엔 스티렌)는 3D프린터에서 가장 흔히 사용하는 플라스틱이다.

### 4-2: 고정 조건 (Fixed Constraint)

```
FEM → Constraints → Create FEM Constraint Fixed

1. 3D 뷰에서 모터 마운트의 구멍 4개 선택
   (베이스 플레이트와 체결되는 Φ3mm 구멍들의 내면)
2. OK
```

> ⚠ 선택이 어려우면 조합보기에서 Body를 숨기기/표시 전환
> 구멍 내면은 3D 뷰를 회전하여 선택

### 4-3: 하중 조건 (Force Constraint)

```
FEM → Constraints → Create FEM Constraint Force

1. 3D 뷰에서 모터 마운트의 모터 장착면 선택
   (모터 플랜지가 닿는 면)

2. Force Editor:
   - Force: "5 N" (모터 중량 ~0.05kg × 10 = 0.5N, 안전계수 10배 적용)
   - Direction: "Normal" (면에 수직 방향)
     또는 벡터 지정: (0, 0, -1) — 중력 방향
   
3. OK
```

### 4-4: Meshing (격자 생성)

```
FEM → Mesh → Create FEM Mesh from Shape

1. 모터 마운트 선택
2. Meshing Parameters:
   - Maximum Element Size: "2 mm"
   - Second Order: 체크 (더 정확한 결과)
   
3. OK → "Mesh" 객체 생성
4. 조합보기에서 Mesh 선택 → 우클릭 → "Apply" (메시 생성 실행)
```

> 메시 생성에 10~30초 소요. 더 촘촘한 메시(1mm)는 더 정확하지만 계산 시간이 길어진다.

---

## 5. Solver 실행

### 5-1: Solver 설정

```
FEM → Solver → Create FEM Solver → CalculiX

1. Solver 객체가 생성되면:
   - Analysis Type: "Static" (정적 해석)
   - Output: "All" (모든 결과 출력)
```

### 5-2: 실행

```
조합보기에서 Solver 선택
FEM → Solver → Run Solver Calculation (또는 더블클릭)
→ "Solve" 버튼 클릭

→ 검은 콘솔 창이 나타나며 계산 진행 (1~3분)
→ 완료 메시지 확인
```

---

## 6. 결과 확인

### 6-1: 결과 표시

```
조합보기 → "Results" 객체 생성됨
FEM → Post Processing → Show Result

1. Type: "Von Mises Stress" 선택
   (Von Mises = 등가 응력, 재료의 파괴 기준)
2. Show: 체크
```

### 6-2: 결과 해석

```
색상 막대 (Color Bar):
  상단: 최대 응력 (빨강)
  하단: 최소 응력 (파랑)

확인할 것:
1. 가장 빨간(응력 집중) 부분이 어디인가?
2. 최대 응력 값은? (MPa 단위)
3. ABS 항복 강도(40MPa)와 비교하여 안전율 계산
```

### 6-3: 안전율 계산

```
안전율(Safety Factor) = 재료 항복강도 ÷ 최대 발생 응력

예:
최대 응력 = 28MPa
ABS 항복강도 = 40MPa
안전율 = 40 / 28 = 1.43

→ 안전율이 2.0 미만이면 설계 개선 필요!
```

---

## 7. 설계 개선

### 7-1: 응력 집중 위치 확인

FEA 결과에서 빨간 영역이 발견되면:

| 위치 | 문제 | 개선 방법 |
|------|------|----------|
| 구멍 주변 | 응력 집중 (가장 일반적) | 구멍 주변 보강 리브 추가 |
| 모서리 | 날카로운 모서리에서 응력 집중 | Fillet 추가 (R2~3mm) |
| 얇은 부분 | 두께 부족 | 두께 증가 (5mm → 8mm) |

### 7-2: 설계 변경하기

```
1. 조합보기에서 원래 마운트의 Body 더블클릭 (편집 모드)
2. 개선 사항 적용:
   a. 베이스 두께: 5mm → 8mm
   b. 리브 추가: 모터 장착면 뒤쪽에 3mm 두께 리브
   c. 모든 날카로운 모서리에 Fillet R2mm
3. Body 편집 완료 → 조합보기 빈 곳 더블클릭
```

### 7-3: 재해석

1. 조합보기에서 Mesh 선택 → 삭제
2. 새 Mesh 생성 (4-4 반복)
3. Solver 재실행 (5-2 반복)

### 7-4: 개선 결과 비교

```
항목        개선 전        개선 후
─────────  ─────────      ─────────
최대 응력   28 MPa         11 MPa
안전율      1.43           3.64
응력 분포   3군데 집중      고르게 분산
색상        빨강 존재       파랑~초록 위주
```

> **성공!** 설계 변경으로 안전율이 1.43 → 3.64로 향상되었다.

---

## 8. 결과 저장

### 8-1: 스크린샷 저장

```
1. 3D 뷰를 적절한 각도로 회전
2. FEA 결과가 보이도록 설정
3. Windows + Shift + S (캡처 도구) 또는 FreeCAD 메뉴:
   Tools → Save Picture → "fea_before.png"
4. 개선 후에도 동일하게 저장 → "fea_after.png"
```

### 8-2: FEM 분석 파일 저장

```
Ctrl+S → "motor_mount_fea.FCStd"
```

---

## 9. FEA 핵심 요약

> **"FEA는 설계의 취약점을 색깔로 보여주는 도구"**

| 단계 | 핵심 동작 |
|------|----------|
| ① 재료 | 어떤 재료를 쓸지 정한다 (ABS, PLA 등) |
| ② 고정 | 어디가 움직이지 않는 부분인지 정한다 |
| ③ 하중 | 어디에, 얼마나 힘이 가해지는지 정한다 |
| ④ 메시 | 물체를 작은 조각으로 나눈다 |
| ⑤ 실행 | 컴퓨터가 계산한다 |
| ⑥ 결과 | 빨간 부분 = 보강 필요 |

---

## ✅ Step 9 완료 체크리스트

- [ ] FEM 작업대에서 새 해석(Analysis)을 생성했다
- [ ] 재료(ABS)를 할당했다
- [ ] 고정 조건과 하중 조건을 설정했다
- [ ] Mesh를 생성했다
- [ ] Solver가 정상 실행되었다
- [ ] Von Mises Stress 결과를 확인했다
- [ ] 설계 개선 전/후를 비교했다 (스크린샷 저장)
- [ ] 안전율을 계산했다

# FreeCAD Sketch 기능 교육 자료

## 1. 스냅(Snap)

### 개요

FreeCAD Sketcher는 SolidWorks처럼 자동 스냅보다 **구속조건(Constraint)**
중심입니다.

### Draft Workbench의 Snap

-   Endpoint
-   Midpoint
-   Center
-   Intersection
-   Grid Snap

사용: 1. Draft Workbench 선택 2. Snap 툴바 표시 3. 필요한 Snap 활성화 4.
객체 작성

### Sketcher에서 위치 맞추기

1.  점/선을 대략 배치
2.  Coincident, Horizontal, Vertical, Symmetry, Tangent 등 Constraint
    적용
3.  치수 Constraint 추가
4.  Fully Constrained 확인

------------------------------------------------------------------------

## 2. Sketch Array

### Rectangular Array

1.  Sketch 편집
2.  배열할 요소 선택
3.  Sketch → Rectangular Array
4.  행/열, 간격 입력
5.  확인

### Polar Array

1.  요소 선택
2.  Sketch → Polar Array
3.  중심 선택
4.  개수와 각도 입력
5.  확인

팁: - 원본 수정 시 배열도 함께 수정됨.

------------------------------------------------------------------------

## 3. Projection(구 External Geometry)

### 목적

기존 모델의 모서리나 점을 현재 Sketch의 참조로 사용.

### 사용법

1.  면 선택
2.  새 Sketch 생성
3.  Projection 도구 선택
4.  참조할 모서리 선택
5.  보라색 참조선 생성
6.  참조선을 기준으로 스케치 작성

### 특징

-   참조 전용
-   원본 변경 시 자동 업데이트

------------------------------------------------------------------------

## SolidWorks 대응

  SolidWorks                FreeCAD
  ------------------------- -------------------
  Convert Entities          Projection
  Linear Sketch Pattern     Rectangular Array
  Circular Sketch Pattern   Polar Array
  Smart Dimension           Constraints
  Relations                 Constraints

## 실습

1.  100×60 사각형 작성
2.  중심 원 작성
3.  Rectangular Array로 구멍 4개 생성
4.  새 Sketch에서 Projection으로 모서리 가져오기
5.  Constraint로 Fully Constrained 만들기


---

## 4. SolidWorks의 요소 변환(Convert Entities)과 FreeCAD의 차이

### SolidWorks의 Convert Entities
기존 3D 모델의 모서리나 이미 작성된 스케치 요소를 선택하면 **현재 스케치에서 편집 가능한 실제 스케치 선**으로 변환합니다.

### FreeCAD에서 동일한 작업

#### (1) 3D 모서리 가져오기
`Projection`(구 External Geometry)을 사용합니다.

절차
1. 모델의 면을 선택하여 Sketch를 생성한다.
2. **Projection** 도구를 실행한다.
3. 필요한 모서리를 선택한다.
4. 선택한 모서리가 **보라색 참조선**으로 생성된다.

> 참조선은 원본 형상과 연관성을 유지하며 원본이 변경되면 자동으로 업데이트된다.

#### (2) 참조선을 실제 스케치 선으로 사용할 수 있는가?
아니요. Projection으로 생성된 요소는 **참조(Reference)** 이며 직접 편집하거나 돌출 형상에 사용하는 실제 스케치 요소가 아니다.

실제 선이 필요하면 참조선을 기준으로 Line, Arc 등의 스케치 요소를 다시 작성해야 한다.

#### (3) 기존 스케치를 그대로 가져오기
`CarbonCopy` 기능을 사용한다.

CarbonCopy는 다음 정보를 함께 복사한다.

- 선, 원, 호
- 치수
- 구속조건

Sketch 전체를 재사용할 때 적합하다.

### 기능 비교

| 작업 | SolidWorks | FreeCAD |
|---|---|---|
| 3D 모서리를 현재 스케치로 가져오기 | Convert Entities | Projection |
| 가져온 요소가 실제 스케치 선 | 가능 | 불가능(참조선만 생성) |
| 기존 Sketch 전체 복사 | 제한적 | CarbonCopy |
| 원본 변경 시 연관성 유지 | 가능 | 가능 |

### 교육 포인트
SolidWorks 사용자가 가장 혼동하는 부분은 **Projection으로 생성된 선이 실제 스케치 선이 아니라 참조선**이라는 점이다. 따라서 FreeCAD에서는 Projection으로 기준 형상을 만든 후, 필요한 경우 실제 스케치 요소를 다시 작성하는 작업 흐름을 익혀야 한다.

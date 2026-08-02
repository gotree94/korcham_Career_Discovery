# DC Transfer (.tf) — DC 전달함수 해석

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

DC 동작점에서 **출력/입력 전달함수(이득)**와 **입력 저항·출력 저항**을 한 번에 계산하는 해석. 증폭기의 DC 이득과 임피던스 확인에 사용.

## 결과 확인 방법

동작점 창에 Transfer Function(이득), input impedance, output impedance가 출력됨

## 파라미터 (Simulate > Edit Simulation Cmd → DC Transfer 탭)

| 항목 | 의미 |
|---|---|
| Output | 출력: 노드 전압 `V(노드)` 또는 소스 전류 `I(전압원)` |
| Source | 입력 소스 이름 |

## 지시어

- `.tf V(<out>[,<ref>]) <src>` 또는 `.tf I(<Vsource>) <src>`

## 본 자료 실습 예제

예제 없음. 응용: `01_voltage_divider.asc`에 Vout 노드 이름(F4)을 붙인 뒤
`.tf V(Vout) V1`을 추가하면 분배비 ≈ 0.6667과 입력/출력 저항을 확인할 수 있다.

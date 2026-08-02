# Noise (.noise) — 노이즈 해석

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

소자의 열노이즈·쇼트노이즈가 출력에 얼마나 나타나는지 **주파수별**로 계산하는 해석. 저잡음 증폭기 설계 시 사용.

## 결과 확인 방법

- 출력 변수 `onoise`(출력 환산), `inoise`(입력 환산), `V(onoise)`/`V(inoise)`로 그래프 확인
- **소자별 기여도**(요약표) 확인 가능

## 파라미터 (Simulate > Edit Simulation Cmd → Noise 탭)

| 항목 | 의미 |
|---|---|
| Output | 출력 노드 (예: V(Vout), V(Vout,ref)) |
| Reference | 기준 노드 (미지정 시 GND) |
| Source | 입력(노이즈원) 전압/전류원 |
| Points per summary | 몇 포인트마다 소자 기여도를 요약할지 (0이면 마지막 한 지점만) |
| Type of sweep / Number of points / Start~Stop Frequency | AC와 동일한 주파수 스윕 설정 |

## 지시어

- `.noise V(<out>[,<ref>]) <src> <dec|oct|lin> <Npoints> <fstart> <fstop> [<Npsummary>]`

## 본 자료 실습 예제

예제 없음. 응용: `03_RC_lowpass_filter.asc`에서 Vout 노드에 F4로 이름을 붙인 뒤
`.noise V(Vout) V1 dec 100 1 1Meg`를 추가하면 R1/C1의 노이즈 기여도를 볼 수 있다.

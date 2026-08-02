# AC Analysis (.ac) — 주파수 영역(소신호) 해석

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

DC 동작점에서 회로를 **선형화**한 뒤, 입력 주파수를 바꿔가며 **이득과 위상**을 계산하는 해석. 필터의 컷오프 주파수, 증폭기의 주파수 응답을 볼 때 사용 (Bode Plot).

## 필수 조건

입력 신호원에 **AC 진폭을 지정**해야 한다. (전압원 우클릭 → Advanced → AC Amplitude = 1 → 소자 옆에 `AC 1` 표시). DC 값과는 별개로 부여한다.

## 결과 확인 방법

- x축=주파수(로그), y축=크기(dB)·위상(°) 그래프

## 파라미터 (Simulate > Edit Simulation Cmd → AC Analysis 탭)

| 항목 | 의미 |
|---|---|
| Type of sweep | Decade(10배당) / Octave(2배당) / Linear(등간격) / List(목록) |
| Number of points | Decade·Octave: 구간당 포인트 수 (보통 10~100), Linear: 전체 포인트 수 |
| Start Frequency / Stop Frequency | 분석할 주파수 범위 |

## 지시어

- `.ac <dec|oct|lin> <Npoints> <fstart> <fstop>` (예: `.ac dec 100 1 1Meg`)

## 본 자료 실습 예제

| 파일 | 내용 |
|---|---|
| `03_RC_lowpass_filter.asc` | RC LPF, 컷오프 ≈ 159Hz |
| `05_LC_resonance.asc` | LC 공진, f0 ≈ 5.03kHz |

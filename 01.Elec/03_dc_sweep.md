# DC Sweep (.dc) — DC 스윕 해석

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

한 전압/전류원을 x축처럼 범위 안에서 바꿔가며 DC 응답 곡선을 그리는 해석. **I-V 특성 곡선**, 제너 동작 확인 등에 사용.

## 결과 확인 방법

- x축=스윕 소스 값, y축=출력 전압/전류 그래프
- 두 번째 소스를 스윕하면 패밀리 커브

## 파라미터 (Simulate > Edit Simulation Cmd → DC sweep 탭)

| 항목 | 의미 |
|---|---|
| Name of 1st source to sweep | 스윕할 소스 이름 (예: V1, Vds) |
| Type of sweep | Linear(등간격) / Decade / Octave / List |
| Start value / Stop value | 소스 시작·끝 값 |
| Increment (Linear) | 증가 간격 (0보다 커야 함) |
| 2nd/3rd source to sweep | **중첩 스윕** — 두 번째 소스를 반복하며 패밀리 커브 생성 |

## 지시어

- `.dc <src> <start> <stop> <incr> [<src2> <start2> <stop2> <incr2>]`
- 예: `.dc Vds 0 10 0.1 Vgs 2 6 1` (Vds를 0→10V 0.1 간격으로, Vgs를 2→6V 1 간격으로 반복)

## 본 자료 실습 예제

| 파일 | 내용 |
|---|---|
| `06_diode_IV_curve.asc` | 다이오드 I-V |
| `08_zener_regulator.asc` | 제너 I-V |
| `12_MOSFET_IV_curve.asc` | MOSFET I-V, 중첩 스윕 |

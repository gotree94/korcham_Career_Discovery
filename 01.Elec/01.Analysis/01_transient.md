# Transient (.tran) — 시간 영역 해석

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

시간 축 위에서 전압·전류가 어떻게 변화하는지 계산하는 해석. 과도응답, 충방전, 스위칭, 정류처럼 **시간에 따라 변하는** 동작을 볼 때 사용. **이 자료에서 가장 많이 쓰는 해석**이다.

## 결과 확인 방법

- x축=시간, y축=전압/전류 그래프 (파형 위에서 커서 클릭 → 좌표값 표시)

## 파라미터 (Simulate > Edit Simulation Cmd → Transient 탭)

| 항목 | 의미 | 예시 |
|---|---|---|
| Stop Time | 시뮬레이션할 전체 시간 (Tstop) | 5m = 5ms |
| Time to Start Saving Data | 파형을 저장하기 시작할 시간 (Tstart). 실행 후 그래프/데이터 용량을 줄임 | 3 = 3초 이후만 저장 |
| Maximum Timestep | 계산 간격의 상한 (Tmaxstep). 작을수록 정밀·느림 (기본: 자동) | 1u = 1µs 이하 간격 |
| Start external DC supply voltages at 0V | 전원을 0V부터 서서히 올리며 시작 (전원 기동 시뮬레이션) | 체크 |
| Use Initial Conditions | 커패시터/인덕터의 초기조건 사용 (UIC) | 체크 |
| Steady State | 초기 과도 구간을 자동으로 건너뛰고 정상상태만 계산 | 체크 |

## 지시어

- 기본: `.tran <Tstop>` (예: `.tran 20m`)
- 전체 형식: `.tran <Tstep> <Tstop> <Tstart> <Tmaxstep>` (예: `.tran 0 10 3 0.2`)

## 본 자료 실습 예제

| 파일 | 내용 |
|---|---|
| `02_RC_charge_discharge.asc` | RC 충방전 |
| `04_RL_transient.asc` | RL 과도 |
| `07_halfwave_rectifier.asc` | 정류 |
| `09_BJT_switch_LED.asc` | BJT 스위치 |
| `10_BJT_common_emitter_amp.asc` | 증폭기 |
| `11_MOSFET_switch.asc` | MOSFET 스위치 |
| `13_chopper_motor_driver.asc` | 초퍼 |

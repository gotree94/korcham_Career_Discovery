# DC op pnt (.op) — DC 동작점 해석

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

커패시터를 개방, 인덕터를 단락으로 가정하고 **DC 동작점(Q-point)**을 계산하는 해석. 다른 모든 해석(.ac/.dc/.tran)도 실행 전에 내부적으로 이 동작점을 먼저 구한다.

## 파라미터

없음 (DC op pnt 탭의 "Perform Operating Point Analysis" 체크만)

## 결과 확인 방법

- **동작점(Operating Point) 창**에 노드 전압·소자 전류 표시
- 실행 후 회로 창에서 노드·소자 위에 마우스를 올리면 커서 옆에 값 표시

## 지시어

- `.op`

## 본 자료 실습 예제

| 파일 | 내용 |
|---|---|
| `01_voltage_divider.asc` | 분배 전압 확인 |
| `10_BJT_common_emitter_amp.asc` | 증폭기 Q-point: VCE가 공급전압 중간 부근인지 확인 |

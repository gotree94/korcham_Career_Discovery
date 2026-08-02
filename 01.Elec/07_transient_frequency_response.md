# Transient Frequency Response (.fra) — 과도 주파수 응답 해석 (고급)

[← Analysis 목차](README.md) · [README (전체)](../README.md)

## 의미

과도(시간 영역) 해석을 **여러 주파수의 사인 테스트 신호**로 반복 수행해 주파수 응답(Bode)을 얻는 해석. LTspice 17.1+에서 도입되어 26에서도 제공.

## 쓰이는 곳

스위칭 전원(SMPS)의 제어 루프처럼 **비선형 회로**의 루프 게인·위상, 출력 임피던스 측정. (선형 회로는 `.ac`로 충분하다)

## 사용 절차

1. `F2`로 **fra(frequency response analyzer) 소자**를 회로의 측정 지점에 배치
2. fra 소자 우클릭 → 테스트 신호 설정 (주파수 범위, 진폭, settle 시간)
3. **Simulate > Edit Simulation Cmd → Transient Frequency Response 탭** → `.fra` 지시어 생성 (이때 다른 해석 지시어는 주석 처리)
4. ▶ 실행 → Bode Plot(루프 게인/위상) 확인

## 지시어

- `.fra` (fra 소자와 함께 동작)

## 본 자료 실습 예제

예제 없음. LTspice 설치 폴더 `Examples/Educational/FRA`에 공식 예제가 있다.

# 전자 소자의 기본 원리와 LTspice 시뮬레이션 교육자료

**대상**: 임베디드/전자공학 입문자 (직업훈련·고등학생 수준) <br>
**작성**: Multimix / 광주인력개발원 교육과정 <br>
**도구**: LTspice (Analog Devices 공식 배포, 무료) — 최신 버전(24/26, `LTspice64`) 권장, LTspice XVII와도 완전 호환 <br>

---

## 실습 파일 목록 (더블클릭으로 바로 실행)

> 본 폴더(`01.Elec`)의 `01~13_*.asc` 파일은 **시뮬레이션 지시어가 이미 포함된 완성 회로**다.
> 각 예제는 "UI로 진행하기" 절차대로 파일을 열고 실행하기만 하면 된다. (상세 절차는 오른쪽 문서 링크 참조)

| # | 파일 | 내용 | 해석 종류 | 상세 문서 |
|---|---|---|---|---|
| 1 | `01_voltage_divider.asc` | 저항 전압 분배기 | `.op` | [2.3 전압 분배기](02_resistor.md) |
| 2 | `02_RC_charge_discharge.asc` | RC 충방전 | `.tran` | [3.3 RC 충방전](03_capacitor.md) |
| 3 | `03_RC_lowpass_filter.asc` | RC 저역통과필터 (Bode) | `.ac` | [3.4 RC LPF](03_capacitor.md) |
| 4 | `04_RL_transient.asc` | RL 과도응답/역기전력 | `.tran` | [4.3 RL 과도응답](04_inductor.md) |
| 5 | `05_LC_resonance.asc` | LC 공진 | `.ac` | [4.4 LC 공진](04_inductor.md) |
| 6 | `06_diode_IV_curve.asc` | 다이오드 I-V 특성 | `.dc` | [5.3 다이오드 I-V](05_diode.md) |
| 7 | `07_halfwave_rectifier.asc` | 반파 정류 | `.tran` | [5.4 반파 정류](05_diode.md) |
| 8 | `08_zener_regulator.asc` | 제너 정전압 | `.dc` | [5.5 제너 정전압](05_diode.md) |
| 9 | `09_BJT_switch_LED.asc` | NPN 스위치 (LED) | `.tran` | [6.3 NPN 스위치](06_bjt.md) |
| 10 | `10_BJT_common_emitter_amp.asc` | 공통 이미터 증폭기 | `.tran` | [6.4 공통 이미터 증폭기](06_bjt.md) |
| 11 | `11_MOSFET_switch.asc` | MOSFET 스위치 | `.tran` | [7.3 MOSFET 스위치](07_fet.md) |
| 12 | `12_MOSFET_IV_curve.asc` | MOSFET I-V 곡선 | `.dc` | [7.4 MOSFET I-V](07_fet.md) |
| 13 | `13_chopper_motor_driver.asc` | 초퍼 모터 드라이버 (VT6-mini 연계) | `.tran` | [7.5 초퍼 구동회로](07_fet.md) |

---

## 목차 (번호별 문서)

| # | 문서 | 내용 |
|---|---|---|
| 0 | [00_installation.md](00_installation.md) | LTspice 설치 (상세) |
| 1 | [01_basics_ui.md](01_basics_ui.md) | LTspice 기본 사용법 (UI 중심) |
| 2 | [02_resistor.md](02_resistor.md) | 저항 (Resistor) |
| 3 | [03_capacitor.md](03_capacitor.md) | 캐패시터 (Capacitor) |
| 4 | [04_inductor.md](04_inductor.md) | 인덕터 (Inductor) |
| 5 | [05_diode.md](05_diode.md) | 다이오드 (Diode) |
| 6 | [06_bjt.md](06_bjt.md) | BJT (Bipolar Junction Transistor) |
| 7 | [07_fet.md](07_fet.md) | FET (전계효과 트랜지스터, MOSFET) |
| 8 | [08_analysis.md](08_analysis.md) | Analysis(해석) 종류 상세 |
| 9 | [09_common_usage.md](09_common_usage.md) | LTspice 공통 사용법 요약 |
| 10 | [10_final_project.md](10_final_project.md) | 종합 실습 과제 |
| 11 | [11_teaching_guide.md](11_teaching_guide.md) | 참고: 교육 진행 순서 제안 |

**해석 파라미터 상세**는 [`Analysis/`](Analysis/README.md) 폴더에 해석별로 분할되어 있다.

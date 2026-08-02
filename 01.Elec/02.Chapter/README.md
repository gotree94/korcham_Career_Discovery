# 챕터 실습 (02.Chapter) — 목차

[← 전체 목차](../README.md)

이 폴더에는 **회로 파일(`.asc`) 13개**와 각 실습의 **이론·UI 절차 문서(실습NN_*.md)**가 있다.
`.asc` 파일은 더블클릭으로 바로 실행되고, 각 예제의 상세 이론과 확인 사항은 우측 실습 문서에 정리되어 있다.

| # | 회로 파일 | 내용 | 해석 종류 | 실습 문서 |
|---|---|---|---|---|
| 1 | `01_voltage_divider.asc` | 저항 전압 분배기 | `.op` | [실습01](실습01_전압_분배기.md) |
| 2 | `02_RC_charge_discharge.asc` | RC 충방전 | `.tran` | [실습02](실습02_RC_충방전.md) |
| 3 | `03_RC_lowpass_filter.asc` | RC 저역통과필터 (Bode) | `.ac` | [실습03](실습03_RC_저역통과필터.md) |
| 4 | `04_RL_transient.asc` | RL 과도응답/역기전력 | `.tran` | [실습04](실습04_RL_과도응답.md) |
| 5 | `05_LC_resonance.asc` | LC 공진 | `.ac` | [실습05](실습05_LC_공진.md) |
| 6 | `06_diode_IV_curve.asc` | 다이오드 I-V 특성 | `.dc` | [실습06](실습06_다이오드_IV_곡선.md) |
| 7 | `07_halfwave_rectifier.asc` | 반파 정류 | `.tran` | [실습07](실습07_반파_정류.md) |
| 8 | `08_zener_regulator.asc` | 제너 정전압 | `.dc` | [실습08](실습08_제너_정전압.md) |
| 9 | `09_BJT_switch_LED.asc` | NPN 스위치 (LED) | `.tran` | [실습09](실습09_NPN_스위치.md) |
| 10 | `10_BJT_common_emitter_amp.asc` | 공통 이미터 증폭기 | `.tran` | [실습10](실습10_공통_이미터_증폭기.md) |
| 11 | `11_MOSFET_switch.asc` | MOSFET 스위치 | `.tran` | [실습11](실습11_MOSFET_스위치.md) |
| 12 | `12_MOSFET_IV_curve.asc` | MOSFET I-V 곡선 | `.dc` | [실습12](실습12_MOSFET_IV_곡선.md) |
| 13 | `13_chopper_motor_driver.asc` | 초퍼 모터 드라이버 (VT6-mini 연계) | `.tran` | [실습13](실습13_초퍼_모터_드라이버.md) |

## 학습 순서

1. [실습01](실습01_전압_분배기.md) ~ [실습05](실습05_LC_공진.md): 수동소자(R, C, L) 기초
2. [실습06](실습06_다이오드_IV_곡선.md) ~ [실습08](실습08_제너_정전압.md): 반도체 소자(다이오드)
3. [실습09](실습09_NPN_스위치.md) ~ [실습12](실습12_MOSFET_IV_곡선.md): BJT/MOSFET
4. [실습13](실습13_초퍼_모터_드라이버.md): 종합 응용 (초퍼 모터 드라이버, VT6-mini 연계)

> 각 실습의 해석 종류(`.op`/`.tran`/`.ac`/`.dc`)에 대한 자세한 설명은 [01.Analysis](../01.Analysis/README.md) 참조.

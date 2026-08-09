# Analysis(해석) 종류 상세 — 목차

LTspice의 모든 시뮬레이션은 **해석 종류(Analysis)**와 **입력 파라미터**로 결정된다.
설정은 메뉴 **Simulate > Edit Simulation Cmd** 대화상자에서 **탭별로** 하거나, 회로 창에서 **S** 키를 눌러 지시어(`.tran` 등)를 직접 입력해 만든다.

LTspice 26 기준 해석 탭은 7종이며, 각각의 의미·입력 파라미터·결과 확인 방법은 아래 별도 파일로 분할되어 있다.

| 파일 | 해석 | 지시어 | 의미 (해석이 답하는 질문) | 본 자료 예제 |
|---|---|---|---|---|
| [01_transient.md](01_transient.md) | Transient | `.tran` | 시간이 지나면 전압/전류는 어떻게 변하나? | 02, 04, 07, 09, 10, 11, 13 |
| [02_ac_analysis.md](02_ac_analysis.md) | AC Analysis | `.ac` | 주파수가 변하면 이득/위상은? (Bode) | 03, 05 |
| [03_dc_sweep.md](03_dc_sweep.md) | DC Sweep | `.dc` | 한 소스를 바꾸면 DC 응답 곡선은? (I-V) | 06, 08, 12 |
| [04_noise.md](04_noise.md) | Noise | `.noise` | 주파수별 노이즈 기여도는? | (응용) |
| [05_dc_transfer.md](05_dc_transfer.md) | DC Transfer | `.tf` | DC 이득·입출력 저항은? | 01(응용) |
| [06_dc_operating_point.md](06_dc_operating_point.md) | DC op pnt | `.op` | DC 동작점(Q-point)은? | 01 |
| [07_transient_frequency_response.md](07_transient_frequency_response.md) | Transient Frequency Response | `.fra` | 비선형 회로의 주파수 응답은? (고급) | (응용) |

## 권장 학습 순서

1. [06_dc_operating_point.md](06_dc_operating_point.md) — `.op` (모든 해석의 기초, 파라미터 없음)
2. [01_transient.md](01_transient.md) — `.tran` (가장 많이 쓰는 해석)
3. [02_ac_analysis.md](02_ac_analysis.md) — `.ac` (Bode Plot)
4. [03_dc_sweep.md](03_dc_sweep.md) — `.dc` (I-V 곡선)
5. 이후 선택: `.noise`, `.tf`, `.fra`

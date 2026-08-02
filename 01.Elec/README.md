# 전자 소자의 기본 원리와 LTspice 시뮬레이션 교육자료

**대상**: 임베디드/전자공학 입문자 (직업훈련·고등학생 수준) <br>
**작성**: Multimix / 광주인력개발원 교육과정 <br>
**도구**: LTspice (Analog Devices 공식 배포, 무료) — 최신 버전(24/26, `LTspice64`) 권장, LTspice XVII와도 완전 호환 <br>

---

## 학습 순서 (순서대로 진행)

| 단계 | 문서 | 내용 |
|---|---|---|
| 0 | **이 문서 (README.md)** | 개요 + LTspice 설치 |
| 1 | [01_basics_ui.md](01_basics_ui.md) | LTspice 기본 사용법 (UI 중심) |
| 2 | [01.Analysis/README.md](01.Analysis/README.md) | Analysis(해석) 종류 상세 — `.op`/`.tran`/`.ac`/`.dc` 등 |
| 3 | [02.Chapter/](02.Chapter/) | 챕터별 실습 — 실습 01~13 (이론 + UI 절차 포함) |

> **진행 방식**: 설치 → 기본 사용법 → 해석 종류 이해 → 실습 파일을 더블클릭으로 열어 실행.

---

## 실습 파일 목록 (더블클릭으로 바로 실행)

> `02.Chapter/` 폴더의 `01~13_*.asc` 파일은 **시뮬레이션 지시어가 이미 포함된 완성 회로**다.
> 각 예제의 **이론 + UI 진행 절차**는 우측 실습 문서에 상세히 설명되어 있다.

| # | 파일 | 내용 | 해석 종류 | 실습 문서 |
|---|---|---|---|---|
| 1 | `01_voltage_divider.asc` | 저항 전압 분배기 | `.op` | [실습01](02.Chapter/실습01_전압_분배기.md) |
| 2 | `02_RC_charge_discharge.asc` | RC 충방전 | `.tran` | [실습02](02.Chapter/실습02_RC_충방전.md) |
| 3 | `03_RC_lowpass_filter.asc` | RC 저역통과필터 (Bode) | `.ac` | [실습03](02.Chapter/실습03_RC_저역통과필터.md) |
| 4 | `04_RL_transient.asc` | RL 과도응답/역기전력 | `.tran` | [실습04](02.Chapter/실습04_RL_과도응답.md) |
| 5 | `05_LC_resonance.asc` | LC 공진 | `.ac` | [실습05](02.Chapter/실습05_LC_공진.md) |
| 6 | `06_diode_IV_curve.asc` | 다이오드 I-V 특성 | `.dc` | [실습06](02.Chapter/실습06_다이오드_IV_곡선.md) |
| 7 | `07_halfwave_rectifier.asc` | 반파 정류 | `.tran` | [실습07](02.Chapter/실습07_반파_정류.md) |
| 8 | `08_zener_regulator.asc` | 제너 정전압 | `.dc` | [실습08](02.Chapter/실습08_제너_정전압.md) |
| 9 | `09_BJT_switch_LED.asc` | NPN 스위치 (LED) | `.tran` | [실습09](02.Chapter/실습09_NPN_스위치.md) |
| 10 | `10_BJT_common_emitter_amp.asc` | 공통 이미터 증폭기 | `.tran` | [실습10](02.Chapter/실습10_공통_이미터_증폭기.md) |
| 11 | `11_MOSFET_switch.asc` | MOSFET 스위치 | `.tran` | [실습11](02.Chapter/실습11_MOSFET_스위치.md) |
| 12 | `12_MOSFET_IV_curve.asc` | MOSFET I-V 곡선 | `.dc` | [실습12](02.Chapter/실습12_MOSFET_IV_곡선.md) |
| 13 | `13_chopper_motor_driver.asc` | 초퍼 모터 드라이버 (VT6-mini 연계) | `.tran` | [실습13](02.Chapter/실습13_초퍼_모터_드라이버.md) |

---

## 0. LTspice 설치 (상세)

### 0.1 시스템 요구사항

| 항목 | 요구사항 |
|---|---|
| OS | Windows 10/11 (64비트) 권장. macOS 지원. Linux는 공식 미지원(Wine 가능) |
| 저장 공간 | 설치 파일 약 178MB + 설치 후 약 500MB |
| 메모리 | 4GB 이상 권장 (간단한 실습 회로는 2GB도 가능) |
| 인터넷 | 다운로드/모델 라이브러리 최초 업데이트 시 필요 |

### 0.2 다운로드

1. 브라우저로 **공식 사이트** 접속: `https://www.analog.com/ltspice`
2. 페이지의 **Download LTspice** 영역에서 본인 OS 선택:
   - Windows 10/11 64비트 → **Download for Windows 10/11 x64** → `LTspice64.msi` 다운로드
   - macOS → **Download for macOS**
   - 과거 버전(LTspice XVII)은 지원 종료. 특별한 이유가 없으면 최신 버전 사용
3. 파일 크기가 약 178MB이므로 다운로드 완료를 확인한 뒤 진행

> 참고: 검색엔진 광고/유사 사이트가 아닌 **반드시 analog.com** 에서만 다운로드할 것.
> LTspice는 공식적으로 무료이며, 설치 파일 자체는 인터넷 없이도 재배포 가능하다.

### 0.3 설치 (Windows 기준)

1. 다운로드한 `LTspice64.msi`를 **더블클릭**
2. Windows 보안 경고(UAC)가 뜨면 **[예]** 클릭
3. 설치 마법사 순서:
   - **Next** → 설치 유형 선택 (**Everyone** 권장) → Next
   - 설치 위치는 기본값 `C:\Program Files\ADI\LTspice` 유지 권장
   - **Install** → 완료 표시 → **Finish**
4. 설치 확인: **시작 메뉴 → "LTspice" 검색** → 실행
   (바탕화면에 `LTspice` 바로가기가 생성됨)

### 0.4 최초 실행 및 환경 확인

1. 첫 실행 시 **사용 약관 동의** 화면 → **[Accept]** 클릭
2. **Tools > Update Components** 실행 → 최신 모델 라이브러리 업데이트 (인터넷 필요, 최초 1회)
3. `.asc` 파일 연결 설정(한 번만):
   - `02.Chapter/01_voltage_divider.asc` 우클릭 → **연결 프로그램 → LTspice** → **"항상 이 앱 사용"** 체크
4. 정상 동작 확인: 예제 파일을 더블클릭해 열리고, **▶(Run) 버튼**이 보이는지 확인

### 0.5 실습실(학원) 일괄 배포 팁

- `LTspice64.msi` 하나만 USB로 복사하면 **인터넷 없이 전 교실 설치** 가능
- 설치 후 최초 1회만 인터넷으로 `Update Components` 실행 (못 하면 대부분 모델이 내장되어 있어 실습 진행 가능)
- 학생별 계정이 다른 PC라면 설치 유형을 **Everyone**으로 선택

### 0.6 설치/실행 문제 해결

| 증상 | 해결 |
|---|---|
| `.asc` 더블클릭해도 안 열림 | 0.4의 연결 프로그램 설정, 또는 LTspice에서 **File > Open** |
| 파일을 저장/열 때 오류 | 한글·특수문자 **경로** 문제 → 영문 경로(예: `C:\LTspice_work`)로 복사 |
| "Unknown subcircuit" 모델 오류 | **Tools > Update Components** 실행 후 재시뮬레이션 |
| 실행 즉시 종료됨 | 보안 S/W 확인, 다른 버전(XVII 또는 최신) 설치 시도 |

---
[다음: 1. LTspice 기본 사용법](01_basics_ui.md)

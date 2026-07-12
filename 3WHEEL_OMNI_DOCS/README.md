# 3휠 옴니 구동 로봇 - 키나마틱 모델 구현

## NUCLEO-STM32F103RB + RB-35GM 모터 + L298P 드라이버

---

## 1. 시스템 개요

### 1.1 대상 하드웨어

| 구성요소 | 사양 |
|----------|------|
| **MCU** | NUCLEO-F103RB (STM32F103RBT6, ARM Cortex-M3, 64MHz) |
| **모터** | RB-35GM 11TYPE, DC 12V, 1/50 기어박스 |
| **휠** | 58mm 플라스틱 옴니휠 (Lego/BO/Servo 호환) |
| **드라이버** | L298P (ST) 듀얼 H-브릿지 x3, PWM+DIR 방식 |
| **인코더** | 모터축 쿼드란처 인코더, 11 PPR |

### 1.2 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                  NUCLEO-F103RB                       │
│                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ UART 명령│  │   키나마틱    │  │  모터 제어    │ │
│  │ (USART2) │→ │  FK + IK     │→ │  PWM + DIR    │ │
│  └──────────┘  └──────────────┘  └───────────────┘ │
│       ↑               ↑                   ↓          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ 시리얼   │  │   오도메트리  │  │   L298P x3    │ │
│  │ 터미널   │  │ (데드 레커닝) │  │  (모터 3개)   │ │
│  └──────────┘  └──────────────┘  └───────┬───────┘ │
│         ↑                                ↓          │
│  ┌──────────────────────────────────────────────┐   │
│  │        인코더 읽기 (TIM1/2/4)                │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │                    │                │
    ┌────┴────┐         ┌────┴────┐      ┌────┴────┐
    │ 모터 0  │         │ 모터 1  │      │ 모터 2  │
    │  전방   │         │ 좌후방  │      │ 우후방  │
    │  (90°)  │         │ (210°)  │      │ (330°)  │
    └────┬────┘         └────┬────┘      └────┬────┘
         │                    │                │
    ┌────┴────┐         ┌────┴────┐      ┌────┴────┐
    │ 옴니    │         │ 옴니    │      │ 옴니    │
    │  휠     │         │  휠     │      │  휠     │
    │  58mm   │         │  58mm   │      │  58mm   │
    └─────────┘         └─────────┘      └─────────┘
```

---

## 2. 키나마틱 모델 이론

### 2.1 로봇 좌표계

```
            Y (좌측)
            ^
            |
            |   모터 0 (전방, 90°)
            |      ○
            |
            |
  ──────────+──────────→ X (전방)
           / \
          /   \
     ○           ○
  모터 1      모터 2
  (210°)      (330°)
```

- **X축**: 로봇 전진 방향
- **Y축**: 로봇 좌측 방향 (X에 수직)
- **회전**: 반시계방향(CCW)이 양수
- 3개 휠이 **120°** 간격으로 배치

### 2.2 기구학적 파라미터

| 파라미터 | 기호 | 값 | 설명 |
|----------|------|-----|------|
| 휠 반경 | `r` | 29 mm | 58mm 지름 / 2 |
| 휠베이스 반경 | `R` | 100 mm | 중심 ~ 휠 접촉점 거리 |
| 기어비 | `N` | 1/50 | RB-35GM 기어박스 |
| 인코더 CPR | `CPR` | 2200 | 11 PPR × 4 (쿼드란처) × 50 (기어) |
| 최대 출력 RPM | | 120 RPM | 12V 무부하 |
| PWM 주파수 | | 20 kHz | 가청주파수 이상 |

### 2.3 인코더 해상도 계산

```
모터축:         11 PPR (한 회전당 펄스 수)
쿼드란처 디코드: 11 × 4 = 44 카운트/모터 1회전
1/50 기어 후:   44 × 50 = 2200 카운트/출력축 1회전
라디안당:       2200 / (2π) ≈ 350.14 카운트/라디안
```

---

## 3. 역키나마틱 (Inverse Kinematics, IK)

### 3.1 목적

목표 로봇 본체 속도 `(vx, vy, ωz)`로부터, 각 휠이 달성해야 하는 선속도를 계산한다.

### 3.2 수학적 유도

각 휠은 진행 방향으로 로봇의 속도를 제약한다. X축에서 각도 `θi`인 휠 `i`에 대해:

```
v_wheel_i = -sin(θi) · vx + cos(θi) · vy + R · ωz
```

여기서:
- `v_wheel_i` = 휠 `i`의 선속도 [m/s]
- `θi` = 로봇 X축에서 휠 `i`까지의 각도
- `R` = 휠베이스 반경
- `(vx, vy, ωz)` = 로봇 본체 속도

### 3.3 휠 각도 정의

| 휠 | θ (도) | θ (라디안) | sin(θ) | cos(θ) |
|----|--------|-----------|--------|--------|
| 모터 0 | 90° | π/2 | 1.0 | 0.0 |
| 모터 1 | 210° | 7π/6 | -0.5 | -0.866 |
| 모터 2 | 330° | 11π/6 | -0.5 | 0.866 |

### 3.4 전개된 IK 방정식

휠 각도를 대입하면:

```
v0 = -vx + 0·vy + R·ωz       = -vx + R·ωz
v1 = 0.5·vx - 0.866·vy + R·ωz
v2 = 0.5·vx + 0.866·vy + R·ωz
```

### 3.5 코드 구현

```c
// omni_kinematic.c: Omni_InverseKinematics()
float v0 = (-SIN_90  * vx + COS_90  * vy + R * omega);
float v1 = (-SIN_210 * vx + COS_210 * vy + R * omega);
float v2 = (-SIN_330 * vx + COS_330 * vy + R * omega);

motors[MOTOR_0].target_speed = v0;
motors[MOTOR_1].target_speed = v1;
motors[MOTOR_2].target_speed = v2;
```

---

## 4. 정키나마틱 (Forward Kinematics, FK)

### 4.1 목적

인코더로 측정한 휠 속도 `(w0, w1, w2)`로부터, 로봇의 실제 본체 속도 `(vx, vy, ωz)`를 계산한다.

### 4.2 수학적 유도

IK 행렬 방정식으로부터 시작:

```
[v0]   [-sin(θ0)   cos(θ0)   R] [vx ]
[v1] = [-sin(θ1)   cos(θ1)   R] [vy ]
[v2]   [-sin(θ2)   cos(θ2)   R] [ωz ]
```

`(vx, vy, ωz)`를 풀어냄:

**세 방정식을 모두 더함:**
```
v0 + v1 + v2 = 0·vx + 0·vy + 3R·ωz
→ ωz = (v0 + v1 + v2) / (3R)
```

**v1을 v2에서 뺌:**
```
v2 - v1 = 0·vx + √3·vy + 0·ωz
→ vy = (v2 - v1) / √3
```

**0번 방정식으로부터:**
```
v0 = -vx + R·ωz
vx = -v0 + R·ωz = -v0 + (v0 + v1 + v2)/3 = (-2v0 + v1 + v2)/3
```

### 4.3 최종 FK 방정식

```
vx    = (r/3) · (-2·w0 + w1 + w2)
vy    = (r/√3) · (w2 - w1)
ωz    = (r/(3·R)) · (w0 + w1 + w2)
```

여기서 `w0, w1, w2`는 측정된 휠 선속도 [m/s].

### 4.4 코드 구현

```c
// omni_kinematic.c: Omni_ForwardKinematics()
robot->vx    = r_over_3 * (-2.0f * w0 + w1 + w2);
robot->vy    = r_over_3 * (w2 - w1) * TWO_OVER_SQRT3;
robot->omega = (r / (3.0f * R)) * (w0 + w1 + w2);
```

---

## 5. 오도메트리 (데드 레커닝)

### 5.1 적분 방법

본체 좌표계에서 오일러 적분을 수행한 후, 글로벌 좌표계로 회전:

```
x_new     = x_old     + (vx·cos(θ) - vy·sin(θ)) · dt
y_new     = y_old     + (vx·sin(θ) + vy·cos(θ)) · dt
theta_new = theta_old + ωz · dt
```

### 5.2 쎄타 정규화

드리프트 방지를 위해 쎄타를 `[-π, π]` 범위로 정규화:
```c
while (theta > π)  theta -= 2π;
while (theta < -π) theta += 2π;
```

### 5.3 한계점

데드 레커닝은 다음 요인으로 인해 시간이 지남에 따라 오차가 누적됨:
- 휠 미끄러짐
- 인코더 해상도 한계
- 기계 공차
- 바닥 표면 상태 변화

장기적인 정확한 위치 추정을 위해서는 IMU 또는 기타 센서 추가를 고려해야 함.

---

## 6. 모터 제어

### 6.1 L298P 드라이버 인터페이스

각 L298P 모듈이 하나의 모터를 제어:

| L298P 핀 | STM32 핀 | 기능 |
|----------|---------|------|
| ENA | PA6 (TIM3_CH1) | PWM 속도 제어 |
| IN1 | PB12 | 방향 A |
| IN2 | PB15 | 방향 B (항상 IN1의 반대) |

**L298P 진리표 (PWM+DIR 방식):**

| ENA (PWM) | IN1 | IN2 | 모터 상태 |
|-----------|-----|-----|----------|
| 듀티 | H | L | 전진 (속도 = 듀티%) |
| 듀티 | L | H | 후진 (속도 = 듀티%) |
| 0 | L | L | 코스트 (자유 정지) |
| 1 | H | H | 브레이크 (급정지) |

### 6.2 속도 → PWM 변환

```c
// 목표 속도 [m/s]를 PWM 듀티 [0..PWM_PERIOD]로 변환
float ratio = fabsf(speed) / MOTOR_MAX_SPEED_MS;
pwm_duty = (uint16_t)(ratio * PWM_PERIOD);

// 방향 설정
if (speed > 0) { IN1=HIGH; IN2=LOW; }   // 전진
if (speed < 0) { IN1=LOW;  IN2=HIGH; }  // 후진
if (speed == 0) { IN1=LOW; IN2=LOW; }   // 코스트
```

### 6.3 타이머 할당

| 타이머 | 타입 | 기능 | 클럭 | 해상도 |
|--------|------|------|------|--------|
| TIM1 | 고급 | 인코더 2 (모터 2) | 64 MHz | 16비트 |
| TIM2 | 범용 (32비트) | 인코더 0 (모터 0) | 64 MHz | 32비트 |
| TIM3 | 범용 (16비트) | PWM 출력 (3채널) | 64 MHz | 16비트 |
| TIM4 | 범용 (16비트) | 인코더 1 (모터 1) | 64 MHz | 16비트 |

### 6.4 PWM 설정

```
타이머 클럭:   64 MHz (APB1 타이머, 2× 프리스케일러)
PWM 주파수:    20 kHz
프리스케일러:  0
ARR (주기):    64,000,000 / 20,000 - 1 = 3,199
해상도:        12비트 유효 (0 ~ 3199)
```

### 6.5 인코더 설정

```
모드:              TI12 (양 채널, 양 엣지 = 4× 쿼드란처)
유효 CPR:          2200 카운트/출력축 1회전
읽기 주기:         10 ms
최대 카운트/루프:   ~44 (최대 속도 시)
카운터 타입:       프리런닝 (부호없음), 델타는 소프트웨어로 계산
```

---

## 7. 핀 할당 (NUCLEO-F103RB)

### 7.1 전체 핀 맵

| 핀 | AF/모드 | 기능 | 방향 |
|----|---------|------|------|
| PA0 | TIM2_CH1 | 인코더 0 Ch A | 입력 |
| PA1 | TIM2_CH2 | 인코더 0 Ch B | 입력 |
| PA2 | USART2_TX | 디버그 UART TX | AF 출력 |
| PA3 | USART2_RX | 디버그 UART RX | 입력 |
| PA5 | GPIO | LD2 (보드 내장 LED) | 출력 |
| PA6 | TIM3_CH1 | 모터 0 PWM (ENA) | AF 출력 |
| PA7 | TIM3_CH2 | 모터 1 PWM (ENA) | AF 출력 |
| PA8 | TIM1_CH1 | 인코더 2 Ch A | 입력 |
| PA9 | TIM1_CH2 | 인코더 2 Ch B | 입력 |
| PA13 | SWDIO | SWD 디버그 | AF |
| PA14 | SWCLK | SWD 디버그 | AF |
| PB0 | TIM3_CH3 | 모터 2 PWM (ENA) | AF 출력 |
| PB3 | SWO | SWD 트레이스 | AF |
| PB6 | TIM4_CH1 | 인코더 1 Ch A | 입력 |
| PB7 | TIM4_CH2 | 인코더 1 Ch B | 입력 |
| PB12 | GPIO | 모터 0 IN1 | 출력 |
| PB13 | GPIO | 모터 1 IN1 | 출력 |
| PB14 | GPIO | 모터 2 IN1 | 출력 |
| PB15 | GPIO | 모터 0 IN2 | 출력 |
| PC6 | GPIO | 모터 1 IN2 | 출력 |
| PC7 | GPIO | 모터 2 IN2 | 출력 |
| PC13 | EXTI | 파란색 버튼 (B1) | 입력 |

### 7.2 L298P 배선도

```
                    NUCLEO-F103RB
                 ┌────────────────┐
                 │                │
    모터 0 ◄────│ PA6 (TIM3_CH1)│ ENA
    L298P  ◄────│ PB12          │ IN1
           ◄────│ PB15          │ IN2
                 │                │
    모터 1 ◄────│ PA7 (TIM3_CH2)│ ENA
    L298P  ◄────│ PB13          │ IN1
           ◄────│ PC6           │ IN2
                 │                │
    모터 2 ◄────│ PB0 (TIM3_CH3)│ ENA
    L298P  ◄────│ PB14          │ IN1
           ◄────│ PC7           │ IN2
                 │                │
    인코더0 ────►│ PA0 (TIM2_CH1)│ Ch A
           ────►│ PA1 (TIM2_CH2)│ Ch B
                 │                │
    인코더1 ────►│ PB6 (TIM4_CH1)│ Ch A
           ────►│ PB7 (TIM4_CH2)│ Ch B
                 │                │
    인코더2 ────►│ PA8 (TIM1_CH1)│ Ch A
           ────►│ PA9 (TIM1_CH2)│ Ch B
                 │                │
    디버그  ◄───►│ PA2/PA3       │ USART2
                 └────────────────┘
```

---

## 8. UART 명령어 인터페이스

### 8.1 프로토콜

- **보드레이트**: 115200
- **포맷**: ASCII 텍스트, `\r` 또는 `\n`으로 종료
- **응답**: 100ms마다 오도메트리 데이터 출력

### 8.2 사용 가능한 명령어

| 명령어 | 포맷 | 설명 | 예시 |
|--------|------|------|------|
| **V** | `V vx vy omega` | 속도 지정 (m/s, m/s, rad/s) | `V 0.1 0.0 0.5` |
| **S** | `S` | 모든 모터 정지 | `S` |
| **P** | `P` | 현재 오도메트리 출력 | `P` |
| **M** | `M idx speed` | 개별 모터 제어 | `M 0 0.2` |

### 8.3 사용 예시

```
> V 0.2 0.0 0.0      ← 전방 0.2 m/s로 이동
< ODO|x=0.000 y=0.000 th=0.00|VX=0.198 VY=0.001 W=0.002|E0=44 E1=43 E2=44
< ODO|x=0.002 y=0.000 th=0.00|VX=0.200 VY=-0.001 W=0.001|E0=88 E1=87 E2=88
...
> S                    ← 정지
> M 1 0.15            ← 모터 1만 전방 0.15 m/s
```

---

## 9. 제어 루프

### 9.1 타이밍

```
메인 루프:  while(1) { ... }     ← 딜레이 없음, HAL_GetTick() 폴링
  └─ 10ms마다:
       1. Motor_UpdateAllEncoders()    ← 모든 인코더 카운터 읽기
       2. Omni_ForwardKinematics()     ← 실제 속도 계산
       3. Omni_UpdateOdometry()        ← 위치 적분
       4. Omni_InverseKinematics()     ← 목표 휠 속도 계산
       5. Motor_SpeedControlStep()     ← 각 모터 P제어기
  └─ 100ms마다:
       UART_PrintOdometry()            ← 시리얼 터미널로 상태 전송
  └─ 약 50ms마다:
       HAL_GPIO_TogglePin(LED)         ← 하트비트 표시
```

### 9.2 속도 제어기 (P제어)

```c
오차 = 목표속도 - 실제속도;
출력 = Kp × 오차 + 피드포워드;
Motor_SetSpeed(idx, 출력);
```

| 파라미터 | 값 | 설명 |
|----------|-----|------|
| Kp | 500.0 | 비례 이득 |
| 피드포워드 | 0.0 | 오프셋 보상 |
| 업데이트 주기 | 100 Hz | 10ms 주기 |

---

## 10. 파일 구조

```
SMART_CAR_Base/
├── Core/
│   ├── Inc/
│   │   ├── main.h                     ← 모터 핀 정의 추가
│   │   ├── omni_config.h              ← 신규: 전체 하드웨어 설정
│   │   ├── motor.h                    ← 신규: 모터 제어 API
│   │   ├── omni_kinematic.h           ← 신규: 키나마틱 API
│   │   └── stm32f1xx_hal_conf.h       ← 수정: HAL_TIM 활성화
│   └── Src/
│       ├── main.c                     ← 수정: 제어 루프 + UART
│       ├── motor.c                    ← 신규: 모터 제어 구현
│       └── omni_kinematic.c           ← 신규: 키나마틱 구현
├── Drivers/
│   └── STM32F1xx_HAL_Driver/
│       ├── Inc/
│       │   ├── stm32f1xx_hal_tim.h    ← 추가: FW 저장소에서 복사
│       │   └── stm32f1xx_hal_tim_ex.h ← 추가: FW 저장소에서 복사
│       └── Src/
│           ├── stm32f1xx_hal_tim.c    ← 추가: FW 저장소에서 복사
│           └── stm32f1xx_hal_tim_ex.c ← 추가: FW 저장소에서 복사
└── Debug/
    └── Drivers/STM32F1xx_HAL_Driver/Src/
        └── subdir.mk                  ← 수정: TIM 파일을 빌드에 추가
```

### 10.1 신규 생성 파일

| 파일 | 라인 수 | 용도 |
|------|---------|------|
| `omni_config.h` | 139 | 하드웨어 설정 상수 |
| `motor.h` | 94 | 모터 제어 API 헤더 |
| `motor.c` | 337 | 모터 초기화, PWM, 인코더, 속도 제어 |
| `omni_kinematic.h` | 80 | 키나마틱 API 헤더 |
| `omni_kinematic.c` | 123 | FK, IK, 오도메트리 수학 |

### 10.2 기존 파일 수정

| 파일 | 변경 내용 |
|------|----------|
| `main.c` | include, 변수, 제어 루프, UART 핸들러 추가 |
| `main.h` | 모터 방향 핀 정의 추가 |
| `stm32f1xx_hal_conf.h` | `HAL_TIM_MODULE_ENABLED` 활성화 |
| `subdir.mk` | TIM 파일을 빌드 시스템에 등록 |

---

## 11. 빌드 오류 및 해결 방법

### 11.1 첫 번째 빌드: 84개 오류, 9개 경고

#### 근본 원인: HAL 타이머 모듈 미활성화

CubeMX로 생성된 프로젝트는 HAL 모듈의 일부만 활성화했다. TIM 모듈이 `stm32f1xx_hal_conf.h`에서 **주석 처리**되어 있었다:

```c
// 수정 전 (오류):
/*#define HAL_TIM_MODULE_ENABLED   */

// 수정 후 (해결):
#define HAL_TIM_MODULE_ENABLED
```

**84개 오류가 발생한 이유:**

`stm32f1xx_hal.h` 헤더는 `stm32f1xx_hal_conf.h`의 `#define` 플래그에 따라 하위 모듈을 조건부로 포함한다. `HAL_TIM_MODULE_ENABLED`가 없으면 `stm32f1xx_hal_tim.h` 파일이 포함되지 않아:

- `TIM_HandleTypeDef` - 정의되지 않음
- `TIM_OC_InitTypeDef` - 정의되지 않음
- `TIM_Encoder_InitTypeDef` - 정의되지 않음
- `HAL_TIM_PWM_Init()` - 암시적 선언
- `HAL_TIM_Encoder_Init()` - 암시적 선언
- `HAL_TIM_PWM_Start()` - 암시적 선언
- `HAL_TIM_Encoder_Start()` - 암시적 선언
- `__HAL_TIM_SET_COMPARE()` - 암시적 선언
- `__HAL_TIM_GET_COUNTER()` - 암시적 선언
- `TIM_CHANNEL_1/2/3/ALL` - 정의되지 않음
- `TIM_COUNTERMODE_UP` - 정의되지 않음
- `TIM_CLOCKDIVISION_DIV1` - 정의되지 않음
- `TIM_AUTORELOAD_PRELOAD_ENABLE/DISABLE` - 정의되지 않음
- `TIM_OCMODE_PWM1` - 정의되지 않음
- `TIM_OCPOLARITY_HIGH` - 정의되지 않음
- `TIM_OCFAST_DISABLE` - 정의되지 않음
- `TIM_ENCODERMODE_TI12` - 정의되지 않음
- `TIM_ICPOLARITY_RISING` - 정의되지 않음
- `TIM_ICSELECTION_DIRECTTI` - 정의되지 않음
- `TIM_ICPSC_DIV1` - 정의되지 않음

타이머 관련 타입, 매크로, 함수가 모두 누락됨.

#### 오류 연쇄 다이어그램

```
HAL_TIM_MODULE_ENABLED 미정의
    │
    ▼
stm32f1xx_hal_tim.h 미포함
    │
    ├──► TIM_HandleTypeDef 미정의
    │       └──► Motor_t 구조체 컴파일 불가
    │               └──► motor.h 손상
    │                       ├──► main.c 실패
    │                       ├──► motor.c 실패
    │                       └──► omni_kinematic.c 실패 (motor.h 포함)
    │
    ├──► TIM_CHANNEL_x 매크로 미정의
    │       └──► 모든 HAL_TIM_PWM/Encoder 호출 실패
    │
    └──► TIM_COUNTERMODE_x 매크로 미정의
            └──► 타이머 초기화 코드 실패
```

#### 추가 오류: `Error_Handler()` 선언 누락

`motor.c`가 `Error_Handler()`를 호출했지만 `motor.h → omni_config.h → stm32f1xx_hal.h`만 포함하였다. `Error_Handler()` 프로토타입은 `main.h`에 선언되어 있으며, 이는 포함되지 않았다.

**해결:** `motor.c`에 `#include "main.h"` 추가.

#### 추가 경고: 사용되지 않는 변수

```c
// omni_kinematic.c에 사용되지 않는 변수가 있었음:
float inv_r = 1.0f / r;   // ← 사용되지 않음

// 해결: 사용되지 않는 변수 제거
```

### 11.2 두 번째 빌드: `stm32f1xx_hal_tim.h: No such file or directory`

#### 근본 원인: HAL 드라이버 파일이 프로젝트에 없음

`stm32f1xx_hal_conf.h`에서 `HAL_TIM_MODULE_ENABLED`를 활성화했음에도 빌드가 실패했다. 실제 TIM HAL **드라이버 파일**이 CubeMX에 의해 프로젝트에 포함되지 않았기 때문이다.

CubeMX가 프로젝트를 생성할 때, 활성화된 모듈의 HAL 소스/헤더 파일만 복사한다. TIM이 생성 시 비활성화되어 있었으므로:

- `stm32f1xx_hal_tim.h` (헤더) - **프로젝트에 없음**
- `stm32f1xx_hal_tim.c` (소스) - **프로젝트에 없음**
- `stm32f1xx_hal_tim_ex.h` (헤더) - **프로젝트에 없음**
- `stm32f1xx_hal_tim_ex.c` (소스) - **프로젝트에 없음**

`hal_conf.h`는 `stm32f1xx_hal.h`에게 `#include "stm32f1xx_hal_tim.h"`를 지시하지만, 해당 파일이 프로젝트 디렉토리 트리에 존재하지 않는다.

또한 STM32CubeIDE 매니지드 빌드는 `subdir.mk` 파일을 사용하여 소스 파일을 **명시적으로 나열**한다. 파일을 디렉토리에 복사하는 것만으로는 부족하며, 빌드 시스템에도 등록해야 한다.

#### 해결 (2단계)

**1단계: STM32Cube FW 저장소에서 HAL TIM 드라이버 파일 복사**

원본: `STM32Cube\Repository\STM32Cube_FW_F1_V1.8.7\Drivers\STM32F1xx_HAL_Driver\`

```
Inc/stm32f1xx_hal_tim.h      → 프로젝트/Drivers/STM32F1xx_HAL_Driver/Inc/
Inc/stm32f1xx_hal_tim_ex.h   → 프로젝트/Drivers/STM32F1xx_HAL_Driver/Inc/
Src/stm32f1xx_hal_tim.c      → 프로젝트/Drivers/STM32F1xx_HAL_Driver/Src/
Src/stm32f1xx_hal_tim_ex.c   → 프로젝트/Drivers/STM32F1xx_HAL_Driver/Src/
```

**2단계: `Debug/Drivers/STM32F1xx_HAL_Driver/Src/subdir.mk`에 등록**

`C_SRCS`, `OBJS`, `C_DEPS`, `clean` 섹션에 추가:

```makefile
# C_SRCS에 추가:
../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.c \
../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.c \

# OBJS에 추가:
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.o \
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.o \

# C_DEPS에 추가:
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.d \
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.d \
```

### 11.3 모든 수정 사항 요약 (최종)

| # | 문제 | 파일 | 해결 |
|---|------|------|------|
| 1 | HAL_TIM_MODULE_ENABLED 주석 처리됨 | `stm32f1xx_hal_conf.h` | `#define` 주석 해제 |
| 2 | `Error_Handler()` 선언 누락 | `motor.c` | `#include "main.h"` 추가 |
| 3 | 사용되지 않는 변수 `inv_r` | `omni_kinematic.c` | 변수 제거 |
| 4 | **HAL TIM 드라이버 파일이 프로젝트에 없음** | `Drivers/STM32F1xx_HAL_Driver/` | FW 저장소에서 복사 |
| 5 | **TIM 파일이 빌드 시스템에 등록 안됨** | `Debug/.../subdir.mk` | C_SRCS/OBJS/C_DEPS에 추가 |

---

## 12. 설정 가이드

### 12.1 로봇에 맞게 조정해야 할 파라미터

최초 실행 전 `omni_config.h`에서 다음을 수정:

```c
// 1. 휠베이스 반경 - 실제 섀시에서 중심~휠 거리 측정
#define WHEELBASE_RADIUS_M  0.100f   // 실제 값으로 변경

// 2. 모터 방향 - 휠이 반대로 회전하면 부호 변경
#define MOTOR0_DIR_SIGN     +1       // 필요시 -1로 변경
#define MOTOR1_DIR_SIGN     +1
#define MOTOR2_DIR_SIGN     +1

// 3. 속도 제어기 이득 - 부드러운 동작 위해 튜닝
#define SPEED_CTRL_KP       500.0f   // 반응 느리면 증가, 진동하면 감소
```

### 12.2 테스트 체크리스트

1. **모터 방향 테스트**: `M 0 0.1`, `M 1 0.1`, `M 2 0.1`을 하나씩 전송. 각 모터가 전진 방향으로 회전해야 함. 반대로 회전하면 해당 `DIR_SIGN`의 부호를 변경.

2. **인코더 테스트**: `M 0 0.1`을 전송하고 오도메트리 출력의 `E0` 값을 관찰. 꾸준히 증가해야 함.

3. **키나마틱 테스트**: `V 0.1 0.0 0.0` - 로봇이 전진. `V 0.0 0.1 0.0` - 로봇이 좌측 이동. `V 0.0 0.0 1.0` - 로봇이 반시계 방향 회전.

---

## 13. 개정 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-07-13 | 1.0 | 최초 구현 |
| 2026-07-13 | 1.1 | HAL_TIM_MODULE_ENABLED 수정, main.h include 추가, 미사용 변수 제거 |
| 2026-07-13 | 1.2 | HAL TIM 드라이버 파일 추가, subdir.mk 빌드 시스템 등록 |

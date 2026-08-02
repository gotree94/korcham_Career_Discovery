# 3-Wheel Omni Drive Robot - Kinematic Model Implementation

## NUCLEO-STM32F103RB + RB-35GM Motor + L298P Driver

---

## 1. System Overview

### 1.1 Target Hardware

| Component | Specification |
|-----------|--------------|
| **MCU** | NUCLEO-F103RB (STM32F103RBT6, ARM Cortex-M3, 64MHz) |
| **Motor** | RB-35GM 11TYPE, DC 12V, 1/50 Gearbox |
| **Wheel** | 58mm Plastic Omni Wheel (Lego/BO/Servo compatible) |
| **Driver** | L298P (ST) Dual H-Bridge x3, PWM+DIR mode |
| **Encoder** | Motor shaft quadrature encoder, 11 PPR |

### 1.2 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  NUCLEO-F103RB                       │
│                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ UART Cmd │  │  Kinematics  │  │ Motor Control │ │
│  │ (USART2) │→ │  FK + IK     │→ │  PWM + DIR    │ │
│  └──────────┘  └──────────────┘  └───────────────┘ │
│       ↑               ↑                   ↓          │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ Serial   │  │  Odometry    │  │   L298P x3    │ │
│  │ Terminal │  │ (Dead Reckon)│  │  (3 Motors)   │ │
│  └──────────┘  └──────────────┘  └───────┬───────┘ │
│         ↑                                ↓          │
│  ┌──────────────────────────────────────────────┐   │
│  │          Encoder Reading (TIM1/2/4)          │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │                    │                │
    ┌────┴────┐         ┌────┴────┐      ┌────┴────┐
    │ Motor 0 │         │ Motor 1 │      │ Motor 2 │
    │Front-L  │         │Front-R  │      │ Rear-C  │
    │ (150°)  │         │  (30°)  │      │ (270°)  │
    └────┬────┘         └────┬────┘      └────┬────┘
         │                    │                │
    ┌────┴────┐         ┌────┴────┐      ┌────┴────┐
    │ Omni    │         │ Omni    │      │ Omni    │
    │ Wheel   │         │ Wheel   │      │ Wheel   │
    │  58mm   │         │  58mm   │      │  58mm   │
    └─────────┘         └─────────┘      └─────────┘
```

---

## 2. Kinematic Model Theory

### 2.1 Robot Coordinate System

```
            Y (Left)
            ^
            |
  (150°) ○  |  ○ (30°)
  Motor 0   |   Motor 1
            |
  ──────────+──────────→ X (Forward)
            |
            |
            |      ○
            |   Motor 2
            |  (270°)
```

- **X-axis**: Forward direction of the robot
- **Y-axis**: Left direction (perpendicular to X)
- **Rotation**: Counter-clockwise (CCW) is positive
- All three wheels are spaced at **120°** intervals
- **Y-shape layout**: 2 wheels front (left + right), 1 wheel rear (center)

### 2.2 Mechanical Parameters

| Parameter | Symbol | Value | Description |
|-----------|--------|-------|-------------|
| Wheel radius | `r` | 29 mm | 58mm diameter / 2 |
| Wheelbase radius | `R` | 100 mm | Center to wheel contact point |
| Gear ratio | `N` | 1/50 | RB-35GM gearbox |
| Encoder CPR | `CPR` | 2200 | 11 PPR × 4 (quadrature) × 50 (gear) |
| Max output RPM | | 120 RPM | At 12V no-load |
| PWM frequency | | 20 kHz | Above audible range |

### 2.3 Encoder Resolution Calculation

```
Motor shaft:       11 PPR (pulses per revolution)
Quadrature decode: 11 × 4 = 44 counts/motor revolution
After 1/50 gear:   44 × 50 = 2200 counts/output revolution
Per radian:        2200 / (2π) ≈ 350.14 counts/radian
```

---

## 3. Inverse Kinematics (IK)

### 3.1 Purpose

Given a desired robot body velocity `(vx, vy, ωz)`, compute the linear velocity each wheel needs to achieve.

### 3.2 Mathematical Derivation

Each wheel constrains the robot's velocity along its rolling direction. For wheel `i` at angle `θi` from the X-axis:

```
v_wheel_i = -sin(θi) · vx + cos(θi) · vy + R · ωz
```

Where:
- `v_wheel_i` = linear velocity of wheel `i` [m/s]
- `θi` = angle of wheel `i` from robot X-axis
- `R` = wheelbase radius
- `(vx, vy, ωz)` = robot body velocity

### 3.3 Wheel Angle Definitions

| Wheel | θ (degrees) | θ (radians) | sin(θ) | cos(θ) |
|-------|-------------|-------------|--------|--------|
| Motor 0 | 150° | 5π/6 | 0.5 | -0.866 |
| Motor 1 | 30° | π/6 | 0.5 | 0.866 |
| Motor 2 | 270° | 3π/2 | -1.0 | 0.0 |

### 3.4 Expanded IK Equations

Substituting the wheel angles:

```
v0 = -0.5·vx - 0.866·vy + R·ωz
v1 = -0.5·vx + 0.866·vy + R·ωz
v2 =  vx                + R·ωz
```

### 3.5 Code Implementation

```c
// omni_kinematic.c: Omni_InverseKinematics()
float v0 = (-SIN_150 * vx + COS_150 * vy + R * omega);
float v1 = (-SIN_30  * vx + COS_30  * vy + R * omega);
float v2 = (-SIN_270 * vx + COS_270 * vy + R * omega);

motors[MOTOR_0].target_speed = v0;
motors[MOTOR_1].target_speed = v1;
motors[MOTOR_2].target_speed = v2;
```

---

## 4. Forward Kinematics (FK)

### 4.1 Purpose

Given measured wheel velocities `(w0, w1, w2)` from encoders, compute the robot's actual body velocity `(vx, vy, ωz)`.

### 4.2 Mathematical Derivation

Starting from the IK matrix equation:

```
[v0]   [-sin(θ0)   cos(θ0)   R] [vx ]
[v1] = [-sin(θ1)   cos(θ1)   R] [vy ]
[v2]   [-sin(θ2)   cos(θ2)   R] [ωz ]
```

Solving for `(vx, vy, ωz)`:

**Sum all three equations:**
```
v0 + v1 + v2 = 0·vx + 0·vy + 3R·ωz
→ ωz = (v0 + v1 + v2) / (3R)
```

**Subtract v0 from v1:**
```
v1 - v0 = 0·vx + √3·vy + 0·ωz
→ vy = (v1 - v0) / √3
```

**From equation 2:**
```
v2 = vx + R·ωz
vx = v2 - R·ωz = v2 - (v0 + v1 + v2)/3 = (-v0 - v1 + 2v2)/3
```

### 4.3 Final FK Equations

```
vx    = (r/3) · (-w0 - w1 + 2·w2)
vy    = (r/√3) · (w1 - w0)
ωz    = (r/(3·R)) · (w0 + w1 + w2)
```

Where `w0, w1, w2` are the measured wheel linear velocities [m/s].

### 4.4 Code Implementation

```c
// omni_kinematic.c: Omni_ForwardKinematics()
robot->vx    = r_over_3 * (-w0 - w1 + 2.0f * w2);
robot->vy    = r_over_3 * (w1 - w0) * TWO_OVER_SQRT3;
robot->omega = (r / (3.0f * R)) * (w0 + w1 + w2);
```

---

## 5. Odometry (Dead Reckoning)

### 5.1 Integration Method

Using Euler integration in the body frame, then rotating to the global frame:

```
x_new     = x_old     + (vx·cos(θ) - vy·sin(θ)) · dt
y_new     = y_old     + (vx·sin(θ) + vy·cos(θ)) · dt
theta_new = theta_old + ωz · dt
```

### 5.2 Theta Normalization

Theta is normalized to `[-π, π]` to prevent drift:
```c
while (theta > π)  theta -= 2π;
while (theta < -π) theta += 2π;
```

### 5.3 Limitations

Dead reckoning accumulates error over time due to:
- Wheel slippage
- Encoder resolution limits
- Mechanical tolerances
- Floor surface variations

For accurate long-term positioning, consider adding IMU or other sensors.

---

## 6. Motor Control

### 6.1 L298P Driver Interface

Each L298P module controls one motor:

| L298P Pin | STM32 Pin | Function |
|-----------|-----------|----------|
| ENA | PA6 (TIM3_CH1) | PWM speed control |
| IN1 | PB12 | Direction A |
| IN2 | PB15 | Direction B (always opposite of IN1) |

**L298P Truth Table (PWM+DIR mode):**

| ENA (PWM) | IN1 | IN2 | Motor State |
|-----------|-----|-----|-------------|
| Duty | H | L | Forward (speed = duty%) |
| Duty | L | H | Reverse (speed = duty%) |
| 0 | L | L | Coast (free stop) |
| 1 | H | H | Brake (fast stop) |

### 6.2 Speed to PWM Conversion

```c
// Convert desired speed [m/s] to PWM duty [0..PWM_PERIOD]
float ratio = fabsf(speed) / MOTOR_MAX_SPEED_MS;
pwm_duty = (uint16_t)(ratio * PWM_PERIOD);

// Set direction
if (speed > 0) { IN1=HIGH; IN2=LOW; }   // Forward
if (speed < 0) { IN1=LOW;  IN2=HIGH; }  // Reverse
if (speed == 0) { IN1=LOW; IN2=LOW; }   // Coast
```

### 6.3 Timer Allocation

| Timer | Type | Function | Clock | Resolution |
|-------|------|----------|-------|------------|
| TIM1 | Advanced | Encoder 2 (Motor 2) | 64 MHz | 16-bit |
| TIM2 | General (32-bit) | Encoder 0 (Motor 0) | 64 MHz | 32-bit |
| TIM3 | General (16-bit) | PWM outputs (3ch) | 64 MHz | 16-bit |
| TIM4 | General (16-bit) | Encoder 1 (Motor 1) | 64 MHz | 16-bit |

### 6.4 PWM Configuration

```
Timer clock:     64 MHz (APB1 timer, 2× prescaler)
PWM frequency:   20 kHz
Prescaler:       0
ARR (period):    64,000,000 / 20,000 - 1 = 3,199
Resolution:      12 bits effective (0 ~ 3199)
```

### 6.5 Encoder Configuration

```
Mode:            TI12 (both channels, both edges = 4× quadrature)
Effective CPR:   2200 counts/output revolution
Read period:     10 ms
Max counts/loop: ~44 (at max speed)
Counter type:    Free-running (unsigned), delta computed in software
```

---

## 7. Pin Assignment (NUCLEO-F103RB)

### 7.1 Complete Pin Map

| Pin | AF/Mode | Function | Direction |
|-----|---------|----------|-----------|
| PA0 | TIM2_CH1 | Encoder 0 Ch A | Input |
| PA1 | TIM2_CH2 | Encoder 0 Ch B | Input |
| PA2 | USART2_TX | Debug UART TX | AF Output |
| PA3 | USART2_RX | Debug UART RX | Input |
| PA5 | GPIO | LD2 (on-board LED) | Output |
| PA6 | TIM3_CH1 | Motor 0 PWM (ENA) | AF Output |
| PA7 | TIM3_CH2 | Motor 1 PWM (ENA) | AF Output |
| PA8 | TIM1_CH1 | Encoder 2 Ch A | Input |
| PA9 | TIM1_CH2 | Encoder 2 Ch B | Input |
| PA13 | SWDIO | SWD Debug | AF |
| PA14 | SWCLK | SWD Debug | AF |
| PB0 | TIM3_CH3 | Motor 2 PWM (ENA) | AF Output |
| PB3 | SWO | SWD Trace | AF |
| PB6 | TIM4_CH1 | Encoder 1 Ch A | Input |
| PB7 | TIM4_CH2 | Encoder 1 Ch B | Input |
| PB12 | GPIO | Motor 0 IN1 | Output |
| PB13 | GPIO | Motor 1 IN1 | Output |
| PB14 | GPIO | Motor 2 IN1 | Output |
| PB15 | GPIO | Motor 0 IN2 | Output |
| PC6 | GPIO | Motor 1 IN2 | Output |
| PC7 | GPIO | Motor 2 IN2 | Output |
| PC13 | EXTI | Blue Button (B1) | Input |

### 7.2 L298P Wiring Diagram

```
                    NUCLEO-F103RB
                 ┌────────────────┐
                 │                │
    Motor 0 ◄────│ PA6 (TIM3_CH1)│ ENA
    L298P  ◄────│ PB12          │ IN1
           ◄────│ PB15          │ IN2
                 │                │
    Motor 1 ◄────│ PA7 (TIM3_CH2)│ ENA
    L298P  ◄────│ PB13          │ IN1
           ◄────│ PC6           │ IN2
                 │                │
    Motor 2 ◄────│ PB0 (TIM3_CH3)│ ENA
    L298P  ◄────│ PB14          │ IN1
           ◄────│ PC7           │ IN2
                 │                │
    Enc 0  ─────►│ PA0 (TIM2_CH1)│ Ch A
           ─────►│ PA1 (TIM2_CH2)│ Ch B
                 │                │
    Enc 1  ─────►│ PB6 (TIM4_CH1)│ Ch A
           ─────►│ PB7 (TIM4_CH2)│ Ch B
                 │                │
    Enc 2  ─────►│ PA8 (TIM1_CH1)│ Ch A
           ─────►│ PA9 (TIM1_CH2)│ Ch B
                 │                │
    Debug  ◄────►│ PA2/PA3       │ USART2
                 └────────────────┘
```

---

## 8. UART Command Interface

### 8.1 Protocol

- **Baud rate**: 115200
- **Format**: ASCII text, terminated by `\r` or `\n`
- **Response**: Odometry data printed every 100ms

### 8.2 Available Commands

| Command | Format | Description | Example |
|---------|--------|-------------|---------|
| **V** | `V vx vy omega` | Set velocity (m/s, m/s, rad/s) | `V 0.1 0.0 0.5` |
| **S** | `S` | Stop all motors | `S` |
| **P** | `P` | Print current odometry | `P` |
| **M** | `M idx speed` | Manual motor control | `M 0 0.2` |

### 8.3 Example Session

```
> V 0.2 0.0 0.0      ← Move forward at 0.2 m/s
< ODO|x=0.000 y=0.000 th=0.00|VX=0.198 VY=0.001 W=0.002|E0=44 E1=43 E2=44
< ODO|x=0.002 y=0.000 th=0.00|VX=0.200 VY=-0.001 W=0.001|E0=88 E1=87 E2=88
...
> S                    ← Stop
> M 1 0.15            ← Motor 1 only, forward at 0.15 m/s
```

---

## 9. Control Loop

### 9.1 Timing

```
Main Loop:  while(1) { ... }     ← No delay, polls HAL_GetTick()
  └─ Every 10ms:
       1. Motor_UpdateAllEncoders()    ← Read all encoder counters
       2. Omni_ForwardKinematics()     ← Compute actual velocity
       3. Omni_UpdateOdometry()        ← Integrate position
       4. Omni_InverseKinematics()     ← Compute target wheel speeds
       5. Motor_SpeedControlStep()     ← P-controller for each motor
  └─ Every 100ms:
       UART_PrintOdometry()            ← Send status to serial terminal
  └─ Every ~50ms:
       HAL_GPIO_TogglePin(LED)         ← Heartbeat indicator
```

### 9.2 Speed Controller (P-Control)

```c
error = target_speed - actual_speed;
output = Kp × error + feedforward;
Motor_SetSpeed(idx, output);
```

| Parameter | Value | Description |
|-----------|-------|-------------|
| Kp | 500.0 | Proportional gain |
| Feedforward | 0.0 | Offset compensation |
| Update rate | 100 Hz | 10ms period |

---

## 10. File Structure

```
SMART_CAR_Base/
├── Core/
│   ├── Inc/
│   │   ├── main.h                     ← Added motor pin defines
│   │   ├── omni_config.h              ← NEW: All configuration
│   │   ├── motor.h                    ← NEW: Motor control API
│   │   ├── omni_kinematic.h           ← NEW: Kinematics API
│   │   └── stm32f1xx_hal_conf.h       ← MODIFIED: HAL_TIM enabled
│   └── Src/
│       ├── main.c                     ← MODIFIED: Control loop + UART
│       ├── motor.c                    ← NEW: Motor implementation
│       └── omni_kinematic.c           ← NEW: Kinematics implementation
├── Drivers/
│   └── STM32F1xx_HAL_Driver/
│       ├── Inc/
│       │   ├── stm32f1xx_hal_tim.h    ← ADDED: From FW repository
│       │   └── stm32f1xx_hal_tim_ex.h ← ADDED: From FW repository
│       └── Src/
│           ├── stm32f1xx_hal_tim.c    ← ADDED: From FW repository
│           └── stm32f1xx_hal_tim_ex.c ← ADDED: From FW repository
└── Debug/
    └── Drivers/STM32F1xx_HAL_Driver/Src/
        └── subdir.mk                  ← MODIFIED: Added TIM files to build
```

### 10.1 New Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `omni_config.h` | 139 | Hardware configuration constants |
| `motor.h` | 94 | Motor control API header |
| `motor.c` | 337 | Motor init, PWM, encoder, speed control |
| `omni_kinematic.h` | 80 | Kinematics API header |
| `omni_kinematic.c` | 123 | FK, IK, odometry math |

### 10.2 Existing Files Modified

| File | Changes |
|------|---------|
| `main.c` | Added includes, variables, control loop, UART handler |
| `main.h` | Added motor direction pin defines |
| `stm32f1xx_hal_conf.h` | Enabled `HAL_TIM_MODULE_ENABLED` |

---

## 11. Build Errors and Solutions

### 11.1 First Build: 84 Errors, 9 Warnings

#### Root Cause: HAL Timer Module Not Enabled

The CubeMX-generated project only enabled a subset of HAL modules. The TIM module was **commented out** in `stm32f1xx_hal_conf.h`:

```c
// BEFORE (broken):
/*#define HAL_TIM_MODULE_ENABLED   */

// AFTER (fixed):
#define HAL_TIM_MODULE_ENABLED
```

**Why this caused 84 errors:**

The `stm32f1xx_hal.h` header conditionally includes sub-modules based on `#define` flags in `stm32f1xx_hal_conf.h`. Without `HAL_TIM_MODULE_ENABLED`, the file `stm32f1xx_hal_tim.h` was never included, which meant:

- `TIM_HandleTypeDef` - undefined
- `TIM_OC_InitTypeDef` - undefined
- `TIM_Encoder_InitTypeDef` - undefined
- `HAL_TIM_PWM_Init()` - implicit declaration
- `HAL_TIM_Encoder_Init()` - implicit declaration
- `HAL_TIM_PWM_Start()` - implicit declaration
- `HAL_TIM_Encoder_Start()` - implicit declaration
- `__HAL_TIM_SET_COMPARE()` - implicit declaration
- `__HAL_TIM_GET_COUNTER()` - implicit declaration
- `TIM_CHANNEL_1/2/3/ALL` - undefined
- `TIM_COUNTERMODE_UP` - undefined
- `TIM_CLOCKDIVISION_DIV1` - undefined
- `TIM_AUTORELOAD_PRELOAD_ENABLE/DISABLE` - undefined
- `TIM_OCMODE_PWM1` - undefined
- `TIM_OCPOLARITY_HIGH` - undefined
- `TIM_OCFAST_DISABLE` - undefined
- `TIM_ENCODERMODE_TI12` - undefined
- `TIM_ICPOLARITY_RISING` - undefined
- `TIM_ICSELECTION_DIRECTTI` - undefined
- `TIM_ICPSC_DIV1` - undefined

Every single type, macro, and function related to timers was missing.

#### Error Cascade Diagram

```
HAL_TIM_MODULE_ENABLED not defined
    │
    ▼
stm32f1xx_hal_tim.h not included
    │
    ├──► TIM_HandleTypeDef undefined
    │       └──► Motor_t struct can't compile
    │               └──► motor.h broken
    │                       ├──► main.c fails
    │                       ├──► motor.c fails
    │                       └──► omni_kinematic.c fails (includes motor.h)
    │
    ├──► TIM_CHANNEL_x macros undefined
    │       └──► All HAL_TIM_PWM/Encoder calls fail
    │
    └──► TIM_COUNTERMODE_x macros undefined
            └──► Timer init code fails
```

#### Additional Error: Missing `Error_Handler()` Declaration

`motor.c` called `Error_Handler()` but only included `motor.h → omni_config.h → stm32f1xx_hal.h`. The `Error_Handler()` prototype is declared in `main.h`, which was not included.

**Fix:** Added `#include "main.h"` to `motor.c`.

#### Additional Warning: Unused Variable

```c
// omni_kinematic.c had an unused variable:
float inv_r = 1.0f / r;   // ← never used

// Fix: removed the unused variable
```

### 11.2 Second Build: `stm32f1xx_hal_tim.h: No such file or directory`

#### Root Cause: HAL Driver Files Missing from Project

Even after enabling `HAL_TIM_MODULE_ENABLED` in `stm32f1xx_hal_conf.h`, the build failed because the actual TIM HAL **driver files** were never included in the project by CubeMX.

When CubeMX generates a project, it only copies the HAL source/header files for the modules that are enabled. Since TIM was disabled at generation time:

- `stm32f1xx_hal_tim.h` (header) - **not in project**
- `stm32f1xx_hal_tim.c` (source) - **not in project**
- `stm32f1xx_hal_tim_ex.h` (header) - **not in project**
- `stm32f1xx_hal_tim_ex.c` (source) - **not in project**

The `hal_conf.h` tells `stm32f1xx_hal.h` to `#include "stm32f1xx_hal_tim.h"`, but that file doesn't exist in the project directory tree.

Additionally, the STM32CubeIDE managed build uses `subdir.mk` files that **explicitly list** every source file. Simply copying the files into the directory is not enough - they must also be registered in the build system.

#### Fix (2 steps)

**Step 1: Copy HAL TIM driver files from STM32Cube FW repository**

Source: `STM32Cube\Repository\STM32Cube_FW_F1_V1.8.7\Drivers\STM32F1xx_HAL_Driver\`

```
Inc/stm32f1xx_hal_tim.h      → project/Drivers/STM32F1xx_HAL_Driver/Inc/
Inc/stm32f1xx_hal_tim_ex.h   → project/Drivers/STM32F1xx_HAL_Driver/Inc/
Src/stm32f1xx_hal_tim.c      → project/Drivers/STM32F1xx_HAL_Driver/Src/
Src/stm32f1xx_hal_tim_ex.c   → project/Drivers/STM32F1xx_HAL_Driver/Src/
```

**Step 2: Register in `Debug/Drivers/STM32F1xx_HAL_Driver/Src/subdir.mk`**

Add to `C_SRCS`, `OBJS`, `C_DEPS`, and `clean` sections:

```makefile
# In C_SRCS:
../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.c \
../Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.c \

# In OBJS:
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.o \
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.o \

# In C_DEPS:
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim.d \
./Drivers/STM32F1xx_HAL_Driver/Src/stm32f1xx_hal_tim_ex.d \
```

### 11.3 Summary of All Fixes (Complete)

| # | Issue | File | Fix |
|---|-------|------|-----|
| 1 | HAL_TIM_MODULE_ENABLED commented out | `stm32f1xx_hal_conf.h` | Uncomment `#define` |
| 2 | Missing `Error_Handler()` declaration | `motor.c` | Add `#include "main.h"` |
| 3 | Unused variable `inv_r` | `omni_kinematic.c` | Remove the variable |
| 4 | **HAL TIM driver files not in project** | `Drivers/STM32F1xx_HAL_Driver/` | Copy from FW repository |
| 5 | **TIM files not in build system** | `Debug/.../subdir.mk` | Add to C_SRCS/OBJS/C_DEPS |

---

## 12. Configuration Guide

### 12.1 Parameters to Adjust for Your Robot

Before first run, modify these in `omni_config.h`:

```c
// 1. WHEELBASE RADIUS - Measure center-to-wheel distance on your chassis
#define WHEELBASE_RADIUS_M  0.100f   // Change to your actual value

// 2. MOTOR DIRECTION - If a wheel spins backward, flip the sign
#define MOTOR0_DIR_SIGN     +1       // Change to -1 if needed
#define MOTOR1_DIR_SIGN     +1
#define MOTOR2_DIR_SIGN     +1

// 3. SPEED CONTROLLER GAIN - Tune for smooth operation
#define SPEED_CTRL_KP       500.0f   // Increase if sluggish, decrease if oscillating
```

### 12.2 Testing Checklist

1. **Motor direction test**: Send `M 0 0.1`, `M 1 0.1`, `M 2 0.1` one at a time. Each motor should spin forward. If backward, flip the corresponding `DIR_SIGN`.

2. **Encoder test**: Send `M 0 0.1` and watch the `E0` value in the odometry output. It should increase steadily.

3. **Kinematics test**: Send `V 0.1 0.0 0.0` - robot should move forward. Send `V 0.0 0.1 0.0` - robot should strafe left. Send `V 0.0 0.0 1.0` - robot should rotate CCW.

---

## 13. Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-13 | 1.0 | Initial implementation |
| 2026-07-13 | 1.1 | Fixed HAL_TIM_MODULE_ENABLED, added main.h include, removed unused variable |

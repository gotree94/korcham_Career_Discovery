/**
 * @file    motor.h
 * @brief   Motor control API for 3-wheel omni robot with L298P driver
 */

#ifndef MOTOR_H
#define MOTOR_H

#include "omni_config.h"

/* Motor index */
typedef enum {
    MOTOR_0 = 0,
    MOTOR_1 = 1,
    MOTOR_2 = 2,
    MOTOR_COUNT = 3
} MotorIndex_t;

/* Motor state */
typedef struct {
    /* Hardware handles */
    TIM_HandleTypeDef   *htim_pwm;      /* Timer for PWM output */
    uint32_t             pwm_channel;    /* PWM channel */

    /* L298P direction pins */
    GPIO_TypeDef        *in1_port;
    uint16_t             in1_pin;
    GPIO_TypeDef        *in2_port;
    uint16_t             in2_pin;

    /* Encoder */
    TIM_HandleTypeDef   *htim_enc;      /* Timer for encoder input */
    int32_t              enc_count;      /* Current encoder count (signed) */
    int16_t              enc_delta;      /* Delta since last read */
    float                speed_mps;      /* Measured speed [m/s] */
    float                speed_rads;     /* Measured angular velocity [rad/s] */

    /* Control */
    float                target_speed;   /* Target speed [m/s] */
    int8_t               dir_sign;       /* +1 or -1 for direction correction */
    uint16_t             pwm_duty;       /* Current PWM duty [0..PWM_PERIOD] */
    int8_t               pwm_dir;        /* +1 forward, -1 reverse, 0 stop */
} Motor_t;

/* Global motor array (defined in motor.c) */
extern Motor_t g_motors[MOTOR_COUNT];

/**
 * @brief  Initialize all motor hardware (TIM PWM, GPIO, encoder timers)
 */
void Motor_InitAll(void);

/**
 * @brief  Start PWM output and encoder reading for all motors
 */
void Motor_StartAll(void);

/**
 * @brief  Set motor speed (open-loop)
 * @param  idx      Motor index (MOTOR_0, MOTOR_1, MOTOR_2)
 * @param  speed_ms Desired speed in m/s (positive = forward, negative = reverse)
 */
void Motor_SetSpeed(MotorIndex_t idx, float speed_ms);

/**
 * @brief  Stop all motors (coast)
 */
void Motor_StopAll(void);

/**
 * @brief  Read encoder delta for one motor
 * @param  idx  Motor index
 * @return Encoder delta counts since last read
 */
int16_t Motor_ReadEncoder(MotorIndex_t idx);

/**
 * @brief  Update all motor encoder readings and compute speeds
 *         Call this periodically (e.g. every ENCODER_UPDATE_MS)
 */
void Motor_UpdateAllEncoders(void);

/**
 * @brief  Apply closed-loop speed control for one motor (simple P controller)
 * @param  idx Motor index
 */
void Motor_SpeedControlStep(MotorIndex_t idx);

/**
 * @brief  Get the timer handle for PWM (TIM3)
 */
TIM_HandleTypeDef *Motor_GetPwmTimer(void);

#endif /* MOTOR_H */

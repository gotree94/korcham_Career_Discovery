/**
 * @file    motor.c
 * @brief   Motor control implementation for 3-wheel omni robot
 *          L298P driver: ENA=PWM, IN1/IN2=direction
 */

#include "motor.h"
#include "main.h"
#include <math.h>

/* ---------- Global Motor Instances ---------- */
Motor_t g_motors[MOTOR_COUNT];

/* Timer handles (allocated here) */
static TIM_HandleTypeDef htim_pwm;   /* TIM3 - PWM outputs */
static TIM_HandleTypeDef htim_enc0;  /* TIM2 - Encoder 0 (32-bit) */
static TIM_HandleTypeDef htim_enc1;  /* TIM4 - Encoder 1 */
static TIM_HandleTypeDef htim_enc2;  /* TIM1 - Encoder 2 */

/* Encoder shadow counters (for delta calculation) */
static int32_t enc0_prev = 0;
static int16_t enc1_prev = 0;
static int16_t enc2_prev = 0;

/*==========================================================================
 *  Clock Enable Helpers
 *==========================================================================*/
static void Motor_InitClocks(void)
{
    __HAL_RCC_TIM1_CLK_ENABLE();
    __HAL_RCC_TIM2_CLK_ENABLE();
    __HAL_RCC_TIM3_CLK_ENABLE();
    __HAL_RCC_TIM4_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
}

/*==========================================================================
 *  GPIO Initialization (L298P IN1/IN2 + PWM AF pins)
 *==========================================================================*/
static void Motor_InitGPIO(void)
{
    GPIO_InitTypeDef gpio = {0};

    /* --- PWM output pins (AF push-pull): PA6, PA7, PB0 --- */
    gpio.Mode  = GPIO_MODE_AF_PP;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;

    gpio.Pin   = GPIO_PIN_6 | GPIO_PIN_7;       /* PA6=TIM3_CH1, PA7=TIM3_CH2 */
    HAL_GPIO_Init(GPIOA, &gpio);

    gpio.Pin   = GPIO_PIN_0;                     /* PB0=TIM3_CH3 */
    HAL_GPIO_Init(GPIOB, &gpio);

    /* --- Direction output pins (push-pull) --- */
    gpio.Mode  = GPIO_MODE_OUTPUT_PP;
    gpio.Pull  = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_HIGH;

    /* Motor 0: IN1=PB12, IN2=PB15 */
    gpio.Pin = M0_IN1_PIN;
    HAL_GPIO_Init(M0_IN1_PORT, &gpio);
    gpio.Pin = M0_IN2_PIN;
    HAL_GPIO_Init(M0_IN2_PORT, &gpio);

    /* Motor 1: IN1=PB13, IN2=PC6 */
    gpio.Pin = M1_IN1_PIN;
    HAL_GPIO_Init(M1_IN1_PORT, &gpio);
    gpio.Pin = M1_IN2_PIN;
    HAL_GPIO_Init(M1_IN2_PORT, &gpio);

    /* Motor 2: IN1=PB14, IN2=PC7 */
    gpio.Pin = M2_IN1_PIN;
    HAL_GPIO_Init(M2_IN1_PORT, &gpio);
    gpio.Pin = M2_IN2_PIN;
    HAL_GPIO_Init(M2_IN2_PORT, &gpio);

    /* --- Encoder input pins (floating/pull-up) --- */
    gpio.Mode  = GPIO_MODE_INPUT;
    gpio.Pull  = GPIO_PULLUP;

    /* Encoder 0: PA0(TIM2_CH1), PA1(TIM2_CH2) */
    gpio.Pin = GPIO_PIN_0 | GPIO_PIN_1;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* Encoder 1: PB6(TIM4_CH1), PB7(TIM4_CH2) */
    gpio.Pin = GPIO_PIN_6 | GPIO_PIN_7;
    HAL_GPIO_Init(GPIOB, &gpio);

    /* Encoder 2: PA8(TIM1_CH1), PA9(TIM1_CH2) */
    gpio.Pin = GPIO_PIN_8 | GPIO_PIN_9;
    HAL_GPIO_Init(GPIOA, &gpio);
}

/*==========================================================================
 *  TIM3 - PWM Output (3 channels, 20kHz)
 *==========================================================================*/
static void Motor_InitPWM(void)
{
    htim_pwm.Instance           = TIM3;
    htim_pwm.Init.Prescaler     = 0;
    htim_pwm.Init.CounterMode   = TIM_COUNTERMODE_UP;
    htim_pwm.Init.Period        = PWM_PERIOD;
    htim_pwm.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim_pwm.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;

    if (HAL_TIM_PWM_Init(&htim_pwm) != HAL_OK) {
        Error_Handler();
    }

    TIM_OC_InitTypeDef oc = {0};
    oc.OCMode     = TIM_OCMODE_PWM1;
    oc.Pulse      = 0;
    oc.OCPolarity = TIM_OCPOLARITY_HIGH;
    oc.OCFastMode = TIM_OCFAST_DISABLE;

    if (HAL_TIM_PWM_ConfigChannel(&htim_pwm, &oc, TIM_CHANNEL_1) != HAL_OK) Error_Handler();
    if (HAL_TIM_PWM_ConfigChannel(&htim_pwm, &oc, TIM_CHANNEL_2) != HAL_OK) Error_Handler();
    if (HAL_TIM_PWM_ConfigChannel(&htim_pwm, &oc, TIM_CHANNEL_3) != HAL_OK) Error_Handler();
}

/*==========================================================================
 *  Encoder Timer Init (TIM1, TIM2, TIM4)
 *==========================================================================*/
static void Motor_InitEncoders(void)
{
    TIM_Encoder_InitTypeDef enc = {0};

    enc.EncoderMode  = TIM_ENCODERMODE_TI12;
    enc.IC1Polarity  = TIM_ICPOLARITY_RISING;
    enc.IC1Selection  = TIM_ICSELECTION_DIRECTTI;
    enc.IC1Prescaler = TIM_ICPSC_DIV1;
    enc.IC1Filter    = 0x03;
    enc.IC2Polarity  = TIM_ICPOLARITY_RISING;
    enc.IC2Selection  = TIM_ICSELECTION_DIRECTTI;
    enc.IC2Prescaler = TIM_ICPSC_DIV1;
    enc.IC2Filter    = 0x03;

    /* Encoder 0: TIM2 (32-bit) */
    htim_enc0.Instance             = TIM2;
    htim_enc0.Init.Prescaler       = 0;
    htim_enc0.Init.CounterMode     = TIM_COUNTERMODE_UP;
    htim_enc0.Init.Period          = 0xFFFFFFFF;
    htim_enc0.Init.ClockDivision   = TIM_CLOCKDIVISION_DIV1;
    htim_enc0.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Encoder_Init(&htim_enc0, &enc) != HAL_OK) Error_Handler();

    /* Encoder 1: TIM4 (16-bit) */
    htim_enc1.Instance             = TIM4;
    htim_enc1.Init.Prescaler       = 0;
    htim_enc1.Init.CounterMode     = TIM_COUNTERMODE_UP;
    htim_enc1.Init.Period          = 0xFFFF;
    htim_enc1.Init.ClockDivision   = TIM_CLOCKDIVISION_DIV1;
    htim_enc1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Encoder_Init(&htim_enc1, &enc) != HAL_OK) Error_Handler();

    /* Encoder 2: TIM1 (16-bit, advanced timer in encoder mode) */
    htim_enc2.Instance             = TIM1;
    htim_enc2.Init.Prescaler       = 0;
    htim_enc2.Init.CounterMode     = TIM_COUNTERMODE_UP;
    htim_enc2.Init.Period          = 0xFFFF;
    htim_enc2.Init.ClockDivision   = TIM_CLOCKDIVISION_DIV1;
    htim_enc2.Init.RepetitionCounter = 0;
    htim_enc2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Encoder_Init(&htim_enc2, &enc) != HAL_OK) Error_Handler();
}

/*==========================================================================
 *  Public Functions
 *==========================================================================*/

void Motor_InitAll(void)
{
    Motor_InitClocks();
    Motor_InitGPIO();
    Motor_InitPWM();
    Motor_InitEncoders();

    /* Motor 0 */
    g_motors[MOTOR_0].htim_pwm   = &htim_pwm;
    g_motors[MOTOR_0].pwm_channel = TIM_CHANNEL_1;
    g_motors[MOTOR_0].in1_port   = M0_IN1_PORT;
    g_motors[MOTOR_0].in1_pin    = M0_IN1_PIN;
    g_motors[MOTOR_0].in2_port   = M0_IN2_PORT;
    g_motors[MOTOR_0].in2_pin    = M0_IN2_PIN;
    g_motors[MOTOR_0].htim_enc   = &htim_enc0;
    g_motors[MOTOR_0].dir_sign   = MOTOR0_DIR_SIGN;

    /* Motor 1 */
    g_motors[MOTOR_1].htim_pwm   = &htim_pwm;
    g_motors[MOTOR_1].pwm_channel = TIM_CHANNEL_2;
    g_motors[MOTOR_1].in1_port   = M1_IN1_PORT;
    g_motors[MOTOR_1].in1_pin    = M1_IN1_PIN;
    g_motors[MOTOR_1].in2_port   = M1_IN2_PORT;
    g_motors[MOTOR_1].in2_pin    = M1_IN2_PIN;
    g_motors[MOTOR_1].htim_enc   = &htim_enc1;
    g_motors[MOTOR_1].dir_sign   = MOTOR1_DIR_SIGN;

    /* Motor 2 */
    g_motors[MOTOR_2].htim_pwm   = &htim_pwm;
    g_motors[MOTOR_2].pwm_channel = TIM_CHANNEL_3;
    g_motors[MOTOR_2].in1_port   = M2_IN1_PORT;
    g_motors[MOTOR_2].in1_pin    = M2_IN1_PIN;
    g_motors[MOTOR_2].in2_port   = M2_IN2_PORT;
    g_motors[MOTOR_2].in2_pin    = M2_IN2_PIN;
    g_motors[MOTOR_2].htim_enc   = &htim_enc2;
    g_motors[MOTOR_2].dir_sign   = MOTOR2_DIR_SIGN;

    /* Zero all states */
    for (int i = 0; i < MOTOR_COUNT; i++) {
        g_motors[i].enc_count   = 0;
        g_motors[i].enc_delta   = 0;
        g_motors[i].speed_mps   = 0.0f;
        g_motors[i].speed_rads  = 0.0f;
        g_motors[i].target_speed = 0.0f;
        g_motors[i].pwm_duty    = 0;
        g_motors[i].pwm_dir     = 0;
    }
}

void Motor_StartAll(void)
{
    HAL_TIM_PWM_Start(&htim_pwm, TIM_CHANNEL_1);
    HAL_TIM_PWM_Start(&htim_pwm, TIM_CHANNEL_2);
    HAL_TIM_PWM_Start(&htim_pwm, TIM_CHANNEL_3);

    HAL_TIM_Encoder_Start(&htim_enc0, TIM_CHANNEL_ALL);
    HAL_TIM_Encoder_Start(&htim_enc1, TIM_CHANNEL_ALL);
    HAL_TIM_Encoder_Start(&htim_enc2, TIM_CHANNEL_ALL);
}

void Motor_SetSpeed(MotorIndex_t idx, float speed_ms)
{
    Motor_t *m = &g_motors[idx];

    /* Apply direction correction sign */
    float corrected = speed_ms * (float)m->dir_sign;

    /* Clamp to max speed */
    if (corrected > MOTOR_MAX_SPEED_MS)  corrected = MOTOR_MAX_SPEED_MS;
    if (corrected < -MOTOR_MAX_SPEED_MS) corrected = -MOTOR_MAX_SPEED_MS;

    /* Determine direction and duty */
    if (corrected > 0.001f) {
        m->pwm_dir = +1;
    } else if (corrected < -0.001f) {
        m->pwm_dir = -1;
    } else {
        m->pwm_dir = 0;
    }

    /* Convert m/s to PWM duty [0..PWM_PERIOD] */
    float ratio = fabsf(corrected) / MOTOR_MAX_SPEED_MS;
    if (ratio > 1.0f) ratio = 1.0f;
    m->pwm_duty = (uint16_t)(ratio * (float)PWM_PERIOD);

    /* Set L298P direction pins */
    if (m->pwm_dir == +1) {
        HAL_GPIO_WritePin(m->in1_port, m->in1_pin, GPIO_PIN_SET);
        HAL_GPIO_WritePin(m->in2_port, m->in2_pin, GPIO_PIN_RESET);
    } else if (m->pwm_dir == -1) {
        HAL_GPIO_WritePin(m->in1_port, m->in1_pin, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(m->in2_port, m->in2_pin, GPIO_PIN_SET);
    } else {
        /* Coast: both LOW */
        HAL_GPIO_WritePin(m->in1_port, m->in1_pin, GPIO_PIN_RESET);
        HAL_GPIO_WritePin(m->in2_port, m->in2_pin, GPIO_PIN_RESET);
    }

    /* Set PWM duty */
    __HAL_TIM_SET_COMPARE(m->htim_pwm, m->pwm_channel, m->pwm_duty);
}

void Motor_StopAll(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        Motor_SetSpeed((MotorIndex_t)i, 0.0f);
    }
}

int16_t Motor_ReadEncoder(MotorIndex_t idx)
{
    Motor_t *m = &g_motors[idx];
    int16_t delta = 0;

    if (m->htim_enc->Instance == TIM2) {
        /* TIM2 is 32-bit */
        int32_t current = (int32_t)__HAL_TIM_GET_COUNTER(m->htim_enc);
        delta = (int16_t)(current - enc0_prev);
        enc0_prev = current;
    } else if (m->htim_enc->Instance == TIM4) {
        /* TIM4 is 16-bit */
        uint16_t raw = __HAL_TIM_GET_COUNTER(m->htim_enc);
        delta = (int16_t)((uint16_t)(raw - (uint16_t)enc1_prev));
        enc1_prev = (int16_t)raw;
    } else if (m->htim_enc->Instance == TIM1) {
        /* TIM1 is 16-bit */
        uint16_t raw = __HAL_TIM_GET_COUNTER(m->htim_enc);
        delta = (int16_t)((uint16_t)(raw - (uint16_t)enc2_prev));
        enc2_prev = (int16_t)raw;
    }

    m->enc_count += delta;
    m->enc_delta  = delta;

    return delta;
}

void Motor_UpdateAllEncoders(void)
{
    for (int i = 0; i < MOTOR_COUNT; i++) {
        Motor_ReadEncoder((MotorIndex_t)i);

        Motor_t *m = &g_motors[i];
        /* delta counts / (CPR * dt) = angular velocity [rad/s]
         * Linear speed = angular_vel * radius [m/s] */
        m->speed_rads = (float)m->enc_delta / ENCODER_CPR_OUTPUT_SHAFT
                        / ENCODER_UPDATE_SEC;
        m->speed_mps  = m->speed_rads * WHEEL_RADIUS_M;
    }
}

void Motor_SpeedControlStep(MotorIndex_t idx)
{
    Motor_t *m = &g_motors[idx];

    float error = m->target_speed - m->speed_mps;
    float output = SPEED_CTRL_KP * error + SPEED_CTRL_FEEDFORWARD;

    Motor_SetSpeed(idx, output);
}

TIM_HandleTypeDef *Motor_GetPwmTimer(void)
{
    return &htim_pwm;
}

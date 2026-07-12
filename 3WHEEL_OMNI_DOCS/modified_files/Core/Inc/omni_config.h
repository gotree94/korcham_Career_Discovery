/**
 * @file    omni_config.h
 * @brief   3-Wheel Omni Drive Robot - Hardware Configuration
 *
 * MCU:        NUCLEO-STM32F103RB (STM32F103RBT6, Cortex-M3, 64MHz)
 * Motor:      RB-35GM 11TYPE 12V, 1/50 Gearbox
 * Wheel:      58mm Plastic Omni Wheel
 * Driver:     L298P x3 (Dual H-Bridge, PWM+DIR mode)
 * Encoder:    Motor shaft encoder, Quadrature decode
 */

#ifndef OMNI_CONFIG_H
#define OMNI_CONFIG_H

#include "stm32f1xx_hal.h"

/*==========================================================================
 *  Mechanical Parameters
 *==========================================================================*/

/* Wheel */
#define WHEEL_RADIUS_M              0.029f      /* 58mm diameter / 2 */
#define WHEEL_DIAMETER_MM           58

/* Robot wheelbase: distance from center to wheel contact point */
#define WHEELBASE_RADIUS_M          0.100f      /* 100mm - CHANGE to match your chassis */

/* Wheel angle from robot X-axis (counter-clockwise positive)
 *   Motor0 = front (90deg)
 *   Motor1 = rear-left (210deg)
 *   Motor2 = rear-right (330deg) */
#define WHEEL0_ANGLE_DEG            90.0f
#define WHEEL1_ANGLE_DEG            210.0f
#define WHEEL2_ANGLE_DEG            330.0f

/*==========================================================================
 *  Motor & Encoder Parameters
 *==========================================================================*/

/* RB-35GM 11TYPE with 1/50 gearbox */
#define GEAR_RATIO                  50
#define ENCODER_PPR_MOTOR_SHAFT     11          /* Pulses per rev at motor shaft */
#define ENCODER_CPR_QUADRATURE      (ENCODER_PPR_MOTOR_SHAFT * 4)  /* 44 counts/motor rev */
#define ENCODER_CPR_OUTPUT_SHAFT    (ENCODER_CPR_QUADRATURE * GEAR_RATIO)  /* 2200 counts/output rev */
#define ENCODER_COUNTS_PER_RADIAN   ((float)ENCODER_CPR_OUTPUT_SHAFT / (2.0f * 3.14159265f))

/* Motor speed limits (output shaft) */
#define MOTOR_MAX_RPM_OUTPUT        120         /* Max output RPM at 12V no-load */
#define MOTOR_MAX_SPEED_MS          (2.0f * 3.14159265f * WHEEL_RADIUS_M * MOTOR_MAX_RPM_OUTPUT / 60.0f)
#define MOTOR_MAX_ANGULAR_VEL       (2.0f * 3.14159265f * MOTOR_MAX_RPM_OUTPUT / 60.0f)

/*==========================================================================
 *  Timer & PWM Parameters
 *==========================================================================*/

/* System: APB1 timer clock = 64MHz, APB2 timer clock = 64MHz */
#define TIMER_CLOCK_HZ              64000000UL

/* PWM frequency (20kHz to avoid audible noise) */
#define PWM_FREQUENCY_HZ            20000UL
#define PWM_PERIOD                  (TIMER_CLOCK_HZ / PWM_FREQUENCY_HZ - 1)  /* = 3199 */

/* Encoder read loop period (ms) */
#define ENCODER_UPDATE_MS           10
#define ENCODER_UPDATE_SEC          (ENCODER_UPDATE_MS / 1000.0f)

/*==========================================================================
 *  Speed Controller (Proportional)
 *==========================================================================*/
#define SPEED_CTRL_KP               500.0f      /* Proportional gain (tune this!) */
#define SPEED_CTRL_FEEDFORWARD      0.0f        /* Feedforward offset */

/*==========================================================================
 *  L298P Motor Driver Pin Mapping
 *
 *  Motor 0:  ENA=PA6(TIM3_CH1),  IN1=PB12, IN2=PB15
 *  Motor 1:  ENA=PA7(TIM3_CH2),  IN1=PB13, IN2=PC6
 *  Motor 2:  ENA=PB0(TIM3_CH3),  IN1=PB14, IN2=PC7
 *==========================================================================*/

/* Motor 0 */
#define M0_EN_PORT                  GPIOA
#define M0_EN_PIN                   GPIO_PIN_6
#define M0_IN1_PORT                 GPIOB
#define M0_IN1_PIN                  GPIO_PIN_12
#define M0_IN2_PORT                 GPIOB
#define M0_IN2_PIN                  GPIO_PIN_15

/* Motor 1 */
#define M1_EN_PORT                  GPIOA
#define M1_EN_PIN                   GPIO_PIN_7
#define M1_IN1_PORT                 GPIOB
#define M1_IN1_PIN                  GPIO_PIN_13
#define M1_IN2_PORT                 GPIOC
#define M1_IN2_PIN                  GPIO_PIN_6

/* Motor 2 */
#define M2_EN_PORT                  GPIOB
#define M2_EN_PIN                   GPIO_PIN_0
#define M2_IN1_PORT                 GPIOB
#define M2_IN1_PIN                  GPIO_PIN_14
#define M2_IN2_PORT                 GPIOC
#define M2_IN2_PIN                  GPIO_PIN_7

/*==========================================================================
 *  Encoder Timer Mapping
 *
 *  Motor 0 Encoder: TIM2 (32-bit) - CH1=PA0, CH2=PA1
 *  Motor 1 Encoder: TIM4 (16-bit) - CH1=PB6, CH2=PB7
 *  Motor 2 Encoder: TIM1 (16-bit) - CH1=PA8, CH2=PA9
 *==========================================================================*/

#define ENC0_TIM                    TIM2
#define ENC0_TIM_CHANNEL_A          TIM_CHANNEL_1
#define ENC0_TIM_CHANNEL_B          TIM_CHANNEL_2

#define ENC1_TIM                    TIM4
#define ENC1_TIM_CHANNEL_A          TIM_CHANNEL_1
#define ENC1_TIM_CHANNEL_B          TIM_CHANNEL_2

#define ENC2_TIM                    TIM1
#define ENC2_TIM_CHANNEL_A          TIM_CHANNEL_1
#define ENC2_TIM_CHANNEL_B          TIM_CHANNEL_2

/*==========================================================================
 *  Motor Direction Polarity
 *  Change sign (+1 / -1) if a motor spins opposite to expected direction
 *==========================================================================*/
#define MOTOR0_DIR_SIGN             +1
#define MOTOR1_DIR_SIGN             +1
#define MOTOR2_DIR_SIGN             +1

/*==========================================================================
 *  UART Debug
 *==========================================================================*/
#define DEBUG_UART                  huart2
#define DEBUG_BAUD                  115200

#endif /* OMNI_CONFIG_H */

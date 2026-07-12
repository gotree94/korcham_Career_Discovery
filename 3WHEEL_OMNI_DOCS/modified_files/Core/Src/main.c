/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "motor.h"
#include "omni_kinematic.h"
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */
OmniRobot_t robot;
static uint32_t last_loop_tick = 0;
static uint32_t last_print_tick = 0;

/* UART receive buffer */
static uint8_t uart_rx_byte;
static char    uart_cmd_buf[64];
static uint8_t uart_cmd_idx = 0;

/* Command variables */
static float cmd_vx    = 0.0f;
static float cmd_vy    = 0.0f;
static float cmd_omega = 0.0f;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART2_UART_Init(void);
/* USER CODE BEGIN PFP */
void UART_ProcessCommand(void);
void UART_PrintOdometry(const OmniRobot_t *robot);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* UART RX interrupt callback */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2) {
        if (uart_rx_byte == '\n' || uart_rx_byte == '\r') {
            if (uart_cmd_idx > 0) {
                uart_cmd_buf[uart_cmd_idx] = '\0';
                UART_ProcessCommand();
                uart_cmd_idx = 0;
            }
        } else {
            if (uart_cmd_idx < sizeof(uart_cmd_buf) - 1) {
                uart_cmd_buf[uart_cmd_idx++] = (char)uart_rx_byte;
            }
        }
        /* Re-arm receive interrupt */
        HAL_UART_Receive_IT(&huart2, &uart_rx_byte, 1);
    }
}

/* UART command parser */
void UART_ProcessCommand(void)
{
    char *cmd = uart_cmd_buf;

    if (cmd[0] == 'V' || cmd[0] == 'v') {
        /* Format: "V vx vy omega" (m/s, m/s, rad/s) */
        float vx = 0, vy = 0, w = 0;
        if (sscanf(cmd, "V %f %f %f", &vx, &vy, &w) >= 3) {
            cmd_vx    = vx;
            cmd_vy    = vy;
            cmd_omega = w;
        }
    }
    else if (cmd[0] == 'S' || cmd[0] == 's') {
        /* Stop */
        cmd_vx    = 0.0f;
        cmd_vy    = 0.0f;
        cmd_omega = 0.0f;
        Motor_StopAll();
    }
    else if (cmd[0] == 'P' || cmd[0] == 'p') {
        /* Print status */
        UART_PrintOdometry(&robot);
    }
    else if (cmd[0] == 'M' || cmd[0] == 'm') {
        /* Manual motor control: "M motor_idx speed_mps" */
        int idx = 0;
        float spd = 0;
        if (sscanf(cmd, "M %d %f", &idx, &spd) >= 2) {
            if (idx >= 0 && idx < MOTOR_COUNT) {
                Motor_SetSpeed((MotorIndex_t)idx, spd);
            }
        }
    }
}

/* Print odometry via UART */
void UART_PrintOdometry(const OmniRobot_t *r)
{
    char buf[128];
    int len = snprintf(buf, sizeof(buf),
        "ODO|x=%.3f y=%.3f th=%.2f|VX=%.3f VY=%.3f W=%.3f|E0=%ld E1=%d E2=%d\r\n",
        r->x, r->y, r->theta,
        r->vx, r->vy, r->omega,
        (long)g_motors[MOTOR_0].enc_count,
        (int)g_motors[MOTOR_1].enc_count,
        (int)g_motors[MOTOR_2].enc_count);
    HAL_UART_Transmit(&huart2, (uint8_t *)buf, len, 100);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
  /* Initialize motor hardware and kinematics */
  Motor_InitAll();
  Omni_Init(&robot);
  Motor_StartAll();

  /* Start UART interrupt receive */
  HAL_UART_Receive_IT(&huart2, &uart_rx_byte, 1);

  /* Greeting */
  {
      const char *hello = "3-Wheel Omni Robot Ready\r\n"
                          "Commands: V vx vy w | S(stop) | P(print) | M idx spd\r\n";
      HAL_UART_Transmit(&huart2, (uint8_t *)hello, strlen(hello), 100);
  }

  last_loop_tick = HAL_GetTick();
  last_print_tick = HAL_GetTick();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    uint32_t now = HAL_GetTick();

    /* 10ms control loop */
    if (now - last_loop_tick >= ENCODER_UPDATE_MS) {
        last_loop_tick = now;

        /* Read all encoders and compute wheel speeds */
        Motor_UpdateAllEncoders();

        /* Forward kinematics: wheel speeds -> robot velocity */
        Omni_ForwardKinematics(&robot, g_motors);

        /* Update dead-reckoning odometry */
        Omni_UpdateOdometry(&robot, ENCODER_UPDATE_SEC);

        /* Inverse kinematics: desired velocity -> target wheel speeds */
        Omni_InverseKinematics(&robot, cmd_vx, cmd_vy, cmd_omega, g_motors);

        /* Apply P speed control to each motor */
        for (int i = 0; i < MOTOR_COUNT; i++) {
            Motor_SpeedControlStep((MotorIndex_t)i);
        }

        /* Toggle LED as heartbeat */
        HAL_GPIO_TogglePin(LD2_GPIO_Port, LD2_Pin);
    }

    /* Print odometry every 100ms */
    if (now - last_print_tick >= 100) {
        last_print_tick = now;
        UART_PrintOdometry(&robot);
    }

    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI_DIV2;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL16;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : B1_Pin */
  GPIO_InitStruct.Pin = B1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

# 13. UART Communication

## 1. UART 개요

UART(Universal Asynchronous Receiver/Transmitter)는 비동기 직렬 통신 프로토콜입니다.

| 항목 | 사양 |
|------|------|
| 핀 | TX (송신), RX (수신) |
| 속도 | 9600~115200 bps (일반적) |
| 전압 | 3.3V (Jetson, 5V 장치는 레벨시프터 필요) |

## 2. Jetson UART 핀맵

| UART | TX 핀 | RX 핀 | 비고 |
|:----:|:----:|:----:|------|
| UART1 | Pin 8 (GPIO 160) | Pin 10 (GPIO 161) | 일반 시리얼 통신 |
| UART2 | M.2 Key E | - | Bluetooth 전용 |

## 3. UART 테스트

```bash
# 시리얼 장치 확인
ls /dev/ttyTHS*

# Loopback 테스트 (TX → RX 연결)
echo "Hello" > /dev/ttyTHS1
cat /dev/ttyTHS1 &
# → Hello 출력 확인
```

## 4. Python UART 예제

```python
import serial

ser = serial.Serial(
    port='/dev/ttyTHS1',
    baudrate=115200,
    timeout=1
)

# 송신
ser.write(b'AT Command\r\n')

# 수신
response = ser.readline()
print(f"Response: {response}")

ser.close()
```

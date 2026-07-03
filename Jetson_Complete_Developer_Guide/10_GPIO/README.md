# 10. GPIO Programming

## 1. Jetson GPIO 개요

Jetson Xavier NX의 40-pin 헤더는 Raspberry Pi와 물리적으로 동일한 핀 배열을 사용합니다.

### GPIO 라이브러리

| 라이브러리 | 설치 | 특징 |
|:----------:|:----:|------|
| **Jetson.GPIO** | `pip3 install Jetson.GPIO` | NVIDIA 공식, RPi.GPIO와 유사 API |
| libgpiod | `apt install gpiod` | Linux 표준 GPIO 인터페이스 |

> **주의**: Jetson.GPIO 사용 시 `sudo`가 필요할 수 있습니다.
> 권한 설정: `sudo usermod -aG gpio $USER`

---

## 2. GPIO 핀맵 (Xavier NX 40-pin Header)

| Pin | Name | 기능 | Pin | Name | 기능 |
|:---:|:----:|:----:|:---:|:----:|:----:|
| 1 | 3.3V | 전원 | 2 | 5V | 전원 |
| 3 | I2C1_SDA | GPIO08 | 4 | 5V | 전원 |
| 5 | I2C1_SCL | GPIO09 | 6 | GND | 접지 |
| 7 | **GPIO** **216** | CLK_32K | 8 | **GPIO** **160** | UART1_TX |
| 9 | GND | 접지 | 10 | **GPIO** **161** | UART1_RX |
| 11 | **GPIO** **17** | 초음파 Trig | 12 | **GPIO** **18** | 초음파 Echo |
| 13 | **GPIO** **27** | 초음파 Trig2 | 14 | GND | 접지 |
| 15 | **GPIO** **22** | 초음파 Echo2 | 16 | **GPIO** **23** | IR 센서 1 |
| 17 | 3.3V | 전원 | 18 | **GPIO** **24** | IR 센서 2 |
| 19 | **GPIO** **10** | SPI_MOSI | 20 | GND | 접지 |
| 21 | **GPIO** **9** | SPI_MISO | 22 | **GPIO** **25** | IR 센서 3 |
| 23 | **GPIO** **11** | SPI_SCK | 24 | **GPIO** **8** | SPI_CS |
| 25 | GND | 접지 | 26 | **GPIO** **7** | SPI_CS1 |
| 27 | I2C_SDA | LCD SDA | 28 | I2C_SCL | LCD SCL |
| 29 | **GPIO** **5** | 초음파 Trig3 | 30 | GND | 접지 |
| 31 | **GPIO** **6** | 초음파 Echo3 | 32 | **GPIO** **12** | 모터 PWM |
| 33 | **GPIO** **13** | 모터 IN3 | 34 | GND | 접지 |
| 35 | **GPIO** **19** | 모터 IN4 | 36 | **GPIO** **16** | 버튼 입력 |
| 37 | **GPIO** **26** | 부저 | 38 | **GPIO** **20** | 모터 IN5 |
| 39 | GND | 접지 | 40 | **GPIO** **21** | 모터 IN6 |

---

## 3. 실습 1: LED 깜빡이기 (GPIO Output)

### 연결
```
GPIO12 (Pin 32) ── 330Ω ──┬── LED (+)
                          GND
```

### 코드
```python
import Jetson.GPIO as GPIO
import time

LED_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
```

### 실행
```bash
python3 led_blink.py
```

---

## 4. 실습 2: 버튼 입력 (GPIO Input)

### 연결
```
GPIO16 (Pin 36) ──┬── 버튼
                  GND (버튼 반대쪽)
```

### 코드 (Polling)
```python
import Jetson.GPIO as GPIO
import time

BTN_PIN = 16
LED_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        if GPIO.input(BTN_PIN):
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.05)
except KeyboardInterrupt:
    GPIO.cleanup()
```

---

## 5. 실습 3: 인터럽트 (GPIO Event)

```python
import Jetson.GPIO as GPIO

BTN_PIN = 16
LED_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LED_PIN, GPIO.OUT)

led_state = False

def button_callback(channel):
    global led_state
    led_state = not led_state
    GPIO.output(LED_PIN, led_state)
    print(f"Button pressed! LED {'ON' if led_state else 'OFF'}")

GPIO.add_event_detect(BTN_PIN, GPIO.RISING,
                      callback=button_callback, bouncetime=300)

try:
    print("Press the button (Ctrl+C to exit)")
    while True:
        GPIO.wait_for_edge(BTN_PIN, GPIO.RISING)
except KeyboardInterrupt:
    GPIO.cleanup()
```

> **인터럽트 vs Polling**: 인터럽트는 CPU를 낭비하지 않고 이벤트 발생 시에만 반응합니다.

---

## 6. 실습 4: PWM (Pulse Width Modulation)

### 연결
```
GPIO12 (Pin 32) ── 330Ω ──┬── LED
                          GND
```

### 코드
```python
import Jetson.GPIO as GPIO
import time

PWM_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)

pwm = GPIO.PWM(PWM_PIN, 1000)  # 1kHz
pwm.start(0)  # 듀티비 0%

try:
    while True:
        # 듀티비 0→100→0 반복 (LED 숨쉬기 효과)
        for duty in range(0, 101, 5):
            pwm.ChangeDutyCycle(duty)
            time.sleep(0.05)
        for duty in range(100, -1, -5):
            pwm.ChangeDutyCycle(duty)
            time.sleep(0.05)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
```

### PWM 듀티비와 전압 관계

```
듀티비 0%   = 0V (항상 OFF)      ───────────
듀티비 50%  = 1.65V (평균)      _--_--_--_--
듀티비 75%  = 2.48V (평균)      ----__----__
듀티비 100% = 3.3V (항상 ON)    ───────────
```

---

## 7. GPIO 핀 할당 충돌 방지

```bash
# 특정 핀의 현재 기능 확인
sudo cat /sys/kernel/debug/gpio

# 핀 활성 상태 확인
sudo cat /sys/class/gpio/gpio*/direction 2>/dev/null
```

```python
# GPIO 핀 해제
GPIO.cleanup()  # 모든 핀 해제
GPIO.cleanup(12)  # 특정 핀만 해제
```

---

## 8. GPIO 응용: 초음파 센서 거리 측정

```python
import Jetson.GPIO as GPIO
import time

TRIG = 17
ECHO = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.000002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    timeout = time.time() + 0.1
    while GPIO.input(ECHO) == 0:
        if time.time() > timeout:
            return -1
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        if time.time() > timeout:
            return -1
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    return distance

try:
    while True:
        dist = measure_distance()
        if dist > 0:
            print(f"Distance: {dist:.1f} cm")
        else:
            print("Measurement timeout")
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()
```

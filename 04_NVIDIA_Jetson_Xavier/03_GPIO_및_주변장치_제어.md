# 03. GPIO 및 주변장치 제어

## 학습 목표

- Jetson GPIO 구조 이해
- Python 라이브러리(`Jetson.GPIO`)로 제어
- I2C / UART / SPI 통신 실습

## 사전 준비

- [ ] 브레드보드, LED, 저항, 버튼
- [ ] I2C 센서 (예: 온습도 센서)
- [ ] 점퍼 케이블

---

## 1. GPIO 개요

- 40-Pin Header 구성과 핀 번호 체계
- Jetson.GPIO 라이브러리 설치

```bash
$ sudo pip3 install Jetson.GPIO
$ sudo groupadd -f -r gpio
$ sudo usermod -a -G gpio ubuntu
```

---

## 2. GPIO 출력 — LED 제어

```python
import Jetson.GPIO as GPIO

LED_PIN = 7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

for _ in range(5):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()
```

> ※ 회로 연결도(핀 → LED → 저항 → GND) 이미지를 첨부하세요.

---

## 3. GPIO 입력 — 버튼 제어

```python
import Jetson.GPIO as GPIO

BTN_PIN = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    if GPIO.input(BTN_PIN) == GPIO.LOW:
        print("Button pressed!")
```

---

## 4. I2C 통신

```bash
$ sudo apt install i2c-tools
$ i2cdetect -y -r 1      # 연결된 I2C 주소 검색
```

```python
import smbus2

bus = smbus2.SMBus(1)
# 센서 레지스터 읽기 예제
data = bus.read_byte_data(0x40, 0x00)
print(hex(data))
```

---

## 5. UART / SPI

- UART: 시리얼 센서/모듈 통신 (`/dev/ttyTHS1`)
- SPI: 고속 통신 (ADC, 디스플레이 등)
- 하드웨어 핀 활성화 방법 (`config.txt` / device tree) 안내

---

## 실습

1. LED 점멸 제어
2. 버튼 입력으로 LED 상태 변경
3. I2C로 온습도 센서 값 읽기
4. UART로 모듈 통신 테스트

## 정리 및 체크리스트

- [ ] GPIO 입출력 제어 가능
- [ ] `i2cdetect`로 센서 검색
- [ ] I2C 센서 데이터 읽기
- [ ] UART 시리얼 통신

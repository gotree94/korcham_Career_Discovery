# 11. I2C Communication

## 1. I2C 개요

I2C(Inter-Integrated Circuit)는 두 개의 선(SDA, SCL)으로 여러 장치를 연결하는 동기식 직렬 통신 프로토콜입니다.

| 항목 | 사양 |
|------|------|
| 핀 | SDA (데이터), SCL (클럭) |
| 속도 | 표준 100kHz, 고속 400kHz |
| 주소 | 7비트 (0x00~0x7F) |
| 버스 전압 | 3.3V (Jetson) |

## 2. Jetson I2C 버스

| 버스 | 핀헤더 | 용도 |
|:----:|:------:|------|
| I2C1 | Pin 3(SDA), Pin 5(SCL) | 일반 센서 |
| I2C2 | Pin 27(SDA), Pin 28(SCL) | LCD, 주변장치 |

## 3. I2C 스캔

```bash
# I2C 버스 1 스캔 (Pin 3/5)
sudo i2cdetect -y -r 1

# I2C 버스 2 스캔 (Pin 27/28)
sudo i2cdetect -y -r 2

# CSI 카메라 I2C 버스
sudo i2cdetect -y -r 7
```

## 4. I2C LCD 예제

```python
import smbus2
import time

class I2CLCD:
    def __init__(self, addr=0x27, bus=2):
        self.bus = smbus2.SMBus(bus)
        self.addr = addr
        self.init_lcd()

    def write_text(self, text, line=0):
        addr = 0x80 + (0x40 if line else 0x00)
        self.write_cmd(addr)
        for c in text.ljust(16)[:16]:
            self.bus.write_byte_data(self.addr, 0x40, ord(c))
            time.sleep(0.002)

    def write_cmd(self, cmd):
        self.bus.write_byte_data(self.addr, 0x80, cmd)
        time.sleep(0.005)

lcd = I2CLCD(0x27)
lcd.write_text("Hello, Jetson!", 0)
lcd.write_text("I2C LCD Ready", 1)
```

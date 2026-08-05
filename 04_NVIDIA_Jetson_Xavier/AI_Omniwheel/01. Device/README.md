# 옴니휠 로봇 교육 과정 - 01. Device 실습

NVIDIA Jetson Xavier NX 기반 옴니휠 로봇의 **하드웨어 장치 제어** 실습 모음입니다. I2C 센서/액추에이터 제어부터 직렬통신 기반 모터 제어, 그리고 이를 통합한 응용 예제까지 순서대로 학습합니다.

## 1. 실행 환경

| 항목 | 내용 |
| --- | --- |
| 대상 보드 | NVIDIA Jetson Xavier NX |
| 시스템 | JetPack 4.x, Ubuntu 18.04 |
| 실행 환경 | Jupyter Notebook / JupyterLab, Python 3.6 |
| 작업 디렉터리 | 반드시 `01. Device` 폴더 (아래 "공통 사전 준비" 참고) |

## 2. 커리큘럼 표

| 순서 | 파일 | 내용 | 난이도 |
| --- | --- | --- | --- |
| 1 | `1-1. LED 점멸 제어.ipynb` | PCA9685 PWM 채널로 LED 8개 순차 ON/OFF | ★☆☆☆☆ |
| 2 | `1-2. LED 밝기 제어.ipynb` | duty_cycle 0~4095 변화로 LED 밝기(페이드) 제어 | ★☆☆☆☆ |
| 3 | `2. Buzzer 제어.ipynb` | PCA9685 주파수 변경으로 멜로디(음계) 연주 | ★☆☆☆☆ |
| 4 | `3. 모션 감지 센서 모니터링.ipynb` | Jetson GPIO 입력으로 모션 감지 판정 | ★★☆☆☆ |
| 5 | `4. PIR 센서 모니터링.ipynb` | PCF8591 A1 ADC로 인체 감지 (1.6V 초과) | ★★☆☆☆ |
| 6 | `5. Flame 센서 모니터링.ipynb` | PCF8591 A2 ADC로 화염 감지 (1.6V 미만) | ★★☆☆☆ |
| 7 | `6. Light 센서 모니터링.ipynb` | BH1750 조도 센서 lux 측정 | ★★☆☆☆ |
| 8 | `7. 적외선 온도 센서 모니터링.ipynb` | MLX90614 비접촉 주변/물체 온도 측정 | ★★☆☆☆ |
| 9 | `8. 온도&습도&기압 센서 모니터링.ipynb` | BME280(0x76) 온도/습도/기압 측정 | ★★☆☆☆ |
| 10 | `9. CO2 센서 모니터링.ipynb` | CCS811(0x5B) eCO2/TVOC 측정 | ★★☆☆☆ |
| 11 | `10. 미세먼지 감지 센서 모니터링.ipynb` | PCF8591 A0 + GPIO LED 펄스로 미세먼지 측정 | ★★★☆☆ |
| 12 | `11. CLCD 제어.ipynb` | I2C LCD(0x27) 백라이트/문자/커서 제어 | ★★☆☆☆ |
| 13 | `12. PSD 센서 모니터링.ipynb` | 직렬통신 패킷 프로토콜로 PSD(앞/옆/뒤) 거리 모니터링 | ★★★★☆ |
| 14 | `13. Ultrasonic 센서 모니터링.ipynb` | 직렬통신으로 초음파 6개 거리 모니터링 | ★★★★☆ |
| 15 | `14. Encoder 모니터링.ipynb` | 오도미터 요청/엔코더 초기화로 3바퀴 위치 모니터링 | ★★★★☆ |
| 16 | `15. 모터 제어.ipynb` | 모터 제어 패킷(0xC0)으로 X/Y/Z 속도 제어 | ★★★☆☆ |
| 17 | `통합예제.ipynb` | 초음파 거리 기반 주행 + 부저 경고 + LCD 표시 통합 | ★★★★★ |

## 3. 공통 사전 준비

### 3.1 라이브러리 설치

I2C 장치 및 직렬통신, GPIO에 필요한 라이브러리를 한 번에 설치한다. (각 노트북에 필요한 것만 골라도 된다)

```bash
sudo pip3 install Jetson.GPIO pyserial adafruit-circuitpython-pca9685 adafruit-circuitpython-pcf8591 adafruit-circuitpython-bh1750 adafruit-circuitpython-mlx90614 adafruit-circuitpython-bme280 adafruit-circuitpython-ccs811
```

| 라이브러리 | 용도 | 사용 실습 |
| --- | --- | --- |
| `busio`, `board` | I2C 통신 버스 (Adafruit Blinka에서 제공) | 1-1~11, 통합예제 |
| `adafruit_pca9685` | PCA9685 PWM 드라이버 (LED/부저) | 1-1, 1-2, 2, 통합예제 |
| `adafruit_pcf8591` | PCF8591 ADC (PIR/Flame/미세먼지) | 4, 5, 10 |
| `adafruit_bh1750` | BH1750 조도 센서 | 6 |
| `adafruit_mlx90614` | MLX90614 적외선 온도 센서 | 7 |
| `adafruit_bme280` | BME280 온도/습도/기압 센서 | 8 |
| `adafruit_ccs811` | CCS811 CO2 센서 | 9 |
| `Jetson.GPIO` | Jetson GPIO (모션 감지, 미세먼지 LED) | 3, 10 |
| `pyserial` | 직렬통신 (Arduino 패킷 통신) | 12, 13, 14, 15, 통합예제 |
| `libraries.*` | 이 과정 제공 패키지 (Omniwheel_Protocol, LCD) | 11~15, 통합예제 |

> `busio`, `board`, `adafruit_*` 라이브러리는 Adafruit Blinka(CircuitPython for Jetson)가 설치되어 있어야 import 된다. 설치되어 있지 않다면 `sudo pip3 install adafruit-blinka`를 먼저 실행한다.

### 3.2 I2C 활성화 및 권한

- I2C 버스가 활성화되어 있어야 하며, 장치 접근 권한이 필요하다.
  ```bash
  sudo chmod 666 /sys/bus/i2c/devices/i2c-0/bus_clk_rate
  ```
- 연결된 장치 주소 확인:
  ```bash
  i2cdetect -y -r 1
  ```
- 주요 장치 주소:

| 장치 | 주소 |
| --- | --- |
| PCA9685 (PWM) | 0x40 |
| PCF8591 (ADC/DAC) | 0x48 |
| BH1750 (조도) | 0x23 |
| MLX90614 (적외선 온도) | 0x5A |
| BME280 (온습도기압) | 0x76 |
| CCS811 (CO2) | 0x5B |
| CLCD (PCF8574) | 0x27 |

### 3.3 GPIO 권한 설정 (3, 10번 실습)

```bash
sudo groupadd -f -r gpio
sudo usermod -a -G gpio $USER
sudo cp /opt/nvidia/jetson-gpio/etc/99-gpio.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
# 재부팅 후 Jupyter 실행
```

- GPIO 모드는 `GPIO.TEGRA_SOC`를 사용한다. 모션 센서 = `SPI3_CS0_N`, 미세먼지 LED = `SPI3_CS1_N`.
- ⚠ `GPIO.setmode()`는 `GPIO.setup()`보다 **반드시 먼저** 실행해야 한다.

### 3.4 직렬통신 포트 권한 (12~15, 통합예제)

```bash
sudo chmod 777 /dev/ttyACM0
```

- 포트: `/dev/ttyACM0`, 보드레이트: 115200, 라이브러리: pyserial.

### 3.5 작업 디렉터리 (중요)

- `libraries` 패키지(Omniwheel_Protocol, I2C_Charactor_Liquid_Crystal_Display)는 **namespace package**라서 `__init__.py`가 없어도 import되지만, 반드시 **`01. Device` 폴더가 작업 디렉터리**여야 한다.
- 다른 폴더에서 노트북을 열면 `ModuleNotFoundError: No module named 'libraries'`가 발생한다.

## 4. 통신 프로토콜 요약 (직렬통신 실습 공통)

- Arduino_ID = **0x20**
- 패킷 구조: `STX(0x02) + ID + Length(10자리×2) + CMD + Payload(MID+ASCII 데이터) + LRC(2자리) + ETX(0x03)`
- `Omniwheel_Protocol.Packet` 클래스:
  - 송신: `setID` → `setCMD` → `clearPayload` → `addPayload` → `calcLRC_Lower` → `packetToList` → `write`
  - 수신: `parsingList(리스트)`로 파싱, `getID/getCMD/getPayload`로 값 추출
- CMD 체계:

| CMD | 의미 |
| --- | --- |
| 0xA0 | 오도미터(엔코더) 값 요청 |
| 0xA1 | 센서(초음파/PSD) 값 요청 |
| 0xB0 | 오도미터 응답 |
| 0xB1 | 센서 응답 |
| 0xC0 | 모터 제어 (Control, 응답 없음) |
| 0xC2 | 엔코더 초기화 |

- MID 체계:

| MID | 의미 |
| --- | --- |
| 0x80 | 초음파 / 엔코더 1번 / X 선속도 |
| 0x81 | 엔코더 2번 / Y 선속도 / PSD |
| 0x82 | 엔코더 3번 / Z 각속도 |

## 5. 실습 안전 수칙

1. 모터 제어(15번)와 통합예제는 로봇이 실제로 움직인다. 넓고 안전한 공간에서 실습한다.
2. 무한루프 셀을 실행한 뒤에는 **정지 셀(모터 0 전송)**을 실행하거나 **Kernel → Interrupt**로 중지한다.
3. 화염 센서(5번) 실험은 라이터/성냥 등으로 짧게 수행하고 주변에 가연물을 두지 않는다.
4. 배선을 바꾸기 전에는 항상 전원을 끄거나, I2C 장치가 연결된 상태에서 임의로 단자에 손을 대지 않는다.

## 6. 학습 로드맵

- **1단계 (I2C 기초)**: 1-1 ~ 2 — PWM을 통한 LED/부저 제어로 딥러닝 이전의 기본 하드웨어 제어 이해
- **2단계 (아날로그/디지털 센서)**: 3 ~ 10 — GPIO, ADC, I2C 센서별 특성과 판정 로직 학습
- **3단계 (표시 장치)**: 11 — LCD 출력으로 센서 데이터 시각화 기초
- **4단계 (직렬통신)**: 12 ~ 15 — 옴니휠 패킷 프로토콜로 센서/엔코더/모터 제어
- **5단계 (통합 응용)**: 통합예제 — 센서+액추에이터+표시 장치를 결합한 자율 주행 시나리오

> 각 실습은 별도의 마크다운 문서(`<노트북 이름>.md`)로 상세 해설이 제공된다. 코드를 실행하기 전에 해당 문서를 먼저 읽으면 실습 효과가 높다.

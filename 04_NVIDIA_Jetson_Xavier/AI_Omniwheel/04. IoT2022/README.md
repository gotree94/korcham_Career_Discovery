# IoT2022 실습 노트북 교육 문서

NVIDIA Jetson Xavier NX 기반 옴니휠 로봇 교육 과정에서 사용하는 `IoT2022` 폴더의 Jupyter 노트북 15개를 가르치기 위한 교육용 마크다운 문서 모음입니다.

## 1. 전체 개요
- 대상 보드: **NVIDIA Jetson Xavier NX** (JetPack 4.x, Ubuntu 18.04, Python 3.6)
- 실행 환경: Jupyter Notebook/Lab, `IoT2022` 폴더에서 실행
- 센서 제어 계층: 대부분 **I2C → Adafruit CircuitPython** (`busio`, `board`, `adafruit_*`)
- 본 아카이브의 IoT2022 버전은 I2C 버스를 **`board.SCL_1 / board.SDA_1`** 로 사용한다. (01. Device 버전은 `board.SCL / board.SDA` — 버스 번호가 다르므로 주의)
- 12~15번은 Arduino와 **직렬통신(/dev/ttyUSB0, 9600)** 으로 통신한다. (01. Device 버전은 /dev/ttyACM0, 115200 — 포트와 속도가 다름)

## 2. 커리큘럼 표

| 번호 | 노트북 | 주제 | 핵심 기술 | 오타/수정 여부 |
| --- | --- | --- | --- | --- |
| 1 | 1.LED.ipynb | LED 순차 점멸 | PCA9685 PWM (0x40), duty_cycle | 정상 동작 |
| 2 | 2.LED2.ipynb | LED 밝기 램프 | PWM 페이드 인/아웃 (0→4095) | 정상 동작 |
| 3 | 3.busio.ipynb | 부저 멜로디 | 주파수 제어, 채널 15, 50% 듀티 | 정상 동작 |
| 4 | 4.Motion.ipynb | 모션 감지 | Jetson.GPIO, 'UART2_RTS' | `GPIO.setmode` 누락 주의 |
| 5 | 5.PIR.ipynb | PIR 인체 감지 | PCF8591 (0x48) A1, 1.6V 초과 | `mport`→`import`, `Analogln`→`AnalogIn` |
| 6 | 6.Flame.ipynb | 화염 감지 | PCF8591 A2, 1.6V 미만 | `Analogln`→`AnalogIn` |
| 7 | 7.Light.ipynb | 조도 측정 | BH1750 (0x23) lux | `light_sensor -`→`=`, `%2f`→`%.2f` |
| 8 | 8.적외선.ipynb | 적외선 온도 | MLX90614 (0x5A) | `%2.f`→`%.2f` |
| 9 | 9.temp.ipynb | 온습도/기압 | BME280 (0x76) | 정상 동작 |
| 10 | 10.CO2.ipynb | CO2/TVOC | CCS811 (0x5B) | 정상 동작 |
| 11 | 11.미세먼지.ipynb | 미세먼지 | PCF8591 A0 + GPIO 'CAM_AF_EN' | `GPIO.outpit`→`GPIO.output` |
| 12 | 12.PSD.ipynb | 바닥 PSD | 직렬통신, 0xA1/0xB1, MID 0x81 | 변수명 미정의 + 루프 위치 오류 |
| 13 | 13.초음파.ipynb | 초음파 6개 | 직렬통신, MID 0x80, 3자리 분할 | `if` 들여쓰기 오류 |
| 14 | 14.PSD.ipynb | 엔코더/오도미터 | 직렬통신, 0xA0/0xB0/0xC2, MID 0x80~82 | print 문자열 연결 오류 |
| 15 | 15.DC.ipynb | DC 모터 제어 | 직렬통신, 0xC0, -600~600 | `_date`→`_data`, 무한루프 구조 오류 |

## 3. 공통 사전 준비
### 3.1 라이브러리 설치
```bash
sudo pip3 install Jetson.GPIO pyserial adafruit-circuitpython-pca9685 adafruit-circuitpython-pcf8591 adafruit-circuitpython-bh1750 adafruit-circuitpython-mlx90614 adafruit-circuitpython-bme280 adafruit-circuitpython-ccs811
```

### 3.2 I2C 장치 주소 (i2cdetect로 확인)
- PCA9685 = 0x40, PCF8591 = 0x48, BH1750 = 0x23, MLX90614 = 0x5A, BME280 = 0x76, CCS811 = 0x5B

### 3.3 직렬통신 사전 설정 (12~15번 공통)
- 포트: `/dev/ttyUSB0`, baudrate: **9600**
- 포트 권한: `sudo chmod 777 /dev/ttyUSB0`
- Arduino_ID = 0x20
- **Omniwheel_Protocol.py 필수**: `import Omniwheel_Protocol`이 동작해야 한다. 이 아카이브에서는 `01. Device\libraries\` 아래에 있으므로, 해당 파일을 IoT2022 폴더로 **복사**하거나 `01. Device\libraries` 폴더가 현재 경로에 있어야 한다.
- 패킷 구조: STX(0x02) + ID + Length + LRC 등은 `Omniwheel_Protocol.Packet` 사용.
- 주요 CMD: 0xA0=오도미터 요청, 0xA1=센서 요청, 0xB0=응답, 0xC0=모터 제어, 0xC2=엔코더 초기화
- 주요 MID: 0x80=초음파/엔코더1/X, 0x81=엔코더2/Y/PSD, 0x82=엔코더3/Z

## 4. 이 버전의 오타·수정 안내 요약
각 노트북의 원본 코드에는 오타/구조 오류가 있어 그대로 실행하면 동작하지 않거나 잘못 동작합니다. **원본 코드는 각 문서에 그대로 보존**되어 있고, 각 문서 5번 절에 "실행 전 수정이 필요한 부분"으로 정확한 수정 코드를 안내합니다.

| 노트북 | 핵심 수정 |
| --- | --- |
| 4.Motion | `GPIO.setmode(GPIO.TEGRA_SOC)` 추가 |
| 5.PIR | `mport`→`import`, `Analogln`→`AnalogIn` (2곳) |
| 6.Flame | `Analogln`→`AnalogIn` (2곳) |
| 7.Light | `light_sensor - ...`→`light_sensor = ...`, `%2f`→`%.2f` |
| 8.적외선 | `%2.f`→`%.2f` (2곳) |
| 11.미세먼지 | `GPIO.outpit`→`GPIO.output` |
| 12.PSD | 미정의 변수명(`ANSWER_PSD_SENSOR`/`MID_PSD_SENSOR`/`REQUEST_PSD_SENSOR`)을 정의된 상수로 통일 + `while` 루프를 함수 밖으로 이동 |
| 13.초음파 | `Packet_send` 내부 `if(send_flag==False)` 블록 들여쓰기 수정 |
| 14.PSD | print 문의 따옴표 배치 수정 (문자열 연결) |
| 15.DC | 파라미터 `_date`→`_data`, `while` 루프를 함수 밖으로 이동 |

## 5. 실습 진행 흐름 (권장 순서)
1. I2C 기초: 1.LED → 2.LED2 → 3.busio (PCA9685 이해)
2. GPIO 기초: 4.Motion (Jetson.GPIO)
3. ADC 센서: 5.PIR → 6.Flame → 11.미세먼지 (PCF8591)
4. 디지털 I2C 센서: 7.Light → 8.적외선 → 9.temp → 10.CO2
5. 직렬통신: 12.PSD → 13.초음파 → 14.엔코더 → 15.DC (Omniwheel_Protocol 필요)

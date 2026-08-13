# AI_Omniwheel 로봇 전체 아키텍처 분석

> 분석 근거: `C:\Users\Administrator\Desktop\새 폴더 (7)\AI_Omniwheel` 프로젝트 전체
> (01. Device 노트북 + libraries, 02. ROS 노트북, 03. AI 노트북 + 모델, AI_Test)
> 작성일: 2026-08-13

> 참고: 이전 문서들은 **Jetson 보드 단독** 관점이었고, 본 문서는 **주변 장치 + 구동부 + AI + ROS를 포함한 로봇 전체** 아키텍처입니다.

---

## 1. 시스템 개요

**WOW-2037L AI 로봇** (옴니휠 기반) — Jetson Xavier NX가 "두뇌"(AI/ROS), **Cortex-M MCU가 "척수"(실시간 구동·센서 취득)** 를 맡는 2-프로세서 분산 구조입니다.

```
┌────────────────────────────────────────────────────────────────────────┐
│                       Jetson Xavier NX (두뇌)                          │
│  Jupyter(8888) · ROS Melodic · TensorRT(FP16) · TF2.5 · OpenCV         │
│  bready 패키지: PyCamera / ObjectDetector / optimizer                   │
├────────────────────────────────────────────────────────────────────────┤
│  [I2C]  PCA9685(16ch PWM)  CLCD(16x2)  PCF8591(ADC→미세먼지)           │
│  [GPIO] 미세먼지 LED 스위치 등                                          │
│  [CSI]  카메라 → GStreamer TCP(127.0.0.1:5000)                         │
│  [USB]  /dev/ttyACM0 (115200) ◄─────────────┐                            │
├──────────────────────────────────────────────┼─────────────────────────┤
│  Cortex-M MCU (척수) ◄───────────────────────┘                          │
│  - 3× Omni 모터(옴니휠) 드라이버 + 인코더 3ch                            │
│  - 초음파(바닥 6개)/PSD(3ch)/스위치                                       │
│  - 화염/PIR/CO2/미세먼지/적외선온도/마이크로파/사운드(4ch)/배터리          │
│  - ECO 모듈: 조도 · 자세(X/Y/Z) · 기압 · 지자기                          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 하드웨어 구성 요소

### 2.1 메인 컴퓨터 — Jetson Xavier NX

- JetPack 4.6.1 (Ubuntu 18.04, Py3.6), CUDA 10.2, TensorRT 8.0.1, TF 2.5.0+nv21.7
- 역할: AI 추론(객체인식), ROS 노드, Jupyter 서버, 카메라 스트리밍, 직렬 브리지
- 상세는 `C:\Jetson_Xavier_NX_아키텍처_분석_및_Orin_Nano_마이그레이션.md` 참고

### 2.2 구동 제어 MCU — Cortex (Arduino 계열, ID 0x20)

- Jetson과 **USB CDC 시리얼(/dev/ttyACM0)** 연결, 115200bps
  - Jetson의 `comm_Arduino.py` 기본값 = `/dev/ttyACM0`, 115200 (확인 완료)
  - 로컬 노트북 사본만 `/dev/ttyTCU0`(구형 드라이버명)로 되어 있어 차이 발생
  - 접속 확인된 직렬 포트: `/dev/ttyACM0`(Cortex USB), `/dev/ttyTHS0/1/4`(UART), `/dev/ttyUSB0`(rplidar)
- 실시간으로 처리:
  - **3× 옴니휠 모터** — `CONTROL_DRIVE(X, Y, W)` 값 범위 **-600 ~ +600**
  - **엔코더 3ch** — `REQUEST_ODOMETER / CONTROL_ENCODER(리셋)`

### 2.3 구동부 — 3-Wheel Omni

- 3개의 옴니휠(Omniwheel) — X/Y 선속도 + W 각속도 3채널 독립 제어
- 엔코더 3개 → `encoder_to_odom.py`가 **옴니휠 기구학(60° 배치)으로 x/y 벡터 및 각속도 계산**
  - `ROUND_LENGTH = 10`(cm, 휠 원주), `ROUND_ENCODER_RATIO = 1`

### 2.4 Cortex 연결 센서 (Omniwheel 프로토콜로 취득)

| 센서 | CMD(MID) | 데이터 | 노트북 |
|---|---|---|---|
| 초음파 (바닥) | REQUEST_BOTTOM_SENSOR 0xA1 (MID 0x80) | 6개 × 3자리 ASCII | 13. Ultrasonic |
| PSD 거리 | 0xA1 (MID 0x81) | 3개 × 3자리 | 12. PSD |
| 스위치(범프) | 0xA2 | 2ch | - |
| 화염 | 0xA3 | 1ch | 5. Flame |
| ECO 조도 | 0xA4 (0x80) | LUX | 6. Light |
| ECO 자세 X/Y/Z | 0xA4 (0x81~0x83) | IMU | 8. 온습도/기압 |
| ECO 기압 | 0xA4 (0x84) | hPa | 8. |
| ECO 지자기 | 0xA4 (0x85) | 나침반 | - |
| PIR 모션 | 0xA5 | 1ch | 4. PIR |
| CO2 가스 | 0xA6 | ppm | 9. CO2 |
| 미세먼지 | 0xA7 | μg/m³ | 10. 미세먼지 |
| 적외선 온도 | 0xA8 | ℃ | 7. 적외선 온도 |
| 마이크로파 모션 | 0xA9 | 1ch | 3. 모션 감지 |
| 사운드 | 0xAA | 4ch | - |
| 배터리 | 0xAB | V | - |

### 2.5 Jetson 직결 장치 (I2C / GPIO / CSI)

| 장치 | 인터페이스 | 용도 | 근거 |
|---|---|---|---|
| **PCA9685** PWM 16ch | I2C (SCL_1/SDA_1) + GPIO D22(EN) | 부저 멜로디(채널15), 서보/LED | PCA9685_Module.py, 예제1-3 |
| **CLCD 16x2** | I2C (SCL/SDA) | 상태 표시 | 11. CLCD, libraries/LCD |
| **PCF8591** ADC/DAC | I2C | 미세먼지 아날로그 측정 (GPIO로 먼지 LED 점등 후 ADC) | 10. 미세먼지 |
| **카메라** | CSI (GStreamer) | 영상 → `tcp://127.0.0.1:5000` TCP 스트림 (406×306) | 6/7. AI 노트북 |

> Jetson에 설치된 Adafruit 계열 라이브러리(BH1750 조도, BME280 온습도/기압, CCS811 CO2, MLX90614 적외선온도)는 **Jetson I2C 직결**로도 동일 센서를 지원하므로, 실제 배선은 "Cortex 경유"와 "Jetson 직결"이 중복 가능한 구조입니다. 어느 경로가 실제 사용되는지는 하드웨어 배선으로 확인 필요.

---

## 3. 통신 계층

### 3.1 Jetson ↔ Cortex — Omniwheel 프로토콜

바이너리+ASCII 혼합 커스텀 패킷 (`Omniwheel_Protocol.py`, `Payload.py`):

```
[STX 0x02] [ID] [Length 2자리] [CMD] [Payload...] [LRC 2자리] [ETX 0x03]
```

- **ID**: 0x10(Jetson) / 0x20(Cortex)
- **Length**: CMD부터 Payload까지 길이 (2자리 ASCII)
- **Payload**: `MID(0x80~0x8F)` + ASCII 문자열 데이터 (다수 MID 다중 포함 가능)
- **LRC**: 검증 합(2자리 16진수 ASCII)
- **CMD**:
  - `REQUEST` 0xA0~0xAB — 센서/엔코더 요청
  - `ANSWER` 0xB0~0xBB — Cortex 응답
  - `CONTROL` 0xC0~0xC2 — 구동(X/Y/W) · 모듈(LED/부저) · 엔코더 리셋

**통신 방식**: 요청-응답 동기 방식. Jetson이 요청을 보내면 `wait_Request` 플래그를 걸고 응답이 올 때까지 대기. `comm_Arduino.py`의 백그라운드 스레드가 직렬 포트를 열고 송수신을 관리.

### 3.2 Jetson ↔ I2C 장치

- I2C 버스: `board.SCL/SDA`(기본 버스)와 `board.SCL_1/SDA_1`(버스 1) 두 곳 사용
- 기기: PCA9685(0x40 부근), CLCD(0x27), PCF8591(0x48), BH1750(0x23), BME280(0x76), CCS811(0x5A), MLX90614(0x5A)

### 3.3 Jetson ↔ 카메라

- CSI 카메라 → TCP 스트림(`tcp://127.0.0.1:5000`) → `PyCamera.URLCamera`가 수신
- `URLCamera` 구현 확인: `cv2.VideoCapture(camera_url)` + `CAP_PROP_BUFFERSIZE=1` + **백그라운드 읽기 스레드**(`live_thread=True`, daemon)로 영상 지연 최소화
- `example06.py`(추적 노드)는 `PyCamera.URLCamera("tcp://localhost:5000")` 사용
- (참고: 스트리밍 서버 프로세스는 로봇 아이들 상태에서 미관찰 — `gst-launch` 파이프라인 명령은 미확인)

### 3.4 ROS 토픽 (ROS1 Melodic — catkin_ws 실측)

| 토픽/패키지 | 타입 | 흐름 |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | AI 노드 → **Robot_Operate.py**(구동 브리지) → Cortex |
| `/sensor_data_pub` | `omniwheel_project/Sensor_data` (32필드) | Robot_Operate.py가 센서 요청 스레드로 주기 발행 |
| `/odom` | `nav_msgs/Odometry` | `encoder_to_odom.py`(엔코더→옴니휠 기구학) 발행 / `omni_navigation`에선 `laser_scan_matcher_node`가 생성 |
| `/scan` | `sensor_msgs/LaserScan` | `rplidarNode` (`/dev/ttyUSB0`, 115200) |
| `msgChatter` | `omniwheel_project/Numb` | 커스텀 메시지 예제 |

- **구동 브리지 노드**: `Robot_Operate.py` — `/cmd_vel`(Twist) 구독 → `CONTROL_DRIVE(X,Y,W)` 직렬 전송, `CTRL_DATA_RATIO = 1200`, 구동 전 엔코더 리셋(`CONTROL_ENCODER` + `MID_CONTROL_CLEAR_ENC`) 수행, `comm_Arduino` 기반
- catkin_ws 구성: `hector_slam`, `omniwheel_project`, `rplidar_ros`
- omniwheel_project 구성: `launch`(4개) · `param`(costmap/planner yaml) · `urdf/omni_robot.urdf` · `msg`(Sensor_data 32필드, Module_ctrl, Numb) · `maps`(lab/mymap/gj/TestMap_v1) · `scripts`(Python 노드) · `navigation_rviz.rviz`
- launch 4종: `omni_slam`(hector_slam + rplidar + teleop), `omni_follow`(example06 + Robot_Operate), `omni_navigation`(map_server+AMCL+move_base+laser_scan_matcher+rviz+Robot_Operate), `move_base`(DWA 플래너 + omni costmap 파라미터)

---

## 4. 소프트웨어 계층

```
┌─────────────────────────────────────────────────┐
│  AI (객체인식 추적)                              │
│  ObjectDetector(bready) ─ TensorRT 8 FP16 엔진  │
│  SSD MobileNet V1 · 300×300 · person/animal      │
│  P-제어: angular=(0.5-x)*2, linear=(0.8-y)*10   │
├─────────────────────────────────────────────────┤
│  ROS Melodic                                     │
│  /cmd_vel publish · omniwheel_project(custom msg)│
├─────────────────────────────────────────────────┤
│  디바이스 드라이버 계층                           │
│  comm_Arduino(직렬/스레드) · PCA9685 · LCD · PCF │
│  Omniwheel_Protocol/Payload · omni_database      │
├─────────────────────────────────────────────────┤
│  bready 패키지                                   │
│  camera_utils.PyCamera(URLCamera)                │
│  object_detection_tools.ObjectDetector/optimizer │
└─────────────────────────────────────────────────┘
```

### 4.1 AI 파이프라인 (03. AI + catkin_ws 실측)

**모델 계열이 2종 존재** (이식 시 모두 ONNX 재변환 대상):

1. **bready UFF→TRT 엔진** (Jupyter Inference 경로):
   - TF Object Detection API — **SSD MobileNet V1**, 2클래스(person, animal), 입력 300×300
   - `pipeline.config`: COCO 사전학습(`ssd_mobilenet_v1_coco_2018_01_28`)에서 fine-tuning
   - checkpoint → **UFF → TensorRT 8 엔진(FP16)**: `model.v1.uff`(22MB) + `model.v1.pbtxt`
   - NMS/GridAnchor를 TRT 커스텀 플러그인(UFF)으로 변환
   - 설치 위치: `/usr/local/lib/python3.6/dist-packages/bready`(1.1.0) + `bready_object_detection`(0.1)
2. **training_models frozen-graph (ROS 추적 노드 경로)**:
   - `scripts/training_models/models_object_detection_coco/` — `data/classes.txt` = **COCO 80클래스 전체**
   - `models/num_recognition_nano` — TRT 최적화 frozen graph
   - `example06.py`에서 `ObjectDetector.Tester('./training_models/.../num_recognition_nano', ...)`로 로드

**추론·추적** (example06.py): 프레임별 `execute()` → `closest_detection`(가장 가까운 person 박스) → P-제어 → `/cmd_vel`

### 4.2 개발/실행 환경

- **Jupyter Notebook(8888)** — 모든 단계(디바이스 테스트→ROS→AI→추적)가 노트북으로 구성됨
- **bready** 패키지(v1.1.0) + **bready-object-detection**(0.1) 커스텀 pip 설치
- 전원/부팅 시 `autodetect_syslog.bash`로 하드웨어 자동 감지

---

## 5. 데이터 흐름 (제어 루프)

### 5.1 사람추적 폐루프 (핵심 동작)

```
카메라(CSI)
  → tcp://127.0.0.1:5000 → PyCamera.URLCamera (live_thread, cv2.VideoCapture)
  → ObjectDetector.execute()  (TensorRT FP16, SSD-MNV1)
  → closest_detection('person') : 박스 중심 (x,y) 정규화
  → P-제어: angular = (0.5 - x) * 2
            linear  = (0.8 - clamp(y, 0.7, 0.8)) * 10
  → Twist → /cmd_vel (ROS)
  → Robot_Operate.py : CTRL_DATA_RATIO=1200 배율 → CONTROL_DRIVE(X, Y, W) 패킷
  → Cortex → 3× 옴니휠 모터 PWM  ← 반복
```

### 5.2 엔코더 → 오드메트리 (위치 피드백)

```
Cortex 엔코더 3ch → REQUEST_ODOMETER → ANSWER_ODOMETER(0xB0)
  → encoder_to_odom.py : 3휠 기구학 → X/Y/각속도
  → omni_database.py (공유 상태 저장)
```

### 5.3 센서 폴링

```
Jetson → REQUEST_*(0xA0~0xAB) → Cortex → ANSWER_*(0xB0~0xBB)
  → payload.getData() : ASCII 파싱(예: 초음파 6개×3자리)
  → omni_database 저장 → Jupyter 모니터링
```

---

## 6. 아키텍처 특이사항 (마이그레이션 관점)

| 구성요소 | 현재(Xavier NX) | Orin Nano 이식 시 영향 |
|---|---|---|
| Cortex 통신 | USB CDC `/dev/ttyACM0`, 115200 | **동일** — USB 시리얼이므로 그대로 사용 가능 |
| PCA9685/CLCD/PCF8591 (I2C) | board.SCL/SDA, SCL_1/SDA_1 | **동일** — Jetson 라이브러리로 호환 (핀맵만 재확인) |
| 카메라 CSI + TCP 스트림 | GStreamer → `127.0.0.1:5000` | 카메라 드라이버는 새 JetPack에서 **재검증** 필요 (CSI 동일 포트) |
| AI 모델 | UFF → **TensorRT 8** 엔진 | **TensorRT 10에서 UFF 제거됨** → `.onnx`로 재변환 필수 |
| bready 패키지 | Py3.6용 | Py3.10(Ubuntu 22.04) 호환 재설치 필요 |
| ROS | Melodic(ROS1) | Humble(ROS2) 포팅 또는 Noetic 유지 선택 |
| omniwheel 프로토콜 | 자체 패킷 (STX~LRC) | **그대로 재사용 가능** — 하드웨어/직렬 레벨 프로토콜이라 플랫폼 무관 |

---

## 7. Jetson 재연결 실측 결과 (2026-08-13)

Jetson(192.168.1.4) SSH 재접속으로 확인된 내용 (위 각 절에 반영):

| 항목 | 결과 |
|---|---|
| ROS 구동 노드 | **확인** — `Robot_Operate.py` (`/cmd_vel` → `CONTROL_DRIVE`, 엔코더 리셋, `/sensor_data_pub` 발행) |
| catkin_ws 구성 | `hector_slam` + `omniwheel_project` + `rplidar_ros` |
| launch 파일 | 4종 전체 내용 확인 (`omni_slam`, `omni_follow`, `omni_navigation`, `move_base`) |
| 네비게이션 | map_server(gj.yaml) + AMCL + move_base(DWA/omni costmap) + laser_scan_matcher + rviz |
| AI 모델 | `training_models/.../num_recognition_nano` (COCO 80클래스), bready는 site-packages에 1.1.0 설치 확인 |
| 직렬 포트 | `/dev/ttyACM0`(Cortex), `/dev/ttyTHS0/1/4`, `/dev/ttyUSB0`(rplidar) — `comm_Arduino` 기본값 `/dev/ttyACM0` 115200 |
| 카메라 | `URLCamera` = `cv2.VideoCapture(tcp://127.0.0.1:5000)` + 백그라운드 읽기 스레드 |
| 실행 프로세스 | 확인 시점에 ROS/GStreamer 프로세스 없음 (아이들 상태) |

## 8. 잔여 미확인 항목

- [ ] 카메라 스트리밍 서버 시작 명령(`gst-launch` 파이프라인) — 실행 중일 때 확인 필요
- [ ] Cortex 펌웨어 (모터 PID, 센서 취득 루프) — 로봇 MCU에 내장
- [ ] `/odom` TF 트리 및 AMCL·laser_scan_matcher 실제 발행 여부 (부팅 시)
- [ ] 실제 센서 배선: Cortex 경유 vs Jetson I2C 직결 중복 항목
- [ ] `training_models/models/num_recognition_nano` 내부 파일 상세 (frozen graph vs TRT engine)

---

## 9. 정리

- 이 로봇은 **Jetson(Xavier NX) — Cortex(MCU)** 2계층 분산 구조로, AI/ROS와 실시간 구동·센서가 분리되어 있습니다.
- 모든 통신이 **자체 제작 Omniwheel 바이너리 프로토콜**로 표준화되어 있어, 하드웨어 경계(직렬/I2C)는 플랫폼 독립적입니다.
- **Orin Nano로 업그레이드할 때 재작업이 필요한 것은 "AI 스택(TRT10 UFF→ONNX, bready 재설치)"과 "ROS 포팅"**이며, 구동부(Cortex)·센서·프로토콜은 그대로 이식 가능합니다.
- 마이그레이션 상세 절차는 `C:\Jetson_Xavier_NX_아키텍처_분석_및_Orin_Nano_마이그레이션.md`와 `C:\Jetson_Orin_Nano_성능_비교_검토.md` 참고.

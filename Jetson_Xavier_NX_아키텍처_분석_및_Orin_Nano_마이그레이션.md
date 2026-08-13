# Jetson Xavier NX 시스템 아키텍처 분석 및 Orin Nano 마이그레이션 가이드

> 대상 시스템: `bready-desktop` (192.168.1.4) — Jetson Xavier NX Developer Kit
> 목적: 현재 시스템의 아키텍처를 정리하고, 이를 기반으로 **Jetson Orin Nano**로 업그레이드하는 방법 제시
> 작성일: 2026-08-13

---

## 목차

1. [현재 시스템 아키텍처 분석](#1-현재-시스템-아키텍처-분석)
2. [아키텍처 다이어그램](#2-아키텍처-다이어그램)
3. [Orin Nano 성능/사양 비교](#3-orin-nano-성능사양-비교)
4. [구성요소별 마이그레이션 매핑](#4-구성요소별-마이그레이션-매핑)
5. [마이그레이션 절차](#5-마이그레이션-절차)
6. [검증 체크리스트](#6-검증-체크리스트)
7. [리스크 및 주의사항](#7-리스크-및-주의사항)

---

## 1. 현재 시스템 아키텍처 분석

### 1.1 하드웨어 계층

- **보드**: NVIDIA Jetson Xavier NX Developer Kit (260핀 SO-DIMM 모듈)
- **CPU**: 6-core Carmel (ARM64) @ 1.9GHz
- **GPU**: Volta 아키텍처 384 CUDA + 48 Tensor 코어, **DLA(INT8 가속기) 보유**
- **메모리**: 8GB LPDDR4x (확인: 7.6GB), 51.2 GB/s 대역폭
- **저장장치**:
  - `/dev/mmcblk1p1` 59GB microSD → **루트 파일시스템** (/)
  - `/dev/mmcblk0p1` 14GB eMMC → 데이터 보조 (미디어 마운트)
- **네트워크**: 이더넷 192.168.1.4, Wi-Fi(NetworkManager), Ubuntu 18.04.5 + 커널 4.9.253-tegra

### 1.2 OS 및 NVIDIA 소프트웨어 스택

| 계층 | 버전 | 비고 |
|---|---|---|
| OS | Ubuntu 18.04.5 (bionic) | |
| 커널 | 4.9.253-tegra | NVIDIA L4T R32.6.1 |
| JetPack | **4.6.1 (L4T R32.6.1)** | Xavier NX 지원 세대 |
| CUDA | 10.2.300 | |
| cuDNN | 8.2.1.32 | |
| TensorRT | 8.0.1.6 (lib + python) | |
| OpenCV | 4.1.1 | |
| GStreamer | 1.14.5 | 카메라/영상 |
| VisionWorks / v4l2 | 포함 | |

### 1.3 AI 런타임 계층 (Python 3.6.9)

| 패키지 | 버전 | 용도 |
|---|---|---|
| tensorflow | 2.5.0+nv21.7 | 객체인식 모델 학습/추론 (GPU) |
| numpy | 1.19.4 | |
| onnx / onnxruntime | 1.9.0 / 1.8.1 | 모델 변환·추론 |
| pycuda | 2019.1.2 | 커스텀 CUDA 호출 |
| pycocotools | - | COCO 평가 |
| tensorrt | 8.0.1.6 | TRT 엔진 python API |
| **torch** | **설치 안 됨** | 필요 시 별도 설치 필요 |
| bready | 1.1.0 | 커스텀 pip 패키지 |
| bready-object-detection | 0.1 | 커스텀 물체감지 패키지 |

### 1.4 로봇 프레임워크 계층

- **ROS Melodic** (`/opt/ros/melodic`) — ROS1 최신종 (EOL)
- **catkin_ws** 워크스페이스 존재 → 로봇 제어 노드 빌드 환경
- ROS1 + 객체인식(python)을 결합한 구조

### 1.5 센서/주변기기 계층 (GPIO 및 I2C/USB)

| 라이브러리 | 버전 | 대상 센서 |
|---|---|---|
| Jetson.GPIO | 2.0.17 | 40핀 GPIO, PWM |
| Adafruit-Blinka | 6.13.0 | CircuitPython 호환 센서 |
| - | - | **BH1750** (조도) |
| - | - | **BME280** (온습도/기압) |
| - | - | **CCS811** (CO2/VOC) |
| - | - | **MLX90614** (비접촉 온도) |
| - | - | **PCA9685** (PWM 16ch → 모터/서보) |
| - | - | **PCF8591** (ADC/DAC) |
| spidev | - | SPI |
| rplidar-roboticia | 0.9.5 | RPLidar (레이저) |
| PyAudio / pygame | - | 오디오 |
| pyserial / pyusb / pyftdi | - | 시리얼/USB/FTDI |

### 1.6 서비스/데몬 계층 (systemd)

| 서비스 | 용도 |
|---|---|
| ssh | 원격 접속 |
| docker (20.10.2) | 컨테이너 |
| jupyter_notebook | Jupyter 서버 (port 8888, `AI_Omniwheel` 서빙) |
| nvargus-daemon / nvgetty / nvphs | NVIDIA 카메라/시리얼 |
| gpsd | GPS |
| smbd (Samba) | 파일 공유 |
| run_autodetect | 부팅 자동 감지 |

### 1.7 애플리케이션 계층

- **AI_Omniwheel** — 메인 프로젝트 (Jupyter 기반 객체인식/물체감지)
- **HiBready / HiBready_Editor_Data** — Unity 연동 프로젝트
- **installROSXavier** — ROS 설치 스크립트
- **startup / test / project / jupyter_example** — 실행/테스트 스크립트
- **Node.js v14.16.1** — 웹 연동용

### 1.8 환경 특이사항

- `.bashrc`에 CUDA PATH, `LD_LIBRARY_PATH`, `LD_PRELOAD=libgomp` 설정
- apt 저장소: NVIDIA cuda-repo-l4t-10-2-local, repo.download.nvidia.com r32.6, packages.ros.org(bionic)
- `autodetect_syslog.bash` — 부팅 시 하드웨어 자동 감지 로그

---

## 2. 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│  AI_Omniwheel(Jupyter 8888) | HiBready(Unity) | Node.js v14 │
│  bready / bready-object-detection (pip)                     │
├─────────────────────────────────────────────────────────────┤
│                    ROBOT FRAMEWORK                          │
│            ROS Melodic (ROS1) + catkin_ws                   │
├─────────────────────────────────────────────────────────────┤
│                    AI RUNTIME (Py3.6)                       │
│  TF 2.5.0+nv21.7 | TensorRT 8.0.1 | onnx/onnxruntime       │
│  pycuda | numpy | pycocotools                               │
├─────────────────────────────────────────────────────────────┤
│                    NVIDIA COMPUTE STACK                     │
│  CUDA 10.2 | cuDNN 8.2.1 | OpenCV 4.1.1 | GStreamer 1.14.5 │
├─────────────────────────────────────────────────────────────┤
│                    OS LAYER                                 │
│  Ubuntu 18.04.5 | kernel 4.9.253-tegra | JetPack 4.6.1     │
│  Docker 20.10.2 | systemd (ssh/jupyter/gpsd/samba)          │
├─────────────────────────────────────────────────────────────┤
│                    HARDWARE (Xavier NX)                     │
│  Volta 384 CUDA + 48 Tensor + DLA | 6×Carmel | 8GB LPDDR4x  │
│  microSD 59G(root) + eMMC 14G | 40핀 GPIO | CSI | USB | GbE │
│  센서: BH1750/BME280/CCS811/MLX90614/PCA9685/PCF8591/RPLidar│
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Orin Nano 성능/사양 비교

| 항목 | Xavier NX 8GB (현재) | Orin Nano 8GB (기본) | Orin Nano Super |
|---|---|---|---|
| GPU | Volta 384+48 Tensor | Ampere 1024 | Ampere 1024 @1.02GHz |
| AI 성능 | 21 TOPS | 40 TOPS | 67 TOPS |
| CPU | 6× Carmel 1.9GHz | 6× A78AE 1.5GHz | 6× A78AE 1.7GHz |
| 메모리 | 8GB LPDDR4x 51.2GB/s | 8GB LPDDR5 68.3GB/s | 8GB LPDDR5 102.4GB/s |
| DLA | **있음** | **없음** | **없음** |
| OS 지원 | Ubuntu 20.04 (JetPack 5.1.7 끝) | **Ubuntu 22.04 (JetPack 6.x)** | 동일 |

**체감 차이**: AI 약 2배(Super 3배), CPU 1.5~2배, 대역폭 1.3~2배, ROS2 Humble 네이티브 가능.

> 자세한 비교 및 구매 판단은 별도 문서 `C:\Jetson_Orin_Nano_성능_비교_검토.md` 참고.

---

## 4. 구성요소별 마이그레이션 매핑

현재 아키텍처의 각 계층을 Orin Nano(JetPack 6.x 기준)로 옮기는 대응표입니다.

### 4.1 OS 및 컴퓨트 스택

| 현재 (Xavier NX) | Orin Nano (JetPack 6.x) | 작업 |
|---|---|---|
| Ubuntu 18.04 / Python 3.6.9 | Ubuntu 22.04 / Python 3.10 | 코드 문법 호환 검증 (`2to3`/`ruff`) |
| JetPack 4.6.1 | JetPack 6.x (5.1.7부터 시작해도 무방) | SDK Manager로 신규 플래시 |
| CUDA 10.2.300 | CUDA 12.x | 커스텀 C/CUDA 확장 **재컴파일** |
| cuDNN 8.2.1 | cuDNN 9.x | - |
| TensorRT 8.0.1 | TensorRT 10.x | **엔진 재빌드** (`.engine` 재생성) |
| OpenCV 4.1.1 | OpenCV 4.8+ | API 대부분 호환 |
| GStreamer 1.14.5 | GStreamer 1.20+ | nvarguscamerasrc 동일 |

### 4.2 AI 런타임

| 현재 | Orin Nano | 작업 |
|---|---|---|
| TensorFlow 2.5.0+nv21.7 | TF 2.15/2.16 (NGC wheel) 또는 **PyTorch 2.4+** | 모델 `.h5`/SavedModel → 재로드·재변환 |
| onnx 1.9.0 / onnxruntime 1.8.1 | onnxruntime-gpu 최신 | 재설치 |
| pycuda 2019.1.2 | pycuda 최신 | 재컴파일 |
| bready 1.1.0 / bready-object-detection 0.1 | 동일 (재설치) | `pip install` |
| torch 없음 | PyTorch 가능 (JetPack 6) | 선택 설치 |

> **실측 모델 2종 (2026-08-13, Jetson SSH 확인)** — 둘 다 TRT 8 기반이므로 Orin Nano(TRT 10) 이식 시 **모두 ONNX 재변환 필요**:
> 1. `bready` UFF→TRT 8 엔진 — SSD MobileNet V1 2클래스(person/animal), 300×300, `model.v1.uff` (Jupyter Inference 경로)
> 2. `catkin_ws/.../scripts/training_models/models_object_detection_coco/models/num_recognition_nano` — COCO **80클래스** frozen graph, TRT 최적화 (ROS 추적 노드 `example06.py`가 사용)
>
> `classes.txt`(80클래스)와 bready 사이트패키지 위치를 확인했고, UFF 컨버터(TRT 8 내장)는 TRT 10에서 제거되므로 TF→ONNX→TRT 10 순서로 재구축해야 합니다.

### 4.3 로봇 프레임워크

| 현재 | Orin Nano | 작업 |
|---|---|---|
| ROS Melodic (ROS1) | **ROS2 Humble (네이티브, Ubuntu 22.04 지원)** 또는 ROS1 Noetic | 노드 포팅: `rospy→rclpy`, 메시지 재생성, launch 파일 변환 |
| catkin_ws | colcon_ws | 빌드 시스템 전환 |

> ROS2로 갈지 ROS1 Noetic 유지(구버전 코드 그대로)인지는 **코드 복잡도**에 따라 결정. 객체인식은 Python이므로 rclpy 포팅 난이도 낮음.

### 4.4 센서/GPIO

| 현재 | Orin Nano | 작업 |
|---|---|---|
| Jetson.GPIO 2.0.17 | Jetson.GPIO 최신 | 핀 번호 보드라벨 기준 동일, **칩 번호 재확인** |
| Adafruit Blinka 6.13.0 | 최신 (A78AE 지원 추가됨) | 재설치, `board.SDA/SCL` 매핑 확인 |
| BH1750/BME280/CCS811/MLX90614/PCA9685/PCF8591 | 동일 라이브러리 | I2C 버스 주소 변경 여부 확인 |
| spidev / rplidar | 동일 | USB 직결이면 드라이버 그대로 |
| PyAudio/pygame/pyserial | 동일 | USB 기기라면 그대로 |

### 4.5 서비스 및 데이터

| 현재 | Orin Nano | 작업 |
|---|---|---|
| jupyter_notebook (8888) | 동일 재구성 | systemd 유닛 재생성 |
| docker 20.10.2 | docker 최신 (JetPack 6 기본) | - |
| gpsd / smbd | 동일 | 설정 복사 |
| microSD 루트 59G + eMMC 14G | microSD 루트 + NVMe 권장 | 데이터 이전 (rsync/scp) |

---

## 5. 마이그레이션 절차

### Phase 1 — 사전 준비 (현재 보드에서)

1. **DLA 사용 여부 확인** (핵심 결정 포인트)
   - `grep -r "dla" /home/bready/AI_Omniwheel` / `trtexec --help | grep DLA`
   - DLA 사용 중이면 **Orin NX**로 방향 전환.
2. 코드/데이터 백업
   - `rsync -av /home/bready/AI_Omniwheel /home/bready/catkin_ws ...`
   - 루트 저장소 목록 백업: `pip freeze > requirements.txt`, `dpkg --get-selections`
3. 모델 파일 확보: `.h5`/SavedModel/`.onnx`/`.engine` 원본 확인 (TRT 10은 8 엔진 못 읽음 → **onnx 재변환**)

### Phase 2 — 하드웨어 조달

4. **Orin Nano 8GB Dev Kit** 구매 (Super는 소프트웨어 업데이트로 추후 적용)
   - CSI 카메라/전원/부팅미디어(권장 NVMe 128G+) 포함 확인

### Phase 3 — 베이스 OS 구축 (신규 보드)

5. NVIDIA SDK Manager로 **JetPack 6.x** 플래시 (또는 SD 카드 이미지)
6. 사용자 `bready` 생성, SSH/Samba/gpsd 설정 (기존 설정 복원)
7. CUDA/cuDNN/TensorRT/OpenCV apt 설치 (JetPack 기본 포함 여부 확인)

### Phase 4 — AI/ROS 스택 (신규 보드)

8. Python 3.10 가상환경 구성 → NGC wheel로 TF 또는 PyTorch 설치
9. **ROS2 Humble** 설치 (`ros2-*-humble` apt) 또는 ROS1 Noetic
10. 커스텀 pip 패키지(bready 등) 재설치, `.bashrc` 환경변수 복원

### Phase 5 — 애플리케이션 이식

11. 프로젝트 코드 복사 → 경로/하드코딩 수정
12. TensorRT 엔진 **onnx 재변환** (TF 2.5 그래프 → onnx → TRT 10)
13. ROS 노드 포팅 (rospy→rclpy) 및 colcon 빌드
14. 센서 테스트: GPIO/I2C/USB 라이브러리 재설치 후 각 센서 읽기 확인

### Phase 6 — 서비스화 및 통합

15. jupyter_notebook systemd 유닛 재생성 (8888, AI_Omniwheel 서빙)
16. 부팅 자동실행(autodetect, startup) 복원
17. 전체 워크플로우 통합 시험

---

## 6. 검증 체크리스트

- [ ] `nvidia-smi` / `jetson_release` → JetPack 6.x 정상
- [ ] TensorRT 10에서 `.engine` 생성 및 추론 FPS 확인 (기존 대비 ≥2배 목표)
- [ ] ROS2 토픽 발행/구독 정상 (또는 Noetic 노드 구동)
- [ ] Jupyter 8888 접속 및 AI_Omniwheel 노트북 실행
- [ ] GPIO: 모터(PCA9685)/서보 PWM 출력 정상
- [ ] I2C: BH1750/BME280/CCS811/MLX90614 센서값 정상 (주소 확인)
- [ ] RPLidar 스캔 데이터 정상
- [ ] CSI/USB 카메라 GStreamer 파이프라인 정상
- [ ] GPS(Serial) 수신 정상
- [ ] Samba/SSH/네트워크(192.168.1.4) 정상
- [ ] HiBready(Unity) ↔ 보드 통신 정상

---

## 7. 리스크 및 주의사항

1. **DLA 의존성** — Orin Nano는 DLA가 없음. DLA 사용 시 Orin NX로 계획 변경.
2. **TensorRT 엔진 호환 불가** — `.engine`은 GPU 세대/버전 간 호환 안 됨. 반드시 onnx 재변환.
3. **TF 2.5 코드** — Python 3.10에서 `tf.compat.v1` 세션 방식 코드는 수정 필요 (Eager/`keras` 모델 권장).
4. **ROS Melodic → Humble 포팅** — 메시지/서비스 타입 변경이 있을 수 있어 **시간 배정 필수**.
5. **GPIO 핀맵** — 보드라벨(BOARD 모드)은 같지만 커널 칩 번호(SYSFS) 다를 수 있어 실행 테스트로 확인.
6. **CSI 카메라** — 캐리어 보드 변경 시 카메라 드라이버/배선 재검증.
7. **비용** — Dev Kit 구매 + NVMe 등 부수 비용. DLA가 필요 없다면 "성능 2배 + SW 제약 해소"가 투자 대비 확실한 이득.

---

> 참고 문서
> - `C:\Jetson_Orin_Nano_성능_비교_검토.md` — 성능 비교 상세
> - `C:\Jetson_Xavier_NX_시스템_재구성_가이드.md` — 기존 환경 재현
> - `C:\Jetson_Xavier_NX_최신_시스템_구축_가이드.md` — JetPack 5.1.7 최신 구축
> - `C:\Jetson_Xavier_NX_ROS2_사용_가이드.md` — ROS2 분리 사용

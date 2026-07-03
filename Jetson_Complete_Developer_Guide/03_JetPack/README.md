# 03. JetPack SDK

## 1. JetPack 개요

JetPack은 NVIDIA Jetson 보드를 위한 **통합 소프트웨어 패키지**입니다.

```
JetPack = L4T (Linux for Tegra) + CUDA + cuDNN + TensorRT
          + OpenCV + GStreamer + VPI + Multimedia API + ...
```

| 구성 요소 | 역할 |
|-----------|------|
| **L4T** (Linux for Tegra) | Ubuntu 기반 커스텀 Linux OS + 부트로더 + 디바이스 드라이버 |
| **CUDA** | GPU 병렬 컴퓨팅 플랫폼 |
| **cuDNN** | 딥러닝 가속 라이브러리 (Convolution, LSTM 최적화) |
| **TensorRT** | AI 추론 최적화 엔진 (FP16/INT8 양자화, NVDLA 연동) |
| **OpenCV** | 컴퓨터 비전 라이브러리 (CUDA 가속 지원) |
| **GStreamer** | 멀티미디어 파이프라인 (카메라, 인코딩/디코딩) |
| **VPI** (Vision Programming Interface) | 하드웨어 가속 컴퓨터 비전 |
| **Multimedia API** | 카메라, 비디오 인코더/디코더 저수준 API |

---

## 2. JetPack 버전별 상세 비교

### 버전별 매핑

| JetPack | L4T | Ubuntu | CUDA | cuDNN | TensorRT | Python | OpenCV | 출시 |
|:-------:|:---:|:------:|:----:|:-----:|:--------:|:------:|:------:|:----:|
| **4.6** | 32.6.1 | 18.04 | 10.2 | 8.x | 8.x | 3.6 | 4.1.1 | 2021 |
| **4.6.1** | 32.7.1 | 18.04 | 10.2 | 8.x | 8.4 | 3.6 | 4.1.1 | 2022 |
| **5.0** | 34.1.0 | 20.04 | 11.4 | 8.4 | 8.4 | 3.8 | 4.5 | 2022 |
| **5.1** | 35.1.0 | 20.04 | 11.4 | 8.6 | 8.5 | 3.8 | 4.5 | 2023 |
| **5.1.3** | 35.5.0 | 20.04 | 11.4 | 8.8 | 8.6 | 3.8 | 4.5 | 2024 |
| **6.0** | 36.3.0 | 22.04 | 12.2 | 8.9 | 8.6 | 3.10 | 4.8 | 2024 |
| **6.1** | 36.4.0 | 22.04 | 12.6 | 9.3 | 10.x | 3.10 | 4.8 | 2025 |

### 지원 보드

| 보드 | JetPack 4.6 | JetPack 5.x | JetPack 6.x |
|------|:-----------:|:-----------:|:-----------:|
| Jetson Nano | O | X | X |
| **Xavier NX** | **O** | **O** | **O** (6.1+) |
| AGX Xavier | O | O | O (6.1+) |
| Orin Nano | X | O | O |
| Orin NX | X | O | O |
| AGX Orin | X | O | O |

### 현재 환경 (JetPack 4.6)의 특징

| 장점 | 단점 |
|------|------|
| 매우 안정적, 수많은 검증 사례 | Python 3.6 (오래됨) |
| ROS1 Melodic 네이티브 지원 | ROS2 Humble/Jazzy 미지원 |
| NVDLA 완벽 지원 | CUDA 10.2 (최신 CUDA 12.x와 호환성 낮음) |
| Ubuntu 18.04 안정성 | Isaac ROS 일부 기능 미지원 |
| Xavier NX 최적 성능 | 최신 AI 모델 변환 시 제약 |

---

## 3. 설치 확인

```bash
# JetPack 버전 확인
cat /etc/nv_tegra_release
# → R32 (release), REVISION: 6.1

# CUDA 버전
nvcc --version
# → Cuda compilation tools, release 10.2, V10.2.89

# cuDNN 버전
cat /usr/include/cudnn_version.h | grep CUDNN_MAJOR -A 2

# TensorRT 버전
dpkg -l | grep tensorrt
# 또는
python3 -c "import tensorrt; print(tensorrt.__version__)"

# OpenCV 버전
python3 -c "import cv2; print(cv2.__version__)"

# VPI 버전
dpkg -l | grep vpi
```

---

## 4. 주요 컴포넌트 설치 스크립트

```bash
#!/bin/bash
# JetPack 4.6 환경必备 패키지 설치

# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 개발 도구
sudo apt install -y build-essential cmake git vim \
    python3-pip python3-dev python3-numpy

# 3. Python 패키지
pip3 install --upgrade pip
pip3 install numpy opencv-python pillow matplotlib \
    jupyterlab pandas tqdm

# 4. Jetson.GPIO
sudo pip3 install Jetson.GPIO
sudo groupadd -f gpio
sudo usermod -aG gpio $USER

# 5. I2C 도구
sudo apt install -y i2c-tools

# 6. ROS1 Melodic
sudo apt install -y ros-melodic-desktop
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
```

---

## 5. JetPack 업그레이드 가이드 (JetPack 4.6 → 5.x)

### 고려사항

| 항목 | 4.6 (현재) | 5.x (업그레이드) |
|------|:--------:|:--------------:|
| Ubuntu | 18.04 → **재설치 필요** | 20.04 |
| CUDA | 10.2 → **재설치 필요** | 11.4 |
| Python | 3.6 → **재설치 필요** | 3.8 |
| ROS | Melodic → **변경** | Foxy/Galactic |
| 저장된 데이터 | **전부 소실** | SD 카드 교체로 보존 가능 |

### 업그레이드 방법

```
1. JetPack 5.x SD 카드 이미지 다운로드 (NVIDIA 공식 사이트)
2. SD 카드에 이미지 플래싱 (balenaEtcher, dd 등)
3. 필요한 패키지 재설치
4. 데이터 마이그레이션
```

> **SD 카드 방식은 보드+SD 카드만으로 간단히 버전 전환이 가능**하므로,
> 프로젝트별로 SD 카드를 교체하여 사용하는 것을 추천합니다.

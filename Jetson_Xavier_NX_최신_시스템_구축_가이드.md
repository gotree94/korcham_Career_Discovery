# NVIDIA Jetson Xavier NX 최신 시스템(JetPack 5.1.7) 구축 가이드

> 작성일: 2026-08-13
> 대상 하드웨어: **NVIDIA Jetson Xavier NX Developer Kit** (현재 `192.168.1.4` / `bready-desktop`)
> 현재 시스템: JetPack 4.6.1 (Ubuntu 18.04, Python 3.6)
> 이 문서의 목표: **이 하드웨어에서 구동 가능한 최신 소프트웨어 스택으로의 구축 방법 상세 안내**

---

## 1. 핵심 요약

| 항목 | 현재 (JetPack 4.6.1) | **최신 (JetPack 5.1.7)** |
|---|---|---|
| Jetson Linux (L4T) | R32.6.1 | **R35.6.5** |
| OS | Ubuntu 18.04.5 LTS | **Ubuntu 20.04 LTS** |
| 커널 | 4.9.253-tegra | **5.10.x-tegra** |
| 부트로더 | TegraBoot | **UEFI + OP-TEE** |
| CUDA | 10.2.300 | **11.4.19** (옵션: 11.8/12.x 업그레이드 가능) |
| cuDNN | 8.2.1.32 | **8.6.0** |
| TensorRT | 8.0.1 | **8.5.2** |
| OpenCV | 4.1.1 | **4.5.4** |
| VPI | - | **2.4** |
| Python | 3.6.9 | **3.8.10** |
| TensorFlow | 2.5.0+nv21.7 | **2.12.0+nv23.06** (cp38) |
| PyTorch | 미설치 | **2.1.0a0+nv23.06** (cp38) |
| ROS | Melodic (18.04) | **Noetic** (20.04) |
| Vulkan | 1.1 | **1.3** |
| Nsight Tools | - | Systems 2022.5 / Graphics 2022.6 |

### ⚠️ 가장 중요한 제약 (2026년 기준 확정 정보)
- **Jetson Xavier NX는 JetPack 5.x가 마지막 지원 버전입니다.**
  - NVIDIA 공식: "JetPack 6 does not support Xavier series" (NVIDIA 포럼, 2024-11)
  - JetPack 6/7은 **Orin 계열 전용** (Ubuntu 22.04+).
- Xavier NX 지원의 **최종판 = JetPack 5.1.7 / L4T 35.6.5** (2026-07-24 릴리스).
  - 5.1.6 (2026-02) 이후 버그 수정/보안 패치 반영.
- 따라서 "이 보드의 최신 구성"은 **JetPack 5.1.7**이며, 이후 버전은 이 하드웨어에 설치 불가.
- NVIDIA는 Xavier 시리즈의 수명 종료(EOL)를 준비 중이며 보안 업데이트 범위가 제한됩니다.

---

## 2. 준비 사항

### 2.1. 하드웨어
| 항목 | 필요 사항 |
|---|---|
| 호스트 PC | SDK Manager 사용 시 **Ubuntu 18.04/20.04 x86 PC** 필요 (SD 이미지 방식은 Windows/macOS/Linux 모두 가능) |
| microSD | 64 GB 이상, U3 속도 권장 (JetPack 5 루트파일시스템 + 개발 패키지 용량 필요) |
| USB 케이블 | Micro-B (OTG, 리커버리 모드 진입용) |
| 전원 | 19V/3A USB-C 또는 보드 전용 어댑터 |
| 네트워크 | 이더넷 또는 Wi-Fi (apt/패키지 다운로드) |

### 2.2. 데이터 백업 (필수)
기존 보드(4.6.1)의 사용자 데이터를 먼저 백업하세요. JetPack 5는 **재플래시 기반 전환이며 기존 시스템 보존이 불가능**합니다.
```bash
# 기존 보드에서 SSH로 백업
scp -r bready@192.168.1.4:/home/bready/AI_Omniwheel .
scp -r bready@192.168.1.4:/home/bready/catkin_ws .
scp bready@192.168.1.4:/home/bready/.bashrc .
scp bready@192.168.1.4:/home/bready/autodetect_syslog.bash .

# 전체 pip 패키지 목록 저장
pip3 freeze > packages_jp461.txt
```

### 2.3. 알아둘 사항: 4.6 → 5.x 직접 업그레이드는 불가
- JetPack 4.x(R32) 부트 콘텐츠는 JetPack 5.x(R35)와 **호환되지 않습니다.**
- NVIDIA 공식 답변: "JetPack 4.x releases are incompatible with JetPack 5.x releases. Please have a host PC to do the reflash."
- OTA 업그레이드(32.x→35.x)도 지원되지 않음.
- → **반드시 QSPI 업데이트 + 재플래시 절차**를 따라야 합니다 (3장).

---

## 3. JetPack 5.1.7 설치 (업그레이드 경로)

### 경로 A — SD 카드 이미지 방식 (권장, 호스트 PC OS 제약 없음)

#### Step 1. QSPI 펌웨어 업데이트 (4.x에서 처음 5.x 진입 시 1회 필수)
JetPack 5.x를 **한 번도** 실행하지 않은 보드는 QSPI를 먼저 35.1 이상으로 업데이트해야 합니다.

1. QSPI 이미지 다운로드:
   ```
   https://developer.nvidia.com/embedded/L4T/r35_Release_v1.0/QSPI-img/Jetson_Xavier_NX_QSPI_35.1.gz
   ```
2. 보드를 **리커버리 모드**로 진입:
   - 전원 연결 상태에서 리셋 버튼과 리커버리 버튼을 함께 누름
   - 리셋 먼저 해제 → 3초 후 리커버리 해제
   - 호스트 PC에서 `lsusb` → `0955:7e19 NVidia Corp.` 확인
3. 호스트 PC(Linux)에서 `Jetson_Xavier_NX_QSPI_35.1.gz` 압축 해제 후:
   ```bash
   sudo ./updater.sh --bl -c <해제된 디렉터리>/qspi_flash/*  # QSPI 플래시
   ```
   - Windows 호스트의 경우 NVIDIA SDK Manager 또는 리눅스 VM에서 수행.

#### Step 2. SD 카드 이미지 다운로드 및 작성
- JetPack 5.1.5용 Xavier NX 개발자 키트 SD 카드 이미지 다운로드:
  ```
  https://developer.nvidia.com/downloads/embedded/l4t/r35_release_v6.0/JP514-xnx-sd-card-image_b11.zip
  ```
  (파일명은 JP514이지만 **JetPack 5.1.5 / L4T 35.6.2 이미지**입니다)
- 이미지 작성:
  - **Windows**: Rufus 또는 balenaEtcher
  - **Linux**: `sudo dd if=sd_card_image.img of=/dev/sdX bs=4M status=progress && sync`

#### Step 3. 첫 부팅 및 초기 설정
1. SD 카드 삽입 후 부팅
2. Ubuntu 설치 마법사:
   - 언어/키보드/시간대
   - 사용자명: `bready`, 비밀번호: `00000000`, 호스트명: `bready-desktop`
   - 자동 로그인 여부 선택
3. 첫 부팅 후 반드시 재부팅 1회

#### Step 4. JetPack 5.1.5 → 5.1.7 (최신) 업그레이드
```bash
# 1) NVIDIA 저장소를 r35.6으로 변경
sudo vi /etc/apt/sources.list.d/nvidia-l4t-apt-source.list
#  → 모든 URL의 r35.x 버전을 "r35.6"으로 수정

# 2) 시스템 전체 업그레이드
sudo apt update
sudo apt dist-upgrade -y
sudo apt install -f -o Dpkg::Options::="--force-overwrite"
sudo reboot

# 3) 버전 확인
cat /etc/nv_tegra_release        # R35 (REV 6.5) 확인
```

### 경로 B — NVIDIA SDK Manager 방식 (Ubuntu 호스트 PC 필수)
```text
1. NVIDIA SDK Manager 다운로드: https://developer.nvidia.com/sdk-manager
2. JetPack 5.1.7 선택, Target Hardware: "Jetson Xavier NX modules"
3. 보드를 리커버리 모드로 진입 후 USB 연결 (lsusb: 0955:7e19)
4. SDK Manager가 OS 플래시 + JetPack 구성요소(CUDA/cuDNN/TensorRT 등) 설치까지 자동 수행
   - Host Machine 구성요소는 선택 해제 가능
   - 저장 공간이 부족하면 "Jetson Runtime Components"만 선택
5. 초기 설정: bready / 00000000 / bready-desktop
```

### 경로 C — Jetson Linux 35.6.5 타르볼 + 수동 플래시
```bash
# 호스트 Linux에서
wget https://developer.nvidia.com/downloads/embedded/l4t/r35_release_v6.0/release/Jetson_Linux_R35.6.5_aarch64.tbz2
# 압축 해제 후
sudo ./flash.sh -r jetson-xavier-nx-devkit mmcblk0p1
```
- SDK Manager가 없는 환경에서 수동 제어가 필요할 때 사용.

> **권장**: SD 카드 이미지로 시작해 apt로 5.1.7까지 올리는 방식이 가장 간단하고 호스트 OS 제약이 없습니다.

---

## 4. 시스템 기본 설정

```bash
# 패키지 저장소/업그레이드
sudo apt update && sudo apt upgrade -y

# 개발 기본 도구
sudo apt install -y build-essential cmake make git python3-pip python3-dev
sudo apt install -y ssh openssh-server network-manager
sudo apt install -y gpsd samba vsftpd

# pip 최신화
sudo python3 -m pip install --upgrade pip

# swap 파일 확장 (메모리 8GB, AI 빌드 시 유용) — jetsonhacks
git clone https://github.com/JetsonHacksNano/installSwapfile
cd installSwapfile && ./installSwapfile.sh && sudo reboot

# jetson-stats (jtop 모니터링)
sudo pip3 install -U jetson-stats
# 재부팅 후: jtop
```

### 환경변수 설정 (~/.bashrc)
```bash
cat >> ~/.bashrc << 'EOF'
# CUDA
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
# JetPack 5에서 OpenMP 필요 시
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1${LD_PRELOAD:+:${LD_PRELOAD}}
EOF
source ~/.bashrc
```

---

## 5. NVIDIA 핵심 컴퓨트 스택 (CUDA / cuDNN / TensorRT / OpenCV)

JetPack 5.1.7 이미지에는 OS 설치 시 기본 포함되어 있습니다. 필요한 구성요소만 추가 설치:
```bash
sudo apt update
sudo apt install -y nvidia-jetpack          # JetPack 핵심 런타임+개발 패키지 전체

# 또는 개별 설치 (선택)
sudo apt install -y cuda-toolkit-11-4 libcudnn8 libcudnn8-dev
sudo apt install -y nvidia-tensorrt          # TensorRT 8.5.2 + Python 바인딩
sudo apt install -y libopencv-dev python3-opencv   # OpenCV 4.5.4 (NVIDIA 빌드)
```

### (선택) CUDA 최신 버전 업그레이드
JetPack 5.0.2부터 **Jetson Linux/다른 구성요소 업데이트 없이 CUDA 11.8 이상 설치 가능** (NVIDIA CUDA for Tegra 앱노트 방식).
```bash
# CUDA 12.x 예 (Ubuntu 20.04용 aarch64)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004-arm64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update
sudo apt install -y cuda-toolkit
```
> 주의: cuDNN/TensorRT는 JetPack 기본(11.4)과 함께 동작하며, 일부 프레임워크 wheel은 CUDA 11.4 기반이므로 **기본값 유지 권장**.

### 설치 검증
```bash
nvcc --version                            # release 11.4
dpkg -l | grep -E "cudnn|tensorrt"       # libcudnn8 8.6.x / tensorrt 8.5.x
python3 -c "import cv2; print(cv2.__version__)"   # 4.5.4
python3 -c "import tensorrt; print(tensorrt.__version__)"  # 8.5.x
gst-inspect-1.0 --version                 # 1.16.x
```

---

## 6. Python AI 프레임워크 (JetPack 5.1.x 전용 NVIDIA wheel)

> Ubuntu 20.04 = **Python 3.8 (cp38)**. PyPI의 x86 바이너리는 사용 불가 → 반드시 NVIDIA 제공 aarch64 wheel 사용.

### 6.1 TensorFlow 2.12.0+nv23.06 (JetPack 5.1.x 최신)
```bash
# NVIDIA 공식 wheel 인덱스에서 설치 (JP 5.1.2+용)
python3 -m pip install tensorflow==2.12.0+nv23.06 \
  --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v512/pip
# 또는 특정 파일 직접 설치
# wget https://developer.download.nvidia.com/compute/redist/jp/v512/tensorflow/tensorflow-2.12.0+nv23.06-cp38-cp38-linux_aarch64.whl
# python3 -m pip install ./tensorflow-2.12.0+nv23.06-cp38-cp38-linux_aarch64.whl
```

### 6.2 PyTorch 2.1.0a0+nv23.06 (JetPack 5.1.x 최신)
```bash
python3 -m pip install --upgrade pip
python3 -m pip install numpy==1.26.1       # 의존성 고정 권장
python3 -m pip install --no-cache \
  https://developer.download.nvidia.com/compute/redist/jp/v512/pytorch/torch-2.1.0a0+41361538.nv23.06-cp38-cp38-linux_aarch64.whl
# torchvision 동일 인덱스에서 설치 (버전은 Download Center에서 확인)
```

### 6.3 데이터과학 / 추론 관련 패키지
```bash
python3 -m pip install numpy scipy pandas matplotlib scikit-learn scikit-image
python3 -m pip install onnx onnxruntime pycocotools
python3 -m pip install pycuda pybind11  # TensorRT 커스텀 레이어 개발용
python3 -m pip install Pillow tqdm requests
python3 -m pip install flask flask-cors  # 기존 bready 웹 서버 구성 재현
python3 -m pip install albumentations efficientnet segmentation-models
```

### 6.4 검증 (GPU 동작)
```bash
python3 -c "import tensorflow as tf; print(tf.__version__, tf.config.list_physical_devices('GPU'))"
# → 2.12.0 [PhysicalDevice(name='/physical_device:GPU:0', ...)]

python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"
# → 2.1.0a0... True
```

---

## 7. ROS Noetic (Ubuntu 20.04)

기존 4.6.1 환경의 ROS Melodic에 대응하는 최신 ROS1 LTS는 **Noetic**입니다.
(ROS Noetic 지원 종료: 2025-05, 그러나 Ubuntu 20.04에서 여전히 가장 광범위하게 사용)

```bash
# 저장소 추가
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update

# 데스크톱 설치
sudo apt install -y ros-noetic-desktop

# 환경설정
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc

# catkin 워크스페이스
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws && catkin_make
```

> **ROS2 (옵션)**: Ubuntu 20.04 지원 ROS2는 Foxy/Galactic (지원 종료됨). ROS2 Humble은 Ubuntu 22.04 전용이므로 이 보드에서는 설치 불가. ROS2가 필수라면 별도 L4T 커스텀 배포판 검토 필요.

---

## 8. 하드웨어/센서 라이브러리 (기존 구성 재현)

```bash
# GPIO (Jetson.GPIO) — JetPack 5에서도 동일
sudo pip3 install Jetson.GPIO
sudo groupadd -f gpio && sudo usermod -aG gpio bready
# udev 규칙 생성 후 재부팅

# Adafruit CircuitPython 센서 (Python 3.8 호환 최신 버전 사용 가능)
sudo pip3 install Adafruit-Blinka
sudo pip3 install adafruit-circuitpython-bh1750 adafruit-circuitpython-bme280
sudo pip3 install adafruit-circuitpython-ccs811 adafruit-circuitpython-mlx90614
sudo pip3 install adafruit-circuitpython-pca9685 adafruit-circuitpython-pcf8591

# 기타 하드웨어/미디어
sudo pip3 install spidev rplidar-roboticia pynput pyserial pyusb pyftdi
sudo apt install -y python3-pyaudio  # 또는 pip install PyAudio
sudo pip3 install pygame playsound

# I2C/SPI 활성화
sudo /opt/nvidia/jetson-io/config-by-pin.py --help   # jetson-io로 I2C/SPI/UART 설정
```

### 카메라 확인 (CSI 카메라 — GStreamer)
```bash
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! fakesink
```
- USB 카메라는 `v4l2sink` 사용, OpenCV `cv2.VideoCapture(0)` 동일 동작.

---

## 9. Docker / 컨테이너 (선택)

JetPack 5에는 **NVIDIA Container Runtime**이 포함되어 있어 GPU 가속 컨테이너를 바로 실행할 수 있습니다.
```bash
# docker.io 설치 (미설치 시)
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker bready

# NVIDIA L4T 컨테이너 (NGC) 사용 예
docker run --rm --runtime nvidia \
  nvcr.io/nvidia/l4t-tensorflow:r35.6.5-tf2.12-py3 \
  python3 -c "import tensorflow as tf; print(tf.__version__)"
```
> 커뮤니티 관리 이미지 모음: github.com/dusty-nv/jetson-containers

---

## 10. Jupyter Notebook 서비스 (기존 구성 재현)

기존 보드의 systemd 서비스와 동일하게 등록:
```bash
sudo tee /etc/systemd/system/jupyter_notebook.service > /dev/null << 'EOF'
[Unit]
Description=Jupyter Notebook Server

[Service]
Type=simple
User=bready
ExecStart=/bin/bash -c "source /home/bready/.profile;/usr/bin/python3 -m jupyter notebook --NotebookApp.ip='0.0.0.0' --Notebook.port=8888 --NotebookApp.open_browser=False --NotebookApp.token='' --NotebookApp.password='' /home/bready/AI_Omniwheel"

[Install]
WantedBy=multi-user.target
EOF
sudo pip3 install notebook
sudo systemctl enable --now jupyter_notebook.service
# 확인: http://192.168.1.4:8888
```

---

## 11. 기타 개발 도구 (최신 버전)

```bash
# Node.js 최신 LTS (Ubuntu 20.04, NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version    # v20.x

# CMake 최신
sudo apt install -y cmake   # 또는 pip install cmake

# gcc/g++ 9 (Ubuntu 20.04 기본) — CUDA 11.4 호환
gcc --version
```

---

## 12. 검증 체크리스트 (구축 완료 후)

```bash
# 1) JetPack/L4T
cat /etc/nv_tegra_release                  # R35 (REV 6.5)

# 2) OS/커널
cat /etc/os-release                        # Ubuntu 20.04.6
uname -r                                   # 5.10.104-tegra

# 3) CUDA
nvcc --version                             # 11.4
nvidia-smi                                 # Xavier NX 인식

# 4) cuDNN / TensorRT
dpkg -l | grep -E "cudnn|tensorrt"

# 5) 프레임워크
python3 -c "import tensorflow as tf; print(tf.__version__, tf.config.list_physical_devices('GPU'))"
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python3 -c "import cv2; print(cv2.__version__)"          # 4.5.4
python3 -c "import tensorrt; print(tensorrt.__version__)" # 8.5.2

# 6) ROS
source /opt/ros/noetic/setup.bash && roscore --version

# 7) Jupyter
curl -s http://localhost:8888 | head -1

# 8) 카메라
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! fakesink

# 9) GPIO
python3 -c "import RPi.GPIO as GPIO; print('GPIO OK')"   # Jetson.GPIO로 import
```

---

## 13. 주의사항 및 제약 (반드시 숙지)

1. **이 보드의 최종 지원 버전 = JetPack 5.1.7.** 이후(EOL) 업데이트는 없습니다. 보안 패치 수준의 지원만 지속.
2. **JetPack 4.6.1 → 5.1.7 직접 업그레이드는 불가** — QSPI 업데이트 + 재플래시 필수. 기존 데이터 백업 후 진행.
3. **Python은 3.6 → 3.8로 변경.** 기존 스크립트 중 `f-string`/문법은 대부분 호환되지만, **Python 3.6용으로 빌드된 C 확장(구버전 라이브러리)은 재빌드 필요.**
4. **TensorFlow/PyTorch는 NVIDIA 전용 wheel만 사용** (PyPI 공식 aarch64 wheel 없음). 버전이 JetPack에 묶여 있어 함부로 올리면 GPU 오류 발생.
   - TF 2.12, PyTorch 2.1이 5.1.x의 마지막 공식 wheel입니다.
5. **TensorFlow 2.13+는 Python 3.9 필요** → Ubuntu 20.04(3.8)에서는 설치 불가.
6. **ROS Melodic(18.04)은 설치 불가** → Noetic 사용. 기존 패키지 소스는 대부분 그대로 빌드됩니다.
7. **JetPack 6 이상은 절대 설치 불가** (Xavier 시리즈 미지원, 하드웨어/드라이버 차이).
8. 카메라 ISP(GStreamer `nvarguscamerasrc`)는 동일하게 동작하나, 일부 오래된 CSI 센서 드라이버는 커널 5.10에서 패치 필요할 수 있음.
9. eMMC(14GB) 파티션은 SD 루트와 별도로 포맷/마운트 설정을 다시 해야 합니다 (`/etc/fstab`).
10. 보안 권장: `bready/00000000`은 기본 자격증명이므로 실사용 시 SSH 키 인증 + 비밀번호 변경을 권장합니다.

---

## 부록 A. 참고 자료

| 자료 | 링크 |
|---|---|
| JetPack 5.1.7 공지 (NVIDIA 포럼) | forums.developer.nvidia.com/t/jetpack-5-1-7-l4t-35-6-5-is-now-live |
| JetPack SDK 5.1.7 페이지 | developer.nvidia.com/embedded/jetpack-sdk-517 |
| Jetson Linux 35.6.5 릴리스 노트 | docs.nvidia.com/jetson/archives/r35.6.5/ReleaseNotes |
| Xavier NX SD 카드 이미지 (5.1.5) | developer.nvidia.com/downloads/embedded/l4t/r35_release_v6.0/JP514-xnx-sd-card-image_b11.zip |
| QSPI 35.1 이미지 | developer.nvidia.com/embedded/L4T/r35_Release_v1.0/QSPI-img/Jetson_Xavier_NX_QSPI_35.1.gz |
| TensorFlow for Jetson 설치 문서 | docs.nvidia.com/deeplearning/frameworks/install-tf-jetson-platform |
| PyTorch for Jetson 설치 문서 | docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform |
| NVIDIA Download Center (Jetson) | developer.nvidia.com/embedded/downloads |
| jetson-containers (커뮤니티) | github.com/dusty-nv/jetson-containers |

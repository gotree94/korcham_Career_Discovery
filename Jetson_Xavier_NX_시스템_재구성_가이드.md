# NVIDIA Jetson Xavier NX 개발 환경 분석 및 시스템 재구성 가이드

> 분석 대상: `192.168.1.4` (호스트명 `bready-desktop`, 사용자 `bready`)
> 분석 일시: 2026-08-13 (SSH 원격 분석 기반)
> 목적: 동일한 시스템 구성을 새 보드(또는 초기화된 보드)에 그대로 재현하기 위한 절차

---

## 1. 시스템 요약 (분석 결과)

| 항목 | 값 |
|---|---|
| 보드 | **NVIDIA Jetson Xavier NX Developer Kit** |
| 호스트명 | `bready-desktop` |
| OS | **Ubuntu 18.04.5 LTS (Bionic Beaver)** |
| 커널 | `4.9.253-tegra` (L4T) |
| **JetPack 버전** | **4.6.1 (R32.6.1)** |
| 아키텍처 | aarch64 |
| CPU | 6 코어 |
| RAM | 7.6 GB (+ Swap 9.8 GB) |
| 저장장치 | root: microSD 59 GB (`/dev/mmcblk1p1`), eMMC 14 GB (`/dev/mmcblk0p1`, 데이터용으로 마운트됨) |
| NVIDIA L4T 패키지 | `nvidia-l4t-*` 32.6.1-20210726122859 |

### 핵심 소프트웨어 스택
| 구성요소 | 버전 |
|---|---|
| CUDA | **10.2.300** (`/usr/local/cuda-10.2`) |
| cuDNN | **8.2.1.32** (`libcudnn8`, `libcudnn8-dev`) |
| TensorRT | **8.0.1** (+ Python 바인딩 8.0.1.6) |
| OpenCV | **4.1.1** (apt 기반) |
| GStreamer | 1.14.5 |
| Python | 3.6.9 (시스템) + pip 21.3.1 |
| TensorFlow | **2.5.0+nv21.7** (NVIDIA NGC 전용 빌드) |
| NumPy / SciPy / Pandas | 1.19.4 / 1.5.4 / 1.1.5 |
| PyTorch | **미설치** |
| ROS | **Melodic** (`/opt/ros/melodic`) |
| Docker | 20.10.2 |
| Node.js / npm | v14.16.1 |
| gcc / g++ | 7.5.0 |
| CMake / Make | 3.10.2 / 4.x |
| Jupyter | Notebook (systemd 서비스로 상시 구동) |

---

## 2. 최소 하드웨어/부팅 요건

동일 구성을 재현하려면 아래가 필요합니다.
- **Jetson Xavier NX Developer Kit** (8GB 버전 권장) 또는 동일 보드
- JetPack 4.6.1 호환 **microSD 카드** (64GB 이상 권장, 대상은 59GB 루트 파티션 사용)
- USB-C 전원(19V) 및 호스트 PC (SD 이미지 작성용)
- eMMC(14GB)는 데이터용 2차 저장장치로 사용됨

> 참고: Xavier NX는 NVIDIA에서 **JetPack 4.6.x까지만** 공식 지원합니다.
> (JetPack 5.x는 Xavier NX에 지원되지 않음 — 반드시 4.6.1 사용)

---

## 3. 재구성 절차

### 3.1. JetPack 4.6.1 이미지 준비

1. NVIDIA Developer 사이트에서 JetPack 4.6.1용 Xavier NX 개발자 키트 SD 카드 이미지를 다운로드
   - 파일명 예: `Jetson_Xavier_NX_Developer_Kit_SD_Card_Image_r32.6.1.zip`
   - (일반 PC용 이미지이므로 Windows에서도 작성 가능)
2. SD 카드에 이미지 작성
   - **Windows**: Rufus 또는 balenaEtcher 사용
   - **Linux**: `sudo dd if=image.img of=/dev/sdX bs=4M status=progress`
3. SD 카드를 Xavier NX에 삽입하고 부팅
4. 첫 부팅 시 설치 마법사에서 다음 설정 수행
   - 사용자명: `bready`
   - 비밀번호: `00000000` (기존 구성과 동일하게)
   - 호스트명: `bready-desktop`
   - 로그인 자동 / 시리얼 로그인 여부는 자유

### 3.2. 기본 패키지 설치 및 저장소 구성

```bash
sudo apt update && sudo apt upgrade -y

# 기본 개발 도구
sudo apt install -y build-essential cmake git make
sudo apt install -y python3-pip python3-dev
sudo apt install -y ssh openssh-server   # SSH 서버(기본 활성화)
sudo apt install -y gpsd samba vsftpd    # 서비스용 패키지

# pip 업그레이드
python3 -m pip install --upgrade pip
```

### 3.3. NVIDIA 저장소 / CUDA · cuDNN · TensorRT (JetPack 기본 제공)

JetPack 4.6.1 이미지에는 이미 다음이 포함되어 있습니다. **버전 일치 확인**:
```bash
# 설치 후 버전 확인
cat /etc/nv_tegra_release          # R32 (REV 6.1) 확인
ls /usr/local/cuda-10.2            # CUDA 10.2
dpkg -l | grep cudnn               # libcudnn8 8.2.1.32
dpkg -l | grep tensorrt            # tensorrt 8.0.1.6

# bashrc에 CUDA 환경변수 추가 (기존 보드와 동일하게)
cat >> ~/.bashrc << 'EOF'
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1${LD_PRELOAD:+:${LD_PRELOAD}}
EOF
source ~/.bashrc
```

기존 보드의 NVIDIA apt 저장소 구성 (확인용):
```
deb file:///var/cuda-repo-l4t-10-2-local /
deb https://repo.download.nvidia.com/jetson/common r32.6 main
deb https://repo.download.nvidia.com/jetson/t194 r32.6 main
```

### 3.4. Python AI 패키지 설치

기존 보드는 **시스템 Python 3.6**에 대부분 패키지가 글로벌 설치되어 있습니다.
(가상환경 대신 시스템 전역 설치 방식 사용)

```bash
# NVIDIA TensorFlow 2.5 (JetPack 4.6 전용 빌드 - pipy 대신 NVIDIA 저장소에서)
# NVIDIA 공식 사이트에서 tensorflow-2.5.0+nv21.7-cp36-cp36m-linux_aarch64.whl 다운로드
pip3 install tensorflow-2.5.0+nv21.7-cp36-cp36m-linux_aarch64.whl

# TensorRT Python 바인딩 (apt로 설치됨)
sudo apt install -y python3-libnvinfer python3-libnvinfer-dev
pip3 install tensorrt==8.0.1.6

# 핵심 데이터과학/딥러닝 패키지 (버전은 Python 3.6 호환 버전 필수)
pip3 install numpy==1.19.4 scipy==1.5.4 pandas==1.1.5
pip3 install matplotlib==3.3.4 scikit-learn==0.24.2 scikit-image==0.17.2
pip3 install opencv-python==4.1.1.26        # 또는 JetPack OpenCV 4.1.1 사용
pip3 install onnx==1.9.0 onnxruntime==1.8.1 tf2onnx==1.9.2
pip3 install albumentations==1.0.3 efficientnet==1.0.0 segmentation-models==1.0.1
pip3 install pycuda==2019.1.2 pycocotools==2.0.2
pip3 install flask==2.0.1 flask-cors==3.0.10
pip3 install tqdm Pillow==8.3.1 requests==2.26.0
```

> 참고: Python 3.6에서 **최신 패키지 대부분이 동작하지 않음**.
> 위 버전들은 기존 보드에서 검증된 버전 목록입니다. 3.5절 전체 목록과 대조하세요.

### 3.5. 기존 보드 전체 pip 패키지 목록 (재현용 참고)

분석 결과 아래 주요 패키지가 설치되어 있었습니다 (전체 목록의 요약):

| 카테고리 | 패키지 (버전) |
|---|---|
| AI/ML | tensorflow 2.5.0+nv21.7, keras-nightly, tensorboard 2.6.0, tf-models-official 2.5.0, tensorflow-datasets 4.4.0, tensorflow-model-optimization 0.6.0, tensorflow-hub 0.12.0, tf-slim, efficientnet, image-classifiers |
| ONNX/TRT | onnx 1.9.0, onnxruntime 1.8.1, onnx-graphsurgeon, graphsurgeon 0.4.5, uff 0.6.9, tensorrt 8.0.1.6, tensorflow-addons 0.12.2 |
| 데이터과학 | numpy 1.19.4, scipy 1.5.4, pandas 1.1.5, matplotlib 3.3.4, scikit-learn 0.24.2, scikit-image 0.17.2, albumentations 1.0.3 |
| 센서/하드웨어 | Jetson.GPIO 2.0.17, Adafruit-Blinka 6.13.0, adafruit-circuitpython-bh1750/bme280/ccs811/mlx90614/pca9685/pcf8591, spidev 3.5, rplidar-roboticia 0.9.5, pynput 1.7.3, pygame 2.0.1, PyAudio 0.2.11, playsound 1.3.0, pyserial 3.5, pyusb, pyftdi |
| 웹/서버 | Flask 2.0.1, Flask-Cors 3.0.10, waitress 2.0.0, notebook 6.4.3, jupyter 5.5.5, kaggle 1.5.12, google-cloud-* |
| 기타 | pycuda 2019.1.2, pycocotools 2.0.2, PyInstaller 3.6, pafy 0.5.5, youtube_dl |

### 3.6. ROS Melodic 설치

기존 보드는 ROS **Melodic**을 jetsonhacks의 `installROSXavier` 스크립트로 설치했습니다.

```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu bionic main" > /etc/apt/sources.list.d/ros-latest.list'
wget http://packages.ros.org/ros.key -O - | sudo apt-key add -
sudo apt update

# 데스크톱 풀버전 (기존 보드: ros-melodic-rqt-gui, smach 등 포함)
sudo apt install -y ros-melodic-desktop

# ROS 환경설정
echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc

# catkin 워크스페이스
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws && catkin_make
```

### 3.7. Jupyter Notebook 서비스 등록 (상시 구동)

기존 보드의 systemd 서비스 `/etc/systemd/system/jupyter_notebook.service`:
```ini
[Unit]
Description=Jupyter Notebook Server

[Service]
Type=simple
User=bready
ExecStart=/bin/bash -c "source /home/bready/.profile;/usr/local/bin/jupyter notebook --NotebookApp.ip='0.0.0.0' --Notebook.port=8888 --NotebookApp.open_browser=False --NotebookApp.token='' --NotebookApp.password='' /home/bready/AI_Omniwheel"

[Install]
WantedBy=multi-user.target
```
재현:
```bash
sudo cp jupyter_notebook.service /etc/systemd/system/
sudo systemctl enable jupyter_notebook.service
sudo systemctl start jupyter_notebook.service
# 확인: http://192.168.1.4:8888 (토큰/비밀번호 없음)
```

### 3.8. 기타 시스템 구성

#### 환경변수 (~/.bashrc 추가분)
```bash
export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1${LD_PRELOAD:+:${LD_PRELOAD}}
```

#### 상시 서비스 목록 (기존 보드에서 실행 중)
- `ssh.service` — SSH 원격 접속
- `docker.service`, `containerd.service` — Docker
- `jupyter_notebook.service` — Jupyter (8888)
- `nvargus-daemon.service`, `nvgetty.service`, `nvphs.service` — 카메라/시리얼 (JetPack 기본)
- `gpsd.service` — GPS
- `smbd.service`, `nmbd.service` — Samba 파일 공유
- `run_autodetect.service` — 커스텀 자동감지 (`~/.bashrc` → `autodetect_syslog.bash`)
- `systemd-resolved`, `NetworkManager` 등 기본 서비스

#### eMMC 데이터 파티션 마운트
```bash
# eMMC(/dev/mmcblk0p1)를 /media/bready/<UUID>/ 로 마운트
sudo blkid
# /etc/fstab에 UUID 기반 추가
```

### 3.9. 커스텀 패키지 및 프로젝트 디렉터리 (기존 보드 기준)

기존 보드 홈 디렉터리의 주요 프로젝트 (`/home/bready/`):
| 디렉터리 | 설명 |
|---|---|
| `AI_Omniwheel` | 주 프로젝트 (Jupyter 기본 작업 디렉터리) |
| `HiBready`, `HiBready_Editor_Data` | Unity 앱 관련 |
| `catkin_ws` | ROS 워크스페이스 |
| `installROSXavier` | ROS 설치 스크립트 |
| `jupyter_example` | Jupyter 예제 |
| `project`, `src`, `startup`, `test` | 기타 개발 폴더 |
| `autodetect_syslog.bash` | 자동 감지 스크립트 |

커스텀 pip 패키지: `bready 1.1.0`, `bready-object-detection 0.1`
```bash
# 재현 시 해당 소스 디렉터리에서
pip3 install -e .
```

---

## 4. 검증 (재구성 후 체크리스트)

```bash
# 1. JetPack / L4T 버전
cat /etc/nv_tegra_release              # R32 REV 6.1 기대

# 2. CUDA
ls /usr/local/cuda-10.2 && nvcc --version   # 10.2.300 기대

# 3. cuDNN / TensorRT
dpkg -l | grep -E "cudnn|tensorrt"     # 8.2.1.32 / 8.0.1

# 4. TensorFlow GPU 동작 확인
python3 -c "import tensorflow as tf; print(tf.__version__, tf.test.is_gpu_available())"
# 기대: 2.5.0 True

# 5. OpenCV
python3 -c "import cv2; print(cv2.__version__)"   # 4.1.1

# 6. ROS
source /opt/ros/melodic/setup.bash && roscore --version

# 7. Jupyter
curl -s http://localhost:8888 | head -1   # 응답 확인

# 8. 카메라 (JetPack 테스트)
gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM),width=1280,height=720' ! fakesink
```

---

## 5. 주의사항 / 제약

1. **JetPack 5.x는 Xavier NX 미지원** → 반드시 JetPack 4.6.1 이미지 사용
2. Python 3.6 제약 → 일부 최신 패키지는 호환 불가, 위 목록의 검증 버전 사용
3. `nvcc`는 `/usr/local/cuda/bin`이 PATH에 있어야 동작 (`.bashrc` 설정 필수)
4. TensorFlow는 **NVIDIA NGC 전용 aarch64 빌드**를 사용해야 함 (pipy의 x86 바이너리 불가)
5. PyTorch는 기존 보드에 미설치 상태 — 필요 시 NVIDIA JetPack 4.6용 torch 1.x wheel 별도 설치
6. 비밀번호(00000000) 및 SSH 접속 보안은 실사용 환경에 맞춰 변경 권장

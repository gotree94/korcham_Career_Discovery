# Jetson Xavier NX ROS2 사용 가이드

> 작성일: 2026-08-13
> 대상: **NVIDIA Jetson Xavier NX** (JetPack 5.1.7 / L4T 35.6.5 / Ubuntu 20.04)
> 전제: ROS1 **Noetic이 네이티브로 설치되어 있음** (별도의 ROS1 환경과 분리해 ROS2를 사용하는 방법)
> 목표: ROS2를 독립적으로 구동하고, 필요 시 ROS1과 통신(브리지)까지 구성

---

## 1. ROS2 배포판 선택 (이 보드에서의 제약)

| ROS2 배포판 | Ubuntu 20.04 공식 지원 | 지원 상태 (2026년) | 이 보드 사용 가능 여부 |
|---|---|---|---|
| Foxy | O (공식 apt) | **EOL (2023-05 종료)** | 네이티브 가능 (비권장) |
| Galactic | O (공식 apt) | **EOL (2022-11 종료)** | 네이티브 가능 (비권장) |
| Humble | X (Ubuntu 22.04 전용) | 지원 중 (2027-05까지) | **Docker 컨테이너로 사용** |
| Jazzy+ | X (Ubuntu 24.04 전용) | 지원 중 | Docker 컨테이너로 사용 가능 |

> **결론**: 지원 중인 ROS2(Humble 이상)를 이 보드에서 쓰려면 **Docker 컨테이너 방식이 사실상 유일한 공식적 경로**입니다.
> JetPack 5.x(Ubuntu 20.04)는 ROS2 Foxy/Galactic까지만 네이티브 apt 설치가 가능하며, 둘 다 EOL입니다.

### 방법 비교 요약

| 방법 | ROS2 버전 | GPU 가속 | 난이도 | 비고 |
|---|---|---|---|---|
| **① docker + dusty-nv (권장)** | Humble/Iron | ✅ (L4T 기반) | 쉬움 | JetPack/L4T 최적화, NVIDIA 커뮤니티 표준 |
| ② docker + 공식 osrf/ros | Humble | ❌ (ROS 자체는 GPU 불필요) | 쉬움 | 순수 ROS2 개발용, L4T 스택 없음 |
| ③ 네이티브 apt (Foxy/Galactic) | Foxy | ✅ | 보통 | EOL, 그래도 가장 단순한 "네이티브" |
| ④ Isaac ROS 미러 | Humble | ✅ | 중간 | NVIDIA 제공, 설치 JetPack 버전 정합성 필요 |
| ⑤ RoboStack (conda) | 최신 | △ | 중간 | Python 환경 제어가 까다로움 |

---

## 2. 공통 준비: Docker 설치 및 GPU 지원 확인

방법 ①②에서 사용. (JetPack 5에는 NVIDIA Container Runtime이 기본 포함)

```bash
# docker.io 설치 (없으면)
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER   # 현재 사용자에 docker 권한 부여 (재로그인 필요)

# GPU 런타임 확인
sudo docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-base:r35.4.1 \
  nvidia-smi   # → Jetson Xavier NX 인식되면 OK
```

---

## 3. 방법 ① (권장) docker + dusty-nv/jetson-containers — GPU 가속 ROS2 Humble

[`dusty-nv/jetson-containers`](https://github.com/dusty-nv/jetson-containers)는 JetPack/L4T에 최적화된 ROS2 컨테이너 이미지를 제공합니다.
- 지원: `foxy`, `galactic`, `humble`, `iron` (ROS2) + `noetic`, `melodic` (ROS1)
- JetPack 5(Ubuntu 20.04)에서 Humble은 **소스 빌드로 제공** → GPU(CUDA/cuDNN/TensorRT/OpenCV) 사용 가능
- 사용 중인 L4T 버전(r35.6.5)에 맞는 이미지를 자동 선택/빌드하는 `autotag` 지원

### 3.1. jetson-containers 도구 설치

```bash
git clone https://github.com/dusty-nv/jetson-containers
cd jetson-containers
bash install.sh
# 로그아웃/재로그인 후 명령 사용 가능
```

### 3.2. ROS2 Humble 컨테이너 실행

```bash
# 가장 간단한 방법: 호환 이미지 자동 선택(또는 빌드) 후 실행
jetson-containers run $( autotag ros:humble-ros-base )

# 이미지 확인
docker images | grep dustynv/ros

# 수동 실행 (이미지 태그 확인 후)
docker run --runtime nvidia -it --rm --network=host \
  dustynv/ros:humble-ros-base-l4t-r35.4.1
```

> `autotag`이 r35.6.5에 정확히 일치하는 프리빌드가 없으면 가장 가까운 r35.x 이미지를 쓰거나 직접 빌드합니다.
> 빌드가 필요한 경우: `jetson-containers build ros:humble-ros-base` (시간 소요, swap 확보 권장)

### 3.3. 컨테이너 내부에서 ROS2 동작 확인

```bash
# 컨테이너 bash에서
source /opt/ros/humble/setup.bash
ros2 --version                    # ros2 core packages

# talker/listener 데모 (터미널 2개)
ros2 run demo_nodes_cpp talker    # 터미널 1
ros2 run demo_nodes_cpp listener  # 터미널 2

# 토픽 확인
ros2 topic list
ros2 topic echo /chatter
```

### 3.4. 호스트 작업공간 마운트 (코드 개발)

```bash
# 호스트의 ~/ros2_ws를 컨테이너에 공유
mkdir -p ~/ros2_ws/src

docker run --runtime nvidia -it --rm --network=host \
  -v ~/ros2_ws:/home/ros2_ws \
  -v /home/bready/catkin_ws:/home/catkin_ws \
  dustynv/ros:humble-ros-base-l4t-r35.4.1

# 컨테이너에서 colcon 빌드
cd /home/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### 3.5. 컨테이너 자동 시작 (서비스 등록, 선택)

`~/.config/systemd/user/ros2-humble.service`:
```ini
[Unit]
Description=ROS2 Humble Container (Jetson)

[Service]
Type=simple
ExecStart=/usr/bin/docker run --rm --name ros2_humble --runtime nvidia -it --network=host -v /home/bready/ros2_ws:/home/ros2_ws dustynv/ros:humble-ros-base-l4t-r35.4.1
Restart=always

[Install]
WantedBy=default.target
```
```bash
systemctl --user daemon-reload
systemctl --user enable --now ros2-humble.service
```

---

## 4. 방법 ② docker + 공식 osrf/ros — GPU 불필요한 순수 ROS2

ROS2 코어/노드는 GPU가 필요 없으므로, L4T 최적화가 필요 없는 일반 개발에 유용합니다.
공식 이미지의 arm64 버전을 사용합니다.

```bash
# arm64 전용 이미지 (desktop은 amd64 전용인 경우가 많음 → ros-base 사용)
docker pull osrf/ros:humble-ros-base

docker run -it --rm --network=host \
  -v ~/ros2_ws:/home/ros2_ws \
  osrf/ros:humble-ros-base
```

> 주의: 이 이미지는 Ubuntu 22.04 기반이므로 GPU(CUDA) 가속은 `--runtime nvidia`로도 동작하지 않습니다.
> GPU 컴퓨팅이 필요한 노드가 있으면 반드시 **방법 ①**을 사용하세요.

---

## 5. 방법 ③ 네이티브 설치 — ROS2 Foxy (EOL, 가장 단순)

ROS1 Noetic과 **같은 시스템에 나란히** 설치됩니다. (EOL이므로 신규 권장은 아님)

```bash
# 5.1. ROS2 저장소 추가
sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update

# 5.2. 설치 (데스크톱 또는 베이스)
sudo apt install -y ros-foxy-desktop
# 또는 최소: sudo apt install -y ros-foxy-ros-base

# 5.3. 환경별 활성화 (각 셸에서 선택)
source /opt/ros/foxy/setup.bash    # ROS2 사용 시
source /opt/ros/noetic/setup.bash  # ROS1 사용 시
# → 두 개를 동시에 source 하면 충돌하므로 셸마다 하나씩!

# 5.4. 예제
source /opt/ros/foxy/setup.bash
ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_cpp listener
```

> 팁: 셸에서 간편하게 전환하려면 `~/.bashrc` 대신 alias 사용
> `alias ros1='source /opt/ros/noetic/setup.bash'`
> `alias ros2='source /opt/ros/foxy/setup.bash'`

---

## 6. 방법 ④ NVIDIA Isaac ROS 미러 (Humble, JP 5.1.x)

NVIDIA가 JetPack 5.x를 위해 제공하는 ROS2 Humble 미러 저장소입니다.
- **요구사항 정합성 주의**: Isaac ROS 2.1은 **JetPack 5.1.2 / L4T 35.4.1** 기준으로 빌드됨 (우리 보드는 5.1.7/L4T 35.6.5 — 일반적으로 하위 호환되어 동작하지만 패키지별 확인 필요)
- GPU 최적화 CV/AI 패키지(Isaac ROS, NITROS 등)를 함께 쓰려면 이 경로가 유리

```bash
# 공식 문서의 현재 절차를 따르세요 (URL이 버전에 따라 변경됨)
# https://nvidia-isaac-ros.github.io/getting_started/isaac_apt_repository.html

sudo apt install -y curl gnupg
curl https://nvidia-isaac-ros.github.io/repos/repo.key | sudo apt-key add -
# 또는 (신버전)
sudo curl -sSL https://nvidia-isaac-ros.github.io/repos/repo.key \
  -o /usr/share/keyrings/isaac_ros-keyring.gpg

echo "deb https://isaac.download.nvidia.com/isaac-ros/... $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/isaac_ros.list

sudo apt update
sudo apt install -y ros-humble-ros-base  # NVIDIA 빌드 Humble
```
> ⚠️ 저장소 URL과 패키지명은 Isaac ROS 릴리스마다 다릅니다. **반드시 공식 getting-started 페이지의 현재 값을 사용**하세요 (위 URL은 예시).

---

## 7. 방법 ⑤ RoboStack (conda 기반) — 최신 ROS2

Conda/mamba 환경에서 ROS2 전체를 관리하는 대안. Python 환경을 자유롭게 제어할 수 있습니다.
```bash
# miniforge/mamba 설치 후
conda create -n ros2_humble -c conda-forge -c robostack-staging ros-humble-desktop python=3.10
conda activate ros2_humble
```
- 공식 ROS2 apt(22.04 전용)를 우회하므로 이 보드에서도 최신 배포판을 쓸 수 있음.
- 다만 Python 바인딩과 시스템(CUDA) 연동이 번거로울 수 있어, GPU 컴퓨팅 중심 작업에는 방법 ①이 더 유리.

---

## 8. ROS1 Noetic ↔ ROS2 브리지 (ros1_bridge)

ROS1(Noetic)과 ROS2가 **분리된 환경**에 있으면, 통신이 필요할 때 브리지를 둡니다.

### 8.1. 둘 다 네이티브일 때 (ROS1 + ROS2 Foxy)

```bash
sudo apt install -y ros-foxy-ros1-bridge

# ROS1과 ROS2를 같은 셸에서 활성화 (순서 중요: ROS1 먼저, ROS2 나중)
source /opt/ros/noetic/setup.bash
source /opt/ros/foxy/setup.bash

ros2 run ros1_bridge dynamic_bridge
# → 양쪽의 같은 토픽이 자동 연결됨
```

### 8.2. ROS1 네이티브 + ROS2 컨테이너일 때 (권장 구성)

컨테이너 ROS2가 호스트 ROS1과 통신하려면 **컨테이너 안에도 ROS1을 함께 설치**하고 브리지를 실행합니다.

```bash
# dusty-nv 컨테이너에서 (방법 ①의 컨테이너 bash)
# ROS1 Noetic 설치 (컨테이너 내부, focal)
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update
sudo apt install -y ros-noetic-ros-base

# 브리지 빌드
mkdir -p ~/bridge_ws/src && cd ~/bridge_ws/src
git clone -b humble https://github.com/ros2/ros1_bridge.git
cd ~/bridge_ws
source /opt/ros/noetic/setup.bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install

# 실행 (네트워크=host + ROS_MASTER_URI 공유)
source install/setup.bash
ros2 run ros1_bridge dynamic_bridge
```

> 통신 조건:
> - 컨테이너는 `--network=host`로 실행해야 호스트 ROS1과 `ROS_MASTER_URI`/DDS 도메인을 공유합니다.
> - ROS1은 `ROS_MASTER_URI=http://localhost:11311`, ROS2는 DDS 도메인 ID가 같아야 함 (`export ROS_DOMAIN_ID=0`).

---

## 9. 주의사항 및 운영 팁

1. **도메인 ID**: ROS1·ROS2가 한 네트워크에 여러 대 있으면 `export ROS_DOMAIN_ID=<0~101>`로 격리하세요.
2. **`--network=host`**: 컨테이너 ROS2 노드가 호스트/외부와 통신하려면 필수. (다른 컨테이너와 별개 동작도 가능)
3. **swap**: Humble을 소스 빌드할 때 8GB RAM으론 부족할 수 있음 → `installSwapfile`로 swap 8~10GB 확보 권장.
4. **저장 공간**: 이미지 크기가 큼 (humble-ros-base ~5GB). eMMC(14GB) 여유 확인.
5. **JetPack 버전 정합성**: 컨테이너 이미지는 특정 L4T 기준으로 빌드됨. `autotag`/`dustynv` 태그의 `r35.x`가 호스트 L4T(35.6.5)와 **같거나 이전**이어야 합니다.
6. **EOL 주의**: 네이티브 Foxy는 이미 EOL — 보안/호환 이슈에 대응하려면 컨테이너(Humble) 사용을 권장.
7. **Isaac ROS**: 특정 JetPack 소수 버전에 고정된 패키지가 많으므로, 사용 전 지원 매트릭스 확인 필수.

---

## 10. 검증 체크리스트

```bash
# 1. Docker + NVIDIA 런타임
docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-base:r35.4.1 nvidia-smi

# 2. ROS2 (컨테이너 또는 네이티브)
ros2 --version
ros2 run demo_nodes_cpp talker & ros2 run demo_nodes_cpp listener
ros2 topic list | grep chatter

# 3. GPU 연동 (방법 ① 컨테이너)
python3 -c "import torch; print(torch.cuda.is_available())"   # True 기대 (torch 포함 이미지 시)

# 4. 브리지 (ROS1 ↔ ROS2)
rostopic list        # ROS1 터미널
ros2 topic list      # ROS2 터미널 — 동일한 /chatter 확인
```

---

## 부록 A. 참고 자료

| 자료 | 링크 |
|---|---|
| jetson-containers (NVIDIA 공식 계열 커뮤니티) | github.com/dusty-nv/jetson-containers |
| dustynv/ros 이미지 목록 | hub.docker.com/r/dustynv/ros |
| 공식 ROS2 Docker 이미지 | hub.docker.com/r/osrf/ros |
| ROS2 Humble 설치 문서 (Ubuntu 22.04) | docs.ros.org/en/humble/Installation.html |
| Isaac ROS 시작하기 / apt 저장소 | nvidia-isaac-ros.github.io/getting_started/isaac_apt_repository.html |
| ROS1↔ROS2 브리지 | github.com/ros2/ros1_bridge |
| RoboStack | github.com/RoboStack/ros-humble |

---

## 11. 이 보드(구형 하드웨어)에서 최신 업데이트 + ROS2가 실제로 가치가 있는가? (판단 가이드)

> "예전 하드웨어(Xavier NX)를 쓰는 입장에서, 최신 버전 업데이트와 ROS2 사용이
> 속도나 활용도의 증가에 도움이 될까?"에 대한 정리입니다.
> **결론 먼저**: *속도 향상* 목적이라면 효과가 적고, *활용도(생태계/호환성)* 목적이라면 효과가 있습니다.
> 다만 이 보드가 EOL(EOL 임박)이라는 점을 고려한 신중한 판단이 필요합니다.

### 11.1. 최신 버전 업데이트 (JetPack 5.1.7) — 속도 vs 활용도

| 항목 | 영향 | 평가 |
|---|---|---|
| CPU/GPU 성능 | 하드웨어 동일 → **원천 성능 변화 없음** | ❌ 기대 효과 낮음 |
| TensorRT 8.0 → 8.5 | 일부 모델(Transformer 계열) 추론 몇 % 향상, DLA 활용 개선 | ⚠️ 모델별 편차 큼 |
| CUDA 10.2 → 11.4 | 동일 GPU에서 성능 증가는 미미, 신규 라이브러리 호환성 확보 | ⚠️ 제한적 |
| PyTorch 2.1 사용 가능 | 기존엔 **설치 자체 불가** → 최신 AI 모델/학습 코드 구동 가능 | ✅ **가장 큰 실익** |
| Python 3.6 → 3.8 | 미미한 성능 향상 + 최신 pip 패키지 호환 폭 확대 | ⚠️ 제한적 |
| Ubuntu 20.04 / 커널 5.10 | 신규 드라이버·보안 패치·시스템 안정성 | ✅ 보안/유지보수 측면 |
| 비용 | 재플래시 + 전체 환경 재구축 + 카메라/GPIO/기존 코드 재검증 | ⚠️ 리스크·시간 큼 |

### 11.2. ROS2 사용 — 속도 vs 활용도

- **속도 측면: 사실상 무의미**
  - ROS2는 ROS1보다 **빠르지 않습니다.** 오히려 DDS 디스커버리로 시작 오버헤드가 더 큽니다.
  - 단일 로봇·로컬 통신에서는 ROS1이 더 가볍고 단순합니다.
  - ROS2의 장점은 성능이 아니라 **아키텍처**(실시간 QoS, 멀티로봇, zero-copy, 현대적 도구/보안)입니다.
- **활용도 측면: 가치 있음 (조건부)**
  - 신규 패키지(Isaac ROS, 최신 Nav2 등)는 ROS2 전용으로만 배포됩니다.
  - ROS1 Noetic이 EOL(2025-05)이므로 **신규 생태계 확장이 막혀 있습니다.**
  - 단, 이 보드도 EOL이 가까워 ROS2의 "미래 지향적" 가치를 충분히 누리기엔 남은 수명이 짧습니다.

### 11.3. 상황별 권장안 (요약)

| 상황 | 권장 |
|---|---|
| 기존 ROS1 시스템이 잘 동작 중 | **업데이트만 하고 ROS2 마이그레이션 불필요** |
| PyTorch / 최신 AI 모델이 필요 | JetPack 5.1.7로 업데이트 (실익 큼) |
| 신규 ROS2 패키지가 꼭 필요 | 컨테이너로 ROS2 Humble만 분리 사용 (본 문서 3장 절차) |
| 순수한 성능 향상만 기대 | 업데이트 불필요 — 하드웨어 한계가 병목 |

### 11.4. 최종 요점

> 이 보드는 이미 성능의 한계에 도달한 하드웨어입니다.
> **성능**을 원한다면 소프트웨어 업데이트가 아니라 보드 교체(Orin NX/Nano)가 유일한 해법입니다.
> 소프트웨어 업데이트와 ROS2는 "더 빨라지게"가 아니라 **"할 수 있는 것의 폭"을 넓혀줍니다.**
> 예산과 리소스가 한정되어 있다면, 현재 잘 돌아가는 ROS1 Noetic 시스템을 유지하면서
> 필요한 새 기능만 컨테이너(ROS2)로 얹는 구조가 **비용 대비 최적**입니다.

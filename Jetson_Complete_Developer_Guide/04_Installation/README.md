# 04. Installation & Setup

## 1. SDK Manager

NVIDIA SDK Manager는 Jetson 보드에 OS를 플래싱하고 JetPack을 설치하는 공식 도구입니다.

### 설치 (Host PC 필요)

```bash
# Host PC (Ubuntu x86_64)에서
wget https://developer.download.nvidia.com/sdkmanager/SDKManager.deb
sudo dpkg -i SDKManager.deb
sudo apt --fix-broken install
```

### 플래싱 절차

```
1. Jetson 보드를 Recovery Mode로 진입
2. USB 케이블로 Host PC와 연결
3. SDK Manager 실행
4. 대상 보드 선택 (Jetson Xavier NX)
5. JetPack 버전 선택 (4.6 / 5.x / 6.x)
6. Flash + Install 진행 (약 30~60분 소요)
```

---

## 2. Recovery Mode

### 강제 복구 모드 진입

```bash
# Developer Kit 기준
1. 전원 차단
2. J40 (FORCE_RECOVERY) 핀 쇼트
3. 전원 연결
4. USB-C (데이터 포트)를 Host PC와 연결
5. Host PC에서 확인
lsusb  # NVIDIA Corp. APX 항목 확인
```

### 복구 모드 확인

```bash
# Host PC에서
lsusb | grep NVIDIA
# → NVIDIA Corp. APX (복구 모드 정상)

# 또는
sudo dmesg | grep -i nvidia
```

---

## 3. SD 카드 이미지 플래싱 (간편 방법)

SD 카드 이미지는 NVIDIA 공식 사이트에서 다운로드 가능합니다.

### 다운로드

| JetPack | 다운로드 링크 |
|:-------:|:------------:|
| 4.6.1 | https://developer.nvidia.com/jetpack-461-archive |
| 5.1.3 | https://developer.nvidia.com/jetpack-sdk-513 |
| 6.1 | https://developer.nvidia.com/jetpack-sdk-61 |

### 플래싱 방법

#### Linux/macOS (dd)
```bash
# SD 카드 장치 확인
lsblk  # /dev/sdX 또는 /dev/mmcblkX

# 이미지 플래싱 (약 10~20분)
sudo dd if=jetson_xavier_nx_jp46.img of=/dev/sdX bs=4M status=progress
sync
```

#### Windows (balenaEtcher)
```
1. balenaEtcher 다운로드 및 실행
2. 이미지 파일 선택
3. SD 카드 선택
4. Flash! 클릭 (약 10~20분)
```

#### Windows (Win32 Disk Imager)
```
1. Win32 Disk Imager 실행
2. 이미지 파일 선택
3. SD 카드 드라이브 선택
4. Write 클릭
```

---

## 4. 초기 설정 (First Boot)

### 부팅 후 기본 설정

```bash
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 사용자 계정 기본
# username: jetson / password: jetson (변경 권장)

# 3. Hostname 변경
sudo hostnamectl set-hostname my-jetson

# 4. SSH 활성화
sudo systemctl enable ssh
sudo systemctl start ssh

# 5. 전력 모드 설정 (20W MAXN)
sudo nvpmodel -m 0
sudo jetson_clocks

# 6. Swap 파일 (RAM 부족 대비)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 5. 네트워크 설정

### Wi-Fi (M.2 Key E 슬롯에 Wi-Fi 모듈 필요)

```bash
# Wi-Fi 목록
nmcli dev wifi list

# Wi-Fi 연결
nmcli dev wifi connect "SSID" password "PASSWORD"

# 고정 IP 설정
sudo nano /etc/netplan/01-netcfg.yaml
```

```yaml
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
sudo netplan apply
```

### USB 테더링 (스마트폰)

```bash
# 안드로이드: USB 테더링 활성화
# iOS: 개인용 핫스팟 → USB 전용

# 연결 확인
ip a  # usb0 또는 eth1 확인
```

---

## 6. 원격 접속

### SSH 접속

```bash
# Host PC에서
ssh jetson@192.168.1.100  # Jetson IP 주소
```

### VNC (그래픽 환경)

```bash
# Jetson에서 VNC 서버 설치
sudo apt install vino
gsettings set org.gnome.Vino require-encryption false

# VNC 클라이언트에서 접속
# 192.168.1.100:5900
```

### Jupyter Lab

```bash
pip3 install jupyterlab
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# Host PC 브라우저에서
# http://192.168.1.100:8888
```

---

## 7. 개발 환경 검증

```bash
# 모든 구성 요소가 정상 설치되었는지 확인
cat /etc/nv_tegra_release
nvcc --version
python3 -c "import tensorrt; print('TensorRT:', tensorrt.__version__)"
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"
python3 -c "import torch; print('PyTorch:', torch.__version__)"
python3 -c "import Jetson.GPIO; print('GPIO: OK')"
```

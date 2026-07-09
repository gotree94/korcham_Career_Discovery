# 21. Troubleshooting

## 1. 부팅 문제

### 보드가 켜지지 않음

| 증상 | 원인 | 해결 |
|:----|:-----|:-----|
| 전원 LED 안켜짐 | 전원 부족/불량 | 5V/4A 이상 어댑터 확인, USB-C PD 45W 권장 |
| 부팅 중 멈춤 | SD 카드 불량 | 다른 SD 카드로 테스트 |
| 화면 안나옴 | HDMI 케이블 | HDMI 2.0 케이블 사용, DisplayPort 시도 |

### 복구 모드

```bash
# 복구 모드 진입 (Developer Kit)
1. 전원 차단
2. FORCE_RECOVERY 핀 (J40) 쇼트
3. 전원 연결
4. USB-C → Host PC 연결
5. Host PC에서 확인:
   lsusb | grep NVIDIA
   # → "NVIDIA Corp. APX" 확인
```

---

## 2. 카메라 문제

### CSI 카메라

| 증상 | 원인 | 해결 |
|:----|:-----|:------|
| **/dev/video0 없음** | 케이블 방향/연결 | 리본 케이블 반대 방향 시도 (금속 핀이 안쪽) |
| **검은 화면** | 잘못된 sensor-id | `sensor-id=0` → `sensor-id=1` 변경 |
| **낮은 FPS** | 전력 부족 | 15W/20W 모드로 전환 |
| **이미지 깨짐** | 케이블 길이/간섭 | 15cm 이하 케이블, EMI 차폐 |
| **해상도 오류** | 센서 모드 불일치 | IMX219: 3264x2464@21fps, 1920x1080@30fps |

### USB 카메라

```bash
# USB 카메라 확인
lsusb
v4l2-ctl --list-devices

# 권한 문제
sudo chmod 666 /dev/video1

# udev 규칙 영구 적용
echo 'SUBSYSTEM=="video4linux", MODE="0666"' | \
    sudo tee /etc/udev/rules.d/99-camera.rules
```

---

## 3. GPIO 문제

### GPIO 핀 동작 안함

| 증상 | 원인 | 해결 |
|:----|:-----|:------|
| LED 안켜짐 | 잘못된 핀 번호 | 핀맵 확인, BCM/BOARD 모드 확인 |
| 버튼 입력 안됨 | PULL 설정 | `pull_up_down=GPIO.PUD_DOWN/UP` 설정 |
| PWM 미동작 | 비활성 핀 | 다른 PWM 핀으로 변경 |
| Permission 오류 | 권한 없음 | `sudo` 실행 또는 `gpio` 그룹 추가 |

```bash
# GPIO 권한 설정
sudo usermod -aG gpio $USER
# 로그아웃 후 재로그인

# GPIO 핀 상태 확인
sudo cat /sys/kernel/debug/gpio | grep GPIO
```

---

## 4. 전력 문제

### 전력 부족 증상

```
- USB 장치 인식 불안정
- 카메라 FPS 저하
- GPU 클럭 강제 저하
- 갑작스러운 셧다운
- Wi-Fi/블루투스 연결 끊김
```

### 전력 확인

```bash
# 현재 전력 소비
sudo tegrastats | grep VDD_IN

# 전력 모드 확인
sudo nvpmodel -q

# 20W MAXN 모드 (최대 성능)
sudo nvpmodel -m 0
sudo jetson_clocks
```

| 상황 | 권장 전원 |
|:----|:---------|
| 기본 부팅/데스크탑 | 5V/3A (15W) |
| AI 추론 + 카메라 | 5V/4A (20W) |
| USB 3.0 장치 다수 | 5V/5A (25W) 이상 |
| NVMe SSD + AI + 카메라 | 5V/5A 이상 |

---

## 5. CUDA/TensorRT 문제

### CUDA 에러

| 에러 | 원인 | 해결 |
|:----|:-----|:------|
| `cudaErrorNoDevice` | CUDA 미설치 | `nvcc --version` 확인 |
| `cudaErrorOutOfMemory` | GPU 메모리 부족 | 배치 크기/해상도 축소 |
| `cudaErrorInvalidValue` | 잘못된 커널 인자 | 입력 shape 확인 |
| `unspecified launch failure` | 커널 오류 | `cudaGetLastError()`로 확인 |

### TensorRT 변환 실패

```bash
# 로그 수준 높여서 재시도
trtexec --onnx=model.onnx --saveEngine=model.engine \
        --verbose --fp16

# workspace 메모리 증가
trtexec --onnx=model.onnx --saveEngine=model.engine \
        --workspace=2048 --fp16
```

---

## 6. ROS 문제

### ROS1 Melodic

| 증상 | 원인 | 해결 |
|:----|:-----|:------|
| `command not found: roslaunch` | setup.bash 미실행 | `source /opt/ros/melodic/setup.bash` |
| `Unable to contact master` | roscore 미실행 | `roscore &` 실행 |
| `[WARN] topic not found` | 노드명/토픽명 오타 | `rostopic list`로 확인 |

### ROS2 (JetPack 6.x 환경)

```bash
# ROS2 환경
source /opt/ros/humble/setup.bash

# 문제 해결
ros2 doctor
sudo sysctl -w net.core.rmem_max=26214400  # DDS 통신 버퍼
```

---

## 7. SD 카드/저장소 문제

### SD 카드 성능 저하

```bash
# 쓰기 속도 테스트
sudo dd if=/dev/zero of=~/test bs=1M count=100 conv=fdatasync

# 읽기 속도 테스트
sudo hdparm -t /dev/mmcblk0

# 성능 기준 (UHS-I U3)
# 읽기: 80MB/s 이상
# 쓰기: 30MB/s 이상
```

### SD 카드 수명 관리

```bash
# 로그를 메모리에 기록 (SD 카드 쓰기 감소)
sudo apt install ramlog

# SWAP 사용 최소화
sudo swapoff -a

# 저널링 최소화 (ext4)
sudo tune2fs -O ^has_journal /dev/mmcblk0p1
```

### SD 카드 이미지 백업

```bash
# SD 카드 → 이미지 파일 백업 (Host PC)
sudo dd if=/dev/sdX of=jetson_backup.img bs=4M status=progress

# 압축 백업
sudo dd if=/dev/sdX bs=4M | gzip > jetson_backup.img.gz
```

---

## 8. 네트워크 문제

### Wi-Fi

```bash
# Wi-Fi 목록
nmcli dev wifi list

# Wi-Fi 연결
nmcli dev wifi connect "SSID" password "PASSWORD"

# 연결 문제 시: NetworkManager 재시작
sudo systemctl restart NetworkManager
```

### SSH

```bash
# SSH 연결 안될 때
# 1. SSH 서비스 확인
sudo systemctl status ssh

# 2. 방화벽 확인
sudo ufw status

# 3. IP 주소 확인
ip addr show | grep inet

# 4. SSH 디버그
ssh -vvv jetson@192.168.1.100
```

---

## 9. 시스템 리셋

### 소프트 리셋

```bash
sudo reboot
```

### 하드 리셋 (전원 재연결)

```bash
# 모든 전원 분리 → 10초 대기 → 재연결
# SD 카드도 분리 후 재삽입
```

### 공장 초기화

```bash
# SD 카드를 다시 플래싱 (04_Installation 참조)
# 또는 NVIDIA SDK Manager로 재설치
```

---

## 10. 자주 묻는 질문 (FAQ)

| 질문 | 답변 |
|:----|:------|
| **Jetson 전원 LED는 켜지는데 화면이 안 나와요** | HDMI 케이블 확인, DisplayPort 시도, USB-C DP 모니터 직접 연결 |
| **CUDA가 10.2인데 최신 버전을 쓸 수 있나요?** | JetPack 6.x 업그레이드 필요 (SD 카드 재설치) |
| **ROS2 Humble을 설치하고 싶어요** | JetPack 4.6(Ubuntu 18.04)에서는 불가. JetPack 6.x로 업그레이드 필요 |
| **CSI 카메라가 인식이 안 돼요** | `sensor-id=0/1` 변경, 케이블 방향 확인, `i2cdetect -y -r 7`로 주소 확인 |
| **AI 모델 추론 속도가 너무 느려요** | TensorRT 변환, FP16/INT8 양자화, NVDLA 사용, `jetson_clocks` 실행 |
| **SD 카드 용량이 부족해요** | NVMe SSD를 M.2 슬롯에 추가, 큰 파일은 SSD로 이동 |
| **Jetson이 너무 뜨거워요** | 방열판+팬 확인, 15W 모드 사용, 실내 온도 30°C 이하 |
| **Python 3.6 말고 3.8/3.10을 쓰고 싶어요** | JetPack 5.x(3.8) 또는 JetPack 6.x(3.10)로 업그레이드 |

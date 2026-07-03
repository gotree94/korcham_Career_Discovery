# 09. Camera on Jetson

## 1. 카메라 인터페이스 개요

Jetson Xavier NX는 3가지 방식의 카메라를 지원합니다.

| 방식 | 인터페이스 | 지연시간 | 화질 | 사용 난이도 |
|:----:|:---------:|:-------:|:----:|:----------:|
| CSI | MIPI CSI-2 | 낮음 | 우수 | 중간 |
| USB | USB 3.0 | 중간 | 보통 | 쉬움 |
| RTSP | 네트워크 | 높음 | 다양 | 쉬움 |

---

## 2. CSI Camera

### 지원 CSI 카메라

| 모델 | 해상도 | FPS | 인터페이스 | 특징 |
|:----:|:------:|:---:|:---------:|------|
| **IMX219** | 3280x2464 | 30/15 | 2-lane | 라즈베리파이 카메라 v2, 저렴 |
| **IMX477** | 4056x3040 | 30/15 | 2-lane | 라즈베리파이 HQ 카메라, 고화질 |
| IMX290 | 1920x1080 | 60 | 2-lane | 저조도 우수 |
| OV9281 | 1280x800 | 120 | 2-lane | 고속 촬영 |

### CSI 연결 (Xavier NX)

```
Jetson Xavier NX CSI Connector:
  ┌──────────────────────────────┐
  │  15  13  11   9   7   5   3  1 │
  │                               │
  │  16  14  12  10   8   6   4  2 │
  └──────────────────────────────┘

  Lane 0~1: IMX219 (카메라 1)
  Lane 2~3: IMX219 (카메라 2) — 듀얼 카메라 지원
```

### 카메라 연결 확인

```bash
# CSI 카메라 장치 확인
ls /dev/video*

# I2C 주소 확인 (카메라 통신)
sudo i2cdetect -y -r 7  # CSI 카메라 I2C 버스

# 카메라 목록
v4l2-ctl --list-devices
```

### GStreamer 파이프라인

```bash
# CSI 카메라 실시간 보기 (터미널)
gst-launch-1.0 nvarguscamerasrc ! \
    'video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1' ! \
    nvvidconv ! 'video/x-raw, format=BGRx' ! \
    nvvidconv ! 'video/x-raw, format=I420' ! \
    xvimagesink

# fps 디스플레이 포함
gst-launch-1.0 nvarguscamerasrc ! \
    'video/x-raw(memory:NVMM), width=1920, height=1080' ! \
    nvvidconv ! 'video/x-raw, format=BGRx' ! \
    videorate ! 'video/x-raw, framerate=30/1' ! \
    fpsdisplaysink video-sink=xvimagesink text-overlay=true
```

### CSI 카메라 해상도 vs FPS 표

| 모드 | 해상도 | FPS | 화각 |
|:----:|:------:|:---:|:----:|
| 0 | 3264x2464 | 21 | Full |
| 1 | 3264x1848 | 28 | 16:9 |
| 2 | 1920x1080 | 30 | 16:9 |
| 3 | 1280x720 | 60 | 16:9 |
| 4 | 1280x720 | 120 | 16:9 (센서 제한) |

### IMX219 CSI 카메라 Python 예제

```python
import cv2

# CSI 카메라 GStreamer 파이프라인
pipeline = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), "
    "width=1280, height=720, "
    "framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=1280, height=720 ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Failed to open CSI camera")
    exit()

print("CSI Camera opened successfully")
print(f"Resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x"
      f"{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.putText(frame, "CSI Camera (IMX219)", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('CSI Camera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### IMX477 (HQ Camera)

```python
# IMX477 파이프라인
pipeline_hq = (
    "nvarguscamerasrc sensor-id=0 ! "
    "video/x-raw(memory:NVMM), "
    "width=1920, height=1080, framerate=30/1 ! "
    "nvvidconv ! "
    "video/x-raw, format=BGRx ! "
    "videoconvert ! "
    "video/x-raw, format=BGR ! "
    "appsink"
)
```

---

## 3. USB Camera

### USB 카메라 확인

```bash
# 연결된 USB 장치 확인
lsusb

# 비디오 장치 확인
v4l2-ctl --list-devices

# USB 카메라 상세 정보
v4l2-ctl -d /dev/video1 --all
```

### USB 카메라 Python

```python
import cv2

# USB 카메라 (일반적으로 /dev/video1)
cap = cv2.VideoCapture(1)

# 속성 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('USB Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 4. RTSP (IP Camera)

### RTSP 스트리밍

```python
import cv2

# IP Camera RTSP URL
rtsp_url = "rtsp://admin:password@192.168.1.200:554/stream1"

cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 지연 최소화

while True:
    ret, frame = cap.read()
    if not ret:
        print("Reconnecting...")
        cap.open(rtsp_url)
        continue

    cv2.imshow('RTSP Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### RTSP 서버 실행 (Jetson → IP Camera 역할)

```bash
# CSI 카메라 → RTSP 스트리밍
gst-launch-1.0 nvarguscamerasrc ! \
    'video/x-raw(memory:NVMM), width=1280, height=720' ! \
    nvvidconv ! 'video/x-raw, format=I420' ! \
    omxh264enc ! 'video/x-h264, stream-format=byte-stream' ! \
    h264parse ! rtph264pay ! \
    udpsink host=224.1.1.1 port=5000
```

---

## 5. Arducam 카메라

Arducam은 다양한 CSI 카메라 모듈을 제공합니다.

### Arducam IMX219 (라즈베리파이 v2 호환)

```bash
# Arducam IMX219 설정 (라즈베리파이 포맷)
# Jetson에서는 sensor-id=0로 자동 인식

# 확인
sudo i2cdetect -y -r 7
# 0x10 주소 확인 → Arducam IMX219 정상
```

### Arducam 자동 노출 제어

```python
import cv2

# AE(자동 노출) 및 AWB(자동 화이트밸런스) 제어
pipeline = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), width=1280, height=720 ! "
    "nvvidconv flip-method=2 ! "  # 상하 반전
    "video/x-raw, format=BGRx ! videoconvert ! appsink"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

# 수동 노출 설정 (nvarguscamerasrc controls)
# exposure = 1000000 (1ms) ~ 33000000 (33ms)
# gain = 1 ~ 16
```

---

## 6. 카메라 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| **CSI 카메라 안잡힘** | 케이블 연결 불량 | 재연결, 반대 방향 시도 |
| **검은 화면** | 잘못된 sensor-id | `sensor-id=0` 또는 `1` 시도 |
| **깜빡임** | 전원 부족 | 외부 전원 공급 |
| **낮은 FPS** | 해상도/파이프라인 | 1280x720, varspeed 확인 |
| **USB 미인식** | 권한 문제 | `sudo` 또는 udev 규칙 추가 |
| **색상 이상** | WB 설정 | `whitebalance=1` (auto) |

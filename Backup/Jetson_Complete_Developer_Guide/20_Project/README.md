# 20. 실무 프로젝트

## 프로젝트 개요

본 장에서는 Jetson Xavier NX를 활용한 실무 프로젝트를 다룹니다.
대한상공회의소 자율주행하드웨어개발 과정과 연계하여 구성되었습니다.

---

## 프로젝트 1: AI Camera (지능형 카메라)

### 개요
USB/CSI 카메라로 실시간 영상을 캡처하고 AI 객체 검출을 수행합니다.

### 난이도: ⭐⭐
### 소요시간: 2~3h

### 구조
```
[CSI/USB Camera] → [OpenCV Capture] → [TensorRT YOLO] → [결과 표시]
```

### 실습

```python
# ai_camera.py
import cv2
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda

class AICamera:
    def __init__(self, engine_path, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # TensorRT 엔진 로드 (생략)
        print(f"AI Camera initialized (device: {camera_id})")

    def process_frame(self, frame):
        # AI 추론 (객체 검출)
        height, width = frame.shape[:2]
        # ... TensorRT 추론 로직 ...

        # 결과를 프레임에 표시
        cv2.putText(frame, "AI Camera Ready", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            result = self.process_frame(frame)
            cv2.imshow('AI Camera', result)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    cam = AICamera('yolov11.engine')
    cam.run()
```

---

## 프로젝트 2: AGV (Automated Guided Vehicle)

### 개요
라인 트레이싱 또는 경로 추종 기능을 갖춘 자율주행 AGV.

### 난이도: ⭐⭐⭐
### 소요시간: 4~6h

### 시스템 구성
```
[Camera/LiDAR] → [경로 인식] → [모터 제어] → [주행]
                     ↓
               [장애물 감지] → [회피/정지]
```

### 핵심 코드 (라인 트레이싱)
```python
# line_tracing.py
import cv2
import numpy as np
import Jetson.GPIO as GPIO

class LineTracer:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        # 모터 초기화 (생략)

    def get_line_position(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 200, 255,
                                  cv2.THRESH_BINARY_INV)
        height, width = binary.shape
        roi = binary[height//2:, :]
        M = cv2.moments(roi)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            return cx - width // 2  # 중앙과의 오차
        return None

    def control_motor(self, error, max_error=200):
        kp = 0.5
        turn = error / max_error * 50
        # omni_drive(0, 30, turn)  # 전진 + 회전
        return turn

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            error = self.get_line_position(frame)

            if error is not None:
                turn = self.control_motor(error)
                cv2.putText(frame, f"Error: {error}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 255, 0), 2)
            else:
                print("Line not found! Searching...")

            cv2.imshow('AGV Line Tracing', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
```

---

## 프로젝트 3: AMR (Autonomous Mobile Robot)

### 개요
LiDAR + SLAM 기반 자율주행 로봇 (ROS1 Melodic 활용).

### 난이도: ⭐⭐⭐⭐
### 소요시간: 8~16h

### 필수 패키지
```bash
sudo apt install ros-melodic-slam-gmapping
sudo apt install ros-melodic-amcl
sudo apt install ros-melodic-move-base
sudo apt install ros-melodic-dwa-local-planner
```

### SLAM 실행
```bash
# 1. LiDAR 실행
roslaunch rplidar_ros rplidar.launch

# 2. SLAM (지도 작성)
roslaunch slam_gmapping slam_gmapping.launch

# 3. RVIZ로 확인
rviz

# 4. 키보드로 로봇 이동 (지도 생성)
roslaunch teleop_twist_keyboard teleop.launch

# 5. 지도 저장
rosrun map_server map_saver -f my_map
```

### 자율 주행 (AMCL + MoveBase)
```bash
# 1. LiDAR 실행
roslaunch rplidar_ros rplidar.launch

# 2. AMCL (위치 추정)
roslaunch amcl amcl.launch map_file:=my_map.yaml

# 3. MoveBase (경로 계획 + 주행)
roslaunch move_base move_base.launch

# 4. RVIZ에서 목적지 설정 (2D Nav Goal)
rviz
```

---

## 프로젝트 4: Robot Vision (Pick & Place)

### 개요
카메라로 객체를 인식하고 로봇팔의 그리핑 포인트를 계산합니다.

### 난이도: ⭐⭐⭐
### 소요시간: 4~6h

```python
# robot_vision.py
import cv2
import numpy as np

class RobotVision:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)

    def detect_object(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 특정 색상 객체 검출 (예: 빨간색)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 1000:  # 최소 면적
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                print(f"Object at: ({cx}, {cy}), Area: {area}")

        return frame

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            result = self.detect_object(frame)
            cv2.imshow('Robot Vision', result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
```

---

## 프로젝트 5: OCR (Text Recognition)

### 개요
Jetson으로 실시간 문자 인식(OCR)을 수행합니다.

### 난이도: ⭐⭐
### 소요시간: 2~3h

```bash
# 설치
pip3 install pytesseract
sudo apt install tesseract-ocr tesseract-ocr-kor
```

```python
# jetson_ocr.py
import cv2
import pytesseract

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # OCR 수행
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='kor+eng')

    if text.strip():
        cv2.putText(frame, text.strip()[:30], (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)

    cv2.imshow('Jetson OCR', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 프로젝트 6: Object Detection (YOLOv11 + TensorRT)

### 개요
YOLOv11 모델을 TensorRT로 최적화하여 실시간 객체 검출.

### 난이도: ⭐⭐⭐⭐
### 소요시간: 4~8h

(자세한 내용은 `16_YOLO` 섹션 참조)

---

## 프로젝트 7: Pose Estimation (자세 추정)

### 개요
사람의 관절 위치를 실시간으로 추정합니다.

### 난이도: ⭐⭐⭐
### 소요시간: 3~5h

---

## 프로젝트 템플릿

### README.md 예시
```markdown
# 프로젝트명

## 개요
간단한 설명

## 시스템 요구사항
- JetPack 4.6+
- Python 3.6+
- (기타 의존성)

## 설치
```bash
git clone ...
cd project
pip3 install -r requirements.txt
```

## 실행
```bash
python3 main.py
```

## 결과 예시
(스크린샷 또는 영상)

## 학습 포인트
- 배운 점 1
- 배운 점 2
```

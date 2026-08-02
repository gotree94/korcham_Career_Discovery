# 07. OpenCV on Jetson

## 1. OpenCV 개요

OpenCV(Open Source Computer Vision Library)는 실시간 컴퓨터 비전을 위한 라이브러리입니다.

| 항목 | 현재 환경 |
|------|----------|
| OpenCV 버전 | 4.1.1 |
| CUDA 지원 | O (GPU 가속 가능) |
| Python 바인딩 | cv2 |

### GPU 가속 OpenCV 빌드 확인

```python
import cv2
print(cv2.getBuildInformation())
# CUDA 관련 항목 확인:
#   CUDA: YES
#   cuDNN: YES
#   OpenCL: YES
```

---

## 2. 기본 이미지 처리

### 이미지 읽기/쓰기/표시

```python
import cv2
import numpy as np

# 읽기
img = cv2.imread('image.jpg')
print(f"Shape: {img.shape}")  # (height, width, channels)

# 변환
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
resized = cv2.resize(img, (640, 480))
rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

# 쓰기
cv2.imwrite('output.jpg', gray)
```

### 실시간 카메라

```python
import cv2

cap = cv2.VideoCapture(0)  # 0: USB, 1: CSI (gstreamer)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # GPU 가속 처리 (cv2.cuda)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    cv2.imshow('Camera', edges)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 3. CUDA 가속 OpenCV

OpenCV의 CUDA 모듈은 GPU에서 직접 이미지 처리를 수행합니다.

### CPU vs GPU 성능 비교

```python
import cv2
import time
import numpy as np

img = cv2.imread('large_image.jpg')
img_gpu = cv2.cuda_GpuMat()
img_gpu.upload(img)

# CPU GaussianBlur
start = time.time()
for _ in range(100):
    cpu_result = cv2.GaussianBlur(img, (15, 15), 1.5)
cpu_time = time.time() - start
print(f"CPU: {cpu_time*10:.1f} ms/frame")

# GPU GaussianBlur
start = time.time()
for _ in range(100):
    gpu_result = cv2.cuda_GaussianBlur(img_gpu, (15, 15), 1.5)
gpu_time = time.time() - start
print(f"GPU: {gpu_time*10:.1f} ms/frame")

print(f"GPU speedup: {cpu_time/gpu_time:.1f}x")
```

### CUDA 지원 함수 목록

```python
# 이미지 필터
cv2.cuda_GaussianBlur()
cv2.cuda_Sobel()
cv2.cuda_Canny()
cv2.cuda_bilateralFilter()

# 색상 변환
cv2.cuda_cvtColor()

# 피라미드
cv2.cuda_pyrDown()
cv2.cuda_pyrUp()

# 행렬 연산
cv2.cuda_add()
cv2.cuda_multiply()
cv2.cuda_threshold()
```

---

## 4. 실습: Sobel Edge Detection (CUDA)

```python
import cv2
import numpy as np
import time

# CPU 버전
def sobel_cpu(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    return cv2.magnitude(sobelx, sobely)

# GPU 버전
def sobel_gpu(img):
    gpu_img = cv2.cuda_GpuMat()
    gpu_img.upload(img)
    gpu_gray = cv2.cuda.cvtColor(gpu_img, cv2.COLOR_BGR2GRAY)
    gpu_sobelx = cv2.cuda.createSobelFilter(
        gpu_gray.type(), 1, 0, 3)
    gpu_sobely = cv2.cuda.createSobelFilter(
        gpu_gray.type(), 0, 1, 3)
    sobelx = gpu_sobelx.apply(gpu_gray)
    sobely = gpu_sobely.apply(gpu_gray)
    result = cv2.cuda.addWeighted(sobelx, 0.5, sobely, 0.5, 0)
    return result.download()

# 실행
img = cv2.imread('test.jpg')

start = time.time()
cpu_result = sobel_cpu(img)
print(f"CPU: {(time.time()-start)*1000:.1f}ms")

start = time.time()
gpu_result = sobel_gpu(img)
print(f"GPU: {(time.time()-start)*1000:.1f}ms")
```

---

## 5. CSI 카메라 with GStreamer

```python
import cv2

# CSI 카메라 파이프라인 (IMX219)
cs_pipeline = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), width=1280, height=720, "
    "framerate=30/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=1280, height=720 ! "
    "appsink"
)

cap = cv2.VideoCapture(cs_pipeline, cv2.CAP_GSTREAMER)

while True:
    ret, frame = cap.read()
    cv2.imshow('CSI Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 6. OpenCV + TensorRT 연동

```python
import cv2
import numpy as np
import tensorrt as trt

def preprocess_for_trt(frame, input_size=(224, 224)):
    """OpenCV 프레임을 TensorRT 입력 형식으로 변환"""
    img = cv2.resize(frame, input_size)
    img = img.transpose(2, 0, 1)  # HWC → CHW
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)
    return img

# 사용 예
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    input_data = preprocess_for_trt(frame)
    # TensorRT 추론 호출
    # output = engine.infer(input_data)

    cv2.imshow('OpenCV + TensorRT', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

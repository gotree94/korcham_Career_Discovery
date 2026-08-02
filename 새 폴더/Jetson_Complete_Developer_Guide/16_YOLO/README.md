# 16. YOLO Object Detection

## 1. YOLO 개요

YOLO(You Only Look Once)는 실시간 객체 검출을 위한 대표적인 딥러닝 모델입니다.

| 버전 | 출시 | mAP | 속도 (Jetson) | 특징 |
|:----:|:----:|:---:|:------------:|------|
| YOLOv5 | 2021 | 50.4 | ~30 FPS | PyTorch 기반, 경량 |
| YOLOv8 | 2023 | 53.0 | ~25 FPS | Ultralytics 공식 |
| **YOLOv11** | **2024** | **54.3** | **~30 FPS** | **최신, 가장 빠름** |
| YOLO-NAS | 2023 | 52.2 | ~35 FPS | NVIDIA 최적화 |

> 현재 JetPack 4.6에서는 ONNX → TensorRT 변환을 통해 YOLOv11 사용 가능.

---

## 2. YOLOv11 설치

```bash
# Ultralytics 설치 (Python 3.6 호환 확인)
pip3 install ultralytics

# ONNX
pip3 install onnx onnxruntime

# 설치 확인
python3 -c "from ultralytics import YOLO; print('YOLO ready')"
```

---

## 3. YOLOv11 기본 사용

### 이미지 객체 검출

```python
from ultralytics import YOLO
import cv2

# 모델 로드
model = YOLO('yolo11n.pt')  # nano: 가장 빠름
# model = YOLO('yolo11s.pt')  # small
# model = YOLO('yolo11m.pt')  # medium

# 단일 이미지 추론
results = model('test.jpg')

# 결과 표시
for r in results:
    boxes = r.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        print(f"Class: {model.names[cls]}, "
              f"Conf: {conf:.2f}, "
              f"Box: {[int(v) for v in xyxy]}")
```

### 실시간 카메라 검출

```python
from ultralytics import YOLO
import cv2

model = YOLO('yolo11n.pt')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 추론
    results = model(frame, verbose=False)

    # 결과 시각화
    annotated = results[0].plot()

    cv2.imshow('YOLOv11 Live', annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 4. ONNX Export (TensorRT 변환 전)

```python
from ultralytics import YOLO

# 모델 로드
model = YOLO('yolo11n.pt')

# ONNX 변환
model.export(format='onnx', imgsz=640)

# 확인
import onnx
onnx_model = onnx.load('yolo11n.onnx')
onnx.checker.check_model(onnx_model)
print("ONNX export successful!")
```

---

## 5. TensorRT 변환 (FP16)

```bash
# trtexec으로 ONNX → TensorRT 엔진 변환
trtexec --onnx=yolo11n.onnx \
        --saveEngine=yolo11n_fp16.engine \
        --fp16 \
        --workspace=1024

# NVDLA 사용 (Xavier NX)
trtexec --onnx=yolo11n.onnx \
        --saveEngine=yolo11n_dla.engine \
        --useDLA --dlaCore=0 \
        --fp16 \
        --workspace=1024

# 변환 시간: 약 5~15분 (모델 크기에 따라 상이)
```

---

## 6. TensorRT YOLO 추론

```python
# trt_yolo.py
import tensorrt as trt
import pycuda.driver as cuda
import numpy as np
import cv2
import time

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

class TRTYOLO:
    def __init__(self, engine_path, conf_thresh=0.5):
        with open(engine_path, 'rb') as f:
            runtime = trt.Runtime(TRT_LOGGER)
            self.engine = runtime.deserialize_cuda_engine(f.read())
            self.context = self.engine.create_execution_context()
        self.conf_thresh = conf_thresh
        self.input_shape = (640, 640)

        # 바인딩 설정
        self.inputs = []
        self.outputs = []
        self.bindings = []
        for binding in self.engine:
            size = trt.volume(self.engine.get_binding_shape(binding))
            dtype = trt.nptype(self.engine.get_binding_dtype(binding))
            host_mem = cuda.pagelocked_empty(size, dtype)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            self.bindings.append(int(device_mem))
            if self.engine.binding_is_input(binding):
                self.inputs.append(host_mem)
            else:
                self.outputs.append(host_mem)

    def preprocess(self, frame):
        img = cv2.resize(frame, self.input_shape)
        img = img.transpose(2, 0, 1)
        img = img.astype(np.float32) / 255.0
        return np.expand_dims(img, axis=0)

    def infer(self, frame):
        input_data = self.preprocess(frame)
        np.copyto(self.inputs[0], input_data.ravel())
        cuda.memcpy_htod(self.bindings[0], self.inputs[0])
        self.context.execute_v2(self.bindings)
        cuda.memcpy_dtoh(self.outputs[0], self.bindings[1])
        return self.postprocess(self.outputs[0])

    def postprocess(self, output):
        # YOLO 출력 파싱 (boxes, scores, classes)
        # ... (출력 형식에 따라 처리)
        return []

# 실행
engine = TRTYOLO('yolo11n_fp16.engine')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    start = time.time()
    detections = engine.infer(frame)
    elapsed = time.time() - start

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{cls}: {conf:.2f}", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.putText(frame, f"FPS: {1/elapsed:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('TensorRT YOLO', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 7. 성능 벤치마크 (Xavier NX, 20W 모드)

| 모델 | 형식 | FPS | mAP | 메모리 |
|:----:|:----:|:---:|:---:|:-----:|
| YOLOv11n | PyTorch | 12 | 39.5 | 1.2GB |
| YOLOv11n | ONNX | 18 | 39.5 | 800MB |
| YOLOv11n | TensorRT FP16 | **45** | 39.2 | 450MB |
| YOLOv11n | TensorRT INT8 | **60** | 37.8 | 300MB |
| YOLOv11s | TensorRT FP16 | 22 | 47.0 | 800MB |
| YOLOv11m | TensorRT FP16 | 10 | 52.0 | 1.5GB |

> 실제 FPS는 입력 해상도, 배치 크기, NVDLA 사용 여부에 따라 달라집니다.

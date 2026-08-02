# 15. AI Inference on Jetson

## 1. AI 추론 파이프라인 개요

```
학습 (Training) — 클라우드/PC에서 수행
  │
  ├── PyTorch / TensorFlow → 모델 학습
  ├── ONNX Export (.onnx)
  └── TensorRT Optimization (.trt / .engine)
        │
추론 (Inference) — Jetson Edge에서 수행
        ├── TensorRT Runtime
        ├── DeepStream SDK
        └── Custom Application (Python/C++)
```

### 모델 변환 파이프라인

```
PyTorch (.pth) → ONNX (.onnx) → TensorRT (.engine) → Jetson 추론
```

---

## 2. TensorRT

### TensorRT란?

NVIDIA TensorRT는 AI 추론을 **최적화**하고 **가속**하는 SDK입니다.

| 최적화 기법 | 효과 |
|:-----------|:----:|
| 레이어 융합 (Layer Fusion) | 커널 실행 횟수 감소 |
| FP16/INT8 양자화 | 모델 크기 1/2~1/4, 속도 2~4배 |
| 커널 자동 튜닝 | 최적의 CUDA 커널 선택 |
| 동적 메모리 관리 | 메모리 사용량 최적화 |
| **NVDLA 연동** | Xavier NX 전용 하드웨어 가속 |

### TensorRT 버전 확인 (현재 환경)

```bash
# TensorRT 버전
dpkg -l | grep tensorrt

# Python에서 확인
python3 -c "import tensorrt as trt; print(trt.__version__)"
```

### ONNX → TensorRT 변환 예제

```python
# convert_to_trt.py
import tensorrt as trt

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

def build_engine(onnx_path, engine_path, use_fp16=True, use_dla=False):
    builder = trt.Builder(TRT_LOGGER)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, TRT_LOGGER)

    # ONNX 파일 로드
    with open(onnx_path, 'rb') as f:
        parser.parse(f.read())

    config = builder.create_builder_config()
    config.set_memory_pool_limit(
        trt.MemoryPoolType.WORKSPACE, 1 << 30)  # 1GB

    if use_fp16:
        config.set_flag(trt.BuilderFlag.FP16)

    # Xavier NX: NVDLA 사용 설정
    if use_dla:
        config.set_flag(trt.BuilderFlag.GPU_FALLBACK)
        config.default_device_type = trt.DeviceType.DLA
        config.DLA_core = 0

    # 엔진 빌드
    serialized_engine = builder.build_serialized_network(network, config)
    with open(engine_path, 'wb') as f:
        f.write(serialized_engine)

    print(f"Engine saved to {engine_path}")

if __name__ == '__main__':
    build_engine('model.onnx', 'model_fp16.engine',
                 use_fp16=True, use_dla=False)
```

### TensorRT 추론 실행

```python
# inference_trt.py
import tensorrt as trt
import numpy as np
import cv2
import time

TRT_LOGGER = trt.Logger(trt.Logger.WARNING)

class TRTInference:
    def __init__(self, engine_path):
        with open(engine_path, 'rb') as f:
            runtime = trt.Runtime(TRT_LOGGER)
            self.engine = runtime.deserialize_cuda_engine(f.read())
            self.context = self.engine.create_execution_context()
            self.inputs, self.outputs, self.bindings = [], [], []
            self.stream = cuda.Stream()

            for binding in self.engine:
                size = trt.volume(
                    self.engine.get_binding_shape(binding))
                dtype = trt.nptype(
                    self.engine.get_binding_dtype(binding))
                host_mem = cuda.pagelocked_empty(size, dtype)
                device_mem = cuda.mem_alloc(host_mem.nbytes)
                self.bindings.append(int(device_mem))
                if self.engine.binding_is_input(binding):
                    self.inputs.append(host_mem)
                else:
                    self.outputs.append(host_mem)

    def infer(self, input_data):
        np.copyto(self.inputs[0], input_data.ravel())
        cuda.memcpy_htod_async(
            self.bindings[0], self.inputs[0], self.stream)
        self.context.execute_async_v2(
            bindings=self.bindings,
            stream_handle=self.stream.handle)
        cuda.memcpy_dtoh_async(
            self.outputs[0], self.bindings[1], self.stream)
        self.stream.synchronize()
        return self.outputs[0]

# 사용 예
if __name__ == '__main__':
    engine = TRTInference('model_fp16.engine')

    # 이미지 전처리 (224x224)
    img = cv2.imread('test.jpg')
    img = cv2.resize(img, (224, 224))
    img = img.transpose(2, 0, 1).astype(np.float32) / 255.0

    # 추론
    start = time.time()
    output = engine.infer(img)
    elapsed = time.time() - start

    print(f"Inference time: {elapsed*1000:.1f} ms")
    print(f"Top-1 class: {np.argmax(output)}")
```

---

## 3. ONNX Runtime

### 설치

```bash
# ONNX Runtime (aarch64)
pip3 install onnxruntime

# 확인
python3 -c "import onnxruntime; print(onnxruntime.__version__)"
```

### ONNX Runtime 추론

```python
# inference_onnx.py
import onnxruntime as ort
import numpy as np
import cv2

# 세션 생성
session = ort.InferenceSession('model.onnx')
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# 입력 준비
img = cv2.imread('test.jpg')
img = cv2.resize(img, (224, 224))
img = img.transpose(2, 0, 1).astype(np.float32) / 255.0
img = np.expand_dims(img, axis=0)

# 추론
outputs = session.run([output_name], {input_name: img})
pred_class = np.argmax(outputs[0])
print(f"Predicted class: {pred_class}")
```

---

## 4. PyTorch (Jetson에서)

### 설치

```bash
# JetPack 4.6: PyTorch 1.10 (공식 휠)
wget https://nvidia.box.com/shared/static/...torch...whl
pip3 install torch-*-linux_aarch64.whl

# torchvision
sudo apt install libjpeg-dev zlib1g-dev
pip3 install torchvision
```

> JetPack 버전에 맞는 PyTorch 휠을 NVIDIA 공식 페이지에서 다운로드해야 합니다.

### PyTorch 추론 예제

```python
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np

# 모델 로드 (사전 학습)
model = torch.jit.load('resnet50_traced.pt')
model.eval().to('cuda')

# 이미지 전처리
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

img = Image.open('test.jpg')
input_tensor = transform(img).unsqueeze(0).to('cuda')

# 추론
with torch.no_grad():
    output = model(input_tensor)
    pred = torch.argmax(output, dim=1).item()

print(f"Predicted: {pred}")
```

---

## 5. TensorRT 명령줄 도구 (trtexec)

```bash
# ONNX → TensorRT 엔진 변환 (FP16)
trtexec --onnx=model.onnx \
        --saveEngine=model_fp16.engine \
        --fp16

# NVDLA 사용 (Xavier NX)
trtexec --onnx=model.onnx \
        --saveEngine=model_dla.engine \
        --useDLA --dlaCore=0 --fp16

# 추론 속도 테스트
trtexec --loadEngine=model_fp16.engine \
        --duration=10  # 10초 동안 반복 추론
```

---

## 6. Jetson AI 성능 최적화 체크리스트

| 최적화 | 방법 | 예상 효과 |
|:-------|:----|:---------:|
| FP16 양자화 | `--fp16` | 속도 2x, 메모리 1/2 |
| INT8 양자화 | 보정 데이터셋 필요 | 속도 3~4x, 메모리 1/4 |
| NVDLA 사용 | `--useDLA --dlaCore=0` | GPU 부하 ↓, 전력 효율 ↑ |
| 배치 처리 | batch_size ≥ 1 | 처리량 ↑ |
| jetson_clocks | `sudo jetson_clocks` | 성능 일관성 ↑ |
| 전력 모드 | `sudo nvpmodel -m 0` | 최대 성능 |

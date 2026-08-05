# 05. AI 추론 (TensorRT)

## 학습 목표

- GPU 가속 AI 추론 개념 이해
- TensorRT 변환 및 최적화
- YOLO 객체 인식 실습

## 사전 준비

- [ ] JetPack의 TensorRT/CUDA 설치 확인 (`01장`)
- [ ] 사전 학습된 YOLO 모델 파일
- [ ] 테스트 이미지/영상

```bash
$ python3 -c "import tensorrt; print(tensorrt.__version__)"
$ nvidia-smi   # GPU 상태 확인
```

---

## 1. AI 추론 개요

- 딥러닝 학습(Inference)과 추론(Inference) 차이
- CPU 추론 vs GPU(CUDA) 추론
- Jetson의 딥러닝 파이프라인: TensorRT → cuDNN → CUDA

---

## 2. TensorRT 소개

- NVIDIA TensorRT: GPU 추론 최적화 엔진
- FP16 / INT8 양자화로 성능 향상
- ONNX → TensorRT Engine 변환 흐름

```text
[PyTorch 모델] → [ONNX Export] → [TensorRT Engine] → [추론 실행]
```

> ※ 각 단계별 변환 명령과 예제 코드를 추가하세요.

---

## 3. YOLO 객체 인식 실습

### 기본 파이프라인

1. 카메라/영상 입력
2. YOLO 모델 추론
3. 바운딩박스 시각화
4. FPS 성능 측정

```python
# 예제 골격 (실행 코드는 교습 자료에 상세 작성)
def detect(frame):
    detections = model(frame)
    return render_boxes(frame, detections)
```

---

## 4. 성능 비교

| 방식 | FPS | 비고 |
| ---- | --- | ---- |
| CPU 추론 | - | 기준값 측정 |
| GPU 추론 (TensorRT) | - | 최적화 전후 비교 |
| FP16 / INT8 | - | 정확도 vs 속도 트레이드오프 |

> ※ 실습 결과를 채워 넣는 표입니다.

---

## 실습

1. TensorRT 설치 확인
2. ONNX 모델을 TensorRT 엔진으로 변환
3. 정지 이미지에서 객체 인식
4. 실시간 카메라 객체 인식 + FPS 측정

## 정리 및 체크리스트

- [ ] TensorRT 엔진 변환
- [ ] YOLO 객체 인식 실행
- [ ] 실시간 추론 (FPS 확인)
- [ ] FP16/INT8 성능 비교

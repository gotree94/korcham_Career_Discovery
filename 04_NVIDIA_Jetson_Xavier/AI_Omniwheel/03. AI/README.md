# 03. AI — 객체 인식 및 추적 실습

본 과정은 Jetson Xavier NX의 **TensorRT**를 이용해 학습된 **SSD(Single Shot Detector)** 모델을
최적화(변환)하고, 실시간 카메라 영상에서 **사람(person)** 을 검출한 뒤,
검출 결과로 **옴니휠 로봇을 자율 추적(주행)** 하는 실습입니다.

- 프레임워크: TensorFlow 1.15 → UFF → **TensorRT 8** (JetPack 4.x 기반)
- 카메라: GStreamer 스트리밍 → `tcp://127.0.0.1:5000`
- 모션: ROS 1 `/cmd_vel` 토픽으로 로봇 제어

---

## 📚 커리큘럼 구성

| 순서 | 파일 | 내용 | 비고 |
| ---- | ---- | ---- | ---- |
| 01 | [5. Optimization.md](5.%20Optimization.md) | TF 체크포인트 → TensorRT 엔진 변환(FP16) | 모델 준비 |
| 02 | [6. Inference.md](6.%20Inference.md) | 카메라 영상에서 실시간 사람 검출 | 검출만 수행 |
| 03 | [7. Object Tracking.md](7.%20Object%20Tracking.md) | 검출 → `/cmd_vel` 발행 → 로봇 자율 추적 | 종합 |

> 📌 반드시 5 → 6 → 7 순서로 진행해야 합니다.
> 5에서 생성한 **최적화 모델(optimization 폴더)** 이 6·7의 전제조건입니다.

---

## 🛠 사전 준비 (핵심)

### 1. 필수 패키지 상태 확인 — ⚠️ 매우 중요

```python
from bready.object_detection_tools.lib.optimization_tools import optimizer as det_optimizer
```

- 위 import가 성공해야 실습 가능합니다.
- **`bready` 패키지는 이 아카이브에 포함되어 있지 않습니다.** (`HiBready\_internal` 비어 있음)
- 실제 보드에 원본 이미지에 포함된 `bready` 패키지가 설치되어 있어야 합니다.
- 아카이브에만 들어있고 보드에 없는 경우: 별도로 패키지를 확보해
  `pip install` 또는 경로 추가 후 진행하세요.

### 2. 모델 파일 위치 (폴더 구조)

```
03. AI/
├── recognition/          # 원본 TensorFlow 모델
│   ├── pipeline.config
│   ├── model.ckpt.meta / .index / .data-00000-of-00001
│   ├── frozen_inference_graph.pb
│   └── saved_model/
├── optimization/         # 5번 실습의 결과물 (TensorRT 엔진)
│   └── frozen_inference_graph.pb
├── detection_classes.txt # 클래스(라벨) 목록
└── 5/6/7 .ipynb
```

### 3. 카메라 스트리밍 실행 (선행 필수)

```bash
# startup/startup.sh (GStreamer: nvarguscamerasrc → tcpserversink port 5000)
$ ./startup.sh
```

- 6·7번 실습은 `tcp://127.0.0.1:5000` 에서 영상을 받으므로
  **이 스트리밍이 먼저 실행 중이어야** 합니다.

### 4. ROS Master (7번만 해당)

```bash
$ source /opt/ros/melodic/setup.bash
$ roscore
$ source ~/catkin_ws/devel/setup.bash   # 옴니휠 모터 구동 노드 실행 시
```

- 7번은 `/cmd_vel` 토픽으로 주행 명령을 보내므로, 이를 **구독하는 옴니휠 구동 노드**
  (예: `omniwheel_project` 의 노드)가 함께 실행 중이어야 합니다.

### 5. 실습 권장 환경

```bash
$ jupyter notebook   # camera/GStreamer, TensorRT, rospy가 모두 뜨는 터미널에서 실행
```

---

## ⚠️ 공통 주의사항

1. **무한 루프**가 많습니다. 종료는 셀 정지(`Kernel → Interrupt`) 또는 `KeyboardInterrupt` 입니다.
2. 카메라·TensorRT·ROS를 한 번에 띄우면 메모리 부족이 발생할 수 있습니다.
   → 카메라 스트리밍을 먼저 단독 실행 후 실습.
3. `detection_classes.txt` : COCO 90클래스 기반. 본 실습은 **person** 클래스를 사용합니다.
4. GPU 메모리 절약을 위해 FP16 정밀도로 변환합니다 (5번 실습).

---

## 🔄 실습 실행 순서 요약

| 단계 | 내용 | 실행 |
| ---- | ---- | ---- |
| 1 | `startup.sh` 실행 (카메라 스트리밍) | 터미널 |
| 2 | 5. Optimization 실행 → `optimization/` 생성 | 노트북 |
| 3 | 6. Inference 실행 → 화면에 사람 검출 박스 확인 | 노트북 |
| 4 | 7. Object Tracking 실행 → 로봇이 사람을 추적 | 노트북 (+ROS) |

> 확장: 6·7 실습에서 검출 클래스를 바꾸면(person 외 물체) 다른 물체 추적이 가능합니다.

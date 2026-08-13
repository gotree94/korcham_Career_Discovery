# Jetson Orin Nano 성능 비교 및 업그레이드 검토

> 대상: 현재 사용 중인 **Jetson Xavier NX (8GB) Developer Kit** → **Jetson Orin Nano** 교체 검토
> 작성일: 2026-08-13

---

## 1. 사양 비교

| 항목 | 현재 Xavier NX 8GB | Orin Nano 8GB (기본) | Orin Nano Super (8GB) |
|---|---|---|---|
| GPU | Volta 384 CUDA + 48 Tensor | **Ampere 1024 CUDA** + 32 Tensor | Ampere 1024 CUDA @ 1.02GHz |
| AI 성능 | 21 TOPS (INT8) | **40 TOPS** (INT8) | **67 TOPS** (INT8) |
| CPU | 6× Carmel 1.9GHz | 6× A78AE 1.5GHz (IPC 크게↑) | 6× A78AE 1.7GHz |
| 메모리 | 8GB LPDDR4x **51.2 GB/s** | 8GB LPDDR5 **68.3 GB/s** | 8GB LPDDR5 **102.4 GB/s** |
| 전력 | 10/15/20W | 7~25W (유사) | 7~25W |
| 소프트웨어 | JetPack 5.1.7 (종점) | **JetPack 5.x + 6.x (Ubuntu 22.04)** | 동일 |

> **Orin Nano Super란?**
> 하드웨어를 바꾸는 것이 아니라 **소프트웨어(펌웨어/드라이버) 업데이트로 성능을 높이는** 공식 변형입니다.
> 기존 Orin Nano 소유자도 무료로 Super 성능으로 업그레이드할 수 있습니다.

---

## 2. 실제 체감 성능 차이

- **AI 추론(객체인식 등): 약 2배** (Super는 약 3배)
  - 같은 모델이 두 배 빠르거나,
  - **더 크고 정확한 모델(YOLOv8-M 등)을 기존과 같은 FPS로** 구동 가능
- **CPU 연산: 약 1.5~2배** — ROS 노드, 경로계획, 다중 프로세스 동시 구동에 여유 확보
- **메모리 대역폭: 약 1.3배(기본) ~ 2배(Super)** — 카메라 영상 처리, GStreamer 파이프라인, 후처리에 실질 이득
- **소프트웨어 활용도: 차이가 가장 큼** — JetPack 6(Ubuntu 22.04) 지원으로 기존 제약이 대부분 해소됨
  - 네이티브 **ROS2 Humble**, PyTorch 2.4+, 최신 TensorRT 10.x 지원

---

## 3. 반드시 고려할 점 (함정 2가지)

### 3.1 Orin Nano에는 DLA(INT8 전용 가속기)가 없음

| 모델 | GPU | DLA | PVA |
|---|---|---|---|
| Xavier NX | Volta 384 | 1~2개 (있음) | 있음 |
| Orin NX | Ampere 1024 | **2개** | - |
| **Orin Nano** | Ampere 1024 | **없음** | - |

- 현재 시스템이 **TensorRT DLA 모드로 추론 중이라면** Orin Nano로 바꾸면 오히려 전력효율/성능이 퇴보할 수 있음.
- **DLA에 의존한다면 Orin NX 8GB를 권장** (70 TOPS, DLA 2개, Xavier NX 대비 약 3배).
- 판단 방법: `trtexec` 옵션에 `--useDLA`, `--useDLACore=0` 가 있는지, 코드에서 `dla_enabled` 플래그를 쓰는지 확인.

### 3.2 모듈 호환 불가 — "지금 시스템에 끼우는 것"은 불가능

- NVIDIA 공식 답변: Orin Nano/NX는 Xavier NX와 **핀 호환이 안 됨** (같은 260핀 SO-DIMM 폼팩터지만 핀아웃 상이).
- 현재 Developer Kit 캐리어 보드에 Orin Nano를 꽂을 수 없음.
- **Orin Nano용 개발 키트(또는 모듈 + 호환 캐리어 보드)를 새로 구매**해야 함.
- GPIO 40핀 핀맵은 Xavier NX와 거의 동일하지만, **CSI 카메라 및 일부 I/O는 캐리어 보드별 재검증 필요**.

---

## 4. 결론

| 관점 | 판단 |
|---|---|
| 순수 성능 (AI 2배, CPU/메모리 향상) | ✅ 확실한 이득 |
| 소프트웨어 활용도 (ROS2 Humble 네이티브 등) | ✅ 이 보드의 한계 해소 |
| 비용/이식 작업 (새 보드 구매 + 재플래시 + 센서/GPIO/코드 재검증) | ⚠️ 신규 투자 필요 |
| DLA 기반 추론을 쓰는 경우 | ⚠️ Orin NX로 가야 함 |

**정리**: "지금 시스템에 적용"이 아니라 **"보드를 Orin Nano(또는 NX)로 교체"**라는 전제로 성능 2배 + 소프트웨어 제약 해소의 실질적 이득이 있습니다.
구매 전에 **현재 코드가 GPU(TensorRT GPU 모드)로 도는지, DLA로 도는지**부터 확인하세요 — DLA라면 Orin NX가 정답입니다.

---

## 5. 참고 링크

- NVIDIA Jetson 모듈 성능 비교: https://www.nvidia.com/ko-kr/autonomous-machines/embedded-systems/jetson-modules/
- Orin Nano Super 업데이트: https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/nano-super-developer-kit/
- Orin Nano vs Xavier NX 핀 호환성 (NVIDIA FAQ): Jetson 개발자 포럼 "Orin Nano pin compatible with Xavier NX" 검색

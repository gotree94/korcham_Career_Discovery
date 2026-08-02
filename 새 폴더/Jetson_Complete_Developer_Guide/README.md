# Jetson Complete Developer Guide

> NVIDIA Jetson 플랫폼을 위한 종합 개발자 가이드
> Target: Jetson Xavier NX Developer Kit (JetPack 4.6 / Ubuntu 18.04)
> 용도: 대한상공회의소 AI/로봇 교육 과정 교재

---

## 목차

| # | 섹션 | 내용 | 난이도 |
|:-:|:----|:----|:------:|
| 00 | [Introduction](00_Introduction/README.md) | Jetson 개요, AI Edge Computing 개념 | ⭐ |
| 01 | [Jetson Family](01_Jetson_Family/README.md) | 전 모델 비교, Xavier NX 상세, Orin Nano 비교 | ⭐⭐ |
| 02 | [Hardware](02_Hardware/README.md) | CPU/GPU/NVDLA/Memory/CSI/PCIe 구조 | ⭐⭐ |
| 03 | [JetPack](03_JetPack/README.md) | 버전별 비교, 설치 확인, 업그레이드 가이드 | ⭐ |
| 04 | [Installation](04_Installation/README.md) | SDK Manager, Flash, Recovery, 초기 설정 | ⭐⭐ |
| 05 | [Linux](05_Linux/README.md) | Ubuntu, Shell 명령어, tegrastats 모니터링 | ⭐ |
| 06 | [CUDA](06_CUDA/README.md) | CUDA 기초, Vector Add, Sobel, PyCUDA | ⭐⭐⭐ |
| 07 | [OpenCV](07_OpenCV/README.md) | 이미지 처리, GPU 가속, CSI 카메라 | ⭐⭐ |
| 08 | [GStreamer](08_GStreamer/README.md) | 멀티미디어 파이프라인, 스트리밍 | ⭐⭐⭐ |
| 09 | [Camera](09_Camera/README.md) | CSI/USB/RTSP, IMX219, IMX477, Arducam | ⭐⭐ |
| 10 | [GPIO](10_GPIO/README.md) | LED, Button, PWM, Interrupt, 초음파 센서 | ⭐ |
| 11 | [I2C](11_I2C/README.md) | I2C 통신, LCD, 센서 | ⭐⭐ |
| 12 | [SPI](12_SPI/README.md) | SPI 통신 | ⭐⭐ |
| 13 | [UART](13_UART/README.md) | UART 시리얼 통신 | ⭐⭐ |
| 14 | [CAN](14_CAN/README.md) | CAN FD 통신 | ⭐⭐⭐ |
| 15 | [AI Inference](15_AI/README.md) | TensorRT, ONNX, PyTorch, trtexec | ⭐⭐⭐ |
| 16 | [YOLO](16_YOLO/README.md) | YOLOv11, TensorRT 변환, 실시간 검출 | ⭐⭐⭐⭐ |
| 17 | [ROS2](17_ROS2/README.md) | ROS2 개념, Topics/Services/Actions, DDS | ⭐⭐⭐ |
| 18 | [Isaac ROS](18_Isaac_ROS/README.md) | FoundationPose, Visual SLAM, AprilTag | ⭐⭐⭐⭐ |
| 19 | [Isaac Sim](19_Isaac_Sim/README.md) | Digital Twin, ROS2 Bridge, 시뮬레이션 | ⭐⭐⭐⭐ |
| 20 | [Projects](20_Project/README.md) | AI Camera, AGV, AMR, Robot Vision, OCR | ⭐⭐⭐ |
| 21 | [Troubleshooting](21_Troubleshooting/README.md) | 전체 문제해결 가이드, FAQ | ⭐ |

---

## 현재 검증 환경

| 항목 | 값 |
|------|-----|
| Board | NVIDIA Jetson Xavier NX Developer Kit |
| SoC | Tegra Xavier (T194) |
| JetPack | 4.6 (L4T R32.6.1) |
| Ubuntu | 18.04.5 LTS (Bionic Beaver) |
| CUDA | 10.2 |
| TensorRT | 8.x |
| Python | 3.6.9 |
| ROS | Melodic (ROS2는 JetPack 6.x 업그레이드 시) |

---

## 구성 방법

각 섹션은 독립적으로 읽을 수 있도록 구성되어 있습니다.

```bash
# 전체 구조
Jetson_Complete_Developer_Guide/
├── README.md                   ← 이 파일 (전체 목차)
├── 00_Introduction/README.md   ← Jetson 소개
├── 01_Jetson_Family/README.md  ← 제품군 비교
├── ... (각 섹션)
└── code_examples/              ← 실습 코드 모음 (향후 추가)
```

---

## 라이선스

교육 목적으로 자유롭게 사용, 수정, 배포할 수 있습니다.

---

## 참고 자료

- [NVIDIA Jetson Developer Zone](https://developer.nvidia.com/embedded-computing)
- [Jetson Community Projects](https://jetson-nano-projects.com/)
- [NVIDIA Docs — Jetson Xavier NX](https://docs.nvidia.com/jetson/xavier-nx/)

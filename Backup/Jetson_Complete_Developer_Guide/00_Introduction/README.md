# 00. Jetson Introduction

## 1. Jetson이란?

NVIDIA Jetson은 **AI at the Edge(에지에서의 AI)** 를 위해 설계된 임베디드 시스템온칩(SoC) 플랫폼입니다.

| 구분 | 일반 PC | Jetson |
|------|---------|--------|
| 전력 | 65~300W+ | 5~15W (모델별 상이) |
| GPU | 별도 그래픽카드 | 통합 GPU (SoC 내장) |
| 크기 | 데스크탑 | 신용카드~소형 보드 |
| AI 추론 | 클라우드 의존 | 온디바이스 추론 가능 |
| 실시간 제어 | 어려움 | GPIO/I2C/SPI/CAN 직접 제어 |

### Jetson의 핵심 가치

1. **저전력 고성능 AI**: 15W 이하에서 수 TOPS(Tera Operations Per Second)의 AI 성능
2. **온디바이스 AI 추론**: 클라우드 없이 로컬에서 실시간 AI 처리
3. **다양한 I/O**: GPIO, I2C, SPI, UART, CAN, CSI, PCIe 등 로봇/임베디드에 최적화
4. **ROS/ROS2 호환**: 로봇 운영체제와 완벽한 통합
5. **NVIDIA 생태계**: CUDA, TensorRT, DeepStream, Isaac 등 전용 툴체인

---

## 2. AI Edge Computing

### 클라우드 AI vs 엣지 AI

```
클라우드 AI:
  센서 → 인터넷 → 클라우드 서버 → AI 추론 → 결과 ← (대기시간 100ms~1s)

엣지 AI:
  센서 → Jetson → AI 추론 → 즉시 실행 (대기시간 1~10ms)
```

### 엣지 AI의 장점

| 항목 | 설명 |
|------|------|
| **실시간성** | 네트워크 지연 없이 밀리초 단위 응답 |
| **프라이버시** | 데이터가 로컬에서만 처리되어 보안 유리 |
| **오프라인 동작** | 인터넷 없이 AI 구동 가능 |
| **대역폭 절약** | 클라우드로 모든 데이터를 보낼 필요 없음 |

### 적용 분야

| 분야 | 예시 |
|------|------|
| **자율주행 로봇** | AGV, AMR, 자율주행 카트 |
| **스마트 팩토리** | 불량 검사, 안전 감시, 예측 정비 |
| **스마트 시티** | 교통 모니터링, 출입 통제 |
| **의료** | 내시경 영상 분석, 세포 검사 |
| **소매** | 매장 분석, 계산대 없는 결제 |
| **농업** | 작물 상태 모니터링, 선별 |

---

## 3. 본 가이드의 목표

```
이 가이드는 "Jetson 보드를 처음 만지는 개발자/교육생"이
하드웨어 설정부터 CUDA, TensorRT, ROS2, Isaac ROS까지
단계적으로 습득할 수 있도록 구성되었습니다.
```

### 대상 독자
- 임베디드/AI 개발자 입문자
- 로봇 공학도
- 대한상공회의소 AI/로봇 교육 과정 학습자

### 사전 지식
- Python 기본 문법
- Linux 터미널 기초 (선택)

---

## 4. 현재 시스템 정보 (참조)

본 가이드는 아래 환경에서 검증되었습니다:

| 항목 | 값 |
|------|-----|
| Board | NVIDIA Jetson Xavier NX Developer Kit |
| SoC | NVIDIA Tegra Xavier (T194) |
| CPU | 6-Core NVIDIA Carmel ARM v8.2 64-bit |
| GPU | 384-Core NVIDIA Volta + 48 Tensor Cores |
| Ubuntu | 18.04.5 LTS (Bionic Beaver) |
| Architecture | aarch64 |
| L4T | 32.6.1 |
| JetPack | 4.6 |
| CUDA | 10.2 |
| TensorRT | 8.x |
| cuDNN | 8.x |
| Python | 3.6.9 |

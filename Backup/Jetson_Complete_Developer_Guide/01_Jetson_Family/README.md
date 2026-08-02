# 01. Jetson Family

## 1. Jetson 제품군 개요

NVIDIA Jetson은 2014년 첫 출시 이후 지속적으로 발전해왔습니다.

```
Jetson TK1 (2014) → TX1 (2015) → TX2 (2017) → Nano (2019)
→ Xavier NX (2020) → AGX Xavier (2018) → Orin Nano (2022)
→ Orin NX (2022) → AGX Orin (2022) → Orin Nano Super (2024)
```

---

## 2. 주요 모델 상세 비교

| 항목 | **Jetson Nano** | **Xavier NX** | **AGX Xavier** | **Orin Nano** | **Orin NX** | **AGX Orin** |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 출시 | 2019 | 2020 | 2018 | 2022 | 2022 | 2022 |
| CPU | 4x A57 | 6x Carmel | 8x Carmel | 6x A78AE | 12x A78AE | 12x A78AE |
| GPU | 128-core Maxwell | 384-core Volta | 512-core Volta | Ampere | Ampere | Ampere |
| Tensor Core | 없음 | **48** | 64 | 1024 | 2048 | 4096 |
| NVDLA | 없음 | **2x** (14+14TOPS) | 2x | 없음 | 없음 | 없음 |
| AI 성능 | 0.5 TOPS | **21 TOPS** | 32 TOPS | 40 TOPS | 100 TOPS | 275 TOPS |
| RAM | 4GB LPDDR4 | **8GB LPDDR4x** | 32GB LPDDR4x | 8GB LPDDR5 | 16GB LPDDR5 | 64GB LPDDR5 |
| 전력 | 5~10W | **10~20W** | 10~30W | 7~15W | 10~25W | 15~60W |
| 가격대 | $129 | **$399** | $1,099 | $199 | $499 | $1,999 |

---

## 3. Xavier NX 상세 (본 교육 과정 기준)

### 사양

| 항목 | 사양 |
|------|------|
| **SoC** | NVIDIA Tegra Xavier (T194) |
| **CPU** | 6-Core NVIDIA Carmel ARM v8.2 64-bit (L1: 512KB, L2: 2MB) |
| **GPU** | 384-Core NVIDIA Volta GPU (Max Clock: 1100 MHz) |
| **Tensor Cores** | 48개 (FP16/INT8 추론 가속) |
| **NVDLA** | 2x NVDLA 엔진 (각 5+5 TOPS, 총 ~20 TOPS) |
| **메모리** | 8GB LPDDR4x (51.2GB/s) |
| **저장소** | microSD (권장: 128GB UHS-1 이상), NVMe (M.2 Key M) |
| **비디오 인코더** | 2x 4K60 H.265/H.264 |
| **비디오 디코더** | 2x 4K60 H.265/H.264 |
| **CSI 카메라** | 2-lane x 2 (CIL_LANE0~3) |
| **USB** | USB 3.0 Type-A x 4, USB-C (DP 포함) |
| **PCIe** | M.2 Key M (PCIe x4) |
| **네트워크** | Gigabit Ethernet, Wi-Fi (옵션 M.2 Key E) |
| **GPIO** | 40-pin 헤더 (Jetson 표준 핀맵) |
| **전력** | 10W / 15W / 20W 모드 (선택 가능) |
| **폼팩터** | 103mm x 90.5mm (Developer Kit) |

### 전력 모드별 성능

| 모드 | 전력 | GPU 클럭 | CPU 클럭 | AI 성능 |
|------|:----:|:--------:|:--------:|:-------:|
| 10W (2-core) | 10W | 520 MHz | 1.2 GHz | ~10 TOPS |
| 15W (4-core) | 15W | 800 MHz | 1.4 GHz | ~15 TOPS |
| **20W (6-core)** | **20W** | **1100 MHz** | **1.9 GHz** | **~21 TOPS** |

> 교육 과정에서는 `sudo nvpmodel -m 0` (20W MAXN 모드) 권장

### Xavier NX vs Orin Nano 비교표

| 항목 | Xavier NX | Orin Nano (8GB) | 차이 |
|------|:--------:|:--------------:|:----:|
| **AI 성능** | 21 TOPS | 40 TOPS | Orin 1.9x |
| **Tensor Core** | 48 (Gen2) | 1024 (Gen3) | Orin 압도적 |
| **GPU Arch** | Volta | Ampere | Orin 최신 |
| **CUDA Cores** | 384 | 1024 | Orin 2.7x |
| **RAM** | 8GB LPDDR4x | 8GB LPDDR5 | Orin 대역폭 우위 |
| **NVDLA** | 2개 탑재 | 없음 | Xavier 강점 |
| **전력** | 10~20W | 7~15W | Xavier 다소 높음 |
| **가격** | ~$399 | ~$199 | Orin 저렴 |

### Xavier NX의 강점
- **NVDLA 탑재**: GPU 부담 없이 AI 추론을 전담하는 하드웨어 가속기
- **Tensor Core**: 48개 Volta Tensor Core로 FP16/INT8 연산 가속
- **성숙한 생태계**: JetPack 4.x/5.x 모두 지원, 검증된 안정성
- **CAN FD**: 차량용 통신(CAN) 네이티브 지원 (Orin Nano는 미지원)

---

## 4. Jetson 보드 식별 방법

```bash
# 1. 보드 모델 확인
cat /proc/device-tree/model
# → "NVIDIA Jetson Xavier NX Developer Kit"

# 2. JetPack/L4T 버전 확인
cat /etc/nv_tegra_release
# → R32 (release), REVISION: 6.1, GCID: 27863751, ...

# 3. CPU 정보
lscpu | grep "Model name"

# 4. GPU 정보
sudo tegrastats

# 5. 메모리 정보
grep MemTotal /proc/meminfo

# 6. CUDA 버전
nvcc --version

# 7. TensorRT 버전
dpkg -l | grep tensorrt

# 8. 전력 모드 확인
sudo nvpmodel -q
```

---

## 5. 모델 선택 가이드

| 사용 목적 | 추천 모델 | 사유 |
|-----------|----------|------|
| AI 교육/입문 | **Jetson Nano** | 저렴, 기본 AI 학습 가능 |
| AI+로봇+ROS | **Xavier NX** | NVDLA+CAN+성숙한 ROS 지원 |
| 산업용 비전 | **Orin NX** | 고성능, Ampere GPU |
| 자율주행 연구 | **AGX Orin** | 최고 성능, 275 TOPS |
| 멀티 카메라 | **AGX Xavier** | 고성능, 풍부한 I/O |

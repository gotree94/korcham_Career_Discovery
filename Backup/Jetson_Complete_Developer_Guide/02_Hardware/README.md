# 02. Jetson Hardware Architecture

## 1. CPU — NVIDIA Carmel (Xavier NX 기준)

### 아키텍처 개요

| 항목 | 사양 |
|------|------|
| 코어 | 6x NVIDIA Carmel ARM v8.2 64-bit |
| L1 캐시 | 512KB (64KB/core: 32KB I + 32KB D) |
| L2 캐시 | 2MB (공유) |
| 클럭 | 최대 1.9 GHz (20W 모드 기준) |
| 명령어셋 | ARMv8.2-A (AArch64) |
| 특징 | 동적 전력 관리, Out-of-Order 실행 |

### CPU 성능 측정

```bash
# CPU 정보 확인
lscpu

# CPU 스트레스 테스트
sudo apt install stress
stress --cpu 6 --timeout 30

# 실시간 CPU 클럭 확인
sudo cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
```

### AArch64 vs x86_64 차이

| 항목 | ARM64 (aarch64) | x86_64 |
|------|:--------------:|:------:|
| 명령어 길이 | 고정 4바이트 | 가변 길이 |
| 전력 효율 | 우수 | 상대적 낮음 |
| 소프트웨어 생태계 | 성장 중 | 성숙 |
| Jetson 적용 | O | X |

> **주의**: aarch64는 amd64 패키지와 호환되지 않습니다. 반드시 `arm64` 또는 `aarch64`용 패키지를 설치해야 합니다.

---

## 2. GPU — NVIDIA Volta (GV10B)

### 사양

| 항목 | 값 |
|------|-----|
| GPU 아키텍처 | NVIDIA Volta (GV10B) |
| CUDA 코어 | 384개 |
| Tensor Core | 48개 (2세대) |
| SM(Streaming Multiprocessor) | 6개 |
| GPU 클럭 | 최대 1.1 GHz |
| FP32 성능 | 845 GFLOPS |
| FP16 성능 | 1.69 TFLOPS |
| INT8 성능 | 3.38 TOPS |

### GPU 활용 확인

```bash
# 실시간 GPU 상태 모니터링
sudo tegrastats

# 출력 예시:
# RAM 3345/7851MB (lfb 4097MB) SWAP 0/10036MB (cached 0MB)
# CPU [8%@1400, ...] EMC_FREQ 50% GR3D_FREQ 54%
# AO 42C CPU 44.5C GPU 43.5C ... VDD_IN 2324/2324

# GR3D_FREQ = GPU 사용률
# GPU 온도 확인 (43.5C 위 예시)

# NVIDIA-SMI (JetPack 4.6에서는 미지원, 대신 tegrastats)
```

### GPU 메모리 계층

```
GPU 칩
  ├── L1 캐시 / Shared Memory (128KB/SM)
  ├── L2 캐시 (512KB)
  └── GPU 메모리 (통합 메모리 아키텍처)
        └── 시스템 RAM 8GB와 공유 (UMA: Unified Memory Architecture)
```

> **특징**: Jetson은 CPU-GPU가 물리적 메모리를 공유 (UMA). 별도 VRAM 없음.
> 일반 GPU (RTX 3090)와의 가장 큰 차이점.

---

## 3. NVDLA (NVIDIA Deep Learning Accelerator)

### 개요

NVDLA는 **GPU와 독립적으로 동작하는 AI 추론 전용 하드웨어**입니다.

| 항목 | 사양 |
|------|------|
| 개수 | 2개 (NVDLA0, NVDLA1) |
| 성능 | 각 5+5 TOPS (INT8, Convolution 기준) |
| 총 성능 | ~20 TOPS (GPU+CUDA 병행 시 21 TOPS) |
| 전력 효율 | GPU 대비 3~5배 효율적 (추론 전용) |
| 지원 연산 | Convolution, Activation, Pooling, FC |

### NVDLA 작동 방식

```
입력 이미지
    ↓
NVDLA0 (Conv Layer 1~3)  ← GPU는 다른 작업 가능
NVDLA1 (Conv Layer 4~6)
    ↓
결과 (분류/검출)
```

### NVDLA 활용 확인

```bash
# NVDLA 디바이스 확인
ls /dev/nvhost-nvdla*
# → /dev/nvhost-nvdla0, /dev/nvhost-nvdla1

# TensorRT가 NVDLA를 사용하는지 확인
# (TensorRT 로그에 "NVDLA" 포함 시 사용 중)
```

> **TensorRT에서 NVDLA 사용 설정**: `trtexec --useDLA --dlaCore=0 ...`

### Xavier NX만의 차별점

NVDLA는 **Xavier NX와 AGX Xavier에만 존재**합니다.
Orin Nano/Orin NX/AGX Orin에는 NVDLA가 없습니다 (대신 Tensor Core가 대체).

---

## 4. 메모리 시스템

### 메모리 계층

| 계층 | 크기 | 대역폭 | 레이턴시 |
|------|:----:|:------:|:--------:|
| 레지스터 | 수천 바이트 | 10TB/s+ | 1 cycle |
| L1 캐시 (CPU) | 32KB I + 32KB D / core | ~1TB/s | 3~5 cycles |
| L2 캐시 (CPU) | 2MB (공유) | ~500GB/s | 10~20 cycles |
| L1 캐시 (GPU) | 128KB / SM | ~2TB/s | 5~10 cycles |
| L2 캐시 (GPU) | 512KB | ~500GB/s | 20~40 cycles |
| **LPDDR4x** (시스템 RAM) | **8GB** | **51.2GB/s** | **100~200 cycles** |

### 메모리 확인

```bash
# 전체 메모리
free -h
# → total 7.6G / used 2.0G / free 4.7G / available 5.4G

# 상세 메모리 정보
cat /proc/meminfo | grep -E "MemTotal|MemFree|Cached|SwapTotal"

# GPU 메모리 확인
sudo tegrastats | grep RAM

# Swap 확인
swapon --show
```

### Swap 설정 (메모리 부족 시)

```bash
# 8GB Swap 파일 생성
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 적용
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 5. CSI (Camera Serial Interface)

### CSI 포트 (Xavier NX)

| 인터페이스 | 핀 | 최대 해상도 |
|-----------|:---:|:----------:|
| CSI Lane 0~1 | 2-lane | 1920x1080 @ 60fps |
| CSI Lane 2~3 | 2-lane | 1920x1080 @ 60fps |

### 지원 카메라

| 카메라 | 인터페이스 | 해상도 | Jetson 호환 |
|--------|:---------:|:------:|:----------:|
| IMX219 | CSI 2-lane | 3280x2464 | O |
| IMX477 | CSI 2-lane | 4056x3040 | O |
| OV9281 | CSI 2-lane | 1280x800 | O |
| USB 카메라 | USB 3.0 | 다양 | O (v4l2) |

> 자세한 내용은 `09_Camera` 섹션 참조

---

## 6. PCIe

### PCIe 구성 (Xavier NX)

| 항목 | 사양 |
|------|------|
| 컨트롤러 | 1x PCIe Gen3 |
| 레인 | x4 (M.2 Key M 슬롯) |
| 대역폭 | ~4 GB/s (Gen3 x4) |
| 용도 | NVMe SSD, AI 가속기, 캡처 카드 |

### NVMe SSD 장착 시 성능

```bash
# NVMe SSD 속도 테스트
sudo apt install hdparm
sudo hdparm -t /dev/nvme0n1

# 일반적인 속도: 1500~3500 MB/s (SSD 사양에 따라 상이)
```

---

## 7. 전원 관리

### 전력 모드

```bash
# 현재 전력 모드 확인
sudo nvpmodel -q

# 사용 가능한 모드 목록
sudo nvpmodel --list

# 20W MAXN 모드 (최대 성능)
sudo nvpmodel -m 0

# 15W 모드
sudo nvpmodel -m 1

# 10W 모드
sudo nvpmodel -m 2

# 부팅 시 자동 적용
sudo systemctl enable nvpmodel
```

### 전력 소비 확인

```bash
sudo tegrastats | grep VDD_IN
# → VDD_IN 2324/2324 (현재/최대 전력 mW)
```

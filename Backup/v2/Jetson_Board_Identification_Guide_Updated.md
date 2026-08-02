# NVIDIA Jetson 보드 모델 확인 방법

(기존 문서 내용 요약)

이 문서는 Jetson 보드 모델 확인, JetPack/L4T 확인, CPU/GPU/메모리 확인,
jetson_release 사용법, 시스템 정보 확인 스크립트를 포함합니다.

------------------------------------------------------------------------

# 사용자 보드 분석 결과

## 모델 확인

``` bash
cat /proc/device-tree/model
```

출력

``` text
NVIDIA Jetson Xavier NX Developer Kit
```

### 분석

-   보드: **NVIDIA Jetson Xavier NX Developer Kit**
-   SoC: NVIDIA Tegra Xavier (T194)
-   CPU: 6-Core NVIDIA Carmel ARMv8
-   GPU: 384-Core Volta GPU + 48 Tensor Cores

------------------------------------------------------------------------

## JetPack / L4T

``` bash
cat /etc/nv_tegra_release
```

출력

``` text
# R32(release), REVISION: 6.1, GCID: 27863751, BOARD: t186ref, EABI:aarch64
```

  항목       값
  ---------- -----------
  L4T        32.6.1
  JetPack    4.6
  Ubuntu     18.04 LTS
  CUDA       10.2
  TensorRT   8.x

현재는 JetPack 4.6이 설치되어 있으며, 최신 기능이 필요하다면 지원 가능한
최신 JetPack으로 업그레이드를 고려할 수 있습니다.

------------------------------------------------------------------------

## 메모리

사용자가 제공한 `free -h` 결과는 총 메모리 **76G**로 보였으나, 일반적인
Xavier NX의 사양과 일치하지 않습니다.

다음 명령으로 실제 메모리를 다시 확인하는 것을 권장합니다.

``` bash
grep MemTotal /proc/meminfo
```

또는

``` bash
free -h
```

`7.6G`를 `76G`로 잘못 읽은 것은 아닌지도 함께 확인하는 것이 좋습니다.

------------------------------------------------------------------------

# 종합 분석

  항목       결과
  ---------- ------------------------------------------------
  보드       NVIDIA Jetson Xavier NX Developer Kit
  SoC        NVIDIA Tegra Xavier (T194)
  CPU        6-Core NVIDIA Carmel
  GPU        384-Core Volta + 48 Tensor Cores
  JetPack    4.6
  L4T        32.6.1
  Ubuntu     18.04
  CUDA       10.2
  TensorRT   8.x
  메모리     추가 확인 필요 (`grep MemTotal /proc/meminfo`)

## 추가 확인 권장 명령

``` bash
lscpu
grep MemTotal /proc/meminfo
lsblk
sudo tegrastats
nvcc --version
dpkg -l | grep nvinfer
```

# NVIDIA Jetson 보드 모델 확인 방법

Jetson 보드에서는 리눅스 명령으로 **정확한 모델명(Orin Nano, Xavier NX,
Nano, AGX Orin 등)** 과 **JetPack/L4T 버전**, **모듈 정보**까지 확인할
수 있습니다.

## 1. L4T/JetPack 정보

``` bash
cat /etc/nv_tegra_release
```

예시:

``` text
# R36 (release), REVISION: 3.0, GCID: xxxxx, BOARD: t234ref, EABI: aarch64
```

-   R35.x → JetPack 5
-   R36.x → JetPack 6

------------------------------------------------------------------------

## 2. Jetson 모델명 확인 (가장 추천)

``` bash
cat /proc/device-tree/model
```

예시:

``` text
NVIDIA Jetson Orin Nano Developer Kit
```

------------------------------------------------------------------------

## 3. 하드웨어 정보

``` bash
sudo dmesg | grep -i "DMI"
```

또는

``` bash
sudo dmesg | grep -i jetson
```

------------------------------------------------------------------------

## 4. CPU 확인

``` bash
cat /proc/cpuinfo
```

또는

``` bash
lscpu
```

------------------------------------------------------------------------

## 5. 메모리 확인

``` bash
free -h
```

또는

``` bash
cat /proc/meminfo
```

------------------------------------------------------------------------

## 6. GPU 확인

``` bash
nvidia-smi
```

> 일부 Jetson Nano에서는 지원되지 않을 수 있습니다.

------------------------------------------------------------------------

## 7. JetPack 버전 확인

``` bash
dpkg-query --show nvidia-l4t-core
```

또는

``` bash
apt list --installed | grep nvidia-l4t-core
```

------------------------------------------------------------------------

## 8. jetson_release 사용

설치:

``` bash
sudo apt install python3-pip
git clone https://github.com/rbonghi/jetson_stats.git
cd jetson_stats
sudo pip3 install -U .
```

실행:

``` bash
jetson_release
```

------------------------------------------------------------------------

## 9. EEPROM/호환 정보

``` bash
sudo i2cdetect -y -r 0
```

또는

``` bash
tr '\0' '\n' < /sys/firmware/devicetree/base/compatible
```

예시:

``` text
nvidia,p3768-0000+p3767-0005
```

------------------------------------------------------------------------

## 10. 주요 정보 한 번에 확인

``` bash
echo "===== MODEL ====="
cat /proc/device-tree/model

echo
echo "===== COMPATIBLE ====="
tr '\0' '\n' < /sys/firmware/devicetree/base/compatible

echo
echo "===== L4T ====="
cat /etc/nv_tegra_release

echo
echo "===== CPU ====="
lscpu

echo
echo "===== MEMORY ====="
free -h

echo
echo "===== CUDA ====="
nvcc --version 2>/dev/null

echo
echo "===== TENSORRT ====="
dpkg -l | grep nvinfer
```

## 결론

가장 정확하게 보드를 식별하려면 아래 두 명령이면 충분합니다.

``` bash
cat /proc/device-tree/model
```

``` bash
tr '\0' '\n' < /sys/firmware/devicetree/base/compatible
```

이 결과를 확인하면 Jetson 모델, JetPack, CUDA 지원 여부 등을 정확하게
판단할 수 있습니다.

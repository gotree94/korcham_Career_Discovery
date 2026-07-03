# 05. Linux on Jetson

## 1. Ubuntu on Jetson

### 기본 정보

| 항목 | 현재 환경 |
|------|----------|
| OS | Ubuntu 18.04.5 LTS (Bionic Beaver) |
| Kernel | Linux aarch64 |
| Architecture | ARM 64-bit (aarch64) |
| 기본 Shell | Bash |

### 패키지 관리

```bash
# apt (APT: Advanced Package Tool)
sudo apt update              # 패키지 목록 갱신
sudo apt upgrade             # 모든 패키지 업그레이드
sudo apt install <패키지명>  # 패키지 설치
sudo apt remove <패키지명>   # 패키지 제거
sudo apt search <키워드>     # 패키지 검색

# pip (Python 패키지)
pip3 install <패키지명>      # Python 패키지 설치
pip3 list                    # 설치된 패키지 목록
pip3 freeze > requirements.txt  # 현재 환경 저장
```

### aarch64 패키지 호환성

| 패키지 타입 | 설치 가능 | 비고 |
|:-----------:|:---------:|------|
| `apt` (공식 저장소) | O | ARM64 패키지 자동 설치 |
| `pip3` (순수 Python) | O | 아키텍처 무관 |
| `pip3` (C 확장 포함) | △ | 사전 컴파일된 wheel 필요 |
| `.deb` (arm64) | O | `dpkg -i`로 설치 |
| `.deb` (amd64) | X | 에뮬레이션 없이 실행 불가 |
| Snap | △ | 일부 제한적 지원 |
| Docker (arm64 이미지) | O | `docker run --platform linux/arm64` |

---

## 2. Shell 기본 명령어

### 파일/디렉토리 조작

```bash
pwd                     # 현재 위치 출력
ls -la                  # 파일 목록 (자세히, 숨김 포함)
cd ~                    # 홈 디렉토리로 이동
mkdir my_project        # 디렉토리 생성
cp file1 file2          # 파일 복사
mv file1 dir1/          # 파일 이동/이름 변경
rm file.txt             # 파일 삭제
rm -rf dir/             # 디렉토리 강제 삭제
find . -name "*.py"     # 파일 검색
```

### 파일 내용 보기

```bash
cat file.txt            # 파일 내용 출력
head -20 file.txt       # 앞 20줄
tail -f log.txt         # 실시간 로그 모니터링
less file.txt           # 페이지 단위 보기 (q: 종료)
grep "ERROR" log.txt    # 패턴 검색
wc -l file.txt          # 줄 수 세기
```

### 권한 관리

```bash
chmod +x script.sh      # 실행 권한 추가
chmod 755 script.sh     # rwxr-xr-x
chown user:group file   # 소유자 변경
sudo !!                 # 직전 명령을 sudo로 재실행
```

### 프로세스/시스템

```bash
ps aux                  # 모든 프로세스 목록
top                     # 실시간 프로세스 모니터링 (종료: q)
htop                    # 향상된 top (설치 필요)
kill -9 PID             # 프로세스 강제 종료
df -h                   # 디스크 사용량
du -sh *                # 현재 디렉토리 용량
free -h                 # 메모리 사용량
uname -a                # 시스템 정보
```

---

## 3. 파일 시스템 구조

| 경로 | 용도 |
|------|------|
| `/` | 루트 파일 시스템 |
| `/home/` | 사용자 홈 디렉토리 |
| `/etc/` | 시스템 설정 파일 |
| `/var/log/` | 시스템 로그 |
| `/opt/` | 추가 소프트웨어 |
| `/usr/local/` | 사용자 설치 프로그램 |
| `/dev/` | 디바이스 파일 (GPIO, I2C 등) |
| `/proc/` | 프로세스/커널 정보 (가상 파일시스템) |
| `/sys/` | 하드웨어 정보 (가상 파일시스템) |

### Jetson 특수 경로

```bash
# NVIDIA 관련
/proc/device-tree/model   # 보드 모델명
/etc/nv_tegra_release     # L4T 버전

# Jetson 클럭/전력
/sys/devices/system/cpu/cpu*/cpufreq/  # CPU 클럭 정보
/sys/kernel/debug/tegra_fuse/          # 하드웨어 퓨즈 정보

# NVDLA
/dev/nvhost-nvdla0       # NVDLA 엔진 0
/dev/nvhost-nvdla1       # NVDLA 엔진 1

# 카메라
/dev/video0              # CSI 카메라
/dev/video1              # USB 카메라
```

---

## 4. 텍스트 에디터 (nano)

```bash
# nano 기본 사용법
nano file.txt

# 단축키
Ctrl+O   : 저장
Ctrl+X   : 종료
Ctrl+K   : 한 줄 잘라내기
Ctrl+U   : 붙여넣기
Ctrl+W   : 검색
Ctrl+G   : 도움말
```

> 교육용으로 nano 추천. vim/emacs는 선택사항.

---

## 5. 시스템 모니터링 (Jetson 특화)

```bash
# ★ 가장 중요한 명령어: tegrastats
sudo tegrastats

# 출력 해석
# RAM 3345/7851MB    → 사용중/전체 RAM
# SWAP 0/10036MB     → 사용중/전체 SWAP
# CPU [8%@1400,...]  → 각 CPU 코어 사용률/클럭
# GR3D_FREQ 54%      → GPU 사용률
# AO 42C CPU 44.5C GPU 43.5C → 온도
# VDD_IN 2324/2324   → 현재/최대 전력 (mW)

# 간단한 시스템 정보
uname -a
lscpu
cat /proc/meminfo | grep MemTotal
```

---

## 6. 실습: 터미널 생존 게임

```bash
# 실습 1: 센서 데이터 수집 파이프라인
mkdir -p ~/jetson_lab && cd ~/jetson_lab
nano collect_data.sh
```

```bash
#!/bin/bash
# collect_data.sh
echo "Timestamp,GPU_Temp,CPU_Temp,RAM_Used" > sensor_log.csv
for i in {1..10}; do
    TEMP=$(sudo tegrastats | grep -oP 'GPU \K[0-9.]+(?=C)')
    TIMESTAMP=$(date +%H:%M:%S)
    echo "$TIMESTAMP,$TEMP" >> sensor_log.csv
    sleep 1
done
cat sensor_log.csv
```

```bash
chmod +x collect_data.sh
./collect_data.sh

# 결과 확인
cat sensor_log.csv
grep "45" sensor_log.csv  # 45도 포함 라인 검색
```

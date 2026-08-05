# 02. Linux 기초

## 학습 목표

- Ubuntu(L4T) 파일 시스템 구조 이해
- 터미널 기본 명령어 숙달
- 패키지 관리 및 시스템 정보 확인

## 사전 준비

- [ ] 01장 완료 (Jetson 부팅, SSH 접속)

---

## 1. 파일 시스템 구조

| 경로 | 용도 |
| ---- | ---- |
| `/` | 루트 디렉터리 |
| `/home` | 사용자 홈 디렉터리 |
| `/etc` | 시스템 설정 파일 |
| `/var` | 로그, 가변 데이터 |
| `/usr` | 설치된 응용 프로그램 |
| `/dev` | 하드웨어 디바이스 파일 |

> ※ 주요 디렉터리를 실제로 탐색하며 설명하는 자료를 추가하세요.

---

## 2. 기본 명령어

### 파일/디렉터리

```bash
$ pwd            # 현재 경로
$ ls -la         # 파일 목록 (숨김 포함)
$ cd ~           # 홈 이동
$ mkdir test     # 디렉터리 생성
$ cp / mv / rm   # 복사 / 이동 / 삭제
```

### 권한 관리

```bash
$ chmod 755 file
$ chown user:group file
$ sudo  # 관리자 권한 실행
```

### 프로세스/네트워크

```bash
$ top / htop     # 프로세스 확인
$ ps aux         # 전체 프로세스
$ ifconfig / ip addr
$ ping <host>
```

---

## 3. 패키지 관리 (APT)

```bash
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install <패키지>
$ sudo apt remove <패키지>
```

---

## 4. 텍스트 에디터

```bash
$ nano file.txt      # 초보자용
$ vim file.txt       # 고급 에디터
$ gedit file.txt     # GUI 에디터
```

---

## 실습

1. `/` 경로에서 주요 디렉터리 탐색
2. 디렉터리 생성 → 파일 작성 → 복사/이동/삭제
3. `apt`로 패키지 설치
4. CPU/GPU 사용률 확인 (`top`, `nvidia-smi`)

## 정리 및 체크리스트

- [ ] 파일 시스템 구조 설명 가능
- [ ] 파일/권한/프로세스 명령어 사용
- [ ] apt로 패키지 설치/삭제
- [ ] `nvidia-smi`로 GPU 확인

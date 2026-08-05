# NVIDIA Jetson Xavier NX 실습 과정

본 과정은 **NVIDIA Jetson Xavier NX** 보드를 활용하여 임베디드 Linux 환경,
센서/카메라 인터페이스, **GPU 기반 AI 추론(TensorRT)**, 그리고 **ROS 2 기반
로봇 통합**까지 실습하는 교육 커리큘럼입니다.

- 대상 보드: NVIDIA Jetson Xavier NX (Developer Kit)
- 호스트 PC: Windows + VirtualBox(Ubuntu) 연동
- 소프트웨어: JetPack SDK, TensorRT, ROS 2 (Humble)
- 참고: 기존 옴니휠 로봇 프로젝트(`Jetson_Xavier_NX_Modul.FCStd`)와 연계

---

## 초기 설정

![](img/001.png)

![](img/002.png)

![](img/003.png)

![](img/004.png)

![](img/005.png)

![](img/006.png)

![](img/007.png)

![](img/008.png)

![](img/009.png)

---

## 📚 커리큘럼 구성

| 순서 | 파일 | 내용 |
| ---- | ---- | ---- |
| 01 | [01_보드_소개_및_환경설정.md](01_보드_소개_및_환경설정.md) | Jetson Xavier NX 하드웨어 소개, JetPack 설치, 부팅 |
| 02 | [02_Linux_기초.md](02_Linux_기초.md) | Ubuntu Linux 기초, 터미널 명령어, 파일 시스템 |
| 03 | [03_GPIO_및_주변장치_제어.md](03_GPIO_및_주변장치_제어.md) | Jetson GPIO, I2C/UART/SPI, LED·버튼 제어 |
| 04 | [04_카메라_및_센서_인터페이스.md](04_카메라_및_센서_인터페이스.md) | CSI/USB 카메라, 센서 데이터 수집 |
| 05 | [05_AI_추론_TensorRT.md](05_AI_추론_TensorRT.md) | GPU 가속 AI 추론, TensorRT, YOLO 실습 |
| 06 | [06_ROS2_로봇_통합.md](06_ROS2_로봇_통합.md) | ROS 2 설치, 토픽 통신, 로봇 통합 |
| 07 | [07_종합_프로젝트.md](07_종합_프로젝트.md) | 자율주행/객체인식 통합 프로젝트 |

> 📌 초보자라면 **01 → 02 → 03 → 04** 순서로 기반을 다진 뒤,
> **05 → 06 → 07** 순서로 AI·로봇 통합 실습을 진행하시기 바랍니다.

---

## 🛠 필수 설치 항목

| 구분 | 항목 | 버전/방식 |
| ---- | ---- | --------- |
| 호스트 | NVIDIA SDK Manager | 최신 (Windows) |
| 보드 OS | JetPack SDK (L4T) | 5.x (Ubuntu 20.04 기반) |
| 호스트 VM | VirtualBox + Ubuntu | 22.04 |
| AI 프레임워크 | TensorRT / CUDA | JetPack 포함 |
| 로봇 미들웨어 | ROS 2 | Humble |

---

## 🚀 학습 목표 (최종 산출물)

1. Jetson Xavier NX 보드 부팅 및 개발 환경 구축
2. Linux 터미널 · 시스템 관리 능력 습득
3. GPIO·I2C·UART 기반 주변장치 제어
4. 카메라/센서 데이터 실시간 수집
5. TensorRT를 활용한 GPU AI 추론 (객체 인식)
6. ROS 2 노드 통신과 로봇 제어 연동
7. AI + 로봇 통합 데모 프로젝트 완성

---

## ✅ 학습 완료 체크리스트

- [ ] JetPack 설치 및 Jetson 부팅 확인
- [ ] SSH 원격 접속으로 호스트 PC와 통신
- [ ] 터미널 기본 명령어 자유롭게 사용
- [ ] GPIO로 LED/버튼 제어
- [ ] 카메라 영상 캡처 및 표시
- [ ] TensorRT로 YOLO 객체 인식 실행
- [ ] ROS 2 노드 간 토픽 통신
- [ ] 통합 데모 (객체 인식 + 로봇 제어) 완성

---

## 📝 참고 자료

- NVIDIA Jetson 공식 문서: https://docs.nvidia.com/jetson/
- JetPack SDK: https://developer.nvidia.com/embedded/jetpack
- ROS 2 Humble 문서: https://docs.ros.org/en/humble/

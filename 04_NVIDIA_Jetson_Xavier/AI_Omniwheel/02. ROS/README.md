# 02. ROS — ROS 1 기초 통신 실습

본 과정은 Jetson Xavier NX에 설치된 **ROS 1(Melodic)** 환경에서 Jupyter Notebook으로
노드 간 통신(Topic, Service, Message)을 실습하는 교육 자료입니다.

- ROS 버전: **ROS Melodic** (Ubuntu 18.04 기반, `installROSXavier` 스크립트로 설치)
- 실행 방식: Jupyter Notebook (rospy 직접 호출)
- 의존 패키지: `omniwheel_project` (커스텀 msg/srv) → `catkin_ws` 빌드 필요
- 관련 작업공간: `AI_Omniwheel\catkin_ws`

---

## 📚 커리큘럼 구성

| 순서 | 파일 | 내용 | 개념 |
| ---- | ---- | ---- | ---- |
| 01 | [1-1. Simple publish.md](1-1.%20Simple%20publish.md) | 문자열 토픽 발행 | Publisher, `rospy.Rate` |
| 02 | [1-2. Simple Subscribe.md](1-2.%20Simple%20Subscribe.md) | 문자열 토픽 구독 | Subscriber, 콜백 |
| 03 | [2-1. Simple Service.md](2-1.%20Simple%20Service.md) | 서비스 서버 | Service, srv, 핸들러 |
| 04 | [2-2. Simple Client.md](2-2.%20Simple%20Client.md) | 서비스 클라이언트 | ServiceProxy, 요청/응답 |
| 05 | [3-1. Message Publish.md](3-1.%20Message%20Publish.md) | 커스텀 메시지 발행 | `.msg`, 사용자 정의 메시지 |
| 06 | [3-2. Message Subscribe.md](3-2.%20Message%20Subscribe.md) | 커스텀 메시지 구독 | 커스텀 메시지 수신 |

> 📌 01 → 02 (Topic) → 03 → 04 (Service) → 05 → 06 (Message) 순서로 학습합니다.
> 모든 실습은 **동일 노트북 안에서 발행/구독이 함께 실행**되지 않으므로,
> **터미널에서 발행 노드를 먼저 띄우고 노트북에서 수신**하는 방식으로 검증합니다.

---

## 🛠 공통 사전 준비

### 1. ROS 설치 (이미 설치된 경우 생략)

```bash
# installROSXavier 폴더에서
$ ./installROS.sh -p ros-melodic-desktop-full
$ ./setupCatkinWorkspace.sh
```

### 2. catkin_ws 빌드 (커스텀 msg/srv 생성)

```bash
$ cd ~/catkin_ws          # 본 자료: AI_Omniwheel\catkin_ws
$ source /opt/ros/melodic/setup.bash
$ catkin_make
$ source devel/setup.bash
```

> Service(2-1, 2-2)와 Message(3-1, 3-2)는 `omniwheel_project` 패키지의
> `AddTwoInts.srv` / `Numb.msg` 를 사용하므로 **반드시 빌드 완료 후** 진행해야 합니다.

### 3. ROS Master 실행

모든 노드는 마스터(roscore)가 있어야 동작합니다.

```bash
$ roscore          # 별도 터미널에서 실행 (계속 떠 있어야 함)
```

### 4. Jupyter 환경 준비

```bash
$ source /opt/ros/melodic/setup.bash
$ source ~/catkin_ws/devel/setup.bash
$ jupyter notebook    # 또는 jupyter lab
```

> ⚠️ Jupyter 커널이 ROS 환경 변수(`ROS_MASTER_URI`, `PYTHONPATH`)를 물려받도록
> **터미널에서 source 후 jupyter를 실행**해야 합니다. 그렇지 않으면
> `from omniwheel_project.srv import ...` import 오류가 발생합니다.

---

## 🔄 실습 실행 순서 요약

| 단계 | 내용 | 실행 위치 |
| ---- | ---- | --------- |
| 1 | `roscore` 실행 | 터미널 1 |
| 2 | `catkin_ws` 빌드 & source | 터미널 2 |
| 3 | Jupyter 실행 | 터미널 2 |
| 4 | 노트북에서 발행/서비스 노드 실행 | 노트북 |
| 5 | `rostopic echo` / `rqt_graph`로 확인 | 터미널 2 |

---

## 📝 참고

- 커스텀 메시지 정의: `catkin_ws/src/omniwheel_project/msg/Numb.msg` → `int64 number`
- 커스텀 서비스 정의: `catkin_ws/src/omniwheel_project/srv/AddTwoInts.srv`
  ```text
  int64 a
  int64 b
  ---
  int64 sum
  ```
- 확장 실습(고급): `catkin_ws/src/omniwheel_project/launch/` 의
  `omni_slam.launch`, `omni_navigation.launch` 및
  `scripts/ROS_Examples/` 의 4~6번(launch 분석, SLAM, Navigation) 자료

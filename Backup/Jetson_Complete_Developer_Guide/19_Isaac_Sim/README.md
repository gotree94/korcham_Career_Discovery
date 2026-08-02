# 19. Isaac Sim

## 1. Isaac Sim 개요

NVIDIA Isaac Sim은 로봇 시뮬레이션을 위한 Omniverse 기반 플랫폼입니다.

| 항목 | 설명 |
|:----|:------|
| 엔진 | NVIDIA Omniverse (RTX 실시간 렌더링) |
| ROS2 Bridge | 네이티브 ROS2 토픽 연동 |
| 물리 엔진 | PhysX 5.x |
| 센서 | 카메라, LiDAR, IMU, Contact 등 |
| Digital Twin | 실제 로봇과 동일한 가상 모델 |

## 2. 시스템 요구사항

| 요구사항 | 최소 | 권장 |
|:---------|:----|:----|
| GPU | RTX 2060 | RTX 4080+ |
| RAM | 32GB | 64GB |
| 저장소 | 50GB | 100GB (SSD) |
| OS | Ubuntu 20.04+ | Ubuntu 22.04 |
| **Jetson 실행** | **불가 (Host PC 필요)** | **데스크탑/서버에서 실행** |

> Isaac Sim은 **Jetson에서 직접 실행할 수 없습니다**. Host PC(데스크탑)에서 시뮬레이션하고 Jetson 로봇과 ROS2로 통신합니다.

## 3. ROS2 Bridge 구성

```
[Isaac Sim (Host PC)] ←→ ROS2 Topics ←→ [Jetson Robot (실제)]
        │                                       │
        │   /camera/image                         │
        │   /scan (LiDAR)                         │
        │   /cmd_vel                              │
        │   /tf                                   │
        └───────────────────────────────────────┘
```

## 4. Isaac Sim 설치

```bash
# Host PC (Ubuntu 20.04/22.04)에서
# NVIDIA Omniverse Launcher 다운로드
# → Isaac Sim 2023.x 설치

# ROS2 Bridge 활성화
./isaac_sim.sh --enable ros2-bridge
```

## 5. 활용 예: Digital Twin

```
1. Isaac Sim에서 로봇 모델 로드 (Jetson AGV)
2. 실제 Jetson과 ROS2 통신 연결
3. 시뮬레이션된 센서 데이터로 AI 모델 학습
4. 학습된 모델을 실제 Jetson에 배포
5. 실제 로봇 주행 데이터를 시뮬레이션에 반영
```

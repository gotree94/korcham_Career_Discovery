# 18. Isaac ROS

## 1. Isaac ROS 개요

NVIDIA Isaac ROS는 ROS2 기반의 로봇 개발 가속 패키지 모음입니다.

| 패키지 | 기능 | GPU 가속 |
|:------:|:----:|:--------:|
| Isaac ROS DNN Stereo Depth | 딥러닝 기반 스테레오 깊이 추정 | O |
| Isaac ROS Visual SLAM | 시각적 SLAM | O |
| Isaac ROS AprilTag | AprilTag 마커 검출 | O |
| Isaac ROS Pose Estimation | FoundationPose 기반 6D 자세 추정 | O |
| Isaac ROS Image Pipeline | 이미지 처리 파이프라인 | O |
| Isaac ROS Object Detection | 객체 검출 (TensorRT) | O |
| Isaac ROS Segmentation | 세그멘테이션 | O |

## 2. 설치 (JetPack 6.x 필요)

> Isaac ROS는 **JetPack 6.x (Ubuntu 22.04) 이상에서 공식 지원**됩니다.
> 현재 Xavier NX 환경(JetPack 4.6)에서는 일부 패키지만 제한적으로 동작 가능합니다.

```bash
# Isaac ROS 설치 (ROS2 Humble 기준)
sudo apt install ros-humble-isaac-ros-*

# 또는 소스 빌드
mkdir -p ~/isaac_ros_ws/src
cd ~/isaac_ros_ws
git clone https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
```

## 3. 주요 패키지

### Isaac ROS Visual SLAM

```bash
ros2 launch isaac_ros_visual_slam isaac_ros_visual_slam.launch.py
```

### Isaac ROS AprilTag

```bash
ros2 launch isaac_ros_apriltag isaac_ros_apriltag.launch.py
```

### Isaac ROS DNN Stereo Depth

```bash
ros2 launch isaac_ros_dnn_stereo_depth dnn_stereo_depth.launch.py
```

## 4. 제약 사항 (현재 Xavier NX JetPack 4.6)

| 기능 | JetPack 4.6 | JetPack 6.x |
|:----:|:-----------:|:-----------:|
| Isaac ROS Visual SLAM | X | O |
| Isaac ROS AprilTag | △ (소스 빌드) | O |
| FoundationPose | X | O |
| DNN Stereo Depth | X | O |

> 자세한 내용은 [NVIDIA Isaac ROS 공식 문서](https://nvidia-isaac-ros.github.io/) 참조

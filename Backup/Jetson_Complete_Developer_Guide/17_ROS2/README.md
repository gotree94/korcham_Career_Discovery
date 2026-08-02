# 17. ROS2 on Jetson

## 1. ROS2 개요

ROS2 (Robot Operating System 2)는 로봇 애플리케이션 개발을 위한 분산 통신 프레임워크입니다.

| 항목 | ROS1 (Melodic) | ROS2 (Humble/Jazzy) |
|:----:|:-------------:|:------------------:|
| 대상 OS | Ubuntu 18.04 | Ubuntu 22.04+ |
| 통신 | TCPROS/UDPROS | DDS (Data Distribution Service) |
| 실시간 | 제한적 | 지원 |
| 멀티로봇 | 제한적 | 네이티브 지원 |
| 보안 | 없음 | SROS2 (암호화/인증) |
| **JetPack 4.6** | **O (네이티브)** | **X (Ubuntu 18.04 미지원)** |

### 현재 환경 (JetPack 4.6) 제약

- ROS2 Humble: **Ubuntu 22.04 필요** → JetPack 6.x 업그레이드 시 사용 가능
- ROS2 Jazzy: **Ubuntu 24.04 필요** → JetPack 6.x +
- 본 섹션은 **참고용**으로, 실제 사용하려면 JetPack 업그레이드 필요

---

## 2. ROS2 설치 (JetPack 6.x 환경)

### JetPack 6.x + Ubuntu 22.04 기준

```bash
# ROS2 Humble 설치
sudo apt update && sudo apt upgrade -y
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install -y ros-humble-desktop

# 환경 설정
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# 추가 패키지
sudo apt install -y ros-humble-rviz2 \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-nav2 \
    ros-humble-slam-toolbox
```

---

## 3. ROS2 기본 개념

### Nodes (노드)

```bash
# 노드 실행
ros2 run demo_nodes_cpp talker
ros2 run demo_nodes_py listener

# 노드 목록
ros2 node list

# 노드 정보
ros2 node info /talker
```

### Topics (토픽)

```bash
# 토픽 목록
ros2 topic list

# 토픽 정보
ros2 topic info /chatter

# 토픽 구독 (실시간 데이터 보기)
ros2 topic echo /chatter

# 토픽 발행 빈도
ros2 topic hz /chatter
```

### Services (서비스)

```bash
# 서비스 목록
ros2 service list

# 서비스 호출
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 5, b: 3}"
```

### Actions (액션)

```bash
# 액션 목록
ros2 action list

# 액션 정보
ros2 action info /turtle1/rotate_absolute
```

---

## 4. ROS2 Python 예제

### Publisher

```python
#!/usr/bin/env python3
# publisher.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello from Jetson!'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

def main():
    rclpy.init()
    node = MinimalPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Subscriber

```python
#!/usr/bin/env python3
# subscriber.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String, 'topic', self.listener_callback, 10)

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: {msg.data}')

def main():
    rclpy.init()
    node = MinimalSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

### Service

```python
#!/usr/bin/env python3
# service_server.py
import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts

class AddTwoIntsServer(Node):
    def __init__(self):
        super().__init__('add_two_ints_server')
        self.srv = self.create_service(
            AddTwoInts, 'add_two_ints', self.callback)

    def callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(
            f'{request.a} + {request.b} = {response.sum}')
        return response

def main():
    rclpy.init()
    node = AddTwoIntsServer()
    rclpy.spin(node)
```

---

## 5. ROS2 DDS 미들웨어

ROS2는 DDS(Data Distribution Service)를 기반으로 통신합니다.

| DDS 구현 | 특징 | ROS2 기본 |
|:---------:|:----:|:---------:|
| Fast DDS | eProsima, 기본 DDS | Humble 기본 |
| Cyclone DDS | Eclipse, 경량 | Jazzy 기본 |
| GurumDDS | 한국, 경량+보안 | 선택 |

```bash
# DDS 확인
ros2 doctor

# DDS 변경 (Humble → Cyclone DDS)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```

---

## 6. ROS2 + Jetson GPIO

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import Jetson.GPIO as GPIO

class GPIOLEDNode(Node):
    def __init__(self):
        super().__init__('gpio_led_node')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.OUT)
        self.subscription = self.create_subscription(
            Bool, 'led_control', self.callback, 10)

    def callback(self, msg):
        GPIO.output(12, msg.data)
        self.get_logger().info(f'LED set to {msg.data}')

def main():
    rclpy.init()
    node = GPIOLEDNode()
    rclpy.spin(node)
    GPIO.cleanup()
```

---

## 7. ROS2 + Camera (Image Transport)

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.publisher = self.create_publisher(Image, 'camera/image', 10)
        self.timer = self.create_timer(0.033, self.publish_frame)  # 30fps
        self.cap = cv2.VideoCapture(0)
        self.bridge = CvBridge()

    def publish_frame(self):
        ret, frame = self.cap.read()
        if ret:
            msg = self.bridge.cv2_to_imgmsg(frame, 'bgr8')
            self.publisher.publish(msg)

def main():
    rclpy.init()
    node = CameraPublisher()
    rclpy.spin(node)
    node.cap.release()
```

---

## 8. TF2 (좌표 변환)

```bash
# TF 트리 보기
ros2 run tf2_tools view_frames.py

# TF echo
ros2 run tf2_ros tf2_echo map base_link
```

```python
import rclpy
from rclpy.node import Node
import tf2_ros
from geometry_msgs.msg import TransformStamped

class TFBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_broadcaster')
        self.br = tf2_ros.TransformBroadcaster(self)
        self.timer = self.create_timer(0.1, self.broadcast)

    def broadcast(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = 1.0
        t.transform.translation.y = 2.0
        t.transform.rotation.w = 1.0
        self.br.sendTransform(t)
```

---

## 9. Gazebo 시뮬레이션

```bash
# Gazebo 설치
sudo apt install ros-humble-gazebo-ros-pkgs

# TurtleBot3 시뮬레이션
sudo apt install ros-humble-turtlebot3-gazebo
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

---

## 10. JetPack 4.6에서 ROS2 우회 방법

현재 환경(JetPack 4.6 / Ubuntu 18.04)에서 ROS2가 필요하다면:

| 방법 | 설명 | 난이도 |
|:----:|------|:------:|
| **듀얼 SD 카드** | JetPack 4.6(ROS1) + 6.x(ROS2) SD 카드 교체 | 쉬움 |
| **Docker** | ROS2 Humble Docker 컨테이너 실행 | 중간 |
| **소스 빌드** | ROS2 Eloquent를 Ubuntu 18.04에 소스 빌드 | 어려움 |
| **JetPack 업그레이드** | JetPack 6.x로 업그레이드 (SD 카드 재설치) | 중간 |

> **권장**: 프로젝트 목적에 따라 SD 카드를 분리하여 사용 (ROS1=Melodic, ROS2=별도 SD 카드)

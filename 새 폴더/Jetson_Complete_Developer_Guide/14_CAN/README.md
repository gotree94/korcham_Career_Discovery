# 14. CAN Communication

## 1. CAN 개요

CAN(Controller Area Network)은 차량/산업용 통신 프로토콜입니다.

| 항목 | Xavier NX |
|------|:---------:|
| CAN 컨트롤러 | 내장 (MCP251x 호환) |
| CAN FD | 지원 |
| 최대 속도 | 5 Mbps (CAN FD) |
| **Orin Nano** | **CAN 미지원** |

> Xavier NX의 강점 중 하나: CAN FD 네이티브 지원
> (Orin Nano는 CAN 미지원으로 자동차/산업용에 Xavier NX가 유리)

## 2. CAN 설정

```bash
# CAN 인터페이스 활성화
sudo modprobe can
sudo modprobe can_raw
sudo modprobe mttcan

# CAN 설정 (250kbps)
sudo ip link set can0 type can bitrate 250000 dbitrate 1000000 fd on
sudo ip link set can0 up

# 설정 확인
ip -details link show can0
```

## 3. CAN 송수신

```bash
# CAN 수신 모니터링
candump can0

# CAN 메시지 전송
cansend can0 123#DEADBEEF

# 더 자세히
cansniffer can0
```

## 4. Python CAN 예제

```python
import can

bus = can.interface.Bus(channel='can0', bustype='socketcan')

# 송신
msg = can.Message(
    arbitration_id=0x123,
    data=[0xDE, 0xAD, 0xBE, 0xEF],
    is_extended_id=False
)
bus.send(msg)

# 수신
for msg in bus:
    print(f"ID: {hex(msg.arbitration_id)}, "
          f"Data: {msg.data.hex()}")
```

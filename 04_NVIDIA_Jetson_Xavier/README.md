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

### NVIDIA Jetson Xavier NX 의 상태를 확인하기

#### 시리얼 접속

  * 상태를 확인하기 위해서 제공되는 USB 케이블을 Omni Wheel 로봇의 오른쪽 측면의 Micro USB 커넥터에 연결하고
  * 한쪽은 PC와 연결합니다.
  * 시리얼 프트 번호를 확인하고 속도는 115200, 8, 1 Stop, No Parity 로 설정하면 아래와 같이 부팅 과정보이고
  * 로그인 대기 화면이 나옵니다.
  * ID 는 bready 이며, PW 는 00000000(0 8개 입니다.)

![](img/001.png)

![](img/002.png)

![](img/003.png)

#### 네트워크 접속
   * 시리엏 접속이 와료되면 ifconfig 명령을 통하며 네트워크 IP 를 확인 합니다.
```
bready@bready-desktop:~$ ifconfig
docker0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:2a:38:b7:6d  txqueuelen 0  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

eth0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether 48:b0:2d:67:6e:bc  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 37

l4tbr0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.55.1  netmask 255.255.255.0  broadcast 192.168.55.255
        inet6 fe80::1  prefixlen 128  scopeid 0x20<link>
        inet6 fe80::74c8:a7ff:fe67:2a15  prefixlen 64  scopeid 0x20<link>
        ether 76:c8:a7:67:2a:15  txqueuelen 1000  (Ethernet)
        RX packets 2591  bytes 241022 (241.0 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 161  bytes 24152 (24.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1  (Local Loopback)
        RX packets 658  bytes 51378 (51.3 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 658  bytes 51378 (51.3 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

rndis0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::74c8:a7ff:fe67:2a15  prefixlen 64  scopeid 0x20<link>
        ether 76:c8:a7:67:2a:15  txqueuelen 1000  (Ethernet)
        RX packets 2621  bytes 243987 (243.9 KB)
        RX errors 0  dropped 4  overruns 0  frame 0
        TX packets 200  bytes 40796 (40.7 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

usb0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet6 fe80::74c8:a7ff:fe67:2a17  prefixlen 64  scopeid 0x20<link>
        ether 76:c8:a7:67:2a:17  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 1248  bytes 216060 (216.0 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.0.55  netmask 255.255.255.0  broadcast 192.168.0.255
        inet6 fe80::2635:71c0:1120:d4c5  prefixlen 64  scopeid 0x20<link>
        ether 00:e0:2d:0c:03:e6  txqueuelen 1000  (Ethernet)
        RX packets 2557  bytes 371457 (371.4 KB)
        RX errors 0  dropped 44  overruns 0  frame 0
        TX packets 318  bytes 31482 (31.4 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

bready@bready-desktop:~$
```
* Mobaxterm을 이용해서 네트워크 터미널로 OmniWheel Robot에 접속 합니다.
* https://mobaxterm.mobatek.net/download.html

![](img/004.png)

![](img/005.png)

![](img/006.png)

![](img/007.png)

![](img/008.png)

* VNC로 화면으로 원격에서 UI 화면을 보여면 Mobaxterm에서 VNC로 연결해도 됨. (생각보다 속다가 많이 느림)

![](img/009.png)

![](img/010.png)

![](img/011.png)


---

# NVIDIA Jetson Xavier NX — Ubuntu 시리얼 터미널에서 Wi-Fi 연결 설정

## 1. 개요

NVIDIA Jetson Xavier NX에서 GUI 없이 **시리얼 콘솔(Serial Terminal)**만 사용하여 Ubuntu의 Wi-Fi를 설정하는 방법을 정리한다.

Jetson에서는 일반적으로 **NetworkManager의 `nmcli` 명령**을 이용하면 GUI 없이도 Wi-Fi 검색, 연결, IP 확인 및 자동 연결 설정을 할 수 있다.

전체적인 구성은 다음과 같다.

```text
Jetson Xavier NX
      │
      │ Serial Console
      ▼
Ubuntu Terminal
      │
      ├─ 1. Wi-Fi 장치 확인
      ├─ 2. Wi-Fi 활성화
      ├─ 3. 주변 AP 검색
      ├─ 4. AP 연결
      ├─ 5. IP 주소 확인
      └─ 6. 인터넷 연결 확인
```

---

# 2. Wi-Fi 장치가 인식되었는지 확인

먼저 NetworkManager가 인식하고 있는 네트워크 장치를 확인한다.

```bash
nmcli device status
```

예:

```text
DEVICE    TYPE      STATE         CONNECTION
wlan0     wifi      disconnected  --
eth0      ethernet  disconnected  --
lo        loopback  unmanaged      --
```

여기에서 다음과 같이 `wlan0`이 표시되는지 확인한다.

```text
wlan0     wifi
```

`wlan0`은 Jetson에서 사용하는 Wi-Fi 인터페이스의 대표적인 이름이다.

단, Wi-Fi 모듈이나 Linux 환경에 따라 인터페이스 이름이 다를 수 있다.

---

## 2.1 Wi-Fi 인터페이스를 직접 확인

다음 명령으로 무선 인터페이스를 확인할 수 있다.

```bash
iw dev
```

예:

```text
phy#0
    Interface wlan0
        ifindex 3
        wdev 0x1
        addr xx:xx:xx:xx:xx:xx
        type managed
```

여기에서:

```text
Interface wlan0
```

이 확인되면 Linux에서 Wi-Fi 인터페이스가 인식된 것이다.

---

# 3. Wi-Fi 기능이 활성화되어 있는지 확인

다음 명령을 실행한다.

```bash
nmcli radio wifi
```

정상적으로 활성화되어 있으면:

```text
enabled
```

가 출력된다.

만약 다음과 같이 나온다면:

```text
disabled
```

Wi-Fi를 켠다.

```bash
sudo nmcli radio wifi on
```

그 후 다시 확인한다.

```bash
nmcli radio wifi
```

---

# 4. 주변 Wi-Fi 검색

주변에서 검색되는 Wi-Fi AP를 확인한다.

```bash
nmcli device wifi list
```

또는:

```bash
nmcli dev wifi
```

예:

```text
IN-USE  SSID        MODE   CHAN  RATE        SIGNAL
        MyHomeWiFi  Infra  36    540 Mbit/s  80
        OfficeWiFi  Infra  11    270 Mbit/s  65
        Guest       Infra  1     130 Mbit/s  45
```

여기에서 연결하려는 **SSID**를 확인한다.

예를 들어:

```text
MyHomeWiFi
```

가 연결하려는 Wi-Fi 이름이라고 가정한다.

---

# 5. Wi-Fi 연결

SSID와 비밀번호를 이용하여 연결한다.

```bash
sudo nmcli device wifi connect "MyHomeWiFi" password "12345678"
```

정상적으로 연결되면 다음과 비슷한 메시지가 출력된다.

```text
Device 'wlan0' successfully activated with 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'.
```

여기서 `wlan0`이 실제 Wi-Fi 인터페이스이다.

---

# 6. 연결 상태 확인

연결 후 다음 명령으로 상태를 확인한다.

```bash
nmcli device status
```

정상적으로 연결된 경우:

```text
DEVICE    TYPE      STATE      CONNECTION
wlan0     wifi      connected  MyHomeWiFi
eth0      ethernet  unavailable --
```

핵심은:

```text
wlan0     wifi      connected
```

가 나타나는 것이다.

---

# 7. Wi-Fi IP 주소 확인

Wi-Fi에 정상적으로 연결되었더라도 실제 IP 주소를 확인하는 것이 좋다.

## 방법 1 — `ip addr`

```bash
ip addr show wlan0
```

예:

```text
3: wlan0:
    inet 192.168.0.25/24
```

이 경우 Jetson의 Wi-Fi IP 주소는:

```text
192.168.0.25
```

이다.

---

## 방법 2 — `hostname -I`

더 간단하게 확인하려면:

```bash
hostname -I
```

예:

```text
192.168.0.25
```

---

# 8. 인터넷 연결 확인

먼저 IP 주소를 이용하여 인터넷 연결을 테스트한다.

```bash
ping -c 4 8.8.8.8
```

정상적인 경우:

```text
64 bytes from 8.8.8.8: icmp_seq=1 ttl=...
64 bytes from 8.8.8.8: icmp_seq=2 ttl=...
```

등의 응답이 나온다.

---

## 8.1 DNS까지 확인

IP 주소 통신뿐 아니라 DNS도 정상인지 확인하려면:

```bash
ping -c 4 google.com
```

이 명령까지 정상적으로 응답하면 일반적으로 다음이 모두 정상이다.

```text
Wi-Fi 연결
   ↓
DHCP
   ↓
IP 주소
   ↓
Gateway
   ↓
DNS
   ↓
Internet
```

---

# 9. NetworkManager 연결 정보 확인

현재 저장되어 있는 연결을 확인한다.

```bash
nmcli connection show
```

예:

```text
NAME          UUID                                  TYPE      DEVICE
MyHomeWiFi    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  wifi      wlan0
```

특정 연결의 상세 정보를 확인하려면:

```bash
nmcli connection show "MyHomeWiFi"
```

또는 Wi-Fi 장치 자체의 정보를 확인할 수 있다.

```bash
nmcli device show wlan0
```

여기에서 다음과 같은 항목을 확인할 수 있다.

```text
IP4.ADDRESS
IP4.GATEWAY
IP4.DNS
GENERAL.CONNECTION
```

---

# 10. 재부팅 후 자동 연결 설정

NetworkManager를 이용해 생성한 Wi-Fi 연결은 일반적으로 연결 정보가 저장된다.

자동 연결 여부를 확인하려면:

```bash
nmcli connection show "MyHomeWiFi" | grep autoconnect
```

정상적으로 자동 연결되도록 설정되어 있다면:

```text
connection.autoconnect: yes
```

만약 `no`라면 다음과 같이 설정한다.

```bash
sudo nmcli connection modify "MyHomeWiFi" connection.autoconnect yes
```

이제 Jetson을 재부팅해도 해당 Wi-Fi에 자동으로 연결하도록 설정할 수 있다.

---

# 11. GUI 없이 사용하는 핵심 `nmcli` 명령

Jetson Xavier NX를 **시리얼 콘솔 + SSH 기반 임베디드 장비**로 운용한다면 다음 명령들을 기억해 두면 편리하다.

| 목적 | 명령 |
|---|---|
| 네트워크 장치 확인 | `nmcli device status` |
| Wi-Fi 상태 확인 | `nmcli radio wifi` |
| Wi-Fi 켜기 | `sudo nmcli radio wifi on` |
| 주변 AP 검색 | `nmcli device wifi list` |
| Wi-Fi 연결 | `sudo nmcli device wifi connect "SSID" password "PASSWORD"` |
| 연결 정보 확인 | `nmcli connection show` |
| Wi-Fi 장치 정보 | `nmcli device show wlan0` |
| IP 주소 확인 | `ip addr show wlan0` |
| 간단한 IP 확인 | `hostname -I` |
| 인터넷 테스트 | `ping -c 4 8.8.8.8` |
| DNS 테스트 | `ping -c 4 google.com` |
| Wi-Fi 연결 해제 | `sudo nmcli device disconnect wlan0` |
| Wi-Fi 재연결 | `sudo nmcli device connect wlan0` |

---

# 12. Wi-Fi가 `nmcli`에 나타나지 않을 때

다음 순서로 하드웨어와 드라이버를 확인한다.

## 12.1 NetworkManager 확인

```bash
which nmcli
```

그리고:

```bash
systemctl status NetworkManager
```

정상적인 경우:

```text
Active: active (running)
```

이 나타난다.

---

## 12.2 무선 인터페이스 확인

```bash
iw dev
```

---

## 12.3 PCI 장치 확인

내장/PCIe 방식의 Wi-Fi 장치를 사용하는 경우:

```bash
lspci
```

---

## 12.4 USB Wi-Fi 장치 확인

USB Wi-Fi 동글을 사용하는 경우:

```bash
lsusb
```

---

# 13. 전체 작업 흐름

Jetson Xavier NX에서 시리얼 터미널로 처음 Wi-Fi를 설정한다면 다음 순서로 진행하면 된다.

```text
① Wi-Fi 장치 확인
        │
        ▼
nmcli device status
        │
        ▼
② Wi-Fi 활성화 확인
        │
        ▼
nmcli radio wifi
        │
        ├─ disabled → sudo nmcli radio wifi on
        │
        ▼
③ 주변 Wi-Fi 검색
        │
        ▼
nmcli device wifi list
        │
        ▼
④ SSID 선택
        │
        ▼
sudo nmcli device wifi connect "SSID" password "PASSWORD"
        │
        ▼
⑤ 연결 확인
        │
        ▼
nmcli device status
        │
        ▼
⑥ IP 확인
        │
        ▼
hostname -I
        │
        ▼
⑦ 인터넷 확인
        │
        ▼
ping -c 4 8.8.8.8
        │
        ▼
⑧ DNS 확인
        │
        ▼
ping -c 4 google.com
```

---

# 14. Jetson Xavier NX에서 최종적으로 확인해야 할 구조

Wi-Fi 연결을 문제없이 구성하려면 다음 계층이 모두 정상이어야 한다.

```text
┌──────────────────────────────┐
│       Wi-Fi Access Point     │
│        (공유기 / AP)          │
└──────────────┬───────────────┘
               │
             Wi-Fi
               │
┌──────────────▼───────────────┐
│      Jetson Xavier NX        │
│                              │
│  Wi-Fi Module                │
│       ↓                      │
│  Linux Driver                │
│       ↓                      │
│  wlan0                       │
│       ↓                      │
│  NetworkManager              │
│       ↓                      │
│  nmcli                       │
│       ↓                      │
│  DHCP                        │
│       ↓                      │
│  IP / Gateway / DNS          │
└──────────────────────────────┘
```

문제가 발생했을 때는 **어느 계층에서 문제가 발생했는지**를 확인하면 된다.

---

# 15. 실제 Jetson Xavier NX 시리얼 터미널 연결 예시

다음은 실제 환경에서 실행한 명령과 결과의 예이다.

## 15.1 현재 네트워크 장치 확인

```text
bready@bready-desktop:~$ nmcli device status
DEVICE   TYPE      STATE                                  CONNECTION
l4tbr0   bridge    connected                              l4tbr0
docker0  bridge    connected                              docker0
wlan0    wifi      connecting (getting IP configuration)  room407
eth0     ethernet  unavailable                            --
dummy0   dummy     unmanaged                              --
rndis0   ethernet  unmanaged                              --
usb0     ethernet  unmanaged                              --
lo       loopback  unmanaged                              --
bready@bready-desktop:~$
```

### 분석

여기에서 중요한 부분은:

```text
wlan0    wifi    connecting (getting IP configuration)    room407
```

이다.

즉,

- `wlan0` → Wi-Fi 인터페이스
- `wifi` → 무선 장치
- `room407` → 현재 선택된 SSID
- `connecting (getting IP configuration)` → AP에는 연결을 시도했지만 아직 IP 설정을 받는 중

이라는 의미이다.

특히 `getting IP configuration` 상태가 장시간 지속된다면 DHCP 또는 네트워크 설정을 확인할 필요가 있다.

---

## 15.2 주변 Wi-Fi 검색

```text
bready@bready-desktop:~$ nmcli device wifi list
IN-USE  SSID     MODE   CHAN  RATE       SIGNAL  BARS  SECURITY
        room410  Infra  1     44 Mbit/s  70      ▂▄▆_  WPA2
        iptime   Infra  9     44 Mbit/s  70      ▂▄▆_  --
        room407  Infra  4     44 Mbit/s  50      ▂▄__  WPA2
        room406  Infra  6     44 Mbit/s  23      ▂___  WPA2
bready@bready-desktop:~$
```

검색 결과에서 다음 AP들이 확인된다.

| SSID | 채널 | 신호 | 보안 |
|---|---:|---:|---|
| room410 | 1 | 70 | WPA2 |
| iptime | 9 | 70 | 없음 |
| room407 | 4 | 50 | WPA2 |
| room406 | 6 | 23 | WPA2 |

여기에서는 `room410`의 신호가 `70`으로 비교적 강하게 검색되고 있다.

---

## 15.3 `room410`에 연결

다음 명령으로 Wi-Fi를 변경한다.

```text
bready@bready-desktop:~$ sudo nmcli device wifi connect "room410" password "1111
1111"
[sudo] password for bready:
Device 'wlan0' successfully activated with 'aa949f7e-839c-4b0b-8a2e-17c5cfc0e261                                          '.
bready@bready-desktop:~$
```

핵심 명령은 다음과 같다.

```bash
sudo nmcli device wifi connect "room410" password "11111111"
```

정상적으로 연결되면:

```text
Device 'wlan0' successfully activated with '...'
```

메시지가 출력된다.

즉, 이 결과는 **`wlan0`이 `room410` AP에 성공적으로 연결되었다는 의미**이다.

---

# 16. 연결 후 반드시 확인할 것

Wi-Fi 연결 성공 메시지가 나왔다고 해서 바로 끝내지 말고 다음 명령으로 확인하는 것이 좋다.

### ① 연결 상태

```bash
nmcli device status
```

정상적인 예:

```text
wlan0    wifi    connected    room410
```

### ② IP 주소

```bash
hostname -I
```

또는:

```bash
ip addr show wlan0
```

### ③ Gateway / DNS

```bash
nmcli device show wlan0
```

### ④ 인터넷

```bash
ping -c 4 8.8.8.8
```

### ⑤ DNS

```bash
ping -c 4 google.com
```

---

# 17. 실전에서 가장 많이 사용하는 최소 명령

Jetson Xavier NX에서 시리얼 콘솔로 Wi-Fi를 처음 설정하는 상황이라면 다음 명령만 순서대로 실행해도 된다.

```bash
nmcli device status
```

```bash
nmcli device wifi list
```

```bash
sudo nmcli device wifi connect "WiFi이름" password "WiFi비밀번호"
```

```bash
nmcli device status
```

```bash
hostname -I
```

```bash
ping -c 4 8.8.8.8
```

최종적으로:

```text
wlan0
  ↓
connected
  ↓
IP 주소 획득
  ↓
Gateway 연결
  ↓
DNS 정상
  ↓
Internet 정상
```

이면 Wi-Fi 설정이 완료된 것이다.

---

## 18. SSH 접속으로 이어지는 과정

Wi-Fi가 정상적으로 연결되고 Jetson에 IP가 할당되면 시리얼 케이블을 제거하고 다른 PC에서 SSH로 접속할 수 있다.

예를 들어 Jetson의 IP가:

```text
192.168.0.37
```

이라면:

```bash
ssh 사용자이름@192.168.0.37
```

형태로 접속한다.

따라서 임베디드 개발 환경에서는 다음과 같은 형태로 사용할 수 있다.

```text
처음 설정
    │
    ▼
USB/UART
Serial Console
    │
    ▼
Wi-Fi 설정
    │
    ▼
wlan0
    │
    ▼
IP 주소 획득
    │
    ▼
SSH
    │
    ▼
원격 개발 / ROS2 / Docker / AI 실행
```

> **주의:** 실제 Wi-Fi 비밀번호를 문서에 저장하거나 공유할 때는 보안에 유의한다. 위 예시는 교육용으로 제공된 값이다.

---

## 📝 참고 자료

- NVIDIA Jetson 공식 문서: https://docs.nvidia.com/jetson/
- JetPack SDK: https://developer.nvidia.com/embedded/jetpack
- ROS 2 Humble 문서: https://docs.ros.org/en/humble/

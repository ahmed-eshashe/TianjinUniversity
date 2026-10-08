# CAN Bus Network Topology & Real-Time Loop Setup

## 1. Network Topology
The bimanual robotic cutting bench uses high-speed SocketCAN interfaces to maintain a deterministic 1 kHz control loop:

```
               ┌──────────────────────────────────────────────┐
               │         Host Workstation (Ubuntu 24.04)      │
               │           PREEMPT_RT Kernel 6.8+             │
               │       ROS 2 Jazzy + MoveIt 2 + SkRL          │
               └───────────────┬──────────────┬───────────────┘
                               │              │
                   SocketCAN   │              │ SocketCAN
                   Interface 0 │              │ Interface 1
                               ▼              ▼
                     ┌────────────┐        ┌────────────┐
                     │    can0    │        │    can1    │
                     │  (1 Mbps)  │        │  (1 Mbps)  │
                     └─────┬──────┘        └─────┬──────┘
                           │                     │
              ┌────────────┴────────────┐        │
              │                         │        │
              ▼                         ▼        ▼
       ┌──────────────┐         ┌──────────────┐ ┌───────────────┐
       │   Left Arm   │         │  Right Arm   │ │ Dexterous     │
       │   AR5-L6     │         │   AR5-L6     │ │ LinkerHand O6 │
       │ (Holding)    │         │ (Slicing)    │ │ (Fixturing)   │
       └──────────────┘         └──────────────┘ └───────────────┘
```

---

## 2. Linux SocketCAN Configuration Commands

To bring up the CAN bus channels with 1 Mbps bitrate and 1000-frame TX queue length:

```bash
# 1. Load Linux kernel CAN modules
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan   # For virtual simulation loopback testing

# 2. Configure can0 (Manipulator Bus)
sudo ip link set can0 type can bitrate 1000000
sudo ip link set txqueuelen 1000 dev can0
sudo ip link set can0 up

# 3. Configure can1 (Dexterous Hand Bus)
sudo ip link set can1 type can bitrate 1000000
sudo ip link set txqueuelen 1000 dev can1
sudo ip link set can1 up

# 4. Verify Bus Status
ip -details link show can0
ip -details link show can1
```

---

## 3. Real-Time Execution Guarantees
* **Kernel**: Linux with `PREEMPT_RT` patch.
* **Process Priority**: Real-time FIFO scheduler (`SCHED_FIFO`) with priority 95 assigned to the 1 kHz CAN transceiver thread.
* **Memory Locking**: Call `mlockall(MCL_CURRENT | MCL_FUTURE)` in C++ nodes to prevent page faults from inducing jitter.
* **Round-Trip Latency Target**: $< 0.8\text{ ms}$ per cycle to guarantee 1 kHz deterministic control.

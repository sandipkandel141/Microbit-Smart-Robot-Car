# Microbit Smart Robot Car 🚗

### Wireless Robotic Car with Obstacle Detection and Compass Navigation

A wireless-controlled robotic car developed using **BBC micro:bit and MicroPython**. The project combines embedded programming, radio communication, ultrasonic sensing, and compass-based navigation to provide responsive vehicle control and obstacle awareness.

## Project Overview

This project uses two BBC micro:bit devices:

- **Car micro:bit:** Controls the motors, measures obstacle distances, processes scanning requests, and transmits sensor information.
- **Controller micro:bit:** Sends movement commands, receives sensor data, displays navigation information, and controls an attached servo motor.

The devices communicate wirelessly using the micro:bit radio module.

## Key Features

### Wireless Remote Control
- Forward and backward movement
- Left and right steering
- Wireless commands using micro:bit radio
- Accelerometer-based forward and backward controls

### Obstacle Detection
- Ultrasonic distance measurement
- Forward movement stops when an obstacle is detected within 20 cm
- Distance information transmitted to the controller

### Automatic Direction Scanning
- Shake the controller to initiate a scan
- The car rotates to measure distances on its left and right
- The system recommends a direction based on available space
- Scan results are displayed on the controller

### Compass Navigation
- Built-in compass provides heading measurements
- Heading smoothing reduces abrupt directional changes
- LED display shows directional arrows

### Normal and Turbo Modes
- Normal speed: 40
- Turbo speed: 80
- External button connected to P1 toggles between modes

### Communication Safety
- Radio command timeout stops normal driving when commands are not received within 700 ms
- Scanning uses a staged control sequence
- Radio messages transmit distance, heading, and scan results

## Technologies Used

- **Programming Language:** MicroPython
- **Hardware Platform:** BBC micro:bit V1
- **Communication:** Micro:bit radio
- **Sensors:** Ultrasonic distance sensor, compass, accelerometer
- **Actuators:** DC motors and SG90 servo motor
- **Interfaces:** I2C, GPIO, PWM

## Project Structure

```text
Microbit-Smart-Robot-Car/
├── CarCode.py
├── ControllerCode.py
├── .gitignore
└── README.md
```

**CarCode.py** — Handles motor control, ultrasonic sensing, compass readings, obstacle protection, scanning, and wireless telemetry.

**ControllerCode.py** — Handles user input, radio commands, speed switching, servo control, navigation display, and scan results.

## How It Works

1. The controller reads button and accelerometer inputs.
2. Movement commands are transmitted wirelessly to the car.
3. The car processes commands and operates its motors.
4. An ultrasonic sensor measures the distance to obstacles.
5. The car sends distance and compass information back to the controller.
6. When a scan is requested, the car measures left and right distances and sends a suggested direction.

## Hardware Requirements

- Two BBC micro:bit devices
- Compatible robotic car chassis and motor driver
- DC motors
- Ultrasonic distance sensor
- SG90 servo motor
- External push button for turbo mode
- Compatible power supplies and connecting wires

The motor driver must support the I2C commands used in `CarCode.py`.

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/sandipkandel141/Microbit-Smart-Robot-Car.git
```

2. Open `CarCode.py` in a compatible micro:bit MicroPython editor.
3. Flash the car program onto the car's micro:bit.
4. Open `ControllerCode.py` and flash it onto the controller micro:bit.
5. Connect the motors, ultrasonic sensor, servo, and button to their configured interfaces.
6. Power both devices and calibrate the compass when prompted.
7. Use the controller to operate the car.

**Note:** Hardware wiring, motor-driver compatibility, and calibration should be verified before operation.

## Future Improvements

- Autonomous obstacle avoidance
- Improved navigation algorithms
- Bluetooth or mobile application control
- Real-time sensor monitoring
- More advanced path planning

## Author

**Sandip Kandel**

GitHub: [sandipkandel141](https://github.com/sandipkandel141)

Developed as a hands-on embedded systems and robotics programming project using MicroPython.
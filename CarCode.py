from microbit import *
import radio
from time import sleep_us, ticks_us, ticks_diff
STOP_DISTANCE = 20
TURN_MS = 450

LEFT_MOTOR_PERCENT = 100
RIGHT_MOTOR_PERCENT = 100

cmd = "STOP"
speed = 40
dist = -1

stage = 0
stage_time = 0
scan_id = -1

left = -1
right = -1
result = ""
result_until = 0

last_cmd = running_time()
last_dist = -1000
last_send = -1000
last_heading = -1000
last_result = -1000
motor_state = -1

filtered_heading = -1


# ==================================
# MOTOR CONTROL
# ==================================

def motor(d, s):
    if s > 0:
        s = max(35, s)

    ls = s * LEFT_MOTOR_PERCENT // 100
    rs = s * RIGHT_MOTOR_PERCENT // 100

    if d == 1:
        a, b, c, e = 0, ls, rs, 0

    elif d == 2:
        a, b, c, e = ls, 0, 0, rs

    elif d == 3:
        a, b, c, e = s, 0, s, 0

    elif d == 4:
        a, b, c, e = 0, s, 0, s

    else:
        a, b, c, e = 0, 0, 0, 0

    try:
        i2c.write(0x30, bytes((1, a)))
        i2c.write(0x30, bytes((2, b)))
        i2c.write(0x30, bytes((3, c)))
        i2c.write(0x30, bytes((4, e)))
    except OSError:
        pass


# ==================================
# ULTRASONIC SENSOR
# ==================================

def measure():
    pin14.write_digital(0)
    sleep_us(5)

    pin14.write_digital(1)
    sleep_us(10)

    pin14.write_digital(0)

    t = ticks_us()

    while pin15.read_digital() == 0:
        if ticks_diff(ticks_us(), t) > 25000:
            return -1

    t = ticks_us()

    while pin15.read_digital() == 1:
        if ticks_diff(ticks_us(), t) > 25000:
            return -1

    d = round(ticks_diff(ticks_us(), t) * 0.01715)

    if 2 <= d <= 400:
        return d

    return -1
def smooth_heading(h):
    global filtered_heading

    if filtered_heading < 0:
        filtered_heading = h

    else:
        diff = (
            (h - filtered_heading + 540) % 360
        ) - 180

        filtered_heading = (
            filtered_heading + diff * 0.25
        ) % 360

    return int(filtered_heading)
display.scroll("CAL")

if not compass.is_calibrated():
    compass.calibrate()

display.show(Image.YES)
sleep(500)

radio.config(
    group=57,
    channel=23,
    address=0x12345678,
    power=6,
    length=32,
    queue=3
)
radio.on()

motor(0, 0)

display.show("C")
sleep(300)
display.clear()

last_cmd = running_time()


while True:
    now = running_time()

    # RECEIVE CONTROLLER COMMANDS
    msg = radio.receive()

    if msg:
        if msg.startswith("CMD:"):
            p = msg.split(":")

            if len(p) == 3:
                last_cmd = now

                if stage == 0:
                    cmd = p[1]

                speed = 80 if p[2] == "80" else 40

        elif msg.startswith("SCAN:"):
            try:
                sid = int(msg[5:])
            except ValueError:
                sid = -1

            if sid >= 0:
                last_cmd = now

                if stage == 0 and sid != scan_id:
                    scan_id = sid
                    cmd = "STOP"
                    motor(0, 0)
                    motor_state = -1

                    stage = 1
                    stage_time = now

                    left = -1
                    right = -1
                    result = ""

                    display.show("S")

    # RADIO SAFETY TIMEOUT
    if now - last_cmd > 700:
        cmd = "STOP"

    # AUTOMATIC SCANNING
    if stage:
        t = now - stage_time

        if stage == 1 and t >= 200:
            motor(3, 40)
            stage = 2
            stage_time = now

        elif stage == 2 and t >= TURN_MS:
            motor(0, 0)
            stage = 3
            stage_time = now

        elif stage == 3 and t >= 350:
            left = measure()
            motor(4, 40)
            stage = 4
            stage_time = now

        elif stage == 4 and t >= TURN_MS:
            motor(0, 0)
            stage = 5
            stage_time = now

        elif stage == 5 and t >= 200:
            motor(4, 40)
            stage = 6
            stage_time = now

        elif stage == 6 and t >= TURN_MS:
            motor(0, 0)
            stage = 7
            stage_time = now

        elif stage == 7 and t >= 350:
            right = measure()
            motor(3, 40)
            stage = 8
            stage_time = now

        elif stage == 8 and t >= TURN_MS:
            motor(0, 0)
            stage = 0
            cmd = "STOP"
            motor_state = -1

            if left < 0 and right < 0:
                result = "?"

            elif left < 0:
                result = "R"

            elif right < 0:
                result = "L"

            elif left <= STOP_DISTANCE and right <= STOP_DISTANCE:
                result = "B"

            elif left > right:
                result = "L"

            elif right > left:
                result = "R"

            else:
                result = "="

            display.show(result)
            result_until = now + 8000
            last_result = -1000

    # NORMAL DRIVING
    else:
        if now - last_dist >= 300:
            dist = measure()
            last_dist = now

        if cmd == "FORWARD":
            if 0 <= dist <= STOP_DISTANCE:
                desired = 0
            else:
                desired = 1

        elif cmd == "BACKWARD":
            desired = 2

        elif cmd == "LEFT":
            desired = 3

        elif cmd == "RIGHT":
            desired = 4

        else:
            desired = 0

        state = desired * 100 + speed

        if state != motor_state:
            motor(desired, speed)
            motor_state = state

    # TELEMETRY
    now = running_time()

    if now - last_send >= 300:
        radio.send("D:{}".format(dist))
        last_send = now

    if now - last_heading >= 500:
        if compass.is_calibrated():
            h = smooth_heading(compass.heading())
            radio.send("H:{}".format(h))
        else:
            radio.send("H:-1")

        last_heading = now

    # SEND SCAN RESULT AND DISTANCES
    if result and now < result_until:
        if now - last_result >= 350:
            radio.send(
                "R:{}:{}:{}:{}".format(
                    scan_id, result, left, right
                )
            )
            last_result = now

    sleep(20)
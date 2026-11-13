from microbit import *
import radio

# CONTROLLER V12.0 LITE
# P1 SINGLE-PRESS TURBO TOGGLE
# micro:bit V1

radio.config(
    group=57,
    channel=23,
    address=0x12345678,
    power=6,
    length=32,
    queue=3
)
radio.on()

NORMAL = 40
TURBO = 80
OFFSET = 270
LIMIT = 20

# Turbo button P1 to GND
pin1.set_pull(pin1.PULL_UP)

# SG90 servo P2
pin2.set_analog_period(20)

def servo(us):
    pin2.write_analog(us * 1023 // 20000)

servo(1500)

speed = NORMAL
previous_speed = NORMAL
speed_until = 0

# NEW: P1 button press detection
last_switch = pin1.read_digital()
last_press = -1000

cmd = "STOP"
last_send = -1000

dist = -1
last_dist = -1000
heading = -1
last_heading = -1000

last_fan = 0
fan = False

scan_id = 0
scanning = False
scan_time = 0
last_scan_send = -1000

scan_phase = 0
phase_time = 0
left = -1
right = -1
choice = "?"

last_show = -1000
showing_scroll = False
scroll_end = 0

arrows = (
    Image.ARROW_N,
    Image.ARROW_NE,
    Image.ARROW_E,
    Image.ARROW_SE,
    Image.ARROW_S,
    Image.ARROW_SW,
    Image.ARROW_W,
    Image.ARROW_NW
)

def show_arrow(h):
    d = ((h + OFFSET + 22) % 360) // 45
    display.show(arrows[d])

def scan_arrow(c):
    if c == "L":
        display.show(Image.ARROW_W)
    elif c == "R":
        display.show(Image.ARROW_E)
    elif c == "B":
        display.show(Image.ARROW_S)
    elif c == "=":
        display.show(Image.DIAMOND)
    else:
        display.show("?")

def scroll_text(s):
    global showing_scroll, scroll_end
    display.scroll(s, delay=90, wait=False)
    showing_scroll = True
    scroll_end = running_time() + len(s) * 540 + 500

display.show("N")

while True:
    now = running_time()
    switch = pin1.read_digital()

    # Detect a NEW press, not continuous holding
    if switch == 0 and last_switch == 1:
        if now - last_press > 250:
            if speed == NORMAL:
                speed = TURBO
            else:
                speed = NORMAL

            last_press = now
            speed_until = now + 1200

    last_switch = switch

    # MOVEMENT
    a = button_a.is_pressed()
    b = button_b.is_pressed()

    if a and b:
        y = accelerometer.get_y()
        if y < -200:
            cmd = "FORWARD"
        elif y > 200:
            cmd = "BACKWARD"
        else:
            cmd = "STOP"
    elif a:
        cmd = "LEFT"
    elif b:
        cmd = "RIGHT"
    else:
        cmd = "STOP"

    # SHAKE TO SCAN
    if accelerometer.was_gesture("shake"):
        if not scanning and scan_phase == 0:
            scan_id += 1
            if scan_id > 999:
                scan_id = 1
            scanning = True
            scan_time = now
            last_scan_send = -1000
            choice = "?"

    # SEND COMMAND
    if now - last_send >= 150:
        radio.send("CMD:{}:{}".format(cmd, speed))
        last_send = now

    # SEND SCAN REQUEST
    if scanning and now - last_scan_send >= 350:
        radio.send("SCAN:{}".format(scan_id))
        last_scan_send = now

    # RECEIVE CAR DATA
    for i in range(3):
        msg = radio.receive()
        if msg is None:
            break

        if msg.startswith("D:"):
            try:
                dist = int(msg[2:])
                last_dist = now
            except ValueError:
                pass

        elif msg.startswith("H:"):
            try:
                heading = int(msg[2:])
                last_heading = now
            except ValueError:
                pass

        elif msg.startswith("R:") and scanning:
            p = msg.split(":")
            if len(p) == 5:
                try:
                    if int(p[1]) == scan_id:
                        choice = p[2]
                        left = int(p[3])
                        right = int(p[4])
                        scanning = False
                        scan_phase = 1
                        phase_time = now
                except ValueError:
                    pass

    # SCAN TIMEOUT
    if scanning and now - scan_time > 9000:
        scanning = False

    # SERVO
    interval = 325 if speed == TURBO else 650

    if cmd != "STOP" and now - last_fan >= interval:
        fan = not fan
        servo(2000 if fan else 1000)
        last_fan = now

    # SCROLL TIMER
    if showing_scroll and now >= scroll_end:
        showing_scroll = False

    # SCAN DISPLAY
    if scan_phase == 1:
        if now - phase_time >= 2000:
            scan_phase = 2
            scroll_text("L{}".format(left))

    elif scan_phase == 2 and not showing_scroll:
        scan_phase = 3
        scroll_text("R{}".format(right))

    elif scan_phase == 3 and not showing_scroll:
        scan_phase = 0

    # OBSTACLE
    obstacle = (
        0 <= dist <= LIMIT
        and now - last_dist < 1200
    )

    if not showing_scroll:
        if scanning:
            display.show("S")

        elif scan_phase == 1:
            scan_arrow(choice)

        elif scan_phase == 0 and obstacle:
            if now - last_show > 2500:
                scroll_text(str(dist) + "cm")
                last_show = now
            else:
                display.show(Image.NO)

        elif scan_phase == 0 and now < speed_until:
            display.show("T" if speed == TURBO else "N")

        elif scan_phase == 0:
            if (
                0 <= heading < 360
                and now - last_heading < 2000
            ):
                show_arrow(heading)
            else:
                display.show("?")

    sleep(30)
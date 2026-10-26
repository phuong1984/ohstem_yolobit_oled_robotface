# main.py - demo robotface cho ESP32 + OLED SSD1306 128x64 (I2C)
# Chép lên ESP32: main.py, robotface.py, ssd1306.py
#   ssd1306.py:  import mip; mip.install("ssd1306")   (ESP32 cần có WiFi)
from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C
from robotface import RobotFace, EXPRESSIONS, ANIMATIONS
from yolobit import *
oled = SSD1306_I2C(128, 64, SoftI2C(scl=Pin(pin19.pin), sda=Pin(pin20.pin)))        # dia chi 0x3C
face = RobotFace(oled)                                   # 25 khung/giây


def demo():
    face.idle(True)                          # tự chớp mắt + liếc nhìn trong suốt chương trình
    face.expression("neutral")
    face.wait(2500)                          # wait() thay cho sleep(): idle vẫn chạy

    # 1) lần lượt các biểu cảm tĩnh
    for name in EXPRESSIONS:
        face.expression(name, 300)
        face.wait(1600)

    # 2) lần lượt các animation một lần (play đợi chạy xong)
    face.expression("neutral")
    face.wait(800)
    for name in ANIMATIONS:
        if name == "wake_up":                # wake_up cần đang ngủ
            face.expression("sleep")
            face.wait(1200)
        face.play(name)
        face.wait(700)
        if name == "fall_asleep":
            face.wait(1500)                  # để robot ngủ một lát (play fall_asleep kết thúc ở biểu cảm 'sleep')

    # 3) nói + nhìn theo hướng
    face.expression("happy")
    face.talk_for(3)
    face.expression("neutral")
    for d in ("left", "right", "up", "down", "up_left", "down_right", "center"):
        face.look(d)
        face.wait(700)

    # 4) hiệu ứng lặp: trái tim đập, cười rung, nức nở
    face.expression("love")
    face.heartbeat(True)
    face.wait(3000)
    face.heartbeat(False)
    face.expression("laugh")
    face.loop("laugh", True)
    face.wait(2500)
    face.loop("laugh", False)
    face.expression("cry")
    face.loop("sob", True)
    face.wait(3500)
    face.loop("sob", False)
    face.expression("neutral")
    face.wait(1500)


while True:
    demo()

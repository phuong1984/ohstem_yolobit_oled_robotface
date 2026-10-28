"""robotface.py - Khuôn mặt robot cho OLED SSD1306 128x64 (MicroPython >= 1.19).

Cần MicroPython có framebuf.ellipse() và framebuf.poly() (có từ v1.19). Không cần font hay ảnh:
mọi thứ được vẽ bằng hình cơ bản (hình chữ nhật bo góc, elip, đa giác, đường thẳng).

CÁCH DÙNG NHANH
    from robotface import RobotFace
    face = RobotFace(oled)              # oled = ssd1306.SSD1306_I2C(128, 64, i2c)
    face.idle(True)                     # tự chớp mắt và thỉnh thoảng liếc nhìn
    face.expression("happy")            # đổi biểu cảm (chuyển mượt 300 ms)
    face.wait(2000)                     # đợi 2 giây NHƯNG animation vẫn chạy
    face.play("laugh")                  # animation một lần, đợi chạy xong
    face.talk_for(3)                    # nói trong 3 giây
    face.look("left")                   # nhìn sang trái
    face.heartbeat(True)                # trái tim đập (lặp)

MÔ HÌNH HOẠT ĐỘNG
    * update() vẽ 1 khung hình nếu đến hạn (mặc định 25 khung/giây) và CHỈ gửi ra màn hình khi hình
      thật sự thay đổi. Gọi update() liên tục trong vòng lặp chính của bạn.
    * wait(ms) = vòng lặp gọi update() trong ms mili giây. Dùng nó thay cho time.sleep() để robot
      vẫn chớp mắt, nhìn quanh... trong lúc chờ.
    * play() chạy một lần; play(..., loop=True) lặp nền đến khi stop_animation().
    * Animation LẶP (loop/idle/talk/heartbeat/laugh/sob): chạy cho đến khi tắt.
    * Khuôn mặt là một bộ tham số (độ mở mắt, mí, độ xiên, má, miệng...). Biểu cảm là bộ tham số mẫu;
      các lớp (chớp mắt, nhìn, nói, rung, nảy, đập) chồng lên nhau mà không cần dựng sẵn ảnh.
"""
import time
import math
from array import array
from random import randint, choice

W, H = 128, 64
LX, RX, CY, EW, EH = 36, 92, 26, 32, 32     # tâm mắt trái/phải, tâm dọc, rộng, cao mắt

# ----- danh sách tên (dùng cho menu thả xuống của Blockly) -----
EXPRESSIONS = ("neutral", "happy", "laugh", "excited", "love", "wink", "surprised", "talk",
               "sad", "cry", "angry", "suspicious", "sleepy", "sleep", "dizzy", "error")
ANIMATIONS = ("blink", "double_blink", "wink", "laugh", "surprise", "shake", "nod", "bounce",
              "look_around", "heartbeat", "dizzy", "fall_asleep", "wake_up")
LOOPS = ("idle", "talk", "heartbeat", "laugh", "sob")
DIRECTIONS = ("center", "left", "right", "up", "down", "up_left", "up_right", "down_left", "down_right")

TEARS, ZZZ, SPIN = 1, 2, 4                   # cờ phụ của biểu cảm

# tên: (mắt trái, mắt phải, miệng, mở, mí, xiên, má, lệch dọc, cờ)
#   hình mắt: rect | up (^) | down (u) | heart | star | ring | spiral | cross
#   miệng: None | smile | frown | flat | o | small | open | laugh | wavy
#   xiên: +1 buồn, -1 giận;  mí: tỉ lệ che từ trên;  má: 0..1 (mắt cười)
_E = {
    "neutral":    ("rect", "rect", None, 1, 0, 0, 0, 0, 0),
    "happy":      ("rect", "rect", "smile", 1, 0, 0, 1, 0, 0),
    "laugh":      ("up", "up", "laugh", 1, 0, 0, 0, 0, 0),
    "excited":    ("star", "star", None, 1, 0, 0, 0, 0, 0),
    "love":       ("heart", "heart", None, 1, 0, 0, 0, 0, 0),
    "wink":       ("rect", "up", "smile", 1, 0, 0, 0, 0, 0),
    "surprised":  ("ring", "ring", "o", 1, 0, 0, 0, 0, 0),
    "talk":       ("rect", "rect", "small", 1, 0, 0, 0, 0, 0),
    "sad":        ("rect", "rect", "frown", 1, 0, 1, 0, 2, 0),
    "cry":        ("rect", "rect", "frown", 1, 0, 1, 0, -2, TEARS),
    "angry":      ("rect", "rect", "flat", 1, 0, -1, 0, 2, 0),
    "suspicious": ("rect", "rect", "flat", 1, 0.5, 0, 0, 2, 0),
    "sleepy":     ("rect", "rect", None, 1, 0.55, 0, 0, 4, ZZZ),
    "sleep":      ("down", "down", None, 1, 0, 0, 0, 0, ZZZ),
    "dizzy":      ("spiral", "spiral", "wavy", 1, 0, 0, 0, 0, SPIN),
    "error":      ("cross", "cross", "flat", 1, 0, 0, 0, 0, 0),
}
_MY = {"smile": 53, "frown": 51, "flat": 52, "o": 53, "small": 50, "open": 47, "laugh": 46, "wavy": 52}
_DIRS = {"center": (0, 0), "left": (-1, 0), "right": (1, 0), "up": (0, -1), "down": (0, 1),
         "up_left": (-1, -1), "up_right": (1, -1), "down_left": (-1, 1), "down_right": (1, 1)}
_GLANCES = ((-1, 0), (1, 0), (-1, -0.6), (1, -0.6), (0, -0.8), (0.8, 0.5), (-0.8, 0.5))
_STAR = [(math.cos(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.45),
          math.sin(-math.pi / 2 + i * math.pi / 5) * (1 if i % 2 == 0 else 0.45)) for i in range(10)]
_BLINKS = ("rect", "ring")                 # chỉ các kiểu mắt này mới chớp được
_OFF2 = ((0, 0), (1, 0), (0, 1), (1, 1))
_OFF3 = ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1))


# ------------------------------------------------------------------ hàm vẽ cơ bản
def _rrect(o, x0, y0, w, h, r, c=1):
    """Hình chữ nhật bo góc."""
    if r > h // 2: r = h // 2
    if r > w // 2: r = w // 2
    if r <= 2:
        o.fill_rect(x0, y0, w, h, c)
        return
    o.fill_rect(x0 + r, y0, w - 2 * r, h, c)
    o.fill_rect(x0, y0 + r, w, h - 2 * r, c)
    q = r - 1                                   # elip bán kính q phủ 2q+1 điểm ảnh, không tràn ra ngoài khung
    o.ellipse(x0 + r, y0 + r, q, q, c, True)
    o.ellipse(x0 + w - r - 1, y0 + r, q, q, c, True)
    o.ellipse(x0 + r, y0 + h - r - 1, q, q, c, True)
    o.ellipse(x0 + w - r - 1, y0 + h - r - 1, q, q, c, True)


def _arc(o, cx, cy, rx, ry, a0, a1, t=3, c=1, n=10):
    """Cung elip dày t px (góc theo độ, trục y hướng xuống: 200..340 = nửa trên, 20..160 = nửa dưới)."""
    off = _OFF3 if t >= 3 else _OFF2
    px = py = None
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        x = int(cx + rx * math.cos(a) + 0.5)
        y = int(cy + ry * math.sin(a) + 0.5)
        if px is not None:
            for dx, dy in off:
                o.line(px + dx, py + dy, x + dx, y + dy, c)
        px, py = x, y


def _thick(o, x0, y0, x1, y1, t=3):
    for dx, dy in (_OFF3 if t >= 3 else _OFF2):
        o.line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, 1)


def _z(o, x, y, s):
    """Chữ z nhỏ cạnh s."""
    _thick(o, x, y, x + s, y, 2)
    _thick(o, x + s, y, x, y + s, 2)
    _thick(o, x, y + s, x + s, y + s, 2)


def _beat(x):
    """Nhịp tim 'thình-thịch' trong 900 ms: trả 0..1."""
    if x < 160:
        return math.sin(math.pi * x / 160)
    if 220 <= x < 400:
        return 0.6 * math.sin(math.pi * (x - 220) / 180)
    return 0.0


# ------------------------------------------------------------------ animation một lần
# mỗi hàm nhận (face, t_ms, tổng_ms) và đặt các lớp chồng an_sx, an_sy (dịch), an_size (phóng), an_open (mở mắt)
def _a_blink(f, t, d):
    f.an_open = abs(2.0 * t / d - 1)


def _a_double_blink(f, t, d):
    h = d / 2
    f.an_open = abs(2.0 * (t % h) / h - 1)


def _a_laugh(f, t, d):
    f.an_sy = -3 * abs(math.sin(t * math.pi / 150))


def _a_surprise(f, t, d):
    if t < 220:
        k = 1 - t / 220
        f.an_size = 1 + 0.3 * k
        f.an_sy = -5 * k


def _a_shake(f, t, d):
    f.an_sx = 7 * (1 - t / d) * math.sin(t / 45)


def _a_nod(f, t, d):
    f.an_sy = 5 * (1 - t / d) * math.sin(t * 2 * math.pi / 400)


def _a_bounce(f, t, d):
    f.an_sy = -9 * abs(math.sin(t * math.pi / 300))


_LOOK_SEQ = ((-1, 0), (-1, -0.7), (1, -0.7), (1, 0.4), (0.3, 0.8), (0, 0))


def _a_look(f, t, d):
    f._gt = _LOOK_SEQ[min(len(_LOOK_SEQ) - 1, int(t * len(_LOOK_SEQ) / d))]


def _a_heartbeat(f, t, d):
    f.an_size = 1 + 0.22 * _beat(t % 900)


def _a_dizzy(f, t, d):
    f.an_sx = 4 * math.sin(t / 110)


def _a_asleep(f, t, d):                      # mi sụp dần, đầu gật gù, rồi ngủ
    if t < 300:
        return
    p = (t - 300) / (d - 300)
    f.cur[1] = max(0.0, min(1.0, p + 0.12 * math.sin(t / 180) * (1 - p)))
    f.cur[4] = 4 * p
    f.an_sy = 2 * math.sin(t / 220) * p
    if p > 0.4:
        f.flags |= ZZZ


def _a_wake(f, t, d):                        # ngủ -> mắt hé -> chớp -> mở to
    if t < 750:
        f._once("a", lambda: f.expression("sleepy", 300))
    elif t < 950:
        f.an_open = abs(2.0 * (t - 750) / 200 - 1)
    else:
        f.an_open = 1.0
        f._once("b", lambda: f.expression("neutral", 350))


# tên: (thời lượng ms, biểu cảm tạm thời, khi xong, hàm)    khi xong: "restore" = về lại biểu cảm cũ
_ANIMS = {
    "blink":        (240, None, None, _a_blink),
    "double_blink": (520, None, None, _a_double_blink),
    "wink":         (1000, "wink", "restore", None),
    "laugh":        (1800, "laugh", "restore", _a_laugh),
    "surprise":     (1600, "surprised", "restore", _a_surprise),
    "shake":        (700, None, None, _a_shake),
    "nod":          (800, None, None, _a_nod),
    "bounce":       (900, None, None, _a_bounce),
    "look_around":  (2600, None, None, _a_look),
    "heartbeat":    (2700, "love", "restore", _a_heartbeat),
    "dizzy":        (2600, "dizzy", "restore", _a_dizzy),
    "fall_asleep":  (3600, "neutral", "sleep", _a_asleep),
    "wake_up":      (1700, None, None, _a_wake),
}


class RobotFace:
    def __init__(self, oled, fps=25):
        self.o = oled
        self._ms = max(1, 1000 // fps)
        now = time.ticks_ms()
        self._t0 = self._t_next = self._t_last = now
        # trạng thái nền
        self.sL = self.sR = "rect"
        self.mouth = None
        self.flags = 0
        self.cur = [1.0, 0.0, 0.0, 0.0, 0.0]            # mở, mí, xiên, má, lệch dọc
        self._expr = "neutral"
        self._tr = None                                  # đang chuyển biểu cảm
        self._trL = self._trR = 1.0
        # các lớp chồng
        self.an_sx = self.an_sy = 0.0
        self.an_size = self.an_open = 1.0
        self.lp_sx = self.lp_sy = 0.0
        self.lp_size = 1.0
        self.bl_open = 1.0
        self._bl_t0 = None
        self._bl_d = 170
        # nhìn
        self.gx = self.gy = 0.0
        self._gt = (0.0, 0.0)
        self._user_look = False
        # vòng lặp / rảnh
        self.loops = set()
        self._mouth_ov = None
        self._mouth_t = now
        self._next_blink = time.ticks_add(now, 2500)
        self._next_glance = time.ticks_add(now, 4000)
        self._glance_end = None
        # animation một lần, giọt nước mắt, khóa vẽ lại
        self._a = None
        self._drops = []
        self._tear_t = now
        self._tear_side = 0
        self._key = None
        self._frames = 0

    # ---------------------------------------------------------------- API công khai
    def expression(self, name, ms=300, wait=False):
        """Đổi biểu cảm. ms=0: đổi ngay. Cùng kiểu mắt thì nội suy; khác kiểu thì nhắm -> đổi -> mở."""
        e = _E[name]
        self._expr = name
        if self._tr is not None:
            self._apply(self._tr[3])
            self._tr = None
            self._trL = self._trR = 1.0
        if ms <= 0:
            self._apply(e)
        else:
            self._tr = [time.ticks_ms(), ms, tuple(self.cur), e, e[0] != self.sL, e[1] != self.sR, False]
        if wait:
            self.wait(ms)

    def play(self, name, wait=True, loop=False, loop_pause_ms=1500):
        """Phát animation một lần hoặc lặp đến khi stop_animation() được gọi."""
        if loop and wait:
            raise ValueError("A looping animation cannot wait for completion")
        dur, pre, post, fn = _ANIMS[name]
        self._finish_anim()
        self._a = [
            time.ticks_ms(), dur, pre, post, fn, self._expr, set(), loop,
            loop_pause_ms, None,
        ]
        if pre:
            self.expression(pre, 200)
        if wait:
            while self._a is not None:
                self.update()
                time.sleep_ms(1)

    def stop_animation(self):
        """Dừng animation và khôi phục biểu cảm phù hợp."""
        a = self._a
        if a is None:
            return
        restore = a[5] if a[3] is None else None
        self._finish_anim()
        if restore is not None and self._expr != restore:
            self.expression(restore, 250)

    def busy(self):
        """True nếu đang phát animation một lần hoặc lặp."""
        return self._a is not None

    def loop(self, name, on=True):
        """Bật/tắt animation LẶP: idle, talk, heartbeat, laugh, sob (xem LOOPS)."""
        if on:
            self.loops.add(name)
        else:
            self.loops.discard(name)

    def idle(self, on=True):
        """Chế độ rảnh: tự chớp mắt (thỉnh thoảng chớp đôi) và thỉnh thoảng liếc nhìn."""
        self.loop("idle", on)

    def talk(self, on=True):
        """Miệng đóng-mở theo nhịp ngẫu nhiên như đang nói."""
        self.loop("talk", on)

    def talk_for(self, seconds):
        self.talk(True)
        self.wait(int(seconds * 1000))
        self.talk(False)

    def heartbeat(self, on=True):
        self.loop("heartbeat", on)

    def look(self, direction="center"):
        """Nhìn theo hướng (xem DIRECTIONS). 'center' = nhìn thẳng và cho phép chế độ rảnh liếc ngẫu nhiên."""
        self._gt = _DIRS[direction]
        self._user_look = direction != "center"

    def look_xy(self, x, y):
        """Nhìn theo toạ độ -1..1 (x: trái-phải, y: trên-dưới), ví dụ lấy từ cảm biến/camera. Mượt tự động."""
        self._gt = (max(-1.0, min(1.0, x)), max(-1.0, min(1.0, y)))
        self._user_look = True

    def blink(self, wait=False):
        self.play("blink", wait)

    def wait(self, ms):
        """Đợi ms mili giây nhưng vẫn chạy animation (dùng thay time.sleep)."""
        end = time.ticks_add(time.ticks_ms(), ms)
        while time.ticks_diff(end, time.ticks_ms()) > 0:
            self.update()
            time.sleep_ms(1)

    def run(self):
        """Vòng lặp vô hạn chỉ để chạy animation nền (idle...)."""
        while True:
            self.update()
            time.sleep_ms(1)

    # ---------------------------------------------------------------- nội bộ: cập nhật
    def update(self):
        """Gọi liên tục. Trả True nếu vừa vẽ khung mới ra màn hình."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._t_next) < 0:
            return False
        self._t_next = time.ticks_add(now, self._ms)
        dt = time.ticks_diff(now, self._t_last)
        self._t_last = now
        if dt > 200:
            dt = 200
        t = time.ticks_diff(now, self._t0)
        self._step_transition(now)
        self._step_anim(now)
        self._step_loops(now, t)
        self._step_idle(now)
        k = dt / 110.0
        if k > 1: k = 1.0
        self.gx += (self._gt[0] - self.gx) * k
        self.gy += (self._gt[1] - self.gy) * k
        self._step_tears(now, dt)
        return self._render(t)

    def _apply(self, e):
        self.sL, self.sR, self.mouth = e[0], e[1], e[2]
        self.cur = [float(v) for v in e[3:8]]
        self.flags = e[8]

    def _once(self, key, fn):
        s = self._a[6]
        if key not in s:
            s.add(key)
            fn()

    def _step_transition(self, now):
        tr = self._tr
        if tr is None:
            return
        p = time.ticks_diff(now, tr[0]) / tr[1]
        e = tr[3]
        if p >= 1:
            self._apply(e)
            self._tr = None
            self._trL = self._trR = 1.0
            return
        if tr[4] or tr[5]:                       # đổi kiểu mắt: nhắm -> đổi -> mở
            if p < 0.4:
                k = 1 - p / 0.4
            else:
                if not tr[6]:
                    self._apply(e)
                    tr[6] = True
                k = (p - 0.4) / 0.6
            self._trL = k if tr[4] else 1.0
            self._trR = k if tr[5] else 1.0
        else:                                    # cùng kiểu mắt: nội suy các tham số
            q = p * p * (3 - 2 * p)
            frm, to = tr[2], e[3:8]
            for i in range(5):
                self.cur[i] = frm[i] + (to[i] - frm[i]) * q
            if p >= 0.5 and not tr[6]:
                self.mouth = e[2]
                self.flags = e[8]
                tr[6] = True

    def _step_anim(self, now):
        a = self._a
        if a is None:
            return
        if a[7] and a[9] is not None:
            if time.ticks_diff(now, a[9]) < a[8]:
                return
            a[0] = now
            a[6].clear()
            a[9] = None
            if a[2]:
                self.expression(a[2], 200)
            elif a[4] == _a_wake:
                self.expression("sleep", 200)
            return

        t = time.ticks_diff(now, a[0])
        if t >= a[1]:
            if a[7]:
                self.an_sx = self.an_sy = 0.0
                self.an_size = self.an_open = 1.0
                if not self._user_look:
                    self._gt = (0.0, 0.0)
                if a[3] == "restore":
                    self.expression(a[5], 200)
                elif a[3]:
                    self.expression(a[3], 200)
                elif a[4] == _a_wake:
                    self.expression("sleep", 200)
                a[9] = now
            else:
                self._finish_anim()
        elif a[4] is not None:
            a[4](self, t, a[1])

    def _finish_anim(self):
        a = self._a
        if a is None:
            return
        self._a = None
        self.an_sx = self.an_sy = 0.0
        self.an_size = self.an_open = 1.0
        if not self._user_look:
            self._gt = (0.0, 0.0)
        if a[3] == "restore":
            self.expression(a[5], 250)
        elif a[3]:
            self.expression(a[3], 300)

    def _step_loops(self, now, t):
        L = self.loops
        sy = 0.0
        sx = 0.0
        size = 1.0
        if "heartbeat" in L:
            beat = _beat(t % 900)
            size = 1 + 0.28 * beat
            sy -= 1.5 * beat
        if "laugh" in L:
            phase = t * math.pi / 190
            sy -= 4.5 * abs(math.sin(phase))
            sx += 2.5 * math.sin(phase * 2)
            size *= 1 + 0.035 * abs(math.sin(phase))
        if "sob" in L:
            phase = t * math.pi / 180
            sy += 3.5 * abs(math.sin(phase))
            sx += 1.8 * math.sin(phase * 2)
        if self.sL == "down" and self.sR == "down":          # ngủ: thở nhẹ
            sy += 1.5 * math.sin(t / 650.0)
        self.lp_sx, self.lp_sy, self.lp_size = sx, sy, size
        if "talk" in L:
            if time.ticks_diff(now, self._mouth_t) >= 0:
                k = choice(("small", "open", "flat", "small", "open"))
                while k == self._mouth_ov:
                    k = choice(("small", "open", "flat", "small", "open"))
                self._mouth_ov = k
                self._mouth_t = time.ticks_add(now, randint(90, 190))
        else:
            self._mouth_ov = None

    def _step_idle(self, now):
        if self._bl_t0 is not None:                          # đang chớp
            p = time.ticks_diff(now, self._bl_t0) / self._bl_d
            if p >= 1:
                self._bl_t0 = None
                self.bl_open = 1.0
            else:
                self.bl_open = abs(2 * p - 1)
        if "idle" not in self.loops:
            return
        if self._bl_t0 is None and time.ticks_diff(now, self._next_blink) >= 0:
            self._bl_t0 = now
            self._bl_d = 170
            gap = 320 if randint(0, 4) == 0 else randint(2000, 5200)    # thỉnh thoảng chớp đôi
            self._next_blink = time.ticks_add(now, gap)
        if not self._user_look and self._a is None:
            if self._glance_end is not None:
                if time.ticks_diff(now, self._glance_end) >= 0:
                    self._gt = (0.0, 0.0)
                    self._glance_end = None
                    self._next_glance = time.ticks_add(now, randint(2500, 7000))
            elif time.ticks_diff(now, self._next_glance) >= 0:
                self._gt = choice(_GLANCES)
                self._glance_end = time.ticks_add(now, randint(600, 1400))

    def _step_tears(self, now, dt):
        d = self._drops
        for i in range(len(d) - 1, -1, -1):
            d[i][1] += 40.0 * dt / 1000
            if d[i][1] > H + 4:
                d.pop(i)
        if self.flags & TEARS and len(d) < 5 and time.ticks_diff(now, self._tear_t) >= 0:
            x = LX - 10 if self._tear_side == 0 else RX + 10
            d.append([float(x), float(CY + 14)])
            self._tear_side ^= 1
            self._tear_t = time.ticks_add(now, 650)

    # ---------------------------------------------------------------- nội bộ: vẽ
    def _render(self, t):
        c = self.cur
        sx = self.an_sx + self.lp_sx
        sy = self.an_sy + self.lp_sy
        size = self.an_size * self.lp_size
        ex = int(self.gx * 14 + sx)
        ey = int(self.gy * 8 + sy + c[4])
        mx = int(self.gx * 8 + sx)
        my = int(sy + self.gy * 5 + c[4] / 2)
        bl = self.bl_open * self.an_open
        sqL = c[0] * (bl if self.sL in _BLINKS else 1.0) * self._trL
        sqR = c[0] * (bl if self.sR in _BLINKS else 1.0) * self._trR
        mouth = self._mouth_ov or self.mouth
        spin = t * 0.006 if self.flags & SPIN else 0.0
        zc = (1 + (t // 700) % 3) if self.flags & ZZZ else 0
        drops = tuple((int(d[0]), int(d[1])) for d in self._drops)
        key = (self.sL, self.sR, mouth, int(sqL * 24), int(sqR * 24), int(c[1] * 20), int(c[2] * 20),
               int(c[3] * 20), ex, ey, mx, my, int(size * 24), int(spin * 4), zc, drops)
        if key == self._key:
            return False
        self._key = key
        o = self.o
        o.fill(0)
        cy = CY + ey
        self._eye(o, LX + ex, cy, self.sL, sqL, size, spin, True)
        self._eye(o, RX + ex, cy, self.sR, sqR, size, spin, False)
        if mouth:
            self._mouth(o, mouth, 64 + mx, my)
        for dx, dy in drops:
            o.ellipse(dx, dy + 3, 2, 3, 1, True)
            o.poly(0, 0, array('h', [dx, dy - 4, dx - 2, dy + 1, dx + 2, dy + 1]), 1, True)
        if zc:
            _z(o, 96, 20, 5)
            if zc > 1: _z(o, 104, 10, 7)
            if zc > 2: _z(o, 113, 0, 9)
        o.show()
        self._frames += 1
        return True

    def _eye(self, o, cx, cy, shape, sq, size, spin, left):
        c = self.cur
        if sq < 0.12 and shape != "down" or sq < 0.5 and shape in ("up", "down"):
            o.fill_rect(cx - 13, cy + 1, 27, 3, 1)               # mắt nhắm (đường ngang)
            return
        if shape == "rect":
            w = int(EW * size)
            h = max(3, int(EH * size * sq))
            x0, y0 = cx - w // 2, cy - h // 2
            _rrect(o, x0, y0, w, h, 10)
            if c[1] > 0.01:                                        # mí trên phẳng
                o.fill_rect(x0 - 1, y0 - 1, w + 2, int(h * c[1]) + 1, 0)
            if abs(c[2]) > 0.02:                                   # mí xiên: +buồn, -giận
                amt = int(h * 0.55 * abs(c[2]))
                x1 = x0 + w
                angry = c[2] < 0
                if angry == left:
                    pts = [x0 - 1, y0 - 1, x1 + 1, y0 - 1, x1 + 1, y0 + amt]
                else:
                    pts = [x0 - 1, y0 - 1, x1 + 1, y0 - 1, x0 - 1, y0 + amt]
                o.poly(0, 0, array('h', pts), 0, True)
            if c[3] > 0.01:                                        # má dâng lên: mắt cười
                top = y0 + int(h * (1.2 - 0.62 * c[3]))
                ry = int(h * 0.52)
                o.ellipse(cx, top + ry, w // 2 + 6, ry, 0, True)
        elif shape == "up":
            _arc(o, cx, cy + 8, 15, 12, 200, 340, 4)
        elif shape == "down":
            _arc(o, cx, cy + 7, 15, 11, 20, 160, 4)
        elif shape == "ring":
            r = int(17 * size)
            ry = max(2, int(r * sq))
            o.ellipse(cx, cy - 1, r, ry, 1, True)
            o.ellipse(cx, cy, 5, max(1, int(5 * sq)), 0, True)
        elif shape == "heart":
            s = 34 * size
            r = int(0.29 * s)
            ry = max(1, int(r * sq))
            cyh = cy + 2
            o.ellipse(cx - int(0.24 * s), cyh - int(0.17 * s * sq), r, ry, 1, True)
            o.ellipse(cx + int(0.24 * s), cyh - int(0.17 * s * sq), r, ry, 1, True)
            o.poly(0, 0, array('h', [cx - int(0.52 * s), cyh - int(0.13 * s * sq), cx + int(0.52 * s),
                                     cyh - int(0.13 * s * sq), cx, cyh + int(0.52 * s * sq)]), 1, True)
        elif shape == "star":
            r = 17 * size
            pts = array('h')
            for ux, uy in _STAR:
                pts.append(int(cx + r * ux))
                pts.append(int(cy + 2 + r * uy * sq))
            o.poly(0, 0, pts, 1, True)
        elif shape == "spiral":
            px = py = None
            for i in range(26):
                a = i / 25.0
                r = 15 * a
                ang = a * 3.2 * 2 * math.pi + spin
                x = int(cx + r * math.cos(ang))
                y = int(cy + 2 + r * math.sin(ang))
                if px is not None:
                    o.line(px, py, x, y, 1)
                    o.line(px + 1, py, x + 1, y, 1)
                px, py = x, y
        elif shape == "cross":
            _thick(o, cx - 13, cy - 11, cx + 13, cy + 15, 3)
            _thick(o, cx - 13, cy + 15, cx + 13, cy - 11, 3)

    def _mouth(self, o, kind, x, mdy):
        y = _MY[kind] + mdy
        if kind == "smile":
            _arc(o, x, y - 1, 9, 7, 20, 160, 3)
        elif kind == "frown":
            _arc(o, x, y + 7, 9, 7, 200, 340, 3)
        elif kind == "flat":
            o.fill_rect(x - 9, y + 1, 18, 3, 1)
        elif kind == "o":
            o.ellipse(x, y + 2, 5, 6, 1)
            o.ellipse(x, y + 2, 4, 5, 1)
        elif kind == "small":
            _rrect(o, x - 8, y - 1, 16, 6, 3)
        elif kind == "open":
            _rrect(o, x - 11, y - 3, 22, 15, 6)
        elif kind == "laugh":
            for k in range(13):                                   # nửa đĩa phía dưới
                w = int(14 * math.sqrt(1 - (k / 12.0) ** 2))
                o.fill_rect(x - w, y + k, 2 * w + 1, 1, 1)
        elif kind == "wavy":
            px = x - 12
            py = y + 3
            for i in range(1, 9):
                nx = x - 12 + i * 3
                ny = y + 3 + (3 if i % 2 else -1)
                o.line(px, py, nx, ny, 1)
                o.line(px, py + 1, nx, ny + 1, 1)
                px, py = nx, ny

"""
Gamepad input for 8BitDo SN30 Pro (Windows X-Input).

Translates pad buttons, D-pad, and left stick into the same KEY_* values
the rest of the game already handles. Keyboard input is unchanged.
"""
import pygame
from constants import (
    Direction,
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT,
    KEY_CONFIRM, KEY_CANCEL, KEY_MENU, KEY_QUICKSAVE,
)

STICK_DEADZONE = 0.35
REPEAT_DELAY = 0.28
REPEAT_RATE = 0.09

# X-Input button indices (SN30 Pro in Windows mode: X + Start)
GPAD_CONFIRM = 0   # South: printed B / X-Input A
GPAD_CANCEL = 1    # East: printed A / X-Input B
GPAD_SELECT = 6    # Select (-)
GPAD_START = 7     # Start (+)

BUTTON_TO_KEY = {
    GPAD_CONFIRM: KEY_CONFIRM[0],
    GPAD_CANCEL: KEY_CANCEL[0],
    GPAD_START: KEY_MENU[0],
    GPAD_SELECT: KEY_QUICKSAVE[0],
}

DIR_TO_KEY = {
    Direction.UP: KEY_UP[0],
    Direction.DOWN: KEY_DOWN[0],
    Direction.LEFT: KEY_LEFT[0],
    Direction.RIGHT: KEY_RIGHT[0],
}


def button_to_key(button):
    """Map an X-Input button index to a pygame key, or None if unmapped."""
    return BUTTON_TO_KEY.get(button)


def hat_to_direction(hx, hy):
    """Map a pygame hat tuple to a single Direction (up/down beat left/right)."""
    if hy > 0:
        return Direction.UP
    if hy < 0:
        return Direction.DOWN
    if hx < 0:
        return Direction.LEFT
    if hx > 0:
        return Direction.RIGHT
    return None


def stick_to_direction(ax, ay, deadzone=STICK_DEADZONE):
    """Map left-stick axes to a single Direction, or None inside the deadzone."""
    if abs(ax) < deadzone and abs(ay) < deadzone:
        return None
    if abs(ay) >= abs(ax):
        return Direction.UP if ay < 0 else Direction.DOWN
    return Direction.LEFT if ax < 0 else Direction.RIGHT


def direction_to_key(direction):
    return DIR_TO_KEY.get(direction)


def make_keydown(key):
    return pygame.event.Event(pygame.KEYDOWN, {
        "key": key,
        "mod": 0,
        "unicode": "",
        "scancode": 0,
    })


class InputManager:
    """Owns joystick lifecycle and translates pad input into KEYDOWN events."""

    def __init__(self):
        self.joystick = None
        self.instance_id = None
        self._held_dir = None
        self._hold_time = 0.0
        self._repeat_armed = False
        try:
            pygame.joystick.init()
        except pygame.error:
            return
        if pygame.joystick.get_count() > 0:
            self._open(0)

    @property
    def connected(self):
        return self.joystick is not None

    def process(self, events, dt):
        """Handle hot-plug and buttons; poll hat/stick; return (keydowns, notices)."""
        extra = []
        notices = []

        for event in events:
            if event.type == pygame.JOYDEVICEADDED:
                if self.joystick is None:
                    idx = getattr(event, "device_index", 0)
                    if self._open(idx):
                        notices.append(f"Controller connected: {self.joystick.get_name()}")
            elif event.type == pygame.JOYDEVICEREMOVED:
                removed_id = getattr(event, "instance_id", None)
                if self.joystick is not None and removed_id == self.instance_id:
                    name = self.joystick.get_name()
                    self._close()
                    notices.append(f"Controller disconnected: {name}")
                    if pygame.joystick.get_count() > 0:
                        if self._open(0):
                            notices.append(f"Controller connected: {self.joystick.get_name()}")
            elif event.type == pygame.JOYBUTTONDOWN:
                key = button_to_key(event.button)
                if key is not None:
                    extra.append(make_keydown(key))

        direction = self._read_direction()
        extra.extend(self._update_repeat(direction, dt))
        return extra, notices

    def get_held_directions(self):
        """Exclusive held direction from D-pad / left stick (for overworld walk)."""
        if self._held_dir is None:
            return set()
        return {self._held_dir}

    def _open(self, device_index):
        try:
            if device_index < 0 or device_index >= pygame.joystick.get_count():
                return False
            joy = pygame.joystick.Joystick(device_index)
            joy.init()
            self.joystick = joy
            self.instance_id = joy.get_instance_id()
            self._held_dir = None
            self._hold_time = 0.0
            self._repeat_armed = False
            return True
        except pygame.error:
            self.joystick = None
            self.instance_id = None
            return False

    def _close(self):
        if self.joystick is not None:
            try:
                self.joystick.quit()
            except pygame.error:
                pass
        self.joystick = None
        self.instance_id = None
        self._held_dir = None
        self._hold_time = 0.0
        self._repeat_armed = False

    def _read_direction(self):
        if self.joystick is None:
            return None
        try:
            if self.joystick.get_numhats() > 0:
                hx, hy = self.joystick.get_hat(0)
                hat_dir = hat_to_direction(hx, hy)
                if hat_dir is not None:
                    return hat_dir
            if self.joystick.get_numaxes() >= 2:
                ax = self.joystick.get_axis(0)
                ay = self.joystick.get_axis(1)
                return stick_to_direction(ax, ay)
        except pygame.error:
            return None
        return None

    def _update_repeat(self, direction, dt):
        extra = []
        if direction != self._held_dir:
            self._held_dir = direction
            self._hold_time = 0.0
            self._repeat_armed = False
            key = direction_to_key(direction)
            if key is not None:
                extra.append(make_keydown(key))
            return extra

        if direction is None:
            return extra

        self._hold_time += dt
        threshold = REPEAT_RATE if self._repeat_armed else REPEAT_DELAY
        if self._hold_time >= threshold:
            self._hold_time = 0.0
            self._repeat_armed = True
            key = direction_to_key(direction)
            if key is not None:
                extra.append(make_keydown(key))
        return extra

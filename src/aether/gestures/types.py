from enum import Enum


class Gesture(Enum):
    UNKNOWN = "unknown"
    OPEN_PALM = "open_palm"
    FIST = "fist"
    POINT = "point"
    PINCH = "pinch"
    TWO_FINGERS = "two_fingers"
    LEFT_CLICK = "left_click"
    RIGHT_CLICK = "right_click"
    LEFT_PRESS = "left_press"
    RIGHT_PRESS = "right_press"

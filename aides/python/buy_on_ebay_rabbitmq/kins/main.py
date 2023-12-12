from .appearance.server import Appearance
from .brain.server import Brain


def appearance():
    return Appearance()


def brain():
    return Brain()

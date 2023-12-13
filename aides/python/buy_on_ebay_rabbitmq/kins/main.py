from .appearance.server import Appearance
from .brain.server import Brain
from .keeper.server import Keeper


def appearance():
    return Appearance()


def brain():
    return Brain()


def keeper():
    return Keeper()

import tkinter
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode
import time
import pickle
import io

MC = MouseController()
KC = KeyboardController()

class AnInput():

    def __init__(self, type) -> None:
        self.type = str(type)

    def Playback(self):
        pass

    def GetType(self) -> str:
        return self.type
    

class KeyboardInput(AnInput):

    # key is key, down is keyup or keydown (T/F)
    def __init__(self, key, down):
        super().__init__(f"key|{key}|{down}")
        self.key = key
        self.down = down

    def __str__(self) -> str:
        return f"Key {self.key} " + ("down" if self.down else  "up")

    def __repr__(self) -> str:
        return "ki|" + str(self.key) + "|" + str(self.down)

    def Playback(self):
        match self.down:
            case True:
                KC.press(self.key)
            case False:
                KC.release(self.key)


class KeyPressed(AnInput):

    def __init__(self, key: Key) -> None:
        super().__init__(f"{key}|pressed")
        self.key = key
    
    def __str__(self) -> str:
        return f"{self.key} pressed"

    def __repr__(self) -> str:
        return "kp|" + str(self.key)

    def Playback(self):
        KC.press(self.key)
        KC.release(self.key)


class MouseClick(AnInput):
    # type = move, click, or scroll
    def __init__(self, button, down):
        super().__init__(f"click|{button}|{down}")
        self.button = button
        self.down = down

    def __str__(self) -> str:
        return f"{self.button}" + (" down" if self.down else " up")

    def __repr__(self) -> str:
        return "mc|" + str(self.button) + "|" + str(self.down)
                
    def Playback(self):
        match self.down:
            case True:
                MC.press(self.button)
            case False:
                MC.release(self.button)
                return


class WholeMouseClick(AnInput):
    def __init__(self, button) -> None:
        super().__init__(f"click{button}")
        self.button = button

    def __str__(self) -> str:
        return f"{self.button} clicked"

    def __repr__(self) -> str:
        return "wmc|" + str(self.button)

    def Playback(self):
        MC.press(self.button)
        MC.release(self.button)

class MouseMove(AnInput):
    def __init__(self, pos) -> None:
        super().__init__("move")
        self.pos = pos

    def __str__(self) -> str:
        return f"Move to {self.pos}"

    def __repr__(self) -> str:
        return "mm|" + str(self.pos).replace(' ', '')

    def Playback(self):
        MC.position = self.pos

class MouseScroll(AnInput):
    def __init__(self, amount) -> None:
        super().__init__("scroll")
        self.amount = amount

    def __str__(self) -> str:
        return f"Scroll {self.amount} lines"

    def __repr__(self) -> str:
        return "ms|" + str(self.amount)

    def Playback(self):
        MC.scroll(0, self.amount)
        
class DelayedInput(AnInput):

    def __init__(self, time) -> None:
        super().__init__(f"wait|{time}")
        self.time = time

    def __str__(self) -> str:
        return "wait {0:5.3f} seconds".format(self.time)

    def __repr__(self) -> str:
        return "di|" + str(self.time)

    def Playback(self):
        time.sleep(self.time)



AnInputTypes = {'ki' : type(KeyboardInput),
        'kp' : type(KeyPressed),
        'mc' : type(MouseClick),
        'wmc' : type(WholeMouseClick),
        'mm' : type(MouseMove),
        'ms' : type(MouseScroll),
        'di' : type(DelayedInput)}
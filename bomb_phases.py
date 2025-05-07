#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: Elianna Ayala, Nathan Eshman, Diego Diaz
#################################

# import the configs
from bomb_configs import *
# other imports
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
import os
import sys
from bomb_configs import PRIMARY_COLOR_WIRES
from PIL import Image, ImageTk


#########
# classes
#########
# the LCD display GUI
class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        window.attributes("-fullscreen", True)
        self._timer = None
        self._button = None
        self._puzzle_frames = {}  # Stores active puzzle frames
        self.setupBoot()
        
    def showGameOver(self):
        self.clearPuzzle("riddle")
        frame = Frame(self, bg="black")
        frame.grid(row=7, column=0, columnspan=3)
        label = Label(frame, text="You Lose!", fg="red", bg="black", font=("Courier New", 32))
        label.pack(pady=100)


    def showPuzzle(self, name, widget_builder):
        self.clearPuzzle(name)
        frame = Frame(self, bg="black")
        self._puzzle_frames[name] = frame
        frame.grid(row=7, column=0, columnspan=3)
        widget_builder(frame)   

    def startGame(self, on_start):
        if self._start_screen:
            self._start_screen.destroy()
            self._start_screen = None
        on_start()

    def clearPuzzle(self, name):
        frame = self._puzzle_frames.pop(name, None)
        if frame:
            frame.destroy()

    def showRiddle(self):
        def builder(frame):
            self._lriddle = Label(
                frame,
                bg="black",
                fg="yellow",
                font=("Courier New", 14),
                text="RIDDLE: What did Phineas & Ferb build first?\n1-Time Machine  2-Roller Coaster  3-Robot Dog  4-Spaceship"
            )
            self._lriddle.pack()
        self.showPuzzle("riddle", builder)
           
    def showTrianglePuzzle(self):
        def builder(frame):
            img = Image.open("HOW MANY TRIANGLES.png").resize((1920, 1080))
            self._img_triangle = ImageTk.PhotoImage(img)
            label_img = Label(frame, image=self._img_triangle, bg="black")
            label_img.pack()
            label_text = Label(frame, text="How many triangles?", fg="white", bg="black", font=("Courier New", 16))
            label_text.pack()
        self.showPuzzle("triangle", builder)

    def showKeypadPuzzle(self):
        def builder(frame):
            label = Label(frame, text=f"Enter the passcode:\n{passphrase}", fg="white", bg="black", font=("Courier New", 18))
            label.pack(pady=40)
        self.showPuzzle("keypad", builder)

    def showWiresPuzzle(self):
        def builder(frame):
            label = Label(frame, text="Unplug the PRIMARY COLOR wires (Red, Blue, Yellow).", fg="white", bg="black", font=("Courier New", 16))
            label.pack()
        self.showPuzzle("wires", builder)

    def showButtonPuzzle(self):
        def builder(frame):
            label = Label(frame, text="Wait for the right time and press the button!", fg="white", bg="black", font=("Courier New", 16))
            label.pack()
        self.showPuzzle("button", builder)

    def setupBoot(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self._lscroll = Label(self, bg="black", fg="white", font=("Courier New", 14), text="", justify=LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=W)
        self.pack(fill=BOTH, expand=True)

    def setup(self):
        self._ltimer = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=W)
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        self._lriddle_debug = Label(self, bg="black", fg="cyan", font=("Courier New", 14), text="")
        self._lriddle_debug.grid(row=6, column=0, columnspan=2, sticky=W)
        self._lriddle = Label(self, bg="black", fg="yellow", font=("Courier New", 14), text="")
        self._lriddle.grid(row=6, column=0, columnspan=2, sticky=W)
        self._lstrikes = Label(self, bg="black", fg="#ff5555", font=("Courier New", 18), text="Strikes left: 5")
        self._lstrikes.grid(row=8, column=2, sticky=SE, padx=20, pady=10)
        self._lkeypad_feedback = Label(self, bg="black", fg="white", font=("Courier New", 20), text="")
        self._lkeypad_feedback.grid(row=6, column=1, pady=10)     

        
    def showKeypadFeedback(self, message, color="white"):
        self._lkeypad_feedback.config(text=message, fg=color)
        self.after(1500, lambda: self._lkeypad_feedback.config(text=""))

        if SHOW_BUTTONS:
            self._bpause = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Pause", anchor=CENTER, command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

        if FIRST_GAME_IS_RIDDLE:
            self.showRiddle()
        if RIDDLE_MODE:
            self.showRiddle()

    def setTimer(self, timer):
        self._timer = timer

    def setButton(self, button):
        self._button = button

    def pause(self):
        if RPi:
            self._timer.pause()

    def conclusion(self, success=False):
        self._lscroll["text"] = ""
        self._ltimer.destroy()
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()
        if SHOW_BUTTONS:
            self._bpause.destroy()
            self._bquit.destroy()
        self._bretry = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Retry", anchor=CENTER, command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)
        self._bquit = tkinter.Button(self, bg="red", fg="white", font=("Courier New", 18), text="Quit", anchor=CENTER, command=self.quit)
        self._bquit.grid(row=1, column=2, pady=40)

    def retry(self):
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    def quit(self):
        if RPi:
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            for pin in self._button._rgb:
                pin.value = True
        exit(0)

# template (superclass) for various bomb components/phases
class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        # phases have an electronic component (which usually represents the GPIO pins)
        self._component = component
        # phases have a target value (e.g., a specific combination on the keypad, the proper jumper wires to "cut", etc)
        self._target = target
        # phases can be successfully defused
        self._defused = False
        # phases can be failed (which result in a strike)
        self._failed = False
        # phases have a value (e.g., a pushbutton can be True/Pressed or False/Released, several jumper wires can be "cut"/False, etc)
        self._value = None
        # phase threads are either running or not
        self._running = False

# the timer phase
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # the default value is the specified initial value
        self._value = initial_value
        # is the timer paused?
        self._paused = False
        # initialize the timer's minutes/seconds representation
        self._min = ""
        self._sec = ""
        # by default, each tick is 1 second
        self._interval = 1

    # runs the thread
    def run(self):
        self._running = True
        while self._running:
            try:
                if not self._paused:
                    self._update()
                    print(f"[DEBUG] Timer value = {self._value}")  # Add this
                    self._component.print(str(self))
                    if self._value == 0:
                        print("[DEBUG] Timer hit 0")
                        self._running = False
                        break
                    sleep(self._interval)
                    self._value -= 1
                else:
                    sleep(0.1)
            except Exception as e:
                print(f"[ERROR] Timer crashed: {e}")
                self._running = False
                break



    # updates the timer (only internally called)
    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    # pauses and unpauses the timer
    def pause(self):
        # toggle the paused state
        self._paused = not self._paused
        # blink the 7-segment display when paused
        self._component.blink_rate = (2 if self._paused else 0)

    # returns the timer as a string (mm:ss)
    def __str__(self):
        if not self._min or not self._sec:
            self._update()
        return f"{self._min}:{self._sec}"


# the keypad phase

class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        self._value = ""

    def run(self):
        self._running = True
        while True:
            if not self._running:
                sleep(0.1)
                continue

            if self._component.pressed_keys:
                while self._component.pressed_keys:
                    try:
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)

                self._value += str(key)
                print(f"[DEBUG] Key pressed: {key}, Current input: {self._value}")

                if self._value == self._target:
                    self._defused = True
                    print("[DEBUG] Keypad defused!")

                elif self._value != self._target[0:len(self._value)]:
                    self._failed = True
                    print("[DEBUG] Incorrect keypad input, resetting...")
                    self._value = ""  # reset on wrong input

            sleep(0.1)

    def __str__(self):
        if self._defused:
            return "DEFUSED"
        return self._value if self._value else ""

# the jumper wires phase
class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)
        self._locked_in = False  # 🆕 New flag

    def lock_in(self):
        self._locked_in = True

    def is_correct(self):
        # Read current unplugged state and check if the unplugged wires match the primary color wires
        value_bin = "".join([str(int(pin.value)) for pin in self._component])
        value_dec = int(value_bin, 2)
        expected_value = sum([2**i for i in PRIMARY_COLOR_WIRES])
        return value_dec == expected_value


    def run(self):
        self._running = True
        while self._running:
            try:
                value_bin = "".join([str(int(pin.value)) for pin in self._component])
                self._value = value_bin
                # No need to auto-fail — we only evaluate when button is pressed
                if self._locked_in:
                    value_dec = int(value_bin, 2)
                    expected_value = sum([2**i for i in PRIMARY_COLOR_WIRES])
                    if value_dec == expected_value:
                        self._defused = True
                        self._running = False
                    # Reset lock after checking
                    self._locked_in = False
            except Exception as e:
                print(f"[ERROR] Wires phase: {e}")
            sleep(0.1)


    def __str__(self):
        if self._defused:
            return "DEFUSED"
        if self._value is None:
            return "WAITING"
        return f"{self._value}/{int(self._value, 2)}"



# the pushbutton phase
class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        self._value = False
        self._pressed = False
        self._rgb = component_rgb
        self._color = color
        self._timer = timer
        self._enabled_for_game = True

    def run(self):
        self._running = True

        while self._running:
            prev_value = self._value
            self._value = self._component.value

            if self._value and not prev_value:
                print("[DEBUG] Button pressed")
                if triangle_puzzle._running:
                    triangle_puzzle.press_button()

            sleep(0.1)


    
class TrianglePuzzle(PhaseThread):
    def __init__(self, correct_answer, timer, gui, name="TrianglePuzzle"):
        super().__init__(name)
        self._press_count = 0
        self._correct_answer = correct_answer
        self._timer = timer
        self._gui = gui  # ✅ store gui reference

    def run(self):
        self._running = True
        self._press_count = 0
        if hasattr(self._gui, "_ltriangle_status"):
            self._gui._ltriangle_status.config(
                text=f"Pressed: {self._press_count}/{self._correct_answer}"
            )

    def press_button(self):
        if not self._running:
            return

        self._press_count += 1
        print(f"[DEBUG] Triangle button presses: {self._press_count}")

        if hasattr(self._gui, "_ltriangle_status"):
            self._gui._ltriangle_status.config(
                text=f"Pressed: {self._press_count}/{self._correct_answer}"
            )

        if self._press_count >= self._correct_answer:
            self._defused = True
            self._running = False
            print("[DEBUG] Triangle Puzzle solved!")

            
class BaseTogglePhase(Thread):
    def __init__(self, component, target, name="BaseToggle"):
        super().__init__(name=name, daemon=True)
        self._component = component
        self._target = target
        self._value = None
        self._defused = False
        self._failed = False
        self._running = False

    def read_value(self):
        value_bin = "".join([str(int(pin.value)) for pin in self._component])
        self._value = value_bin
        value_dec = int(value_bin, 2)
        return value_bin, value_dec

    def __str__(self):
        if self._defused:
            return "DEFUSED"
        if self._value is None:
            return "WAITING"
        return f"{self._value}/{int(self._value, 2)}"

# the toggle switches phase
class Toggles(BaseTogglePhase):
    def run(self):
        self._running = True
        while self._running:
            try:
                _, value_dec = self.read_value()
                if value_dec == self._target:
                    self._defused = True
                elif value_dec != 0 and value_dec != self._target:
                    self._failed = True
                  
            except Exception as e:
                print(f"[ERROR] Toggles: {e}")
            sleep(0.1)


class RiddleToggles(BaseTogglePhase):
    def __init__(self, component, target, gui, on_defused, on_strike, name="RiddleToggles"):
        super().__init__(component, target, name)
        self._gui = gui
        self._on_defused = on_defused
        self._on_strike = on_strike
        self._last_wrong = None
        
    def set_state(self, bits):
        for pin, val in zip(self._component, bits):
            pin.value = bool(val)
    
    def read_value(self):
        if hasattr(self, "_simulated_bits"):
            value_bin = "".join([str(int(v)) for v in self._simulated_bits])
        else:
            value_bin = "".join([str(int(pin.value)) for pin in self._component])

        value_dec = int(value_bin, 2)
        return value_bin, value_dec



    def run(self):
        global gui, strikes_left
        self._running = True
        while self._running:
            try:
                # ✅ Don't process anything if already defused
                if self._defused:
                    sleep(0.2)
                    continue

                _, value_dec = self.read_value()
                print("Toggle bits:", [int(pin.value) for pin in self._component])
                print(value_dec == self._target, value_dec,  self._target)

                if value_dec == self._target:
                    self._defused = True
                    print("[DEBUG] Riddle defused!")
                    if hasattr(self._gui, "_lriddle"):
                        self._gui._lriddle.destroy()
                    if hasattr(self._gui, "showCorrect"):
                        self._gui.showCorrect()
                    self._on_defused()

                elif value_dec != 0 and value_dec != self._target:
                    if self._last_wrong != value_dec:
                        print(f"[DEBUG] Incorrect toggle value: {value_dec}, expected {self._target}")
                        strikes_left = self._on_strike()  # ✅ Strike handled here only
                        self._last_wrong = value_dec


                        if strikes_left <= 0:
                            print("[DEBUG] No strikes left — game over")
                            self._running = False
                            self._gui.after(200, self._gui.showGameOver)
                            sleep(2)
                            os._exit(0)

                        else:
                            self._gui._lriddle_debug["text"] = "Wrong! Try again..."
                            self._gui.after(1500, lambda: self._gui._lriddle_debug.config(text=""))

            except Exception as e:
                print(f"[ERROR] RiddleToggles: {e}")
            sleep(0.1)

        

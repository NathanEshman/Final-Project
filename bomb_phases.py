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

    def showPuzzle(self, name, widget_builder):
        self.clearPuzzle(name)
        frame = Frame(self, bg="black")
        self._puzzle_frames[name] = frame
        frame.grid(row=7, column=0, columnspan=3)
        widget_builder(frame)

    def clearPuzzle(self, name):
        frame = self._puzzle_frames.pop(name, None)
        if frame:
            frame.destroy()

    def showRiddle(self):
        def builder(frame):
            label = Label(frame, bg="black", fg="yellow", font=("Courier New", 14),
                          text="RIDDLE: What did Phineas & Ferb build first?\n1-Time Machine  2-Roller Coaster  3-Robot Dog  4-Spaceship")
            label.pack()
        self.showPuzzle("riddle", builder)
        global toggles
        toggles = RiddleToggles(component_toggles, RIDDLE_TOGGLE_ANSWER)
        toggles.start()

    def showTrianglePuzzle(self):
        def builder(frame):
            img = Image.open("HOW MANY TRIANGLES.png").resize((400, 400))
            self._img_triangle = ImageTk.PhotoImage(img)
            label_img = Label(frame, image=self._img_triangle, bg="black")
            label_img.pack()
            label_text = Label(frame, text="How many triangles?", fg="white", bg="black", font=("Courier New", 16))
            label_text.pack()
        self.showPuzzle("triangle", builder)

    def showKeypadPuzzle(self):
        def builder(frame):
            label = Label(frame, text="Enter the passcode using the keypad:", fg="white", bg="black", font=("Courier New", 16))
            label.pack()
        self.showPuzzle("keypad", builder)

    def showWiresPuzzle(self):
        def builder(frame):
            label = Label(frame, text="Unplug the PRIMARY COLOR wires (Red, Blue, Yellow)\nThen press the button to lock in.", fg="white", bg="black", font=("Courier New", 16))
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
        # create empty placeholder labels (will be used selectively)
        self._lkeypad = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)
        self._lwires = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)
        self._lbutton = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)
        self._ltoggles = Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)
        self._lstrikes = Label(self, bg="black", fg="#ff5555", font=("Courier New", 18), text="Strikes left: 5")
        self._lstrikes.grid(row=8, column=2, sticky=SE, padx=20, pady=10)



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
        return f"{self._min}:{self._sec}"

# the keypad phase
class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        # the default value is an empty string
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while (self._running):
            # process keys when keypad key(s) are pressed
            if (self._component.pressed_keys):
                # debounce
                while (self._component.pressed_keys):
                    try:
                        # just grab the first key pressed if more than one were pressed
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                # log the key
                self._value += str(key)
                # the combination is correct -> phase defused
                if (self._value == self._target):
                    self._defused = True
                # the combination is incorrect -> phase failed (strike)
                elif (self._value != self._target[0:len(self._value)]):
                    self._failed = True
            sleep(0.1)

    # returns the keypad combination as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value

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
        # the default value is False/Released
        self._value = False
        # has the pushbutton been pressed?
        self._pressed = False
        # we need the pushbutton's RGB pins to set its color
        self._rgb = component_rgb
        # the pushbutton's randomly selected LED color
        self._color = color
        # we need to know about the timer (7-segment display) to be able to determine correct pushbutton releases in some cases
        self._timer = timer

    # runs the thread
    def run(self):
        global triangle_puzzle
        global toggles
        self._running = True
        self._rgb[0].value = False if self._color == "R" else True
        self._rgb[1].value = False if self._color == "G" else True
        self._rgb[2].value = False if self._color == "B" else True

        while self._running:
            self._value = self._component.value
            if self._value:
                self._pressed = True
                
                

            else:
                if self._pressed:
                    # If wires phase is active and not defused, perform wire-check logic
                    print("[DEBUG] Button pressed and released")
                    
                    if triangle_puzzle._running:
                        triangle_puzzle.lock_in()
                        
                    if toggles._running and isinstance(toggles, RiddleToggles):
                        toggles.evaluate()
                        
                    else:
                        if (not self._target or self._target in self._timer._sec):
                            self._defused = True
                        else:
                            self._failed = True

                    if wires._running and not wires._defused:
                        wires.lock_in()
                        if wires.is_correct():
                            wires._defused = True
                            wires._running = False
                        else:
                            self._timer._value = max(0, self._timer._value - 5)  # ⏱️ Deduct 5 seconds
                            print("[DEBUG] Incorrect wires, -5 seconds penalty")
                    
                    self._pressed = False
            sleep(0.1)
        
class TrianglePuzzle(PhaseThread):
    def __init__(self, correct_answer, timer, name="TrianglePuzzle"):
        super().__init__(name)
        self._correct_answer = str(correct_answer)
        self._input = ""
        self._timer = timer

    def run(self):
        self._running = True
        while self._running:
            if keypad._value:
                self._input = keypad._value
            sleep(0.1)

    def lock_in(self):
        if self._input == self._correct_answer:
            self._defused = True
            self._running = False
            print("[DEBUG] Triangle Puzzle solved!")
        else:
            self._timer._value = max(0, self._timer._value - 5)
            print("[DEBUG] Wrong triangle count! -5 seconds")
            # reset input to try again
            keypad._value = ""


    # returns the pushbutton's state as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return str("Pressed" if self._value else "Released")

# the toggle switches phase
class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)

    def run(self):
        self._running = True
        self._grace_end = time.time() + 2
        while self._running:
            try:
                value_bin = "".join([str(int(pin.value)) for pin in self._component])
                self._value = value_bin
                value_dec = int(value_bin, 2)
                if value_dec == self._target:
                    self._defused = True
                    self._running = False
                elif time.time() > self._grace_end and value_dec != 0 and value_dec != self._target:
                    self._failed = True
            except Exception as e:
                print(f"[ERROR] {self.__class__.__name__} phase: {e}")
            sleep(0.1)

    def __str__(self):
        if self._defused:
            return "DEFUSED"
        if self._value is None:
            return "WAITING"
        return f"{self._value}/{int(self._value, 2)}"

class RiddleToggles(Toggles):
   def run(self):
    global gui
    self._running = True
    self._grace_end = time.time() + 2
    print("[DEBUG] RiddleToggles thread started")
    while self._running:
        try:
            value_bin = "".join([str(int(pin.value)) for pin in self._component])
            value_dec = int(value_bin, 2)
            self._value = value_bin  # ✅ MAKE SURE THIS IS SET
            print(f"[DEBUG] RiddleToggles = {value_bin}/{value_dec} (target = {self._target})")

            if value_dec == self._target:
                print("[DEBUG] Riddle solved!")
                self._defused = True
                self._running = False
                if hasattr(gui, "_lriddle"):
                    gui._lriddle.destroy()
                if hasattr(gui, "showCorrect"):
                    gui.showCorrect()
            elif time.time() > self._grace_end and value_dec != 0 and value_dec != self._target:
                self._failed = True

        except Exception as e:
            print(f"[ERROR] RiddleToggles phase: {e}")
        sleep(0.1)
    
    def evaluate(self):
        global gui, current_phase_index, strikes_left, timer

        value_bin = "".join([str(int(pin.value)) for pin in self._component])
        value_dec = int(value_bin, 2)
        print(f"[DEBUG] Evaluating RiddleToggles: {value_bin} ({value_dec})")

        if value_dec == self._target:
            self._defused = True
            self._running = False
            gui.clearPuzzle("riddle")
            current_phase_index += 1
            gui.after(200, show_current_phase)
            print("[DEBUG] Correct toggle answer — moving to next puzzle.")
        else:
            print("[DEBUG] Incorrect toggle — strike and time penalty.")
            strikes_left -= 1
            timer._value = max(0, timer._value - 5)


        
   def __str__(self):
    if self._defused:
        return "DEFUSED"
    if self._value is None:
        return "WAITING"
    return f"{self._value}/{int(self._value, 2)}"


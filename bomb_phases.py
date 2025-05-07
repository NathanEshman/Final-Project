@ -1,334 +1,334 @@
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
        
    def showStartScreen(self, on_start):
        self._start_screen = Frame(self, bg="black")
        self._start_screen.place(relx=0.5, rely=0.5, anchor="center")
        
        try:
            img = Image.open("Start_Mouse.jpeg").resize((1920, 1080))
            self._start_img = ImageTk.PhotoImage(img)
            label_img = Label(self._start_screen, image=self._start_img, bg="black")
            label_img.pack(pady=20)
        except Exception as e:
            print(f"[ERROR] Failed to load start image: {e}")

        title = Label(self._start_screen, text="Welcome to the Rat Maze", fg="white", bg="black", font=("Courier New", 24))
        title.pack(pady=40)

        subtitle = Label(self._start_screen, text="By Diego Diaz, Elianna Ayala, and Nathan Eshman", fg="gray", bg="black", font=("Courier New", 18))
        subtitle.pack(pady=20)
        
        press_label = Label(self._start_screen, text="Press the physical button to begin", fg="white", bg="black", font=("Courier New", 18))
        press_label.pack(pady=40)

        # Start polling for hardware button press
        self.after(100, lambda: self.wait_for_physical_start(on_start))
    
    def wait_for_physical_start(self, on_start):
        if self._button is None:
            print("[DEBUG] Waiting for button to be set...")
            self.after(100, lambda: self.wait_for_physical_start(on_start))
            return

        if self._button._component.value:
            print("[DEBUG] Button pressed — starting game.")
            self._start_screen.destroy()
            self._start_screen = None
            on_start()
        else:
            self.after(100, lambda: self.wait_for_physical_start(on_start))


        
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
        self._lcheese = Label(self, bg="black", fg="orange", font=("Courier New", 16), text="")
        self._lcheese.grid(row=9, column=0, columnspan=3)
        
    def showCheeseMessage(self, message):
        self._lcheese.config(text=message)
        self.after(3000, lambda: self._lcheese.config(text=""))

        
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
        # the default value is an empty string
        self._value = ""

    # runs the thread
    def run(self):
        self._running = True
        while self._running:
            if self._component.pressed_keys:
                while self._component.pressed_keys:
                    try:
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)

                if key == "#":
                    from bomb import gui, strike, advance_phase, wires

                    print(f"[DEBUG] Locking in wire state: {wires._value}")
                    if wires._value == "01010":  # ✅ this is the correct wire pattern
                    if wires._value == "10101":  # ✅ this is the correct wire pattern
                        wires._defused = True
                        wires._running = False
                        gui.clearPuzzle("wires")


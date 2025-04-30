#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: Diego Diaz, Elianna Ayala, Nathan Eshman
#################################

# imports
import tkinter as tk
from bomb_configs import *
from threading import Thread
from time import sleep
import os
import sys



#########
# classes
#########

class Lcd(tk.Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        window.attributes("-fullscreen", True)
        self._timer = None
        self._button = None
        self.setupBoot()

    def setupBoot(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self._lscroll = tk.Label(self, bg="black", fg="white", font=("Courier New", 14), text="", justify=tk.LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=tk.W)
        self.pack(fill=tk.BOTH, expand=True)

    def setup(self):
        self._ltimer = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=tk.W)
        self._lkeypad = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=tk.W)
        self._lwires = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Wires phase: ")
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=tk.W)
        self._lbutton = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=tk.W)
        self._ltoggles = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=3, sticky=tk.W)
        self._ltrivia_q = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 14), text="Trivia: What did Phineas and Ferb build?\nA) a skyscraper  B) a spaceship\nC) a restaurant   D) a roller coaster")
        self._ltrivia_q.grid(row=6, column=0, columnspan=3, sticky=tk.W)
        self._ltrivia = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Trivia phase: ")
        self._ltrivia.grid(row=7, column=0, columnspan=3, sticky=tk.W)
        self._lstrikes = tk.Label(self, bg="black", fg="#00ff00", font=("Courier New", 18), text="Strikes left: ")
        self._lstrikes.grid(row=8, column=0, sticky=tk.W)

        if SHOW_BUTTONS:
            self._bpause = tk.Button(self, text="Pause", font=("Courier New", 18), bg="red", fg="white", command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)
            self._bquit = tk.Button(self, text="Quit", font=("Courier New", 18), bg="red", fg="white", command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

       

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
        self._bretry = tk.Button(self, text="Retry", font=("Courier New", 18), bg="red", fg="white", command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)
        self._bquit = tk.Button(self, text="Quit", font=("Courier New", 18), bg="red", fg="white", command=self.quit)
        self._bquit.grid(row=1, column=2, pady=40)

    def retry(self):
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])

    def quit(self):
        if RPi:
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            for pin in self._button._rgb:
                pin.value = True
        exit(0)
        

class StartScreen(tk.Frame):
    def __init__(self, master, start_callback, use_rpi_button=False):
        super().__init__(master, bg="black")
        self.master = master
        self.start_callback = start_callback
        self.pack(fill=tk.BOTH, expand=True)

        tk.Label(self, text="DEFUSE THE BOMB", fg="red", bg="black",
              font=("Courier New", 48, "bold")).pack(pady=60)

        tk.Label(self, text="Team: Diego Diaz, Elianna Ayala, Nathan Eshman",
              fg="white", bg="black", font=("Courier New", 18)).pack(pady=10)

        if not use_rpi_button:
            Button(self, text="CONTINUE", command=self.start_game,
                   font=("Courier New", 20), bg="gray20", fg="white",
                   activebackground="green", activeforeground="black",
                   width=20, height=2).pack(pady=60)

        self.bind("<Return>", lambda e: self.start_game())
        self.focus_set()

        if use_rpi_button and RPi:
            import board
            from digitalio import DigitalInOut, Direction, Pull

            self.start_button_pin = DigitalInOut(board.D4)
            self.start_button_pin.direction = Direction.INPUT
            self.start_button_pin.pull = Pull.DOWN
            self.poll_gpio()

    def poll_gpio(self):
        if self.start_button_pin.value:
            self.start_game()
        else:
            self.after(100, self.poll_gpio)

    def start_game(self):
        self.destroy()
        self.start_callback()


class VictoryScreen(tk.Toplevel):
    def __init__(self, master, on_quit=None):
        super().__init__(master)
        self.configure(bg="black")
        self.attributes("-fullscreen", True)

        # Create a Label to hold the video
        self.video_label = Label(self)
        self.video_label.pack()

        # Path to your video file
        video_path = "victoryvideo.mp4"  # <-- put your video in the project folder or give full path

        # Play the video (loop = 1 to repeat, 0 for no loop)
        player = tkvideo(video_path, self.video_label, loop=0, size=(800, 600))
        player.play()

        # Add a Quit button below
        Button(self, text="EXIT GAME", command=on_quit or self.quit_game,
               font=("Courier New", 20), bg="gray20", fg="white",
               activebackground="red", activeforeground="white").pack(pady=20)

    def quit_game(self):
        self.quit()
        self.destroy()


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

#Adjusting the timer seciton so that we can set the timer values and countdown. 
class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        # total remaining time in seconds
        self._value = initial_value
        # pause‑flag
        self._paused = False
        # formatted minute/second strings
        self._min = "00"
        self._sec = "00"
        # tick interval (seconds)
        self._interval = 1

    def _update(self):
        """Recompute the mm:ss display from the remaining seconds."""
        mins, secs = divmod(max(self._value, 0), 60)
        self._min = f"{mins:02}"
        self._sec = f"{secs:02}"

    def __str__(self):
        """What gets printed to the 7‑segment display."""
        return f"{self._min}:{self._sec}"

    def run(self):
        self._running = True
        while self._running:
            if not self._paused:
                # refresh display
                self._update()
                self._component.print(str(self))

                # if we’re at zero, stop and trigger failure
                if self._value <= 0:
                    self._running = False
                    self._component.explode()   # or whatever signals phase failure
                    break

                # wait a second, then decrement
                time.sleep(self._interval)
                self._value -= self._interval
            else:
                # when paused, just poll the flag
                time.sleep(0.1)


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
    def __init__(self, component, target, name="Keypad", max_length=10):
        super().__init__(name, component, target)
        self._value = ""
        self._max_length = max_length
        self._paused = False

    # Allow external pause (e.g., during animations or timeouts)
    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    # Optional: Get current input for UI display
    def get_value(self):
        return self._value

    # Main loop
    def run(self):
        self._running = True
        while self._running:
            if not self._paused and self._component.pressed_keys:
                # Debounce
                while self._component.pressed_keys:
                    try:
                        key = self._component.pressed_keys[0]
                    except IndexError:
                        key = ""
                    sleep(0.1)

                # Only accept input if under max length
                if len(self._value) < self._max_length:
                    self._value += str(key)

                # Check result
                if self._value == self._target:
                    self._defused = True
                    print("Keypad: Correct code entered!")
                    self._running = False  # Optionally stop the thread
                elif not self._target.startswith(self._value):
                    self._failed = True
                    print("Keypad: Incorrect code entered!")
                    self._running = False  # Optionally stop the thread

            sleep(0.1)


    # returns the keypad combination as a string
    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value
        
    def check_keypad():
        return keypad._value == keypad._target



# the jumper wires phase (UPDATED - PRIMARY COLOR UNPLUGGING)
PRIMARY_COLORS = {"Red", "Blue", "Yellow"}

class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)
        self.wire_indexes = ["1", "2", "3", "4"]  # Our wire indexes
        self.wire_states = [True] * len(self.wire_indexes)
        
        # Assign each wire a color
        self.wire_colors = [choice(["Red", "Blue", "Yellow", "Green", "White", "Black"]) for _ in self.wire_indexes]

    def run(self):
        self._running = True
        while self._running:
            for i, pin in enumerate(self._component):
                self.wire_states[i] = pin.value  # True = plugged, False = unplugged

            unplugged_colors = {color for color, state in zip(self.wire_colors, self.wire_states) if not state}
            plugged_colors = {color for color, state in zip(self.wire_colors, self.wire_states) if state}

            if unplugged_colors == PRIMARY_COLORS and PRIMARY_COLORS.isdisjoint(plugged_colors):
                self._defused = True
                self._running = False
            elif not PRIMARY_COLORS.issubset(unplugged_colors):
                self._failed = True
                self._running = False

            sleep(0.1)

    def __str__(self):
        if self._defused:
            return "DEFUSED"
        return " ".join([
            f"{idx}:{'Unplugged' if not state else 'Plugged'}({color})"
            for idx, state, color in zip(self.wire_indexes, self.wire_states, self.wire_colors)
        ])


class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, check_callback, name="Button"):
        """
        component_state: DigitalInOut pin for button press detection
        component_rgb: list of 3 DigitalInOut pins for RGB LED (R, G, B)
        check_callback: function that returns True if input is correct, False otherwise
        """
        super().__init__(name, component_state)
        self._value = False  # True = Pressed, False = Released
        self._pressed = False
        self._rgb = component_rgb
        self._check_callback = check_callback

    def run(self):
        self._running = True
        while self._running:
            # Check current button state
            self._value = self._component.value

            if self._value:  # Button is currently pressed
                self._pressed = True

            elif self._pressed:  # Button was pressed and now released
                # Evaluate user input via callback
                correct = self._check_callback()

                if correct:
                    self._defused = True
                    self._set_led("G")  # Green = correct
                else:
                    self._failed = True
                    self._set_led("R")  # Red = wrong

                self._pressed = False

            sleep(0.1)

    def _set_led(self, color):
        """Helper to set RGB LED color: 'R', 'G', or 'B'"""
        self._rgb[0].value = False if color == "R" else True
        self._rgb[1].value = False if color == "G" else True
        self._rgb[2].value = False if color == "B" else True

    def __str__(self):
        if self._defused:
            return "CORRECT"
        elif self._failed:
            return "INCORRECT"
        return "Waiting for Submit"

# the toggle switches phase
class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)

    # runs the thread
    def run(self):
        self._running = True
        while self._running:
            # Read switches 1 and 3 (index 0 and 2) for disallowed values
            if self._component[0].value or self._component[2].value:
                self._failed = True
                self._running = False
                continue

            # Read switches 2 and 4 (index 1 and 3)
            bits = [str(int(self._component[i].value)) for i in (1, 3)]
            self._value = "".join(bits)

            if self._value == self._target:
                self._defused = True
                self._running = False
            elif len(self._value) == len(self._target) and self._value != self._target:
                self._failed = True
                self._running = False
            sleep(0.1) 
    
    
    def __str__(self):
        if self._defused:
            return "DEFUSED"
        return f"{self._value}"
    
class TriviaPhase(PhaseThread):
    def __init__(self, component, name="Trivia"):
        super().__init__(name, component)
        self.options = [
            "a skyscraper",
            "spaceship",
            "restaurant",
            "a roller coaster"  # correct
        ]
        self.correct = "a roller coaster"
        self._target = self.correct
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            # Convert toggle values to integer index
            try:
                idx = int("".join(str(int(pin.value)) for pin in self._component), 2)
                selected = self.options[idx] if 0 <= idx < len(self.options) else None
            except:
                selected = None

            if selected == self.correct:
                self._value = selected
                self._defused = True
                self._running = False
            elif selected and selected != self.correct:
                self._value = selected
                self._failed = True
                self._running = False

            sleep(0.1)

    def __str__(self):
        if self._defused:
            return "DEFUSED"
        elif self._failed:
            return f"Wrong! {self._value}"
        return "Waiting for Answer"

    

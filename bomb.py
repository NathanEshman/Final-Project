
#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Diego Diaz, Elianna Ayala, Nathan Eshman
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

from tkinter import Tk, Frame, Label, Button, PhotoImage
import os

###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    if not ANIMATE or n == len(boot_text):
        if not ANIMATE:
            gui._lscroll["text"] = boot_text.replace("\x00", "")
        gui.setup()
        if hasattr(gui, "_lscroll"):
            gui._lscroll.destroy()
        if RPi:
            setup_phases()
            check_phases()
    else:
        if boot_text[n] != "\x00":
            gui._lscroll["text"] += boot_text[n]
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)

def setup_phases():
    global timer, keypad, wires, button, toggles

    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)
    keypad = Keypad(component_keypad, keypad_target)
    wires = Wires(component_wires, wires_target)
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    gui.setButton(button)
    toggles = Toggles(component_toggles, toggles_target)

    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

def check_phases():
    global active_phases

    if timer._running:
        gui._ltimer["text"] = f"Time left: {timer}"
    else:
        turn_off()
        gui.after(100, gui.conclusion, False)
        return

    if keypad._running:
        gui._lkeypad["text"] = f"Combination: {keypad}"
        if keypad._defused:
            keypad._running = False
            active_phases -= 1
        elif keypad._failed:
            strike()
            keypad._failed = False
            keypad._value = ""

    if wires._running:
        gui._lwires["text"] = f"Wires: {wires}"
        if wires._defused:
            wires._running = False
            active_phases -= 1
        elif wires._failed:
            strike()
            wires._failed = False

    if button._running:
        gui._lbutton["text"] = f"Button: {button}"
        if button._defused:
            button._running = False
            active_phases -= 1
        elif button._failed:
            strike()
            button._failed = False

    if toggles._running:
        gui._ltoggles["text"] = f"Toggles: {toggles}"
        if toggles._defused:
            toggles._running = False
            active_phases -= 1
        elif toggles._failed:
            strike()
            toggles._failed = False

    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    if strikes_left == 0:
        turn_off()
        gui.after(1000, gui.conclusion, False)
        return

    if active_phases == 0:
        turn_off()
        gui.after(100, gui.conclusion, True)
        return

    gui.after(100, check_phases)

def strike():
    global strikes_left
    strikes_left -= 1

def turn_off():
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    for pin in button._rgb:
        pin.value = True

##########
# GUI Setup
##########
def start_main_game():
    global gui
    for widget in window.winfo_children():
        widget.destroy()
    gui = Lcd(window)
    gui.pack()
    global strikes_left, active_phases
    strikes_left = NUM_STRIKES
    active_phases = NUM_PHASES
    gui.after(1000, bootup)
    if RPi:
        setup_phases()
        check_phases()


window = Tk()
window.title("Defuse the Bomb")
window.geometry("800x600")

start_screen = Frame(window, bg="black")
start_screen.pack(fill="both", expand=True)

Label(
    start_screen,
    text="Bomb Defusal\nBy Diego Diaz, Elianna Ayala, and Nathan Eshman",
    fg="red", bg="black",
    font=("Courier New", 24, "bold")
).pack(pady=40)

try:
    img = PhotoImage(file="Start_Mouse.jpg")
    Label(start_screen, image=img, bg="black").pack()
except Exception as e:
    Label(start_screen, text="[Image Not Found]", fg="white", bg="black").pack()

Button(
    start_screen,
    text="START GAME",
    command=start_main_game,
    font=("Courier New", 20),
    bg="gray20", fg="white",
    activebackground="green", activeforeground="black"
).pack(pady=40)

window.mainloop()


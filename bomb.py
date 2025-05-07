#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Elianna Ayala, Nathan Eshman, Diego Diaz
#################################

from bomb_configs import *
from bomb_phases import *

phase_order = ["riddle", "keypad", "wires", "triangle"]
current_phase_index = 0

# Game state
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

##########
def bootup():
    gui._lscroll["text"] = ""  # Minimal placeholder

def handle_riddle_strike():
    global strikes_left, timer
    strikes_left -= 1
    timer._value = max(0, timer._value - 5)
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    return strikes_left

def advance_phase():
    global current_phase_index
    current_phase_index += 1
    phase = phase_order[current_phase_index]
    if phase == "riddle":
        toggles._running = True
    elif phase == "keypad":
        keypad._running = True
    elif phase == "wires":
        wires._running = True
    elif phase == "triangle":
        triangle_puzzle._running = True
    gui.after(200, show_current_phase)

def setup_phases():
    global timer, keypad, wires, button, toggles, gui
    global triangle_puzzle

    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)

    keypad = Keypad(component_keypad, keypad_target)
    wires = Wires(component_wires, wires_target)
    triangle_puzzle = TrianglePuzzle(6, timer, keypad)
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    gui.setButton(button)

    if RIDDLE_MODE:
        toggles = RiddleToggles(component_toggles, RIDDLE_TOGGLE_ANSWER, gui, advance_phase, handle_riddle_strike)
    else:
        toggles = Toggles(component_toggles, toggles_target)

    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()
    triangle_puzzle.start()

    gui.after(200, show_current_phase)
    if phase_order[current_phase_index] == "riddle":
        toggles._running = True

def show_current_phase():
    for name in ["riddle", "keypad", "wires", "triangle"]:
        gui.clearPuzzle(name)
    phase = phase_order[current_phase_index]
    if phase == "riddle":
        gui.showRiddle()
    elif phase == "keypad":
        gui.showKeypadPuzzle()
    elif phase == "wires":
        gui.showWiresPuzzle()
    elif phase == "triangle":
        gui.showTrianglePuzzle()

def check_phases():
    global active_phases

    if keypad._running:
        gui._lkeypad["text"] = f"Combination: {keypad}"
        if keypad._defused:
            keypad._running = False
            active_phases -= 1
        elif keypad._failed:
            strike()
            keypad._failed = False
            keypad._value = ""

    if triangle_puzzle._running:
        gui._lkeypad["text"] = f"Your Count: {keypad._value}"
        if triangle_puzzle._defused:
            triangle_puzzle._running = False
            active_phases -= 1

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
            if hasattr(gui, "_lriddle"):
                gui._lriddle.destroy()
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
    global strikes_left, timer
    strikes_left -= 1
    timer._value = max(0, timer._value - 5)

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

def start_sequence():
    bootup()
    def after_boot():
        gui.setup()
        if RPi:
            setup_phases()
        show_current_phase()
        check_phases()
    gui.after(4000, after_boot)

##########
window = Tk()
gui = Lcd(window)
start_sequence()
window.mainloop()

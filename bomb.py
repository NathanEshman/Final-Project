
#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Elianna Ayala, Nathan Eshman, Diego Diaz
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

phase_order = ["riddle", "keypad", "wires", "triangle"]
current_phase_index = 0


cheese_available = False
cheese_collected = False
cheese_timer_id = None



###########
# generates the bootup sequence on the LCD
def handle_riddle_strike():
    global strikes_left, timer
    strikes_left -= 1
    timer._value = max(0, timer._value - 5)  # ⏱ Deduct 5 seconds
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    return strikes_left


def advance_phase():
    global current_phase_index
    current_phase_index += 1
<<<<<<< HEAD
    if current_phase_index >= len(phase_order):
        return  # All phases complete
=======

    # ✅ Activate the phase you just moved to
>>>>>>> 03394627024b05ae0e4c009ed49a901c83188fc9
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


<<<<<<< HEAD
def setup_phases():
    global timer, keypad, wires, button, toggles, gui
=======
def bootup(n=0):
    if not ANIMATE:
        gui._lscroll["text"] = boot_text.replace("\x00", "")
    elif n == len(boot_text):
        gui._lscroll["text"] = ""
    else:
        if boot_text[n] != "\x00":
            gui._lscroll["text"] += boot_text[n]
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)

      

# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles, gui  # ✅ Add gui here
>>>>>>> 03394627024b05ae0e4c009ed49a901c83188fc9
    global triangle_puzzle

    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)

    keypad = Keypad(component_keypad, keypad_target)
    wires = Wires(component_wires, wires_target)
    triangle_puzzle = TrianglePuzzle(6, timer, keypad)  # Use your actual triangle count
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer, triangle_puzzle)
    gui.setButton(button)
    

    if RIDDLE_MODE:
        toggles = RiddleToggles(component_toggles, RIDDLE_TOGGLE_ANSWER,gui,advance_phase,handle_riddle_strike)
    else:
        toggles = Toggles(component_toggles, toggles_target)


    # ✅ Start threads AFTER everything is assigned
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()
    triangle_puzzle.start()
<<<<<<< HEAD
    
    
    for phase in [keypad, wires, triangle_puzzle, toggles]:
        phase._running = True 

    first_phase = phase_order[current_phase_index]
    if first_phase == "riddle":
        toggles._running = True
    elif first_phase == "keypad":
        keypad._running = True
    elif first_phase == "wires":
        wires._running = True
    elif first_phase == "triangle":
        triangle_puzzle._running = True
=======
>>>>>>> 03394627024b05ae0e4c009ed49a901c83188fc9

    gui.after(200, show_current_phase)
    
    if phase_order[current_phase_index] == "riddle":
        toggles._running = True

    
def show_current_phase():
    # ✅ Force puzzle switch
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


# checks the phase threads
def check_phases():
    global active_phases
    
    if (keypad._running):
        gui._lkeypad["text"] = f"Combination: {keypad}"
    
    if triangle_puzzle._running:
        gui._lkeypad["text"] = f"Your Count: {keypad._value}"
        if triangle_puzzle._defused:
            triangle_puzzle._running = False
            active_phases -= 1

<<<<<<< HEAD
    if wires._running:
=======
    
    # check the timer
    if (timer._running):
        # update the GUI
        gui._ltimer["text"] = f"Time left: {timer}"
    else:
        # the countdown has expired -> explode!
        # turn off the bomb and render the conclusion GUI
        turn_off()
        gui.after(100, gui.conclusion, False)
        # don't check any more phases
        return
    # check the keypad
    if (keypad._running):
        # update the GUI
        gui._lkeypad["text"] = f"Combination: {keypad}"
        # the phase is defused -> stop the thread
        if (keypad._defused):
            keypad._running = False
            active_phases -= 1
            advance_phase()  # ✅ This moves to the next puzzle correctly

        # the phase has failed -> strike
        elif (keypad._failed):
            strike()
            # reset the keypad
    # check the wires
    if (wires._running):
>>>>>>> 03394627024b05ae0e4c009ed49a901c83188fc9
        gui._lwires["text"] = f"Wires: {wires}"
    
        if (wires._defused):

        if wires._value == "10101":
            wires._defused = True
            wires._running = False
            active_phases -= 1
<<<<<<< HEAD
=======
            activate_cheese_powerup()
            gui.clearPuzzle("wires")
            advance_phase()

        elif (wires._failed):
>>>>>>> 03394627024b05ae0e4c009ed49a901c83188fc9
        elif wires._failed:
            strike()
            wires._failed = False


    # check the button
    if (button._running):
        # update the GUI

<<<<<<< HEAD
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

def start_sequence():#
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
=======
>>>>>>> 03394627024b05ae0e4c009ed49a901c83188fc9

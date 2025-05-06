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

###########
# generates the bootup sequence on the LCD

def handle_riddle_strike():
    global strikes_left
    strikes_left -= 1
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    return strikes_left  # Return updated value for logic checks


def advance_phase():
    global current_phase_index
    current_phase_index += 1

    # ✅ Activate the phase you just moved to
    phase = phase_order[current_phase_index]
    if phase == "keypad":
        keypad._running = True
    elif phase == "wires":
        wires._running = True
    elif phase == "triangle":
        triangle_puzzle._running = True

    gui.after(200, show_current_phase)


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
    global triangle_puzzle

    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)

    keypad = Keypad(component_keypad, keypad_target)
    wires = Wires(component_wires, wires_target)
    triangle_puzzle = TrianglePuzzle(correct_answer=6, timer=timer)  # Use your actual triangle count
    triangle_puzzle.start()
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

    gui.after(200, show_current_phase)
    
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
        # the phase has failed -> strike
        elif (keypad._failed):
            strike()
            # reset the keypad
            keypad._failed = False
            keypad._value = ""
    # check the wires
    if (wires._running):
        # update the GUI
        gui._lwires["text"] = f"Wires: {wires}"
        # the phase is defused -> stop the thread
        if (wires._defused):
            wires._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (wires._failed):
            strike()
            # reset the wires
            wires._failed = False
    # check the button
    if (button._running):
        # update the GUI
        gui._lbutton["text"] = f"Button: {button}"
        # the phase is defused -> stop the thread
        if (button._defused):
            button._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (button._failed):
            strike()
            # reset the button
            button._failed = False
    # check the toggles
    if (toggles._running):
        gui._ltoggles["text"] = f"Toggles: {toggles}"
        if (toggles._defused):
            toggles._running = False
            active_phases -= 1
            # Remove the riddle label if it exists
            if hasattr(gui, "_lriddle"):
                gui._lriddle.destroy()
        elif (toggles._failed):
            strike()
            toggles._failed = False


    # note the strikes on the GUI
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    # too many strikes -> explode!
    if (strikes_left == 0):
        # turn off the bomb and render the conclusion GUI
        turn_off()
        gui.after(1000, gui.conclusion, False)
        # stop checking phases
        return

    # the bomb has been successfully defused!
    if (active_phases == 0):
        # turn off the bomb and render the conclusion GUI
        turn_off()
        gui.after(100, gui.conclusion, True)
        # stop checking phases
        return

    # check the phases again after a slight delay
    gui.after(100, check_phases)

# handles a strike
def strike():
    global strikes_left
    
    # note the strike
    strikes_left -= 1

# turns off the bomb
def turn_off():
    # stop all threads
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    # turn off the 7-segment display
    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    # turn off the pushbutton's LED
    for pin in button._rgb:
        pin.value = True

def start_sequence():
    bootup()

    def after_boot():
        gui.setup()
        if RPi:
            setup_phases()
            toggles.set_state([0, 1, 0, 0])  # Optional: test config
            show_current_phase()  # ✅ Force initial GUI screen to match phase 0
            check_phases()

    # Delay just long enough to finish boot text, then show puzzles
    gui.after(4000, after_boot)


##########
# GUI Setup
##########
# initialize the LCD GUI
window = Tk()
gui = Lcd(window)

# initialize game state
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# create button early so it's ready
button = Button(component_button_state, component_button_RGB, button_target, button_color, None)
gui.setButton(button)

# now show start screen AFTER button is linked
gui.showStartScreen(start_sequence)

window.mainloop()
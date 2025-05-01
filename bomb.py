#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Elianna Ayala, Nathan Eshman, Diego Diaz;
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *
import board
from digitalio import DigitalInOut, Direction, Pull
import time

# TEMP: Toggle pin reader debug
pins = [board.D12, board.D16, board.D20, board.D21]
toggles = [DigitalInOut(p) for p in pins]
for t in toggles:
    t.direction = Direction.INPUT
    t.pull = Pull.DOWN

print("Reading toggles. Press Ctrl+C to stop.")
while True:
    values = "".join(str(int(t.value)) for t in toggles)
    print("Toggles raw:", values)
    time.sleep(0.5)


###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    if (not ANIMATE or n == len(boot_text)):
        if (not ANIMATE):
            gui._lscroll["text"] = boot_text.replace("\x00", "")
        gui.setup()
        if (RPi):
            setup_phases()
            check_phases()
    else:
        if (boot_text[n] != "\x00"):
            gui._lscroll["text"] += boot_text[n]
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)

# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles

    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)
    keypad = Keypad(component_keypad, keypad_target)
    wires = Wires(component_wires, wires_target)
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    gui.setButton(button)

    if RIDDLE_MODE:
        toggles = RiddleToggles(component_toggles, RIDDLE_TOGGLE_ANSWER)
    else:
        toggles = Toggles(component_toggles, toggles_target)

    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

# checks the phase threads
def check_phases():
    global active_phases
    
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
        # update the GUI
        gui._ltoggles["text"] = f"Toggles: {toggles}"
        # the phase is defused -> stop the thread
        if (toggles._defused):
            toggles._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (toggles._failed):
            strike()
            # reset the toggles
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

##########
# GUI Setup
##########
# initialize the LCD GUI
window = Tk()
gui = Lcd(window)

# initialize the bomb strikes and active phases (i.e., not yet defused)
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# "boot" the bomb
gui.after(1000, bootup)

# display the LCD GUI
window.mainloop()
#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Diego Diaz, Elianna Ayala, Nathan Eshman
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *

from bomb_phases import VictoryScreen

from bomb_phases import StartScreen

from tkinter import Tk



###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    if not ANIMATE or n == len(boot_text):
        if not ANIMATE:
            gui._lscroll["text"] = boot_text.replace("\x00", "")
        gui.setup()
        if hasattr(gui, "_lscroll"):  # clear the boot scroll label if still there
            gui._lscroll.destroy()
        if RPi:
            setup_phases()
            check_phases()
    else:
        if boot_text[n] != "\x00":
            gui._lscroll["text"] += boot_text[n]
        gui.after(25 if boot_text[n] != "\x00" else 750, bootup, n + 1)


def check_keypad():
    return keypad._value == keypad._target


# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles, trivia
    
    # setup the timer thread
    timer = Timer(component_7seg, COUNTDOWN)
    # bind the 7-segment display to the LCD GUI so that it can be paused/unpaused from the GUI
    gui.setTimer(timer)
    # setup the keypad thread
    keypad = Keypad(component_keypad, keypad_target)
    # setup the jumper wires thread
    wires = Wires(component_wires, wires_target)
    # setup the pushbutton thread
    button = Button(component_button_state, component_button_RGB, check_keypad)
    # bind the pushbutton to the LCD GUI so that its LED can be turned off when we quit
    gui.setButton(button)
    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target)
    trivia = TriviaPhase(component_toggles)

    # start the phase threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()
    trivia.start()


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
    gui._lbutton["text"] = f"Button: {button}"
    if (button._defused):
        button._running = False
        active_phases -= 1
    elif (button._failed):
        print("Button press incorrect — triggering strike")  # Debug line
        strike()
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
    # check the trivia
        if (trivia._running and not hasattr(trivia, 'popup_shown')):
            trivia.popup_shown = True  # flag to prevent reopening
        def handle_trivia_result(correct):
            trivia._defused = correct
            trivia._failed = not correct
            trivia._running = False
            if correct:
                gui._ltrivia["text"] = "Trivia: DEFUSED"
            else:
                strike()

        launch_trivia_popup(on_answer_callback=handle_trivia_result)

    

    # note the strikes on the GUI
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    # too many strikes -> explode!
    if (strikes_left == 5):
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
        
        # 🟢 NEW: Show the Victory screen
        VictoryScreen(window)
        # stop checking phases
        return

    # check the phases again after a slight delay
    gui.after(100, check_phases)
    
    

# handles a strike
def strike():
    global strikes_left
    strikes_left -= 1
    print(f"STRIKE! Strikes left: {strikes_left}")  # Debug line

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
        
def start_main_game():
    global gui
    gui = Lcd(window)  # Now only create the main GUI AFTER start screen is gone
    gui.pack()
    # initialize the bomb strikes and active phases
    global strikes_left, active_phases
    strikes_left = NUM_STRIKES
    active_phases = NUM_PHASES
    gui.after(1000, bootup)
    if RPi:
        timer.start()
        


# Create the main window
window = Tk()
window.title("Defuse the Bomb")
window.geometry("1920x1080")  # Adjust if needed

# Start the StartScreen
StartScreen(window, start_callback=start_main_game, use_rpi_button=True)

# Run the GUI loop
window.mainloop()


from tkinter import Toplevel, Label, Radiobutton, Button, StringVar, messagebox

def launch_trivia_popup(on_answer_callback=None):
    def submit_answer():
        selected = var.get()
        if selected == "D":
            messagebox.showinfo("Correct!", "That's right! It was a roller coaster.")
            if on_answer_callback:
                on_answer_callback(True)
        else:
            messagebox.showerror("Wrong!", f"Oops! The correct answer was D.")
            if on_answer_callback:
                on_answer_callback(False)
        popup.destroy()

    popup = Toplevel()
    popup.title("Trivia Question")
    popup.geometry("500x300")
    popup.configure(bg="black")

    Label(popup, text="What did Phineas and Ferb build?", bg="black", fg="lime", font=("Courier New", 16)).pack(pady=10)

    var = StringVar()
    options = [
        ("A) a skyscraper", "A"),
        ("B) a spaceship", "B"),
        ("C) a restaurant", "C"),
        ("D) a roller coaster", "D"),
    ]

    for text, value in options:
        Radiobutton(popup, text=text, variable=var, value=value,
                    font=("Courier New", 14), bg="black", fg="white",
                    activebackground="gray", selectcolor="black").pack(anchor="w", padx=40)

    Button(popup, text="Submit", command=submit_answer,
           font=("Courier New", 14), bg="gray", fg="white").pack(pady=20)

    popup.transient()
    popup.grab_set()


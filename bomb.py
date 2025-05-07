        gui.setup()  # ✅ Setup GUI widgets first

        if RPi:
            setup_phases()  # ✅ Start the bomb phase threads
                 
            if phase_order[current_phase_index] == "riddle":
                toggles._running = True

        show_current_phase()  # ✅ Show the puzzle corresponding to current_phase_index

        check_phases()  # ✅ Start the monitoring loop for game logic

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
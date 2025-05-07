
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
gui.showStartScreen(start_sequence)
window.mainloop()
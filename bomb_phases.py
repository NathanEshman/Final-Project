                if value_dec == self._target:
                    self._defused = True
                    print("[DEBUG] Riddle defused!")
                    if hasattr(self._gui, "_lriddle"):
                        self._gui._lriddle.destroy()
                    if hasattr(self._gui, "showCorrect"):
                        self._gui.showCorrect()
                    self._on_defused()

                elif value_dec != 0 and value_dec != self._target:
                    if self._last_wrong != value_dec:
                        print(f"[DEBUG] Incorrect toggle value: {value_dec}, expected {self._target}")
                        strikes_left = self._on_strike()  # ✅ Strike handled here only
                        self._last_wrong = value_dec


                        if strikes_left <= 0:
                            print("[DEBUG] No strikes left — game over")
                            self._running = False
                            self._gui.after(200, self._gui.showGameOver)
                            sleep(2)
                            os._exit(0)

                        else:
                            self._gui._lriddle_debug["text"] = "Wrong! Try again..."
                            self._gui.after(1500, lambda: self._gui._lriddle_debug.config(text=""))

            except Exception as e:
                print(f"[ERROR] RiddleToggles: {e}")
            sleep(0.1)
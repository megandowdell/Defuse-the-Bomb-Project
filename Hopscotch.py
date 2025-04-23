#Hopscotch
#Megan Dowdell

import tkinter as tk
from tkinter import messagebox
import random

class HopscotchGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Hopscotch - All Levels View")

        self.num_rounds = 5
        self.tiles_per_round = 4
        self.current_round = 0
        self.safe_tiles = self.generate_safe_tiles()

        self.round_labels = []
        self.tile_buttons = []

        # Setup layout
        self.header = tk.Label(master, text="Hop through all 5 rounds!", font=("Helvetica", 16))
        self.header.pack(pady=10)

        self.frame = tk.Frame(master)
        self.frame.pack()

        self.draw_all_rounds()

    def generate_safe_tiles(self):
        return [random.sample(range(self.tiles_per_round), k=random.choice([1, 2]))
                for _ in range(self.num_rounds)]

    def draw_all_rounds(self):
        for r in range(self.num_rounds):
            # Round label
            lbl = tk.Label(self.frame, text=f"Level {r + 1}", font=("Helvetica", 14))
            lbl.grid(row=r, column=0, padx=10, pady=5)
            self.round_labels.append(lbl)

            # Tile buttons
            row_buttons = []
            for c in range(self.tiles_per_round):
                btn = tk.Button(self.frame, text=f"Tile {c + 1}", width=10, height=2,
                                command=lambda r=r, c=c: self.check_tile(r, c))
                btn.grid(row=r, column=c + 1, padx=5)
                row_buttons.append(btn)
            self.tile_buttons.append(row_buttons)

        self.update_button_states()

    def update_button_states(self):
        for r in range(self.num_rounds):
            for c in range(self.tiles_per_round):
                state = "normal" if r == self.current_round else "disabled"
                self.tile_buttons[r][c].config(state=state)

            # Highlight current round label
            self.round_labels[r].config(fg="blue" if r == self.current_round else "black")

    def check_tile(self, row, col):
        if col in self.safe_tiles[row]:
            self.current_round += 1
            if self.current_round == self.num_rounds:
                messagebox.showinfo("You Win!", "You safely hopped through all levels!")
                self.master.destroy()
            else:
                self.update_button_states()
        else:
            messagebox.showerror("Boom!", f"Wrong tile on Level {row + 1}!")
            self.master.destroy()

def run_hopscotch_game():
    root = tk.Tk()
    game = HopscotchGame(root)
    root.mainloop()
    
    
run_hopscotch_game()
import tkinter as tk
from tkinter import ttk
import random
import time

class MemoryGame:
    def __init__(self,master):
        # Intitialize main window
        self.master = master
        self.master.title("Memory Game")
        self.master.geometry("900x600")
        self.master.configure(bg = "#1a1a2e")

        # Custom font
        self.custom_font = ("Helvetica", 14, "bold")
        self.colors = {
            'bg': "#1a1a2e",
            'sidebar_bg': "#16213e",
            'card_bg': "#0f3496",
            'card_fg': "#e94560",
            'text': "#ffffff",
            'button_bg': "#4caf50",
            'button_fg':"#ffffff",
            'combobox_bg': "#32374b",
            'combobox_fg': "#ffffff",
            'gameover_bg': "#0f3460"
        }

        self.difficulty_levels = {
            "Easy": {"grid": (4,4), "symbols":["🍓","🫐","🍒","🍋","🍉","🥝","🥥","🍍"]},
            "Medium": {"grid":(4,5), "symbols": ["🍓","🫐","🍒","🍋","🍉","🥝","🥥","🍍","🌽","🥬"]},
            "Hard": {"grid": (5,6), "symbols": ["🍓","🫐","🍒","🍋","🍉","🥝","🥥","🍍","🌽","🥬","🫜","🥕","🥦","🥑","🍎"]}
        }

        # Initial game stats
        self.current_difficulty = "Easy"
        self.revealed = []
        self.matched_pairs = 0
        self.matched_cards = []
        self.moves = 0
        self.start_time = None
        self.game_solved = False

        self.create_widgets()
        self.create_game_grid()
    
    def create_widgets(self):
        # main frame hold all elements
        self.main_frame = tk.Frame(self.master, bg=self.colors['bg']) # create frame with bg color
        self.main_frame.pack(fill=tk.BOTH, expand=True) # frame fills entire window

        # sidebar
        self.sidebar = tk.Frame(self.main_frame, bg=self.colors['sidebar_bg'],width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # frame holds card elements
        self.game_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        self.game_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.create_sidebar()

    def create_sidebar(self):
        title_label = tk.Label(self.sidebar, text="Memory Game", 
                               font=("Helvetica", 24, "bold"),
                               bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        title_label.pack(pady=(30,10)) # padding above and below title

        subtitle_label = tk.Label(self.sidebar, text="Test Your Memory!", 
                               font=("Helvetica", 16, "italic"),
                               bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        subtitle_label.pack(pady=(0,30)) # padding below subtitle

        # Dificulty selector
        self.dificulty_label = tk.Label(self.sidebar, text="Difficulty:", 
                               font=self.custom_font,
                               bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        
        self.dificulty_label.pack(pady=(0,5))

        # Custom style for combobox
        self.style = ttk.Style()

        self.style.theme_create("modern", parent="alt", settings={
            "TCombobox": {
                "configure": {
                    "selectbackground": self.colors['combobox_bg'],
                    "fieldbackground": self.colors['combobox_bg'],
                    "background": self.colors['button_bg'],
                    "foreground": self.colors['combobox_fg']
                }
            }
        })

        # Custom theme for combobox
        self.style.theme_use("modern")

        self.difficulty_combobox =ttk.Combobox(self.sidebar, values=list(self.difficulty_levels.keys()),
                                               state="readonly", font=self.custom_font, width=10)
        self.difficulty_combobox.set(self.current_difficulty)
        self.difficulty_combobox.pack(pady=(0,20))
        self.difficulty_combobox.bind("<<ComboboxSelected>>", self.change_difficulty)
        
        # Game statistics labels
        self.moves_label = tk.Label(self.sidebar, text="Moves: 0",
                                    font=self.custom_font,
                                    bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        self.moves_label.pack(pady=10) # padding around label

        self.time_label = tk.Label(self.sidebar, text="Time: 0:00",
                                    font=self.custom_font,
                                    bg=self.colors['sidebar_bg'], fg=self.colors['text'])
        self.time_label.pack(pady=10)

        # New game button
        self.new_game_button = tk.Button(self.sidebar, text="New Game",
                                    font=self.custom_font,
                                    bg=self.colors['button_bg'], fg=self.colors['button_fg'],
                                    relief=tk.FLAT,
                                    command=self.new_game)
        self.new_game_button.pack(pady=30)

        self.new_game_button.bind("<Enter>",lambda e: e.widget.config(bg="#5dbb5e")) # lighten on hover
        self.new_game_button.bind("<Leave>", lambda e: e.widget.config(bg=self.colors['button_bg']))

    def create_game_grid(self):
        # Create frame to hold all cards
        self.cards_frame = tk.Frame(self.game_frame, bg=self.colors['bg'])  
        self.cards_frame.pack(expand=True)  

        # Initialize cards list and get symbol pairs
        self.cards = [] 

        rows, cols = self.difficulty_levels[self.current_difficulty]["grid"]  
        symbols = self.difficulty_levels[self.current_difficulty]["symbols"] * 2  

        random.shuffle(symbols)
        self.symbols = symbols


        # Create cards in grid
        for i in range(rows):  # Loop through each row
            for j in range(cols):  # Loop through each column in current row
                card_idx = i*cols+j  # Calculate linear index from row and column

                card = tk.Canvas(self.cards_frame, width=80, height=100, 
                               bg=self.colors['card_bg'], highlightthickness=0)  
                card.grid(row=i, column=j, padx=5, pady=5)  
                card.bind("<Button-1>", lambda e, idx=card_idx: self.on_card_click(idx))  # Bind click event

                # Guess card design (visible initailly)
                card.create_rectangle(5, 5, 75, 95, fill=self.colors['card_bg'],  
                                    outline=self.colors['card_fg'], width=2)  
                card.create_text(40, 50, text="?", font=("Helvetica", 24, "bold"),  
                               fill=self.colors['card_fg'])  

                # Create card front (hidden initially) 
                card.create_rectangle(5, 5, 75, 95, fill=self.colors['card_fg'],  
                                    outline=self.colors['card_bg'], width=2,  
                                    state='hidden', tags=('front',))  
                
                card.create_text(40, 50, text=self.symbols[card_idx],  
                               font=("Helvetica", 24, "bold"),       
                               fill=self.colors['card_bg'],          
                               state='hidden', tags=('symbol',))     

                self.cards.append(card)  # Add card to list for later reference

    def on_card_click(self, idx): 
        # Start timer
        #if self.start_time is None:  # If this is the first click of the game
         #   self.start_time = time.time()  
          #  self.update_time()

        # Ignore invalid clicks
        #if idx in self.revealed or idx in self.matched_cards or len(self.revealed) == 2:
            # Skip if card is already revealed, matched, or 2 cards are already flipped
          #  return

        # Reveal the clicked card
        self.reveal_card(idx)
        self.revealed.append(idx)

        # If two cards are revealed, check for a match
        if len(self.revealed) == 2:
            self.moves += 1
            self.moves_label.config(text=f"Moves: {self.moves}")
            self.master.after(500, self.check_match)


    def reveal_card(self, idx):
        card = self.cards[idx]
        card.itemconfig('front', state='normal')
        card.itemconfig('symbol', state='normal')

    def hide_card(self, idx):
        card = self.cards[idx] 
        card.itemconfig('front', state='hidden') 
        card.itemconfig('symbol', state='hidden')

    def check_match(self):
        idx1, idx2 = self.revealed
        if self.symbols[idx1] == self.symbols[idx2]:
            self.matched_pairs += 1
            self.matched_cards.extend([idx1, idx2])

            for idx in [idx1, idx2]:
                card = self.cards[idx]
                card.itemconfig('front', fill="#8bc34a")  

            if self.matched_pairs == len(self.symbols) // 2:
                self.master.after(500, self.game_over)  

        else:  
            self.hide_card(idx1)
            self.hide_card(idx2)
        
        self.revealed.clear()  # Clear the revealed cards list for next move



    def new_game(self):
        self.game_solved = False 
        self.revealed.clear()
        self.matched_cards.clear()
        self.matched_pairs = 0
        self.moves = 0
        self.start_time = None

        # Reset labels
        self.moves_label.config(text="Moves: 0")
        self.time_label.config(text="Time: 0:00")

        # Recreate the game grid
        self.cards_frame.destroy()
        self.create_game_grid()

    def change_difficulty(self,event):
        new_difficulty = self.difficulty_combobox.get()
        if new_difficulty != self.current_difficulty:
            self.current_difficulty = new_difficulty
            self.new_game()


                

if __name__ == "__main__":
    root = tk.Tk() # create main window
    game = MemoryGame(root)
    root.mainloop()

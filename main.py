from Tkinter import Tk
from titleScreen import TitleScreen
import sound

sound.init(
    music="Korobeiniki.mid", 
    sounds = "lock_in rotate pause line_clear game_lost".split()
)

root = Tk()
root.wm_title("Falling Block Game")

root.bind("<Escape>", lambda event: root.destroy())

g = TitleScreen(root)

g.pack()
g.start()

root.mainloop()
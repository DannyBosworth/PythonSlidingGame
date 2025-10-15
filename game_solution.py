#Resolution - 1920x1080
import tkinter as tk
import random
import time
from threading import Thread, Event
import pickle

# Colours are indexed as follows:
# [0] - BG Colour
# [1] - Button Colours
# [2:4] - Tile Colour

colourlist = [["#172815", "#83781B", "#95B46A", "#709255", "#3E5622"],
              ["#36413E", "#BEB2C8", "#8D8D92", "#5D5E60", "#D7D6D6"],
              ["#5F3311", "#AC6B36", "#E1A059", "#CF7E47", "#D38A58"],
              ["#1B4D6C", "#9CBED9", "#39708F", "#729DBD", "#B2C7D8"],
              ["#5A0001", "#D31001", "#BF0402", "#8E020E", "#790004"]]

class App():

    def __init__(self, root: tk.Tk):
        """Initiates the App"""
        self.updateSettings()
        menu = Menu(self.settings, root)
        root.bind("<" + self.settings["Boss"] + ">", lambda e: self.switchWindow("Boss", None))
        menu        
    
    def switchWindow(self, new, time):
        """Switches from one window to another"""
        root.geometry("800x800")
        root.title("Sliding Game")
        self.updateSettings()
        root.config(bg=colourlist[int(self.settings["Colour"])][0])
        for child in root.winfo_children():
            child.destroy()
        if new not in ["Menu", "Boss"]:
            self.menubtn = tk.Button(root, text="X", font=("Arial Black", 24, "bold"), bg=colourlist[int(self.settings["Colour"])][1], relief="flat",default="active", highlightbackground="black", highlightthickness=2, command=lambda: myApp.switchWindow("Menu", None))
            self.menubtn.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
            self.menubtn.place(x=root.winfo_width()-85, y=10, width=75, height=75)
        if new == "Game":
            window = Game(self.settings, root, time)
            window
        if new == "Timetrial":
            window = Timetrial(self.settings, root, 0, time)
            window
        elif new == "Menu":
            window = Menu(self.settings, root)
            window
        elif new == "Settings":
            self.updateSettings()
            window = Settings(self.settings, root)
            window
        elif new == "Leaderboard":
            window = Leaderboard(self.settings, root)
            window
        elif new == "Boss":
            window = Boss(root, time)
            window
        
    def updateSettings(self):
        """Reads the current settings from the file"""
        temp = [s.strip() for s in open("settings.txt", "r").readlines()]
        self.settings = {s.split(":", 1)[0] : s.split(":", 1)[1] for s in temp}



        

class Menu(App):

    def __init__(self, settings: dict, master: tk.Tk):
        """Initiates the menu window"""
        self.colours = colourlist[int(settings["Colour"])]
        self.master = master
        self.border = tk.Frame(master, bg=self.colours[0], highlightbackground="black", highlightthickness=5)
        self.grid = [[tk.Button(self.border, bg=random.choice(self.colours[2:]), relief="flat", font=("Segoe Print", 24, "bold"), highlightbackground="black", highlightthickness=1) for _ in range(3)] for _ in range(3)]
        self.master.config(bg=self.colours[0])
        self.border.focus_set()
        self.drawMenu()

    def drawMenu(self):
        """Draws the menu widgets"""
        self.grid[1][1].config(text="PLAY!", command=self.pickType)
        self.grid[0][1].config(text="SETTINGS", command=lambda: myApp.switchWindow("Settings", None))
        self.grid[2][1].config(text="LEADERBOARD", command=lambda: myApp.switchWindow("Leaderboard", None), font=("Segoe Print", 18, "bold"))
        for i in range(3):
            for j in range(3):
                self.grid[i][j].bind("<Enter>", lambda e: e.widget.config(bg=random.choice(self.colours[2:]), cursor="hand2", relief="sunken"))
                self.grid[i][j].bind("<Leave>", lambda e: e.widget.config(relief="flat"))
                self.grid[i][j].place(x = 200 *i, y = 200 * j, width=200, height=200)
        self.border.place(x=95, y=95, width=610, height=610)

    def pickType(self):
        """Handles the selection of game type"""
        for c in self.border.winfo_children():
            c.destroy()
        self.btn3x3 = tk.Button(self.border, text="3X3", font=("Segoe Print", 24, "bold"), bg=self.colours[1], relief="flat",default="active", highlightbackground="black", highlightthickness=2, command=lambda: self.hideMenu(3))
        self.btntt = tk.Button(self.border, text="Time Trial", font=("Segoe Print", 24, "bold"), bg=self.colours[1], relief="flat",default="active", highlightbackground="black", highlightthickness=2, command=lambda: self.hideMenu("T"))
        self.btn3x3.place(x=150, y=100, width=300, height=150)
        self.btntt.place(x=150, y=350, width=300, height=150)
        self.btn3x3.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
        self.btntt.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))


    def hideMenu(self, type):
        """Animates the closing of the menu"""
        if type == "T":
            myApp.switchWindow("Timetrial", None)
        else:
            myApp.switchWindow("Game", None)

class Game(App):

    def __init__(self, settings: dict, master: tk.Tk, time):
        """Initialises the game window"""
        self.colours = colourlist[int(settings["Colour"])]
        self.settings = settings
        self.master = master
        self.master.bind("<" + self.settings["Boss"] + ">", lambda e: self.bossKey())
        self.timer = tk.Button(self.master, bg=self.colours[1], font=("Segoe Print", 24, "bold"), highlightbackground="black", highlightthickness=2, text="0.0", command=self.restartGame)
        self.timer.bind("<Enter>", lambda e: self.showRestart())
        self.timer.bind("<Leave>", lambda e: self.showRestart())
        self.timerval = 0
        if time != None:
            self.timerval = time 
            self.timer.config(text=str(time))     
        self.master.geometry(str((4)*200) + "x" + str((4)*200))
        self.border = tk.Frame(master, bg=self.colours[0], highlightbackground="black", highlightthickness=5)
        self.master.config(bg=self.colours[0])
        self.timerthread = Thread(target=self.updateTimer)
        self.timerpaused = Event()
        self.finished = Event()
        self.records = [float(r.strip().split(" ")[2]) if r.strip() != "N/A" else float(-1) for r in open("records.txt", "r").readlines()]
        self.pause = tk.Button(self.master, text="II", font=("Arial Black", 24, "bold"), bg=self.colours[1], relief="flat",default="active", highlightbackground="black", highlightthickness=2, command=lambda: self.pauseGame())
        self.pause.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
        self.savebtn = tk.Button(self.master, text="Save", bg=self.colours[1], font=("Segoe Print", 24, "bold"), highlightbackground="black", default="active", relief="flat", highlightthickness=2, command=lambda: self.saveGame())
        self.savebtn.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
        self.loadbtn = tk.Button(self.master, text="Load", bg=self.colours[1], font=("Segoe Print", 24, "bold"), highlightbackground="black", default="active", relief="flat", highlightthickness=2, command=lambda: self.loadGame())
        self.loadbtn.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
        self.loadbtn.bind("<Leave>", lambda e: e.widget.config(highlightbackground="black"))
        self.border.bind("<Key>", self.keyPressed)
        self.border.focus_set()
        self.cheating = False
        self.moved = True
        self.border.bind("<Escape>", lambda e: self.returnMenu())
        self.drawGrid()
    
    def bossKey(self):
        pickle.dump([[self.grid[j][i]["text"] if self.grid[j][i] != None else "0" for i in range(3)] for j in range(3)], open("bossgame.txt", "w+b"), protocol=0)
        myApp.switchWindow("Boss", self.timerval)

    def returnMenu(self):
        """Returns the user to the main menu"""
        self.timerthread = None
        myApp.switchWindow("Menu", None)

    def drawBoard(self):
        """Draws the game board and initialises game array"""
        while True:
            self.grid = [[tk.Button(self.border, bg=random.choice(self.colours[2:]), relief="flat", font=("Segoe Print", 24, "bold"), highlightbackground="black") for _ in range(3)] for _ in range(3)]
            self.blank = [random.randint(0,2), random.randint(0,2)]
            self.grid[self.blank[0]][self.blank[1]] = None
            numbers = list(range(1, 9))
            for i in range(3):
                for j in range(3):
                    if [i,j] != self.blank:
                        self.grid[i][j].config(text="")
                        value = random.choice(numbers)
                        numbers.remove(value)
                        self.grid[i][j].config(text=value)
            if self.checkSolvable():
                break
            else:
                for c in self.border.winfo_children():
                    c.destroy()
        for i in range(3):
            for j in range(3):
                if [i,j] == self.blank:
                    continue
                self.grid[i][j].configure(command= lambda index = [i, j]: self.tileClicked(index))
                self.grid[i][j].bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
                self.grid[i][j].place(x = 200 * j, y = 200 * i, width=200, height=200)

    def updateTimer(self):
        """Handles updating of the timer"""
        while self.timerval != 9999.9:
                time.sleep(0.1)
                if not self.timerpaused.is_set() and not self.cheating and not self.finished.is_set():
                    self.timerval = round(self.timerval + 0.1, 1)
                    try:
                        self.timer.config(text=str(self.timerval))
                    except:
                        break

    def showRestart(self):
        """Displays the restart button over the timer"""
        if self.timer["text"] != "Restart ↻":
            self.timer.config(cursor="hand2", text="Restart ↻")
            self.timerpaused.set()
        else:
            self.timer.config(text=str(float(self.timerval)))
            if self.pause["text"] == "II":
                self.timerpaused.clear()
    
    def restartGame(self):
        """Creates a new random game board"""
        self = Game(self.settings, self.master, 3)

    def drawGrid(self):
        """Draws the widgets for the game window"""
        self.drawBoard()
        self.border.place(x=95, y=95, width=3*200 + 10, height=3*200 + 10)
        self.timer.place(x=root.winfo_width()/2 - 100, y = 10, width=200*(3-2), height=75)
        self.pause.place(x=10, y=10, width=75, height=75)
        self.savebtn.place(x=100, y=root.winfo_height() - 85, width=200*(3-2), height=75)
        self.loadbtn.place(x=root.winfo_width() - 300, y=root.winfo_height() - 85, width=200*(3-2), height=75)


    def checkSolvable(self):
        """Determines if a given board is solvabe"""
        values = [i for val in self.grid for i in val]
        count = 0
        for i in range(len(values)):
            if values[i] == None:
                continue
            for j in range(i+1, len(values)):
                if values[j] != None:
                    if int(values[j]["text"]) < int(values[i]["text"]):
                        count += 1
        if count % 2 == 0 and count != 0:
            return True
        else:
            return False

    def saveGame(self):
        """Saves the current board to the save file"""
        pickle.dump([[self.grid[j][i]["text"] if self.grid[j][i] != None else "0" for i in range(3)] for j in range(3)], open("savegame.txt", "wb"), protocol=0)

    def loadGame(self):
        """Loads a board from the save file"""
        vals =  pickle.load(open("savegame.txt", "rb"))
        for i in range(3):
            for j in range(3):
                if vals[i][j] == "0":
                    self.blank = [i,j]
                    if self.grid[i][j] != None:
                        self.grid[i][j].destroy()
                    self.grid[i][j] = None
                    
                else:
                    if self.grid[i][j] == None:
                        self.grid[i][j] = tk.Button(self.border,text=vals[i][j], bg=random.choice(self.colours[2:]), relief="flat", font=("Segoe Print", 24, "bold"))
                    else:
                        self.grid[i][j].config(text=vals[i][j])
                    self.grid[i][j].configure(command= lambda index = [i, j]: self.tileClicked(index))
                    self.grid[i][j].bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
                    self.grid[i][j].place(x = 200 * j, y = 200 * i, width=200, height=200)
        self.master.update()
        self.timer.config(text="0.0")
        self.timerval = 0
        self.timerpaused.set()



    def pauseGame(self):
        """Pauses and unpauses the game"""
        if self.timerpaused.is_set():
           self.timerpaused.clear()
           self.pause.config(text="II")
           self.cheating = False
        else:
            self.timerpaused.set()
            self.pause.config(text="▶")

        
    def keyPressed(self, key):
        """Handles all keypresses for the game"""
        try:
            if key.keysym == self.settings["Up"]:
                if self.blank[0] == 2:                                  
                    raise
                self.moveValue([self.blank[0]+1, self.blank[1]])
            elif key.keysym == self.settings["Down"]:
                if self.blank[0] == 0:
                    raise   
                self.moveValue([self.blank[0]-1, self.blank[1]])
            elif key.keysym == self.settings["Left"]:
                if self.blank[1] == 2:
                    raise
                self.moveValue([self.blank[0], self.blank[1]+1])
            elif key.keysym == self.settings["Right"]:
                if self.blank[1] == 0:
                    raise
                self.moveValue([self.blank[0], self.blank[1]-1])
            elif key.keysym == "grave":
                if self.cheating == True:
                    if self.pause["text"] == "II":
                        self.timerpaused.clear()
                    self.cheating = False
                else:
                    self.timerpaused.set()
                    self.cheating = True
            elif key.keysym == self.settings["Pause"]:
                self.pauseGame()
        except:
            pass
        else:
            if not self.timerthread.is_alive() and key.keysym in list(self.settings.values())[1:5]:
                    self.timer.config(text="0.0")
                    self.timerthread.start()           
        
    def tileClicked(self, index):
         """Handles actions aftr a tile is clicked"""
         for i in range(-1,2,2):
            if (index[0] + i == self.blank[0] and index[1] == self.blank[1]) or (index[1] + i == self.blank[1] and index[0] == self.blank[0]):
                if not self.timerthread.is_alive():
                    self.timer.config(text="0.0")
                    self.timerthread.start()
                if self.finished.is_set():
                        self.timer.config(text="0.0")  
                        self.finished.clear()   
                self.moveValue(index)


    def moveValue(self, index):
        """Restructures the array when a tile is moved"""
        if not self.finished.is_set() and self.moved:
            if self.timer["text"] != "Restart ↻":
                self.timerpaused.clear()
                self.pause.config(text="II")
            self.moved = False
            move(self.grid[index[0]][index[1]], [self.blank[0] * 200 + 5, self.blank[1] * 200 + 5], [self.blank[0] - index[0] - 5, self.blank[1] - index[1] - 5])
            self.grid[self.blank[0]][self.blank[1]] = self.grid[index[0]][index[1]]
            self.grid[self.blank[0]][self.blank[1]].configure(command= lambda index = [self.blank[0], self.blank[1]]: self.tileClicked(index))
            self.grid[index[0]][index[1]] = None
            self.blank = [index[0], index[1]]
            self.checkWin()
            self.moved = True

    def checkWin(self):
        """Checks if the tiles are in the correct order"""
        count = 1
        for i in range(3):
            for j in range(3):
                if self.grid[i][j] == None:
                    return
                if self.grid[i][j]["text"] == count:
                    count += 1
                    if count == 3**2:
                        break
                else:
                    return
        self.finished.set()
        self.getName()

    def newRecord(self, record, index, name):
        """Writes a new record to the records file"""
        oldlines = open("records.txt", "r").readlines()
        for j in range((4 if index < 5 else 9), index-1, -1):
            if j == index:
                oldlines[j] = name + " - " + str(record) + "\n"
            else:
                oldlines[j] = oldlines[j-1]
        open("records.txt", "w").writelines(oldlines)    
        self.restartGame()    

    def getName(self):
        """Gets a name for new records"""
        for i in range(0, 5):
            if float(self.timer["text"]) < self.records[i] or self.records[i] == float(-1):
                for c in self.border.winfo_children():
                    c.destroy()
                nameentry = tk.Entry(self.border, bg=self.colours[1], font=("Segoe Print", 20, "bold"))
                nameentry.insert(0, "Enter your name...")
                nameentry.bind("<FocusIn>", lambda e: nameentry.delete(0, 18))
                nameentry.bind("<Return>", lambda e: self.newRecord(self.timer["text"], i, nameentry.get()))
                recordlbl = tk.Label(self.border, bg=self.colours[0], font=("Segoe Print", 24, "bold"), text="New Record!")
                nameentry.place(x=150, y=250, width=300, height=100)
                recordlbl.place(x=150, y=10, width=300, height=100)
                break

class Timetrial(Game):

    def __init__(self, settings: dict, master: tk.Tk, wins, time):
        """Initialises the timetrial window"""
        super().__init__(settings, master, 3)
        self.timer.config(text="180.0")
        self.savebtn.destroy()
        self.loadbtn.destroy()
        self.winlbl = tk.Label(self.master, text="Wins: 0", bg=self.colours[1], font=("Segoe Print", 24, "bold"), highlightbackground="black", highlightthickness=2)
        self.winlbl.place(x=300, y=715,  width=200, height=75)
        self.wins = wins
        self.timerval = 180
        if time != None:
            self.timerval = time[0] 
            self.timer.config(text=str(time[0]))
            self.wins = time[1]
            self.winlbl.config(text="Wins: " + str(self.wins))

    def updateTimer(self):
        """Handles and updates the timer"""
        while self.timerval != 0:
                time.sleep(0.1)
                if not self.timerpaused.is_set() and not self.finished.is_set():
                    self.timerval = round(self.timerval - 0.1, 1)
                    try:
                        self.timer.config(text=str(self.timerval))
                    except:
                        break
        self.finished.set()
        if self.timerval == 0:
            self.getName()

    def bossKey(self):
        pickle.dump([[self.grid[j][i]["text"] if self.grid[j][i] != None else "0" for i in range(3)] for j in range(3)], open("bossgame.txt", "w+b"), protocol=0)
        myApp.switchWindow("Boss", [self.timerval, self.wins])

    def getName(self):
        """Gets a name for new records"""
        for i in range(5, 10):
            if float(self.wins) > self.records[i] or self.records[i] == float(-1):
                for c in self.border.winfo_children():
                    c.destroy()
                nameentry = tk.Entry(self.border, bg=self.colours[1], font=("Segoe Print", 20, "bold"))
                nameentry.insert(0, "Enter your name...")
                nameentry.bind("<FocusIn>", lambda e: nameentry.delete(0, 18))
                nameentry.bind("<Return>", lambda e: self.newRecord(self.wins, i, nameentry.get()))
                recordlbl = tk.Label(self.border, bg=self.colours[0], font=("Segoe Print", 24, "bold"), text="New Record!")
                nameentry.place(x=150, y=250, width=300, height=100)
                recordlbl.place(x=150, y=10, width=300, height=100)
                break

    def showRestart(self):
        """Displays the reset button over the timer"""
        if self.timer["text"] != "Restart ↻":
            self.timer.config(cursor="hand2", text="Restart ↻")
            self.timerpaused.set()
        else:
            self.timer.config(text="180.0")
            if self.timer["text"] == "II":
                self.timerpaused.clear()

    def restartGame(self):
        """Creates a new game with a random board"""
        for c in self.border.winfo_children():
            c.destroy()
        self.finished.clear()
        self.drawBoard()

    def keyPressed(self, key):
        """Handles all keypresses for the game"""
        try:
            if key.keysym ==  self.settings["Up"]:
                if self.blank[0] == 2:
                    raise
                self.moveValue([self.blank[0]+1, self.blank[1]])
            elif key.keysym == self.settings["Down"]:
                if self.blank[0] == 0:
                    raise
                self.moveValue([self.blank[0]-1, self.blank[1]])
            elif key.keysym == self.settings["Left"]:
                if self.blank[1] == 2:
                    raise
                self.moveValue([self.blank[0], self.blank[1]+1])
            elif key.keysym == self.settings["Right"]:
                if self.blank[1] == 0:
                    raise
                self.moveValue([self.blank[0], self.blank[1]-1])
            elif key.keysym == self.settings["Pause"]:
                self.pauseGame()
        except:
            pass
        else:
            if not self.timerthread.is_alive() and not self.finished.is_set() and key.keysym in list(self.settings.values())[1:4]:
                self.timerthread.start()

    def checkSolvable(self):
        """Determines if it is possible to solve a given board"""
        values = [i for val in self.grid for i in val]
        count = 0
        for i in range(len(values)):
            if values[i] == None:
                continue
            for j in range(i+1, len(values)):
                if values[j] != None:
                    if int(values[j]["text"]) < int(values[i]["text"]):
                        count += 1
        if count % 2 == 0 and count != 0:
            return True
        else:
            return False 
        
    def checkWin(self):
        """Checks if the tiles are in the correct order"""
        count = 1
        for i in range(3):
            for j in range(3):
                if self.grid[i][j] == None:
                    return False
                if self.grid[i][j]["text"] == count:
                    count += 1
                    if count == 3**2:
                        break
                else:
                    return
        self.wins += 1
        self.winlbl.config(text="Wins: " + str(self.wins))
        self.restartGame()

class Settings(App):

    def __init__(self, settings: dict, master: tk.Tk):
        """Initialises the settings window"""
        self.master = master
        self.settings = settings
        self.colours = colourlist[int(settings["Colour"])]
        self.border = tk.Frame(master, bg=self.colours[1], highlightthickness=5, highlightbackground="black")
        self.colourbuttons = [tk.Button(self.border, command=lambda index = i: self.changeColours(index) , image=colourimgs[i], relief="flat", default="active", highlightbackground="black", highlightthickness=2) for i in range(len(colourlist))]
        self.clrlbl = tk.Label(self.border, text="Colour Theme", font=("Segoe Print", 24, "bold"), bg=self.colours[1])
        self.ctllabel = tk.Label(self.border, text="Key Binds", font=("Segoe Print", 24, "bold"), bg=self.colours[1])
        self.keybindbtns = [tk.Button(self.border, relief="flat", command=lambda index = i: self.readyBind(index),  text=list(self.settings.keys())[i] + " - " + str.upper(list(self.settings.values())[i]), font=("Segoe Print", 15, "bold"), bg=self.colours[1]) for i in range(1, len(self.settings.keys()) - 1)]
        self.border.bind("<Key>", self.updateBind)
        self.border.focus_set()
        self.newbind = None
        self.drawSettings()

    def drawSettings(self):
        """Places and gives binds to the settings widgets"""
        self.border.place(x=95, y=95, width=610, height=610)
        self.clrlbl.place(x=150, y=10, width=300,height=100)
        self.ctllabel.place(x = 150, y=230, width=300, height=100)
        for i in range(len(self.colourbuttons)):
            self.colourbuttons[i].bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
            self.colourbuttons[i].place(x=100*i + 17*(i+1), y = 120, width=100, height=100)
        for i in range(len(self.keybindbtns)):
            self.keybindbtns[i].place(x=150, y=330 + 45*i, width=300, height=40)
            self.keybindbtns[i].bind("<Enter>", lambda e: e.widget.config(cursor="hand2", fg="white"))
            self.keybindbtns[i].bind("<Leave>", lambda e: e.widget.config(fg="black"))

    def readyBind(self, index):
        """Prepares the application to accept a new keybinding"""
        self.newbind = index
        for btn in self.keybindbtns:
            btn.config(relief="flat", bg=self.colours[1])
            btn.bind("<Enter>", lambda e: e.widget.config(cursor="hand2", fg="white"))

        self.keybindbtns[index-1].config(relief="sunken", bg="white", fg="black")
        self.keybindbtns[index-1].bind("<Enter>", lambda e: e.widget.config(cursor="hand2", fg="black"))

    
    def updateBind(self, key):
        """Rewrites a control binding in settings file"""
        if self.newbind != None and (key.keysym not in list(self.settings.values()) or key.keysym == list(self.settings.values())[self.newbind]):
            oldlines = open("settings.txt", "r").readlines()
            oldlines[self.newbind] = list(self.settings.keys())[self.newbind] + ":" + key.keysym + "\n"
            open("settings.txt", "w").writelines(oldlines)
            myApp.switchWindow("Settings", None) 

    


    def changeColours(self, index):
        """Rewrites the colour scheme in settings file"""
        oldlines = open("settings.txt", "r").readlines()
        oldlines[0] = "Colour:" + str(index) + "\n"
        open("settings.txt", "w").writelines(oldlines)
        myApp.switchWindow("Settings", None)    

class Leaderboard(App):

    def __init__(self, settings, master: tk.Tk):
        """Initialises the leaderboard class"""
        self.master = master
        self.master.geometry("800x800")
        self.records = open("records.txt", "r").readlines()
        self.settings = settings
        self.colours = colourlist[int(settings["Colour"])]
        self.border = tk.Frame(master, bg=self.colours[1], highlightthickness=5, highlightbackground="black")
        self.border.focus_set()
        self.lbl3x3 = tk.Label(self.border, bg = self.colours[1], fg="black", font=("Segoe Print", 24, "bold"), text="Standard")
        self.lbltt = tk.Label(self.border, bg = self.colours[1], fg="black", font=("Segoe Print", 24, "bold"), text="Time Trial")
        self.sep = tk.Label(self.border, bg="black")
        self.times3x3 = [tk.Label(self.border, anchor="w", bg=self.colours[1], fg="black", font=("Segoe Print", 20, "bold"), text=str(i + 1) + ". " + self.records[i].strip()) for i in range(5)]
        self.timestt = [tk.Label(self.border, anchor="w", bg=self.colours[1], fg="black", font=("Segoe Print", 20, "bold"), text=str(i + 1) + ". " + self.records[i+5].strip()) for i in range(5)]
        self.ldblbl = tk.Label(self.master, bg = self.colours[1], highlightbackground="black", highlightthickness=5, fg="black", font=("Segoe Print", 30, "bold"), text="Leaderboard")
        self.drawLeaderboard()


    def drawLeaderboard(self):
        """Places the leaderboard widgets on the screen"""
        self.border.place(x=100, y=100, width=600, height=600)
        self.ldblbl.place(x=200, y=10, width=400, height=75)
        self.lbl3x3.place(x=20, y=100, width=200, height=100)
        self.lbltt.place(x=20, y=400, width=200, height=100)
        self.sep.place(x=0, y=299, width=595, height=4)
        for i in range(5):
            self.times3x3[i].place(x=310, y=58*i + 5, width=250, height=53)
            self.timestt[i].place(x=310, y=58*i + 305, width=250, height=53)

class Boss(App):

    def __init__(self, master: tk.Tk, time):
        """Initialises the boss window"""
        self.master = master
        self.time = time
        self.master.title("Command Prompt")
        self.master.config(bg="black")
        self.cmdlbl = tk.Label(text="C:\\>", fg="white", bg="black", font=("Consolas", 16), anchor="nw")
        self.cmdentry = tk.Entry(bg="black", fg="white", font=("Consolas", 16), relief="flat")
        self.cmdentry.bind("<Escape>", lambda e: self.exit())
        self.cmdentry.bind("<Return>", lambda e: self.cmdentry.delete(0, "end"))
        self.cmdentry.focus_set()
        self.cmdlbl.place(x=2, y=2, width=55, height=30)
        self.cmdentry.place(x=57, y=2, width=700, height=30)

    def exit(self):
        if type(self.time) == float:
            myApp.switchWindow("Game", self.time)
        else:
            myApp.switchWindow("Timetrial", self.time)



root = tk.Tk()
root.title("Sliding Game")
root.geometry("800x800")
root.resizable(False, False)
colourimgs = [tk.PhotoImage(file="C" + str(i) + ".png") for i in range(len(colourlist))]
myApp = App(root)

def move(target: tk.Widget, end, delta):
    """Animates the movement of a widget to a new location"""
    while target.winfo_x() != end[1] or target.winfo_y() != end[0]:
        target.place(x=target.winfo_x() + delta[1] , y=target.winfo_y() + delta[0])
        root.update()

root.mainloop()
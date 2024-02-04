from re import A
from tkinter import *
from tkinter import ttk
from MyTks import SelectKeypressWindow
import pynput
from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
from AnInput import *
import time
import pickle
from tkinter.filedialog import askopenfilename, asksaveasfilename
from XtraGUI import *
import json
import math
from bidict import bidict

recording = False
bindingkeyname = None
minWaitTime = 0.6

inputs = []


timeOfLastInput = 0.00

Cpath = ""

def UpdateListVisual():
    inputs_var.set(inputs)

def AppendRecord(inp: AnInput):
    global inputs, timeOfLastInput
    if len(inputs) > 0:
        if type(inp) == MouseScroll and type(inputs[-1]) == MouseScroll and (inp.amount < 0) == (inputs[-1].amount < 0):
            inputs[-1].amount += inp.amount
        elif inputs[-1].GetType() == inp.GetType():
            inputs[-1] = inp
        elif type(inp) == KeyboardInput and type(inputs[-1]) == KeyboardInput and inputs[-1].key == inp.key:
            inputs[-1] = KeyPressed(inp.key)
        elif type (inp) == MouseClick and type(inputs[-1]) == MouseClick and inputs[-1].button == inp.button:
            inputs[-1] = WholeMouseClick(inp.button)
        else:
            if time.time() - timeOfLastInput > minWaitTime:
                inputs.append(DelayedInput(time.time() - timeOfLastInput))
            inputs.append(inp)

    else:
        inputs.append(inp)

    timeOfLastInput = time.time()
    UpdateListVisual()

def StartRecording(*args):
    recordbutton.config(text="stop", command=StopRecording)

    global recording, timeOfLastInput
    recording = True
    timeOfLastInput = time.time()
    print("started rec")

def StopRecording(*args):
    
    recordbutton.config(text="record", command=StartRecording)
    if len(inputs):
        inputs.pop()
    UpdateListVisual()
    global recording
    recording = False
    print("stopped rec")

def PlayRecording(*args):
    for inp in inputs:
        inp.Playback()

def SaveRecordingAs(*args):
    path = asksaveasfilename(defaultextension='.macro', filetypes=[('Macro List',('*.pkl','*.macro'))])
    if not path:
        return
    global Cpath
    Cpath = path
    SaveRecording()

def SaveRecording(*args):
    global Cpath
    if Cpath == "":
        SaveRecordingAs()
        return

    with open(Cpath, 'wb') as file:
        pickle.dump(inputs, file, pickle.HIGHEST_PROTOCOL)

def LoadRecording(*args):
    path = askopenfilename(title='Select a previously recorded macro save', defaultextension='.macro', filetypes=[('Macro List',('*.pkl', '*.macro')), ('Any', '*')])
    if not path:
        return
    with open(path, 'rb') as file:
        inputs.extend(pickle.load(file))

        UpdateListVisual()
        
        global Cpath
        Cpath = path
    
def BindKey(func, key: str):
    global bindingkeyname
    specialKeyBinds[func] = key
    keybindstostrings[func] = str(key)
    bindingkeyname = None

def BindKeyTo(func):
    global bindingkeyname
    bindingkeyname = func

def ClearList():
    inputs_var.set('')
    inputs.clear()
    global Cpath
    Cpath = ""

def SetMinWaitTime():
    global tempMenu
    tempMenu = Tk()
    tempMenu.title('Set minimum time to automatically insert pause while recording')
    men = Menu(tempMenu)
    tempMenu.config(menu=men)
    ttk.Entry(tempMenu).pack()
    ttk.Panedwindow(tempMenu).pack()
    ttk.Button(tempMenu, text='button').pack()
    ttk.Checkbutton(tempMenu, text='check').pack()
    men.add_checkbutton()
    (cb := ttk.Combobox(tempMenu)).pack()
    cb.option_add(3, 'buh')
    #ttk.Notebook(tempMenu).pack
    (om := ttk.OptionMenu(tempMenu, bool())).pack()
    om.option_add(5, 'opt')
    ttk.Progressbar(tempMenu, length=30, maximum=100.0, value=33).pack()
    (rb := ttk.Radiobutton(tempMenu, text='radio')).pack()
    
    ttk.Separator(tempMenu).pack()
    ttk.Sizegrip(tempMenu).pack()

def DeleteSelection():
    for i in range(len(inputsListBox.curselection())): inputs.pop(inputsListBox.curselection()[i]-i)
    UpdateListVisual()
    inputsListBox.select_clear(inputsListBox.curselection()[0], inputsListBox.curselection()[-1])

def InsertInput(inp: AnInput):
    inputs.append(inp)
    UpdateListVisual()

def on_press(key):
    if bindingkeyname:
        BindKey(bindingkeyname, key)
        return

    if key in specialKeyBinds.keys():
        specialKeyBinds[key]()
        return

    if recording:
        AppendRecord(KeyboardInput(key, True))

def on_release(key):
    if recording and key == specialKeyBinds.inverse[StopRecording]:
        StopRecording()

    if recording:
        AppendRecord(KeyboardInput(key, False))
        
def on_move(x, y):
    if recording:
        AppendRecord(MouseMove((x,y)))

def on_click(x, y, button, pressed):
    if recording:
        AppendRecord(MouseClick(button, pressed))

def on_scroll(x, y, dx, dy):
    if recording:
        AppendRecord(MouseScroll(dy))

def do_popup(event):
    try:
        editMenu.tk_popup(event.x_root, event.y_root)
    finally:
        editMenu.grab_release()

def ChooseKeypressPopup():
    t = Tk()
    n = SelectKeypressWindow(t, inputs, inputs_var, inputsListBox.curselection()[0] if inputsListBox.curselection() else None)

# Liste  to mouse events
mouseListener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)

# Listen to keyboard events
keyListener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

mouseListener.start()
keyListener.start()


specialKeyBinds = bidict({ Key.f2 : StartRecording,
                    Key.f3 : StopRecording })

keybindstostrings = dict()

for key in specialKeyBinds:
    if key is Key:
        keybindstostrings.update({specialKeyBinds[key] : StringVar()})

root = Tk()
root.geometry('220x180')
#root.resizable(False, True)
root.title("Macro Controller")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N,W,E,S))

toolbar = Menu(root, tearoff=0)
root.config(menu=toolbar)
filemenu = Menu(toolbar, tearoff=0)
settingsMenu = Menu(toolbar, tearoff=0)
keybindsMenu = Menu(settingsMenu, tearoff=0)
editMenu = Menu(toolbar, tearoff=0)
addInputMenu = Menu(editMenu, tearoff=0)
filemenu.add_command(label='Exit', command=root.destroy)
filemenu.add_command(label='Save as...', command=SaveRecordingAs)
filemenu.add_command(label='Save', command=SaveRecording)
filemenu.add_command(label='New', command=ClearList)
filemenu.add_command(label='Load...', command=LoadRecording)
keybindsMenu.add_command(label='Bind \'Stop Recording\'', command=BindKeyTo(StopRecording))
keybindsMenu.add_command(label='Bind \'Start Recording\'', command=BindKeyTo(StartRecording))
settingsMenu.add_cascade(label='Bind keys...', menu=keybindsMenu)
settingsMenu.add_command(label='Set minimum wait...', command=SetMinWaitTime)
editMenu.add_command(label='Undo')
editMenu.add_command(label='Redo')
editMenu.add_separator()
editMenu.add_command(label='Cut')
editMenu.add_command(label='Copy')
editMenu.add_command(label='Paste')
editMenu.add_command(label='Delete', command=DeleteSelection)
editMenu.add_command(label='Duplicate')
editMenu.add_separator()
addInputMenu.add_command(label='wait')
addInputMenu.add_command(label='keydown')
addInputMenu.add_command(label='keyup')
addInputMenu.add_command(label='keypress', command=ChooseKeypressPopup)
addInputMenu.add_command(label='mousedown')
addInputMenu.add_command(label='mouseup')
addInputMenu.add_command(label='mouse-click')
addInputMenu.add_command(label='mouse position')
addInputMenu.add_command(label='mouse move')
addInputMenu.add_command(label='scroll')
editMenu.add_cascade(label='Insert input', menu=addInputMenu)
toolbar.add_cascade(label='File', menu=filemenu)
toolbar.add_cascade(label='Settings', menu=settingsMenu)
toolbar.add_cascade(label='Edit', menu=editMenu)


#mything = SelectKeypressWindow()

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

inputs_var = StringVar(value=inputs)

(recordbutton := ttk.Button(mainframe, text="record", command=StartRecording)).grid(column=0,row=0, sticky='ns')
(playbutton := ttk.Button(mainframe, text="play", command=PlayRecording, )).grid(column=0,row=1, sticky='ns')
#(savebutton := ttk.Button(mainframe, text="save", command=SaveRecording)).grid(column=3, row=1, sticky=(N,E))
#(loadbutton := ttk.Button(mainframe, text="load", command=LoadRecording)).grid(column=4, row=1, sticky=(N,E))
#(bindstopbutton := ttk.Button(mainframe, text="bind stop rec", command=BindKeyTo(StopRecording))).grid(column=1, row=2, sticky=(N,W))
(clearbutton := ttk.Button(mainframe, text="clear", command=ClearList)).grid(column=0,row=2, sticky='ns')

inputsListBox = Listbox(mainframe,listvariable=inputs_var, selectmode='extended', justify='center')
inputsListBox.grid(column=1,row=0, rowspan=100)
inputsListBox.bind('<Button-3>', do_popup)


root.mainloop()
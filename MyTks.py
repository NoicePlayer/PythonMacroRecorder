from tkinter import *
from tkinter import ttk
from typing import Iterable
from pynput.keyboard import Key, KeyCode
from AnInput import KeyPressed

class SelectKeypressWindow(Frame):
    def __init__(self, master, inpList: list, listvar: StringVar, index: int | None = None):
        Frame.__init__(self, master)
        self.grid()
        self.list = inpList
        self.listvar = listvar
        self.ind = index
        self.createWidgets()

    def createWidgets(self):
        ttk.Label(self, text='Select key: ').grid(column=0,row=0)
        self.keyvalues = list('abcdefghijklmnopqrstuvwxyz1234567890') + [e for e in Key] + ['2323234fsglol']
        self.cb = ttk.Combobox(self, values=[str(v).replace('Key.','') for v in self.keyvalues])
        self.cb.grid(column=1, row=0)
        ttk.Button(self,text='Cancel', command=self.Cancel).grid(column=0,row=1)
        ttk.Button(self, text='Add',command=self.Add).grid(column=1,row=1)

    def Cancel(self):
        self.master.destroy()

    def Add(self):
        if self.cb.current() != -1:
            k = KeyPressed(self.keyvalues[self.cb.current()] if not str(self.keyvalues[self.cb.current()]).isalnum() else KeyCode.from_char(str(self.keyvalues[self.cb.current()])))
            if self.ind:
                self.list.insert(self.ind, k)
            else:
                self.list.append(k)
            self.listvar.set(self.list)
            self.Cancel()
        else:
            Label(self, text='Invalid key!').grid(column=1,row=3)
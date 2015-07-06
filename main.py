#! /usr/bin/env python2

from vtk import *

from Tkinter import *
import ttk

from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

import config
import data
from gui3d import *

class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.pack()

        notebook = ttk.Notebook(self)

        gui2d_frame = Frame(notebook, width=600, height=600)
        gui2d_frame.pack(fill='both', expand=1)
        notebook.add(gui2d_frame, text='2D')

        self.gui3d_frame = Gui3d(notebook)
        self.gui3d_frame.pack(fill='both', expand=1)
        notebook.add(self.gui3d_frame, text='3D')

        notebook.pack(fill='both', expand=1)

        button_frame = Frame(self, bd=1, relief='sunken')
        button_frame.pack(side='bottom', fill='x')

        button_quit = Button(button_frame, text='quit',
            command=self.parent.quit, padx=5, pady=5)
        button_quit.pack(side='right')

        self.initKShortcuts()

    def initKShortcuts(self):
        self.bind_all("<Control-q>", lambda e: self.parent.quit() )
        self.bind_all("q", lambda e: self.parent.quit() )

    def loadData(self, data):
        self.data = data
        self.gui3d_frame.loadData(data)

if __name__ == '__main__':
    data = data.Data(config.config)

    root = Tk()
    app = App(root)
    app.loadData(data)
    root.mainloop()

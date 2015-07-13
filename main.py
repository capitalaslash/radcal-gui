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
        self.pack(fill='both', expand=1)

        # top section
        self.frameFile = Frame(self, height=40, bd=1, relief='sunken')
        self.frameFile.pack(fill='x', expand=0)


        # middle section
        self.frameMain = Frame(self)
        self.frameMain.pack(fill='both', expand=1)

        self.iren = vtkTkRenderWindowInteractor(self.frameMain) #, rw=self.renWin,
#            width=600, height=600)
        self.iren.pack(side='left', fill='both', expand=1)

        notebook = ttk.Notebook(self.frameMain)
        self.frameGui2d = Frame(notebook, width=250) #Gui2d(notebook)
        self.frameGui2d.pack(fill='both', expand=1)
        notebook.add(self.frameGui2d, text='2D')
        self.frameGui3d = Frame(notebook, width=250) #Gui3d(notebook)
        self.frameGui3d.pack(fill='both', expand=1)
        notebook.add(self.frameGui3d, text='3D')
        notebook.pack(side='left', fill='y', expand=0)

        # bottom section
        self.frameButton = Frame(self, bd=1, relief='sunken')
        self.frameButton.pack(side='bottom', fill='x')

        buttonQuit = Button(self.frameButton, text='quit',
            command=self.parent.quit, padx=5, pady=5)
        buttonQuit.pack(side='right')

        self.initKShortcuts()

    def initKShortcuts(self):
        self.bind_all("<Control-q>", lambda e: self.parent.quit() )
        self.bind_all("q", lambda e: self.parent.quit() )

    def loadData(self, data):
        self.data = data
        # self.gui2d_frame.loadData(data)

if __name__ == '__main__':
    data = data.Data(config.config)

    root = Tk()
    app = App(root)
    app.loadData(data)
    root.mainloop()

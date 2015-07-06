#! /usr/bin/env python2

from vtk import *

from Tkinter import *

from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

class App(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.pack()

if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.mainloop()


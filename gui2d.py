#! /usr/bin/env python2

from Tkinter import *

from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

import vtk2d

class Gui2d(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()

        self.vtk = vtk2d.Vtk2d()

        self.iren = vtkTkRenderWindowInteractor(self, rw=self.vtk.renWin, width=600, height=400)
        self.iren.grid(row=0, column=0, sticky='nsew')

        self.vtk.setInteractor(self.iren)

        self.initButtonFrame()

        # all additional space should go to vtk window
        Grid.columnconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 0, weight=1)

    def initButtonFrame(self):
        buttonFrame = Frame(self)
        buttonFrame.grid(row=0, column=1)

        buttonRender = Button(buttonFrame, text='Render', command=self.render)
        buttonRender.pack()

        self.buttonClear = Button(buttonFrame, text='Clear', command=self.clear,
            state='disabled')
        self.buttonClear.pack()

        self.varList = Listbox(buttonFrame, selectmode='browse')
        self.varList.bind('<<ListboxSelect>>', self.varModified)
        self.varList.pack()

    def clear(self):
        self.varList.delete(0, END)
        self.buttonClear['state']='disabled'
        self.vtk.clear()

    def render(self):
        self.varList.delete(0, END)
        varNames = self.vtk.data.getVarList()
        for var in varNames:
            self.varList.insert('end', var)
        self.buttonClear['state']='normal'
        self.vtk.render()

    def varModified(self, *args):
        idx = self.varList.curselection()[0]
        var = self.varList.get(idx)
        # print 'setting ', var
        self.vtk.data.grid.GetPointData().SetActiveScalars(var)
        self.vtk.renWin.Render()

    def initKShortcuts(self):
        self.bind_all("<Control-q>", lambda e: self.parent.quit() )
        self.bind_all("q", lambda e: self.parent.quit() )

    def loadData(self, data):
        self.vtk.loadData(data)

if __name__ == '__main__':
    from config import *
    from data import *
    data = Data(config)

    root = Tk()
    app = Gui2d(root)
    app.initKShortcuts()
    app.loadData(data)
    root.mainloop()

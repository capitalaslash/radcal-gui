#! /usr/bin/env python2

from vtk import *
from Tkinter import *

from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

import data

class Gui3d(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()

        axesActor = vtkAxesActor()
        self.ren = vtkRenderer()
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.ren.AddActor(axesActor)
        renWin = vtkRenderWindow()
        renWin.AddRenderer(self.ren)
        self.camera = self.ren.GetActiveCamera()

        interactor = vtkTkRenderWindowInteractor(self, rw=renWin, width=600, height=600)
        interactor.pack(fill='both', expand=1)

        buttonCamera = Button(self, text='Camera', command=self.outputCamera)
        buttonCamera.pack(side='bottom', padx=5, pady=5)

    def outputCamera(self):
        print self.camera

    def initKShortcuts(self):
        self.bind_all("<Control-q>", lambda e: self.parent.quit() )
        self.bind_all("q", lambda e: self.parent.quit() )

    def loadData(self, data):
        self.data = data

        mapper = vtkDataSetMapper()
        mapper.SetInputData(self.data.grid)
        mapper.SetScalarModeToUseCellData()
        actor = vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)

    def adjustCamera(self):
        # self.ren.ResetCamera()
        self.camera.SetPosition(10.0, -6.0, 5.3)
        self.camera.SetFocalPoint(2.5, 1.5, 0.5)
        self.camera.SetViewUp(-0.31, 0.28, 0.90)


if __name__ == '__main__':
    root = Tk()
    app = Gui3d(root)

    app.initKShortcuts()

    from config import *
    from data import *
    data = Data(config)
    app.loadData(data)
    app.adjustCamera()

    root.mainloop()

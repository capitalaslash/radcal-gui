#! /usr/bin/env python2

import os

import vtk
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

import Tkinter as tk
import tkFileDialog
# import ttk

import config
import data
import vtkgui

class App(tk.Frame):
    def __init__(self, parent, config):
        self.config = config
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.pack(fill='both', expand=1)

        # top section
        self.frameFile = tk.Frame(self, bd=1, relief='sunken')
        self.frameFile.pack(fill='x', expand=0)

        buttonFileOpen = tk.Button(self.frameFile, text='Open file', command=self.openFile)
        buttonFileOpen.pack(side='left')

        self.varFileName = tk.StringVar()
        tk.Label(self.frameFile, textvariable=self.varFileName).pack(side='left')

        # middle section
        frameMain = tk.Frame(self)
        frameMain.pack(fill='both', expand=1)

        renWin = vtk.vtkRenderWindow()
        iren = vtkTkRenderWindowInteractor(frameMain, rw=renWin,
            width=600, height=600)
        self.vtk = vtkgui.VtkGui(iren)
        iren.pack(side='left', fill='both', expand=1)

        frameControl = tk.Frame(frameMain)
        frameControl.pack(side='left')

        frameDim = tk.Frame(frameControl)
        frameDim.pack(fill='x', expand=0)
        self.varDim = tk.IntVar()
        self.varDim.set(3)
        tk.Radiobutton(frameDim, text='2D', variable=self.varDim, value=2,
            command=self.dimModified).pack(side='left', fill='x', expand=1)
        tk.Radiobutton(frameDim, text='3D', variable=self.varDim, value=3,
            command=self.dimModified).pack(side='right', fill='x', expand=1)

        tk.Button(frameControl, text='Render', command=self.render).pack(fill='x', expand=0)

        self.buttonClear = tk.Button(frameControl, text='Clear',
            command=self.clear)
        self.buttonClear.pack(fill='x', expand=0)

        self.varScalarBar = tk.IntVar()
        self.checkScalarBar = tk.Checkbutton(frameControl, text='Scalar Bar',
            variable=self.varScalarBar, command=self.scalarBarModified)
        self.checkScalarBar.pack(fill='x')

        self.varContour = tk.IntVar()
        self.checkContour = tk.Checkbutton(frameControl, text='Contour',
            variable=self.varContour, command=self.contourModified)
        self.checkContour.pack(fill='x')

        tk.Label(frameControl, text='Variables:').pack()
        self.varList = tk.Listbox(frameControl, selectmode='browse')
        self.varList.bind('<<ListboxSelect>>', self.varModified)
        self.varList.pack(fill='x')

        tk.Label(frameControl, text='Probing line:').pack()
        self.frameProbe = tk.Frame(frameControl)
        self.frameProbe.pack(fill='x',expand=1)

        validateFloat = (self.parent.register(self.validateFloat),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.varCoord = tk.StringVar()
        self.varCoord.set('t')

        coordTab = [ 'x', 'y', 'z', 't' ]

        counter=0
        self.coordEntries = {}
        self.coordRadios = {}
        self.coordLabels = {}
        for c in coordTab:
            self.coordRadios[c] = tk.Radiobutton(self.frameProbe, text=c,
                variable=self.varCoord, value=c, command=self.coordModified)
            self.coordRadios[c].grid(row=counter, column=0)
            self.coordEntries[c] = tk.Entry(self.frameProbe,
                validate='key', validatecommand=validateFloat)
            self.coordEntries[c].grid(row=counter, column=1)
            self.coordLabels[c] = tk.StringVar()
            tk.Label(self.frameProbe, textvariable=self.coordLabels[c]).grid(row=counter, column=2)
            counter += 1

        # bottom section
        self.frameButton = tk.Frame(self, bd=1, relief='sunken')
        self.frameButton.pack(fill='x', expand=0)
        tk.Button(self.frameButton, text='Quit', command=self.parent.quit, padx=5, pady=5).pack(side='right')
        tk.Button(self.frameButton, text='Print', command=self.write, padx=5, pady=5).pack(side='right')

        self.clear()
        self.initKShortcuts()

    def openFile(self):
        fileName = tkFileDialog.askopenfilename(
            defaultextension='.dat',
            filetypes=[('dat files', '.dat'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='test.dat',
            parent=self.frameFile,
            # title='title'
            )
        self.varFileName.set(fileName)
        self.config[u'fileName'] = fileName
        self.data = data.Data(**self.config)
        self.data.read()
        self.loadData(self.data)

    def dimModified(self):
        print 'dim =', self.varDim.get()
        self.clear()
        if self.varDim.get() == 2:
            self.coordModified(None)
        elif self.varDim.get() == 3:
            for key, widget in self.coordRadios.iteritems():
                widget['state'] = 'disabled'
            for key, widget in self.coordEntries.iteritems():
                widget['state'] = 'disabled'

    def scalarBarModified(self):
        self.vtk.scalarWidget.SetEnabled(self.varScalarBar.get())
        self.vtk.renWin.Render()

    def contourModified(self):
        self.vtk.clear()
        if self.varContour.get():
            self.vtk.renderContour()
        else:
            self.vtk.render()

    def varModified(self, *args):
        idx = self.varList.curselection()[0]
        var = self.varList.get(idx)
        print 'setting ', var
        self.vtk.data.grid.GetInput().GetPointData().SetActiveScalars(var)
        self.vtk.renWin.Render()

    def coordModified(self, *args):
        print 'coord selected:', self.varCoord.get()
        for key, radio in self.coordRadios.iteritems():
            radio['state'] = 'normal'
        for key, entry in self.coordEntries.iteritems():
            if key == self.varCoord.get():
                entry.delete(0, 'end')
                entry['state'] = 'disabled'
            else:
                entry['state'] = 'normal'

    def render(self):
        if(self.varDim.get() == 3):
            self.vtk.render()
            self.checkScalarBar['state']='normal'
            self.checkContour['state']='normal'
        elif(self.varDim.get() == 2):
            if self.varCoord.get() == 't':
                print 'plot over time not implemented yet!'
            else:
                self.vtk.plot(self.buildLine())
        self.buttonClear['state']='normal'

    def buildLine(self):
        bounds = self.data.grid.GetInput().GetBounds()
        line = [
            [bounds[0], bounds[2], bounds[4]],
            [bounds[1], bounds[3], bounds[5]],
        ]
        coordToInt = { 'x': 0, 'y': 1, 'z': 2, 't': 3}
        for key, entry in self.coordEntries.iteritems():
            if key != self.varCoord.get() and key != 't':
                value = float(entry.get())
                line[0][coordToInt[key]] = value
                line[1][coordToInt[key]] = value
        print "probing line:", line
        return line

    def clear(self):
        self.vtk.clear()
        self.buttonClear['state']='disabled'
        self.varScalarBar.set(0)
        self.checkScalarBar['state']='disabled'
        self.varContour.set(0)
        self.checkContour['state']='disabled'
        for key, widget in self.coordRadios.iteritems():
            widget['state'] = 'disabled'
        for key, widget in self.coordEntries.iteritems():
            widget['state'] = 'disabled'


    def validateFloat(self, action, index, value_if_allowed,
            prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if(action=='1'):
            for char in text:
                if char in '0123456789.-+':
                    try:
                        float(value_if_allowed)
                        return True
                    except ValueError:
                        return False
                else:
                    return False
        else:
            return True

    def initKShortcuts(self):
        self.bind_all("<Control-q>", lambda e: self.parent.quit() )
        self.bind_all("q", lambda e: self.parent.quit() )

    def loadData(self, data):
        self.vtk.loadData(data)
        self.data = data
        self.varList.delete(0, 'end')
        varNames = self.vtk.data.getVarList()
        for var in varNames:
            self.varList.insert('end', var)
        bounds = self.data.grid.GetInput().GetBounds()
        coordBounds = {}
        coordBounds['x'] = [bounds[0], bounds[1]]
        coordBounds['y'] = [bounds[2], bounds[3]]
        coordBounds['z'] = [bounds[4], bounds[5]]
        coordBounds['t'] = [0., 1.]

        for c in coordBounds:
            text = '[' + str(coordBounds[c][0]) + ', ' + str(coordBounds[c][1]) + ']'
            self.coordLabels[c].set(text)

    def write(self):
        fileName = tkFileDialog.asksaveasfilename(
            defaultextension='.vtu',
            filetypes=[('vtu files', '.vtu'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='grid.vtu',
            parent=self.frameButton,
        )
        self.data.write()

if __name__ == '__main__':
    # data = data.Data(config.config)

    root = tk.Tk()
    app = App(root, config.config)
    root.mainloop()

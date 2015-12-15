#! /usr/bin/env python2

import os

import vtk
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

import Tkinter as tk
import tkFileDialog
# import ttk

import time
import config
import data
import vtkgui

class App(tk.Frame):
    def __init__(self, parent, config):
        self.config = config
        tk.Frame.__init__(self, parent)
        self.parent = parent
        parent.wm_title('radcal-gui')
        self.pack(fill='both', expand=1)

        # top section
        self.frameFile = tk.Frame(self, bd=1, relief='sunken')
        self.frameFile.pack(fill='x', expand=0)

        buttonFileOpen = tk.Button(self.frameFile, text='Open file', command=self.open_file)
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
            command=self.dim_modified).pack(side='left', fill='x', expand=1)
        tk.Radiobutton(frameDim, text='3D', variable=self.varDim, value=3,
            command=self.dim_modified).pack(side='right', fill='x', expand=1)

        self.buttonRender = tk.Button(frameControl, text='Render',
            command=self.render, state='disabled')
        self.buttonRender.pack(fill='x', expand=0)

        self.buttonClear = tk.Button(frameControl, text='Clear',
            command=self.clear)
        self.buttonClear.pack(fill='x', expand=0)

        self.varScalarBar = tk.IntVar()
        self.checkScalarBar = tk.Checkbutton(frameControl, text='Scalar Bar',
            variable=self.varScalarBar, command=self.scalarbar_modified)
        self.checkScalarBar.pack(fill='x')

        self.varContour = tk.IntVar()
        self.checkContour = tk.Checkbutton(frameControl, text='Contour',
            variable=self.varContour, command=self.contour_modified)
        self.checkContour.pack(fill='x')

        tk.Label(frameControl, text='Variables:').pack()
        self.varList = tk.Listbox(frameControl, selectmode='browse')
        self.varList.bind('<<ListboxSelect>>', self.var_modified)
        self.varList.pack(fill='x')

        tk.Label(frameControl, text='Probing line:').pack()
        self.frameProbe = tk.Frame(frameControl)
        self.frameProbe.pack(fill='x',expand=1)

        validate_float = (self.parent.register(self.validate_float),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.varCoord = tk.StringVar()
        # self.varCoord.set('x')

        coordTab = [ 'x', 'y', 'z' ]

        counter=0
        self.coordEntries = {}
        self.coordRadios = {}
        self.coordLabels = {}
        for c in coordTab:
            self.coordRadios[c] = tk.Radiobutton(self.frameProbe, text=c,
                variable=self.varCoord, value=c, command=self.coord_modified)
            self.coordRadios[c].grid(row=counter, column=0)
            self.coordEntries[c] = tk.Entry(self.frameProbe,
                validate='key', validatecommand=validate_float)
            self.coordEntries[c].grid(row=counter, column=1)
            self.coordLabels[c] = tk.StringVar()
            tk.Label(self.frameProbe, textvariable=self.coordLabels[c]).grid(row=counter, column=2)
            counter += 1

        self.varTimePlot = tk.IntVar()
        self.checkTimePlot = tk.Checkbutton(self.frameProbe, text='time plot',
            variable=self.varTimePlot, command=self.timeplot_modified,
            state='disabled')
        self.checkTimePlot.grid(row=3, column=0, columnspan=2)

        # bottom section
        self.frameButton = tk.Frame(self, bd=1, relief='sunken')
        self.frameButton.pack(fill='x', expand=0)
        tk.Button(self.frameButton, text='Quit', command=self.parent.quit, padx=5, pady=5).pack(side='right')
        tk.Button(self.frameButton, text='Save', command=self.write, padx=5, pady=5).pack(side='right')
        tk.Button(self.frameButton, text='Print', command=self.screenshot, padx=5, pady=5).pack(side='right')
        frameTime = tk.Frame(self.frameButton)
        frameTime.pack(side='left')

        buttonCfg = {
            'side': 'left'
        }
        self.buttonFirst = tk.Button(frameTime, text='|<',
            command=lambda: self.set_timestep(0), width=3)
        self.buttonFirst.pack(**buttonCfg)
        self.buttonPrev = tk.Button(frameTime, text='<',
            command=lambda: self.set_timestep(self.varCurTimeStep.get()-1), width=3)
        self.buttonPrev.pack(**buttonCfg)
        self.buttonPlay = tk.Button(frameTime, text='|>',
            command=self.play, width=3)
        self.buttonPlay.pack(**buttonCfg)
        self.buttonNext = tk.Button(frameTime, text='>',
            command=lambda: self.set_timestep(self.varCurTimeStep.get()+1), width=3)
        self.buttonNext.pack(**buttonCfg)
        self.buttonLast = tk.Button(frameTime, text='>|',
            command=lambda: self.set_timestep(self.vtk.data.numTimes-1), width=3)
        self.buttonLast.pack(**buttonCfg)

        tk.Label(frameTime, text='time:').pack(side='left', padx=10)
        self.varCurTime = tk.DoubleVar()
        self.varCurTime.set(0.0)
        tk.Label(frameTime, textvariable=self.varCurTime, relief='sunken', width=10).pack(side='left')

        tk.Label(frameTime, text='timestep:').pack(side='left', padx=10)
        self.varCurTimeStep = tk.IntVar()
        self.varCurTimeStep.set('0')
        validate_int = (self.parent.register(self.validate_int),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entryTimeStep = tk.Entry(frameTime, text=self.varCurTimeStep,
            validate='key', validatecommand=validate_int, relief='sunken',
            width=10, justify='right')
        self.entryTimeStep.pack(side='left')
        self.stringTimeStep = tk.StringVar()
        self.labelTimeStep = tk.Label(frameTime,
            textvariable=self.stringTimeStep)
        self.labelTimeStep.pack(side='left')
        self.buttonGo = tk.Button(frameTime, text='go',
            command=self.timestep_modified)
        self.buttonGo.pack(side='left')

        self.clear()
        self.init_kshortcuts()

    def open_file(self):
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
        self.load_data(self.config)
        self.buttonRender['state'] = 'normal'

    def dim_modified(self):
        dim = self.varDim.get()
        self.vtk.dim = dim
        self.vtk.markerWidget.EnabledOff()
        self.clear()
        if dim == 2:
            self.coord_modified(None)
            self.set_probe_panel_state('normal')
            self.checkTimePlot['state'] = 'normal'
        elif self.varDim.get() == 3:
            self.set_probe_panel_state('disabled')
            self.checkTimePlot['state'] = 'disabled'

    def set_probe_panel_state(self, state):
        for key, widget in self.coordRadios.iteritems():
            widget['state'] = state
        for key, widget in self.coordEntries.iteritems():
            widget['state'] = state

    def set_time_frame_state(self, state):
        self.buttonFirst['state'] = state
        self.buttonPrev['state'] = state
        self.buttonPlay['state'] = state
        self.buttonNext['state'] = state
        self.buttonLast['state'] = state
        self.entryTimeStep['state'] = state
        self.buttonGo['state'] = state

    def scalarbar_modified(self):
        self.vtk.scalarBarWidget.SetEnabled(self.varScalarBar.get())
        self.vtk.renWin.Render()

    def contour_modified(self):
        self.vtk.clear()
        self.vtk.contourState = bool(self.varContour.get())
        self.vtk.render()

    def var_modified(self, *args):
        idx = self.varList.curselection()[0]
        var = self.varList.get(idx)
        print 'setting ', var
        self.vtk.change_activescalar(var)
        self.vtk.update_scalarbar()
        self.vtk.update_contourrange()
        self.vtk.renWin.Render()

    def coord_modified(self, *args):
        print 'coord selected:', self.varCoord.get()
        for key, radio in self.coordRadios.iteritems():
            radio['state'] = 'normal'
        for key, entry in self.coordEntries.iteritems():
            if key == self.varCoord.get():
                entry.delete(0, 'end')
                entry['state'] = 'disabled'
            else:
                entry['state'] = 'normal'

    def timeplot_modified(self, *args):
        if self.varTimePlot.get():
            for key, radio in self.coordRadios.iteritems():
                radio['state'] = 'disabled'
            for key, entry in self.coordEntries.iteritems():
                entry['state'] = 'normal'
            self.set_time_frame_state('disabled')
        else:
            self.coord_modified()
            self.set_time_frame_state('normal')

    def timestep_modified(self):
        step = self.varCurTimeStep.get()
        self.vtk.goto_timestep(step)
        self.varCurTime.set(self.vtk.data.times[step])

    def set_timestep(self, step):
        if step > -1 and step < self.vtk.data.numTimes:
            self.varCurTimeStep.set(step)
            self.timestep_modified()

    def play(self):
        for t in range(self.varCurTimeStep.get()+1, self.vtk.data.numTimes):
            time.sleep(0.5)
            self.set_timestep(t)

    def render(self):
        if(self.varDim.get() == 3):
            self.vtk.update_scalarbar()
            self.vtk.render()
            self.checkScalarBar['state']='normal'
            self.checkContour['state']='normal'
        elif(self.varDim.get() == 2):
            self.vtk.set_line(self.build_line())
            self.vtk.plot()
        self.buttonClear['state']='normal'

    def build_line(self):
        bounds = self.vtk.data.grid[0].GetInput().GetBounds()
        line = [
            [bounds[0], bounds[2], bounds[4]],
            [bounds[1], bounds[3], bounds[5]],
        ]
        coordToInt = { 'x': 0, 'y': 1, 'z': 2}
        for key, entry in self.coordEntries.iteritems():
            if key != self.varCoord.get():
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
        self.set_probe_panel_state('disabled')

    def validate_float(self, action, index, value_if_allowed,
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

    def validate_int(self, action, index, value_if_allowed,
            prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if(action=='1'):
            for char in text:
                if char in '0123456789':
                    try:
                        int(value_if_allowed)
                        return True
                    except ValueError:
                        return False
                else:
                    return False
        else:
            return True

    def init_kshortcuts(self):
        self.bind_all("<Control-q>", lambda e: self.parent.quit() )
        self.bind_all("q", lambda e: self.parent.quit() )

    def load_data(self, config):
        self.vtk.load_data(config)
        self.varList.delete(0, 'end')
        varNames = self.vtk.data.get_varlist()
        for var in varNames:
            self.varList.insert('end', var)
        bounds = self.vtk.data.grid[0].GetInput().GetBounds()
        coordBounds = {}
        coordBounds['x'] = [bounds[0], bounds[1]]
        coordBounds['y'] = [bounds[2], bounds[3]]
        coordBounds['z'] = [bounds[4], bounds[5]]

        for c in coordBounds:
            text = '[' + str(coordBounds[c][0]) + ', ' + str(coordBounds[c][1]) + ']'
            self.coordLabels[c].set(text)
        self.stringTimeStep.set('[0, ' + str(self.vtk.data.numTimes-1) + ']')

    def write(self):
        fileName = tkFileDialog.asksaveasfilename(
            defaultextension='.vtu',
            filetypes=[('vtu files', '.vtu'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='grid.vtu',
            parent=self.frameButton,
        )
        if fileName is not None:
            self.data.write(fileName)

    def screenshot(self):
        fileName = tkFileDialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG image', '.png'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='screenshot.png',
            parent=self.frameButton,
        )
        if fileName is not None:
            self.vtk.screenshot(fileName)

if __name__ == '__main__':
    # data = data.Data(config.config)

    root = tk.Tk()
    app = App(root, config.config)
    root.mainloop()

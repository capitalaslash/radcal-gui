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
    """The visualization app."""
    def __init__(self, parent, config):
        self.config = config
        tk.Frame.__init__(self, parent)
        self.parent = parent
        parent.wm_title('radcal-gui')
        self.pack(fill='both', expand=1)

        # top section
        self.frame_file = tk.Frame(self, bd=1, relief='sunken')
        self.frame_file.pack(fill='x', expand=0)

        tk.Button(self.frame_file, text='Open file',
          command=self.open_file).pack(side='left')

        self.var_filename = tk.StringVar()
        tk.Label(self.frame_file, textvariable=self.var_filename).pack(side='left')

        # middle section
        frame_main = tk.Frame(self)
        frame_main.pack(fill='both', expand=1)

        ren_win = vtk.vtkRenderWindow()
        iren = vtkTkRenderWindowInteractor(frame_main, rw=ren_win,
            width=600, height=600)
        self.vtk = vtkgui.VtkGui(iren)
        iren.pack(side='left', fill='both', expand=1)

        frame_control = tk.Frame(frame_main)
        frame_control.pack(side='left')

        frame_dim = tk.Frame(frame_control)
        frame_dim.pack(fill='x', expand=0)
        self.var_dim = tk.IntVar()
        self.var_dim.set(3)
        tk.Radiobutton(frame_dim, text='2D', variable=self.var_dim,
          value=2, command=self.dim_modified).pack(side='left', fill='x', expand=1)
        tk.Radiobutton(frame_dim, text='3D', variable=self.var_dim,
          value=3, command=self.dim_modified).pack(side='right', fill='x', expand=1)

        self.button_render = tk.Button(frame_control, text='Render',
            command=self.render, state='disabled')
        self.button_render.pack(fill='x', expand=0)

        self.button_clear = tk.Button(frame_control, text='Clear',
            command=self.clear)
        self.button_clear.pack(fill='x', expand=0)

        self.var_scalarbar = tk.IntVar()
        self.check_scalarbar = tk.Checkbutton(frame_control, text='Scalar Bar',
            variable=self.var_scalarbar, command=self.scalarbar_modified)
        self.check_scalarbar.pack(fill='x')

        self.var_contour = tk.IntVar()
        self.check_contour = tk.Checkbutton(frame_control, text='Contour',
            variable=self.var_contour, command=self.contour_modified)
        self.check_contour.pack(fill='x')

        tk.Label(frame_control, text='Variables:').pack()
        self.list_var = tk.Listbox(frame_control, selectmode='browse')
        self.list_var.bind('<<ListboxSelect>>', self.var_modified)
        self.list_var.pack(fill='x')

        tk.Label(frame_control, text='Probing line:').pack()
        self.frame_probe = tk.Frame(frame_control)
        self.frame_probe.pack(fill='x',expand=1)

        validate_float = (self.parent.register(self.validate_float),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.var_coord = tk.StringVar()
        # self.var_coord.set('x')

        coord_tab = [ 'x', 'y', 'z' ]

        counter=0
        self.entry_coord = {}
        self.radio_coord = {}
        self.label_coord = {}
        for c in coord_tab:
            self.radio_coord[c] = tk.Radiobutton(self.frame_probe, text=c,
                variable=self.var_coord, value=c, command=self.coord_modified)
            self.radio_coord[c].grid(row=counter, column=0)
            self.entry_coord[c] = tk.Entry(self.frame_probe,
                validate='key', validatecommand=validate_float)
            self.entry_coord[c].grid(row=counter, column=1)
            self.label_coord[c] = tk.StringVar()
            tk.Label(self.frame_probe, textvariable=self.label_coord[c]).grid(row=counter, column=2)
            counter += 1

        self.var_timeplot = tk.IntVar()
        self.check_timeplot = tk.Checkbutton(self.frame_probe, text='time plot',
            variable=self.var_timeplot, command=self.timeplot_modified,
            state='disabled')
        self.check_timeplot.grid(row=3, column=0, columnspan=2)

        # bottom section
        self.frame_control = tk.Frame(self, bd=1, relief='sunken')
        self.frame_control.pack(fill='x', expand=0)
        tk.Button(self.frame_control, text='Quit', command=self.parent.quit, padx=5, pady=5).pack(side='right')
        tk.Button(self.frame_control, text='Save', command=self.write, padx=5, pady=5).pack(side='right')
        tk.Button(self.frame_control, text='Print', command=self.screenshot, padx=5, pady=5).pack(side='right')
        frame_time = tk.Frame(self.frame_control)
        frame_time.pack(side='left')

        button_cfg = {
            'side': 'left'
        }
        self.button_first = tk.Button(frame_time, text='|<',
            command=lambda: self.set_timestep(0), width=3)
        self.button_first.pack(**button_cfg)
        self.button_prev = tk.Button(frame_time, text='<',
            command=lambda: self.set_timestep(self.var_curtimestep.get()-1), width=3)
        self.button_prev.pack(**button_cfg)
        self.button_play = tk.Button(frame_time, text='|>',
            command=self.play, width=3)
        self.button_play.pack(**button_cfg)
        self.button_next = tk.Button(frame_time, text='>',
            command=lambda: self.set_timestep(self.var_curtimestep.get()+1), width=3)
        self.button_next.pack(**button_cfg)
        self.button_last = tk.Button(frame_time, text='>|',
            command=lambda: self.set_timestep(self.vtk.data.num_times-1), width=3)
        self.button_last.pack(**button_cfg)

        tk.Label(frame_time, text='time:').pack(side='left', padx=10)
        self.var_curtime = tk.DoubleVar()
        self.var_curtime.set(0.0)
        tk.Label(frame_time, textvariable=self.var_curtime, relief='sunken', width=10).pack(side='left')

        tk.Label(frame_time, text='timestep:').pack(side='left', padx=10)
        self.var_curtimestep = tk.IntVar()
        self.var_curtimestep.set('0')
        validate_int = (self.parent.register(self.validate_int),
            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry_timestep = tk.Entry(frame_time, text=self.var_curtimestep,
            validate='key', validatecommand=validate_int, relief='sunken',
            width=10, justify='right')
        self.entry_timestep.pack(side='left')
        self.string_timestep = tk.StringVar()
        self.label_timestep = tk.Label(frame_time,
            textvariable=self.string_timestep)
        self.label_timestep.pack(side='left')
        self.button_go = tk.Button(frame_time, text='go',
            command=self.timestep_modified)
        self.button_go.pack(side='left')

        self.clear()
        self.init_kshortcuts()

    def open_file(self):
        filename = tkFileDialog.askopenfilename(
            defaultextension='.dat',
            filetypes=[('dat files', '.dat'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='test.dat',
            parent=self.frame_file,
            # title='title'
            )
        self.var_filename.set(filename)
        self.config[u'filename'] = filename
        self.load_data(self.config)
        self.button_render['state'] = 'normal'

    def dim_modified(self):
        dim = self.var_dim.get()
        self.vtk.dim = dim
        self.vtk.marker_widget.EnabledOff()
        self.clear()
        if dim == 2:
            self.coord_modified(None)
            self.set_probe_panel_state('normal')
            self.check_timeplot['state'] = 'normal'
        elif self.var_dim.get() == 3:
            self.set_probe_panel_state('disabled')
            self.check_timeplot['state'] = 'disabled'

    def set_probe_panel_state(self, state):
        for key, widget in self.radio_coord.iteritems():
            widget['state'] = state
        for key, widget in self.entry_coord.iteritems():
            widget['state'] = state

    def set_time_frame_state(self, state):
        self.button_first['state'] = state
        self.button_prev['state'] = state
        self.button_play['state'] = state
        self.button_next['state'] = state
        self.button_last['state'] = state
        self.entry_timestep['state'] = state
        self.button_go['state'] = state

    def scalarbar_modified(self):
        self.vtk.scalarbar_widget.SetEnabled(self.var_scalarbar.get())
        self.vtk.ren_win.Render()

    def contour_modified(self):
        self.vtk.clear()
        self.vtk.contour_state = bool(self.var_contour.get())
        self.vtk.render()

    def var_modified(self, *args):
        idx = self.list_var.curselection()[0]
        var = self.list_var.get(idx)
        print 'setting ', var
        self.vtk.change_activescalar(var)
        self.vtk.update_scalarbar()
        self.vtk.update_contourrange()
        self.vtk.ren_win.Render()

    def coord_modified(self, *args):
        print 'coord selected:', self.var_coord.get()
        for key, radio in self.radio_coord.iteritems():
            radio['state'] = 'normal'
        for key, entry in self.entry_coord.iteritems():
            if key == self.var_coord.get():
                entry.delete(0, 'end')
                entry['state'] = 'disabled'
            else:
                entry['state'] = 'normal'

    def timeplot_modified(self, *args):
        if self.var_timeplot.get():
            for key, radio in self.radio_coord.iteritems():
                radio['state'] = 'disabled'
            for key, entry in self.entry_coord.iteritems():
                entry['state'] = 'normal'
            self.set_time_frame_state('disabled')
        else:
            self.coord_modified()
            self.set_time_frame_state('normal')

    def timestep_modified(self):
        step = self.var_curtimestep.get()
        self.vtk.goto_timestep(step)
        self.var_curtime.set(self.vtk.data.times[step])

    def set_timestep(self, step):
        if 0 <= step < self.vtk.data.num_times:
            self.var_curtimestep.set(step)
            self.timestep_modified()

    def play(self):
        for t in range(self.var_curtimestep.get()+1, self.vtk.data.num_times):
            time.sleep(0.5)
            self.set_timestep(t)

    def render(self):
        if self.var_dim.get() == 3:
            self.vtk.update_scalarbar()
            self.vtk.render()
            self.check_scalarbar['state']='normal'
            self.check_contour['state']='normal'
        elif self.var_dim.get() == 2:
            self.vtk.set_line(self.build_line())
            self.vtk.plot()
        self.button_clear['state']='normal'

    def build_line(self):
        bounds = self.vtk.data.grid[0].GetInput().GetBounds()
        line = [
            [bounds[0], bounds[2], bounds[4]],
            [bounds[1], bounds[3], bounds[5]],
        ]
        coord_to_int = { 'x': 0, 'y': 1, 'z': 2}
        for key, entry in self.entry_coord.iteritems():
            if key != self.var_coord.get():
                value = float(entry.get())
                line[0][coord_to_int[key]] = value
                line[1][coord_to_int[key]] = value
        print "probing line:", line
        return line

    def clear(self):
        self.vtk.clear()
        self.button_clear['state']='disabled'
        self.var_scalarbar.set(0)
        self.check_scalarbar['state']='disabled'
        self.var_contour.set(0)
        self.check_contour['state']='disabled'
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
        self.list_var.delete(0, 'end')
        varnames = self.vtk.data.get_varnames()
        for var in varnames:
            self.list_var.insert('end', var)
        bounds = self.vtk.data.grid[0].GetInput().GetBounds()
        coord_bounds = {}
        coord_bounds['x'] = [bounds[0], bounds[1]]
        coord_bounds['y'] = [bounds[2], bounds[3]]
        coord_bounds['z'] = [bounds[4], bounds[5]]

        for c in coord_bounds:
            text = '[' + str(coord_bounds[c][0]) + ', ' + str(coord_bounds[c][1]) + ']'
            self.label_coord[c].set(text)
        self.string_timestep.set('[0, ' + str(self.vtk.data.num_times-1) + ']')

    def write(self):
        filename = tkFileDialog.asksaveasfilename(
            defaultextension='.vtu',
            filetypes=[('vtu files', '.vtu'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='grid.vtu',
            parent=self.frame_control,
        )
        if filename is not None:
            self.data.write(filename)

    def screenshot(self):
        filename = tkFileDialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG image', '.png'), ('all files', '.*')],
            initialdir=os.getcwd(),
            initialfile='screenshot.png',
            parent=self.frame_control,
        )
        if filename is not None:
            self.vtk.screenshot(filename)

if __name__ == '__main__':
    # data = data.Data(config.config)

    root = tk.Tk()
    app = App(root, config.config)
    root.mainloop()

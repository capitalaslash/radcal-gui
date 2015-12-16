#! /usr/bin/env python2

import vtk
import time
import data

class VtkGui(object):
    """
    Vtk window manager
    """

    def __init__(self, iren):
        """
        initialization of the interactor and fixed objects
        """
        # state indicators
        self.dim = 3
        self.contour_state = False

        # interactor
        self.iren = iren

        # empty defaults
        self.data = data.Data()
        self.current_timestep = 0
        self.line_points = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]

        # camera
        self.camera = vtk.vtkCamera()
        self.camera.Elevation(-70)
        self.camera.SetViewUp(0, 0, 1)
        self.camera.Azimuth(30)
        self.camera.Dolly(0.8)

        # lookup table
        self.lut = vtk.vtkLookupTable()
        self.lut.SetHueRange(0.66667, 0.0)
        self.lut.Build()

        # 3d mapper
        self.mapper3d = vtk.vtkDataSetMapper()
        self.mapper3d.SetLookupTable(self.lut)
        self.mapper3d.InterpolateScalarsBeforeMappingOn()

        # contour
        self.contour = vtk.vtkContourFilter()
        self.contour.SetNumberOfContours(1)

        # actors
        self.main_actor = vtk.vtkLODActor()
        self.main_actor.SetMapper(self.mapper3d)
        self.outline_actor = vtk.vtkActor()

        # render window
        self.ren_win = self.iren.GetRenderWindow()
        # self.ren_win.SetSize(800, 800)
        # self.ren_win.SetNumberOfLayers(2)

        # main renderer
        self.ren = vtk.vtkRenderer()
        # self.ren.SetLayer(0)
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.ren.SetActiveCamera(self.camera)
        self.ren_win.AddRenderer(self.ren)

        # set interaction style to paraview style
        self.iren.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # keyboard bindings
        self.iren.AddObserver(vtk.vtkCommand.KeyPressEvent, self.on_keypress)

        self.add_widgets()

    def add_widgets(self):
        # axes
        axes = vtk.vtkAxesActor()
        self.marker_widget = vtk.vtkOrientationMarkerWidget()
        self.marker_widget.SetInteractor(self.iren)
        self.marker_widget.SetOrientationMarker(axes)
        self.marker_widget.SetViewport(0.0, 0.0, 0.25, 0.25)

        # scalar bar
        self.scalarbar_actor = vtk.vtkScalarBarActor()
        self.scalarbar_actor.SetLookupTable(self.lut)
        self.scalarbar_widget = vtk.vtkScalarBarWidget()
        self.scalarbar_widget.SetInteractor(self.iren)
        self.scalarbar_widget.SetScalarBarActor(self.scalarbar_actor)

        # contour slider
        self.slider_rep = vtk.vtkSliderRepresentation2D()
        self.slider_rep.SetTitleText("contour")
        self.slider_rep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedViewport()
        self.slider_rep.GetPoint1Coordinate().SetValue(0.65, 0.1)
        self.slider_rep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedViewport()
        self.slider_rep.GetPoint2Coordinate().SetValue(0.95, 0.1)

        self.slider_widget = vtk.vtkSliderWidget()
        self.slider_widget.SetInteractor(self.iren)
        self.slider_widget.SetRepresentation(self.slider_rep)
        self.slider_widget.SetAnimationModeToAnimate()
        self.slider_widget.AddObserver(vtk.vtkCommand.InteractionEvent,
            self.update_contour);

    def clear(self):
        """
        surface visualization of data
        """
        self.ren.RemoveAllViewProps()
        self.ren_win.Render()

    def render(self):
        """
        select the current mode of visualization on trigger proper function
        """
        print 'rendering timestep', self.current_timestep

        if self.dim == 3:
            self.marker_widget.EnabledOn()
            self.slider_widget.SetEnabled(int(self.contour_state))
            if self.contour_state:
                self.render_contour()
            else:
                self.render_3d()
        else:
            self.plot()

    def render_3d(self):
        """
        surface visualization of data
        """
        self.ren.RemoveActor(self.outline_actor)
        if self.data.num_times > 0:
            self.mapper3d.SetInputData(self.data.grid[self.current_timestep])
        self.ren.AddActor(self.main_actor)
        self.ren.ResetCamera()
        self.ren_win.Render()

    def render_contour(self):
        """
        contour visualization of data
        """
        active_scalar = self.data.grid[self.current_timestep].GetPointData().GetScalars()

        self.contour.SetInputData(self.data.grid[self.current_timestep])

        scalar_range = active_scalar.GetRange()
        mean = 0.5*(scalar_range[0]+scalar_range[1])
        self.contour.SetValue(0, mean)

        # viz
        self.mapper3d.SetInputConnection(self.contour.GetOutputPort())
        self.ren.AddActor(self.main_actor)

        self.add_outline()

        self.update_contourrange()
        self.slider_rep.SetValue(mean)
        self.slider_widget.EnabledOn()
        self.ren_win.Render()

    def add_outline(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputData(self.data.grid[self.current_timestep])
        outline_mapper = vtk.vtkDataSetMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        self.outline_actor.SetMapper(outline_mapper)
        self.ren.AddActor(self.outline_actor)

    def set_line(self, linePoints):
        self.line_points = linePoints

    def plot(self):
        """
        plot visualization of data
        """
        self.ren.RemoveAllViewProps()
        # self.marker_widget.EnabledOff()
        active_scalar = self.data.grid[self.current_timestep].GetPointData().GetScalars()
        # print 'active scalar is', active_scalar.GetName()

        line = vtk.vtkLineSource()
        line.SetResolution(30)
        line.SetPoint1(self.line_points[0])
        line.SetPoint2(self.line_points[1])
        probe = vtk.vtkProbeFilter()
        probe.SetInputConnection(line.GetOutputPort())
        probe.SetSourceData(self.data.grid[self.current_timestep])

        tuber = vtk.vtkTubeFilter()
        tuber.SetInputConnection(probe.GetOutputPort())
        tuber.SetRadius(0.02)
        line_mapper = vtk.vtkPolyDataMapper()
        line_mapper.SetInputConnection(tuber.GetOutputPort())
        line_actor = vtk.vtkActor()
        line_actor.SetMapper(line_mapper)
        # self.ren.AddActor(line_actor)

        xyplot = vtk.vtkXYPlotActor()
        if vtk.VTK_MAJOR_VERSION <= 5:
            xyplot.AddInput(probe.GetOutput())
        else:
            xyplot.AddDataSetInputConnection(probe.GetOutputPort())
        xyplot.GetPositionCoordinate().SetValue(0.05, 0.05, 0.0)
        xyplot.GetPosition2Coordinate().SetValue(0.9, 0.9, 0.0) #relative to Position
        xyplot.SetXValuesToArcLength()
        xyplot.SetNumberOfXLabels(6)
        xyplot.SetNumberOfYLabels(6)
        xyplot.SetTitle("title")
        xyplot.SetXTitle("length")
        xyplot.SetYTitle("var")
        # xyplot.SetXRange(.1, .35)
        # xyplot.SetYRange(.2, .4)
        # xyplot.GetProperty().SetColor(0, 0, 0)
        xyplot.GetProperty().SetLineWidth(2)
        self.ren.AddActor2D(xyplot)
        # self.xyplotWidget = vtk.vtkXYPlotWidget()
        # self.xyplotWidget.SetXYPlotActor(xyplot)
        # self.xyplotWidget.SetInteractor(self.iren)
        # self.xyplotWidget.EnabledOn()

        self.ren_win.Render()

    def update_contour(self, obj, ev):
        value = self.slider_widget.GetRepresentation().GetValue()
        self.contour.SetValue(0, value)

    def pointdata_modified(self, obj, ev):
        """
        callback: activated on modifications to pointData in grid
        """
        active_scalar = self.data.grid[self.current_timestep].GetPointData().GetScalars()
        # if not self.mapper3d == None:
        #     self.mapper3d.SetScalarRange(active_scalar.GetRange())
        # scalarBarActor = vtk.vtkScalarBarActor()
        # scalarBarActor.SetTitle(active_scalar.GetName())
        # scalarBarActor.SetLookupTable(self.lut)
        # self.scalarbar_widget.SetScalarBarActor(scalarBarActor)

    def on_keypress(self, obj, ev):
        """
        callback: activated when a key is pressed
        """
        char = obj.GetKeyCode()
        # print 'pressed: ', char
        if char == '1':
            self.change_activescalar('c1')
        elif char == '2':
            self.change_activescalar('c2')
        elif char == '3':
            self.change_activescalar('c3')
        elif char == 'r':
            self.update_scalarbar()
            self.render()
        elif char == 'c':
            self.render_contour()
        elif char == 's':
            self.scalarbar_widget.SetEnabled(1-self.scalarbar_widget.GetEnabled())
            self.ren_win.Render()
        elif char == 'a':
            self.update_scalarbar()
            self.ren_win.Render()
        elif char == ' ':
            self.time_play()
        elif char == 'k':
            self.time_next()
        elif char == 'j':
            self.time_prev()
        elif char == 'x':
            self.clear()
        elif char == 'p':
            self.screenshot('screenshot.png')

    def change_activescalar(self, name):
        for t in xrange(0, self.data.num_times):
            self.data.grid[t].GetPointData().SetActiveScalars(name)
        self.update_scalarbar()
        self.update_contourrange()
        self.ren_win.Render()

    def update_scalarbar(self):
        # resetRange = kwargs.get('resetRange', False)
        active_scalar = self.data.grid[self.current_timestep].GetPointData().GetScalars()
        self.scalarbar_actor.SetTitle(active_scalar.GetName())
        self.mapper3d.SetScalarRange(active_scalar.GetRange())

    def update_contourrange(self):
        active_scalar = self.data.grid[self.current_timestep].GetPointData().GetScalars()
        scalar_range = active_scalar.GetRange()
        self.slider_rep.SetMinimumValue(scalar_range[0])
        self.slider_rep.SetMaximumValue(scalar_range[1])

    def goto_timestep(self, step):
        self.current_timestep = step
        self.render()

    def time_next(self):
        if not self.current_timestep == self.data.num_times-1:
            self.current_timestep += 1
            self.render()

    def time_prev(self):
        if not self.current_timestep == 0:
            self.current_timestep -= 1
            self.render()

    def time_first(self):
        self.current_timestep = 0
        self.render()

    def time_last(self):
        self.current_timestep = self.data.num_times-1
        self.render()

    def time_play(self):
        for t in xrange(self.current_timestep+1, self.data.num_times):
            time.sleep(0.5)
            self.current_timestep = t
            self.render()

    def load_data(self, config):
        self.data.config = config
        self.data.read()
        self.data.grid[self.current_timestep].GetPointData().AddObserver(
            vtk.vtkCommand.ModifiedEvent, self.pointdata_modified)

    def screenshot(self, filename):
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.ren_win)
        w2if.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(filename)
        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(w2if.GetOutput())
        else:
            writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

if __name__ == '__main__':
    import config
    import data

    ren_win = vtk.vtkRenderWindow()
    ren_win.SetSize(config.config['vtkWidth'], config.config['vtkHeight'])
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(ren_win)

    app = VtkGui(iren)
    app.load_data(config.config)

    iren.Initialize()
    ren_win.Render()
    iren.Start()

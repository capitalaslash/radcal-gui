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
        self.contourState = False

        # interactor
        self.iren = iren

        # empty defaults
        self.data = data.Data()
        self.currentTimeStep = 0
        self.linePoints = [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]

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
        self.mainActor = vtk.vtkLODActor()
        self.mainActor.SetMapper(self.mapper3d)
        self.outlineActor = vtk.vtkActor()

        # render window
        self.renWin = self.iren.GetRenderWindow()
        # self.renWin.SetSize(800, 800)
        # self.renWin.SetNumberOfLayers(2)

        # main renderer
        self.ren = vtk.vtkRenderer()
        # self.ren.SetLayer(0)
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.ren.SetActiveCamera(self.camera)
        self.renWin.AddRenderer(self.ren)

        # set interaction style to paraview style
        self.iren.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # keyboard bindings
        self.iren.AddObserver(vtk.vtkCommand.KeyPressEvent, self.on_keypress)

        self.add_widgets()

    def add_widgets(self):
        # axes
        axes = vtk.vtkAxesActor()
        self.markerWidget = vtk.vtkOrientationMarkerWidget()
        self.markerWidget.SetInteractor(self.iren)
        self.markerWidget.SetOrientationMarker(axes)
        self.markerWidget.SetViewport(0.0, 0.0, 0.25, 0.25)

        # scalar bar
        self.scalarBarActor = vtk.vtkScalarBarActor()
        self.scalarBarActor.SetLookupTable(self.lut)
        self.scalarBarWidget = vtk.vtkScalarBarWidget()
        self.scalarBarWidget.SetInteractor(self.iren)
        self.scalarBarWidget.SetScalarBarActor(self.scalarBarActor)

        # contour slider
        self.sliderRep = vtk.vtkSliderRepresentation2D()
        self.sliderRep.SetTitleText("contour")
        self.sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedViewport()
        self.sliderRep.GetPoint1Coordinate().SetValue(0.65, 0.1)
        self.sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedViewport()
        self.sliderRep.GetPoint2Coordinate().SetValue(0.95, 0.1)

        self.sliderWidget = vtk.vtkSliderWidget()
        self.sliderWidget.SetInteractor(self.iren)
        self.sliderWidget.SetRepresentation(self.sliderRep)
        self.sliderWidget.SetAnimationModeToAnimate()
        self.sliderWidget.AddObserver(vtk.vtkCommand.InteractionEvent,
            self.update_contour);

    def clear(self):
        """
        surface visualization of data
        """
        self.ren.RemoveAllViewProps()
        self.renWin.Render()

    def render(self):
        """
        select the current mode of visualization on trigger proper function
        """
        print 'rendering timestep', self.currentTimeStep

        if self.dim == 3:
            self.markerWidget.EnabledOn()
            self.sliderWidget.SetEnabled(int(self.contourState))
            if self.contourState:
                self.render_contour()
            else:
                self.render_3d()
        else:
            self.plot()

    def render_3d(self):
        """
        surface visualization of data
        """
        self.ren.RemoveActor(self.outlineActor)
        if self.data.numTimes > 0:
            self.mapper3d.SetInputConnection(self.data.grid[self.currentTimeStep].GetOutputPort())
        self.ren.AddActor(self.mainActor)
        self.ren.ResetCamera()
        self.renWin.Render()

    def render_contour(self):
        """
        contour visualization of data
        """
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()

        self.contour.SetInputConnection(self.data.grid[self.currentTimeStep].GetOutputPort())

        scalarRange = activeScalar.GetRange()
        mean = 0.5*(scalarRange[0]+scalarRange[1])
        self.contour.SetValue(0, mean)

        # viz
        self.mapper3d.SetInputConnection(self.contour.GetOutputPort())
        self.ren.AddActor(self.mainActor)

        self.add_outline()

        self.update_contourrange()
        self.sliderRep.SetValue(mean)
        self.sliderWidget.EnabledOn()
        self.renWin.Render()

    def add_outline(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(self.data.grid[self.currentTimeStep].GetOutputPort())
        outlineMapper = vtk.vtkDataSetMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())
        self.outlineActor.SetMapper(outlineMapper)
        self.ren.AddActor(self.outlineActor)

    def set_line(self, linePoints):
        self.linePoints = linePoints

    def plot(self):
        """
        plot visualization of data
        """
        self.ren.RemoveAllViewProps()
        # self.markerWidget.EnabledOff()
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        line = vtk.vtkLineSource()
        line.SetResolution(30)
        line.SetPoint1(self.linePoints[0])
        line.SetPoint2(self.linePoints[1])
        probe = vtk.vtkProbeFilter()
        probe.SetInputConnection(line.GetOutputPort())
        probe.SetSourceConnection(self.data.grid[self.currentTimeStep].GetOutputPort())

        tuber = vtk.vtkTubeFilter()
        tuber.SetInputConnection(probe.GetOutputPort())
        tuber.SetRadius(0.02)
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInputConnection(tuber.GetOutputPort())
        lineActor = vtk.vtkActor()
        lineActor.SetMapper(lineMapper)
        # self.ren.AddActor(lineActor)

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
        xyplot.GetProperty().set_lineWidth(2)
        self.ren.AddActor2D(xyplot)
        # self.xyplotWidget = vtk.vtkXYPlotWidget()
        # self.xyplotWidget.SetXYPlotActor(xyplot)
        # self.xyplotWidget.SetInteractor(self.iren)
        # self.xyplotWidget.EnabledOn()

        self.renWin.Render()

    def update_contour(self, obj, ev):
        value = self.sliderWidget.GetRepresentation().GetValue()
        self.contour.SetValue(0, value)

    def pointdata_modified(self, obj, ev):
        """
        callback: activated on modifications to pointData in grid
        """
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        # if not self.mapper3d == None:
        #     self.mapper3d.SetScalarRange(activeScalar.GetRange())
        # scalarBarActor = vtk.vtkScalarBarActor()
        # scalarBarActor.SetTitle(activeScalar.GetName())
        # scalarBarActor.SetLookupTable(self.lut)
        # self.scalarBarWidget.SetScalarBarActor(scalarBarActor)

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
            self.scalarBarWidget.SetEnabled(1-self.scalarBarWidget.GetEnabled())
            self.renWin.Render()
        elif char == 'a':
            self.update_scalarbar()
            self.renWin.Render()
        elif char == ' ':
            self.play()
        elif char == 'k':
            self.next()
        elif char == 'j':
            self.prev()
        elif char == 'x':
            self.clear()
        elif char == 'p':
            self.screenshot('screenshot.png')

    def change_activescalar(self, name):
        for t in xrange(0, self.data.numTimes):
            self.data.grid[t].GetInput().GetPointData().SetActiveScalars(name)
        self.update_scalarbar()
        self.update_contourrange()
        self.renWin.Render()

    def update_scalarbar(self):
        # resetRange = kwargs.get('resetRange', False)
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        self.scalarBarActor.SetTitle(activeScalar.GetName())
        self.mapper3d.SetScalarRange(activeScalar.GetRange())

    def update_contourrange(self):
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        scalarRange = activeScalar.GetRange()
        self.sliderRep.SetMinimumValue(scalarRange[0])
        self.sliderRep.SetMaximumValue(scalarRange[1])

    def goto_timestep(self, step):
        self.currentTimeStep = step
        self.render()

    def next(self):
        if not self.currentTimeStep == self.data.numTimes-1:
            self.currentTimeStep += 1
            self.render()

    def prev(self):
        if not self.currentTimeStep == 0:
            self.currentTimeStep -= 1
            self.render()

    def first(self):
        self.currentTimeStep = 0
        self.render()

    def last(self):
        self.currentTimeStep = self.data.numTimes-1
        self.render()

    def play(self):
        for t in xrange(self.currentTimeStep+1, self.data.numTimes):
            time.sleep(0.5)
            self.currentTimeStep = t
            self.render()

    def load_data(self, config):
        self.data.config = config
        self.data.read()
        self.data.grid[self.currentTimeStep].GetInput().GetPointData().AddObserver(
            vtk.vtkCommand.ModifiedEvent, self.pointdata_modified)

    def screenshot(self, filename):
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(self.renWin)
        w2if.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetFileName(filename)
        writer.SetInput(w2if.GetOutput())
        writer.Write()

if __name__ == '__main__':
    import config
    import data

    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(config.config['vtkWidth'], config.config['vtkHeight'])
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    app = VtkGui(iren)
    app.load_data(config.config)

    iren.Initialize()
    renWin.Render()
    iren.Start()

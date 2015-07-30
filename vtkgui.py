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
        # interactor
        self.iren = iren

        # empty defaults
        self.data = data.Data()
        self.currentTimeStep = 0

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
        self.iren.AddObserver(vtk.vtkCommand.KeyPressEvent, self.onKeyPress)

        self.addWidgets()

    def addWidgets(self):
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
            self.updateContour);

    def clear(self):
        """
        surface visualization of data
        """
        self.ren.RemoveAllViewProps()
        self.renWin.Render()

    def render(self):
        """
        surface visualization of data
        """
        print 'rendering timestep', self.currentTimeStep
        self.ren.RemoveActor(self.outlineActor)
        self.sliderWidget.EnabledOff()
        self.markerWidget.EnabledOn()
        if self.data.numTimes > 0:
            self.mapper3d.SetInputConnection(self.data.grid[self.currentTimeStep].GetOutputPort())
        self.ren.AddActor(self.mainActor)
        self.ren.ResetCamera()
        self.renWin.Render()

    def renderContour(self):
        """
        contour visualization of data
        """
        self.ren.RemoveAllViewProps()
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()

        self.contour.SetInputConnection(self.data.grid[self.currentTimeStep].GetOutputPort())

        scalarRange = activeScalar.GetRange()
        mean = 0.5*(scalarRange[0]+scalarRange[1])
        self.contour.SetValue(0, mean)

        # viz
        self.mapper3d.SetInputConnection(self.contour.GetOutputPort())
        self.ren.AddActor(self.mainActor)

        self.addOutline()

        self.updateContourRange()
        self.sliderRep.SetValue(mean)
        self.sliderWidget.EnabledOn()
        self.renWin.Render()

    def addOutline(self):
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(self.data.grid[self.currentTimeStep].GetOutputPort())
        outlineMapper = vtk.vtkDataSetMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())
        self.outlineActor.SetMapper(outlineMapper)
        self.ren.AddActor(self.outlineActor)

    def plot(self, linePoints):
        """
        plot visualization of data
        """
        self.ren.RemoveAllViewProps()
        # self.markerWidget.EnabledOff()
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        line = vtk.vtkLineSource()
        line.SetResolution(30)
        line.SetPoint1(linePoints[0])
        line.SetPoint2(linePoints[1])
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

        self.renWin.Render()

    def updateContour(self, obj, ev):
        value = self.sliderWidget.GetRepresentation().GetValue()
        self.contour.SetValue(0, value)

    def pointDataModified(self, obj, ev):
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

    def onKeyPress(self, obj, ev):
        """
        callback: activated when a key is pressed
        """
        char = obj.GetKeyCode()
        # print 'pressed: ', char
        if char == '1':
            self.changeActiveScalar('c1')
        elif char == '2':
            self.changeActiveScalar('c2')
        elif char == '3':
            self.changeActiveScalar('c3')
        elif char == 'r':
            self.updateScalarBar()
            self.render()
        elif char == 'c':
            self.renderContour()
        elif char == 's':
            self.scalarBarWidget.SetEnabled(1-self.scalarBarWidget.GetEnabled())
            self.renWin.Render()
        elif char == 'a':
            self.updateScalarBar()
            self.renWin.Render()
        elif char == 'p':
            self.play()
        elif char == 'k':
            self.next()
        elif char == 'j':
            self.prev()
        elif char == 'x':
            self.clear()

    def changeActiveScalar(self, name):
        for t in xrange(0, self.data.numTimes):
            self.data.grid[t].GetInput().GetPointData().SetActiveScalars(name)
        self.updateScalarBar()
        self.updateContourRange()
        self.renWin.Render()

    def updateScalarBar(self):
        # resetRange = kwargs.get('resetRange', False)
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        self.scalarBarActor.SetTitle(activeScalar.GetName())
        self.mapper3d.SetScalarRange(activeScalar.GetRange())

    def updateContourRange(self):
        activeScalar = self.data.grid[self.currentTimeStep].GetInput().GetPointData().GetScalars()
        scalarRange = activeScalar.GetRange()
        self.sliderRep.SetMinimumValue(scalarRange[0])
        self.sliderRep.SetMaximumValue(scalarRange[1])

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

    def loadData(self, config):
        self.data.config = config
        self.data.read()
        self.data.grid[self.currentTimeStep].GetInput().GetPointData().AddObserver(
            vtk.vtkCommand.ModifiedEvent, self.pointDataModified)

if __name__ == '__main__':
    import config
    import data

    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(config.config['vtkWidth'], config.config['vtkHeight'])
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    app = VtkGui(iren)
    app.loadData(config.config)

    iren.Initialize()
    renWin.Render()
    iren.Start()

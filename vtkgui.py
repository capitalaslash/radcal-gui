#! /usr/bin/env python2

import vtk

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
        self.data = None
        self.mapper3d = None
        self.scalarWidget = None

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
        self.marker = vtk.vtkOrientationMarkerWidget()
        self.marker.SetInteractor(self.iren)
        self.marker.SetOrientationMarker(axes)
        self.marker.SetViewport(0.0, 0.0, 0.25, 0.25)
        self.marker.EnabledOn()

        # scalar bar
        self.scalarWidget = vtk.vtkScalarBarWidget()
        self.scalarWidget.SetInteractor(self.iren)

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
        self.ren.RemoveAllViewProps()
        self.marker.EnabledOn()
        activeScalar = self.data.grid.GetInput().GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        # viz
        self.mapper3d = vtk.vtkDataSetMapper()
        self.mapper3d.SetInputConnection(self.data.grid.GetOutputPort())
        # self.mapper3d.SetScalarModeToUseCellData()
        self.mapper3d.SetLookupTable(self.lut)
        self.mapper3d.SetScalarRange(activeScalar.GetRange())
        self.mapper3d.InterpolateScalarsBeforeMappingOn()
        self.mainActor = vtk.vtkLODActor()
        self.mainActor.SetMapper(self.mapper3d)

        self.ren.AddActor(self.mainActor)
        self.ren.ResetCamera()

        # set up scalar bar
        scalarBarActor = vtk.vtkScalarBarActor()
        scalarBarActor.SetTitle(activeScalar.GetName())
        scalarBarActor.SetLookupTable(self.lut)
        self.scalarWidget.SetScalarBarActor(scalarBarActor)
        if self.scalarWidget.GetEnabled():
            self.scalarWidget.EnabledOff()
            self.scalarWidget.EnabledOn()

        self.renWin.Render()

    def renderContour(self):
        """
        contour visualization of data
        """
        self.ren.RemoveAllViewProps()
        self.marker.EnabledOn()
        activeScalar = self.data.grid.GetInput().GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        # contour
        self.contour = vtk.vtkContourFilter()
        self.contour.SetInputConnection(self.data.grid.GetOutputPort())
        self.contour.SetNumberOfContours(1)

        scalarRange = activeScalar.GetRange()
        mean = 0.5*(scalarRange[0]+scalarRange[1])
        self.contour.SetValue(0, mean)

        # viz
        self.mapper3d = vtk.vtkDataSetMapper()
        self.mapper3d.SetInputConnection(self.contour.GetOutputPort())
        self.mapper3d.SetLookupTable(self.lut)
        self.mapper3d.SetScalarRange(activeScalar.GetRange())
        self.mainActor = vtk.vtkLODActor()
        self.mainActor.SetMapper(self.mapper3d)

        # outline
        outline = vtk.vtkOutlineFilter()
        outline.SetInputConnection(self.data.grid.GetOutputPort())
        outlineMapper = vtk.vtkDataSetMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())
        outlineActor = vtk.vtkActor()
        outlineActor.SetMapper(outlineMapper)

        self.ren.AddActor(self.mainActor)
        self.ren.AddActor(outlineActor)
        self.ren.ResetCamera()

        sliderRep = vtk.vtkSliderRepresentation2D()
        sliderRep.SetMinimumValue(scalarRange[0])
        sliderRep.SetMaximumValue(scalarRange[1])
        sliderRep.SetValue(mean)
        sliderRep.SetTitleText("contour")
        sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedViewport()
        sliderRep.GetPoint1Coordinate().SetValue(0.7, 0.1)
        sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedViewport()
        sliderRep.GetPoint2Coordinate().SetValue(1.0, 0.1)

        self.sliderWidget = vtk.vtkSliderWidget()
        self.sliderWidget.SetInteractor(self.iren)
        self.sliderWidget.SetRepresentation(sliderRep)
        self.sliderWidget.SetAnimationModeToAnimate()
        self.sliderWidget.EnabledOn()
        self.sliderWidget.AddObserver(vtk.vtkCommand.InteractionEvent,
            self.updateContour);

        # set up scalar bar
        scalarBarActor = vtk.vtkScalarBarActor()
        scalarBarActor.SetTitle(activeScalar.GetName())
        scalarBarActor.SetLookupTable(self.lut)
        self.scalarWidget.SetScalarBarActor(scalarBarActor)
        if self.scalarWidget.GetEnabled():
            self.scalarWidget.EnabledOff()
            self.scalarWidget.EnabledOn()

        self.renWin.Render()

    def plot(self, linePoints):
        """
        plot visualization of data
        """
        self.ren.RemoveAllViewProps()
        self.marker.EnabledOff()
        activeScalar = self.data.grid.GetInput().GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        line = vtk.vtkLineSource()
        line.SetResolution(30)
        line.SetPoint1(linePoints[0])
        line.SetPoint2(linePoints[1])
        probe = vtk.vtkProbeFilter()
        probe.SetInputConnection(line.GetOutputPort())
        probe.SetSourceConnection(self.data.grid.GetOutputPort())

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
        activeScalar = self.data.grid.GetInput().GetPointData().GetScalars()
        if not self.mapper3d == None:
            self.mapper3d.SetScalarRange(activeScalar.GetRange())
        scalarBarActor = vtk.vtkScalarBarActor()
        scalarBarActor.SetTitle(activeScalar.GetName())
        scalarBarActor.SetLookupTable(self.lut)
        self.scalarWidget.SetScalarBarActor(scalarBarActor)

    def onKeyPress(self, obj, ev):
        """
        callback: activated when a key is pressed
        """
        char = obj.GetKeyCode()
        # print 'pressed: ', char
        if char == '1':
            self.data.grid.GetInput().GetPointData().SetActiveScalars('c1')
        elif char == '2':
            self.data.grid.GetInput().GetPointData().SetActiveScalars('c2')
        elif char == '0':
            self.data.grid.GetInput().GetPointData().SetActiveScalars(None)
        elif char == 'r':
            self.render()
        elif char == 'c':
            self.renderContour()
        elif char == 'x':
            self.scalarWidget.SetEnabled(1-self.scalarWidget.GetEnabled())
        self.renWin.Render()

    def loadData(self, data):
        self.data = data
        self.data.grid.GetInput().GetPointData().AddObserver(
            vtk.vtkCommand.ModifiedEvent, self.pointDataModified)

if __name__ == '__main__':
    import config
    import data
    data = data.Data(**config.config)
    data.read()

    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(config.config['vtkWidth'], config.config['vtkHeight'])
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    app = VtkGui(iren)
    app.loadData(data)

    iren.Initialize()
    renWin.Render()
    iren.Start()

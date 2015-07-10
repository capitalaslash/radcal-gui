#! /usr/bin/env python2

from vtk import *

class Vtk3d(object):
    """
    Vtk3d gui
    """

    def __init__(self):
        """
        initialization of the interactor and fixed objects
        """
        # empty defaults
        self.data = None
        self.scalarWidget = None

        # camera
        self.camera = vtkCamera()
        self.camera.Elevation(-70)
        self.camera.SetViewUp(0, 0, 1)
        self.camera.Azimuth(30)
        self.camera.Dolly(0.8)

        # lookup table
        self.lut = vtkLookupTable()
        self.lut.SetHueRange(0.66667, 0.0)
        self.lut.Build()

        # render window
        self.renWin = vtkRenderWindow()
        self.renWin.SetSize(800, 800)
        self.renWin.SetNumberOfLayers(2)

        # main renderer
        self.ren = vtkRenderer()
        self.ren.SetLayer(0)
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.ren.SetActiveCamera(self.camera)
        self.renWin.AddRenderer(self.ren)

    def setInteractor(self, iren):
        """
        set interactor (independent of used toolkit)
        """
        self.iren = iren
        self.iren.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # keyboard bindings
        self.iren.AddObserver(vtkCommand.KeyPressEvent, self.onKeyPress)

        self.addWidgets()

    def addWidgets(self):
        # axes
        axes = vtkAxesActor()
        self.marker = vtkOrientationMarkerWidget()
        self.marker.SetInteractor(self.iren)
        self.marker.SetOrientationMarker(axes)
        self.marker.SetViewport(0.0, 0.0, 0.25, 0.25)
        self.marker.EnabledOn()

        # scalar bar
        self.scalarWidget = vtkScalarBarWidget()
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
        activeScalar = self.data.grid.GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        # viz
        self.mainMapper = vtkDataSetMapper()
        self.mainMapper.SetInputData(self.data.grid)
        # self.mainMapper.SetScalarModeToUseCellData()
        self.mainMapper.SetLookupTable(self.lut)
        self.mainMapper.SetScalarRange(activeScalar.GetRange())
        self.mainActor = vtkLODActor()
        self.mainActor.SetMapper(self.mainMapper)

        self.ren.AddActor(self.mainActor)
        self.ren.ResetCamera()

        # set up scalar bar
        scalarBarActor = vtkScalarBarActor()
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
        activeScalar = self.data.grid.GetPointData().GetScalars()
        # print 'active scalar is', activeScalar.GetName()

        # contour
        self.contour = vtkContourFilter()
        self.contour.SetInputData(self.data.grid)
        self.contour.SetNumberOfContours(1)

        scalarRange = activeScalar.GetRange()
        mean = 0.5*(scalarRange[0]+scalarRange[1])
        self.contour.SetValue(0, mean)

        # viz
        self.mainMapper = vtkDataSetMapper()
        self.mainMapper.SetInputConnection(self.contour.GetOutputPort())
        self.mainMapper.SetLookupTable(self.lut)
        self.mainMapper.SetScalarRange(activeScalar.GetRange())
        self.mainActor = vtkLODActor()
        self.mainActor.SetMapper(self.mainMapper)

        # outline
        outline = vtkOutlineFilter()
        outline.SetInputData(self.data.grid)
        outlineMapper = vtkDataSetMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())
        outlineActor = vtkActor()
        outlineActor.SetMapper(outlineMapper)

        self.ren.AddActor(self.mainActor)
        self.ren.AddActor(outlineActor)
        self.ren.ResetCamera()

        sliderRep = vtkSliderRepresentation2D()
        sliderRep.SetMinimumValue(scalarRange[0])
        sliderRep.SetMaximumValue(scalarRange[1])
        sliderRep.SetValue(mean)
        sliderRep.SetTitleText("contour")
        sliderRep.GetPoint1Coordinate().SetCoordinateSystemToNormalizedViewport()
        sliderRep.GetPoint1Coordinate().SetValue(0.7, 0.1)
        sliderRep.GetPoint2Coordinate().SetCoordinateSystemToNormalizedViewport()
        sliderRep.GetPoint2Coordinate().SetValue(1.0, 0.1)

        self.sliderWidget = vtkSliderWidget()
        self.sliderWidget.SetInteractor(self.iren)
        self.sliderWidget.SetRepresentation(sliderRep)
        self.sliderWidget.SetAnimationModeToAnimate()
        self.sliderWidget.EnabledOn()
        self.sliderWidget.AddObserver(vtkCommand.InteractionEvent, self.updateContour);

        # set up scalar bar
        scalarBarActor = vtkScalarBarActor()
        scalarBarActor.SetTitle(activeScalar.GetName())
        scalarBarActor.SetLookupTable(self.lut)
        self.scalarWidget.SetScalarBarActor(scalarBarActor)
        if self.scalarWidget.GetEnabled():
            self.scalarWidget.EnabledOff()
            self.scalarWidget.EnabledOn()

        self.renWin.Render()

    def updateContour(self, obj, ev):
        value = self.sliderWidget.GetRepresentation().GetValue()
        self.contour.SetValue(0, value)

    def pointDataModified(self, obj, ev):
        """
        callback: activated on modifications to pointData in grid
        """
        activeScalar = self.data.grid.GetPointData().GetScalars()
        self.mainMapper.SetScalarRange(activeScalar.GetRange())
        scalarBarActor = vtkScalarBarActor()
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
            self.data.grid.GetPointData().SetActiveScalars('c1')
        elif char == '2':
            self.data.grid.GetPointData().SetActiveScalars('c2')
        elif char == '0':
            self.data.grid.GetPointData().SetActiveScalars(None)
        elif char == 'r':
            self.render()
        elif char == 'x':
            self.scalarWidget.SetEnabled(1-self.scalarWidget.GetEnabled())
        self.renWin.Render()

    def loadData(self, data):
        self.data = data
        self.data.grid.GetPointData().AddObserver(vtkCommand.ModifiedEvent, self.pointDataModified)

if __name__ == '__main__':
    from config import *
    from data import *
    data = Data(config)

    app = Vtk3d()
    app.loadData(data)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(app.renWin)
    app.setInteractor(iren)
    app.iren.Initialize()
    app.renWin.Render()
    app.iren.Start()

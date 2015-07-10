#! /usr/bin/env python2

from vtk import *

class Vtk2d(object):
    """
    Vtk2d gui
    """

    def __init__(self):
        """
        initialization of the interactor and fixed objects
        """
        # empty defaults
        self.data = None

        # render window
        self.renWin = vtkRenderWindow()
        self.renWin.SetSize(800, 500)
        self.renWin.SetNumberOfLayers(2)

        # main renderer
        self.ren = vtkRenderer()
        self.ren.SetLayer(0)
        self.ren.SetBackground(0.1, 0.2, 0.4)
        self.renWin.AddRenderer(self.ren)

    def setInteractor(self, iren):
        """
        set interactor (independent of used toolkit)
        """
        self.iren = iren
        # self.iren.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        # keyboard bindings
        self.iren.AddObserver(vtkCommand.KeyPressEvent, self.onKeyPress)

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

        line = vtkLineSource()
        line.SetResolution(30)
        transLine = vtk.vtkTransform()
        transLine.Translate(2.5, 1.5, 0.5)
        transLine.Scale(3, 3, 3)
        transLine.RotateZ(90)
        tf = vtkTransformPolyDataFilter()
        tf.SetInputConnection(line.GetOutputPort())
        tf.SetTransform(transLine)
        probe = vtkProbeFilter()
        probe.SetInputConnection(tf.GetOutputPort())
        probe.SetSourceData(self.data.grid)

        tuber = vtkTubeFilter()
        tuber.SetInputConnection(probe.GetOutputPort())
        tuber.SetRadius(0.02)
        lineMapper = vtkPolyDataMapper()
        lineMapper.SetInputConnection(tuber.GetOutputPort())
        lineActor = vtk.vtkActor()
        lineActor.SetMapper(lineMapper)
        # self.ren.AddActor(lineActor)

        # outline
        outline = vtkOutlineFilter()
        outline.SetInputData(self.data.grid)
        outlineMapper = vtkDataSetMapper()
        outlineMapper.SetInputConnection(outline.GetOutputPort())
        outlineActor = vtkActor()
        outlineActor.SetMapper(outlineMapper)
        outlineActor.GetProperty().SetColor(0.0, 0.0, 0.0)
        # self.ren.AddActor(outlineActor)

        xyplot = vtkXYPlotActor()
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
        # self.xyplotWidget = vtkXYPlotWidget()
        # self.xyplotWidget.SetXYPlotActor(xyplot)
        # self.xyplotWidget.SetInteractor(self.iren)
        # self.xyplotWidget.EnabledOn()

        self.renWin.Render()

    def pointDataModified(self, obj, ev):
        """
        callback: activated on modifications to pointData in grid
        """
        activeScalar = self.data.grid.GetPointData().GetScalars()

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
        self.renWin.Render()

    def loadData(self, data):
        self.data = data
        self.data.grid.GetPointData().AddObserver(vtkCommand.ModifiedEvent, self.pointDataModified)

if __name__ == '__main__':
    from config import *
    from data import *
    data = Data(config)

    app = Vtk2d()
    app.loadData(data)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(app.renWin)
    app.setInteractor(iren)
    app.iren.Initialize()
    app.renWin.Render()
    app.iren.Start()

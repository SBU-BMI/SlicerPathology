import os
import json
import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil
from EditorLib import LabelEffect

# Added libs
from EditorLib import Effect
from EditorLib import LabelEffectLogic

from copy import copy, deepcopy
import numpy as np

__all__ = [
    'QuickTCGAEffectOptions',
    'QuickTCGAEffectTool',
    'QuickTCGAEffectLogic',
    'QuickTCGAEffect'
]


#
# QuickTCGAEffectOptions - see LabelEffect, EditOptions and Effect for superclasses
#

class QuickTCGAEffectOptions(LabelEffect.LabelEffectOptions):
    """ QuickTCGAEffect-specific gui
    """

    def __init__(self, parent=0):
        super(QuickTCGAEffectOptions, self).__init__(parent)
        editUtil = EditorLib.EditUtil.EditUtil()
        self.parameterNode = editUtil.getParameterNode()
        lm = slicer.app.layoutManager()
        self.redSliceWidget = lm.sliceWidget('Red')
        self.yellowSliceWidget = lm.sliceWidget('Yellow')
        self.greenSliceWidget = lm.sliceWidget('Green')
        self.attributes = 'MouseTool'
        self.displayName = 'QuickTCGAEffect'
        self.omode = 0
        slicer.modules.QuickTCGAEffectOptions = self

    def __del__(self):
        super(QuickTCGAEffectOptions, self).__del__()

    def create(self):
        self.params = {}
        self.cparams = {"algorithm": "Yi"}
        status = EditUtil.EditUtil().getParameterNode().GetParameter('QuickTCGAEffect,erich')
        if status == "reset":
            params = {}
        super(QuickTCGAEffectOptions, self).create()
        # self.helpLabel = qt.QLabel("Press Y to run automatic segmentation on the current image using given parameters.",
        #                            self.frame)
        # self.frame.layout().addWidget(self.helpLabel)

        # self.clearButton = qt.QPushButton(self.frame)
        # self.clearButton.text = "Clear Selection"
        # self.frame.layout().addWidget(self.clearButton)
        # self.clearButton.connect('clicked()', self.clearSelection)

        self.setupSegmentationOptions(1)

        self.outlineButton = qt.QPushButton(self.frame)
        self.outlineButton.text = "Toggle Outline"
        self.frame.layout().addWidget(self.outlineButton)
        self.outlineButton.connect('clicked()', self.toggleOutline)

        self.wipeButton = qt.QPushButton(self.frame)
        self.wipeButton.text = "Clear current segmentation label"
        self.frame.layout().addWidget(self.wipeButton)
        self.wipeButton.connect('clicked()', self.wipeSegmentation())

        self.locRadFrame = qt.QFrame(self.frame)
        self.locRadFrame.setLayout(qt.QHBoxLayout())
        self.frame.layout().addWidget(self.locRadFrame)
        self.widgets.append(self.locRadFrame)

        # Nucleus segmentation parameters
        nucleusSegCollapsibleButton = ctk.ctkCollapsibleButton()
        nucleusSegCollapsibleButton.text = "Nucleus Segmentation Parameters"
        nucleusSegCollapsibleButton.collapsed = False
        self.frame.layout().addWidget(nucleusSegCollapsibleButton)

        # Nucleus declumping parameters
        nucleusDeclumpingCollapsibleButton = ctk.ctkCollapsibleButton()
        nucleusDeclumpingCollapsibleButton.text = "Nucleus Declumping Parameters"
        nucleusDeclumpingCollapsibleButton.collapsed = False
        self.frame.layout().addWidget(nucleusDeclumpingCollapsibleButton)

        self.structuresView = \
            slicer.util.findChildren(slicer.modules.SlicerPathologyWidget.editorWidget.volumes, 'StructuresView')[0]
        self.structuresView.connect("activated(QModelIndex)", self.onStructureClickedOrAdded)

        # Layout within the seg parameter button
        nucleusSegFormLayout = qt.QFormLayout(nucleusSegCollapsibleButton)

        # Layout within the declumping parameter button
        nucleusDeclumpingFormLayout = qt.QFormLayout(nucleusDeclumpingCollapsibleButton)

        sr = vtk.vtkSliderRepresentation2D()
        sr.SetHandleSize(10)

        self.frameOtsuSlider = ctk.ctkSliderWidget()
        self.frameOtsuSlider.connect('valueChanged(double)', self.OtsuSliderValueChanged)
        self.frameOtsuSlider.decimals = 1
        self.frameOtsuSlider.minimum = 0.5
        self.frameOtsuSlider.maximum = 1.5
        self.frameOtsuSlider.value = 1.0
        self.frameOtsuSlider.singleStep = 0.01
        self.frameOtsuSlider.setToolTip(
            "Threshold gain for calling something in the image as nucleus. Run as default value 1.0. Then, if undersegment, increase this to 1.2 and re-run. If oversegment, decrease to 0.8 and re-run. Smaller value of this parameter will give fewer regions segmented as nucleus.")
        nucleusSegFormLayout.addRow("Threshold Grain:", self.frameOtsuSlider)

        self.frameCurvatureWeightSlider = ctk.ctkSliderWidget()
        self.frameCurvatureWeightSlider.connect('valueChanged(double)', self.CurvatureWeightSliderValueChanged)
        self.frameCurvatureWeightSlider.decimals = 1
        self.frameCurvatureWeightSlider.minimum = 0
        self.frameCurvatureWeightSlider.maximum = 10
        self.frameCurvatureWeightSlider.value = 8
        self.frameCurvatureWeightSlider.singleStep = 0.01
        self.frameCurvatureWeightSlider.setToolTip(
            "Large value will result in smoother boundary in the resulting segmentation.")
        nucleusSegFormLayout.addRow("Expected Roundness/Smoothness:", self.frameCurvatureWeightSlider)

        self.frameSizeThldSlider = ctk.ctkSliderWidget()
        self.frameSizeThldSlider.connect('valueChanged(double)', self.SizeThldSliderValueChanged)
        self.frameSizeThldSlider.decimals = 1
        self.frameSizeThldSlider.minimum = 1
        self.frameSizeThldSlider.maximum = 30
        self.frameSizeThldSlider.value = 3
        self.frameSizeThldSlider.singleStep = 0.01
        self.frameSizeThldSlider.setToolTip("Any object smaller than this value will be discarded.")
        nucleusSegFormLayout.addRow("Size Lower Threshold:", self.frameSizeThldSlider)

        self.frameSizeUpperThldSlider = ctk.ctkSliderWidget()
        self.frameSizeUpperThldSlider.connect('valueChanged(double)', self.SizeUpperThldSliderValueChanged)
        self.frameSizeUpperThldSlider.decimals = 0
        self.frameSizeUpperThldSlider.minimum = 1
        self.frameSizeUpperThldSlider.maximum = 500
        self.frameSizeUpperThldSlider.value = 50
        self.frameSizeUpperThldSlider.setToolTip("Any object larger than this value will be de-clumped.")
        nucleusDeclumpingFormLayout.addRow("Size Upper Threshold:", self.frameSizeUpperThldSlider)

        self.frameKernelSizeSlider = ctk.ctkSliderWidget()
        self.frameKernelSizeSlider.connect('valueChanged(double)', self.KernelSizeSliderValueChanged)
        self.frameKernelSizeSlider.decimals = 0
        self.frameKernelSizeSlider.minimum = 1
        self.frameKernelSizeSlider.maximum = 30
        self.frameKernelSizeSlider.value = 20
        self.frameKernelSizeSlider.setToolTip("Lower this value will result in smaller object in the declumping.")
        nucleusDeclumpingFormLayout.addRow("Kernel Size:", self.frameKernelSizeSlider)

        self.frameMPPSlider = ctk.ctkSliderWidget()
        self.frameMPPSlider.connect('valueChanged(double)', self.MPPSliderValueChanged)
        self.frameMPPSlider.decimals = 5
        self.frameMPPSlider.minimum = 0.01
        self.frameMPPSlider.maximum = 1
        self.frameMPPSlider.value = 0.25
        self.frameMPPSlider.singleStep = 0.01
        self.frameMPPSlider.setToolTip("For 40x, this is around 0.25. For 20x, this is around 0.5.")
        nucleusDeclumpingFormLayout.addRow("Microns Per Pixel:", self.frameMPPSlider)

        self.DefaultsButton = qt.QPushButton(self.frame)
        self.DefaultsButton.text = "Default Parameter Values"
        self.frame.layout().addWidget(self.DefaultsButton)
        self.DefaultsButton.connect('clicked()', self.ResetToDefaults)
        # nucleusSegFormLayout.addWidget(self.DefaultsButton)

        HelpButton(self.frame, (
            "Otsu threshold:\n Threshold gain for calling something in the image as nucleus. Run as default value 1.0. Then, if undersegment, increase this to 1.2 and re-run. If oversegment, decrease to 0.8 and re-run. Smaller value of this parameter will give fewer regions segmented as nucleus.\n" +
            "\nCurvature Weight:\n Large value will result in smoother boundary in the resulting segmentation.\n" +
            "\nSize Threshold:\n Any object smaller than this value will be discarded.\n" +
            "\nSize Upper Threshold:\n Any object larger than this value will be de-clumped.\n" +
            "\nKernel size:\n Lower this value will result in smaller object in the declumping.\n" +
            "\nMicrons Per Pixel:\n For 40x, this is around 0.25. For 20x, this is around 0.5.\n"))
        self.frame.layout().addStretch(1)  # Add vertical spacer
        self.omode = 0
        self.toggleOutline()

    # 
    # SEGMENTATION SELECTION
    # 
    def setupSegmentationOptions(self, opt):
        if opt == 1:
            # Button: No Declumping
            self.segnoButton = qt.QPushButton(self.frame)
            self.segnoButton.text = run_lbl + " " + segno_lbl
            self.frame.layout().addWidget(self.segnoButton)
            self.segnoButton.connect('clicked()', self.RunSegmenterWO)

            # Button: Mean Shift Declumping
            self.segButton = qt.QPushButton(self.frame)
            self.segButton.text = run_lbl + " " + seg_lbl
            self.frame.layout().addWidget(self.segButton)
            self.segButton.connect('clicked()', self.RunSegmenter)

            # Button: Watershed Declumping
            self.segWtrShd_btn = qt.QPushButton(self.frame)
            self.segWtrShd_btn.text = run_lbl + " " + segWtr_lbl
            self.frame.layout().addWidget(self.segWtrShd_btn)
            self.segWtrShd_btn.connect('clicked()', self.RunSegmenter_WtrShd)
        else:
            # COMBO BOX
            self.methodSelectorComboBox = qt.QComboBox()
            self.methodSelectorComboBox.addItem("No Declumping (fast)", LOGICAL_FAST)
            self.methodSelectorComboBox.addItem("Mean Shift Declumping (slow)", LOGICAL_MSHIFT)
            self.methodSelectorComboBox.addItem("Watershed Declumping (slow)", LOGICAL_WTRSHED)
            self.methodSelectorComboBox.setToolTip('<html>Run Segmentation. Available operations:<ul style="margin: 0">'
                                                   '<li><b>No Declumping:</b> Run segmentation with no declumping. '
                                                   'Runs much faster than when declumping is applied.</li>'
                                                   '<li><b>Mean Shift Declumping:</b> Run segmentation using mean shift '
                                                   'algorithm for declumping. Run time can be from 2 to 2.5 minutes.</li>'
                                                   '<li><b>Watershed Declumping:</b> Run segmentation using watershed '
                                                   'algorithm for declumping.</li>')
            self.frame.layout().addWidget(self.methodSelectorComboBox)
            self.methodSelectorComboBox.connect("currentIndexChanged(int)", self.RunSegmenterTest)

    def ResetToDefaults(self):
        self.frameOtsuSlider.value = 1.0
        self.frameCurvatureWeightSlider.value = 8
        self.frameSizeThldSlider.value = 3
        self.frameSizeUpperThldSlider.value = 50
        self.frameKernelSizeSlider.value = 20
        self.frameMPPSlider.value = 0.25
        self.parameterNode.SetParameter("QuickTCGAEffect,otsuRatio", str(self.frameOtsuSlider.value))
        self.updateParam("otsuRatio", self.frameOtsuSlider.value)
        self.parameterNode.SetParameter("QuickTCGAEffect,curvatureWeight", str(self.frameCurvatureWeightSlider.value))
        self.updateParam("curvatureWeight", self.frameCurvatureWeightSlider.value)
        self.parameterNode.SetParameter("QuickTCGAEffect,sizeThld", str(self.frameSizeThldSlider.value))
        self.updateParam("sizeThld", self.frameSizeThldSlider.value)
        self.parameterNode.SetParameter("QuickTCGAEffect,sizeUpperThld", str(self.frameSizeUpperThldSlider.value))
        self.updateParam("sizeUpperThld", self.frameSizeUpperThldSlider.value)
        self.parameterNode.SetParameter("QuickTCGAEffect,mpp", str(self.frameMPPSlider.value))
        self.updateParam("mpp", self.frameMPPSlider.value)
        self.parameterNode.SetParameter("QuickTCGAEffect,kernelSize", str(self.frameKernelSizeSlider.value))
        self.updateParam("kernelSize", self.frameKernelSizeSlider.value)
        self.updateMRMLFromGUI()

    def wipeSegmentation(self):
        sl = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
        logic = QuickTCGAEffectLogic(sl)
        logic.wipeSegmentation()

    def destroy(self):
        self.currentMessage = ""
        slicer.util.showStatusMessage(self.currentMessage)
        super(QuickTCGAEffectOptions, self).destroy()

    # Run segmentation without declumping
    def RunSegmenterWO(self):
        self.disable_buttons()
        self.segnoButton.text = "*** " + running_lbl + " " + segno_lbl + " ***"
        self.segnoButton.update()
        slicer.modules.QuickTCGAEffectLogic.runQTCGA_NucleiSegYi(0)
        self.enable_buttons()
        self.segnoButton.text = run_lbl + " " + segno_lbl

    # Run segmentation with mean shift
    def RunSegmenter(self):
        self.disable_buttons()
        self.segButton.text = "*** " + running_lbl + " " + seg_lbl + " ***"
        self.segButton.update()
        slicer.modules.QuickTCGAEffectLogic.runQTCGA_NucleiSegYi(1)
        self.enable_buttons()
        self.segButton.text = run_lbl + " " + seg_lbl

    # Run segmentation with watershed
    def RunSegmenter_WtrShd(self):
        self.disable_buttons()
        self.segWtrShd_btn.text = "*** " + running_lbl + " " + segWtr_lbl + " ***"
        self.segWtrShd_btn.update()
        slicer.modules.QuickTCGAEffectLogic.runQTCGA_NucleiSegYi(2)
        self.enable_buttons()
        self.segWtrShd_btn.text = run_lbl + " " + segWtr_lbl

    def disable_buttons(self):
        self.segnoButton.setEnabled(0)
        self.segButton.setEnabled(0)
        self.segWtrShd_btn.setEnabled(0)

    def enable_buttons(self):
        self.segnoButton.setEnabled(1)
        self.segButton.setEnabled(1)
        self.segWtrShd_btn.setEnabled(1)

    # TEST COMBO BOX
    def RunSegmenterTest(self, i):
        operationIndex = self.methodSelectorComboBox.currentIndex
        operation = self.methodSelectorComboBox.itemData(operationIndex)
        print "operation", operation
        print "operationIndex", operationIndex
        print "self.methodSelectorComboBox.count", self.methodSelectorComboBox.count
        print "Current index", operationIndex, "selection changed ", self.methodSelectorComboBox.currentText
        for count in range(self.methodSelectorComboBox.count):
            print self.methodSelectorComboBox.itemText(count)
        print "Current index", i, "selection changed ", self.methodSelectorComboBox.currentText

    def toggleOutline(self):
        if self.omode == 1:
            self.omode = 0
        else:
            self.omode = 1
        self.editUtil.setLabelOutline(self.omode)

    def clearSelection(self):
        EditUtil.EditUtil().getParameterNode().UnsetParameter("QuickTCGAEffect,currentXYPosition")
        EditUtil.EditUtil().getParameterNode().UnsetParameter("QuickTCGAEffect,startXYPosition")

    def updateSliders(self):
        print "updateSliders : ", slicer.modules.QuickTCGAEffectOptions.params
        r = self.structuresView.currentIndex().row()
        if r > -1:
            ei = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r, 3).text()
        else:
            ei = EditUtil.EditUtil().getParameterNode().GetParameter('SlicerPathology,tilename') + '-label'
        if ei not in params:
            params[ei] = cparams.copy()
            if r < 0:
                params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.editUtil.getLabelName()
            else:
                params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r,
                                                                                                               2).text()
            jstr = json.dumps(params, sort_keys=True, indent=4, separators=(',', ': '))  # TODO: outdent?
            self.parameterNode.SetParameter("QuickTCGAEffect,erich", jstr)  # TODO: outdent?
        self.frameOtsuSlider.value = params[ei]["otsuRatio"]
        self.frameCurvatureWeightSlider.value = params[ei]["curvatureWeight"]
        self.frameSizeThldSlider.value = params[ei]["sizeThld"]
        self.frameSizeUpperThldSlider.value = params[ei]["sizeUpperThld"]
        self.frameMPPSlider.value = params[ei]["mpp"]
        self.frameKernelSizeSlider.value = params[ei]["KernelSize"]

    def onStructureClickedOrAdded(self):
        self.updateSliders()

    def updateParam(self, p, v):
        r = self.structuresView.currentIndex().row()
        if r > -1:
            ei = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r, 3).text()
        else:
            ei = EditUtil.EditUtil().getParameterNode().GetParameter('SlicerPathology,tilename') + '-label'
        if ei not in self.params:
            self.params[ei] = self.cparams.copy()
            if r < 0:
                self.params[ei][
                    'label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.editUtil.getLabelName()
            else:
                self.params[ei]['label'] = slicer.modules.SlicerPathologyWidget.editorWidget.helper.structures.item(r,
                                                                                                                    2).text()
        self.params[ei][p] = v
        self.cparams[p] = v
        jstr = json.dumps(self.params, sort_keys=True, indent=4, separators=(',', ': '))
        self.parameterNode.SetParameter("QuickTCGAEffect,erich", jstr)

    def OtsuSliderValueChanged(self, value):
        self.parameterNode.SetParameter("QuickTCGAEffect,otsuRatio", str(value))
        self.updateParam("otsuRatio", value)
        self.updateMRMLFromGUI()

    def CurvatureWeightSliderValueChanged(self, value):
        self.parameterNode.SetParameter("QuickTCGAEffect,curvatureWeight", str(value))
        self.updateParam("curvatureWeight", value)
        self.updateMRMLFromGUI()

    def SizeThldSliderValueChanged(self, value):
        self.parameterNode.SetParameter("QuickTCGAEffect,sizeThld", str(value))
        self.updateParam("sizeThld", value)
        self.updateMRMLFromGUI()

    def SizeUpperThldSliderValueChanged(self, value):
        self.parameterNode.SetParameter("QuickTCGAEffect,sizeUpperThld", str(value))
        self.updateParam("sizeUpperThld", value)
        self.updateMRMLFromGUI()

    def MPPSliderValueChanged(self, value):
        self.parameterNode.SetParameter("QuickTCGAEffect,mpp", str(value))
        self.updateParam("mpp", value)
        self.updateMRMLFromGUI()

    def KernelSizeSliderValueChanged(self, value):
        self.parameterNode.SetParameter("QuickTCGAEffect,kernelSize", str(value))
        self.updateParam("kernelSize", value)
        self.updateMRMLFromGUI()

    # note: this method needs to be implemented exactly as-is
    # in each leaf subclass so that "self" in the observer
    # is of the correct type

    def updateParameterNode(self, caller, event):
        node = EditUtil.EditUtil().getParameterNode()
        if node != self.parameterNode:
            if self.parameterNode:
                node.RemoveObserver(self.parameterNodeTag)
            self.parameterNode = node
            self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

    def setMRMLDefaults(self):
        super(QuickTCGAEffectOptions, self).setMRMLDefaults()

    def updateGUIFromMRML(self, caller, event):
        self.disconnectWidgets()
        super(QuickTCGAEffectOptions, self).updateGUIFromMRML(caller, event)
        self.connectWidgets()

    def updateMRMLFromGUI(self):
        if self.updatingGUI:
            return
        disableState = self.parameterNode.GetDisableModifiedEvent()
        self.parameterNode.SetDisableModifiedEvent(1)
        super(QuickTCGAEffectOptions, self).updateMRMLFromGUI()
        self.parameterNode.SetDisableModifiedEvent(disableState)
        if not disableState:
            self.parameterNode.InvokePendingModifiedEvent()


#
# QuickTCGAEffectTool
#

class QuickTCGAEffectTool(LabelEffect.LabelEffectTool):
    """
    One instance of this will be created per-view when the effect
    is selected.  It is responsible for implementing feedback and
    label map changes in response to user input.
    This class observes the editor parameter node to configure itself
    and queries the current view for background and label volume
    nodes to operate on.
    """

    def __init__(self, sliceWidget):
        super(QuickTCGAEffectTool, self).__init__(sliceWidget)
        # create a logic instance to do the non-gui work
        self.logic = QuickTCGAEffectLogic(self.sliceWidget.sliceLogic())

        self.sliceWidget = sliceWidget
        self.sliceLogic = sliceWidget.sliceLogic()
        self.sliceView = self.sliceWidget.sliceView()
        self.interactor = self.sliceView.interactorStyle().GetInteractor()
        self.renderWindow = self.sliceWidget.sliceView().renderWindow()

        self.actionState = None
        self.startXYPosition = None
        self.currentXYPosition = None

        self.createGlyph()

        self.mapper = vtk.vtkPolyDataMapper2D()
        self.actor = vtk.vtkActor2D()
        self.mapper.SetInputData(self.polyData)
        self.actor.SetMapper(self.mapper)
        property_ = self.actor.GetProperty()
        property_.SetColor(1, 1, 0)
        # property_.SetLineWidth(1)
        self.renderer.AddActor2D(self.actor)
        self.actors.append(self.actor)
        slicer.modules.QuickTCGAEffectTool = self

    def cleanup(self):
        super(QuickTCGAEffectTool, self).cleanup()

    def createGlyph(self):
        self.polyData = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()
        self.polyData.SetPoints(points)
        self.polyData.SetLines(lines)
        prevPoint = None
        firstPoint = None
        for x, y in ((0, 0),) * 4:
            p = points.InsertNextPoint(x, y, 0)
            if prevPoint is not None:
                idList = vtk.vtkIdList()
                idList.InsertNextId(prevPoint)
                idList.InsertNextId(p)
                self.polyData.InsertNextCell(vtk.VTK_LINE, idList)
            prevPoint = p
            if firstPoint is None:
                firstPoint = p
        # make the last line in the polyData
        idList = vtk.vtkIdList()
        idList.InsertNextId(p)
        idList.InsertNextId(firstPoint)
        self.polyData.InsertNextCell(vtk.VTK_LINE, idList)
        self.updateGlyph()

    def updateGlyph(self):
        if not self.startXYPosition or not self.currentXYPosition:
            return
        points = self.polyData.GetPoints()
        xlo, ylo = self.startXYPosition
        xhi, yhi = self.currentXYPosition
        points.SetPoint(0, xlo, ylo, 0)
        points.SetPoint(1, xlo, yhi, 0)
        points.SetPoint(2, xhi, yhi, 0)
        points.SetPoint(3, xhi, ylo, 0)

    def processEvent(self, caller=None, event=None):
        if event == "LeftButtonPressEvent":
            self.actionState = "dragging"
            self.cursorOff()
            self.actor.VisibilityOn()
            xy = self.interactor.GetEventPosition()
            self.startXYPosition = xy
            self.currentXYPosition = xy
            EditUtil.EditUtil().getParameterNode().SetParameter("QuickTCGAEffect,startXYPosition", str(xy))
            EditUtil.EditUtil().getParameterNode().SetParameter("QuickTCGAEffect,currentXYPosition", str(xy))
            self.updateGlyph()
            self.abortEvent(event)
        elif event == "LeftButtonReleaseEvent":
            self.actionState = ""
            self.cursorOn()
            self.abortEvent(event)
        elif event == "MouseMoveEvent":
            if self.actionState == "dragging":
                self.currentXYPosition = self.interactor.GetEventPosition()
                a = abs(self.currentXYPosition[0] - self.startXYPosition[0])
                b = abs(self.currentXYPosition[1] - self.startXYPosition[1])
                c = self.startXYPosition[0]
                d = self.startXYPosition[1]
                if a < b:
                    self.currentXYPosition = (c + a, d - a)
                else:
                    self.currentXYPosition = (c + b, d - b)
                EditUtil.EditUtil().getParameterNode().SetParameter("QuickTCGAEffect,currentXYPosition",
                                                                    str(self.currentXYPosition))
                self.updateGlyph()
                self.sliceView.scheduleRender()
                self.abortEvent(event)
        # elif event == "RightButtonPressEvent":
        #  print "RightButtonPressEvent"
        #  prop = self.actor.GetProperty()
        #  prop.SetColor(0,0,1)
        #  #self.actor.VisibilityOff()
        #  self.sliceView.scheduleRender()
        #  self.abortEvent(event)
        # elif event == "RightButtonReleaseEvent":
        #  x = 5
        elif event == "KeyPressEvent":
            slicer.modules.QuickTCGAEffectOptions.clearSelection()
            self.actor.VisibilityOff()
            self.sliceView.scheduleRender()
            self.abortEvent(event)

    def apply(self):
        lines = self.polyData.GetLines()
        if lines.GetNumberOfCells() == 0:
            return
        self.logic.undoRedo = self.undoRedo
        self.logic.applyPolyMask(self.polyData)


#
# QuickTCGAEffectLogic
#

class QuickTCGAEffectLogic(LabelEffect.LabelEffectLogic):
    """
    This class contains helper methods for a given effect
    type.  It can be instanced as needed by an QuickTCGAEffectTool
    or QuickTCGAEffectOptions instance in order to compute intermediate
    results (say, for user feedback) or to implement the final
    segmentation editing operation.  This class is split
    from the QuickTCGAEffectTool so that the operations can be used
    by other code without the need for a view context.
    """

    def __init__(self, sliceLogic):
        self.sliceLogic = sliceLogic
        self.attributes = 'MouseTool'
        self.displayName = 'QuickTCGAEffect'
        slicer.modules.SlicerPathologyWidget.editorWidget.removeShortcutKeys()
        self.editUtil = EditUtil.EditUtil()
        self.swRed = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
        self.sw = slicer.app.layoutManager().sliceWidget('Red')
        self.interactor = self.sw.sliceView().interactor()  # initialize to red slice interactor
        self.init_QuickTCGA()
        self.QuickTCGACreated = False
        slicer.modules.QuickTCGAEffectLogic = self

    def apply(self, xy):
        pass

    def init_QuickTCGA(self):
        self.emergencyStopFunc = None
        self.dialogBox = qt.QMessageBox()  # will display messages to draw users attention if he does anything wrong
        self.dialogBox.setWindowTitle("QuickTCGA Error")
        self.dialogBox.setWindowModality(qt.Qt.NonModal)  # will allow user to continue interacting with Slicer

        self.labelNode = self.editUtil.getLabelVolume()  # labelLogic.GetVolumeNode()
        self.backgroundNode = self.editUtil.getBackgroundVolume()  # backgroundLogic.GetVolumeNode()
        self.foregroundNode = self.swRed.GetForegroundLayer().GetVolumeNode()

        # perform safety check on right images/labels being selected, #set up images
        # if red slice doesnt have a label or image, go no further
        # if type(self.backgroundNode)==type(None) or type(self.labelNode)==type(None):
        #  self.dialogBox.setText("Either Image (must be Background Image) or Label not set in slice views.")
        #  self.dialogBox.show()

        if self.emergencyStopFunc:
            self.emergencyStopFunc()
            return

        volumesLogic = slicer.modules.volumes.logic()

        self.labelName = self.labelNode.GetName()  # record name of label so user, cant trick us
        self.imgBgrdName = self.backgroundNode.GetName()
        self.imgFgrdName = self.foregroundNode.GetName()

        if self.sliceViewMatchEditor(
                self.sliceLogic) == False:  # do nothing, exit function if user has played with images
            if self.emergencyStopFunc:
                self.emergencyStopFunc()
                return

        # QuickTCGAEffect shortcuts
        # runNucleiSegKey = qt.QKeySequence(qt.Qt.Key_Y)
        # clearSelectionKey = qt.QKeySequence(qt.Qt.Key_Escape)
        # self.qtkeyconnections = []

        # self.qtkeydefsQTCGA = [[runNucleiSegKey, self.runQTCGA_NucleiSegYi],
        #                        [clearSelectionKey, self.runQTCGA_clearSelection]]

        # for keydef in self.qtkeydefsQTCGA:
        #     self.runyi = qt.QShortcut(slicer.util.mainWindow())
        #     self.runyi.setKey(qt.QKeySequence(qt.Qt.Key_Y))
        #     self.runyi.activated.connect(self.runQTCGA_NucleiSegYi)
        #     s.connect('activated()', self.runQTCGA_NucleiSegYi)
        #     s = qt.QShortcut(keydef[0], slicer.util.mainWindow())
        #     s.connect('activated()', keydef[1])
        #     self.qtkeyconnections.append(s)

        self.qTCGALabMod_tag = self.sliceLogic.AddObserver("ModifiedEvent",
                                                           self.QTCGAChangeLabelInput)  # put test listener on the whole window

        # Quick TCGA parameters
        self.bEditTCGA = True
        self.bEditShortCut = False
        self.currentMessage = ""

        seedArray = slicer.util.array(self.labelName)
        self.qTCGASeedArray = seedArray.copy()
        self.qTCGASegArray = seedArray.copy()
        self.qTCGASeedArray[:] = 0
        self.qTCGASegArray[:] = 0

        self.SCutROIRad = 50
        self.volSize = self.labelNode.GetImageData().GetDimensions()
        self.qSCutROIArray = seedArray.copy()  # np.zeros([self.volSize[0],self.volSize[1],1])
        self.qSCutROIArray[:] = 0

        roiVTK = vtk.vtkImageData()
        roiVTK.DeepCopy(self.labelNode.GetImageData())
        self.roiVTK = roiVTK

        import vtkSlicerQuickTCGAModuleLogicPython

        node = EditUtil.EditUtil().getParameterNode()  # get the parameters from MRML
        if node.GetParameter("QuickTCGAEffect,otsuRatio") != "":
            otsuRatio = float(node.GetParameter("QuickTCGAEffect,otsuRatio"))
            curvatureWeight = float(node.GetParameter("QuickTCGAEffect,curvatureWeight"))
            sizeThld = float(node.GetParameter("QuickTCGAEffect,sizeThld"))
            sizeUpperThld = float(node.GetParameter("QuickTCGAEffect,sizeUpperThld"))
            mpp = float(node.GetParameter("QuickTCGAEffect,mpp"))
            kernelSize = float(node.GetParameter("QuickTCGAEffect,kernelSize"))
            opt = slicer.modules.QuickTCGAEffectOptions
            opt.cparams["otsuRatio"] = otsuRatio
            opt.cparams["curvatureWeight"] = curvatureWeight
            opt.cparams["sizeThld"] = sizeThld
            opt.cparams["sizeUpperThld"] = sizeUpperThld
            opt.cparams["mpp"] = mpp
            opt.cparams["kernelSize"] = kernelSize
            qTCGAMod = vtkSlicerQuickTCGAModuleLogicPython.vtkQuickTCGA()
            qTCGAMod.SetSourceVol(self.foregroundNode.GetImageData())
            qTCGAMod.SetotsuRatio(otsuRatio)
            qTCGAMod.SetcurvatureWeight(curvatureWeight)
            qTCGAMod.SetsizeThld(sizeThld)
            qTCGAMod.SetsizeUpperThld(sizeUpperThld)
            qTCGAMod.Setmpp(mpp)
            qTCGAMod.SetkernelSize(kernelSize)
            qTCGAMod.Initialization()
            # print("qTCGAMod:", qTCGAMod)
            self.qTCGAMod = qTCGAMod
            self.QuickTCGACreated = True  # tracks if completed the initialization (so can do stop correctly) of KSlice

    def runQTCGA_clearSelection(self):
        print "wipe them out.  all of them."

        # run Quick TCGA segmenter for the current master volume and label volume

    def runQTCGA_NucleiSegYi(self, seg_type):
        self.currentMessage = "Quick TCGA: running nucleus segmentation ..."
        slicer.util.showStatusMessage(self.currentMessage)
        seedArray = slicer.util.array(self.labelNode.GetName())
        self.qTCGASeedArray[:] = seedArray[:]
        node = EditUtil.EditUtil().getParameterNode()  # get the parameters from MRML
        otsuRatio = float(node.GetParameter("QuickTCGAEffect,otsuRatio"))
        curvatureWeight = float(node.GetParameter("QuickTCGAEffect,curvatureWeight")) / 10
        sizeThld = float(node.GetParameter("QuickTCGAEffect,sizeThld"))
        sizeUpperThld = float(node.GetParameter("QuickTCGAEffect,sizeUpperThld"))
        mpp = float(node.GetParameter("QuickTCGAEffect,mpp"))
        kernelSize = float(node.GetParameter("QuickTCGAEffect,kernelSize"))
        print otsuRatio, " ", curvatureWeight, " ", sizeThld, " ", sizeUpperThld, " ", mpp, " ", kernelSize

        # print("self.qTCGAMod: ", self.qTCGAMod)
        self.qTCGAMod.SetotsuRatio(otsuRatio)
        self.qTCGAMod.SetcurvatureWeight(curvatureWeight)
        self.qTCGAMod.SetsizeThld(sizeThld)
        self.qTCGAMod.SetsizeUpperThld(sizeUpperThld)
        self.qTCGAMod.Setmpp(mpp)
        self.qTCGAMod.SetkernelSize(kernelSize)

        AA = self.foregroundNode.GetImageData()
        LL = self.labelNode.GetImageData()
        ddd = AA.GetDimensions()
        cp = EditUtil.EditUtil().getParameterNode().GetParameter('QuickTCGAEffect,currentXYPosition')
        if cp.__len__() == 0:
            a = (0, 0)
            b = (ddd[0] - 1, ddd[1] - 1)
            slicer.modules.SlicerPathologyWidget.SaveButton.setEnabled(1)
        else:
            currentXYPosition = eval(cp)
            startXYPosition = eval(
                EditUtil.EditUtil().getParameterNode().GetParameter('QuickTCGAEffect,startXYPosition'))
            sliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
            labelLogic = sliceLogic.GetLabelLayer()
            xyToIJK = labelLogic.GetXYToIJKTransform()
            currentXYPosition = xyToIJK.TransformDoublePoint(currentXYPosition + (0,))
            currentXYPosition = (int(round(currentXYPosition[0])), int(round(currentXYPosition[1])))
            startXYPosition = xyToIJK.TransformDoublePoint(startXYPosition + (0,))
            startXYPosition = (int(round(startXYPosition[0])), int(round(startXYPosition[1])))
            a = startXYPosition
            b = currentXYPosition
            slicer.modules.SlicerPathologyWidget.SaveButton.setEnabled(0)
        BB = self.GetTile(AA, a[0], a[1], b[0], b[1])
        LL = self.GetTile(LL, a[0], a[1], b[0], b[1])
        self.qTCGAMod.SetSourceVol(BB)
        self.qTCGAMod.SetSeedVol(LL)
        print "executing segmentation..."
        self.qTCGAMod.Run_NucleiSegYi(seg_type)
        print "segmentation is done"
        self.qTCGASegArray[:] = seedArray[:]
        self.MergeImages(LL, self.labelNode.GetImageData(), a[0], a[1])
        self.foregroundNode.GetImageData().Modified()
        self.foregroundNode.Modified()
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()
        self.currentMessage = "Nuclei segmentation is done"
        slicer.util.showStatusMessage(self.currentMessage)

    def wipeSegmentation(self):
        self.BlankLabelImage(self.labelNode.GetImageData())
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()

    def BlankLabelImage(self, image):
        dim = image.GetDimensions()
        for x in range(0, dim[0]):
            for y in range(0, dim[1]):
                for c in range(0, image.GetNumberOfScalarComponents()):
                    image.SetScalarComponentFromDouble(x, y, 0, c, 0.0)
        image.Modified()

    def GetTile(self, image, x1, y1, x2, y2):
        i = vtk.vtkImageData().NewInstance()
        i.SetDimensions(x2 - x1 + 1, y2 - y1 + 1, 1)
        i.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, image.GetNumberOfScalarComponents())
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for c in range(0, image.GetNumberOfScalarComponents()):
                    i.SetScalarComponentFromDouble(x - x1, y - y1, 0, c, image.GetScalarComponentAsDouble(x, y, 0, c))
        return i

    def MergeImages(self, image1, image2, a, b):
        dim = image1.GetDimensions()
        for x in range(a, a + dim[0]):
            for y in range(b, b + dim[1]):
                for c in range(0, image1.GetNumberOfScalarComponents()):
                    image2.SetScalarComponentFromDouble(x, y, 0, c,
                                                        image1.GetScalarComponentAsDouble(x - a, y - b, 0, c))
        image2.Modified()

    def destroy(self):
        for i in range(len(
                self.qtkeydefsQTCGA)):  # this will be an empty list if the KSlice part has been reached (all growcut functionality disabled)
            keyfun = self.qtkeydefsQTCGA[i]
            keydef = self.qtkeyconnections[i]
            test1 = keydef.disconnect('activated()', keyfun[1])
            test2 = keydef.disconnect('activatedAmbiguously()', keyfun[1])
            # self.qtkeyconnections.remove(keydef) # remove from list
            keydef.setParent(None)
            # why is this necessary for full disconnect (if removed, get the error that more and more keypresses are required if module is repeatedly erased and created
            keydef.delete()  # this causes errors

        # destroy QuickTCGA objects
        self.qTCGASeedArray = None
        self.qTCGASegArray = None
        self.qTCGAMod = None
        self.currentMessage = ""
        self.imgName = None
        self.imgBgrdName = None
        self.imgFgrdName = None
        self.labelNode = None
        self.backgroundNode = None
        slicer.modules.SlicerPathologyWidget.editorWidget.installShortcutKeys()

    def sliceViewMatchEditor(self, sliceLogic):
        imgNode = sliceLogic.GetBackgroundLayer().GetVolumeNode()
        labelNode = sliceLogic.GetLabelLayer().GetVolumeNode()

        # [compare types with isinstance() instead of ==]
        # if type(imgNode) == type(None) or type(labelNode) == type(None):
        #     self.dialogBox.setText("Either image (must be Background Image) or label not set in slice views.")
        #     self.dialogBox.show()
        #     if self.emergencyStopFunc:
        #         self.emergencyStopFunc()
        #     return False

        dimImg = self.backgroundNode.GetImageData().GetDimensions()
        dimLab = self.labelNode.GetImageData().GetDimensions()

        if not (dimImg[0] == dimLab[0] and dimImg[1] == dimLab[1] and dimImg[2] == dimLab[
            2]):  # if sizes dont match up(doing this b/c cant reach HelperBox parameters
            self.dialogBox.setText("Mismatched label to image.")
            self.dialogBox.show()
            if self.emergencyStopFunc:
                self.emergencyStopFunc()
            return False

            # if (self.imgBgrdName == imgNode.GetName()) and (self.labelName == labelNode.GetName()):
            #     return True
            # else:
            #     self.dialogBox.setText("Set image to values used for starting FastGrowCut.")
            #     self.dialogBox.show()
            #     if self.emergencyStopFunc:
            #         self.emergencyStopFunc()
            #     return False

    def QTCGAChangeLabelInput(self, caller, event):

        if self.sliceViewMatchEditor(self.sliceLogic) == False:
            return  # do nothing, exit function

    def entranceCursorDetect(self, caller, event):
        ijkPlane = self.sliceIJKPlane()
        self.ijkPlane = ijkPlane
        self.computeCurrSliceSmarter()


#
# QuickTCGAEffect
#

class QuickTCGAEffectExtension(LabelEffect.LabelEffect):
    """Organizes the Options, Tool, and Logic classes into a single instance
    that can be managed by the EditBox
    """

    def __init__(self):
        # name is used to define the name of the icon image resource (e.g. RectangleEffect.png)
        self.name = "QuickTCGAEffect"
        # tool tip is displayed on mouse hover
        self.toolTip = "hahahahaha"

        self.options = QuickTCGAEffectOptions
        self.tool = QuickTCGAEffectTool
        self.logic = QuickTCGAEffectLogic


""" Test:
sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.EditorEffectTemplateTool(sw)
"""


#
# QuickTCGAEffect
#

class QuickTCGAEffect:
    """
    This class is the 'hook' for slicer to detect and recognize the extension
    as a loadable scripted module
    """

    def __init__(self, parent):
        parent.title = "QuickTCGAEffectTemplate Effect"
        parent.categories = ["Developer Tools.Editor Extensions"]
        parent.contributors = ["Steve Pieper (Isomics)"]  # insert your name in the list
        parent.helpText = """
    Example of an editor extension.  No module interface here, only in the Editor module
    """
        parent.acknowledgementText = """
    This editor extension was developed by
    <Author>, <Institution>
    based on work by:
    Steve Pieper, Isomics, Inc.
    based on work by:
    Jean-Christophe Fillion-Robin, Kitware Inc.
    and was partially funded by NIH grant 3P41RR013218.
    """

    # TODO:
    # don't show this module - it only appears in the Editor module
    # parent.hidden = True

    # Add this extension to the editor's list for discovery when the module
    # is created.  Since this module may be discovered before the Editor itself,
    # create the list if it doesn't already exist.
    try:
        slicer.modules.editorExtensions
    except AttributeError:
        slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['QuickTCGAEffect'] = QuickTCGAEffectExtension


#
# QuickTCGAEffectTemplateWidget
#

class QuickTCGAEffectTemplateWidget:
    def __init__(self, parent=None):
        self.parent = parent

    def setup(self):
        # don't display anything for this widget - it will be hidden anyway
        pass

    def enter(self):
        pass

    def exit(self):
        pass


segno_lbl = "Segmentation No Declumping (fast)"
seg_lbl = "Segmentation Mean Shift Declumping (slow)"
segWtr_lbl = "Segmentation Watershed Declumping"
run_lbl = "Run"
running_lbl = "Running"
LOGICAL_FAST = 'FAST'
LOGICAL_MSHIFT = 'MSHIFT'
LOGICAL_WTRSHED = 'WTRSHED'

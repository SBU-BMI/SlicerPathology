import urllib
import urllib2
import mimetools, mimetypes
import os, stat
import sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from SlicerPathologyUtil.mixins import ModuleWidgetMixin
from Editor import EditorWidget
import PythonQt
import json
import EditorLib
from EditorLib import EditUtil
import datetime


#
# SlicerPathology
#

class SlicerPathology(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Slicer Pathology"
        self.parent.categories = ["Pathology"]
        self.parent.dependencies = []
        self.parent.contributors = ["Erich Bremer, Joel Saltz, Yi Gao, Tammy DiPrima (Stony Brook University)"]
        self.parent.helpText = """
    Automatic and semi-automatic pathology segmentation tools.
    """
        self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""  # replace with organization, grant and thanks.


#
# SlicerPathologyWidget
#

class SlicerPathologyWidget(ScriptedLoadableModuleWidget, ModuleWidgetMixin):
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)

        # self.resourcesPath = os.path.normpath(os.path.join(slicer.modules.slicerpathology.path.replace(self.moduleName + ".py", ""), 'Resources'))
        self.resourcesPath = os.path.join(slicer.modules.slicerpathology.path.replace(self.moduleName + ".py", ""), 'Resources')
        print "self.resourcesPath", self.resourcesPath

        self.modulePath = os.path.dirname(slicer.util.modulePath(self.moduleName))
        print "self.modulePath", self.modulePath

        self.currentStep = 1

    def setup(self):
        self.dirty = False
        # self.editUtil = EditorLib.EditUtil.EditUtil()
        self.parameterNode = EditorLib.EditUtil.EditUtil().getParameterNode()
        self.parameterNode.SetParameter("QuickTCGAEffect,erich", "reset")
        ScriptedLoadableModuleWidget.setup(self)
        # this section is for custom color box
        infoGroupBox = qt.QWidget()
        hbox = qt.QHBoxLayout()
        hbox.setMargin(0)
        self.studySelectionGroupBoxLayout = qt.QGridLayout()
        infoGroupBox.setLayout(hbox)
        self.studySelectionGroupBoxLayout.addWidget(infoGroupBox, 0, 3, 1, 1)

        # icons_path = os.path.normpath(os.path.join(self.resourcesPath, 'Icons', 'icon-infoBox.png'))
        icons_path = os.path.join(self.resourcesPath, 'Icons', 'icon-infoBox.png')
        print "icons_path", icons_path

        infoIcon = qt.QPixmap(icons_path)
        print "infoIcon", infoIcon

        self.customLUTInfoIcon = qt.QLabel()
        self.customLUTInfoIcon.setPixmap(infoIcon)
        self.customLUTInfoIcon.setSizePolicy(PythonQt.QtGui.QSizePolicy())
        hbox.addWidget(self.customLUTInfoIcon)
        self.customLUTLabel = qt.QLabel()
        hbox.addWidget(self.customLUTLabel)
        # end of custom color box section
        self.setupIcons()
        self.setupTabBarNavigation()
        self.setupsetupUI()
        self.setupimageSelectionUI()
        self.setupsegmentationUI()
        self.setupsubmissionUI()
        self.setupEditorWidget()
        editUtil = EditorLib.EditUtil.EditUtil()
        self.parameterNode = editUtil.getParameterNode()

        # Instantiate and connect widgets ...
        #
        # Parameters Area
        #
        parametersCollapsibleButton = ctk.ctkCollapsibleButton()
        parametersCollapsibleButton.text = "Parameters"
        self.layout.addWidget(parametersCollapsibleButton)

        # Layout within the dummy collapsible button
        parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

        #
        # check box to trigger taking screen shots for later use in tutorials
        #
        self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
        self.enableScreenshotsFlagCheckBox.checked = 0
        self.enableScreenshotsFlagCheckBox.setToolTip(
            "If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
        parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

        #
        # scale factor for screen shots
        #
        self.screenshotScaleFactorSliderWidget = ctk.ctkSliderWidget()
        self.screenshotScaleFactorSliderWidget.singleStep = 1.0
        self.screenshotScaleFactorSliderWidget.minimum = 1.0
        self.screenshotScaleFactorSliderWidget.maximum = 50.0
        self.screenshotScaleFactorSliderWidget.value = 1.0
        self.screenshotScaleFactorSliderWidget.setToolTip("Set scale factor for the screen shots.")
        parametersFormLayout.addRow("Screenshot scale factor", self.screenshotScaleFactorSliderWidget)

        #
        # Apply Button
        #
        # self.applyButton = qt.QPushButton("Apply")
        # self.applyButton.toolTip = "Run the algorithm."
        # self.applyButton.enabled = False
        # parametersFormLayout.addRow(self.applyButton)

        # Add vertical spacer
        self.layout.addStretch(1)
        self.j = {}

    def cleanup(self):
        pass

    def onSelect(self):
        self.applyButton.enabled = self.inputSelector.currentNode() and self.outputSelector.currentNode()

    def onApplyButton(self):
        logic = SlicerPathologyLogic()
        enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
        screenshotScaleFactor = int(self.screenshotScaleFactorSliderWidget.value)
        print("Run the algorithm")
        logic.run(self.inputSelector.currentNode(), self.outputSelector.currentNode(), enableScreenshotsFlag,
                  screenshotScaleFactor)

    def setupIcons(self):
        self.setupIcon = self.createIcon('icon-setup.png')
        self.imageSelectionIcon = self.createIcon('icon-imageselection.png')
        self.segmentationIcon = self.createIcon('icon-segmentation.png')
        self.submissionIcon = self.createIcon('icon-submission.png')

    def setupTabBarNavigation(self):
        self.tabWidget = qt.QTabWidget()
        self.layout.addWidget(self.tabWidget)

        setupGroupBox = qt.QGroupBox()
        imageSelectionGroupBox = qt.QGroupBox()
        segmentationGroupBox = qt.QGroupBox()
        submissionGroupBox = qt.QGroupBox()

        self.setupGroupBoxLayout = qt.QFormLayout()
        self.imageSelectionGroupBoxLayout = qt.QFormLayout()
        self.segmentationGroupBoxLayout = qt.QGridLayout()
        self.submissionGroupBoxLayout = qt.QFormLayout()

        setupGroupBox.setLayout(self.setupGroupBoxLayout)
        imageSelectionGroupBox.setLayout(self.imageSelectionGroupBoxLayout)
        segmentationGroupBox.setLayout(self.segmentationGroupBoxLayout)
        submissionGroupBox.setLayout(self.submissionGroupBoxLayout)

        self.tabWidget.setIconSize(qt.QSize(85, 30))

        self.tabWidget.addTab(setupGroupBox, self.setupIcon, '')
        self.tabWidget.addTab(imageSelectionGroupBox, self.imageSelectionIcon, '')
        self.tabWidget.addTab(segmentationGroupBox, self.segmentationIcon, '')
        self.tabWidget.addTab(submissionGroupBox, self.submissionIcon, '')
        self.tabWidget.connect('currentChanged(int)', self.onTabWidgetClicked)

        self.setTabsEnabled([1, 2, 3, 4], True)

    def onTabWidgetClicked(self, currentIndex):
        if currentIndex == 0:
            self.onStep1Selected()
        if currentIndex == 1:
            print ""
        if currentIndex == 2:
            print ""
        if currentIndex == 3:
            print ""

    def setTabsEnabled(self, indexes, enabled):
        for index in indexes:
            self.tabWidget.childAt(1, 1).setTabEnabled(index, enabled)

    def onStep1Selected(self):
        # if self.checkStep3or4Leave() is True:
        # return
        if self.currentStep == 1:
            return
        self.currentStep = 1
        self.setTabsEnabled([0], True)
        self.setTabsEnabled([1, 2, 3], False)

    def setupsetupUI(self):
        self.setupUserName = qt.QLineEdit()
        self.setupGroupBoxLayout.addRow("Username:", self.setupUserName)
        self.setupPassword = qt.QLineEdit()
        self.setupPassword.setEchoMode(2)
        # self.setupGroupBoxLayout.addRow("Password:", self.setupPassword)
        self.dataDirButton = ctk.ctkDirectoryButton()
        self.setupGroupBoxLayout.addRow(qt.QLabel("Data directory:"))
        self.setupGroupBoxLayout.addWidget(self.dataDirButton)
        self.setupExecutionID = qt.QLineEdit()
        self.setupGroupBoxLayout.addRow("Execution ID:", self.setupExecutionID)

    def setupimageSelectionUI(self):
        self.loadDataButton = qt.QPushButton("Load Image from disk")
        self.imageSelectionGroupBoxLayout.addWidget(self.loadDataButton)
        self.loadDataButton.connect('clicked()', self.loadTCGAData)
        self.WIP2 = qt.QPushButton("Select image from web")
        self.WIP2.connect('clicked()', self.onWIP2ButtonClicked)
        self.imageSelectionGroupBoxLayout.addWidget(self.WIP2)
        self.WIP3 = qt.QPushButton("Load image from web")
        self.WIP3.connect('clicked()', self.onWIP3ButtonClicked)
        self.imageSelectionGroupBoxLayout.addWidget(self.WIP3)
        self.RestoreButton = qt.QPushButton("Restore Session")
        self.RestoreButton.connect('clicked()', self.RestoreSession)
        self.imageSelectionGroupBoxLayout.addWidget(self.RestoreButton)

    #  def ebCenter(self):
    #    r = slicer.app.layoutManager().sliceWidget("Red").sliceController()
    #    r.fitSliceToBackground()

    def onWIP2ButtonClicked(self):
        self.openTargetImage0()

    def onWIP3ButtonClicked(self):
        self.openTargetImage()
        r = slicer.app.layoutManager().sliceWidget("Red").sliceController()
        r.fitSliceToBackground()

    def setupsegmentationUI(self):
        print ""

    def setupsubmissionUI(self):
        self.SaveButton = qt.QPushButton("Save")
        self.submissionGroupBoxLayout.addWidget(self.SaveButton)
        self.SaveButton.connect('clicked()', self.onSaveButtonClicked)
        self.SaveButton.setEnabled(0)
        # self.WebSaveButton = qt.QPushButton("Submit to web")
        # self.submissionGroupBoxLayout.addWidget(self.WebSaveButton)
        # self.WebSaveButton.connect('clicked()', self.onWebSaveButtonClicked)

    def QImage2vtkImage(self, image):
        i = vtk.vtkImageData().NewInstance()
        i.SetDimensions(image.width(), image.height(), 1)
        i.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
        for x in range(0, image.width()):
            for y in range(0, image.height()):
                c = qt.QColor(image.pixel(x, y))
                i.SetScalarComponentFromDouble(x, y, 0, 0, c.red())
                i.SetScalarComponentFromDouble(x, y, 0, 1, c.green())
                i.SetScalarComponentFromDouble(x, y, 0, 2, c.blue())
        return i

    def onWIPButtonClicked(self):
        import urllib2
        reply = urllib2.urlopen('http://www.osa.sunysb.edu/erich.png')
        byte_array = reply.read()
        image = qt.QImage(qt.QImage.Format_RGB888)
        image.loadFromData(byte_array)
        imageData = self.QImage2vtkImage(image)
        volumeNode = slicer.vtkMRMLVectorVolumeNode()
        volumeNode.SetName("WEB")
        volumeNode.SetAndObserveImageData(imageData)
        displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
        slicer.mrmlScene.AddNode(volumeNode)
        slicer.mrmlScene.AddNode(displayNode)
        volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.SetAndObserveColorNodeID('vtkMRMLColorTableNodeGrey')
        self.mutate()

    def RestoreSession(self):
        import zipfile
        import os.path
        f = qt.QFileDialog.getOpenFileName()
        zf = zipfile.ZipFile(f)
        for filename in zf.namelist():
            try:
                data = zf.read(filename)
            except KeyError:
                print 'ERROR: Did not find %s in zip file' % filename
            else:
                print filename

    def onSaveButtonClicked(self):
        print "\nSAVING"
        print "\nQuickTCGAEffectOptions.params:", slicer.modules.QuickTCGAEffectOptions.params
        self.dirty = False
        import zipfile
        import os.path
        import uuid
        bundle = EditUtil.EditUtil().getParameterNode().GetParameter('QuickTCGAEffect,erich')
        tran = json.loads(bundle)
        print "\nbundle:\n", bundle
        layers = []
        print ""
        for key in tran:
            print "tran.key:", key
            nn = tran[key]
            nn["file"] = key + '.tif'
            layers.append(tran[key])
        self.j['layers'] = layers
        self.j['username'] = self.setupUserName.text
        self.j['sourcetile'] = self.tilename
        self.j['generator'] = slicer.app.applicationVersion
        self.j['timestamp'] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.j['execution_id'] = self.setupExecutionID.text + "-" + uuid.uuid4().get_urn()
        labelNodes = slicer.util.getNodes('vtkMRMLLabelMapVolumeNode*')
        savedMessage = 'Segmentations for the following series were saved:\n\n'

        if os.path.isabs(self.dataDirButton.directory):
            ddb_dir = self.dataDirButton.directory
        else:
            ddb_dir = os.getcwd()

        ddb_dir = os.path.normpath(ddb_dir);
        print "\nddb_dir:", ddb_dir

        str_name = self.tilename + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.zip'
        print "str_name", str_name
        zfname = os.path.normpath(os.path.join(ddb_dir, str_name))
        # zfname = os.path.join(ddb_dir, str_name)
        # zfname = os.path.normpath(os.path.join(ddb_dir, self.tilename + "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.zip'))

        print "\nzipfile name"
        print zfname

        zf = zipfile.ZipFile(zfname, mode='w')
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_cn = red_logic.GetSliceCompositeNode()
        fg = red_cn.GetForegroundVolumeID()
        ff = slicer.util.getNode(fg)
        sNode = slicer.vtkMRMLVolumeArchetypeStorageNode()
        sNode.SetFileName("original.tif")
        sNode.SetWriteFileFormat('tif')
        sNode.SetURI(None)
        success = sNode.WriteData(ff)
        zf.write("original.tif")
        os.remove("original.tif")
        for label in labelNodes.values():
            labelName = label.GetName()

            # labelFileName = os.path.normpath(os.path.join(ddb_dir, labelName + '.tif'))
            labelFileName = os.path.join(ddb_dir, labelName + '.tif')
            # print "labelFileName", labelFileName

            # compFileName = os.path.normpath(os.path.join(ddb_dir, labelName + '-comp.tif'))
            compFileName = os.path.join(ddb_dir, labelName + '-comp.tif')
            # print "compFileName", compFileName

            sNode.SetFileName(labelFileName)
            success = sNode.WriteData(label)
            if success:
                print "adding " + labelFileName + " to zipfile"
                zf.write(labelFileName, os.path.basename(labelFileName))
                os.remove(labelFileName)
            else:
                print "failed writing " + labelFileName
            comp = self.WriteLonI(label.GetImageData(), ff.GetImageData())
            volumeNode = slicer.vtkMRMLVectorVolumeNode()
            volumeNode.SetName("COMP")
            volumeNode.SetAndObserveImageData(comp)
            sNode.SetFileName(compFileName)
            success = sNode.WriteData(volumeNode)
            if success:
                print "adding " + compFileName + " to zipfile"
                zf.write(compFileName, os.path.basename(compFileName))
                os.remove(compFileName)
            else:
                print "failed writing " + compFileName
        jstr = json.dumps(self.j, sort_keys=True, indent=4, separators=(',', ': '))

        # mfname = os.path.normpath(os.path.join(ddb_dir, 'manifest.json'))
        mfname = os.path.join(ddb_dir, 'manifest.json')
        print "manifest", mfname

        f = open(mfname, 'w')
        f.write(jstr)
        f.close()
        zf.write(mfname, os.path.basename(mfname))
        zf.close()
        os.remove(mfname)
        # import sys
        # reload(sys)
        # sys.setdefaultencoding('utf8')
        # opener = urllib2.build_opener(MultipartPostHandler)
        # params = { "ss" : "0",            # show source
        #           "doctype" : "Inline",
        #           "uploaded_file" : open(zfname, "rb") }
        # print params
        # print opener.open('http://quip1.bmi.stonybrook.edu:4000/upload', params).read()

    def WriteLonI(self, src, dest):
        dim = src.GetDimensions()
        i = vtk.vtkImageData().NewInstance()
        i.SetDimensions(dim[0], dim[1], 1)
        i.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
        for x in range(0, dim[0]):
            for y in range(0, dim[1]):
                if src.GetScalarComponentAsDouble(x, y, 0, 0) == 0:
                    for c in range(0, 3):
                        i.SetScalarComponentFromDouble(x, y, 0, c, dest.GetScalarComponentAsDouble(x, y, 0, c))
                else:
                    if (
                       (src.GetScalarComponentAsDouble(x + 1, y - 1, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x + 1, y, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x + 1, y + 1, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x, y + 1, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x, y - 1, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x - 1, y + 1, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x - 1, y, 0, 0) == 1) and
                       (src.GetScalarComponentAsDouble(x - 1, y - 1, 0, 0) == 1)):
                        for c in range(0, 3):
                            i.SetScalarComponentFromDouble(x, y, 0, c, dest.GetScalarComponentAsDouble(x, y, 0, c))
                    else:
                        i.SetScalarComponentFromDouble(x, y, 0, 0, 0)
                        i.SetScalarComponentFromDouble(x, y, 0, 1, 250)
                        i.SetScalarComponentFromDouble(x, y, 0, 2, 0)
        i.Modified()
        return i

    def onWebSaveButtonClicked(self):
        print "Web Save to be implemented...."

    def checkAndSetLUT(self):
        # Default to module color table
        # self.resourcesPath = os.path.normpath(os.path.join(slicer.modules.slicerpathology.path.replace(self.moduleName + ".py", ""), 'Resources'))
        self.resourcesPath = os.path.join(slicer.modules.slicerpathology.path.replace(self.moduleName + ".py", ""), 'Resources')
        print "self.resourcesPath 1", self.resourcesPath

        # self.colorFile = os.path.normpath(os.path.join(self.resourcesPath, "Colors", "SlicerPathology.csv"))
        self.colorFile = os.path.join(self.resourcesPath, "Colors", "SlicerPathology.csv")
        print "self.colorFile 1", self.colorFile

        self.customLUTLabel.setText('Using Default LUT')
        try:
            self.editorWidget.helper.structureListWidget.merge = None
        except AttributeError:
            pass
        # setup the color table, make sure SlicerPathology LUT is a singleton
        allColorTableNodes = slicer.util.getNodes('vtkMRMLColorTableNode*').values()
        for ctn in allColorTableNodes:
            # print "color: "+ctn.GetName()
            if ctn.GetName() == 'SlicerPathologyColor':
                slicer.mrmlScene.RemoveNode(ctn)
                break
        self.SlicerPathologyColorNode = slicer.vtkMRMLColorTableNode()
        colorNode = self.SlicerPathologyColorNode
        colorNode.SetName('SlicerPathologyColor')
        slicer.mrmlScene.AddNode(colorNode)
        colorNode.SetTypeToUser()
        with open(self.colorFile) as f:
            n = sum(1 for line in f)
        colorNode.SetNumberOfColors(n - 1)
        colorNode.NamesInitialisedOn()
        import csv
        self.structureNames = []
        with open(self.colorFile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for index, row in enumerate(reader):
                success = colorNode.SetColor(index, row['Label'], float(row['R']) / 255, float(row['G']) / 255,
                                             float(row['B']) / 255, float(row['A']))
                if not success:
                    print "color %s could not be set" % row['Label']
                self.structureNames.append(row['Label'])

    def setupEditorWidget(self):
        editorWidgetParent = slicer.qMRMLWidget()
        editorWidgetParent.setLayout(qt.QVBoxLayout())
        editorWidgetParent.setMRMLScene(slicer.mrmlScene)
        self.editorWidget = EditorWidget(parent=editorWidgetParent)
        self.editorWidget.setup()
        self.segmentationGroupBoxLayout.addWidget(self.editorWidget.parent)

    def mutate(self):
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_cn = red_logic.GetSliceCompositeNode()
        fgrdVolID = red_cn.GetBackgroundVolumeID()
        fgrdNode = slicer.util.getNode("WEB")
        fgrdVolID = fgrdNode.GetID()
        fMat = vtk.vtkMatrix4x4()
        # fgrdNode.GetIJKToRASDirectionMatrix(fMat)
        bgrdName = fgrdNode.GetName() + '_gray'
        magnitude = vtk.vtkImageMagnitude()
        magnitude.SetInputData(fgrdNode.GetImageData())
        magnitude.Update()
        bgrdNode = slicer.vtkMRMLScalarVolumeNode()
        bgrdNode.SetImageDataConnection(magnitude.GetOutputPort())
        bgrdNode.SetName(bgrdName)
        # bgrdNode.SetIJKToRASDirectionMatrix(fMat)
        slicer.mrmlScene.AddNode(bgrdNode)
        bgrdVolID = bgrdNode.GetID()
        red_cn.SetForegroundVolumeID(fgrdVolID)
        red_cn.SetBackgroundVolumeID(bgrdVolID)
        red_cn.SetForegroundOpacity(1)

        # resourcesPath = os.path.normpath(os.path.join(slicer.modules.slicerpathology.path.replace("SlicerPathology.py", ""), 'Resources'))
        resourcesPath = os.path.join(slicer.modules.slicerpathology.path.replace("SlicerPathology.py", ""), 'Resources')
        print "resourcesPath", resourcesPath

        # colorFile = os.path.normpath(os.path.join(resourcesPath, "Colors", "SlicerPathology.csv"))
        colorFile = os.path.join(resourcesPath, "Colors", "SlicerPathology.csv")
        print "colorFile", colorFile

        try:
            slicer.modules.EditorWidget.helper.structureListWidget.merge = None
        except AttributeError:
            pass

        allColorTableNodes = slicer.util.getNodes('vtkMRMLColorTableNode*').values()
        for ctn in allColorTableNodes:
            if ctn.GetName() == 'SlicerPathologyColor':
                slicer.mrmlScene.RemoveNode(ctn)
                break

        SlicerPathologyColorNode = slicer.vtkMRMLColorTableNode()
        colorNode = SlicerPathologyColorNode
        colorNode.SetName('SlicerPathologyColor')
        slicer.mrmlScene.AddNode(colorNode)
        colorNode.SetTypeToUser()
        with open(colorFile) as f:
            n = sum(1 for line in f)

        colorNode.SetNumberOfColors(n - 1)
        colorNode.NamesInitialisedOn()
        import csv
        structureNames = []
        with open(colorFile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for index, row in enumerate(reader):
                success = colorNode.SetColor(index, row['Label'], float(row['R']) / 255, float(row['G']) / 255,
                                             float(row['B']) / 255, float(row['A']))
                if not success:
                    print "color %s could not be set" % row['Label']
                structureNames.append(row['Label'])
        volumesLogic = slicer.modules.volumes.logic()
        labelName = bgrdName + '-label'
        refLabel = volumesLogic.CreateAndAddLabelVolume(slicer.mrmlScene, bgrdNode, labelName)
        refLabel.GetDisplayNode().SetAndObserveColorNodeID(SlicerPathologyColorNode.GetID())
        self.editorWidget.helper.setMasterVolume(bgrdNode)

    def openTargetImage0(self):
        self.v = qt.QWebView()
        weburl = 'http://quip1.bmi.stonybrook.edu/slicer/cancer_select.html'
        self.v.setUrl(qt.QUrl(weburl))
        self.v.show()

    def openTargetImage(self):
        import string
        p = self.v.page()
        m = p.mainFrame()
        imageBound = m.evaluateJavaScript(
            'viewer.viewport.viewportToImageRectangle(viewer.viewport.getBounds().x, viewer.viewport.getBounds().y, viewer.viewport.getBounds().width, viewer.viewport.getBounds().height)')
        x = imageBound[u'x']
        y = imageBound[u'y']
        width = imageBound[u'width']
        height = imageBound[u'height']
        self.j['x'] = x
        self.j['y'] = y
        self.j['width'] = width
        self.j['height'] = height
        imagedata = m.evaluateJavaScript('imagedata')
        tmpfilename = imagedata[u'metaData'][1]
        imageFileName = string.rstrip(tmpfilename, '.dzi')
        self.tilename = imagedata[u'imageId']
        print "self.tilename", self.tilename
        self.parameterNode.SetParameter("SlicerPathology,tilename", self.tilename)
        current_weburl = 'http://quip1.uhmc.sunysb.edu/fcgi-bin/iipsrv.fcgi?IIIF=' + imageFileName + '/' + str(
            x) + ',' + str(y) + ',' + str(width) + ',' + str(height) + '/full/0/default.jpg'
        print current_weburl
        self.v.setUrl(qt.QUrl(current_weburl))
        self.v.show()

        reply = urllib2.urlopen(current_weburl)
        byte_array = reply.read()
        image = qt.QImage(qt.QImage.Format_RGB888)
        image.loadFromData(byte_array)
        imageData = self.QImage2vtkImage(image)
        volumeNode = slicer.vtkMRMLVectorVolumeNode()
        volumeNode.SetName("WEB")
        volumeNode.SetAndObserveImageData(imageData)
        displayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
        slicer.mrmlScene.AddNode(volumeNode)
        slicer.mrmlScene.AddNode(displayNode)
        volumeNode.SetAndObserveDisplayNodeID(displayNode.GetID())
        displayNode.SetAndObserveColorNodeID('vtkMRMLColorTableNodeGrey')
        self.mutate()

    def Four2ThreeChannel(self, image):
        dim = image.GetDimensions()
        i = vtk.vtkImageData().NewInstance()
        i.SetDimensions(dim[0], dim[1], 1)
        i.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 3)
        for x in range(0, dim[0]):
            for y in range(0, dim[1]):
                for c in range(0, 3):
                    i.SetScalarComponentFromDouble(x, y, 0, c, image.GetScalarComponentAsDouble(x, y, 0, c))
        i.Modified()
        return i

    def loadTCGAData(self):
        print self.dirty
        if self.dirty:
            if slicer.util.confirmYesNoDisplay("Proceeding will flush any unsaved work.  Do you wish to continue?"):
                EditUtil.EditUtil().getParameterNode().SetParameter('QuickTCGAEffect,erich', "reset")
                slicer.mrmlScene.Clear(0)
                dirty = False
                if slicer.util.openAddVolumeDialog():
                    self.loademup()
        else:
            EditUtil.EditUtil().getParameterNode().SetParameter('QuickTCGAEffect,erich', "reset")
            slicer.mrmlScene.Clear(0)
            dirty = False
            sel = slicer.util.openAddVolumeDialog()
            if sel:
                self.loademup()

    def loademup(self):
        self.dirty = True
        import EditorLib
        editUtil = EditorLib.EditUtil.EditUtil()
        imsainode = editUtil.getBackgroundVolume()
        imsai = imsainode.GetImageData()
        if imsai.GetNumberOfScalarComponents() > 3:
            lala = self.Four2ThreeChannel(imsai)
            print lala.GetNumberOfScalarComponents()
            imsainode.SetAndObserveImageData(lala)
            imsainode.Modified()
        red_logic = slicer.app.layoutManager().sliceWidget("Red").sliceLogic()
        red_cn = red_logic.GetSliceCompositeNode()
        fgrdVolID = red_cn.GetBackgroundVolumeID()
        fgrdNode = slicer.util.getNode(fgrdVolID)
        fMat = vtk.vtkMatrix4x4()
        fgrdNode.GetIJKToRASDirectionMatrix(fMat)
        bgrdName = fgrdNode.GetName() + '_gray'
        self.tilename = fgrdNode.GetName() + '_gray'
        self.parameterNode.SetParameter("SlicerPathology,tilename", self.tilename)
        # Create dummy grayscale image
        magnitude = vtk.vtkImageMagnitude()
        magnitude.SetInputData(fgrdNode.GetImageData())
        magnitude.Update()
        bgrdNode = slicer.vtkMRMLScalarVolumeNode()
        bgrdNode.SetImageDataConnection(magnitude.GetOutputPort())
        bgrdNode.SetName(bgrdName)
        bgrdNode.SetIJKToRASDirectionMatrix(fMat)
        slicer.mrmlScene.AddNode(bgrdNode)
        bgrdVolID = bgrdNode.GetID()
        red_cn.SetForegroundVolumeID(fgrdVolID)
        red_cn.SetBackgroundVolumeID(bgrdVolID)
        red_cn.SetForegroundOpacity(1)
        self.checkAndSetLUT()
        cv = slicer.util.getNode(bgrdName)
        self.volumesLogic = slicer.modules.volumes.logic()
        labelName = bgrdName + '-label'
        refLabel = self.volumesLogic.CreateAndAddLabelVolume(slicer.mrmlScene, cv, labelName)
        refLabel.GetDisplayNode().SetAndObserveColorNodeID(self.SlicerPathologyColorNode.GetID())
        self.editorWidget.helper.setMasterVolume(cv)


#
# SlicerPathologyLogic
#

class SlicerPathologyLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def hasImageData(self, volumeNode):
        """This is a dummy logic method that
        returns true if the passed in volume
        node has valid image data
        """
        if not volumeNode:
            print('no volume node')
            return False
        if volumeNode.GetImageData() == None:
            print('no image data')
            return False
        return True

    def takeScreenshot(self, name, description, type=-1):
        # show the message even if not taking a screen shot
        self.delayDisplay(description)

        if self.enableScreenshots == 0:
            return

        lm = slicer.app.layoutManager()
        # switch on the type to get the requested window
        widget = 0
        if type == slicer.qMRMLScreenShotDialog.FullLayout:
            # full layout
            widget = lm.viewport()
        elif type == slicer.qMRMLScreenShotDialog.ThreeD:
            # just the 3D window
            widget = lm.threeDWidget(0).threeDView()
        elif type == slicer.qMRMLScreenShotDialog.Red:
            # red slice window
            widget = lm.sliceWidget("Red")
        elif type == slicer.qMRMLScreenShotDialog.Yellow:
            # yellow slice window
            widget = lm.sliceWidget("Yellow")
        elif type == slicer.qMRMLScreenShotDialog.Green:
            # green slice window
            widget = lm.sliceWidget("Green")
        else:
            # default to using the full window
            widget = slicer.util.mainWindow()
            # reset the type so that the node is set correctly
            type = slicer.qMRMLScreenShotDialog.FullLayout

        # grab and convert to vtk image data
        qpixMap = qt.QPixmap().grabWidget(widget)
        qimage = qpixMap.toImage()
        imageData = vtk.vtkImageData()
        slicer.qMRMLUtils().qImageToVtkImageData(qimage, imageData)

        annotationLogic = slicer.modules.annotations.logic()
        annotationLogic.CreateSnapShot(name, description, type, self.screenshotScaleFactor, imageData)

    def run(self, inputVolume, outputVolume, enableScreenshots=0, screenshotScaleFactor=1):
        """
        Run the actual algorithm
        """

        self.delayDisplay('Running the aglorithm')

        self.enableScreenshots = enableScreenshots
        self.screenshotScaleFactor = screenshotScaleFactor

        self.takeScreenshot('SlicerPathology-Start', 'Start', -1)

        return True


class SlicerPathologyTest(ScriptedLoadableModuleTest):
    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_SlicerPathology1()

    def test_SlicerPathology1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests sould exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import urllib
        downloads = (
            ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

        for url, name, loader in downloads:
            filePath = slicer.app.temporaryPath + '/' + name
            if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
                print('Requesting download %s from %s...\n' % (name, url))
                urllib.urlretrieve(url, filePath)
            if loader:
                print('Loading %s...\n' % (name,))
                loader(filePath)
        self.delayDisplay('Finished with download and loading\n')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = SlicerPathologyLogic()
        self.assertTrue(logic.hasImageData(volumeNode))
        self.delayDisplay('Test passed!')


####
# 02/2006 Will Holcomb <wholcomb@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable


# Controls how sequences are uncoded. If true, elements may be given multiple values by
#  assigning a sequence.
doseq = 1


class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10  # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                for (key, value) in data.items():
                    if type(value) == file:
                        v_files.append((key, value))
                    else:
                        v_vars.append((key, value))
            except TypeError:
                systype, value, traceback = sys.exc_info()
                raise TypeError, "not a valid non-string sequence or mapping object", traceback

            if len(v_files) == 0:
                data = urllib.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)
                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if (request.has_header('Content-Type')
                    and request.get_header('Content-Type').find('multipart/form-data') != 0):
                    print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
                request.add_unredirected_header('Content-Type', contenttype)

            request.add_data(data)
        return request

    def multipart_encode(vars, files, boundary=None, buffer=None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buffer is None:
            buffer = ''
        for (key, value) in vars:
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"' % key
            buffer += '\r\n\r\n' + value + '\r\n'
        for (key, fd) in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = fd.name.split('/')[-1]
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buffer += '--%s\r\n' % boundary
            buffer += 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
            buffer += 'Content-Type: %s\r\n' % contenttype
            # buffer += 'Content-Length: %s\r\n' % file_size
            fd.seek(0)
            buffer += '\r\n' + fd.read() + '\r\n'
        buffer += '--%s--\r\n\r\n' % boundary
        return boundary, buffer

    multipart_encode = Callable(multipart_encode)

    https_request = http_request

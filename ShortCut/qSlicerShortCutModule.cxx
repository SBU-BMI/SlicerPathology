/*==============================================================================

  Program: 3D Slicer

  Portions (c) Copyright Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

==============================================================================*/

// Qt includes
#include <QtPlugin>

// ShortCut Logic includes
#include <vtkSlicerShortCutLogic.h>

// ShortCut includes
#include "qSlicerShortCutModule.h"
#include "qSlicerShortCutModuleWidget.h"

//-----------------------------------------------------------------------------
Q_EXPORT_PLUGIN2(qSlicerShortCutModule, qSlicerShortCutModule);

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerShortCutModulePrivate
{
public:
  qSlicerShortCutModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerShortCutModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerShortCutModulePrivate
::qSlicerShortCutModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerShortCutModule methods

//-----------------------------------------------------------------------------
qSlicerShortCutModule
::qSlicerShortCutModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerShortCutModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerShortCutModule::~qSlicerShortCutModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerShortCutModule::helpText()const
{
  return "This is a loadable module bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerShortCutModule::acknowledgementText()const
{
  return "This work was was partially funded by NIH grant 3P41RR013218-12S1";
}

//-----------------------------------------------------------------------------
QStringList qSlicerShortCutModule::contributors()const
{
  QStringList moduleContributors;
  moduleContributors << QString("Jean-Christophe Fillion-Robin (Kitware)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerShortCutModule::icon()const
{
  return QIcon(":/Icons/ShortCut.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerShortCutModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerShortCutModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerShortCutModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation * qSlicerShortCutModule
::createWidgetRepresentation()
{
  return new qSlicerShortCutModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerShortCutModule::createLogic()
{
  return vtkSlicerShortCutLogic::New();
}

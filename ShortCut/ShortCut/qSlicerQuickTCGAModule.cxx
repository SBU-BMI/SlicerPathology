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

// QuickTCGA Logic includes
#include <vtkSlicerQuickTCGALogic.h>

// QuickTCGA includes
#include "qSlicerQuickTCGAModule.h"
#include "qSlicerQuickTCGAModuleWidget.h"

//-----------------------------------------------------------------------------
Q_EXPORT_PLUGIN2(qSlicerQuickTCGAModule, qSlicerQuickTCGAModule);

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerQuickTCGAModulePrivate
{
public:
  qSlicerQuickTCGAModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerQuickTCGAModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerQuickTCGAModulePrivate
::qSlicerQuickTCGAModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerQuickTCGAModule methods

//-----------------------------------------------------------------------------
qSlicerQuickTCGAModule
::qSlicerQuickTCGAModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerQuickTCGAModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerQuickTCGAModule::~qSlicerQuickTCGAModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerQuickTCGAModule::helpText()const
{
  return "This is a loadable module bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerQuickTCGAModule::acknowledgementText()const
{
  return "This work was was partially funded by NIH grant 3P41RR013218-12S1";
}

//-----------------------------------------------------------------------------
QStringList qSlicerQuickTCGAModule::contributors()const
{
  QStringList moduleContributors;
  moduleContributors << QString("Jean-Christophe Fillion-Robin (Kitware)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerQuickTCGAModule::icon()const
{
  return QIcon(":/Icons/QuickTCGA.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerQuickTCGAModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerQuickTCGAModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerQuickTCGAModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation * qSlicerQuickTCGAModule
::createWidgetRepresentation()
{
  return new qSlicerQuickTCGAModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerQuickTCGAModule::createLogic()
{
  return vtkSlicerQuickTCGALogic::New();
}

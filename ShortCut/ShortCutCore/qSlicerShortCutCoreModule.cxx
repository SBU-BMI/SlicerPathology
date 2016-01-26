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

// ShortCutCore Logic includes
#include <vtkSlicerShortCutCoreLogic.h>

// ShortCutCore includes
#include "qSlicerShortCutCoreModule.h"
#include "qSlicerShortCutCoreModuleWidget.h"

//-----------------------------------------------------------------------------
Q_EXPORT_PLUGIN2(qSlicerShortCutCoreModule, qSlicerShortCutCoreModule);

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerShortCutCoreModulePrivate
{
public:
  qSlicerShortCutCoreModulePrivate();
};

//-----------------------------------------------------------------------------
// qSlicerShortCutCoreModulePrivate methods

//-----------------------------------------------------------------------------
qSlicerShortCutCoreModulePrivate
::qSlicerShortCutCoreModulePrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerShortCutCoreModule methods

//-----------------------------------------------------------------------------
qSlicerShortCutCoreModule
::qSlicerShortCutCoreModule(QObject* _parent)
  : Superclass(_parent)
  , d_ptr(new qSlicerShortCutCoreModulePrivate)
{
}

//-----------------------------------------------------------------------------
qSlicerShortCutCoreModule::~qSlicerShortCutCoreModule()
{
}

//-----------------------------------------------------------------------------
QString qSlicerShortCutCoreModule::helpText()const
{
  return "This is a loadable module bundled in an extension";
}

//-----------------------------------------------------------------------------
QString qSlicerShortCutCoreModule::acknowledgementText()const
{
  return "This work was was partially funded by NIH grant 3P41RR013218-12S1";
}

//-----------------------------------------------------------------------------
QStringList qSlicerShortCutCoreModule::contributors()const
{
  QStringList moduleContributors;
  moduleContributors << QString("Jean-Christophe Fillion-Robin (Kitware)");
  return moduleContributors;
}

//-----------------------------------------------------------------------------
QIcon qSlicerShortCutCoreModule::icon()const
{
  return QIcon(":/Icons/ShortCutCore.png");
}

//-----------------------------------------------------------------------------
QStringList qSlicerShortCutCoreModule::categories() const
{
  return QStringList() << "Examples";
}

//-----------------------------------------------------------------------------
QStringList qSlicerShortCutCoreModule::dependencies() const
{
  return QStringList();
}

//-----------------------------------------------------------------------------
void qSlicerShortCutCoreModule::setup()
{
  this->Superclass::setup();
}

//-----------------------------------------------------------------------------
qSlicerAbstractModuleRepresentation * qSlicerShortCutCoreModule
::createWidgetRepresentation()
{
  return new qSlicerShortCutCoreModuleWidget;
}

//-----------------------------------------------------------------------------
vtkMRMLAbstractLogic* qSlicerShortCutCoreModule::createLogic()
{
  return vtkSlicerShortCutCoreLogic::New();
}

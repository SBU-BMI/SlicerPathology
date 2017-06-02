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
#include <QDebug>

// SlicerQt includes
#include "qSlicerShortCutModuleWidget.h"
#include "ui_qSlicerShortCutModuleWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ExtensionTemplate
class qSlicerShortCutModuleWidgetPrivate: public Ui_qSlicerShortCutModuleWidget
{
public:
  qSlicerShortCutModuleWidgetPrivate();
};

//-----------------------------------------------------------------------------
// qSlicerShortCutModuleWidgetPrivate methods

//-----------------------------------------------------------------------------
qSlicerShortCutModuleWidgetPrivate::qSlicerShortCutModuleWidgetPrivate()
{
}

//-----------------------------------------------------------------------------
// qSlicerShortCutModuleWidget methods

//-----------------------------------------------------------------------------
qSlicerShortCutModuleWidget::qSlicerShortCutModuleWidget(QWidget* _parent)
  : Superclass( _parent )
  , d_ptr( new qSlicerShortCutModuleWidgetPrivate )
{
}

//-----------------------------------------------------------------------------
qSlicerShortCutModuleWidget::~qSlicerShortCutModuleWidget()
{
}

//-----------------------------------------------------------------------------
void qSlicerShortCutModuleWidget::setup()
{
  Q_D(qSlicerShortCutModuleWidget);
  d->setupUi(this);
  this->Superclass::setup();
}


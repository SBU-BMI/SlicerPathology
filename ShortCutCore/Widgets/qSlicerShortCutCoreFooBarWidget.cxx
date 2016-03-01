/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// FooBar Widgets includes
#include "qSlicerShortCutCoreFooBarWidget.h"
#include "ui_qSlicerShortCutCoreFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ShortCutCore
class qSlicerShortCutCoreFooBarWidgetPrivate
  : public Ui_qSlicerShortCutCoreFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerShortCutCoreFooBarWidget);
protected:
  qSlicerShortCutCoreFooBarWidget* const q_ptr;

public:
  qSlicerShortCutCoreFooBarWidgetPrivate(
    qSlicerShortCutCoreFooBarWidget& object);
  virtual void setupUi(qSlicerShortCutCoreFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerShortCutCoreFooBarWidgetPrivate
::qSlicerShortCutCoreFooBarWidgetPrivate(
  qSlicerShortCutCoreFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerShortCutCoreFooBarWidgetPrivate
::setupUi(qSlicerShortCutCoreFooBarWidget* widget)
{
  this->Ui_qSlicerShortCutCoreFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerShortCutCoreFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerShortCutCoreFooBarWidget
::qSlicerShortCutCoreFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerShortCutCoreFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerShortCutCoreFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerShortCutCoreFooBarWidget
::~qSlicerShortCutCoreFooBarWidget()
{
}

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
#include "qSlicerShortCutFooBarWidget.h"
#include "ui_qSlicerShortCutFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_ShortCut
class qSlicerShortCutFooBarWidgetPrivate
  : public Ui_qSlicerShortCutFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerShortCutFooBarWidget);
protected:
  qSlicerShortCutFooBarWidget* const q_ptr;

public:
  qSlicerShortCutFooBarWidgetPrivate(
    qSlicerShortCutFooBarWidget& object);
  virtual void setupUi(qSlicerShortCutFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerShortCutFooBarWidgetPrivate
::qSlicerShortCutFooBarWidgetPrivate(
  qSlicerShortCutFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerShortCutFooBarWidgetPrivate
::setupUi(qSlicerShortCutFooBarWidget* widget)
{
  this->Ui_qSlicerShortCutFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerShortCutFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerShortCutFooBarWidget
::qSlicerShortCutFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerShortCutFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerShortCutFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerShortCutFooBarWidget
::~qSlicerShortCutFooBarWidget()
{
}

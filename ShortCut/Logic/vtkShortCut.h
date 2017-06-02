#ifndef VTKShortCut_H
#define VTKShortCut_H

#include "vtkSlicerShortCutModuleLogicExport.h"
#include "vtkImageData.h"
#include "ShortCutSegmenter.h"

#include <QProgressBar>
#include <QMainWindow>
#include <QStatusBar>
#include "qSlicerApplication.h"

const unsigned short SrcDimension = 2;
typedef float DistPixelType; // float type pixel for cost function
typedef short SrcPixelType;
typedef unsigned char LabPixelType;

class VTK_SLICER_SHORTCUT_MODULE_LOGIC_EXPORT vtkShortCut : public vtkObject
{
public:
  static vtkShortCut* New();
  // vtkTypeRevisionMacro(vtkFastGrowCutSeg,vtkObject);
  vtkTypeMacro(vtkShortCut, vtkObject);

  // set parameters of Quick TCGA segmenter
  vtkSetObjectMacro(SourceVol, vtkImageData);
  vtkSetObjectMacro(SeedVol, vtkImageData);
  vtkSetObjectMacro(SegVol, vtkImageData);
  vtkSetObjectMacro(SCROIVol, vtkImageData);
  vtkSetMacro(otsuRatio, float);
  vtkSetMacro(curvatureWeight, double);
  vtkSetMacro(sizeThld, float);
  vtkSetMacro(sizeUpperThld, float);
  vtkSetMacro(mpp, double);

  // vtkSetObjectMacro(OutputVol, vtkImageData);

  // vtkSetMacro(InitializationFlag, bool);

  // processing functions
  void Run_QTCGA_Segmentation();
  void Run_QTCGA_Template();
  void Run_Refine_Curvature();
  void Run_QTCGA_ShortCut();
  void Initialization();
  // void RunFGC();
  void PrintSelf(ostream& os, vtkIndent indent);

protected:
  vtkShortCut();
  virtual ~vtkShortCut();

private:
  // vtk image data (from slicer)
  vtkImageData* SourceVol;
  vtkImageData* SeedVol;
  vtkImageData* SegVol;
  vtkImageData* SCROIVol;

  float otsuRatio;
  double curvatureWeight;
  float sizeThld;
  float sizeUpperThld;
  double mpp;

  cv::Mat m_imSrc;
  cv::Mat m_imLab;
  cv::Mat m_imPreSeg;
  cv::Mat m_imSCROI;

  // logic code
  ShortCutSegmenter* m_qTCGASeg;

  // state variables
  bool InitializationFlag;
};

#endif

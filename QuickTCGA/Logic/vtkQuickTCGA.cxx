#include <iostream>
#include "vtkQuickTCGA.h"

#include "vtkObjectFactory.h"
#include "vtkSmartPointer.h"

#include "itkImage.h"
#include "itkTimeProbe.h"

#include "QuickTCGASegmenter.h"
#include "TCGAUtilities.h"

//vtkCxxRevisionMacro(vtkFastGrowCutSeg, "$Revision$"); //necessary?
vtkStandardNewMacro(vtkQuickTCGA); //for the new() macro

namespace
{
  //----------------------------------------------------------------------------
  vtkQuickTCGA::vtkQuickTCGA( )
  {
    SourceVol   = NULL;
    SeedVol   = NULL;
    SegVol = NULL;
    SCROIVol = NULL;
    m_qTCGASeg = NULL;

    otsuRatio = 1.0;
    curvatureWeight = 0.8;
    sizeThld = 3;
    sizeUpperThld = 200;
    mpp = 0.25;
    kernelSize = 15.0;
  }


  vtkQuickTCGA::~vtkQuickTCGA()
  {
    //these functions decrement reference count on the vtkImageData's (incremented by the SetMacros)
    if (this->SourceVol)
      {
        this->SetSourceVol(NULL);
      }
    if (this->SegVol)
      {
        this->SetSegVol(NULL);
      }

    if (this->SeedVol)
      {
        this->SetSeedVol(NULL);
      }
    if(this->SCROIVol)
      {
        this->SetSCROIVol(NULL);
      }
    if (m_qTCGASeg)
      {
        delete m_qTCGASeg;
      }
  }

  void vtkQuickTCGA::Initialization()
  {
    std::cout << "vtkQuickTCGA initialized\n";
    InitializationFlag = false;
    if(m_qTCGASeg == NULL)
      {
        m_qTCGASeg = new QuickTCGASegmenter();
      }
  }


  void vtkQuickTCGA::Run_QTCGA_Segmentation()
  {
    //Convert vtkImage to lplImage
    int dims[3];
    SourceVol->GetDimensions(dims);
    m_imSrc = cv::Mat(dims[1], dims[0], CV_8UC3);
    m_imLab = cv::Mat(dims[1], dims[0], CV_8UC1);

    TCGA::CopyImageVTK2OpenCV<uchar, uchar>(SourceVol, m_imSrc);
    TCGA::CopyImageVTK2OpenCV<short, uchar>(SeedVol, m_imLab);

    m_qTCGASeg->SetSourceImage(m_imSrc);
    m_qTCGASeg->SetLabImage(m_imLab);

    m_qTCGASeg->DoSegmentation();

    m_qTCGASeg->GetSegmentation(m_imLab);

    // Convert lplImage to vtkImage and update SeedVol
    TCGA::CopyImageOpenCV2VTK<uchar, short>(m_imLab, SeedVol);

    std::cout << "Finished TCGA segmentation\n";
  }

  void vtkQuickTCGA::Run_NucleiSegYi()
  {
    //Convert vtkImage to lplImage
    int dims[3];
    SourceVol->GetDimensions(dims);
    m_imSrc = cv::Mat(dims[1], dims[0], CV_8UC3);
    m_imLab = cv::Mat(dims[1], dims[0], CV_8UC1);

    TCGA::CopyImageVTK2OpenCV<uchar, uchar>(SourceVol, m_imSrc);
    TCGA::CopyImageVTK2OpenCV<short, uchar>(SeedVol, m_imLab);

    m_qTCGASeg->SetSourceImage(m_imSrc);
    m_qTCGASeg->SetLabImage(m_imLab);

    m_qTCGASeg->DoNucleiSegmentationYi(otsuRatio, curvatureWeight, sizeThld, sizeUpperThld, mpp, kernelSize);

    m_qTCGASeg->GetSegmentation(m_imLab);

    // Convert lplImage to vtkImage and update SeedVol
    TCGA::CopyImageOpenCV2VTK<uchar, short>(m_imLab, SeedVol);

    std::cout << "Finished TCGA segmentation\n";
  }

  void vtkQuickTCGA::Run_Refine_Curvature()
  {
    //Convert vtkImage to lplImage
    int dims[3];
    SourceVol->GetDimensions(dims);
    m_imSrc = cv::Mat(dims[1], dims[0], CV_8UC3);
    m_imLab = cv::Mat(dims[1], dims[0], CV_8UC1);

    TCGA::CopyImageVTK2OpenCV<uchar, uchar>(SourceVol, m_imSrc);
    TCGA::CopyImageVTK2OpenCV<short, uchar>(SeedVol, m_imLab);

    m_qTCGASeg->SetSourceImage(m_imSrc);
    m_qTCGASeg->SetLabImage(m_imLab);

    m_qTCGASeg->RefineCurvature();

    m_qTCGASeg->GetSegmentation(m_imLab);

    // Convert lplImage to vtkImage and update SeedVol
    TCGA::CopyImageOpenCV2VTK<uchar, short>(m_imLab, SeedVol);

    std::cout << "Finished TCGA refinement\n";
  }

  void vtkQuickTCGA::Run_QTCGA_Template()
  {
    std::cout << "Finished TCGA template matching\n";
  }

  void vtkQuickTCGA::PrintSelf(ostream &os, vtkIndent indent)
  {
    std::cout<<"This function has been found"<<std::endl;
  }

}

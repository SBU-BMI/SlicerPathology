#ifndef TCGAUtilities_h_
#define TCGAUtilities_h_

// std
#include <iostream>
#include <fstream>
#include <limits>

// itk
#include "itkImage.h"
#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"
#include "itkImportImageFilter.h"
//#include "itkVTKImageToImageFilter.h"
#include "itkImageRegionIteratorWithIndex.h"
#include "itkRegionOfInterestImageFilter.h"
#include "vtkImageData.h"
#include <vtkSmartPointer.h>


#include "opencv2/core/core.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <csignal>

#include "vtkSlicerQuickTCGAModuleLogicExport.h"

namespace TCGA
{

// template<typename itkImageType>
// typename itkImageType::Pointer createImage(typename itkImageType::SizeType size, int iniValue);

template<typename PixelType>
void FindVTKImageROI(vtkImageData* im, std::vector<long>& imROI);

template<typename PixelType>
void ExtractVTKImageROI(vtkImageData* im, const std::vector<long>& imROI, std::vector<PixelType>& imROIVec);

template<typename PixelType>
void UpdateVTKImageROI(const std::vector<PixelType>& imROIVec, const std::vector<long>& imROI,  vtkImageData* im);

template<typename ITKImageType>
void FindITKImageROI(typename ITKImageType::Pointer im, std::vector<long>& imROI);

template<typename PixelType>
void ExtractITKImageROI(typename itk::Image<PixelType, 3>::Pointer  im, const std::vector<long>& imROI, \
                        std::vector<PixelType>& imROIVec);

template<typename PixelType>
void UpdateITKImageROI(const std::vector<PixelType>& imROIVec, const std::vector<long>& imROI,  \
                       typename itk::Image<PixelType, 3>::Pointer im);

template<typename VTKPixelType, typename OpenCVPixelType>
void CopyImageVTK2OpenCV(const vtkSmartPointer<vtkImageData> imVTK, cv::Mat &imOpenCV);

template<typename OpenCVPixelType, typename VTKPixelType>
void CopyImageOpenCV2VTK(const cv::Mat &imOpenCV, vtkSmartPointer<vtkImageData> imVTK);



void VTK_SLICER_QUICKTCGA_MODULE_LOGIC_EXPORT
CopyImageVTK2OpenCV(const vtkSmartPointer<vtkImageData> imVTK, cv::Mat &imOpenCV);

void VTK_SLICER_QUICKTCGA_MODULE_LOGIC_EXPORT
CopyImageOpenCV2VTK(const cv::Mat &imOpenCV, vtkSmartPointer<vtkImageData> imVTK);

void VTK_SLICER_QUICKTCGA_MODULE_LOGIC_EXPORT
FindBoundingBoxFromMask(const cv::Mat& imMask, cv::Rect& rect);





  /**
   * readImage
   */
  template< typename itkImage_t >
  typename itkImage_t::Pointer readImage(const char *fileName)
  {
    typedef itk::ImageFileReader< itkImage_t > ImageReaderType;
    typename ImageReaderType::Pointer reader = ImageReaderType::New();
    reader->SetFileName(fileName);

    typename itkImage_t::Pointer image;

    try
      {
        reader->Update();
        image = reader->GetOutput();
      }
    catch ( itk::ExceptionObject &err)
      {
        std::cerr<< "ExceptionObject caught !" << std::endl;
        std::cerr<< err << std::endl;
        raise(SIGABRT);
      }

    return image;
  }

  /**
   * writeImage
   */
  template< typename itkImage_t > void writeImage(typename itkImage_t::Pointer img, const char *fileName)
  {
    typedef itk::ImageFileWriter< itkImage_t > WriterType;

    typename WriterType::Pointer writer = WriterType::New();
    writer->SetFileName( fileName );
    writer->SetInput(img);
    writer->UseCompressionOn();

    try
      {
        writer->Update();
      }
    catch ( itk::ExceptionObject &err)
      {
        std::cout << "ExceptionObject caught !" << std::endl;
        std::cout << err << std::endl;
        raise(SIGABRT);
      }
  }

   template<typename VType>
    void WriteVectorIntoFile(const char* fnSave, const std::vector<VType>& vec) {

        try{
            std::ofstream outfile(fnSave);
            outfile.write((const char *)&vec[0], vec.size()*sizeof(VType));
        }
        catch ( itk::ExceptionObject &err)
          {
            std::cout << "Fail to write to file " << fnSave << std::endl;
            std::cout << err << std::endl;
            raise(SIGABRT);
          }
    }

    template<typename VType>
     void LoadVectorIntoFile(const char* fnLoad, std::vector<VType>& vec, const long VEC_SIZE) {

          try{
             std::ifstream infile(fnLoad);
              vec.resize(VEC_SIZE);
              infile.read((char *)&vec[0], vec.size()*sizeof(VType));
         }
         catch ( itk::ExceptionObject &err)
           {
             std::cout << "Fail to load file " << fnLoad << std::endl;
             std::cout << err << std::endl;
             raise(SIGABRT);
           }
     }
}// douher

#include "TCGAUtilities.hxx"

#endif

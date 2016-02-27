#ifndef itkTypedefs_h_
#define itkTypedefs_h_

// openCV
#include <opencv2/opencv.hpp>


// itk
#include "itkImage.h"
#include "itkRGBPixel.h"


const unsigned int ImageDimension = 2;
typedef itk::Image<float, ImageDimension> itkFloatImageType;

typedef itk::RGBPixel<unsigned char> RGBPixelType;
typedef itk::Image<RGBPixelType, ImageDimension> itkRGBImageType;

typedef itk::Index<ImageDimension> itk2DIndexType;

typedef itk::Image<unsigned int, ImageDimension> itkUIntImageType;
typedef itk::Image<int, ImageDimension> itkIntImageType;

typedef itk::Image<unsigned char, ImageDimension> itkUCharImageType;
typedef itk::Image<char, ImageDimension> itkCharImageType;
typedef itkUCharImageType itkBinaryMaskImageType;

typedef itk::Image<unsigned short, ImageDimension> itkUShortImageType;
typedef itk::Image<short, ImageDimension> itkShortImageType;

typedef itk::Vector< float, 2 > itkVectorType;






#endif

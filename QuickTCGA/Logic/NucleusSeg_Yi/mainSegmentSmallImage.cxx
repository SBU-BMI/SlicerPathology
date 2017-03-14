#include <cstdio>
#include <iostream>
#include <string>


//itk
#include "itkImage.h"
#include "itkRGBPixel.h"
#include "itkImageFileWriter.h"
#include "itkOtsuThresholdImageFilter.h"
#include "itkCastImageFilter.h"
#include "itkOpenCVImageBridge.h"

// openslide

// openCV
#include <opencv2/opencv.hpp>


#include "Normalization.h"

#include "itkTypedefs.h"

#include "BinaryMaskAnalysisFilter.h"


#include "SFLSLocalChanVeseSegmentor2D.h"

#include "utilityTileAnalysis.h"
#include "utilityIO.h"


int main(int argc, char **argv)
{
  if (argc < 3)
	{
      std::cerr<<"Parameters: imageName outputPrefix mpp\n";
      exit(-1);
	}

  const int ImageDimension = 2;

  const char* fileName = argv[1];
  std::string outputPrefix(argv[2]);

  int optionalParameterStartIndex = 3;

  double mpp = 0.25; // usually for 40x, mpp is 0.25
  if (argc > optionalParameterStartIndex)
	{
      mpp = atof(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  //--------------------------------------------------------------------------------
  // When thresholding the hematoxylin channel, an optimization
  // process identify an "optimal" threshold. However, we can adjust
  // it by multiplying with this ratio. So, if we want to get fewer
  // nuclei, we lower this otsuRatio; and vice versa.
  //
  // range: > 0 [0.5, 1.5]

  float otsuRatio = 1.0;
  if (argc > optionalParameterStartIndex)
	{
      otsuRatio = atof(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  /*--------------------------------------------------------------------------------
    Higher value will cause smoother nuclear boundary.

    range: [0, 1]
    --------------------------------------------------------------------------------*/
  double curvatureWeight = 0.8;
  if (argc > optionalParameterStartIndex)
	{
      curvatureWeight = atof(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  /*--------------------------------------------------------------------------------
    nucleus smaller than this value will be regarded as noise and
    removed.

    range > 0 [1,20]
    --------------------------------------------------------------------------------*/
  float sizeThld = 3;
  if (argc > optionalParameterStartIndex)
	{
      sizeThld = atof(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  /*--------------------------------------------------------------------------------
    region larger than this value will be regarded as clump and
    de-clumped.

    range > 0 [50, 400,]
    --------------------------------------------------------------------------------*/
  float sizeUpperThld = 200;
  if (argc > optionalParameterStartIndex)
	{
      sizeUpperThld = atof(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  /*--------------------------------------------------------------------------------
    Declumping parameter. Smaller value results in smaller islands
    during de-clumping
    --------------------------------------------------------------------------------*/
  float msKernel = 20.0;
  if (argc > optionalParameterStartIndex)
	{
      msKernel = atof(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  /*--------------------------------------------------------------------------------
    Number of iterations of level set evolution
    --------------------------------------------------------------------------------*/
  int levelsetNumberOfIteration = 100;
  if (argc > optionalParameterStartIndex)
	{
          levelsetNumberOfIteration = atoi(argv[optionalParameterStartIndex]);
	}
  ++optionalParameterStartIndex;

  cv::Mat thisTile = imread(fileName);

  //itkUCharImageType::Pointer nucleusBinaryMask = itkUCharImageType::New();
  itkUShortImageType::Pointer outputLabelImage = itkUShortImageType::New();
  //cv::Mat outputLabelImageMat;
  //cv::Mat seg = processTile(thisTile, nucleusBinaryMask, outputLabelImage, outputLabelImageMat, otsuRatio, curvatureWeight, sizeThld, sizeUpperThld, mpp, msKernel);
  itkUCharImageType::Pointer nucleusBinaryMask = ImagenomicAnalytics::TileAnalysis::processTile<char>(thisTile, outputLabelImage, \
                                                                                                      otsuRatio, curvatureWeight, \
                                                                                                      sizeThld, sizeUpperThld, \
                                                                                                      mpp, msKernel, \
                                                                                                      levelsetNumberOfIteration);

//	cv::Mat seg = ImagenomicAnalytics::TileAnalysis::processTileCV(thisTile, otsuRatio, curvatureWeight, sizeThld, sizeUpperThld, mpp, msKernel);
//	imwrite("cv_mask.png",seg);

  std::string outputLabelName = outputPrefix.append("_label.png");
  ImagenomicAnalytics::IO::writeImage<itkUCharImageType>(nucleusBinaryMask, outputLabelName.c_str(), 0);

  //imwrite(outputLabelName, seg);


  return 0;
}

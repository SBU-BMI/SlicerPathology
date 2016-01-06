#include "itkPluginUtilities.h"

#include "NucleusSegmentationCLIModuleCLP.h"


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

#include "ProcessTileUtils.h"


int main( int argc, char * argv[] )
{
  PARSE_ARGS;

  std::string fn = "/home/liangjia/Dropbox/Doc/PathologySlicer/Data/Test/Data/TCGA-XJ-A9DX-01Z-00-DX1_appMag_40_29_38_small.png";

//  cv::Mat thisTile = imread(inputImageName);
   cv::Mat thisTile = imread(fn);
   cv::imwrite("/home/liangjia/Desktop/test.png", thisTile);
   std::cout << "save image to desk\n";

  cv::Mat seg = processTile(thisTile, otsuRatio, curvatureWeight, sizeThldLower, sizeThldUpper, mpp);

  cv::imwrite("/home/liangjia/Desktop/seg.png", seg);

  std::string outputLabelName = outputPrefix.append("_label.png");

  imwrite(outputLabelName, seg);

  return EXIT_SUCCESS;
}

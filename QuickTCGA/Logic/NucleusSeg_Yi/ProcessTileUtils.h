#ifndef ProcessTileUtils_h_
#define ProcessTileUtils_h_


#include <cstdio>
#include <iostream>
#include <string>

// openslide

// openCV
#include <opencv2/opencv.hpp>


cv::Mat processTile(cv::Mat thisTileCV, float otsuRatio = 1.0, double curvatureWeight = 0.8, float sizeThld = 3, float sizeUpperThld = 200, double mpp = 0.25, double ks = 15.0);

//template< typename itkImage_t > void writeImage(typename itkImage_t::Pointer img, const char *fileName, bool compress);

#endif

/*
 * PixelOperations.h
 *
 *  Created on: Aug 2, 2011
 *      Author: tcpan
 */

#ifndef PIXELOPERATIONS_H_
#define PIXELOPERATIONS_H_

#include "opencv2/opencv.hpp"
#include <stdio.h>
#include <stdlib.h>

using namespace cv;
using namespace std;

namespace nscale {

class PixelOperations {

public:

	template <typename T>
	static ::cv::Mat invert(const ::cv::Mat& img);

	template <typename T>
	static ::cv::Mat mod(::cv::Mat& img, T mod);

	static ::cv::Mat ComputeInverseStainMatrix(const Mat& M, const Mat& b);
	static ::std::vector<float> ComputeLookupTable();

	static void ColorDeconv( const Mat& image, const Mat& Q, const vector<float>& lut, Mat& H, Mat& E, bool BGR2RGB=true);
	static ::cv::Mat bgr2gray(const ::cv::Mat& img);

	template <typename T>
	static ::cv::Mat replace(const ::cv::Mat &img, T oldval, T newval);
};


}

#endif /* PIXELOPERATIONS_H_ */

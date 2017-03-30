/**
 * MorphologicOperation.h
 *
 *  Created on: Jul 7, 2011
 */
#ifndef MORPHOLOGICOPERATION_H_
#define MORPHOLOGICOPERATION_H_

#include "opencv/cv.hpp"

using namespace cv;

namespace nscale {

    /**
     * DOES NOT WORK WITH MULTICHANNEL.
     */
    template<typename T>
    cv::Mat imreconstruct(const cv::Mat &seeds, const cv::Mat &image, int connectivity);

    cv::Mat_<int> bwlabel2(const cv::Mat &binaryImage, int connectivity, bool relab);

    cv::Mat
    bwareaopen2(const cv::Mat &binaryImage, bool labeled, bool flatten, int minSize, int maxSize, int connectivity,
                int &count);

    template<typename T>
    cv::Mat imhmin(const cv::Mat &image, T h, int connectivity);

    cv::Mat_<int> watershed2(const cv::Mat &origImage, const cv::Mat_<float> &image, int connectivity);

    template<typename T>
    cv::Mat_<unsigned char> localMaxima(const cv::Mat &image, int connectivity);

    template<typename T>
    cv::Mat_<unsigned char> localMinima(const cv::Mat &image, int connectivity);
}

#endif /* MORPHOLOGICOPERATION_H_ */


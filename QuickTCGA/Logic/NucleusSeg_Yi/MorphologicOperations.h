/**
 * MorphologicOperations.h
 *
 *  Created on: Jul 7, 2011
 */
#ifndef MORPHOLOGICOPERATION_H_
#define MORPHOLOGICOPERATION_H_

/*
// not using:
#ifdef _MSC_VER
#define DllExport __declspec(dllexport)
#else
#define DllExport //nothing
#endif
*/

#include "opencv/cv.hpp"

/*
// HIDE GPU
#ifdef WITH_CUDA
#include "opencv2/gpu/gpu.hpp"
#endif
*/

using namespace cv;
/*
// HIDE GPU
#ifdef WITH_CUDA
using namespace cv::gpu;
#endif
*/

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

    /*
    // OMITTING UNUSED FUNCTIONS...
    */

    /*
    // HIDE GPU
    #ifdef WITH_CUDA
    namespace gpu {
      // GPU versions of the same functions.
    }
    #endif
    */

}

#endif /* MORPHOLOGICOPERATION_H_ */

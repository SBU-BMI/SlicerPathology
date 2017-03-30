/*
 * HistologicalEntities.h
 */
#ifndef HistologicalEntities_H_
#define HistologicalEntities_H_

#include <string.h>
#include "opencv2/opencv.hpp"

namespace nscale {

class HistologicalEntities {

public:
    static const int CONTINUE = 4;
    static int plSeparateNuclei(const cv::Mat& img, const cv::Mat& seg_open, cv::Mat& seg_nonoverlap);
};

}
#endif /* HistologicalEntities_H_ */


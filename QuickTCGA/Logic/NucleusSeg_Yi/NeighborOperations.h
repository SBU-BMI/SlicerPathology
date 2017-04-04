/**
 * ScanlineOperations.h
 *
 *  Created on: Aug 2, 2011
 *      Author: tcpan
 */
#ifndef NEIGHBOROPERATIONS_H_
#define NEIGHBOROPERATIONS_H_

#include "cv.h"

namespace nscale {

    class NeighborOperations {

    public:
        // Fixes watershed borders.
        template<typename T>
        static ::cv::Mat border(::cv::Mat &img, T background);
    };

}

#endif /* NEIGHBOROPERATIONS_H_ */

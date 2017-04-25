/**
 * MorphologicOperations.cpp
 *
 *  Created on: Jul 7, 2011
 *
 */
#include <algorithm>
#include <queue>
#include <iostream>
#include <limits>
//#include <omp.h>  // not using
#include "highgui.h"
//#include "Logger.h"  // not using
#include "TypeUtils.h"
#include "MorphologicOperations.h"
#include "PixelOperations.h"
#include "NeighborOperations.h"
#include "ConnComponents.h"

using namespace cv;
//using namespace cv::gpu;  // HIDE GPU
using namespace std;

namespace nscale {

    template<typename T>
    inline void propagate(const Mat &image, Mat &output, std::queue<int> &xQ, std::queue<int> &yQ,
                          int x, int y, T *iPtr, T *oPtr, const T &pval) {

        T qval = oPtr[x];
        T ival = iPtr[x];
        if ((qval < pval) && (ival != qval)) {
            oPtr[x] = min(pval, ival);
            xQ.push(x);
            yQ.push(y);
        }
    }

    template
    void propagate(const Mat &, Mat &, std::queue<int> &, std::queue<int> &,
                   int, int, unsigned char *iPtr, unsigned char *oPtr, const unsigned char &);

    template
    void propagate(const Mat &, Mat &, std::queue<int> &, std::queue<int> &,
                   int, int, float *iPtr, float *oPtr, const float &);

    /**
     * Slightly optimized serial implementation,
     * from Vincent paper on "Morphological Grayscale Reconstruction in Image Analysis: Applicaitons and Efficient Algorithms"
     * This is the fast hybrid grayscale reconstruction
     * Connectivity is either 4 or 8, default 4.
     * This is slightly optimized by avoiding conditional where possible.
     */
    template<typename T>
    Mat imreconstruct(const Mat &seeds, const Mat &image, int connectivity) {
        CV_Assert(image.channels() == 1);
        CV_Assert(seeds.channels() == 1);

        Mat output(seeds.size() + Size(2, 2), seeds.type());
        copyMakeBorder(seeds, output, 1, 1, 1, 1, BORDER_CONSTANT, 0);
        Mat input(image.size() + Size(2, 2), image.type());
        copyMakeBorder(image, input, 1, 1, 1, 1, BORDER_CONSTANT, 0);

        T pval, preval;
        int xminus, xplus, yminus, yplus;
        int maxx = output.cols - 1;
        int maxy = output.rows - 1;
        std::queue<int> xQ;
        std::queue<int> yQ;
        T *oPtr;
        T *oPtrMinus;
        T *oPtrPlus;
        T *iPtr;
        T *iPtrPlus;
        T *iPtrMinus;

        // uint64_t t1 = cci::common::event::timestampInUS();

        // Raster scan
        for (int y = 1; y < maxy; ++y) {

            oPtr = output.ptr<T>(y);
            oPtrMinus = output.ptr<T>(y - 1);
            iPtr = input.ptr<T>(y);

            preval = oPtr[0];
            for (int x = 1; x < maxx; ++x) {
                xminus = x - 1;
                xplus = x + 1;
                pval = oPtr[x];

                // Walk through the neighbor pixels, left and up (N+(p)) only
                pval = max(pval, max(preval, oPtrMinus[x]));

                if (connectivity == 8) {
                    pval = max(pval, max(oPtrMinus[xplus], oPtrMinus[xminus]));
                }
                preval = min(pval, iPtr[x]);
                oPtr[x] = preval;
            }
        }

        // Anti-raster scan
        int count = 0;
        for (int y = maxy - 1; y > 0; --y) {
            oPtr = output.ptr<T>(y);
            oPtrPlus = output.ptr<T>(y + 1);
            oPtrMinus = output.ptr<T>(y - 1);
            iPtr = input.ptr<T>(y);
            iPtrPlus = input.ptr<T>(y + 1);

            preval = oPtr[maxx];
            for (int x = maxx - 1; x > 0; --x) {
                xminus = x - 1;
                xplus = x + 1;

                pval = oPtr[x];

                // Walk through the neighbor pixels, right and down (N-(p)) only
                pval = max(pval, max(preval, oPtrPlus[x]));

                if (connectivity == 8) {
                    pval = max(pval, max(oPtrPlus[xplus], oPtrPlus[xminus]));
                }

                preval = min(pval, iPtr[x]);
                oPtr[x] = preval;

                // Capture the seeds
                // Walk through the neighbor pixels, right and down (N-(p)) only
                pval = oPtr[x];

                if ((oPtr[xplus] < min(pval, iPtr[xplus])) || (oPtrPlus[x] < min(pval, iPtrPlus[x]))) {
                    xQ.push(x);
                    yQ.push(y);
                    ++count;
                    continue;
                }

                if (connectivity == 8) {
                    if ((oPtrPlus[xplus] < min(pval, iPtrPlus[xplus])) ||
                        (oPtrPlus[xminus] < min(pval, iPtrPlus[xminus]))) {
                        xQ.push(x);
                        yQ.push(y);
                        ++count;
                        continue;
                    }
                }
            }
        }

        // uint64_t t2 = cci::common::event::timestampInUS();
        // std::cout << "    scan time = " << t2-t1 << "ms for " << count << " queue entries."<< std::endl;

        // Now process the queue.
        // T qval, ival;
        int x, y;
        count = 0;
        while (!(xQ.empty())) {
            ++count;
            x = xQ.front();
            y = yQ.front();
            xQ.pop();
            yQ.pop();
            xminus = x - 1;
            xplus = x + 1;
            yminus = y - 1;
            yplus = y + 1;

            oPtr = output.ptr<T>(y);
            oPtrPlus = output.ptr<T>(yplus);
            oPtrMinus = output.ptr<T>(yminus);
            iPtr = input.ptr<T>(y);
            iPtrPlus = input.ptr<T>(yplus);
            iPtrMinus = input.ptr<T>(yminus);

            pval = oPtr[x];

            // Look at the 4 connected components
            if (y > 0) {
                propagate<T>(input, output, xQ, yQ, x, yminus, iPtrMinus, oPtrMinus, pval);
            }
            if (y < maxy) {
                propagate<T>(input, output, xQ, yQ, x, yplus, iPtrPlus, oPtrPlus, pval);
            }
            if (x > 0) {
                propagate<T>(input, output, xQ, yQ, xminus, y, iPtr, oPtr, pval);
            }
            if (x < maxx) {
                propagate<T>(input, output, xQ, yQ, xplus, y, iPtr, oPtr, pval);
            }

            // Now 8 connected
            if (connectivity == 8) {

                if (y > 0) {
                    if (x > 0) {
                        propagate<T>(input, output, xQ, yQ, xminus, yminus, iPtrMinus, oPtrMinus, pval);
                    }
                    if (x < maxx) {
                        propagate<T>(input, output, xQ, yQ, xplus, yminus, iPtrMinus, oPtrMinus, pval);
                    }
                }
                if (y < maxy) {
                    if (x > 0) {
                        propagate<T>(input, output, xQ, yQ, xminus, yplus, iPtrPlus, oPtrPlus, pval);
                    }
                    if (x < maxx) {
                        propagate<T>(input, output, xQ, yQ, xplus, yplus, iPtrPlus, oPtrPlus, pval);
                    }
                }
            }
        }

        //	uint64_t t3 = cci::common::event::timestampInUS();
        //	std::cout << "    queue time = " << t3-t2 << "ms for " << count << " queue entries "<< std::endl;

        //	std::cout <<  count << " queue entries "<< std::endl;

        return output(Range(1, maxy), Range(1, maxx));
    }

    /**
     * Operates on BINARY IMAGES ONLY.
     * Perform bwlabel using union-find.
     */
    Mat_<int> bwlabel2(const Mat &binaryImage, int connectivity, bool relab) {
        CV_Assert(binaryImage.channels() == 1);
        // Only works for binary images.
        CV_Assert(binaryImage.type() == CV_8U);

        // Copy, to make data continuous.
        Mat input = Mat::zeros(binaryImage.size(), binaryImage.type());
        binaryImage.copyTo(input);

        ConnComponents cc;
        Mat_<int> output = Mat_<int>::zeros(input.size());
        cc.label((unsigned char *) input.data, input.cols, input.rows, (int *) output.data, -1, connectivity);

        // Relabel if requested
        int j = 0;
        if (relab == true) {
            j = cc.relabel(output.cols, output.rows, (int *) output.data, -1);
            // printf("%d number of components\n", j);
        }

        input.release();

        return output;
    }

    /**
     * Inclusive min, exclusive max
     */
    Mat
    bwareaopen2(const Mat &image, bool labeled, bool flatten, int minSize, int maxSize, int connectivity, int &count) {
        // Only works for binary images.
        CV_Assert(image.channels() == 1);
        // Only works for binary images.
        if (labeled == false)
            CV_Assert(image.type() == CV_8U);
        else
            CV_Assert(image.type() == CV_32S);

        // Copy, to make data continuous.
        Mat input = Mat::zeros(image.size(), image.type());
        image.copyTo(input);
        Mat_<int> output = Mat_<int>::zeros(input.size());

        ConnComponents cc;
        if (labeled == false) {
            Mat_<int> temp = Mat_<int>::zeros(input.size());
            cc.label((unsigned char *) input.data, input.cols, input.rows, (int *) temp.data, -1, connectivity);
            count = cc.areaThresholdLabeled((int *) temp.data, temp.cols, temp.rows, (int *) output.data, -1, minSize,
                                            maxSize);
            temp.release();
        } else {
            count = cc.areaThresholdLabeled((int *) input.data, input.cols, input.rows, (int *) output.data, -1,
                                            minSize, maxSize);
        }

        input.release();
        if (flatten == true) {
            Mat O2 = Mat::zeros(output.size(), CV_8U);
            O2 = output > -1;
            output.release();
            return O2;
        } else
            return output;
    }

    template<typename T>
    Mat imhmin(const Mat &image, T h, int connectivity) {
        // Only works for intensity images.
        CV_Assert(image.channels() == 1);

        /**
         * IMHMIN(I,H) suppresses all minima in I whose depth is less than h
         *
         * MatLAB implementation:
         * I = imcomplement(I);
         * I2 = imreconstruct(imsubtract(I,h), I, conn);
         * I2 = imcomplement(I2);
         */

        Mat mask = nscale::PixelOperations::invert<T>(image);
        Mat marker = mask - h;
        // imwrite("in-imrecon-float-marker.exr", marker);
        // imwrite("in-imrecon-float-mask.exr", mask);

        Mat output = imreconstruct<T>(marker, mask, connectivity);
        return nscale::PixelOperations::invert<T>(output);
    }

    /**
     * Input should have foreground > 0, and 0 for background
     */
    Mat_<int> watershed2(const Mat &origImage, const Mat_<float> &image, int connectivity) {
        // Only works for intensity images.
        CV_Assert(image.channels() == 1);
        CV_Assert(origImage.channels() == 3);

        /**
         * MatLAB implementation:
         * cc = bwconncomp(imregionalmin(A, conn), conn);
         * L = watershed_meyer(A,conn,cc);
         */
        Mat minima = localMinima<float>(image, connectivity);

        // Watershed is sensitive to label values.  Need to relabel.
        Mat_<int> labels = bwlabel2(minima, connectivity, true);

        // Need borders, else get edges at edge.
        Mat input, temp, output;
        copyMakeBorder(labels, temp, 1, 1, 1, 1, BORDER_CONSTANT, Scalar_<int>(0));
        copyMakeBorder(origImage, input, 1, 1, 1, 1, BORDER_CONSTANT, Scalar(0, 0, 0));

        // INPUT: seeds are labeled from 1 to n, with 0 as background or unknown regions
        // OUTPUT: has -1 as borders.
        watershed(input, temp);

        output = nscale::NeighborOperations::border<int>(temp, (int) -1);

        return output(Rect(1, 1, image.cols, image.rows));
    }

    /**
     * Only works with integer images
     */
    template<typename T>
    Mat_<unsigned char> localMaxima(const Mat &image, int connectivity) {
        CV_Assert(image.channels() == 1);

        // Use morphological reconstruction.
        Mat marker = image - 1;
        Mat_<unsigned char> candidates = marker < imreconstruct<T>(marker, image, connectivity);
        // Candidates marked as 0 because flood fill with mask will fill only 0's
        // return (image - imreconstruct(marker, image, 8)) >= (1 - std::numeric_limits<T>::epsilon());
        // return candidates;

        // Now check the candidates
        // First pad the border
        T mn = cci::common::type::min<T>();
        T mx = std::numeric_limits < unsigned
        char > ::max();
        Mat_<unsigned char> output(candidates.size() + Size(2, 2));
        copyMakeBorder(candidates, output, 1, 1, 1, 1, BORDER_CONSTANT, mx);
        Mat input(image.size() + Size(2, 2), image.type());
        copyMakeBorder(image, input, 1, 1, 1, 1, BORDER_CONSTANT, mn);

        int maxy = input.rows - 1;
        int maxx = input.cols - 1;
        int xminus, xplus;
        T val;
        T *iPtr, *iPtrMinus, *iPtrPlus;
        unsigned char *oPtr;
        Rect reg(1, 1, image.cols, image.rows);
        Scalar zero(0);
        Scalar smx(mx);
        // Range xrange(1, maxx);
        // Range yrange(1, maxy);
        Mat inputBlock = input(reg);

        // Next, iterate over image and set candidates that are non-max to 0 (via floodfill)
        for (int y = 1; y < maxy; ++y) {

            iPtr = input.ptr<T>(y);
            iPtrMinus = input.ptr<T>(y - 1);
            iPtrPlus = input.ptr<T>(y + 1);
            oPtr = output.ptr < unsigned
            char > (y);

            for (int x = 1; x < maxx; ++x) {

                // Not a candidate; continue.
                if (oPtr[x] > 0)
                    continue;

                xminus = x - 1;
                xplus = x + 1;

                val = iPtr[x];
                // Compare values

                // 4 connected
                if ((val < iPtrMinus[x]) || (val < iPtrPlus[x]) || (val < iPtr[xminus]) || (val < iPtr[xplus])) {
                    // Flood with type minimum value (only time when the whole image may have mn is if it's flat)
                    floodFill(inputBlock, output, Point(xminus, y - 1), smx, &reg, zero, zero,
                              FLOODFILL_FIXED_RANGE | FLOODFILL_MASK_ONLY | connectivity);
                    continue;
                }

                // 8 connected
                if (connectivity == 8) {
                    if ((val < iPtrMinus[xminus]) || (val < iPtrMinus[xplus]) || (val < iPtrPlus[xminus]) ||
                        (val < iPtrPlus[xplus])) {
                        // Flood with type minimum value (only time when the whole image may have mn is if it's flat)
                        floodFill(inputBlock, output, Point(xminus, y - 1), smx, &reg, zero, zero,
                                  FLOODFILL_FIXED_RANGE | FLOODFILL_MASK_ONLY | connectivity);
                        continue;
                    }
                }
            }
        }
        return output(reg) == 0; // Similar to bitwise NOT.
    }

    template<typename T>
    Mat_<unsigned char> localMinima(const Mat &image, int connectivity) {
        // Only works for intensity images.
        CV_Assert(image.channels() == 1);

        Mat cimage = nscale::PixelOperations::invert<T>(image);
        return localMaxima<T>(cimage, connectivity);
    }

    template Mat imhmin(const Mat &image, unsigned char h, int connectivity);

    template Mat imhmin(const Mat &image, float h, int connectivity);
}

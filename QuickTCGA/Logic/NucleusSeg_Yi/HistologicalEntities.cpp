/**
 * HistologicalEntities
 */
#include <limits>
#include "HistologicalEntities.h"
#include <iostream>
#include "MorphologicOperations.h"
#include "NeighborOperations.h"
#include "PixelOperations.h"
#include "highgui.h"
#include "float.h"
//#include "Logger.h"
#include "ConnComponents.h"

namespace nscale {

using namespace cv;

// Passing in: (newImgCV, seg, watershedMask)
int HistologicalEntities::plSeparateNuclei(const Mat& img, const Mat& seg_open, Mat& seg_nonoverlap)
{
    /**
     * Remove small objects from binary image.
     * bwareaopen is done as a area threshold.
     */
    int compcount2;
    Mat seg_big_t = ::nscale::bwareaopen2(seg_open, false, true, 30, std::numeric_limits<int>::max(), 8, compcount2);
    // printf(" cpu compcount 30-1000 = %d\n", compcount2);

    Mat disk3 = getStructuringElement(MORPH_ELLIPSE, Size(3, 3));

    Mat seg_big = Mat::zeros(seg_big_t.size(), seg_big_t.type());
    dilate(seg_big_t, seg_big, disk3);
    // imwrite("test/out-nucleicandidatesbig.ppm", seg_big);

    /***
     * DISTANCE TRANSFORM:  Matlab code is doing this:
     * Invert the image so nuclear candidates are holes
     * Compute the distance (distance of nuclei pixels to background)
     * Negate the distance.  So now background is still 0, but nuclei pixels have negative distances
     * Set background to -inf
     * Really just want the distance map.  CV computes distance to 0.
     * Background is 0 in output.
     * Then invert to create basins
     */
    Mat dist(seg_big.size(), CV_32FC1);
    // imwrite("seg_big.pbm", seg_big);

    /**
     * OPENCV: compute the distance to nearest zero
     * MATLAB: compute the distance to the nearest non-zero
     */
    distanceTransform(seg_big, dist, CV_DIST_L2, CV_DIST_MASK_PRECISE);
    double mmin, mmax;
    minMaxLoc(dist, &mmin, &mmax);

    // Invert and shift (make sure it's still positive)
    // dist = (mmax + 1.0) - dist;
    dist = -dist; // appears to work better this way.
    // cciutils::cv::imwriteRaw("test/out-dist", dist);

    /**
     * Then set the background to -inf and do imhmin
     * // Mat distance = Mat::zeros(dist.size(), dist.type());
     * Appears to work better with -inf as background
     */
    Mat distance(dist.size(), dist.type(), -std::numeric_limits<float>::max());
    dist.copyTo(distance, seg_big);
    // cciutils::cv::imwriteRaw("test/out-distance", distance);

    /**
     * Then do imhmin. (prevents small regions inside bigger regions)
     * // imwrite("in-imhmin.ppm", distance);
     */
    Mat distance2 = ::nscale::imhmin<float>(distance, 1.0f, 8);
    // imwrite("distance2.ppm", dist);
    // cciutils::cv::imwriteRaw("test/out-distanceimhmin", distance2);

    Mat nuclei = Mat::zeros(img.size(), img.type());
    img.copyTo(nuclei, seg_big);

    /**
     * Watershed in OpenCV requires labels.  Input foreground > 0, 0 is background.
     * Critical to use just the nuclei and not the whole image - else get a ring surrounding the regions.
     */
    Mat watermask = ::nscale::watershed2(nuclei, distance2, 8);
    // cciutils::cv::imwriteRaw("test/out-watershed", watermask);

    // MASK approach:
    seg_nonoverlap = Mat::zeros(seg_big.size(), seg_big.type());
    seg_big.copyTo(seg_nonoverlap, (watermask >= 0));

    /**
     * ERODE to fix border.
     * ...
     * // erode(twm, t_nonoverlap, disk3);
     * ...
     * ERODE has since been replaced with border finding and moved into watershed.
     * ...
     * LABEL approach -erode does not support 32S
     * // seg_nonoverlap = ::nscale::PixelOperations::replace<int>(watermask, (int)0, (int)-1);
     * Watershed output: 0 for background, -1 for border.  bwlabel before watershd has 0 for background.
     */

    return ::nscale::HistologicalEntities::CONTINUE;
}
}


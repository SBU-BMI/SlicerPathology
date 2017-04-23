/**
 * ConnComponents.cpp
 *
 *  Created on: Feb 20, 2012
 *      Author: tcpan
 */
#include "ConnComponents.h"
#include <string.h>
/*
#if defined(__has_include)
#if __has_include("unordered_map.h") // Windows
# include <unordered_map>
#endif
#if __has_include("tr1/unordered_map.h") // Linux
# include <tr1/unordered_map>
using namespace std::tr1;
#endif
#endif
*/
namespace nscale {

    ConnComponents::ConnComponents() {
        // TODO Auto-generated constructor stub
    }

    ConnComponents::~ConnComponents() {
        // TODO Auto-generated destructor stub
    }

    int ConnComponents::find(int *label, int x) {
        if (label[x] == x) {
            return x;
        } else {
            int v = find(label, label[x]);
            label[x] = v;
            return v;
        }
    }

    void ConnComponents::merge(int *label, int x, int y) {
        x = find(label, x);
        y = find(label, y);

        if (label[x] < label[y]) {
            label[y] = x;
        } else if (label[x] > label[y]) {
            label[x] = y;
        }
    }


    /**
     * Adapted from the brazilian cpu union-find CCL.
     * 2 sets of improvements:
     *      2. use a nested loop instead of x and y - avoids % and /.  also increment i, and precompute i-w, and preload img[i].
     * above does not seem to create a big reduction (about 50ms).  timing for sizePhantom is between 1.1 and 1.3 sec.  for astroII.1's mask, about 1.1 sec.
     *      3. early termination - if background, don't go through the merge.  - significant savings.  - down to for size phantom, down to about 300ms.
     * with astroII.1's mask, about 60 ms.  faster than contour based.
     */
    void ConnComponents::label(unsigned char *img, int w, int h, int *label, int bgval, int connectivity) {
        int length = w * h;

        // Initialize
        for (int i = 0; i < length; ++i) {
            label[i] = i;
        }

        // Do the labelling
        int i = -1, imw = 0;
        unsigned char p;
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w; ++x) {
                ++i;
                p = img[i];
                if (p == 0) {
                    label[i] = bgval;
                } else {
                    imw = i - w;
                    if (x > 0 && p == img[i - 1]) merge(label, i, i - 1);
                    if (y > 0 && p == img[imw]) merge(label, i, imw);
                    if (connectivity == 8) {
                        if (y > 0 && x > 0 && p == img[imw - 1]) merge(label, i, imw - 1);
                        if (y > 0 && x < w - 1 && p == img[imw + 1]) merge(label, i, imw + 1);
                    }
                }
            }
        }

        // Final flatten
        for (int i = 0; i < length; ++i) {
            label[i] = flatten(label, i, bgval);
        }

    }

    /**
     * Relabelling to get sequential labels.  assumes labeled image is flattened with background set to bgval
     */
    int ConnComponents::relabel(int w, int h, int *label, int bgval) {
        int length = w * h;
        // unordered_map<int, int> labelmap;
        std::tr1::unordered_map<int, int> labelmap;

        int j = 1;
        // First find the roots
        labelmap[bgval] = 0;
        for (int i = 0; i < length; ++i) {
            if (label[i] == i) {
                // Root. Record its value
                labelmap[i] = j;
                // printf("root: %d: %d\n", j, i);
                ++j;
            }
        }


        // Debug
        // printf("labels = ");
        // for (std::tr1::unordered_map<int, int>::iterator iter = labelmap.begin(); iter != labelmap.end(); ++iter) {
        //     printf("%d->%d ", iter->first, iter->second);
        // }
        // printf("\n");


        // Next do a one pass value change.
        for (int i = 0; i < length; ++i) {
            label[i] = labelmap[label[i]];
        }
        return j - 1;
    }

    int ConnComponents::flatten(int *label, int x, int bgval) {
        if (label[x] == bgval) {
            return bgval;
        } else if (label[x] == x) {
            return x;
        } else {
            int v = flatten(label, label[x], bgval);
            label[x] = v;
            return v;
        }
    }


    int ConnComponents::areaThresholdLabeled(const int *label, const int w, const int h, int *n_label, const int bgval,
                                             const int lower, const int upper) {
        int length = w * h;
        // typedef unordered_map<int, int> AreaMap;
        typedef std::tr1::unordered_map<int, int> AreaMap;
        AreaMap areas, thresholdedareas;

        for (int i = 0; i < length; ++i) {
            if (label[i] != bgval) {  // Not background, then increment area
                areas[label[i]] += 1;
            }
            // Initialize output
            n_label[i] = bgval;
        }

        int j = 0;
        // Count ones that are within threshold
        for (AreaMap::iterator it = areas.begin();
             it != areas.end(); ++it) {
            if (it->second >= lower && it->second < upper) {
                thresholdedareas[it->first] = 1;
                ++j;
            } else {
                thresholdedareas[it->first] = 0;
            }
        }
        areas.clear();

        // TONY finally do the threshold and change the value of the
        for (int i = 0; i < length; ++i) {
            // Look at the roots
            if (label[i] != bgval && thresholdedareas[label[i]] == 1) n_label[i] = label[i];
        }

        thresholdedareas.clear();
        return j;
    }

}

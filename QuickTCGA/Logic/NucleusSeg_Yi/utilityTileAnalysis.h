#ifndef utilitiesTileAnalysis_h_
#define utilitiesTileAnalysis_h_
namespace ImagenomicAnalytics {
    namespace TileAnalysis {
        cv::Mat processTileCV(cv::Mat thisTileCV, \
                          float otsuRatio = 1.0, \
                          double curvatureWeight = 0.8, \
                          float sizeThld = 3, \
                          float sizeUpperThld = 200, \
                          double mpp = 0.25, \
                          float msKernel = 20.0, \
                          int levelsetNumberOfIteration = 100,
                          int seg_type = 0);
    }
}
#endif

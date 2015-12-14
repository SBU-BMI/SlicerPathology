#ifndef SHORTCUT_H
#define SHORTCUT_H

#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <cstdio>
#include <cstring>
#include <list>

const cv::Scalar RED = cv::Scalar(0,0,255);
const cv::Scalar BLUE = cv::Scalar(255,0,0);
const cv::Scalar GREEN = cv::Scalar(0,255,0);
const cv::Scalar YELLOW = cv::Scalar(0, 255, 255);
const cv::Scalar CYAN = cv::Scalar(255, 255, 0);
const int INPUT_KEY = cv::EVENT_FLAG_CTRLKEY;

struct DKElement;

class ShortCut {

public:
    ShortCut();
    ~ShortCut();
    void ReSet();

    void MouseClick( int event, int x, int y, int flags);
    void SetSourceImage(const cv::Mat& imSrc, const cv::Mat& imSeed);
    void ShowImage(bool bPoly = false);
    void DoSegmentation();
    void GetSegmentation(cv::Mat& imSeg);
    void FindNNPolyPoint(const int x, const int y);
    void UpdatePolyGon();

    enum{ NOT_SET = 0, IN_PROCESS = 1, SET = 2 };

private:
    void UpdateSegmentation();
    void IniImSeedFromSeg();

    static const int m_RAD = 1;
    static const int m_THICKNESS = 1;
    static const int m_INDNON = 0;
    static const int m_INDFGD = 1;
    static const int m_INDBGD = 2;
    cv::Scalar m_INDFGD_COLOR;
    cv::Scalar m_INDBGD_COLOR;
    cv::Scalar m_INDNON_COLOR;

    cv::Mat m_imSrc;
    cv::Mat m_imSeed;
    cv::Mat m_imSeg;
    cv::Mat m_imROI;
    cv::Mat m_imROIBoundary;
    std::string m_WinName;
    bool m_bIsInitialized;
    bool m_bShortCut;
    bool m_bManualEdit;
    uchar m_lBtState, m_rBtState;

    std::vector<cv::Point> m_fgdPxls, m_bgdPxls;
    std::vector<std::vector<cv::Point> > m_polys;
    std::vector<int> m_indPolySelect;

    std::vector<uchar> m_labPre;
    std::vector<double> m_distPre;
    DKElement* m_pDK;
};

#endif // SHORTCUT_H

#include "QuickTCGASegmenter.h"

static void On_TrackColorThreshold(int indColorTh, void* userData) {

    QuickTCGASegmenter* pTCGA = static_cast<QuickTCGASegmenter*>(userData);
    pTCGA->OnTrackColorThreshold(indColorTh);
}

QuickTCGASegmenter::QuickTCGASegmenter() {
    m_WindowNameFull = "Segmentation_Full";
    m_WindowNameROI = "Segmentation_ROI";
}

QuickTCGASegmenter::~QuickTCGASegmenter(){;}

void QuickTCGASegmenter::OnTrackColorThreshold(int indColorTh) {

    cv::Mat dst;

    double cTh= (double)indColorTh/m_COLOR_SLIDER_MAX;

    cv::threshold(m_imFeature, dst, cTh*255, 255, CV_THRESH_BINARY_INV);

    int erosion_size = m_STRELE_SIZE;
    cv::Mat element = cv::getStructuringElement(cv::MORPH_CROSS,
                          cv::Size(2 * erosion_size + 1, 2 * erosion_size + 1),
                          cv::Point(erosion_size, erosion_size) );

    cv::dilate(dst, dst, element);
    cv::erode(dst, dst, element);

    // Fill holes
    std::vector<std::vector<cv::Point> > contours;
    std::vector<cv::Vec4i> hierarchy;

    cv::findContours(dst,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE,cv::Point(0,0));
    cv::Scalar color=cv::Scalar(255);

    for(unsigned int i=0;i<contours.size();i++) {
      drawContours(dst,contours,i,color,-1,8,hierarchy,0,cv::Point());
    }

    // Draw contours over source image
    findContours(dst,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE,cv::Point(0,0));

    for (std::vector<std::vector<cv::Point> >::iterator it = contours.begin(); it!=contours.end(); )
    {
        if (cv::contourArea(*it) < m_COUNTOURAREA_MIN)
            it=contours.erase(it);
        else
            ++it;
    }
    color = cv::Scalar(0,255,0);


    cv::Mat srcDraw = m_imSrcSample.clone();
    for(unsigned int i=0;i<contours.size();i++) {
        drawContours(srcDraw,contours,i,color,1,8,hierarchy,0,cv::Point());
    }

    m_contours = contours;
    m_hierarchy = hierarchy;

    cv::imshow(m_WindowNameFull, srcDraw);
}


void QuickTCGASegmenter::SetSourceImage(const cv::Mat& imSrc) {
    m_imSrc = imSrc;
}

void QuickTCGASegmenter::SetLabImage(const cv::Mat& imLab) {
    m_imLab = imLab;
}

void QuickTCGASegmenter::SetROIImage(const cv::Mat &imROI) {
    m_imROI = imROI;
}

void QuickTCGASegmenter::SetPreSegmentation(const cv::Mat& imPreSeg) {
    m_imSegPre = imPreSeg.clone();
}

void QuickTCGASegmenter::GetSegmentation(cv::Mat& imSeg) {
    imSeg = m_imLab;
}

void QuickTCGASegmenter::ComputeFeatureImage() {

    std::vector<cv::Mat> imBGR;

    cv::split(m_imSrcSample, imBGR);
    cv::Scalar meanColor;
    meanColor = cv::mean(m_imSrcSample, m_imLabSample);
    cv::normalize(meanColor, meanColor);

    for(int i = 0; i < 3; i++)
        imBGR[i].convertTo( imBGR[i], CV_32F);

    m_imFeature = imBGR[0]*meanColor[0] + imBGR[1]*meanColor[1] + imBGR[2]*meanColor[2];

    double ftMin, ftMax;
    cv::minMaxLoc( m_imFeature, &ftMin, &ftMax);

    m_imFeature = (m_imFeature - ftMin)/(ftMax - ftMin)*255;
    m_imFeature.convertTo(m_imFeature, CV_8UC1);
}

void QuickTCGASegmenter::DoSegmentation() {

    // Resize image for higher efficiency
     cv::resize(m_imSrc, m_imSrcSample, cv::Size(m_imSrc.cols*m_SAMPLERATE, m_imSrc.rows*m_SAMPLERATE), cv::INTER_LINEAR);
     cv::resize(m_imLab, m_imLabSample, cv::Size(m_imLab.cols*m_SAMPLERATE, m_imLab.rows*m_SAMPLERATE), cv::INTER_NEAREST);


      // Compute feature image
     ComputeFeatureImage();

     cv::Scalar colorTh;
     int indColorTh;
     colorTh = cv::mean(m_imFeature);
     indColorTh = colorTh[0]/255*m_COLOR_SLIDER_MAX;

     cv::namedWindow(m_WindowNameFull,0);
     cv::resizeWindow(m_WindowNameFull, 800, 800);
     cv::imshow(m_WindowNameFull, m_imSrcSample);

     cv::createTrackbar("Feature Strength", m_WindowNameFull, &indColorTh, m_COLOR_SLIDER_MAX, On_TrackColorThreshold, this);
     cv::waitKey();

     cv::Mat seg = cv::Mat::zeros(m_imLabSample.size(), CV_8UC1);
     cv::Scalar color=cv::Scalar(1);
     for(unsigned int i=0;i<m_contours.size();i++) {
       drawContours(seg,m_contours,i,color,-1,8,m_hierarchy,0,cv::Point());
     }
     cv::resize(seg, m_imLab, cv::Size(m_imLab.cols, m_imLab.rows), cv::INTER_NEAREST);


     cv::destroyWindow(m_WindowNameFull);

    std::cout << "Do segmentation at QuickTCGASegmenter\n";
}

void QuickTCGASegmenter::DoNucleiSegmentationYi(float otsuRatio, double curvatureWeight, float sizeThld, float sizeUpperThld, double mpp) {

    // Resize image for higher efficiency
    double samratio = 1;
     cv::resize(m_imSrc, m_imSrcSample, cv::Size(m_imSrc.cols*samratio, m_imSrc.rows*samratio), cv::INTER_LINEAR);

     cv::Mat seg = processTile(m_imSrcSample, otsuRatio, curvatureWeight, sizeThld, sizeUpperThld, mpp);
     cv::resize(seg, m_imLab, cv::Size(m_imLab.cols, m_imLab.rows), cv::INTER_NEAREST);

//     seg.copyTo(m_imLab);
}

void QuickTCGASegmenter::RefineCurvature() {

    // Resize image for higher efficiency
     cv::resize(m_imSrc, m_imSrcSample, cv::Size(m_imSrc.cols*m_SAMPLERATE, m_imSrc.rows*m_SAMPLERATE), cv::INTER_LINEAR);
     cv::resize(m_imLab, m_imLabSample, cv::Size(m_imLab.cols*m_SAMPLERATE, m_imLab.rows*m_SAMPLERATE), cv::INTER_NEAREST);


     cv::Mat seg = cv::Mat::zeros(m_imLabSample.size(), CV_8UC1);
     cv::resize(seg, m_imLab, cv::Size(m_imLab.cols, m_imLab.rows), cv::INTER_NEAREST);

     cv::namedWindow(m_WindowNameROI,0);
     cv::resizeWindow(m_WindowNameROI, 300, 300);
     cv::imshow(m_WindowNameROI, m_imSrcSample);
     cv::waitKey();
     cv::destroyWindow(m_WindowNameROI);
    std::cout << "Do refinement at QuickTCGASegmenter\n";
}

void QuickTCGASegmenter::RefineShortCut() {

    cv::Mat imSrcROI, imLabROI;
    cv::Rect roi;

    // Find ROI to apply ShortCut
    TCGA::FindBoundingBoxFromMask(m_imROI, roi);
    imSrcROI = m_imSrc(roi);
    imLabROI = m_imLab(roi);

    ShortCut sc;
    sc.SetSourceImage(imSrcROI.clone(), imLabROI.clone());
    sc.DoSegmentation();

    cv::Mat imSC;
    sc.GetSegmentation(imSC);

    // Update results
//    imLabROI = (imSegROI&(imLabROI==0)|imSC&(imLabROI > 0));
//    imLabROI = imSC&(imLabTmp > 0);
//    imLabROI = imSC;
    imSC.copyTo(imLabROI);

    std::cout << "Do ShortCut at QuickTCGASegmenter\n";
}

void QuickTCGASegmenter::DoTemplateMatching() {
    std::cout << "Do template matching at QuickTCGASegmenter\n";
}

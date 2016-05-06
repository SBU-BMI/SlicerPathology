
#include "TCGAUtilities.h"

namespace TCGA
{

void CopyImageVTK2OpenCV(const vtkSmartPointer<vtkImageData> imVTK, cv::Mat &imOpenCV) {

    // NOTE: in Slicer VTK label image uses SHORT as default data type!!!
    const int numComponents =  imVTK->GetNumberOfScalarComponents();
    if(numComponents == 1) {
        short* pixel;
        for (int y = 0; y < imOpenCV.rows; ++y)  {
            unsigned char *srow = imOpenCV.ptr<unsigned char>(y);
            for (int x = 0; x < imOpenCV.cols; ++x) {
                pixel  = static_cast<short*>(imVTK->GetScalarPointer(x,y,0));
                *srow++ = pixel[0];
            }
        }
//        cv::flip(imOpenCV,imOpenCV, 0);
    }
    else if(numComponents == 3) {
        cv::Vec3b* dptr = reinterpret_cast<cv::Vec3b*>(imVTK->GetScalarPointer());
        size_t elem_step = imVTK->GetIncrements()[1]/sizeof(cv::Vec3b);

       for (int y = 0; y < imOpenCV.rows; ++y) {
           const cv::Vec3b* drow = dptr + elem_step * y;
           unsigned char *srow = imOpenCV.ptr<unsigned char>(y);
           for (int x = 0; x < imOpenCV.cols; ++x, srow += imOpenCV.channels()) {
               srow[0] = drow[x][2];
               srow[1] = drow[x][1];
               srow[2] = drow[x][0];
           }
       }
//       cv::flip(imOpenCV,imOpenCV, 0);
    }
    else {
        std::cout << "Failed to copy images, image channel doesn't match!\n";
    }
}

void CopyImageOpenCV2VTK(const cv::Mat &imOpenCV, vtkSmartPointer<vtkImageData> imVTK) {

    const int numComponents =  imVTK->GetNumberOfScalarComponents();

    if(numComponents == 1) {

        cv::Mat imOpenCVFlip = imOpenCV;
//        cv::flip(imOpenCV,imOpenCVFlip, 0);

        short* pixel;
        for (int y = 0; y < imOpenCVFlip.rows; ++y)  {
            unsigned char *srow = imOpenCVFlip.ptr<unsigned char>(y);
            for (int x = 0; x < imOpenCVFlip.cols; ++x) {
                pixel  = static_cast<short*>(imVTK->GetScalarPointer(x,y,0));
                pixel[0] = *srow++;
            }
        }
    }
    else if(numComponents == 3) {
        cv::Vec3b* dptr = reinterpret_cast<cv::Vec3b*>(imVTK->GetScalarPointer());
        size_t elem_step = imVTK->GetIncrements()[1]/sizeof(cv::Vec3b);

        cv::Mat imOpenCVFlip = imOpenCV;;
//        cv::flip(imOpenCV,imOpenCVFlip, 0);
        for (int y = 0; y < imOpenCVFlip.rows; ++y) {
           cv::Vec3b* drow = dptr + elem_step * y;
           const unsigned char *srow = imOpenCVFlip.ptr<unsigned char>(y);
           for (int x = 0; x < imOpenCVFlip.cols; ++x, srow += imOpenCV.channels()) {
               drow[x] = cv::Vec3b(srow[2], srow[1], srow[0]);
           }
       }
    }
    else {
        std::cout << "Failed to copy images, image channel doesn't match!\n";
    }
}

void FindBoundingBoxFromMask(const cv::Mat& imMask, cv::Rect& rect) {

    assert(imMask.channels() == 1);

    std::vector<std::vector<cv::Point> > contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::Mat imTemp;

    imTemp = imMask.clone();

    findContours(imTemp,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE,cv::Point(0,0));

    double area, maxArea;
    int indMax = -1;
    maxArea = 0;

    assert(contours.size() > 0);

    for(unsigned int i=0;i<contours.size();i++) {
        area = cv::contourArea(contours[i]);
        if(area > maxArea) {
            maxArea = area;
            indMax = i;
        }
    }
    if (indMax >= 0) {
      rect = cv::boundingRect(contours[indMax]);
    }
}

} // end of TCGA namespace

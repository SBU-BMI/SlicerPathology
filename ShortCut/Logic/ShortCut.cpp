#include <set>
#include <vector>

#include "ShortCut.h"


static void On_MouseClickCallBack(int event, int x, int y, int flags, void* userData) {

    ShortCut* pSC = static_cast<ShortCut*>(userData);
    pSC->MouseClick(event, x, y, flags);

}

/************************************************************
 * Core functions of Short Cut *
************************************************************/
struct BandElement {
    long index;
    int label;
    double t;
    friend bool operator < (const BandElement& bEle0, const BandElement& bEle1) {
        if(bEle0.t == bEle1.t)
            return bEle0.index  < bEle1.index;

        return bEle0.t < bEle1.t;
    }
};

struct DKElement {
    enum FMState {
        Alive,
        Close,
        Far,
        Boundary
    };

    std::vector<unsigned> indNeighbor;
    std::vector<double> t2Neighbor;
    FMState state;
    double t;
    int label;
    bool bValid;
};

const double  GEODESIC_INF = 1e100;
const double EPSILON = 1e-5;
std::set<BandElement> DKBand;


void IniDK(uchar* pImg, uchar* pLabels, const int ROWS, const int COLS, int CHANNELS,
           DKElement* &pDK, uchar* pImROI) {

    assert(CHANNELS>1);

    // DIMX is col, DIMY is row!
    int Nx[] = {-1, 1, 0, 0, -1, -1, 1,  1}; //8-neighbors
    int Ny[] = {0, 0, -1, 1,  1, -1, 1, -1};
    long DIMXY = ROWS*COLS;
    double MAXC = 441.673;
    int idxq, idxp, idxp1, idxp2, idxq1, idxq2, idxp_scn, idxq_scn; // idxp_scn: index for single channel
    int i,j,m;
    double C;

    // index rule: pixelPtr[i*img.cols*cn + j*cn + k], k is channel index
    pDK = new DKElement[DIMXY];

    for(i = 0; i < DIMXY; i++) {
        pDK[i].t = GEODESIC_INF;
        pDK[i].state = DKElement::Far;
        pDK[i].bValid = false;
    }

    std::vector<unsigned> alive_vec;
    for(i=1;i<ROWS-1;i++) {
            for(j=1;j<COLS-1;j++) {


                idxp = i*COLS*CHANNELS + j*CHANNELS;
                idxp1 = idxp+1; idxp2 = idxp+2;
                idxp_scn = i*COLS + j;

                if(pImROI[idxp_scn] == 0) continue;

                pDK[idxp_scn].label = pLabels[idxp_scn];
                pDK[idxp_scn].indNeighbor.resize(8);
                pDK[idxp_scn].t2Neighbor.resize(8);
                pDK[idxp_scn].bValid = true;

                //for every neighbor q
                for(m=0;m<8;m++) {
                    idxq = idxp + Nx[m]*COLS*CHANNELS + Ny[m]*CHANNELS;
                    idxq1 = idxq+1; idxq2 = idxq+2;

                    idxq_scn = idxp_scn + Nx[m]*COLS + Ny[m];

                    if(pImROI[idxq_scn] > 0) {
                        if(CHANNELS>1)
                            C = sqrt( (pImg[idxp ] - pImg[idxq ])*(pImg[idxp ] - pImg[idxq ]) +
                                      (pImg[idxp1] - pImg[idxq1])*(pImg[idxp1] - pImg[idxq1]) +
                                      (pImg[idxp2] - pImg[idxq2])*(pImg[idxp2] - pImg[idxq2]) );
                        else
                            C = sqrt((pImg[idxp_scn ] - pImg[idxq_scn])*(pImg[idxp_scn] - pImg[idxq_scn]));

                        pDK[idxp_scn].indNeighbor[m] = idxq_scn;
                        pDK[idxp_scn].t2Neighbor[m] = C/MAXC+EPSILON;
                    }
                    else {
                        pDK[idxp_scn].indNeighbor[m] = idxq_scn;
                        pDK[idxp_scn].t2Neighbor[m] = GEODESIC_INF;
                    }

                }

                if(pLabels[idxp_scn] != 0) {
                    pDK[idxp_scn].t = 0;
                    pDK[idxp_scn].state = DKElement::Alive;
                    alive_vec.push_back(idxp_scn);
                }
            }
    }

    for(j = 0; j < COLS; j++) {
        pDK[j].state = DKElement::Boundary;
    }
    for(j = 0; j < COLS; j++) {
        idxp = j + (ROWS-1)*COLS;
        pDK[idxp].state = DKElement::Boundary;
    }
    for(i = 0; i < ROWS; i++) {
        idxp = i*COLS;
        pDK[idxp].state = DKElement::Boundary;
    }
    for(i = 0; i < ROWS; i++) {
        idxp = (COLS-1) + i*COLS;
        pDK[idxp].state = DKElement::Boundary;
    }


    // initialize first-ring neighbors
    DKBand.clear();
    for(unsigned int i = 0; i < alive_vec.size(); i++) {
        idxp = alive_vec[i];
        for(unsigned int j = 0; j < pDK[idxp].indNeighbor.size(); j++) {

            idxq = pDK[idxp].indNeighbor[j];
            BandElement ele;
            ele.index = idxq;
            if(pDK[idxq].t > pDK[idxp].t2Neighbor[j] && pDK[idxq].bValid) {
                // update band
                ele.t = pDK[idxp].t2Neighbor[j];
                DKBand.erase(ele);

                ele.t = pDK[idxp].t2Neighbor[j];
                DKBand.insert(ele);

                // update neighbor
                pDK[idxq].t = ele.t;
                pDK[idxq].label = pDK[idxp].label;
            }
        }
    }
}

void UpdateDK(uchar* pImg, uchar* pLabels, const std::vector<uchar>& pLabelsOri,
              const std::vector<double>& pDistOri, const int ROWS, const int COLS, int CHANNELS,
              DKElement* &pDK, uchar* pImROI) {

    // DIMX is col, DIMY is row!
    int Nx[] = {-1, 1, 0, 0, -1, -1, 1,  1}; //8-neighbors
    int Ny[] = {0, 0, -1, 1,  1, -1, 1, -1};
    long DIMXY = ROWS*COLS;
    double MAXC = 441.673;
    int idxq, idxp, idxp1, idxp2, idxq1, idxq2, idxp_scn, idxq_scn; // idxp_scn: index for single channel
    int i,j,m;
    double C;

    for(i = 0; i < DIMXY; i++) {
        pDK[i].t = pDistOri[i];              // Copy original distance information
        pDK[i].label = pLabelsOri[i];   // Copy original label information
        pDK[i].state = DKElement::Far;
        pDK[i].bValid = false;
    }

    std::vector<unsigned> alive_vec;
    for(i=1;i<ROWS-1;i++) {
            for(j=1;j<COLS-1;j++) {
                idxp = i*COLS*CHANNELS + j*CHANNELS;
                idxp1 = idxp+1; idxp2 = idxp+2;
                idxp_scn = i*COLS + j;

                if(pImROI[idxp_scn] == 0) continue;

                pDK[idxp_scn].label = pLabels[idxp_scn];
                pDK[idxp_scn].indNeighbor.resize(8);
                pDK[idxp_scn].t2Neighbor.resize(8);
                pDK[idxp_scn].bValid = true;

                //for every neighbor q
                for(m=0;m<8;m++) {
                    idxq = idxp + Nx[m]*COLS*CHANNELS + Ny[m]*CHANNELS;
                    idxq1 = idxq+1; idxq2 = idxq+2;

                    idxq_scn = idxp_scn + Nx[m]*COLS + Ny[m];

                    if(pImROI[idxq_scn] > 0) {
                        if(CHANNELS>1)
                            C = sqrt( (pImg[idxp ] - pImg[idxq ])*(pImg[idxp ] - pImg[idxq ]) +
                                      (pImg[idxp1] - pImg[idxq1])*(pImg[idxp1] - pImg[idxq1]) +
                                      (pImg[idxp2] - pImg[idxq2])*(pImg[idxp2] - pImg[idxq2]) );
                        else
                            C = sqrt((pImg[idxp ] - pImg[idxq ])*(pImg[idxp ] - pImg[idxq ]));

                        pDK[idxp_scn].indNeighbor[m] = idxq_scn;
                        pDK[idxp_scn].t2Neighbor[m] = C/MAXC+EPSILON;
                    }
                    else {
                        pDK[idxp_scn].indNeighbor[m] = idxq_scn;
                        pDK[idxp_scn].t2Neighbor[m] = GEODESIC_INF;
                    }

                }

                if(pLabels[idxp_scn] != 0) {
                    pDK[idxp_scn].t = 0;
                    pDK[idxp_scn].state = DKElement::Alive;
                    alive_vec.push_back(idxp_scn);
                }
            }
    }

    for(j = 0; j < COLS; j++) {
        pDK[j].state = DKElement::Boundary;
    }
    for(j = 0; j < COLS; j++) {
        idxp = j + (ROWS-1)*COLS;
        pDK[idxp].state = DKElement::Boundary;
    }
    for(i = 0; i < ROWS; i++) {
        idxp = i*COLS;
        pDK[idxp].state = DKElement::Boundary;
    }
    for(i = 0; i < ROWS; i++) {
        idxp = (COLS-1) + i*COLS;
        pDK[idxp].state = DKElement::Boundary;
    }

    // initialize first-ring neighbors
    DKBand.clear();
    for(unsigned int i = 0; i < alive_vec.size(); i++) {
        idxp = alive_vec[i];
        for(unsigned int j = 0; j < pDK[idxp].indNeighbor.size(); j++) {

            idxq = pDK[idxp].indNeighbor[j];
            BandElement ele;
            ele.index = idxq;
            if(pDK[idxq].t >= pDK[idxp].t2Neighbor[j]  && pDK[idxq].bValid) {
                // update band
                ele.t = pDK[idxp].t2Neighbor[j];
                DKBand.erase(ele);

                ele.t = pDK[idxp].t2Neighbor[j];
                DKBand.insert(ele);

                // update neighbor
                pDK[idxq].t = ele.t;
                pDK[idxq].label = pDK[idxp].label;
            }
        }
    }
}

void ClassifyNNPoints(DKElement* pDK) {

    BandElement ele;
    double t, tOri, tSrc;
    int idxp, idxq;

    long k = 0;
    while(!DKBand.empty()) {
        ele = *DKBand.begin();
        DKBand.erase(DKBand.begin());
        idxp = ele.index;
        tSrc = pDK[idxp].t;

        k++;

        for(unsigned int i = 0; i < pDK[idxp].indNeighbor.size(); i++) {
            idxq = pDK[idxp].indNeighbor[i];

            if(pDK[idxq].state == DKElement::Alive || !pDK[idxq].bValid) continue;    // Alive points won't be affected

            t = tSrc+pDK[idxp].t2Neighbor[i];
            tOri = pDK[idxq].t;

            if(tOri >= t) {
                pDK[idxq].t = t;

                ele.index = idxq;
                ele.t = tOri;
                DKBand.erase(ele);

                ele.t = t;
                pDK[idxq].label = pDK[idxp].label;
                DKBand.insert(ele);
            }
        }
    }

}

/************************************************************
 * Definition of Short Cut *
************************************************************/
ShortCut::ShortCut() {
    m_WinName = "ShortCut";
    m_bIsInitialized = false;
    m_bShortCut = true;
    m_bManualEdit = false;
    m_pDK = NULL;

    m_INDFGD_COLOR = cvScalar(m_INDFGD);
    m_INDBGD_COLOR = cvScalar(m_INDBGD);
    m_INDNON_COLOR = cvScalar(m_INDNON);

    m_indPolySelect.resize(2);
    m_indPolySelect[0] = -1;
    m_indPolySelect[1] = -1;
}

ShortCut::~ShortCut(){
    if(m_pDK != NULL)
        delete []m_pDK;
}
void ShortCut::SetSourceImage(const cv::Mat &imSrc, const cv::Mat& imSeed) {

    if(imSeed.empty()) std::cout << "no seed image\n";

    m_imSrc = imSrc;
    m_imSeed = imSeed.clone();

    m_imROI.create(m_imSrc.size(), CV_8UC1);
    m_imSeg.create(m_imSrc.size(), CV_8UC1);
    // Make Rectangular ROI
    m_imROI.setTo(1);

    // Save boundary labels
    m_imROIBoundary = imSeed.clone();
    m_imROIBoundary.setTo(0);
    int COLS = imSeed.cols;
    int ROWS = imSeed.rows;
    int idxp;

    for(int j = 0; j < COLS; j++) {
        m_imROIBoundary.data[j] = imSeed.data[j];
    }
    for(int j = 0; j < COLS; j++) {
        idxp = j + (ROWS-1)*COLS;
        m_imROIBoundary.data[idxp] = imSeed.data[idxp];
    }
    for(int i = 0; i < ROWS; i++) {
        idxp = i*COLS;
        m_imROIBoundary.data[idxp] = imSeed.data[idxp];
    }
    for(int i = 0; i < ROWS; i++) {
        idxp = (COLS-1) + i*COLS;
        m_imROIBoundary.data[idxp] = imSeed.data[idxp];
    }

    m_labPre.resize(imSrc.cols*imSrc.rows);
    m_distPre.resize(imSrc.cols*imSrc.rows);
    m_pDK = new DKElement[imSrc.cols*imSrc.rows];

    std::fill(m_labPre.begin(), m_labPre.end(), 0);
    std::fill(m_distPre.begin(), m_distPre.end(), GEODESIC_INF);
    if(!m_imSeg.empty()) m_imSeg.setTo(m_INDNON);
    m_fgdPxls.clear();
    m_bgdPxls.clear();

    m_bIsInitialized = false;
    m_bShortCut = true;
    m_lBtState = NOT_SET;
    m_rBtState = NOT_SET;

    m_indPolySelect.resize(2);
    m_indPolySelect[0] = -1;
    m_indPolySelect[1] = -1;

//    ReSet();
}

void ShortCut::ReSet() {
    if(!m_imSeed.empty()) m_imSeed.setTo(m_INDNON);
    if(!m_imSeg.empty()) m_imSeg.setTo(m_INDNON);

    std::fill(m_labPre.begin(), m_labPre.end(), 0);
    std::fill(m_distPre.begin(), m_distPre.end(), GEODESIC_INF);

    m_fgdPxls.clear();
    m_bgdPxls.clear();

    m_bIsInitialized = false;
    m_bShortCut = true;
    m_lBtState = NOT_SET;
    m_rBtState = NOT_SET;

    m_indPolySelect.resize(2);
    m_indPolySelect[0] = -1;
    m_indPolySelect[1] = -1;

}

void ShortCut::MouseClick(int event, int x, int y, int flags) {

    cv::Point p;
    switch (event) {
    case cv::EVENT_LBUTTONDOWN:
        if(m_bShortCut) {
            p = cv::Point(x,y);
            m_fgdPxls.push_back(p);
            cv::circle(m_imSeed, p, m_RAD, m_INDFGD_COLOR, m_THICKNESS);

            ShowImage();
        }
        else if(m_bManualEdit) {
            FindNNPolyPoint(x,y);
            if(m_indPolySelect[0] >= 0)
                ;//std::cout << "Find point at " << m_indPolySelect[0] << "," << m_indPolySelect[1] << std::endl;
            else
                std::cout << "No point selected, too far to contour\n";
        }

            m_lBtState = IN_PROCESS;
//        }
        break;
    case cv::EVENT_LBUTTONUP:
            m_lBtState = SET;

            if(m_bManualEdit) {
                // Update polygon
                if(m_indPolySelect[0] >= 0) {
                    m_polys[m_indPolySelect[0]][m_indPolySelect[1]] = cv::Point(x,y);

                    UpdatePolyGon();
                }

                // Reset selected index
                m_indPolySelect[0] = -1;
                m_indPolySelect[1] = -1;
            }
        break;
    case cv::EVENT_RBUTTONDOWN:
        if(m_bShortCut) {
            p = cv::Point(x,y);
            m_bgdPxls.push_back(p);
            cv::circle(m_imSeed, p, m_RAD, m_INDBGD_COLOR, m_THICKNESS);

            ShowImage();
        }

        m_rBtState = IN_PROCESS;
        break;
    case cv::EVENT_RBUTTONUP:
        m_rBtState = SET;
        break;
    case cv::EVENT_MOUSEMOVE:
        if(m_lBtState == IN_PROCESS) {
            if(m_bShortCut) {
                // Record seed points
                p = cv::Point(x,y);
                m_fgdPxls.push_back(p);
                cv::circle(m_imSeed, p, m_RAD, m_INDFGD_COLOR, m_THICKNESS);

                ShowImage();
            }
        }
        else if(m_rBtState == IN_PROCESS) {
            if(m_bShortCut) {
                // Record seed points
                p = cv::Point(x,y);
                m_bgdPxls.push_back(p);
                cv::circle(m_imSeed, p, m_RAD, m_INDBGD_COLOR, m_THICKNESS);

                ShowImage();
            }
        }
        break;
    }

}

void ShortCut::DoSegmentation() {

    if(m_imSrc.empty()) {
        std::cout << "No sorce image\n";
        return;
    }

    IniImSeedFromSeg();
    UpdateSegmentation();

    cv::namedWindow(m_WinName, CV_WINDOW_NORMAL);
    cv::setMouseCallback(m_WinName, On_MouseClickCallBack, this);
    ShowImage();

    bool bQuit = false;
    for(;;) {
       int c = cv::waitKey();
       switch ((char)c) {
       case 'n':
           UpdateSegmentation();
           ShowImage();
           std::cout << "Do segmentation\n";
           break;
       case 'r':
           ReSet();
           ShowImage();
           std::cout << "Reset ShortCut\n";
           break;
       case 'q':
           std::cout << "Quit\n";
           bQuit = true;
           break;
       case 'a':
           if(m_bShortCut) {
               m_bManualEdit = true;
               m_bShortCut = false;
               ShowImage(true);
               std::cout << "Manual editing\n";
           }
           else {
               m_bShortCut = true;
               m_bManualEdit = false;
               ShowImage();
               std::cout << "Short Cut\n";
           }

       }
       if(bQuit) break;
    }

    cv::destroyWindow(m_WinName);
}

void ShortCut::IniImSeedFromSeg() {

   cv::Mat seedFgrd, seedBgrd;
   // Create a structuring element
   int erosion_size = 3;
   cv::Mat element = cv::getStructuringElement(cv::MORPH_CROSS,
          cv::Size(2 * erosion_size + 1, 2 * erosion_size + 1),
          cv::Point(erosion_size, erosion_size));

   // Estimate foreground seed
   seedFgrd = (m_imSeed == 1);
   cv::dilate(seedFgrd, seedBgrd,element);

//   // Extract skeleton as foreground
//   cv::Mat skel(m_imSeed.size(), CV_8UC1, cv::Scalar(0));
//   cv::Mat temp(m_imSeed.size(), CV_8UC1);
//   cv::Mat img;
//   seedFgrd.copyTo(img);
//   bool done;
//   do  {
//     cv::morphologyEx(img, temp, cv::MORPH_OPEN, element);
//     cv::bitwise_not(temp, temp);
//     cv::bitwise_and(img, temp, temp);
//     cv::bitwise_or(skel, temp, skel);
//     cv::erode(img, img, element);

//     double max;
//     cv::minMaxLoc(img, 0, &max);
//     done = (max == 0);
//   } while (!done);
//   img.copyTo(seedFgrd);



//   cv::dilate(seedFgrd, seedBgrd,element);

   cv::erode(seedFgrd,seedFgrd,element);  // dilate(image,dst,element);
   cv::Canny( seedFgrd, seedFgrd, 50, 150, 3);
   cv::threshold(seedFgrd,seedFgrd, 100, 1, cv::THRESH_BINARY);

   // Estimate background seed
   cv::erode(seedBgrd,seedBgrd,element);  // dilate(image,dst,element);
   cv::Canny( seedBgrd, seedBgrd, 50, 150, 3);
   cv::threshold(seedBgrd,seedBgrd, 100, 2, cv::THRESH_BINARY);

   m_imSeed = seedFgrd + seedBgrd;
   // TODO:
   // Estimate distance field and do anti-propagation

   m_lBtState = SET;
   m_rBtState = SET;
}

void ShortCut::UpdateSegmentation() {

    // Local update
    if(m_bIsInitialized) {
        UpdateDK(m_imSrc.data, m_imSeed.data, m_labPre, m_distPre, m_imSrc.rows,
                 m_imSrc.cols, m_imSrc.channels(), m_pDK, m_imROI.data);
        ClassifyNNPoints(m_pDK);

        // Save result
        for(int i = 0; i < m_imSrc.cols*m_imSrc.rows; i++) {
    //        pLabelsOut[i] = pDK[i].label >= 0 ? pDK[i].label : 0;
            m_labPre[i] = m_pDK[i].label;
            m_distPre[i]  = m_pDK[i].t;
        }

        memcpy(m_imSeg.data, m_labPre.data(), m_labPre.size()*sizeof(uchar));
    }
    // New segmentation
    else {
        if(m_lBtState == SET || m_rBtState == SET) {

            IniDK(m_imSrc.data,m_imSeed.data, m_imSrc.rows, m_imSrc.cols, m_imSrc.channels(), m_pDK, m_imROI.data);

            ClassifyNNPoints(m_pDK);

            for(int i = 0; i < m_imSrc.cols*m_imSrc.rows; i++) {
        //        pLabelsOut[i] = pDK[i].label >= 0 ? pDK[i].label : 0;
                m_labPre[i] = m_pDK[i].label;
                m_distPre[i]  = m_pDK[i].t;
            }

            memcpy(m_imSeg.data, m_labPre.data(), m_labPre.size()*sizeof(uchar));

            m_bIsInitialized = true;
        }
        else std::cout << "Please set seed pixels first\n";
    }

    m_fgdPxls.clear();
    m_bgdPxls.clear();
}

void ShortCut::GetSegmentation(cv::Mat &imSeg) {
//    cv::Mat im = m_imSeg&m_INDFGD;
    cv::Mat im = m_imSeg==m_INDFGD;
    cv::threshold(im,im, 0, 1, cv::THRESH_BINARY);
    im = im + m_imROIBoundary;
    imSeg = im.clone();
}

void ShortCut::ShowImage(bool bPoly) {

    if(m_imSrc.empty()) return;

    cv::Mat imResult, imROI;
    if(!m_bIsInitialized) {
        m_imSrc.copyTo(imResult);
        if(!m_imROI.empty()) {
            imROI = m_imROI.clone();
            std::vector<std::vector<cv::Point> > contours;
            std::vector<cv::Vec4i> hierarchy;
            findContours(imROI,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE,cv::Point(0,0));

            if(!bPoly) {
                for(unsigned int i=0;i<contours.size();i++) {
                  drawContours(imResult,contours,i,CYAN,2,8,hierarchy,0,cv::Point());
                }
            }
        }
    }
    else {
        if(!m_imSeg.empty()) {
            m_imSrc.copyTo(imResult);
            // Add segmentation contour ...
            std::vector<std::vector<cv::Point> > contours;
            std::vector<cv::Vec4i> hierarchy;
            cv::Mat imSeg;

            imSeg = m_imSeg&m_INDFGD;
            findContours(imSeg,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE,cv::Point(0,0));
            if(!bPoly) {
                for(unsigned int i=0;i<contours.size();i++) {
                  drawContours(imResult,contours,i,BLUE,1,8,hierarchy,0,cv::Point());
                }
            }
            else {
                m_polys.resize(contours.size());

                for(unsigned int i = 0; i < contours.size(); i++ )
                    cv::approxPolyDP( cv::Mat(contours[i]), m_polys[i], 3, true );


                for(unsigned int i = 0; i < m_polys.size(); i++ ) {
                    std::vector<cv::Point>  poly = m_polys[i];
                    cv::polylines(imResult, poly, 1, BLUE, 2);

                    for(unsigned int j = 0; j < poly.size(); j++) {
                        cv::circle(imResult, poly[j], 3, GREEN, -1, CV_AA);
                    }
                }
            }

            if(!m_imROI.empty()) {
                imROI = m_imROI.clone();

                findContours(imROI,contours,hierarchy,CV_RETR_CCOMP,CV_CHAIN_APPROX_SIMPLE,cv::Point(0,0));
                if(!bPoly) {
                    for(unsigned int i=0;i<contours.size();i++) {
                      drawContours(imResult,contours,i,CYAN,2,8,hierarchy,0,cv::Point());
                    }
                }
            }

        }
    }

    std::vector<cv::Point>::const_iterator it;
    for( it = m_fgdPxls.begin(); it != m_fgdPxls.end(); ++it )
        cv::circle(imResult, *it, m_RAD, GREEN, m_THICKNESS );
    for( it = m_bgdPxls.begin(); it != m_bgdPxls.end(); ++it )
        circle(imResult, *it, m_RAD, YELLOW, m_THICKNESS );

    cv::imshow(m_WinName, imResult);
}

void ShortCut::FindNNPolyPoint(const int x, const int y) {

    if(m_polys.empty()) return;

    double d, dMin;

    cv::Point pt;
    dMin = 1e10;
    for(unsigned int i = 0; i < m_polys.size(); i++) {
        for(unsigned int j = 0; j < m_polys[i].size(); j++) {
            pt = m_polys[i][j];
            d = sqrt((pt.x-x)*(pt.x-x)+(pt.y-y)*(pt.y-y));

            if(d < dMin) {
                dMin = d;
                m_indPolySelect[0] = i;
                m_indPolySelect[1] = j;
            }
        }
    }

}

void ShortCut::UpdatePolyGon() {

    if(m_indPolySelect[0] >= 0) {
        cv::Mat imResult;

        if(!m_imSeg.empty()) {
            m_imSrc.copyTo(imResult);
            // Add segmentation contour ...
            cv::Mat imSeg, imUpdate;

            imSeg = m_imSeg&m_INDFGD;
            imSeg.copyTo(imUpdate);

            for(unsigned int i = 0; i < m_polys.size(); i++ ) {
                std::vector<cv::Point>  poly = m_polys[i];
                cv::polylines(imResult, poly, 1, BLUE, 2);

                for(unsigned int j = 0; j < poly.size(); j++) {
                    cv::circle(imResult, poly[j], 3, GREEN, -1, CV_AA);
                }
            }

            // Update segmentation
            cv::fillPoly(imUpdate, m_polys, cv::Scalar(1));
            imUpdate.copyTo(m_imSeg);


            cv::imshow(m_WinName, imResult);
        }
    }

}

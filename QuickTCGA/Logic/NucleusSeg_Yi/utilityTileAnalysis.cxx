// itk
#include "itkOpenCVImageBridge.h"
#include "itkTypedefs.h"
#include "itkBinaryFillholeImageFilter.h"
#include "itkGradientMagnitudeImageFilter.h"
#include "itkConnectedComponentImageFilter.h"
#include "itkLiThresholdImageFilter.h"
#include "itkHuangThresholdImageFilter.h"
//#include "itkIntermodesThresholdImageFilter.h"
#include "itkIsoDataThresholdImageFilter.h"
//#include "itkKittlerIllingworthThresholdImageFilter.h"
#include "itkMaximumEntropyThresholdImageFilter.h"
#include "itkMomentsThresholdImageFilter.h"
#include "itkOtsuThresholdImageFilter.h"
#include "itkRenyiEntropyThresholdImageFilter.h"
#include "itkShanbhagThresholdImageFilter.h"
#include "itkTriangleThresholdImageFilter.h"
#include "itkYenThresholdImageFilter.h"

#include "itkConnectedComponentImageFilter.h"
#include "itkLabelImageToShapeLabelMapFilter.h"
#include "itkRelabelComponentImageFilter.h"

#include "Normalization.h"
#include "BinaryMaskAnalysisFilter.h"
#include "SFLSLocalChanVeseSegmentor2D.h"


#include "itkTypedefs.h"

#include "utilityScalarImage.h"
#include "utilityIO.h"

#include "time.h"

namespace ImagenomicAnalytics {
    namespace TileAnalysis {
        //--------------------------------------------------------------------------------
        // Extract hematoxylin channel
        template<typename TNull>
        itkUCharImageType::Pointer ExtractHematoxylinChannel(itkRGBImageType::Pointer HAndEImage) {
            int width = HAndEImage->GetLargestPossibleRegion().GetSize()[0];
            int height = HAndEImage->GetLargestPossibleRegion().GetSize()[1];

            std::string stainType = "H&E";

            double leng, A, V, C, log255 = log(255.0);
            int i, j;
            int channelIndex = 0; ///< 0: Hematoxylin; 1: Eosin
            double MODx[3];
            double MODy[3];
            double MODz[3];
            double cosx[3];
            double cosy[3];
            double cosz[3];
            double len[3];
            double q[9];
            // unsigned char rLUT[256];
            // unsigned char gLUT[256];
            // unsigned char bLUT[256];

            //if (!stainType.compare("H&E"))
            {
                // GL Haem matrix
                MODx[0] = 0.644211; //0.650;
                MODy[0] = 0.716556; //0.704;
                MODz[0] = 0.266844; //0.286;
                // GL Eos matrix
                MODx[1] = 0.092789; //0.072;
                MODy[1] = 0.954111; //0.990;
                MODz[1] = 0.283111; //0.105;
                // Zero matrix
                MODx[2] = 0.0;
                MODy[2] = 0.0;
                MODz[2] = 0.0;
            }


            // start
            for (i = 0; i < 3; i++) {
                //normalise vector length
                cosx[i] = cosy[i] = cosz[i] = 0.0;
                len[i] = sqrt(MODx[i] * MODx[i] + MODy[i] * MODy[i] + MODz[i] * MODz[i]);
                if (len[i] != 0.0) {
                    cosx[i] = MODx[i] / len[i];
                    cosy[i] = MODy[i] / len[i];
                    cosz[i] = MODz[i] / len[i];
                }
            }


            // translation matrix
            if (cosx[1] == 0.0) { //2nd colour is unspecified
                if (cosy[1] == 0.0) {
                    if (cosz[1] == 0.0) {
                        cosx[1] = cosz[0];
                        cosy[1] = cosx[0];
                        cosz[1] = cosy[0];
                    }
                }
            }

            if (cosx[2] == 0.0) { // 3rd colour is unspecified
                if (cosy[2] == 0.0) {
                    if (cosz[2] == 0.0) {
                        if ((cosx[0] * cosx[0] + cosx[1] * cosx[1]) > 1) {
                            cosx[2] = 0.0;
                        } else {
                            cosx[2] = sqrt(1.0 - (cosx[0] * cosx[0]) - (cosx[1] * cosx[1]));
                        }

                        if ((cosy[0] * cosy[0] + cosy[1] * cosy[1]) > 1) {
                            cosy[2] = 0.0;
                        } else {
                            cosy[2] = sqrt(1.0 - (cosy[0] * cosy[0]) - (cosy[1] * cosy[1]));
                        }

                        if ((cosz[0] * cosz[0] + cosz[1] * cosz[1]) > 1) {
                            cosz[2] = 0.0;
                        } else {
                            cosz[2] = sqrt(1.0 - (cosz[0] * cosz[0]) - (cosz[1] * cosz[1]));
                        }
                    }
                }
            }

            leng = sqrt(cosx[2] * cosx[2] + cosy[2] * cosy[2] + cosz[2] * cosz[2]);

            cosx[2] = cosx[2] / leng;
            cosy[2] = cosy[2] / leng;
            cosz[2] = cosz[2] / leng;

            for (i = 0; i < 3; i++) {
                if (cosx[i] == 0.0) cosx[i] = 0.001;
                if (cosy[i] == 0.0) cosy[i] = 0.001;
                if (cosz[i] == 0.0) cosz[i] = 0.001;
            }

            //matrix inversion
            A = cosy[1] - cosx[1] * cosy[0] / cosx[0];
            V = cosz[1] - cosx[1] * cosz[0] / cosx[0];
            C = cosz[2] - cosy[2] * V / A + cosx[2] * (V / A * cosy[0] / cosx[0] - cosz[0] / cosx[0]);
            q[2] = (-cosx[2] / cosx[0] - cosx[2] / A * cosx[1] / cosx[0] * cosy[0] / cosx[0] +
                    cosy[2] / A * cosx[1] / cosx[0]) / C;
            q[1] = -q[2] * V / A - cosx[1] / (cosx[0] * A);
            q[0] = 1.0 / cosx[0] - q[1] * cosy[0] / cosx[0] - q[2] * cosz[0] / cosx[0];
            q[5] = (-cosy[2] / A + cosx[2] / A * cosy[0] / cosx[0]) / C;
            q[4] = -q[5] * V / A + 1.0 / A;
            q[3] = -q[4] * cosy[0] / cosx[0] - q[5] * cosz[0] / cosx[0];
            q[8] = 1.0 / C;
            q[7] = -q[8] * V / A;
            q[6] = -q[7] * cosy[0] / cosx[0] - q[8] * cosz[0] / cosx[0];

            // initialize 3 output colour stacks
            itkUCharImageType::Pointer hematoxylinChannel = itkUCharImageType::New();
            hematoxylinChannel->SetRegions(HAndEImage->GetLargestPossibleRegion());
            hematoxylinChannel->Allocate();
            hematoxylinChannel->CopyInformation(HAndEImage);

            itkUCharImageType::PixelType *newpixels = hematoxylinChannel->GetBufferPointer();

            // for (j=0; j<256; j++)
            //   {
            //     rLUT[255-j]=static_cast<unsigned char>(255.0 - (double)j * cosx[channelIndex]);
            //     gLUT[255-j]=static_cast<unsigned char>(255.0 - (double)j * cosy[channelIndex]);
            //     bLUT[255-j]=static_cast<unsigned char>(255.0 - (double)j * cosz[channelIndex]);
            //   }

            // translate ------------------
            int imagesize = width * height;

            itkRGBImageType::PixelType *rgbImagePointer = HAndEImage->GetBufferPointer();

            for (j = 0; j < imagesize; j++) {
                // log transform the RGB data
                unsigned char R = rgbImagePointer[j].GetRed();
                unsigned char G = rgbImagePointer[j].GetGreen();
                unsigned char B = rgbImagePointer[j].GetBlue();
                double Rlog = -((255.0 * log((static_cast<double>(R) + 1) / 255.0)) / log255);
                double Glog = -((255.0 * log((static_cast<double>(G) + 1) / 255.0)) / log255);
                double Blog = -((255.0 * log((static_cast<double>(B) + 1) / 255.0)) / log255);

                // rescale to match original paper values
                double Rscaled = Rlog * q[channelIndex * 3];
                double Gscaled = Glog * q[channelIndex * 3 + 1];
                double Bscaled = Blog * q[channelIndex * 3 + 2];
                double output = exp(-((Rscaled + Gscaled + Bscaled) - 255.0) * log255 / 255.0);

                if (output > 255) {
                    output = 255;
                }

                unsigned char idx = static_cast<unsigned char>(0xff & static_cast<int>(floor(output + .5)));

                ////////////////////////////////////////////////////////////////////////////////
                /// Index to rgb to gray
                ///
                /// The original ImageJ plugin output the colorful H
                /// channel as a indexed image using a LUT. Here I first
                /// use the LUT to convert the index to rgb and then
                /// convert to gray. The formula below is what we have
                /// in matlab rgb2gray
                //newpixels[j] = static_cast<itkUCharImageType::PixelType>(0.2989*rLUT[idx] + 0.5870*gLUT[idx] + 0.1140*bLUT[idx]);
                newpixels[j] = idx;
                /// Index to rgb to gray, end
                ////////////////////////////////////////////////////////////////////////////////
            }


            return hematoxylinChannel;
        }
        //================================================================================


        template<typename TNull>
        cv::Mat normalizeImageColor(cv::Mat image) {
            float meanT[3] = {-0.632356, -0.0516004, 0.0376543};
            float stdT[3] = {0.26235, 0.0514831,
                             0.0114217}; ///< These are learnt from the tempalte GBM image selected by George
            cv::Mat newImgCV = nscale::Normalization::normalization(image, meanT, stdT);

            return newImgCV;
        }


        template<typename TNull>
        itkUCharImageType::Pointer extractTissueMask(cv::Mat image) {
            float mData[8] = {-0.154, 0.035, 0.549, -45.718, -0.057, -0.817, 1.170, -49.887};
            cv::Mat M = cv::Mat(2, 4, CV_32FC1, &mData);

            cv::Mat maskCV = nscale::Normalization::segFG(image, M);
            itkUCharImageType::Pointer foregroundMask = itk::OpenCVImageBridge::CVMatToITKImage<itkUCharImageType>(
                    maskCV);

            return foregroundMask;
        }


        template<typename InputImageType>
        std::vector<typename InputImageType::PixelType>
        computeMultipleThresholdsForGrayScaleImage(typename InputImageType::Pointer inputImage) {
            typedef typename InputImageType::PixelType PixelType;
            std::vector <PixelType> multipleThresholds;

            {
                typedef itk::HuangThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            /* { */
            /*   typedef itk::IntermodesThresholdImageFilter<InputImageType, InputImageType> CalculatorType; */
            /*   typename CalculatorType::Pointer calculator = CalculatorType::New(); */
            /*   calculator->SetInput(inputImage); */
            /*   calculator->Update(); */
            /*   multipleThresholds.push_back(calculator->GetThreshold()); */
            /* } */

            {
                typedef itk::IsoDataThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            /* { */
            /*   typedef itk::KittlerIllingworthThresholdImageFilter<InputImageType, InputImageType> CalculatorType; */
            /*   typename CalculatorType::Pointer calculator = CalculatorType::New(); */
            /*   calculator->SetInput(inputImage); */
            /*   calculator->Update(); */
            /*   multipleThresholds.push_back(calculator->GetThreshold()); */
            /* } */

            {
                typedef itk::LiThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::MaximumEntropyThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::MomentsThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::OtsuThresholdImageFilter <InputImageType, InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::RenyiEntropyThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::ShanbhagThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::TriangleThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            {
                typedef itk::YenThresholdImageFilter <InputImageType, InputImageType> CalculatorType;
                typename CalculatorType::Pointer calculator = CalculatorType::New();
                calculator->SetInput(inputImage);
                calculator->Update();
                multipleThresholds.push_back(calculator->GetThreshold());
            }

            return multipleThresholds;
        }


        template<typename InputImageType, typename OutputImageType>
        typename OutputImageType::Pointer
        optimalThresholdImage(typename InputImageType::Pointer inputImage,
                              typename OutputImageType::PixelType maskValue, float &theThreshold) {
            itkFloatImageType::Pointer image = ScalarImage::castItkImage<InputImageType, itkFloatImageType>(inputImage);

            std::vector <itkFloatImageType::PixelType> a = computeMultipleThresholdsForGrayScaleImage<itkFloatImageType>(
                    image);
            std::sort(a.begin(), a.end());

            float ratio = 0.75;
            long n = static_cast<long>(ratio * static_cast<float>(a.size()));

            theThreshold = a[n];

            typename OutputImageType::Pointer mask = OutputImageType::New();
            mask->SetRegions(image->GetLargestPossibleRegion());
            mask->Allocate();
            mask->FillBuffer(0);
            const itkFloatImageType::PixelType *imageBufferPointer = image->GetBufferPointer();
            typename OutputImageType::PixelType *maskBufferPointer = mask->GetBufferPointer();
            std::size_t numPixels = mask->GetLargestPossibleRegion().GetNumberOfPixels();
            for (std::size_t it = 0; it < numPixels; ++it) {
                maskBufferPointer[it] = imageBufferPointer[it] <= theThreshold ? maskValue : 0;
            }

            return mask;
        }

        template<typename TNull>
        itkUCharImageType::Pointer processTile(cv::Mat thisTileCV, \
                                           itkUShortImageType::Pointer &outputLabelImageUShort, \
                                           float otsuRatio = 1.0, \
                                           double curvatureWeight = 0.8, \
                                           float sizeThld = 3, \
                                           float sizeUpperThld = 200, \
                                           double mpp = 0.25, \
                                           float msKernel = 20.0, \
                                           int levelsetNumberOfIteration = 100, \
                                           bool doDeclump = false) {
            std::cout << "normalizeImageColor.....\n" << std::flush;
            cv::Mat newImgCV = normalizeImageColor<char>(thisTileCV);

            std::cout << "extractTissueMask.....\n" << std::flush;
            itkUCharImageType::Pointer foregroundMask = extractTissueMask<char>(newImgCV);

            itkRGBImageType::Pointer thisTile = itk::OpenCVImageBridge::CVMatToITKImage<itkRGBImageType>(thisTileCV);

            //IO::writeImage<itkRGBImageType>(thisTile, "thisTile.png", 0);

            std::cout << "ExtractHematoxylinChannel.....\n" << std::flush;
            itkUCharImageType::Pointer hematoxylinImage = ExtractHematoxylinChannel<char>(thisTile);

            short maskValue = 1;

            itkFloatImageType::Pointer hemaFloat = ScalarImage::castItkImage<itkUCharImageType, itkFloatImageType>(
                    hematoxylinImage);

            std::cout << "ThresholdImage.....\n" << std::flush;

            itkUCharImageType::Pointer nucleusBinaryMask = ScalarImage::otsuThresholdImage<char>(hemaFloat, maskValue,
                                                                                                 otsuRatio);

            long numPixels = nucleusBinaryMask->GetLargestPossibleRegion().GetNumberOfPixels();

            //std::cout<<"output otsuThresholdImage.....\n"<<std::flush;
            //ImagenomicAnalytics::IO::writeImage<itkUCharImageType>(nucleusBinaryMask, "nucleusBinaryMask.png", 0);

            if (foregroundMask) {
                const itkUCharImageType::PixelType *fgMaskBufferPointer = foregroundMask->GetBufferPointer();
                itkBinaryMaskImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    if (0 == fgMaskBufferPointer[it]) {
                        // for sure glass region
                        nucleusBinaryMaskBufferPointer[it] = 0;
                    }
                }
            }

            if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                std::cout << "before CV\n" << std::flush;

                //int numiter = 100;
                time_t start, end;
                time(&start);
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType> cv;
                cv.setImage(hemaFloat);
                cv.setMask(nucleusBinaryMask);
                cv.setNumIter(levelsetNumberOfIteration);
                cv.setCurvatureWeight(curvatureWeight);
                cv.doSegmentation();
                time(&end);
                double dif = difftime(end, start);
                printf("Elasped time is %.2lf seconds.\n", dif);

                std::cout << "after CV\n" << std::flush;

                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::Pointer phi = cv.mp_phi;

                itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::PixelType *phiBufferPointer = phi->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    nucleusBinaryMaskBufferPointer[it] = phiBufferPointer[it] <= 1.0 ? 1 : 0;
                }
            }

            typedef itk::BinaryFillholeImageFilter <itkBinaryMaskImageType> fhFilterType;
            fhFilterType::Pointer fhfilter = fhFilterType::New();
            fhfilter->SetInput(nucleusBinaryMask);
            fhfilter->SetForegroundValue(1);
            fhfilter->Update();

            typedef itk::ConnectedComponentImageFilter <itkBinaryMaskImageType, itkLabelImageType> ConnectedComponentImageFilterType;
            ConnectedComponentImageFilterType::Pointer connected = ConnectedComponentImageFilterType::New();
            connected->SetInput(nucleusBinaryMask);
            connected->Update();

            typedef itk::RelabelComponentImageFilter <itkLabelImageType, itkLabelImageType> FilterType;
            FilterType::Pointer relabelFilter = FilterType::New();
            relabelFilter->SetInput(connected->GetOutput());
            relabelFilter->SetMinimumObjectSize(static_cast<FilterType::ObjectSizeType>(sizeThld / mpp / mpp));
            relabelFilter->Update();

            itkLabelImageType::Pointer tmpImg = relabelFilter->GetOutput();

            itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
            itkLabelImageType::PixelType *tmpImgBufferPointer = tmpImg->GetBufferPointer();

            for (long it = 0; it < nucleusBinaryMask->GetLargestPossibleRegion().GetNumberOfPixels(); ++it) {
                nucleusBinaryMaskBufferPointer[it] = tmpImgBufferPointer[it] > 0 ? 1 : 0;
            }


            if (doDeclump) {
                if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                    gth818n::BinaryMaskAnalysisFilter binaryMaskAnalyzer;
                    binaryMaskAnalyzer.setMaskImage(nucleusBinaryMask);
                    binaryMaskAnalyzer.setObjectSizeThreshold(sizeThld);
                    binaryMaskAnalyzer.setObjectSizeUpperThreshold(sizeUpperThld);
                    binaryMaskAnalyzer.setKernelSize(msKernel);
                    binaryMaskAnalyzer.setMPP(mpp);
                    binaryMaskAnalyzer.update();

                    std::cout << "after declumping\n" << std::flush;

                    itkUIntImageType::Pointer outputLabelImage = binaryMaskAnalyzer.getConnectedComponentLabelImage();
                    itkUCharImageType::Pointer edgeBetweenLabelsMask = ScalarImage::edgesOfDifferentLabelRegion<char>(
                            ScalarImage::castItkImage<itkUIntImageType, itkUIntImageType>(
                                    binaryMaskAnalyzer.getConnectedComponentLabelImage()));
                    itkUCharImageType::PixelType *edgeBetweenLabelsMaskBufferPointer = edgeBetweenLabelsMask->GetBufferPointer();

                    const itkUIntImageType::PixelType *outputLabelImageBufferPointer = outputLabelImage->GetBufferPointer();

                    itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

                    for (long it = 0; it < numPixels; ++it) {
                        nucleusBinaryMaskBufferPointer[it] = outputLabelImageBufferPointer[it] >= 1 ? 1 : 0;
                        nucleusBinaryMaskBufferPointer[it] *= (1 - edgeBetweenLabelsMaskBufferPointer[it]);
                    }
                }
            }


            if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                int numiter = 50;
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType> cv;
                cv.setImage(hemaFloat);
                cv.setMask(nucleusBinaryMask);
                cv.setNumIter(numiter);
                cv.setCurvatureWeight(curvatureWeight);
                cv.doSegmentation();

                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::Pointer phi = cv.mp_phi;

                itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::PixelType *phiBufferPointer = phi->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    nucleusBinaryMaskBufferPointer[it] = phiBufferPointer[it] <= 1.0 ? 1 : 0;
                }
            }

            // "FIX hole in object" (Yi's commit 3/23/17)
            fhFilterType::Pointer fhfilter1 = fhFilterType::New();
            fhfilter1->SetInput( nucleusBinaryMask );
            fhfilter1->SetForegroundValue( 1 );
            fhfilter1->Update();

            //std::cout << "before ConnectedComponent\n" << std::flush;
            //typedef itk::ConnectedComponentImageFilter <itkUCharImageType, itkUShortImageType > ConnectedComponentImageFilterType;
            //ConnectedComponentImageFilterType::Pointer connected = ConnectedComponentImageFilterType::New ();
            //connected->SetInput(nucleusBinaryMask);
            //connected->Update();
            //outputLabelImageUShort = connected->GetOutput();
            //std::cout << "after ConnectedComponent\n" << std::flush;

            return fhfilter1->GetOutput();
            //return nucleusBinaryMask;
        }


        template<typename TNull>
        itkUCharImageType::Pointer processTileOptimalThreshold(cv::Mat thisTileCV, \
                                                           itkUShortImageType::Pointer &outputLabelImageUShort, \
                                                           double curvatureWeight = 0.8, \
                                                           float sizeThld = 3, \
                                                           float sizeUpperThld = 200, \
                                                           double mpp = 0.25, \
                                                           float msKernel = 20.0, \
                                                           int levelsetNumberOfIteration = 100, \
                                                           bool doDeclump = false) {
            std::cout << "normalizeImageColor.....\n" << std::flush;
            cv::Mat newImgCV = normalizeImageColor<char>(thisTileCV);

            std::cout << "extractTissueMask.....\n" << std::flush;
            itkUCharImageType::Pointer foregroundMask = extractTissueMask<char>(newImgCV);

            itkRGBImageType::Pointer thisTile = itk::OpenCVImageBridge::CVMatToITKImage<itkRGBImageType>(thisTileCV);

            //IO::writeImage<itkRGBImageType>(thisTile, "thisTile.png", 0);

            std::cout << "ExtractHematoxylinChannel.....\n" << std::flush;
            itkUCharImageType::Pointer hematoxylinImage = ExtractHematoxylinChannel<char>(thisTile);

            short maskValue = 1;

            itkFloatImageType::Pointer hemaFloat = ScalarImage::castItkImage<itkUCharImageType, itkFloatImageType>(
                    hematoxylinImage);

            std::cout << "ThresholdImage.....\n" << std::flush;

            float theThreshold = 0;
            itkUCharImageType::Pointer nucleusBinaryMask            \
 = optimalThresholdImage<itkFloatImageType, itkUCharImageType>(hemaFloat,
                                                               static_cast<itkUCharImageType::PixelType>(maskValue),
                                                               theThreshold);

            long numPixels = nucleusBinaryMask->GetLargestPossibleRegion().GetNumberOfPixels();

            if (foregroundMask) {
                const itkUCharImageType::PixelType *fgMaskBufferPointer = foregroundMask->GetBufferPointer();
                itkBinaryMaskImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    if (0 == fgMaskBufferPointer[it]) {
                        // for sure glass region
                        nucleusBinaryMaskBufferPointer[it] = 0;
                    }
                }
            }

            if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                std::cout << "before CV\n" << std::flush;

                //int numiter = 100;
                time_t start, end;
                time(&start);
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType> cv;
                cv.setImage(hemaFloat);
                cv.setMask(nucleusBinaryMask);
                cv.setNumIter(levelsetNumberOfIteration);
                cv.setCurvatureWeight(curvatureWeight);
                cv.doSegmentation();
                time(&end);
                double dif = difftime(end, start);
                printf("Elasped time is %.2lf seconds.\n", dif);

                std::cout << "after CV\n" << std::flush;

                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::Pointer phi = cv.mp_phi;

                itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::PixelType *phiBufferPointer = phi->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    nucleusBinaryMaskBufferPointer[it] = phiBufferPointer[it] <= 1.0 ? 1 : 0;
                }
            }

            if (doDeclump) {
                if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                    gth818n::BinaryMaskAnalysisFilter binaryMaskAnalyzer;
                    binaryMaskAnalyzer.setMaskImage(nucleusBinaryMask);
                    binaryMaskAnalyzer.setObjectSizeThreshold(sizeThld);
                    binaryMaskAnalyzer.setObjectSizeUpperThreshold(sizeUpperThld);
                    binaryMaskAnalyzer.setKernelSize(msKernel);
                    binaryMaskAnalyzer.setMPP(mpp);
                    binaryMaskAnalyzer.update();

                    std::cout << "after declumping\n" << std::flush;

                    itkUIntImageType::Pointer outputLabelImage = binaryMaskAnalyzer.getConnectedComponentLabelImage();
                    itkUCharImageType::Pointer edgeBetweenLabelsMask = ScalarImage::edgesOfDifferentLabelRegion<char>(
                            ScalarImage::castItkImage<itkUIntImageType, itkUIntImageType>(
                                    binaryMaskAnalyzer.getConnectedComponentLabelImage()));
                    itkUCharImageType::PixelType *edgeBetweenLabelsMaskBufferPointer = edgeBetweenLabelsMask->GetBufferPointer();

                    const itkUIntImageType::PixelType *outputLabelImageBufferPointer = outputLabelImage->GetBufferPointer();

                    itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

                    for (long it = 0; it < numPixels; ++it) {
                        nucleusBinaryMaskBufferPointer[it] = outputLabelImageBufferPointer[it] >= 1 ? 1 : 0;
                        nucleusBinaryMaskBufferPointer[it] *= (1 - edgeBetweenLabelsMaskBufferPointer[it]);
                    }
                }
            }


            if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                int numiter = 50;
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType> cv;
                cv.setImage(hemaFloat);
                cv.setMask(nucleusBinaryMask);
                cv.setNumIter(numiter);
                cv.setCurvatureWeight(curvatureWeight);
                cv.doSegmentation();

                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::Pointer phi = cv.mp_phi;

                itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::PixelType *phiBufferPointer = phi->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    nucleusBinaryMaskBufferPointer[it] = phiBufferPointer[it] <= 1.0 ? 1 : 0;
                }
            }

            std::cout << "before ConnectedComponent\n" << std::flush;
            typedef itk::ConnectedComponentImageFilter <itkUCharImageType, itkUShortImageType> ConnectedComponentImageFilterType;
            ConnectedComponentImageFilterType::Pointer connected = ConnectedComponentImageFilterType::New();
            connected->SetInput(nucleusBinaryMask);
            connected->Update();
            outputLabelImageUShort = connected->GetOutput();
            std::cout << "after ConnectedComponent\n" << std::flush;

            return nucleusBinaryMask;
        }


        template<typename TNull>
        itkUIntImageType::Pointer processTileOutputLabel(cv::Mat thisTileCV, \
                                                      itkUShortImageType::Pointer &outputLabelImageUShort, \
                                                      float otsuRatio = 1.0, \
                                                      double curvatureWeight = 0.8, \
                                                      float sizeThld = 3, \
                                                      float sizeUpperThld = 200, \
                                                      double mpp = 0.25, \
                                                      float msKernel = 20.0, \
                                                      int levelsetNumberOfIteration = 100) {
            std::cout << "normalizeImageColor.....\n" << std::flush;
            cv::Mat newImgCV = normalizeImageColor<char>(thisTileCV);

            std::cout << "extractTissueMask.....\n" << std::flush;
            itkUCharImageType::Pointer foregroundMask = extractTissueMask<char>(newImgCV);

            itkRGBImageType::Pointer thisTile = itk::OpenCVImageBridge::CVMatToITKImage<itkRGBImageType>(thisTileCV);

            //IO::writeImage<itkRGBImageType>(thisTile, "thisTile.png", 0);

            std::cout << "ExtractHematoxylinChannel.....\n" << std::flush;
            itkUCharImageType::Pointer hematoxylinImage = ExtractHematoxylinChannel<char>(thisTile);

            short maskValue = 1;

            itkFloatImageType::Pointer hemaFloat = ScalarImage::castItkImage<itkUCharImageType, itkFloatImageType>(
                    hematoxylinImage);

            std::cout << "otsuThresholdImage.....\n" << std::flush;
            itkUCharImageType::Pointer nucleusBinaryMask = ScalarImage::otsuThresholdImage<char>(hemaFloat, maskValue,
                                                                                                 otsuRatio);
            long numPixels = nucleusBinaryMask->GetLargestPossibleRegion().GetNumberOfPixels();

            //std::cout<<"output otsuThresholdImage.....\n"<<std::flush;
            //ImagenomicAnalytics::IO::writeImage<itkUCharImageType>(nucleusBinaryMask, "nucleusBinaryMask.png", 0);

            if (foregroundMask) {
                const itkUCharImageType::PixelType *fgMaskBufferPointer = foregroundMask->GetBufferPointer();
                itkBinaryMaskImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    if (0 == fgMaskBufferPointer[it]) {
                        // for sure glass region
                        nucleusBinaryMaskBufferPointer[it] = 0;
                    }
                }
            }

            if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                std::cout << "before CV\n" << std::flush;

                //int numiter = 100;
                time_t start, end;
                time(&start);
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType> cv;
                cv.setImage(hemaFloat);
                cv.setMask(nucleusBinaryMask);
                cv.setNumIter(levelsetNumberOfIteration);
                cv.setCurvatureWeight(curvatureWeight);
                cv.doSegmentation();
                time(&end);
                double dif = difftime(end, start);
                printf("Elasped time is %.2lf seconds.\n", dif);

                std::cout << "after CV\n" << std::flush;

                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::Pointer phi = cv.mp_phi;

                itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
                CSFLSLocalChanVeseSegmentor2D<itkFloatImageType::PixelType>::LSImageType::PixelType *phiBufferPointer = phi->GetBufferPointer();

                for (long it = 0; it < numPixels; ++it) {
                    nucleusBinaryMaskBufferPointer[it] = phiBufferPointer[it] <= 1.0 ? 1 : 0;
                }
            }

            itkUIntImageType::Pointer outputLabelImage;
            if (!ScalarImage::isImageAllZero<itkBinaryMaskImageType>(nucleusBinaryMask)) {
                gth818n::BinaryMaskAnalysisFilter binaryMaskAnalyzer;
                binaryMaskAnalyzer.setMaskImage(nucleusBinaryMask);
                binaryMaskAnalyzer.setObjectSizeThreshold(sizeThld);
                binaryMaskAnalyzer.setObjectSizeUpperThreshold(sizeUpperThld);
                binaryMaskAnalyzer.setKernelSize(msKernel);
                binaryMaskAnalyzer.setMPP(mpp);
                binaryMaskAnalyzer.update();

                std::cout << "after declumping\n" << std::flush;

                outputLabelImage = binaryMaskAnalyzer.getConnectedComponentLabelImage();
                // itkUCharImageType::Pointer edgeBetweenLabelsMask = ScalarImage::edgesOfDifferentLabelRegion<char>(ScalarImage::castItkImage<itkUIntImageType, itkUIntImageType>(binaryMaskAnalyzer.getConnectedComponentLabelImage()));
                // itkUCharImageType::PixelType* edgeBetweenLabelsMaskBufferPointer = edgeBetweenLabelsMask->GetBufferPointer();

                // const itkUIntImageType::PixelType* outputLabelImageBufferPointer = outputLabelImage->GetBufferPointer();

                // itkUCharImageType::PixelType* nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

                // for (long it = 0; it < numPixels; ++it)
                //   {
                //     nucleusBinaryMaskBufferPointer[it] = outputLabelImageBufferPointer[it] >= 1?1:0;
                //     nucleusBinaryMaskBufferPointer[it] *= (1 - edgeBetweenLabelsMaskBufferPointer[it]);
                //   }
            }


            return outputLabelImage;
        }


        cv::Mat processTileCV(cv::Mat thisTileCV, \
                          float otsuRatio = 1.0, \
                          double curvatureWeight = 0.8, \
                          float sizeThld = 3, \
                          float sizeUpperThld = 200, \
                          double mpp = 0.25, \
                          float msKernel = 20.0, \
                          int levelsetNumberOfIteration = 100,
                              bool doDeclump = false) {
            itkUShortImageType::Pointer outputLabelImage;

            // call regular segmentation function
            itkUCharImageType::Pointer nucleusBinaryMask = processTile<char>(thisTileCV, \
                                                                       outputLabelImage, \
                                                                       otsuRatio, \
                                                                       curvatureWeight, \
                                                                       sizeThld, \
                                                                       sizeUpperThld, \
                                                                       mpp, \
                                                                       msKernel, \
                                                                       levelsetNumberOfIteration,
                                                                             doDeclump);

            // change pixel values for visualization reasons
/*
            itkUCharImageType::PixelType *nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
            long numPixels = nucleusBinaryMask->GetLargestPossibleRegion().GetNumberOfPixels();
            for (long it = 0; it < numPixels; ++it) {
                if (nucleusBinaryMaskBufferPointer[it] == 1) {
                    nucleusBinaryMaskBufferPointer[it] = 255;
                }
            }
*/

            cv::Mat binary = itk::OpenCVImageBridge::ITKImageToCVMat<itkUCharImageType>(nucleusBinaryMask);
            return binary;

        }


    }
}// namespace


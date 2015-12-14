#include <cstdio>
#include <iostream>
#include <string>


//itk
#include "itkImage.h"
#include "itkRGBPixel.h"
#include "itkImageFileWriter.h"
#include "itkOtsuThresholdImageFilter.h"
#include "itkCastImageFilter.h"
#include "itkOpenCVImageBridge.h"
#include "itkBinaryFillholeImageFilter.h"

// openslide

// openCV
#include <opencv2/opencv.hpp>


#include "Normalization.h"

#include "itkTypedefs.h"

#include "BinaryMaskAnalysisFilter.h"


#include "SFLSLocalChanVeseSegmentor2D.h"

/**
 * writeImage
 */
template< typename itkImage_t > void writeImage(typename itkImage_t::Pointer img, const char *fileName, bool compress)
{
	typedef itk::ImageFileWriter< itkImage_t > WriterType;

	typename WriterType::Pointer writer = WriterType::New();
	writer->SetFileName( fileName );
	writer->SetInput(img);
	if (compress)
	{
		writer->UseCompressionOn();
	}
	else
	{
		writer->UseCompressionOff();
	}

	try
	{
		writer->Update();
	}
	catch ( itk::ExceptionObject &err)
	{
		std::cout << "ExceptionObject caught !" << std::endl; 
		std::cout << err << std::endl; 
		raise(SIGABRT);   
	}
}


itkUCharImageType::Pointer ExtractHematoxylinChannel(itkRGBImageType::Pointer HAndEImage)
{
	int width = HAndEImage->GetLargestPossibleRegion().GetSize()[0];
	int height = HAndEImage->GetLargestPossibleRegion().GetSize()[1];

	std::string stainType = "H&E";

	double leng, A, V, C, log255=log(255.0);
	int i,j;
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
		MODx[0]= 0.644211; //0.650;
		MODy[0]= 0.716556; //0.704;
		MODz[0]= 0.266844; //0.286;
		// GL Eos matrix
		MODx[1]= 0.092789; //0.072;
		MODy[1]= 0.954111; //0.990;
		MODz[1]= 0.283111; //0.105;
		// Zero matrix
		MODx[2]= 0.0;
		MODy[2]= 0.0;
		MODz[2]= 0.0;
	}


	// start
	for (i=0; i<3; i++)
	{
		//normalise vector length
		cosx[i]=cosy[i]=cosz[i]=0.0;
		len[i]=sqrt(MODx[i]*MODx[i] + MODy[i]*MODy[i] + MODz[i]*MODz[i]);
		if (len[i] != 0.0)
		{
			cosx[i]= MODx[i]/len[i];
			cosy[i]= MODy[i]/len[i];
			cosz[i]= MODz[i]/len[i];
		}
	}


	// translation matrix
	if (cosx[1]==0.0)
	{ //2nd colour is unspecified
		if (cosy[1]==0.0)
		{
			if (cosz[1]==0.0)
			{
				cosx[1]=cosz[0];
				cosy[1]=cosx[0];
				cosz[1]=cosy[0];
			}
		}
	}

	if (cosx[2]==0.0)
	{ // 3rd colour is unspecified
		if (cosy[2]==0.0)
		{
			if (cosz[2]==0.0)
			{
				if ((cosx[0]*cosx[0] + cosx[1]*cosx[1])> 1)
				{
					cosx[2]=0.0;
				}
				else
				{
					cosx[2]=sqrt(1.0-(cosx[0]*cosx[0])-(cosx[1]*cosx[1]));
				}

				if ((cosy[0]*cosy[0] + cosy[1]*cosy[1])> 1)
				{
					cosy[2]=0.0;
				}
				else
				{
					cosy[2]=sqrt(1.0-(cosy[0]*cosy[0])-(cosy[1]*cosy[1]));
				}

				if ((cosz[0]*cosz[0] + cosz[1]*cosz[1])> 1)
				{
					cosz[2]=0.0;
				}
				else
				{
					cosz[2]=sqrt(1.0-(cosz[0]*cosz[0])-(cosz[1]*cosz[1]));
				}
			}
		}
	}

	leng=sqrt(cosx[2]*cosx[2] + cosy[2]*cosy[2] + cosz[2]*cosz[2]);

	cosx[2]= cosx[2]/leng;
	cosy[2]= cosy[2]/leng;
	cosz[2]= cosz[2]/leng;

	for (i=0; i<3; i++)
	{
		if (cosx[i] == 0.0) cosx[i] = 0.001;
		if (cosy[i] == 0.0) cosy[i] = 0.001;
		if (cosz[i] == 0.0) cosz[i] = 0.001;
	}

	//matrix inversion
	A = cosy[1] - cosx[1] * cosy[0] / cosx[0];
	V = cosz[1] - cosx[1] * cosz[0] / cosx[0];
	C = cosz[2] - cosy[2] * V/A + cosx[2] * (V/A * cosy[0] / cosx[0] - cosz[0] / cosx[0]);
	q[2] = (-cosx[2] / cosx[0] - cosx[2] / A * cosx[1] / cosx[0] * cosy[0] / cosx[0] + cosy[2] / A * cosx[1] / cosx[0]) / C;
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

	itkUCharImageType::PixelType* newpixels = hematoxylinChannel->GetBufferPointer();

	// for (j=0; j<256; j++)
	//   {
	//     rLUT[255-j]=static_cast<unsigned char>(255.0 - (double)j * cosx[channelIndex]);
	//     gLUT[255-j]=static_cast<unsigned char>(255.0 - (double)j * cosy[channelIndex]);
	//     bLUT[255-j]=static_cast<unsigned char>(255.0 - (double)j * cosz[channelIndex]);
	//   }

	// translate ------------------
	int imagesize = width * height;

	itkRGBImageType::PixelType* rgbImagePointer = HAndEImage->GetBufferPointer();

	for (j=0;j<imagesize;j++)
	{
		// log transform the RGB data
		unsigned char R = rgbImagePointer[j].GetRed();
		unsigned char G = rgbImagePointer[j].GetGreen();
		unsigned char B = rgbImagePointer[j].GetBlue();
		double Rlog = -((255.0*log((static_cast<double>(R)+1)/255.0))/log255);
		double Glog = -((255.0*log((static_cast<double>(G)+1)/255.0))/log255);
		double Blog = -((255.0*log((static_cast<double>(B)+1)/255.0))/log255);

		// rescale to match original paper values
		double Rscaled = Rlog * q[channelIndex*3];
		double Gscaled = Glog * q[channelIndex*3+1];
		double Bscaled = Blog * q[channelIndex*3+2];
		double output = exp(-((Rscaled + Gscaled + Bscaled) - 255.0) * log255 / 255.0);

		if(output>255)
		{
			output=255;
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


itkUCharImageType::Pointer otsuThresholdImage(itkFloatImageType::Pointer image, itkUCharImageType::PixelType maskValue, float otsuRatio = 1.0)
{
	typedef itk::OtsuThresholdImageFilter<itkFloatImageType, itkUCharImageType> FilterType;
	FilterType::Pointer otsuFilter = FilterType::New();
	otsuFilter->SetInput(image);
	otsuFilter->SetInsideValue(maskValue);
	otsuFilter->Update();

	itkUCharImageType::Pointer mask = otsuFilter->GetOutput();

	itkFloatImageType::PixelType otsuThld = otsuRatio*(otsuFilter->GetThreshold());

	const itkFloatImageType::PixelType* imageBufferPointer = image->GetBufferPointer();
	itkUCharImageType::PixelType* maskBufferPointer = mask->GetBufferPointer();
	long numPixels = mask->GetLargestPossibleRegion().GetNumberOfPixels();
	for (long it = 0; it < numPixels; ++it)
	{
		maskBufferPointer[it] = imageBufferPointer[it]<=otsuThld?maskValue:0;
	}

	return mask;
}



template< typename InputImageType, typename OutputImageType >
	typename OutputImageType::Pointer
castItkImage( const InputImageType* inputImage )
{
	typedef itk::CastImageFilter< InputImageType, OutputImageType > itkCastFilter_t;

	typename itkCastFilter_t::Pointer caster = itkCastFilter_t::New();
	caster->SetInput( inputImage );
	caster->Update();

	return caster->GetOutput();
}

//itkUCharImageType::Pointer processTile(cv::Mat thisTileCV, float otsuRatio = 1.0, double curvatureWeight = 0.8, float sizeThld = 3, float sizeUpperThld = 200, double mpp = 0.25)
cv::Mat processTile(cv::Mat thisTileCV, float otsuRatio = 1.0, double curvatureWeight = 0.8, float sizeThld = 3, float sizeUpperThld = 200, double mpp = 0.25)
{
	float meanT[3] = {-0.632356, -0.0516004, 0.0376543};
	float stdT[3] = {0.26235, 0.0514831, 0.0114217}; ///< These are learnt from the tempalte GBM image selected by George
	cv::Mat newImgCV = nscale::Normalization::normalization(thisTileCV, meanT, stdT);

	float mData[8] = {-0.154, 0.035, 0.549, -45.718, -0.057, -0.817, 1.170, -49.887};
	cv::Mat M = cv::Mat(2, 4, CV_32FC1, &mData);

	cv::Mat maskCV = nscale::Normalization::segFG(newImgCV, M);
	itkUCharImageType::Pointer foregroundMask = itk::OpenCVImageBridge::CVMatToITKImage< itkUCharImageType >( maskCV );

	itkRGBImageType::Pointer thisTile = itk::OpenCVImageBridge::CVMatToITKImage< itkRGBImageType >( thisTileCV );

	itkUCharImageType::Pointer hematoxylinImage = ExtractHematoxylinChannel(thisTile);



	short maskValue = 1;

	itkFloatImageType::Pointer hemaFloat = castItkImage<itkUCharImageType, itkFloatImageType>(hematoxylinImage);

	itkBinaryMaskImageType::Pointer nucleusBinaryMask = otsuThresholdImage(hemaFloat, maskValue, otsuRatio);
	long numPixels = nucleusBinaryMask->GetLargestPossibleRegion().GetNumberOfPixels();

	if (foregroundMask)
	{
		const itkUCharImageType::PixelType* fgMaskBufferPointer = foregroundMask->GetBufferPointer();
		itkBinaryMaskImageType::PixelType* nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();

		for (long it = 0; it < numPixels; ++it)
		{
			if (0 == fgMaskBufferPointer[it])
			{
				// for sure glass region
				nucleusBinaryMaskBufferPointer[it] = 0;
			}
		}
	}


	int numiter = 100;
	CSFLSLocalChanVeseSegmentor2D< itkFloatImageType::PixelType > cv;
	cv.setImage(hemaFloat);
	cv.setMask( nucleusBinaryMask );
	cv.setNumIter(numiter);
	cv.setCurvatureWeight(curvatureWeight);
	cv.doSegmenation();

	CSFLSLocalChanVeseSegmentor2D< itkFloatImageType::PixelType >::LSImageType::Pointer phi = cv.mp_phi;

	itkUCharImageType::PixelType* nucleusBinaryMaskBufferPointer = nucleusBinaryMask->GetBufferPointer();
	CSFLSLocalChanVeseSegmentor2D< itkFloatImageType::PixelType >::LSImageType::PixelType* phiBufferPointer = phi->GetBufferPointer();

	for (long it = 0; it < numPixels; ++it)
	{
		nucleusBinaryMaskBufferPointer[it] = phiBufferPointer[it]<=1.0?1:0;
	}

	gth818n::BinaryMaskAnalysisFilter binaryMaskAnalyzer;
	binaryMaskAnalyzer.setMaskImage( nucleusBinaryMask );
	binaryMaskAnalyzer.setObjectSizeThreshold(sizeThld);
	binaryMaskAnalyzer.setObjectSizeUpperThreshold(sizeUpperThld);
	binaryMaskAnalyzer.setMPP(mpp);
	binaryMaskAnalyzer.update();

	itkUIntImageType::Pointer sizeLabel = binaryMaskAnalyzer.getConnectedComponentLabelImage();

	const itkUIntImageType::PixelType* sizeLabelBufferPointer = sizeLabel->GetBufferPointer();
	for (long it = 0; it < numPixels; ++it)
	{
		nucleusBinaryMaskBufferPointer[it] = sizeLabelBufferPointer[it] >= 1?1:0;
	}


        typedef itk::BinaryFillholeImageFilter< itkUCharImageType > FilterType;
        FilterType::Pointer filler = FilterType::New();
        filler->SetFullyConnected( 1 );
        filler->SetForegroundValue( 1 );
        filler->SetInput(nucleusBinaryMask);
        filler->Update();

        nucleusBinaryMask = filler->GetOutput();

	Mat binary = itk::OpenCVImageBridge::ITKImageToCVMat< itkUCharImageType >( nucleusBinaryMask  );
	return binary;
//	return nucleusBinaryMask;
}


template void writeImage<itkUCharImageType>(itkUCharImageType::Pointer img, const char *fileName, bool compress);



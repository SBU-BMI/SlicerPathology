#ifndef utilityScalarImage_h_
#define utilityScalarImage_h_

// itk
#include "itkOtsuThresholdImageFilter.h"
#include "itkCastImageFilter.h"
#include "itkBinaryBallStructuringElement.h"
#include "itkBinaryErodeImageFilter.h"
#include "itkGradientMagnitudeImageFilter.h"
#include "itkContourExtractor2DImageFilter.h"

// local
#include "itkTypedefs.h"


namespace ImagenomicAnalytics
{
  namespace ScalarImage
  {
    template< typename ImageType >
    bool isImageAllZero(ImageType* image)
    {
      std::size_t numPixels = image->GetLargestPossibleRegion().GetNumberOfPixels();

      typename ImageType::PixelType z = itk::NumericTraits<typename ImageType::PixelType>::ZeroValue();

      /// Check if the current mask is all zero
      bool imageIsAllZero = true;
      const typename ImageType::PixelType* imageBufferPointer = image->GetBufferPointer();
      for (std::size_t it = 0; it < numPixels; ++it)
        {
          if (imageBufferPointer[it] != z)
            {
              imageIsAllZero = false;
              break;
            }
        }

      return imageIsAllZero;
    }


    template< typename TNull >
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


    template< typename TNull >
    itkUCharImageType::Pointer edgesOfDifferentLabelRegion(itkUIntImageType::Pointer labelImage)
    {
      typedef itk::GradientMagnitudeImageFilter<itkUIntImageType, itkFloatImageType >  GradientMagnitudeImageFilterType;
      GradientMagnitudeImageFilterType::Pointer gradientMagnitudeImageFilter = GradientMagnitudeImageFilterType::New();
      gradientMagnitudeImageFilter->SetInput(labelImage);
      gradientMagnitudeImageFilter->Update();

      itkFloatImageType::Pointer gradImage = gradientMagnitudeImageFilter->GetOutput();
      itkFloatImageType::PixelType* gradImageBufferPointer = gradImage->GetBufferPointer();

      itkUCharImageType::Pointer mask = itkUCharImageType::New();
      mask->SetRegions( gradImage->GetLargestPossibleRegion() );
      mask->Allocate();
      mask->FillBuffer(0);

      itkUCharImageType::PixelType* maskBufferPointer = mask->GetBufferPointer();

      long numPixels = mask->GetLargestPossibleRegion().GetNumberOfPixels();

      for (long it = 0; it < numPixels; ++it)
        {
          if (gradImageBufferPointer[it] >= 0.5)
            {
              maskBufferPointer[it] = 1;
            }
        }


      return mask;
    }


    template< typename TNull >
    itkRGBImageType::Pointer generateSegmentationOverlay(itkRGBImageType::Pointer img, itkUCharImageType::Pointer binaryMask)
    {
      /// Compute the boundary of the mask by erode
      typedef itk::BinaryBallStructuringElement< itkUCharImageType::PixelType, itkUCharImageType::ImageDimension> StructuringElementType;
      StructuringElementType structuringElement;
      int radius = 1;
      structuringElement.SetRadius(radius);
      structuringElement.CreateStructuringElement();

      typedef itk::BinaryErodeImageFilter<itkUCharImageType, itkUCharImageType, StructuringElementType> BinaryErodeImageFilterType;
      BinaryErodeImageFilterType::Pointer erodeFilter = BinaryErodeImageFilterType::New();
      erodeFilter->SetInput(binaryMask);
      erodeFilter->SetErodeValue(1);
      erodeFilter->SetKernel(structuringElement);
      erodeFilter->Update();
      itkUCharImageType::Pointer erodeMask = erodeFilter->GetOutput();

      //std::cout<<"after erosion"<<std::endl<<std::flush;

      itkRGBImageType::Pointer currentTileOverlaySegmentation = itkRGBImageType::New();
      currentTileOverlaySegmentation->SetRegions(img->GetLargestPossibleRegion() );
      currentTileOverlaySegmentation->Allocate();

      itk2DIndexType idx;
      long nx = img->GetLargestPossibleRegion().GetSize(0);
      long ny = img->GetLargestPossibleRegion().GetSize(1);

      RGBPixelType overlayColor;
      overlayColor.SetRed(0);
      overlayColor.SetGreen(255);
      overlayColor.SetBlue(255);

      for (long iy = 0; iy < ny; ++iy )
        {
          idx[1] = iy;
          for (long ix = 0; ix < nx; ++ix )
            {
              idx[0] = ix;

              currentTileOverlaySegmentation->SetPixel(idx, img->GetPixel(idx));

              if (0 == erodeMask->GetPixel(idx) && 1 == binaryMask->GetPixel(idx))
                {
                  currentTileOverlaySegmentation->SetPixel(idx, overlayColor);
                }
            }
        }

      return currentTileOverlaySegmentation;
    }


    template< typename TNull >
    itkUIntImageType::Pointer binaryImageToConnectedComponentLabelImage(itkBinaryMaskImageType::Pointer bwImage)
    {
      typedef itk::ConnectedComponentImageFilter <itkBinaryMaskImageType, itkUIntImageType > ConnectedComponentImageFilterType;
      ConnectedComponentImageFilterType::Pointer connected = ConnectedComponentImageFilterType::New ();
      connected->SetInput(bwImage);
      connected->Update();
      /// Connected component to separate each nucleus
      ////////////////////////////////////////////////////////////////////////////////

      //m_totalNumberOfConnectedComponents = connected->GetObjectCount();

      return connected->GetOutput();
    }


    template< typename TNull >
    void computeBoundingBoxesForAllConnectedComponents(itkUIntImageType::Pointer labelImage, std::vector< int64_t >& allBoundingBoxes)
    {
      //--------------------------------------------------------------------------------
      // The ASSUMPTION is that the labels are sequential from {1, 2,
      // ..., largestLabel}. So the largest label also indicates the
      // number of unique labels. Entire computation will be wrong if
      // this assumption does not hold.
      // ================================================================================
      std::size_t np = labelImage->GetLargestPossibleRegion().GetNumberOfPixels();
      //std::cout<<np<<std::endl;

      const itkUIntImageType::PixelType* labelImageBufferPointer = labelImage->GetBufferPointer();

      itkUIntImageType::PixelType numberOfUniqueNonZeroLabels = 0;

      for (std::size_t ip = 0; ip < np; ++ip)
        {
          numberOfUniqueNonZeroLabels = numberOfUniqueNonZeroLabels>labelImageBufferPointer[ip]?numberOfUniqueNonZeroLabels:labelImageBufferPointer[ip];
        }

      //std::cout<<numberOfUniqueNonZeroLabels<<std::endl;


      /// each object has x0, y0, x1, y1
      int64_t nx = static_cast<int64_t>(labelImage->GetLargestPossibleRegion().GetSize()[0]);
      int64_t ny = static_cast<int64_t>(labelImage->GetLargestPossibleRegion().GetSize()[1]);

      allBoundingBoxes.resize(4*numberOfUniqueNonZeroLabels);
      for (std::size_t it = 0; it < numberOfUniqueNonZeroLabels; ++it)
        {
          allBoundingBoxes[4*it] = nx;
          allBoundingBoxes[4*it+1] = ny;
          allBoundingBoxes[4*it+2] = 0;
          allBoundingBoxes[4*it+3] = 0;
        }

      itk2DIndexType idx;
      for (int64_t iy = 0; iy < ny; ++iy)
        {
          idx[1] = iy;

          for (int64_t ix = 0; ix < nx; ++ix)
            {
              idx[0] = ix;

              itkUIntImageType::PixelType thisLabel = labelImage->GetPixel(idx);

              if (!thisLabel)
                {
                  continue;
                }

              itkUIntImageType::PixelType thisLabelIndex = thisLabel - 1; // label 1 get 0-th place in the bounding box vector

              allBoundingBoxes[4*thisLabelIndex] = allBoundingBoxes[4*thisLabelIndex]<=ix?allBoundingBoxes[4*thisLabelIndex]:ix;
              allBoundingBoxes[4*thisLabelIndex + 1] = allBoundingBoxes[4*thisLabelIndex + 1]<=iy?allBoundingBoxes[4*thisLabelIndex + 1]:iy;

              allBoundingBoxes[4*thisLabelIndex + 2] = allBoundingBoxes[4*thisLabelIndex + 2]>=ix?allBoundingBoxes[4*thisLabelIndex + 2]:ix;
              allBoundingBoxes[4*thisLabelIndex + 3] = allBoundingBoxes[4*thisLabelIndex + 3]>=iy?allBoundingBoxes[4*thisLabelIndex + 3]:iy;
            }
        }

      return;
    }

    template< typename TNull >
    void computeBoundingBoxesForAllConnectedComponents(itkBinaryMaskImageType::Pointer binaryImage, std::vector< int64_t >& allBoundingBoxes)
    {
      itkUIntImageType::Pointer labelImage = binaryImageToConnectedComponentLabelImage<char>(binaryImage);

      computeBoundingBoxesForAllConnectedComponents<char>(labelImage, allBoundingBoxes);

      return;
    }



    template< typename ImageType >
    void extractContour(typename ImageType::Pointer binaryImage, int64_t x0, int64_t y0, \
                        std::vector<double>& contourPoints)
    {
      // typedef itk::ApproximateSignedDistanceMapImageFilter< ImageType, itkFloatImageType  > ApproximateSignedDistanceMapImageFilterType;
      // typename ApproximateSignedDistanceMapImageFilterType::Pointer approximateSignedDistanceMapImageFilter = ApproximateSignedDistanceMapImageFilterType::New();
      // approximateSignedDistanceMapImageFilter->SetInput(binaryImage);
      // approximateSignedDistanceMapImageFilter->SetInsideValue(1);
      // approximateSignedDistanceMapImageFilter->SetOutsideValue(0);
      // approximateSignedDistanceMapImageFilter->Update();

      // typedef itk::DiscreteGaussianImageFilter<ImageType, itkFloatImageType >  GaussianFilterType;
      // double variance = 0.1;
      // typename GaussianFilterType::Pointer gaussianFilter = GaussianFilterType::New();
      // gaussianFilter->SetInput( binaryImage );
      // gaussianFilter->SetVariance(variance);
      // gaussianFilter->Update();


      //typedef itk::ContourExtractor2DImageFilter <itkFloatImageType> ContourExtractor2DImageFilterType;
      typedef itk::ContourExtractor2DImageFilter <ImageType> ContourExtractor2DImageFilterType;
      typename ContourExtractor2DImageFilterType::Pointer contourExtractor2DImageFilter = ContourExtractor2DImageFilterType::New();
      //contourExtractor2DImageFilter->SetInput(gaussianFilter->GetOutput());
      contourExtractor2DImageFilter->SetInput(binaryImage);
      contourExtractor2DImageFilter->SetContourValue(0.5);
      contourExtractor2DImageFilter->Update();

      // std::cout<<"here 2\n"<<std::flush;

      // std::cout << "There are " << contourExtractor2DImageFilter->GetNumberOfOutputs() << " contours" << std::endl;

      contourPoints.clear();
      for(unsigned int i = 0; i < contourExtractor2DImageFilter->GetNumberOfOutputs(); ++i)
        {
          //std::cout << "Contour " << i << ": " << std::endl;

          typename ContourExtractor2DImageFilterType::VertexListType::ConstIterator vertexIterator = contourExtractor2DImageFilter->GetOutput(i)->GetVertexList()->Begin();
          while(vertexIterator != contourExtractor2DImageFilter->GetOutput(i)->GetVertexList()->End())
            {
              //std::cout << vertexIterator->Value() << std::endl;

              contourPoints.push_back(x0 + vertexIterator->Value()[0]);
              contourPoints.push_back(y0 + vertexIterator->Value()[1]);
              ++vertexIterator;
            }
          //std::cout << std::endl;
        }

      return;
    }
  }
}// namespace


#endif

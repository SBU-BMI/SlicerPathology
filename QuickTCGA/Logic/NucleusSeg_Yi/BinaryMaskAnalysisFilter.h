#ifndef BinaryMaskAnalysisFilter_h_
#define BinaryMaskAnalysisFilter_h_


// itk
#include "itkImage.h"
#include "itkConnectedComponentImageFilter.h"
#include "itkLabelImageToShapeLabelMapFilter.h"

// // local
// #include "itkTypedefs.h"


namespace gth818n
{
  class BinaryMaskAnalysisFilter
  {
  public:
    //typedef BinaryMaskAnalysisFilter Self;

    ////////////////////////////////////////////////////////////////////////////////
    /// ctor
    BinaryMaskAnalysisFilter();
    ~BinaryMaskAnalysisFilter() {}
    /// ctor, end
    ////////////////////////////////////////////////////////////////////////////////


    ////////////////////////////////////////////////////////////////////////////////
    /// typedef
    static const unsigned int ImageDimension = 2;
    typedef itk::Image<unsigned char, ImageDimension> itkUCharImageType;
    typedef itkUCharImageType itkBinaryMaskImageType;

    typedef itk::Image<float, ImageDimension> itkFloatImageType;

    typedef itk::Image<unsigned long, ImageDimension> itkULongImageType;
    typedef itk::Image<unsigned int, ImageDimension> itkUIntImageType;
    typedef itk::Image<int, ImageDimension> itkIntImageType;
    typedef itkUIntImageType itkLabelImageType;

    /// typedef, end
    ////////////////////////////////////////////////////////////////////////////////


    ////////////////////////////////////////////////////////////////////////////////
    /// public fn
    void setMaskImage(const itkBinaryMaskImageType* img);

    void setObjectSizeThreshold(float sizeThld) {m_objectSizeThreshold = sizeThld;}
    void setObjectSizeUpperThreshold(float sizeUpperThld) {m_objectSizeUpperThreshold = sizeUpperThld;}

    void setMPP(float mpp);

    void setKernelSize(double ks);

    itkFloatImageType::Pointer getFeatureColoredImage(unsigned char featureType);
    itkLabelImageType::Pointer getConnectedComponentLabelImage();

    void update();

    const std::vector<double>& getObjectAreas(); ///< mpp^2 * numberOfPixels where the numberOfPixels part does not respect image spcing (mpp)
    const std::vector<double>& getObjectPerimeters(); ///< spacing affects this in LabelImageToShapeLabelMapFilter
    const std::vector<double>& getObjectEquivalentSphericalRadius(); ///< spacing affects this in LabelImageToShapeLabelMapFilter
    /// public fn, end
    ////////////////////////////////////////////////////////////////////////////////


  private:
    typedef itk::Index<ImageDimension> itk2DIndexType;
    ////////////////////////////////////////////////////////////////////////////////
    /// The max of <unsigned int>, as tested in
    /// ../test/mainNumericTraits.cxx, is 4G. Should be large enough for
    /// representing the label of each nucleus in a tile. Enough for a
    /// WSI?
    ///
    /// typedef unsigned int LabelType;
    /// typedef itk::Image< LabelType, Dimension > LabelImageType;

    typedef itk::ShapeLabelObject< itkLabelImageType::PixelType, itkLabelImageType::ImageDimension > ShapeLabelObjectType;
    typedef itk::LabelMap< ShapeLabelObjectType >         LabelMapType;
    typedef itk::LabelImageToShapeLabelMapFilter< itkLabelImageType, LabelMapType> I2LType;


    ////////////////////////////////////////////////////////////////////////////////
    /// private data
    const itkBinaryMaskImageType* m_inputImage;
    itkBinaryMaskImageType::Pointer m_binaryMask;
    itkLabelImageType::Pointer m_connectedComponentLabelImage;

    itkFloatImageType::Pointer m_featureColoredImage; ///< as the genearl output channel if want to color the object by some feature. So that we don't have to have separated "colorBySize", "colorBySizePerimeterRatio" etc.

    LabelMapType::Pointer m_labelMap;

    float m_mpp; ///< Micron Per Pixel

    double m_kernelSize;

    float m_objectSizeThreshold; ///< object smaller than this will be discarded. unit in physical spaces

    float m_objectSizeUpperThreshold; ///< object larger than this will be broken. unit in physical spaces


    /// coputed features
    unsigned int m_numberOfObjects; ///< I will use "Object" as well as "Connected Component"
    std::vector<double> m_objectAreas;
    std::vector<double> m_objectPerimeters;
    std::vector<double> m_objectEquivalentSphericalRadius;
    //std::vector<double> m_objectNecessityOfBreaking;
    std::vector<char> m_objectToBreak;
    /// coputed features, end


    bool m_allDone;
    /// private data, end
    ////////////////////////////////////////////////////////////////////////////////


    ////////////////////////////////////////////////////////////////////////////////
    /// private fn
    void _computeConnectedComponentsLabelImage();
    void _computeLabelMap();
    void _computeObjectFeatures();
    void _findObjectsToBreak();

    //void _computeObjectNecessityOfBreakingValues();

    void _colorObjectByFeature(unsigned char featureType);
    void _breakRegion();
    /// private fn
    ////////////////////////////////////////////////////////////////////////////////
  };

}// namespace gth818n


#endif // BinaryMaskAnalysisFilter_h_

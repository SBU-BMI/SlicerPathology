#ifndef HierarchicalMeanshiftClusteringFilter_hxx_
#define HierarchicalMeanshiftClusteringFilter_hxx_

#include "itkNumericTraits.h"
#include "vnl/vnl_random.h"

#include "HierarchicalMeanshiftClusteringFilter.h"
#include "MeanshiftClusteringFilter.h"

namespace gth818n
{

  template< typename TCoordRep, unsigned int NPointDimension >
  HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::HierarchicalMeanshiftClusteringFilter() : m_outputStream(std::cout)
  {
    m_inputPointSet = 0;

    //m_subsampleRatio = 0.1;
    m_subsampleRatio = -1;

    m_radius = 3.0;
    m_allDone = false;
  }

  template< typename TCoordRep, unsigned int NPointDimension >
  HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::HierarchicalMeanshiftClusteringFilter(std::ostream& logFileStream) : m_outputStream(logFileStream)
  {
    m_inputPointSet = 0;

    //m_subsampleRatio = 0.1;
    m_subsampleRatio = -1;

    m_radius = 3.0;
    m_allDone = false;
  }



  template< typename TCoordRep, unsigned int NPointDimension >
  int HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::_prepareForRun()
  {
    if (0 == m_inputPointSet->Size())
      {
        m_outputStream<<"Error: means shift input point set is empty.\n";
        abort();
      }

    if (m_subsampleRatio < 0)
      {
        /// since in setSubSampleRatio(), it was checked if (ratio <=
        /// 0.0 || ratio > 1.0), so the only situation this happens is
        /// because m_subsampleRatio has not been touched and should
        /// be -1

        _computeOptimalSubSampleRatio();
      }

    return 0;
  }

  template< typename TCoordRep, unsigned int NPointDimension >
  void HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::_computeOptimalSubSampleRatio()
  {
    /// find a m_subsampleRatio so that there are 1000 points for mean shift
    if (m_inputPointSet->Size() <= 1000)
      {
        m_subsampleRatio = 1.0;
      }
    else
      {
        m_subsampleRatio = 1000.0/static_cast<double>(m_inputPointSet->Size());
      }

    return;
  }



  template< typename TCoordRep, unsigned int NPointDimension >
  void HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::update()
  {
    m_outputStream<<"In HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::update()\n"<<std::flush;

    _prepareForRun();

    m_outputStream<<"In HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::update(), before sub-sampling\n"<<std::flush;
    std::cout<<"In HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::update(), before sub-sampling\n"<<std::flush;
    m_outputStream<<"m_subsampleRatio = "<<m_subsampleRatio<<std::endl<<std::flush;
    std::cout<<"m_subsampleRatio = "<<m_subsampleRatio<<std::endl<<std::flush;
    
    /// Sub-sample input point set
    typename VectorSampleType::Pointer subsample = VectorSampleType::New();

    subsample->PushBack(m_inputPointSet->GetMeasurementVector(0) ); ///< so the subsample is never empty.

    vnl_random rg;
    for (unsigned int i = 1 ; i < m_inputPointSet->Size() ; ++i ) ///< since 0-th has been pushed in, here start with 1
      {
        if (rg.drand64() <= m_subsampleRatio)
          {
            subsample->PushBack(m_inputPointSet->GetMeasurementVector(i) );
          }
      }

    m_outputStream<<"before mean shift\n"<<std::flush;
    std::cout<<"before mean shift\n"<<std::flush;

    /// Run mean shift on sub-sample
    typedef gth818n::MeanshiftClusteringFilter<TCoordRep, NPointDimension> MeanshiftClusteringFilterType;
    MeanshiftClusteringFilterType ms;
    ms.setInputPointSet(subsample);
    ms.setRadius(m_radius);
    ms.update();

    m_outputStream<<"after mean shift\n"<<std::flush;
    std::cout<<"after mean shift\n"<<std::flush;


    /// Get label back to input point set by closest point criteria
    std::vector<long> sublabel = ms.getLabelOfPoints();
    m_centers = ms.getCenters();

    typedef typename itk::Statistics::KdTreeGenerator< VectorSampleType > TreeGeneratorType;
    typedef typename TreeGeneratorType::KdTreeType TreeType;
    //typedef typename TreeType::NearestNeighbors NeighborsType;
    //typedef typename TreeType::KdTreeNodeType NodeType;

    typename TreeGeneratorType::Pointer subTreeGenerator = TreeGeneratorType::New();
    subTreeGenerator->SetSample( subsample );
    subTreeGenerator->SetBucketSize( 16 );
    subTreeGenerator->Update();
    typename TreeType::Pointer subtree = subTreeGenerator->GetOutput();

    unsigned int numberOfNeighbors = 1;
    typename TreeType::InstanceIdentifierVectorType neighbors;

    m_labelOfPoints.resize(m_inputPointSet->Size());

    for (unsigned int i = 0 ; i < m_inputPointSet->Size() ; ++i )
      {
        const VectorType& queryPoint = m_inputPointSet->GetMeasurementVector(i);
        subtree->Search( queryPoint, numberOfNeighbors, neighbors ) ;
        m_labelOfPoints[i] = static_cast<long>(sublabel[neighbors[0]]);
      }


    m_outputStream<<"done with hierachical mean shift\n"<<std::flush;
    std::cout<<"done with hierachical mean shift\n"<<std::flush;


    m_allDone = true;

    return;
  }

  template< typename TCoordRep, unsigned int NPointDimension >
  void HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::setRadius(RealType rad)
  {
    if (rad <= 0.0)
      {
        m_outputStream<<"Error: rad should > 0, but got "<<rad<<std::endl;
        abort();
      }

    m_radius = rad;

    return;
  }

  template< typename TCoordRep, unsigned int NPointDimension >
  void HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::setSubsampleRatio(RealType ratio)
  {
    if (ratio <= 0.0 || ratio > 1.0)
      {
        m_outputStream<<"Error: ratio should in (0, 1], but got "<<ratio<<std::endl;
        abort();
      }

    m_subsampleRatio = ratio;

    return;
  }


  template< typename TCoordRep, unsigned int NPointDimension >
  typename HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::VectorSampleType::Pointer
  HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::getCenters()
  {
    if (!m_allDone)
      {
        m_outputStream<<"Error: not done.\n";
      }

    return m_centers;
  }


  template< typename TCoordRep, unsigned int NPointDimension >
  std::vector<long>
  HierarchicalMeanshiftClusteringFilter<TCoordRep, NPointDimension>::getLabelOfPoints()
  {
    if (!m_allDone)
      {
        m_outputStream<<"Error: not done.\n";
      }

    return m_labelOfPoints;
  }


}// namespace gth818n


#endif

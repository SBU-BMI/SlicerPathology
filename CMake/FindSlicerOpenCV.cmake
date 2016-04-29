# For the Slicer dashboard, the build directories should be at the same level.
set(SOCV_CONFIG_PATHS
        ${OpenCVExample_BINARY_DIR}/../SlicerOpenCV-build/inner-build
)

find_file(
        SLICEROPENCV_CONFIG_FILE
        SlicerOpenCVConfig.cmake
        PATHS ${SOCV_CONFIG_PATHS}
        DOC "The path to the SlicerOpenCVConfig.cmake file"
         )
message(STATUS "FindSlicerOpenCV: SLICEROPENCV_CONFIG_FILE = ${SLICEROPENCV_CONFIG_FILE}")
include(${SLICEROPENCV_CONFIG_FILE})
message(STATUS "FindSlicerOpenCV: SlicerOpenCV_DIR set to = ${SlicerOpenCV_DIR}")


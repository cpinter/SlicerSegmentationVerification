cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SegmentationVerification)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/cpinter/SlicerSegmentationVerification")
set(EXTENSION_CONTRIBUTORS "Csaba Pinter (EBATINCA, S.L.)")
set(EXTENSION_DESCRIPTION "Tools for verifying the result of AI segmentation.")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/cpinter/SlicerSegmentationVerification/main/SegmentationVerification.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/cpinter/SlicerSegmentationVerification/main/SegmentationVerification_Screenshot.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SegmentationVerification)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})

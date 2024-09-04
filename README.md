# Segmentation Verification

Extension containing a 3D Slicer module (Segmentation Verification) for verifying the result of AI segmentation. The module allows quick review of each segment (mask, label) in a segmentation.

![image](https://raw.githubusercontent.com/cpinter/SlicerSegmentationVerification/main/SegmentationVerification.png)

https://github.com/NA-MIC/ProjectWeek/assets/1325980/77379558-be9d-4c17-a1a9-a38f78384d4b

For reference, the related [Slicer Project Week #41 project page](https://github.com/NA-MIC/ProjectWeek/blob/master/PW41_2024_MIT/Projects/SegmentationVerificationModuleForFinalizingMultiLabelAiSegmentations/README.md)

## How to use

1. Achieve a new AI segmentation (for example by using the [TotalSegmentator](https://github.com/lassoan/SlicerTotalSegmentator) or [MONAIAuto3DSeg](https://github.com/lassoan/SlicerMONAIAuto3DSeg) extension)
    - As an alternative you can download a sample dataset from [Imaging Data Commons](https://github.com/ImagingDataCommons/idc-index):
        - Programatically
            - `pip install --upgrade idc-index`
            - `idc download-from-selection --study-instance-uid 1.2.840.113654.2.55.119867199987299072242360817545965112631 --download-dir .`
        - You can also download it using `SlicerIDCBrowser` by pasting the UID into the study field (see [forum topic](https://discourse.slicer.org/t/sliceridcbrowser-extension-released/32279/2))
        - Or the [IDC portal on the web](https://portal.imaging.datacommons.cancer.gov/explore/)
    - Load the downloaded data as DICOM (you will need the DCMQI extension but you have it if you already installed the IDCBrowser)
2. Open the Segmentation Verification module
3. Select the new segmentation if it is not already selected
4. Click on any segment to show only that one in the slice views and the 3D view as well

By going through the segments one by one and reviewing them against the anatomical image, you can evaluate the accuracy of the automatic segmentation of that specific segment.

Other options:
- If you check the "Show neighboring segments semi-transparent" checkbox, the neighboring (spatially adjacent) segments will be shown as well
- The "Previous" and "Next" buttons facilitate stepping between the segments

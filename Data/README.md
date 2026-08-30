# Data Directory

This directory contains the data files used as inputs for the secondary computational analyses reported in the associated study:

**Process-Level Insights into Fenton and Photo-Fenton Treatment of Textile and Dye-Intermediate Wastewater: An In Silico Treatment-Response Analysis within a Fe²⁺:H₂O₂ Ratio Window**

The files include the extracted source data and analysis-ready datasets prepared for the individual computational workflows.

## Data Provenance

The analysis was based exclusively on previously published experimental datasets. No new experimental measurements were generated as part of the present computational study.

The source datasets were obtained from:

1. **Pollution assessment of untreated textile and dye-intermediate wastewater in Ahmedabad Industrial Estate, Gujarat, India: Implications for water quality management for effective treatment strategies**

   DOI: [10.17632/bxpj4h3m7y.1](https://doi.org/10.17632/bxpj4h3m7y.1)

2. **Lab-scale investigation of Fenton and Photo-Fenton processes for removal of pollutant from textile and dye-intermediate industrial wastewater, Ahmedabad Industrial Estate, Gujarat, India**

   DOI: [10.17632/89nhkwnc9y.1](https://doi.org/10.17632/89nhkwnc9y.1)

Both original datasets are available under the **CC BY 4.0** license.

## Data Workflow

The data files are numbered according to their position in the computational workflow:

**00 → 10 → 20 → 30 → 40 → 50 → 60 → 70**

where each stage corresponds to a progressively prepared dataset used by the associated Python analysis script.

| Stage  | Analysis                                                    | Input file(s)                                                                                                                                     | Associated code               |
| ------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| **00** | Original extracted data                                     | `00_OriginalExtractedData.xlsx`                                                                                                                   | Source/extraction dataset     |
| **10** | Preliminary evaluation and secondary descriptor preparation | `11PrimaryWastewaterData4LogBar.xlsx`<br>`12SecondaryWastewaterData4LogBar.xlsx`                                                                  | `C10LogBar.py`                |
| **20** | Post-treatment residual concentration profiling             | `21T_FData4LogTreatmentBar.xlsx`<br>`22T_PFData4LogTreatmentBar.xlsx`<br>`23DI_FData4LogTreatmentBar.xlsx`<br>`24DI_PFData4LogTreatmentBar.xlsx`  | `C20LogTreatmentBar.py`       |
| **30** | Incremental Treatment Response (ITR) analysis               | `31T_FData4ITRA.xlsx`<br>`32T_PFData4ITRA.xlsx`<br>`33DI_FData4ITRA.xlsx`<br>`34DI_PFData4ITRA.xlsx`                                              | `C30ITRA.py`                  |
| **40** | Incremental Response Index (IRI)                            | `41Data4IRI.xlsx`                                                                                                                                 | `C40IRI.py`                   |
| **50** | Random Forest regression and variable importance analysis   | `51Data4RandomForest.xlsx`                                                                                                                        | `C50RandomForest.py`          |
| **60** | Response surface analysis                                   | `61Data4DosePerformanceRSM.xlsx`<br>`62Data4MatrixEvolutionRSM.xlsx`<br>`63Data4OpticalInterferenceRSM.xlsx`<br>`64Data4TreatmentDynamicRSM.xlsx` | `C60RSM.py`                   |
| **70** | Multi-response Derringer desirability optimization          | `71Data4DerringerDesirability.xlsx`                                                                                                               | `C70DerringerDesirability.py` |

## Wastewater Matrix and Treatment Abbreviations

The datasets contain two wastewater matrices:

* **T** — Textile wastewater
* **DI** — Dye-intermediate wastewater

Treatment-process abbreviations are:

* **F** — Fenton treatment
* **PF** — Photo-Fenton treatment

Accordingly:

* `T_F` = Textile wastewater treated by Fenton
* `T_PF` = Textile wastewater treated by Photo-Fenton
* `DI_F` = Dye-intermediate wastewater treated by Fenton
* `DI_PF` = Dye-intermediate wastewater treated by Photo-Fenton

## File Naming Convention

The numerical prefixes identify the computational stage:

* `00` — original extracted data
* `10` — preliminary evaluation
* `20` — residual concentration profiling
* `30` — Incremental Treatment Response analysis
* `40` — Incremental Response Index
* `50` — Random Forest analysis
* `60` — response surface analysis
* `70` — multi-response desirability optimization

The suffixes identify the specific analysis or wastewater-treatment configuration where applicable.

## Derived Analysis Datasets

The numbered datasets after `00_OriginalExtractedData.xlsx` are analysis-ready files prepared for the corresponding computational procedures. They should therefore be regarded as **derived working datasets**, rather than independent experimental datasets.

The original experimental measurements remain attributable to the published source datasets identified above.

## Reproducibility

The Excel files in this directory are provided to allow the computational workflow to be followed from the extracted source data through the individual analysis stages.

The corresponding Python scripts are located in the parent repository. The relationship between each script and its input dataset is documented in the main repository `README.md`.

Users reproducing the analysis should use the data files together with the corresponding Python scripts and the software environment specified in the parent repository.

## Data Integrity

The data files were prepared for the analyses reported in the associated manuscript. Any transformation, restructuring, calculation of secondary descriptors, or preparation of analysis-specific datasets should be interpreted in the context of the corresponding computational script.

The Python scripts provide the computational procedures used to process and analyze these data.

## License and Attribution

The original experimental datasets are available under the **CC BY 4.0** license. Appropriate attribution should be provided when the original data are reused.

The analysis-ready datasets in this repository are provided as part of the computational workflow accompanying the study.

For details of the code license, see the `LICENSE` file in the parent repository.

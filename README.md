# Codes_Fenton_PhotoFenton_Treatment_Response_Analysis
Reproducible Python workflow for process-level treatment-response analysis and optimization of Fenton/Photo-Fenton wastewater treatment.

# Process-Level Treatment-Response Analysis of Fenton and Photo-Fenton Oxidation

**Reproducible Python workflow for process-level treatment-response analysis and optimization of Fenton/Photo-Fenton wastewater treatment.**

Python scripts accompanying the study:

**Process-Level Insights into Fenton and Photo-Fenton Treatment of Textile and Dye-Intermediate Wastewater: An In Silico Treatment-Response Analysis within a Fe²⁺:H₂O₂ Ratio Window**

## Overview

This repository contains the Python scripts used for the secondary computational analysis of previously published experimental datasets on Fenton and Photo-Fenton treatment of textile and dye-intermediate industrial wastewater.

The wastewater characterization data were obtained from:

* **Pollution assessment of untreated textile and dye-intermediate wastewater in Ahmedabad Industrial Estate, Gujarat, India: Implications for water quality management for effective treatment strategies**
  DOI: [10.17632/bxpj4h3m7y.1](https://doi.org/10.17632/bxpj4h3m7y.1)

* **Lab-scale investigation of Fenton and Photo-Fenton processes for removal of pollutant from textile and dye-intermediate industrial wastewater, Ahmedabad Industrial Estate, Gujarat, India**
  DOI: [10.17632/89nhkwnc9y.1](https://doi.org/10.17632/89nhkwnc9y.1)

Both datasets are available under the **CC BY 4.0** license.

No new experimental data were generated as part of the present computational study. The analyses reported in the associated manuscript were performed using the previously published experimental data.

## Computational Workflow

The computational workflow includes:

* secondary wastewater descriptor calculation;
* post-treatment residual concentration profiling;
* Incremental Treatment Response (ITR) analysis;
* Incremental Response Index (IRI) analysis;
* Random Forest regression and variable importance analysis;
* response surface analysis; and
* multi-response Derringer desirability optimization.

## Computational Workflow and Code–Data Mapping

| Process                                                       | Code                          | Code developed with AI assistance | Input data                                                                                                                                         |
| ------------------------------------------------------------- | ----------------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Preliminary Evaluation**                                    | `C10LogBar.py`                | Google Gemini                     | `11PrimaryWastewaterData4LogBar.xlsx`<br>`12SecondaryWastewaterData4LogBar.xlsx`                                                                   |
| **Post-Treatment Residual Concentration Profiling**           | `C20LogTreatmentBar.py`       | Google Gemini                     | `21T_FData4LogTreatmentBar.xlsx`<br>`22T_PFData4LogTreatmentBar.xlsx`<br>`23DI_FData4LogTreatmentBar.xlsx`<br>`24DI_PFData4LogTreatmentBar.xlsx`   |
| **Incremental Treatment Response (ITR) Analysis**             | `C30ITRA.py`                  | Anthropic Claude                  | `31T_FData4ITRA.xlsx`<br>`32T_PFData4ITRA.xlsx`<br>`33DI_FData4ITRA.xlsx`<br>`34DI_PFData4ITRA.xlsx`                                               |
| **Incremental Response Index (IRI)**                          | `C40IRI.py`                   | Anthropic Claude                  | `41Data4IRI.xlsx`                                                                                                                                  |
| **Random Forest Regression and Variable Importance Analysis** | `C50RandomForest.py`          | Anthropic Claude                  | `51Data4RandomForest.xlsx`                                                                                                                         |
| **Response Surface Analysis**                                 | `C60RSM.py`                   | Anthropic Claude                  | `61Data4DosePerformanceRSM.xlsx`<br>`62Data4MatrixEvolutionRSM.xlsx`<br>`63Data4OpticalInterferenceRSM.xlsx`<br>`64Data4TreatmentDynamicsRSM.xlsx` |
| **Multi-response Derringer Desirability Optimization**        | `C70DerringerDesirability.py` | Anthropic Claude                  | `71Data4DerringerDesirability.xlsx`                                                                                                                |

## Software Requirements

The computational analyses were performed using **Python 3.11**. The principal Python packages and versions used in the analysis are listed below.

| Software/Package | Version |
| ---------------- | ------: |
| Python           |    3.11 |
| NumPy            |  1.26.4 |
| pandas           |   3.0.0 |
| scikit-learn     |   1.6.1 |
| SciPy            |  1.11.4 |
| Matplotlib       |  3.10.0 |
| Plotly           |  5.18.0 |

The required Python packages are also provided in [`requirements.txt`](requirements.txt) to facilitate reproduction of the computational analyses.

## Reproducibility

The scripts in this repository correspond to the computational procedures used to generate the analyses and results reported in the associated manuscript.

For reproducibility, users should:

1. Install Python 3.11.
2. Install the required packages listed in `requirements.txt`.
3. Place the required input datasets in the appropriate directory.
4. Run the corresponding Python script for the desired analysis.
5. Use the generated outputs for comparison with the analyses and figures reported in the manuscript.

The numerical and analytical procedures in the scripts were reviewed, modified, and tested by the authors.

## AI-Assisted Code Development

Portions of the Python scripts were initially developed with assistance from **Google Gemini** and **Anthropic Claude**. The scripts were subsequently reviewed, modified, tested, and finalized by the authors.

The authors take full responsibility for the final code, analytical procedures, results, and interpretations reported in the associated study.

## Data Availability

The experimental datasets used as inputs for this secondary computational analysis were obtained from the previously published datasets identified above.

The original datasets are available under the **CC BY 4.0** license through their respective data repositories.

Users should cite the original dataset publications in addition to citing the associated research article when using the data.

## Code Availability

The Python source code used for the computational analyses is openly available in this repository:

**GitHub:**
https://github.com/paulat0grant/Codes_Fenton_PhotoFenton_Treatment_Response_Analysis

A versioned release corresponding to the manuscript should be archived separately with a persistent DOI for long-term citation and reproducibility.

## Citation

If you use the code or computational workflow from this repository, please cite the associated research article.

If you use the original experimental datasets, please also cite the corresponding dataset sources listed in the **Data Availability** section.

## License

The Python code in this repository is distributed under the **MIT License**.

The experimental datasets used in this study are subject to their respective **CC BY 4.0** license terms.

See the `LICENSE` file for the complete MIT License terms.


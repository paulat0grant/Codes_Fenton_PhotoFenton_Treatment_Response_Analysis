# Codes_Fenton_PhotoFenton_Treatment_Response_Analysis
Reproducible Python workflow for process-level treatment-response analysis and optimization of Fenton/Photo-Fenton wastewater treatment.

# Process-Level Treatment-Response Analysis of Fenton and Photo-Fenton Oxidation

Python scripts accompanying the study:

**Process-Level Insights into Fenton and Photo-Fenton Treatment of
Textile and Dye-Intermediate Wastewater: An In Silico Treatment-Response
Analysis within a Fe²⁺:H₂O₂ Ratio Window**

This repository contains the Python scripts used for the secondary
computational analysis of a previously published experimental dataset
on Fenton and Photo-Fenton treatment of textile and dye-intermediate
wastewater. Untreated data collected from “Pollution assessment of untreated textile and dye-intermediate wastewater in Ahmedabad Industrial Estate, Gujarat, India: Implications for water quality management for effective treatment strategies” (doi: https://doi.org/10.17632/bxpj4h3m7y.1). And treatment data collected from “Lab-scale investigation of Fenton and Photo-Fenton processes for removal of pollutant from textile and dye-intermediate industrial wastewater, Ahmedabad Industrial Estate, Gujarat, India” (doi: https://doi.org/10.17632/89nhkwnc9y.1).

The workflow includes:

- secondary wastewater descriptor calculation;
- residual treatment-response profiling;
- Incremental Response Index (IRI) analysis;
- Random Forest regression and variable importance analysis;
- response surface analysis; and
- multi-response Derringer desirability optimization.

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




> **AI-assisted code development:** Portions of the Python scripts were initially developed with assistance from Google Gemini and Anthropic Claude. The scripts were subsequently reviewed, modified, tested, and finalized by the authors. The authors take full responsibility for the final code, analytical procedures, results, and interpretations.

The scripts were used to generate the analyses and results reported
in the associated manuscript.

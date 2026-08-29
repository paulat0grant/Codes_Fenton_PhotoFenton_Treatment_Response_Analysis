# Code developed with Gemini assistance on 19 July 2026


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Define the Excel file path
# Ensure this matches your exact filename in your working folder
excel_file = "Prelim.xlsx"

if not os.path.exists(excel_file):
    raise FileNotFoundError(f"Please ensure '{excel_file}' is in your active directory.")

# 2. Read Sheet 1 ("Raw_Effluent_Data") natively from the .xlsx file
# We use sheet_name=0 to target the very first sheet
df_raw = pd.read_excel(excel_file, sheet_name=0)

# Clean up column names to strip out hidden spaces
df_raw.columns = df_raw.columns.str.strip()

print("=== SUCESSFULLY READ RAW EFFLUENT DATA FROM EXCEL ===")

# 3. Perform Physicochemical Ratio Calculations
# Extracting exact cell values based on rows matching the parameters
def get_val(param_name, column):
    return float(df_raw.loc[df_raw['Parameter'].str.strip() == param_name, column].values[0])

textile_ph = get_val('pH', 'Textile Effluent')
textile_tss = get_val('TSS (mg/l)', 'Textile Effluent')
textile_tds = get_val('TDS (mg/l)', 'Textile Effluent')
textile_cod = get_val('COD (mg/l)', 'Textile Effluent')
textile_nitrate = get_val('Nitrate (mg/l)', 'Textile Effluent')
textile_turbidity = get_val('Turbidity (NTU)', 'Textile Effluent')
textile_color = get_val('Colour (Pt. Co.)', 'Textile Effluent')

dye_ph = get_val('pH', 'Dye Intermediate')
dye_tss = get_val('TSS (mg/l)', 'Dye Intermediate')
dye_tds = get_val('TDS (mg/l)', 'Dye Intermediate')
dye_cod = get_val('COD (mg/l)', 'Dye Intermediate')
dye_nitrate = get_val('Nitrate (mg/l)', 'Dye Intermediate')
dye_turbidity = get_val('Turbidity (NTU)', 'Dye Intermediate')
dye_color = get_val('Colour (Pt. Co.)', 'Dye Intermediate')

# Mathematical Domain Ratios
ratio_tss_tds_textile = textile_tss / textile_tds
ratio_tss_tds_dye = dye_tss / dye_tds

ratio_nitrate_cod_textile = textile_nitrate / textile_cod
ratio_nitrate_cod_dye = dye_nitrate / dye_cod

od_proxy_textile = textile_turbidity * textile_color
od_proxy_dye = dye_turbidity * dye_color

# Print Summary Tables for Manuscript Text
print("\n--- Calculated Chemical Modeling Parameters ---")
print(f"Textile TSS/TDS Ratio: {ratio_tss_tds_textile:.4f}")
print(f"Dye-Intermediate TSS/TDS Ratio: {ratio_tss_tds_dye:.4f} (Textile is {ratio_tss_tds_textile/ratio_tss_tds_dye:.1f}x higher in particulates)")
print(f"Textile Nitrate/COD Scavenging Index: {ratio_nitrate_cod_textile:.4f}")
print(f"Dye-Intermediate Nitrate/COD Scavenging Index: {ratio_nitrate_cod_dye:.4f} (Dye-Int is {ratio_nitrate_cod_dye/ratio_nitrate_cod_textile:.1f}x more vulnerable to scavenging)")
print(f"Textile Optical Density Proxy (Turbidity * Color): {od_proxy_textile:,.2f}")
print(f"Dye-Intermediate Optical Density Proxy: {od_proxy_dye:,.2f} (Textile attenuation factor is {od_proxy_textile/od_proxy_dye:.1f}x greater)\n")

# =====================================================================
# 4. Restructure Matrix for Logarithmic Visualization (Exclude pH)
# =====================================================================
# Clean parameter names
df_raw['Parameter'] = df_raw['Parameter'].str.strip()

# Exclude pH because it is already an inverse-log value
df_plot = df_raw[df_raw['Parameter'] != ''].copy()

# Melt from wide to long format
df_melted = pd.melt(
    df_plot, 
    id_vars=['Parameter', 'Unit'], 
    value_vars=['Textile Effluent', 'Dye Intermediate'],
    var_name='Wastewater Matrix', 
    value_name='Value'
)

# Convert to float and save original value for data text labels
df_melted['Value'] = df_melted['Value'].astype(float)
df_melted['Original_Value'] = df_melted['Value']

# Manually compute log10 to prevent the Seaborn log(0) bar-vanishing bug
df_melted['Log_Value'] = np.log10(df_melted['Value'])


# =====================================================================
# 5. Plotting Configuration (Pure Matplotlib Implementation)
# =====================================================================
plt.figure(figsize=(12, 7))
sns.set_style("whitegrid")  # Keep the clean journal grid style

# Extract unique parameters and set up manual bar positioning
parameters = df_plot['Parameter'].unique()
x_indexes = np.arange(len(parameters))
bar_width = 0.35

# Filter the melted data manually to ensure explicit plotting arrays
textile_data = df_melted[df_melted['Wastewater Matrix'] == 'Textile Effluent']
dye_data = df_melted[df_melted['Wastewater Matrix'] == 'Dye Intermediate']

# Align arrays to ensure parameters match order perfectly
textile_logs = [textile_data[textile_data['Parameter'] == p]['Log_Value'].values[0] for p in parameters]
dye_logs = [dye_data[dye_data['Parameter'] == p]['Log_Value'].values[0] for p in parameters]

textile_raw = [textile_data[textile_data['Parameter'] == p]['Original_Value'].values[0] for p in parameters]
dye_raw = [dye_data[dye_data['Parameter'] == p]['Original_Value'].values[0] for p in parameters]

# Draw the bars explicitly using native Matplotlib
rects1 = plt.bar(x_indexes - bar_width/2, textile_logs, bar_width, 
                 label='Textile Effluent', color='#1f77b4', edgecolor='black', linewidth=1.2)
rects2 = plt.bar(x_indexes + bar_width/2, dye_logs, bar_width, 
                 label='Dye Intermediate', color='#ff7f0e', edgecolor='black', linewidth=1.2)

# Customize the Y-axis ticks to represent a traditional log scale
plt.yticks([0, 1, 2, 3, 4], ['1', '10', '100', '1,000', '10,000'], fontsize=10)
plt.ylim(0, 4.5)

# Axis labels and titles aligned with journal standards
plt.title('Physicochemical Baseline Profile of Raw Industrial Effluents (Logarithmic Scale)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Water Quality Parameter', fontsize=12, fontweight='bold', labelpad=10)
plt.ylabel('Concentration / Measurement Value', fontsize=12, fontweight='bold', labelpad=10)

plt.xticks(x_indexes, parameters, rotation=45, ha='right', fontsize=10)
plt.legend(title='Wastewater Stream', title_fontproperties={'weight':'bold'}, loc='upper right')

# Helper function to place true value text annotations cleanly above the bars
def autolabel(rects, raw_values):
    for rect, raw_val in zip(rects, raw_values):
        height = rect.get_height()
        if height > 0:
            label_text = f'{raw_val:,.1f}' if abs(raw_val) >= 10 else f'{raw_val:.2f}'
            plt.annotate(label_text,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 5),  # 5 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', 
                        fontsize=8, fontweight='semibold', rotation=0)

# Run the label assignment
autolabel(rects1, textile_raw)
autolabel(rects2, dye_raw)

plt.tight_layout()

# Save High-Resolution Figure for Manuscript Compilation
output_path = 'Figure_1_Baseline_Log10_Profile.png'
plt.savefig(output_path, dpi=300)
print(f"Success! High-resolution manuscript figure saved as: {output_path}")
plt.show()

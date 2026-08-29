# Code developed with Gemini assistance on 22 July 2026


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================================
# 1. Load & Clean Data
# =====================================================================
excel_file = "Fenton101.xlsx"
if not os.path.exists(excel_file):
    raise FileNotFoundError(f"Please ensure '{excel_file}' is in your active directory.")

df_raw = pd.read_excel(excel_file, sheet_name=0)
df_raw.columns = df_raw.columns.str.strip()
df_raw['Parameter'] = df_raw['Parameter'].str.strip()

# Remove pH if it's there (since it's already a log value)
df_plot = df_raw[df_raw['Parameter'] != 'pH'].copy()

# CRITICAL FIX: Group by Parameter to prevent duplicate row overlays
condition_cols = [col for col in df_plot.columns if col not in ['Parameter', 'Unit']]
df_grouped = df_plot.groupby('Parameter', sort=False)[condition_cols].first().reset_index()

# Get parameters and setup tracking
parameters = df_grouped['Parameter'].values
x_indexes = np.arange(len(parameters))
total_conditions = len(condition_cols)
bar_width = 0.8 / total_conditions  

# =====================================================================
# 2. Plotting Setup (High-Contrast Custom Palette)
# =====================================================================
plt.figure(figsize=(14, 8))
plt.grid(axis='y', linestyle='--', alpha=0.7, zorder=0) 

# Explicit color mapping for your ratios
color_map = {
    'Initial': '#1f77b4',  # Blue
    '1:10': '#e75480',     # Pink
    '1:20': '#d62728',     # Red
    '1:30': '#8c564b'      # Brown
}
fallback_colors = ['#1f77b4', '#8c564b' , '#d62728', '#e75480']

# Loop through each column and explicitly draw the bars
for i, col_name in enumerate(condition_cols):
    # Safe numerical conversion using the grouped dataframe
    raw_values = pd.to_numeric(df_grouped[col_name], errors='coerce').fillna(1.0).values
    
    # Floor protection: values <= 1 rest cleanly at 0
    log_values = np.where(raw_values > 1, np.log10(raw_values), 0.0)
    
    # Calculate offset for grouped bars
    offset = (i - (total_conditions - 1) / 2) * bar_width
    
    # Match color by column name or fallback sequentially
    bar_color = color_map.get(col_name, fallback_colors[i % len(fallback_colors)])
    
    # Draw bars explicitly
    rects = plt.bar(x_indexes + offset, log_values, bar_width, 
                    label=col_name, color=bar_color, 
                    edgecolor='black', linewidth=0.8, zorder=3)
    
    # Annotate text values above bars
    for rect, raw_val in zip(rects, raw_values):
        height = rect.get_height()
        if height >= 0:
            if raw_val >= 10:
                label_text = f'{raw_val:,.1f}'
            else:
                label_text = f'{raw_val:.2f}'
                
            plt.annotate(label_text,
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', 
                        fontsize=7.5, fontweight='semibold', rotation=90,
                        clip_on=False) 

# =====================================================================
# 3. Formatting & Ticks
# =====================================================================
plt.yticks([0, 1, 2, 3, 4], ['1', '10', '100', '1,000', '10,000'], fontsize=10)
plt.ylim(0, 4.8)  

plt.title('Fenton Treated Textile Wastewater Parameter Profile at Fe2+/H2O2 Ratios (Logarithmic Scale)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Water Quality Parameter', fontsize=11, fontweight='bold', labelpad=10)
plt.ylabel('Concentration / Value', fontsize=11, fontweight='bold', labelpad=10)

plt.xticks(x_indexes, parameters, rotation=45, ha='right', fontsize=10)
plt.legend(title='Treatment Ratio', title_fontproperties={'weight':'bold'}, loc='upper right')

plt.tight_layout()

output_path = 'Figure_1_Fixed_Profile.png'
plt.savefig(output_path, dpi=300)
plt.show()

import pandas as pd
import numpy as np

fifty_cutoff = 180.12
overall_baseline = 360.25

GHG_baseline = 381.13
nitrogen_baseline = 4.21
water_baseline = 1501.2

def create_ghg_label(label):
    if label > overall_baseline:
        return "Red"
    elif (label <= overall_baseline) & (label > fifty_cutoff):
        return "Yellow"
    elif label <= fifty_cutoff:
        return "Green"

def create_results_all_factors(df):
    df["Combined Label"] = ""

    def calculate_all_factors(ghg, nitrogen, water):
        weighted_ghg = ghg / (3 * GHG_baseline)
        weighted_nitrogen = nitrogen / (3 * nitrogen_baseline)
        weighted_water = water / (3 * water_baseline)
        return weighted_ghg + weighted_nitrogen + weighted_water

    for ind, row in df.iterrows():
        label = calculate_all_factors(row["GHG Emission (g) / 100g"], row["N lost (g) / 100g"],
                                      row["Stress-Weighted Water Use (L) / 100g"])

        if label <= 0.5:
            df.loc[ind, "Combined Label"] = "Green"
        elif label >= 1:
            df.loc[ind, "Combined Label"] = "Red"
        elif (label > 0.5) or (label < 1):
            df.loc[ind, "Combined Label"] = "Yellow"
    return df
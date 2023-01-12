import pandas as pd
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import seaborn as sns

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

def add_menu_names(df, dict):
    df["Displayed Name"] = ""
    menu_name = list(dict.keys())
    menu_ID = list(dict.values())
    for ind, row in df.iterrows():
        searchID = row["ProdId"]
        if searchID in menu_ID:
            position = menu_ID.index(searchID)
            name = menu_name[position]
            df.loc[ind, "Displayed Name"] = name
        else:
            continue
    name_col = df.pop("Displayed Name")
    df.insert(0, "Displayed Name", name_col)
    df = df.dropna(subset=["Displayed Name"])

    df_temp = df["Displayed Name"].str.split("|", expand=True)
    df["Category"] = df_temp[0]
    df["Displayed Name"] = df_temp[1]
    name_col2 = df.pop("Category")
    df.insert(0, "Category", name_col2)
    return df


def create_final_counts(df):
    ghg_red = df["GHG Only Label"].value_counts()["Red"]
    ghg_yellow = df["GHG Only Label"].value_counts()["Yellow"]
    ghg_green = df["GHG Only Label"].value_counts()["Green"]
    all_red = df["Combined Label"].value_counts()["Red"]
    all_yellow = df["Combined Label"].value_counts()["Yellow"]
    all_green = df["Combined Label"].value_counts()["Green"]
    print(all_red, all_yellow, all_green)
    data = {"GHG Label Counts": [ghg_red, ghg_yellow, ghg_green],
            "Combined Label Counts": [all_red, all_yellow, all_green]}
    results = pd.DataFrame(data, index=["Red", "Yellow", "Green"])
    return results

def create_visualizations(df):
    df.reset_index(inplace=True)
    df = df.rename(columns={"index":"Color"})
    sns.set_theme(style="darkgrid")
    palette = {"Green":"tab:green", "Red":"tab:red", "Yellow":"tab:orange"}
    fig, axes = plt.subplots(1,2, figsize=(7,4), sharex=False, sharey=True)
    fig.suptitle("Emission Label Counts")
    ax1 = sns.barplot(data=df, x=df["Color"], y=df["GHG Label Counts"], ax=axes[0], palette=palette)
    ax1.set_title("GHG Emission Label")
    ax1.set_ylabel("Counts")
    ax1.set_xlabel("")
    ax2 = sns.barplot(data=df, x=df["Color"], y=df["Combined Label Counts"], ax=axes[1], palette=palette)
    ax2.set_title("Combined Emissions Label")
    ax2.set_ylabel("")
    ax2.set_xlabel("")
    fig.title="Color Comparison"
    ax1.set_title="GHG Emission Label Counts"
    ax2.set_title="Combined Emissions Label Counts"
    ax2.set_ylabel=""
    for ax in [ax1, ax2]:
        for i in ax.containers:
            ax.bar_label(i, )
    plt.tight_layout()
    plt.savefig("notebooks/data/final/2022_2023_CFFS_Outcomes/Gather_Summary_fig.png")
    plt.show()

def create_category_true(df):
    df["RED"] = ""
    df["YELLOW"] = ""
    df["GREEN"] = ""
    for ind, row in df.iterrows():
        if row["Combined Label"] == "Red":
            df.loc[ind, "RED"] = "TRUE"
        if row["Combined Label"] == "Yellow":
            df.loc[ind, "YELLOW"] = "TRUE"
        if row["Combined Label"] == "Green":
            df.loc[ind, "GREEN"] = "TRUE"
    return df
import numpy as np
import pandas as pd

# Std_Unit = pd.read_csv("notebooks/data/external/standard_conversions.csv")

existing_units = ["lb", "LBS", "oz", "Kg", "kg", "L"]

def converter_constructor(value, old_unit):
    if (old_unit == "lb") or (old_unit == "LBS"):
        value = value * 453.592
    elif old_unit == "oz":
        value = value * 28.3495
    elif (old_unit == "Kg") or (old_unit == "kg"):
        value = value * 1000
    elif old_unit == "L":
        value = value * 1000
    return (value, "g")

def construct_empty_conversion_df():
    columns = ["ConversionId", "Multiplier", "ConvertFromQty", "ConvertFromUom", "ConvertToQty", "ConvertToUom"]
    df = pd.DataFrame(columns=columns)
    return df

def convert_units(items, empty_df):
    for ind, row in items.iterrows():
        conversionId = row["ItemId"]
        if row["UOM"] in ["g", "ml"]:
            fromQty = row["Qty"]
            fromUom = row["UOM"]
            toQty = row["Qty"]
            toUom = row["UOM"]
            multiplier = 1.0
        elif row["UOM"] in existing_units:
            fromQty = row["Qty"]
            fromUom = row["UOM"]
            toQty = converter_constructor(fromQty, fromUom)[0]
            toUom = converter_constructor(fromQty, fromUom)[1]
            multiplier = toQty / fromQty
        else:
            fromQty = row["Qty"]
            fromUom = row["UOM"]
            toQty = 999
            toUom = "g"
            multiplier = 0.0
        info = [conversionId, multiplier, fromQty, fromUom, toQty, toUom]
        empty_df.loc[len(empty_df.index)] = info
    return empty_df

def find_nonstd_units(df):
    conv_df = df.loc[df["ConvertToQty"] == 999]
    diff_df = pd.merge(df, conv_df, how='outer', indicator='Exist')
    std_df = diff_df.loc[diff_df['Exist'] != 'both']
    std_df = std_df.drop(["Exist"], axis=1)
    return conv_df, std_df

def add_nonstd_units(std_df, conv_df):
    df = pd.concat([std_df, conv_df], axis=0)
    df = df.reset_index().drop(["index"], axis=1)
    for ind, row in df.iterrows():
        if row["Multiplier"] == 0.0:
            df.loc[ind, "Multiplier"] = float(row["ConvertToQty"]) / float(row["ConvertFromQty"])
    return df




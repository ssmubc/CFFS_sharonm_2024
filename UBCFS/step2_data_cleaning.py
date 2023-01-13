import numpy as np
import pandas as pd


Std_Unit = pd.read_csv("notebooks/data/external/standard_conversions.csv")

def update_conversions_list(update_conv, conversions):
    """
    Updates `data/cleaning/update/Conv_UpdateConv.csv`.
    """

    for index, row in update_conv.iterrows():
        Id = update_conv.loc[index, 'ConversionId']
        conversions.drop(conversions[conversions['ConversionId'] == Id].index, inplace=True)

    frames = [conversions, update_conv]
    conversions = pd.concat(frames).reset_index(drop=True, inplace=False).drop_duplicates()
    return conversions

def assign_multiplier(update_conv):
    for ind, row in update_conv.iterrows():
        if pd.isnull(row["Multiplier"]):
            update_conv.loc[ind, "Multiplier"] = row["ConvertFromQty"] / row["ConvertToQty"]
    return update_conv

def sort_liquid_and_solid_unit(std_unit):
    """
    Identifies items in `data/external/standard_conversions.csv` that converts TO g or ml.
    """

    liquid_unit = std_unit.loc[std_unit['ConvertToUom'] == 'ml', 'ConvertFromUom'].tolist()
    solid_unit = std_unit.loc[std_unit['ConvertToUom'] == 'g', 'ConvertFromUom'].tolist()
    return liquid_unit, solid_unit

# Classifies whether the given unit is in standard unit list.
# If the unit is found, returns quantity and unit being converted to.
# If the unit is not present in `data/external/standard_conversions.csv`, returns original quantity and uom.
def std_converter(qty, uom, std_unit=Std_Unit):
    # std_unit = pd.read_csv("data/external/standard_conversions.csv")

    """
    From `data/external/standard_conversions.csv`, if the unit is defined under "ConvertFromUom",
    returns converted quantity and new unit of measurement.
    If not found in `data/external/standard_conversions.csv`, returns quantity and original unit.
    """

    if uom in std_unit["ConvertFromUom"].tolist():
        multiplier = std_unit.loc[std_unit["ConvertFromUom"] == uom, "Multiplier"]
        Qty = float(qty) * float(multiplier)
        Uom = std_unit.loc[std_unit["ConvertFromUom"] == uom, "ConvertToUom"].values[0]
    else:
        Qty = qty
        Uom = uom
    return (Qty, Uom)

def spc_converter(ingre, qty, uom, conversions, liquid_unit, solid_unit):
    """
    If the unit can be converted to standard units (g or ml), directs to std_converter.
    If ingre(IngredientId) is in spc_cov, find conversionId, converting unit, conversion unit from
    `data/cleaning/Conversions_Added.csv`.
    """

    spc_cov = list(filter(None, conversions["ConversionId"].tolist()))
    # spc_cov = [item for item in spc_cov if not (pd.null(item)) == True]

    if uom in liquid_unit + solid_unit:
        return std_converter(qty, uom)
    elif ingre in spc_cov:
        conversion = conversions.loc[(conversions["ConversionId"] == ingre) &
                                     (conversions["ConvertFromUom"] == uom) &
                                     (conversions["ConvertToUom"] == "g")]
        # conversion.drop_duplicates(subset=['ConversionId'], inplace=True)
        multiplier = conversion["Multiplier"]
        if multiplier.empty:
            return std_converter(qty, uom)
        else:
            Qty = float(qty) / float(multiplier)
            Uom = conversion["ConvertToUom"].values[0]
            return (Qty, Uom)
    else:
        return std_converter(qty, uom)

# Filter out items with unit information unknown
def items_with_nonstd_units(ingre, liquid_unit, solid_unit, conversions):
    col_names = list(ingre.columns.values)
    Items_Nonstd = []

    for ind, row in ingre.iterrows():
        Ingre = ingre.loc[ind, "IngredientId"]
        Uom = ingre.loc[ind, "Uom"]
        if Uom not in ["g", "ml"] and Uom not in liquid_unit + solid_unit and Ingre.startswith("I") and Ingre not in \
                conversions["ConversionId"].tolist():
            Dict = {}
            Dict.update(dict(row))
            Items_Nonstd.append(Dict)

    Items_Nonstd = pd.DataFrame(Items_Nonstd, columns=col_names)
    Items_Nonstd.drop_duplicates(subset=["IngredientId"], inplace=True)
    return Items_Nonstd

def cleanup_preps_units(preps, conversions, Std_Unit):
    liquid_unit, solid_unit = sort_liquid_and_solid_unit(Std_Unit)
    preps["StdQty"] = np.nan
    preps["StdUom"] = np.nan
    for index in preps.index:
        PrepId = preps.loc[index, "PrepId"]
        Qty = preps.loc[index, "PakQty"]
        Uom = preps.loc[index, "PakUOM"]
        preps.loc[index, "StdQty"] = spc_converter(PrepId, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
        preps.loc[index, "StdUom"] = spc_converter(PrepId, Qty, Uom, conversions, liquid_unit, solid_unit)[1]
    return preps

def preps_with_nonstd_unit(preps):
    # preps: Preps_Unit_Cleaned.csv

    # Find out preps with non-standard units
    col_names = list(preps.columns.values)
    preps_nonstd = []

    for index, row in preps.iterrows():
        StdUom = preps.loc[index, "StdUom"]
        if StdUom not in ["g", "ml"]:
            Dict = {}
            Dict.update(dict(row))
            preps_nonstd.append(Dict)

    preps_nonstd = pd.DataFrame(preps_nonstd, columns=col_names)

    manual_prepU = pd.read_csv("notebooks/data/cleaning/update/Preps_UpdateUom.csv")
    col_names2 = list(preps_nonstd.columns.values)
    preps_nonstd_na = []

    for index, row in preps_nonstd.iterrows():
        PrepId = preps_nonstd.loc[index, "PrepId"]
        if PrepId not in manual_prepU["PrepId"].values:
            Dict = {}
            Dict.update(dict(row))
            preps_nonstd_na.append(Dict)

    preps_nonstd = pd.DataFrame(preps_nonstd_na, columns=col_names2)
    return preps_nonstd

def sort_new_items(items, items_list_assigned):
    col_names = list(items.columns.values)
    new_items_list = []

    for index, row in items.iterrows():
        ItemId = items.loc[index, "ItemId"]
        if ItemId not in items_list_assigned["ItemId"].values:
            Dict = {}
            Dict.update(dict(row))
            new_items_list.append(Dict)

    new_items_list = pd.DataFrame(new_items_list, columns=col_names)
    return new_items_list

if __name__ == '__main__':
    pass

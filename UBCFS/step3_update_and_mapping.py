import numpy as np
import pandas as pd
import pdpipe as pdp
import matplotlib.pyplot as plt
import glob
import os
import csv
from itertools import islice
from decimal import Decimal
import xml.etree.ElementTree as et
from xml.etree.ElementTree import parse
import openpyxl
import pytest
from datetime import datetime
from main import *

def update_uom_for_preps(manual_prep, preps):
    for index, row in manual_prep.iterrows():
        PrepId = manual_prep.loc[index, "PrepId"]
        qty = manual_prep.loc[index, "StdQty"]
        uom = manual_prep.loc[index, "StdUom"]
        preps.loc[preps["PrepId"] == PrepId, "StdQty"] = qty
        preps.loc[preps["PrepId"] == PrepId, "StdUom"] = uom
    return preps

def import_list_of_new_items_with_emission_factors(items_assigned, new_items_added):
    frames = [items_assigned, new_items_added]
    items_assigned_updated = pd.concat(frames).reset_index(drop=True, inplace=False).drop_duplicates()
    items_assigned_updated[["CategoryID"]] = items_assigned_updated[["CategoryID"]].apply(pd.to_numeric)
    return items_assigned_updated

def map_items_to_ghge_factors(items_assigned_updated, ghge_factors):
    mapping = pd.merge(items_assigned_updated, ghge_factors.loc[:, ["Category ID", "Food Category",
                                                                    "Active Total Supply Chain Emissions (kg CO2 / kg food)"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "Active Total Supply Chain Emissions (kg CO2 / kg food)"] = 0

    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    return mapping

def map_items_to_nitrogen_factors(mapping, nitro_factors):
    mapping = pd.merge(mapping, nitro_factors.loc[:, ["Category ID", "Food Category", "g N lost/kg product"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "g N lost/kg product"] = 0

    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    return mapping

def map_items_to_water_factors(mapping, water_factors):
    mapping = pd.merge(mapping, water_factors.loc[:, ["Category ID", "Food Category",
                                                      "Freshwater Withdrawals (L/FU)",
                                                      "Stress-Weighted Water Use (L/FU)"]],
                       how="left", left_on="CategoryID", right_on="Category ID")
    for index in mapping.index:
        if np.isnan(mapping.loc[index, "Category ID"]):
            mapping.loc[index, "Freshwater Withdrawals (L/FU)"] = 0
            mapping.loc[index, "Stress-Weighted Water Use (L/FU)"] = 0

    mapping = mapping.drop(columns=["Category ID", "Food Category"])
    return mapping

def manual_adjust_factors(manual_factor, mapping):
    for index, row in manual_factor.iterrows():
        itemId = manual_factor.loc[index, "ItemId"]
        ghge = manual_factor.loc[index, "Active Total Supply Chain Emissions (kg CO2 / kg food)"]
        nitro =  manual_factor.loc[index, "g N lost/kg product"]
        water = manual_factor.loc[index, "Freshwater Withdrawals (L/FU)"]
        str_water = manual_factor.loc[index, "Stress-Weighted Water Use (L/FU)"]
        mapping.loc[mapping['ItemId'] == itemId, 'Active Total Supply Chain Emissions (kg CO2 / kg food)'] = ghge
        mapping.loc[mapping['ItemId'] == itemId, 'g N lost/kg product'] = nitro
        mapping.loc[mapping['ItemId'] == itemId, 'Freshwater Withdrawals (L/FU)'] = water
        mapping.loc[mapping['ItemId'] == itemId, 'Stress-Weighted Water Use (L/FU)'] = str_water
    # mapping.drop_duplicates(subset=["ItemId"], inplace=True)
    return mapping

if __name__ == '__main__':
    pass
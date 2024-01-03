import numpy as np
import pandas as pd

def assign_category_ID(df):
    df["Category"] = 0
    return df

def match_ghge_emissions(ghge, df):
    df = df.merge(ghge, left_on="Category", right_on="Category ID")
    df = df[["ConversionId", "ConvertToQty", "ConvertToUom", "Category",
             "Active Total Supply Chain Emissions (kg CO2 / kg food)"]]
    return df

def match_nitrogen_lost(n, df):
    df = df.merge(n, left_on = "Category", right_on="Category ID")
    df = df[["ConversionId", "ConvertToQty", "ConvertToUom", "Category",
             "Active Total Supply Chain Emissions (kg CO2 / kg food)", "g N lost/kg product"]]
    return df

def match_water_withdrawals(water, df):
    df = df.merge(water, left_on="Category", right_on="Category ID")
    df = df[["ConversionId", "ConvertToQty", "ConvertToUom", "Category",
             "Active Total Supply Chain Emissions (kg CO2 / kg food)", "g N lost/kg product",
             "Freshwater Withdrawals (L/FU)"]]
    return df

# Added by Sharon May 29
def match_land_withdrawals(land, df):
    df = df.merge(land, left_on="Category", right_on="Category ID")
    df = df[["ConversionId", "ConvertToQty", "ConvertToUom", "Category",
             "Active Total Supply Chain Emissions (kg CO2 / kg food)", "g N lost/kg product",
             "km^2 land use/kg product", "Freshwater Withdrawals (L/FU)"]]
    return df


def match_products_to_items(items, df):
    df = df.merge(items, left_on="ConversionId", right_on="ItemId")
    df = df.drop(["ItemId", "Description", "Qty", "UOM"], axis=1)
    return df

def scale_emissions(df):
    for emission in ["g N lost/kg product"]:
        df[emission] = df[emission].apply(lambda x: x / 1000)
        
    for emission in ["km^2 land use/kg product"]:
        df[emission] = df[emission].apply(lambda x: x * 1000)  # turn into m^2 and remove /kg product part to have per grams
                                                               # so when we multiply by grams for weight, the units cancel
    df = df.rename(columns={"Active Total Supply Chain Emissions (kg CO2 / kg food)":"CO2 Emission (g CO2)",
                            "g N lost/kg product":"Nitrogen Lost (g)",
                            "Freshwater Withdrawals (L/FU)":"Water Withdrawals (mL)",
                            "km^2 land use/kg product": "Land Use (m^2)"})
    return df

def total_emission_by_food(df):
    df["ConvertToQty"] = df["ConvertToQty"].astype(float)
    df["Total CO2 Emission (g)"] = df["CO2 Emission (g CO2)"] * df["ConvertToQty"]
    df["Total Nitrogen Emission (g)"] = df["Nitrogen Lost (g)"] * df["ConvertToQty"]
    df["Total Freshwater Withdrawals (mL)"] = df["Water Withdrawals (mL)"] * df["ConvertToQty"]
    
    # May 29
    df["Total Land Use (m^2)"] = df["Land Use (m^2)"] * df["ConvertToQty"]
    return df

def assign_weight(df):
    df["Weight (g)"] = 0
    all_prod = df["PrepId"].unique().tolist()
    for prod in all_prod:
        weight = 0
        for ind, row in df.iterrows():
            if row["PrepId"] == prod:
                weight += row["ConvertToQty"]
        for ind, row in df.iterrows():
            if row["PrepId"] == prod:
                df.loc[ind, "Weight (g)"] = weight
    return df

def calculate_emissions_per_products(df):
#     final_df = pd.DataFrame(columns=["ProdId", "PrepId", "Weight (g)", "Total CO2 Emission (g)", "Total Nitrogen Emission (g)",
#                                      "Total Freshwater Withdrawals (mL)"])
    # final_df = pd.DataFrame(columns=["ProdId", "Weight (g)", "Total CO2 Emission (g)", "Total Nitrogen Emission (g)",
    #                                  "Total Freshwater Withdrawals (mL)"])
    final_df = pd.DataFrame(columns=["ProdId", "PrepId", "Weight (g)", "Total CO2 Emission (g)", "Total Nitrogen Emission (g)",
                                     "Total Freshwater Withdrawals (mL)", "Total Land Use (m^2)"])

    all_prod = df["PrepId"].unique().tolist()

    for prod in all_prod:
        temp_df = df.loc[df["PrepId"] == prod]
        ProdId = prod
        Weight = 0
        total_CO2 = 0
        total_N = 0
        total_Water = 0
        
        # Added May 29
        total_Land = 0
        
        for ind, row in temp_df.iterrows():
            prepId = row["ProdId"]
            Weight += row["Weight (g)"]
            total_CO2 += row["Total CO2 Emission (g)"]
            total_N += row["Total Nitrogen Emission (g)"]
            total_Water += row["Total Freshwater Withdrawals (mL)"]
            
            # Added May 29
            total_Land += row["Total Land Use (m^2)"]
            
        info = [ProdId, prepId, Weight, total_CO2, total_N, total_Water, total_Land]
        final_df.loc[len(final_df.index)] = info
        print("--------------")
        print(final_df)
    print(final_df)
    return final_df

def calculate_100g_emissions(df):
    for ind, row in df.iterrows():
        df.loc[ind, "GHG Emission (g) / 100g"] = (row["Total CO2 Emission (g)"] / row["Weight (g)"]) * 100
        df.loc[ind, "N lost (g) / 100g"] = (row["Total Nitrogen Emission (g)"] / row["Weight (g)"]) * 100
        df.loc[ind, "Stress-Weighted Water Use (L) / 100g"] = ((row["Total Freshwater Withdrawals (mL)"] / 1000) / row["Weight (g)"]) * 100
        
        # Added May 29
        df.loc[ind, "Land Use (m^2) / 100g"] = (row["Total Land Use (m^2)"] / row["Weight (g)"]) * 100
    print(df.columns)
    return df

def calculate_by_weight(df):
    for ind, row in df.iterrows():
        df.loc[ind, "GHG Emission (g) / g"] = (row["Total CO2 Emission (g)"] / row["Weight (g)"])
        df.loc[ind, "N lost (g) / g"] = (row["Total Nitrogen Emission (g)"] / row["Weight (g)"])
        df.loc[ind, "Stress-Weighted Water Use (L) / g"] = ((row["Total Freshwater Withdrawals (mL)"] / 1000) / row["Weight (g)"])
        
        # Added May 29
        df.loc[ind, "Land Use (m^2) / g"] = (row["Total Land Use (m^2)"] / row["Weight (g)"])
    return df




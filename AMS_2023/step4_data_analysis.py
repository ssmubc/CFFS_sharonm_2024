import pandas as pd
from notebooks.UBCFS.step2_data_cleaning import spc_converter, std_converter

def unit_conversion_for_preps(manual_prepu, conversions):
    prep_cov = manual_prepu[["PrepId", "PakQty", "PakUOM", "StdQty", "StdUom"]]
    prep_cov.insert(1, "Multiplier", "")
    prep_cov.columns = conversions.columns
    for ind, row in prep_cov.iterrows():
        prep_cov.loc[ind, "Multiplier"] = float(row["ConvertFromQty"]) / float(row["ConvertToQty"])
    # prep_cov.loc['Multiplier'] = prep_cov['ConvertFromQty'] / prep_cov['ConvertToQty']
    frames = [conversions, prep_cov]
    conversions = pd.concat(frames).reset_index(drop=True, inplace=False).drop_duplicates()
    return conversions

def rearrange_preps(preps):
    preps["GHG Emission (g)"] = 0
    preps["GHG Emission (g)/StdUom"] = 0
    preps["N lost (g)"] = 0
    preps["N lost (g)/StdUom"] = 0
    preps["Freshwater Withdrawals (ml)"] = 0
    preps["Freshwater Withdrawals (ml)/StdUom"] = 0
    preps["Stress-Weighted Water Use (ml)"] = 0
    preps["Stress-Weighted Water Use (ml)/StdUom"] = 0
    return preps

def get_items_ghge_prep(index, row, ingredient, preps, mapping, spc_cov, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredient.loc[ingredient["Recipe"] == preps.loc[index, "PrepId"]]
    ghg = preps.loc[index, "GHG Emission (g)"]
    nitro = preps.loc[index, "N lost (g)"]
    water = preps.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = preps.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = preps.loc[index, "StdQty"]
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre.startswith("I"):
            ghge = mapping.loc[mapping["ItemId"] == ingre, "Active Total Supply Chain Emissions (kg CO2 / kg food)"]
            nitro_fac = mapping.loc[mapping["ItemId"] == ingre, "g N lost/kg product"]
            water_fac = mapping.loc[mapping["ItemId"] == ingre, "Freshwater Withdrawals (L/FU)"]
            str_water_fac = mapping.loc[mapping["ItemId"] == ingre, "Stress-Weighted Water Use (L/FU)"]
            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            if ingre in spc_cov:
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
    preps.loc[index, "GHG Emission (g)"] = float(ghg)
    preps.loc[index, "GHG Emission (g)/StdUom"] = ghg/float(weight)
    preps.loc[index, "N lost (g)"] = float(nitro)
    preps.loc[index, "N lost (g)/StdUom"] = nitro/float(weight)
    preps.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    preps.loc[index, 'Freshwater Withdrawals (ml)/StdUom'] = water / float(weight)
    preps.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    preps.loc[index, 'Stress-Weighted Water Use (ml)/StdUom'] = str_water / float(weight)
    return preps

def link_preps(index, row, ingredients, preps, spc_cov, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredients.loc[ingredients["Recipe"] == preps.loc[index, "PrepId"]]
    ghg = preps.loc[index, "GHG Emission (g)"]
    nitro = preps.loc[index, "N lost (g)"]
    water = preps.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = preps.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = preps.loc[index, "StdQty"]
    if len(ingres) == 1:
        ingre = ingres.iloc[0]["IngredientId"]
        if ingre.startswith("P"):
            ghge = preps.loc[preps["PrepId"] == ingre, "GHG Emission (g)/StdUom"]
            nitro_fac = preps.loc[preps["PrepId"] == ingre, "N lost (g)/StdUom"]
            water_fac = preps.loc[preps["PrepId"] == ingre, "Freshwater Withdrawals (ml)/StdUom"]
            str_water_fac = preps.loc[preps["PrepId"] == ingre, "Stress-Weighted Water Use (ml)/StdUom"]
            Qty = float(ingres.iloc[0]["Qty"])
            Uom = ingres.iloc[0]["Uom"]
            if ingre in spc_cov:
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
    preps.loc[index, "GHG Emission (g)"] = float(ghg)
    preps.loc[index, "GHG Emission (g)/StdUom"] = ghg / float(weight)
    preps.loc[index, "N lost (g)"] = float(nitro)
    preps.loc[index, "N lost (g)/StdUom"] = nitro / float(weight)
    preps.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    preps.loc[index, 'Freshwater Withdrawals (ml)/StdUom'] = water / float(weight)
    preps.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    preps.loc[index, 'Stress-Weighted Water Use (ml)/StdUom'] = str_water / float(weight)
    return preps

def get_preps_ghge_prep(index, row, ingredients, preps, spc_cov, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredients.loc[ingredients["Recipe"] == preps.loc[index, "PrepId"]]
    ghg = preps.loc[index, "GHG Emission (g)"]
    nitro = preps.loc[index, "N lost (g)"]
    water = preps.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = preps.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = preps.loc[index, "StdQty"]
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre.startswith("P") and len(ingres) > 1:
            ghge = preps.loc[preps["PrepId"] == ingre, "GHG Emission (g)/StdUom"]
            nitro_fac = preps.loc[preps["PrepId"] == ingre, "N lost (g)/StdUom"]
            water_fac = preps.loc[preps["PrepId"] == ingre, "Freshwater Withdrawals (ml)/StdUom"]
            str_water_fac = preps.loc[preps["PrepId"] == ingre, "Stress-Weighted Water Use (ml)/StdUom"]
            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            if ingre in spc_cov:
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
    preps.loc[index, "GHG Emission (g)"] = float(ghg)
    preps.loc[index, "GHG Emission (g)/StdUom"] = ghg/float(weight)
    preps.loc[index, "N lost (g)"] = float(nitro)
    preps.loc[index, "N lost (g)/StdUom"] = nitro/float(weight)
    preps.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    preps.loc[index, 'Freshwater Withdrawals (ml)/StdUom'] = water / float(weight)
    preps.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    preps.loc[index, 'Stress-Weighted Water Use (ml)/StdUom'] = str_water / float(weight)
    return preps

def rearrange_products(products):
    products['Weight (g)'] = 0
    products['GHG Emission (g)'] = 0
    products['N lost (g)'] = 0
    products['Freshwater Withdrawals (ml)'] = 0
    products['Stress-Weighted Water Use (ml)'] = 0
    return products

def get_items_ghge(index, row, ingredient, products, mapping, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredient.loc[ingredient["Recipe"] == products.loc[index, "ProdId"]]
    ghg = products.loc[index, "GHG Emission (g)"]
    nitro = products.loc[index, "N lost (g)"]
    water = products.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = products.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = products.loc[index, "Weight (g)"]
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre.startswith("I"):
            ghge = mapping.loc[mapping["ItemId"] == ingre, "Active Total Supply Chain Emissions (kg CO2 / kg food)"]
            nitro_fac = mapping.loc[mapping["ItemId"] == ingre, "g N lost/kg product"]
            water_fac = mapping.loc[mapping["ItemId"] == ingre, "Freshwater Withdrawals (L/FU)"]
            str_water_fac = mapping.loc[mapping["ItemId"] == ingre, "Stress-Weighted Water Use (L/FU)"]
            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            if ingre in conversions["ConversionId"].tolist():
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac) / 1000
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
    products.loc[index, "GHG Emission (g)"] = float(ghg)
    products.loc[index, "Weight (g)"] = float(weight)
    products.loc[index, "N lost (g)"] = float(nitro)
    products.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    products.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    return products

def spc_converter(ingre, qty, uom, conversions, liquid_unit, solid_unit):
    """
    If the unit can be converted to standard units (g or ml), directs to std_converter.
    If ingre(IngredientId) is in spc_cov, find conversionId, converting unit, conversion unit from
    `data/cleaning/Conversions_Added.csv`.
    """

    spc_cov = list(filter(None, conversions["ConversionId"].tolist()))

    if uom in liquid_unit + solid_unit:
        return std_converter(qty, uom)
    elif ingre in spc_cov:
        conversion = conversions.loc[(conversions["ConversionId"] == ingre) &
                                     (conversions["ConvertFromUom"] == uom) &
                                     (conversions["ConvertToUom"] == "g")]
        # conversion = conversion.replace(r'^\s*$', np.nan, regex=True)
        conversion.drop_duplicates(subset=['ConversionId'], inplace=True)
        multiplier = conversion["Multiplier"]
        if multiplier.empty:
            return std_converter(qty, uom)
        else:
            Qty = float(qty) / float(multiplier)
            Uom = conversion["ConvertToUom"].values[0]
            return (Qty, Uom)
    else:
        return std_converter(qty, uom)

def get_preps_ghge(index, row, ingredient, products, preps, conversions, liquid_unit, solid_unit, std_unit):
    ingres = ingredient.loc[ingredient["Recipe"] == products.loc[index, "ProdId"]]
    ghg = products.loc[index, "GHG Emission (g)"]
    nitro = products.loc[index, "N lost (g)"]
    water = products.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = products.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = products.loc[index, "Weight (g)"]
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre.startswith("P"):
            ghge = preps.loc[preps["PrepId"] == ingre, "GHG Emission (g)/StdUom"]
            nitro_fac = preps.loc[preps["PrepId"] == ingre, "N lost (g)/StdUom"]
            water_fac = preps.loc[preps["PrepId"] == ingre, "Freshwater Withdrawals (ml)/StdUom"]
            str_water_fac = preps.loc[preps["PrepId"] == ingre, "Stress-Weighted Water Use (ml)/StdUom"]
            Qty = float(ingres.loc[ind, "Qty"])
            Uom = ingres.loc[ind, "Uom"]
            if ingre in conversions["ConversionId"].tolist():
                qty = spc_converter(ingre, Qty, Uom, conversions, liquid_unit, solid_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
            else:
                qty = std_converter(Qty, Uom, std_unit)[0]
                weight += qty
                ghg += qty * float(ghge)
                nitro += qty * float(nitro_fac)
                water += qty * float(water_fac)
                str_water += qty * float(str_water_fac)
    products.loc[index, "GHG Emission (g)"] = float(ghg)
    products.loc[index, "Weight (g)"] = float(weight)
    products.loc[index, "N lost (g)"] = float(nitro)
    products.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    products.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    return products

def get_products_ghge(index, row, ingredient, products):
    ingres = ingredient.loc[ingredient["Recipe"] == products.loc[index, "ProdId"]]
    ghg = products.loc[index, "GHG Emission (g)"]
    nitro = products.loc[index, "N lost (g)"]
    water = products.loc[index, "Freshwater Withdrawals (ml)"]
    str_water = products.loc[index, "Stress-Weighted Water Use (ml)"]
    weight = products.loc[index, "Weight (g)"]
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre.startswith("R"):
            ghge = products.loc[products["ProdId"] == ingre, "GHG Emission (g)"]
            nitro_fac = products.loc[products["ProdId"] == ingre, "N lost (g)"]
            water_fac = products.loc[products["ProdId"] == ingre, "Freshwater Withdrawals (ml)"]
            str_water_fac = products.loc[products["ProdId"] == ingre, "Stress-Weighted Water Use (ml)"]
            Weight = products.loc[products["ProdId"] == ingre, "Weight (g)"]
            Qty = float(ingres.loc[ind, "Qty"])
            ghg += Qty * float(ghge)
            nitro += Qty * float(nitro_fac)
            water += Qty * float(water_fac)
            str_water += Qty * float(str_water_fac)
            weight += Qty * float(Weight)
    products.loc[index, "GHG Emission (g)"] = float(ghg)
    products.loc[index, "Weight (g)"] = float(weight)
    products.loc[index, "N lost (g)"] = float(nitro)
    products.loc[index, 'Freshwater Withdrawals (ml)'] = float(water)
    products.loc[index, 'Stress-Weighted Water Use (ml)'] = float(str_water)
    return products

def filter_products(index, row, ingredients, preps_nonstd, products):
    ingres = ingredients.loc[ingredients["Recipe"] == products.loc[index, "ProdId"]]
    for ind, row in ingres.iterrows():
        ingre = ingres.loc[ind, "IngredientId"]
        if ingre in preps_nonstd["PrepId"].tolist():
            print(ingre, index, products.loc[index, "ProdId"])
            products.drop(index, inplace=True)
            break

def products_cleanup(products):
    products['Freshwater Withdrawals (L)'] = round(products['Freshwater Withdrawals (ml)'] / 1000, 2)
    products['Stress-Weighted Water Use (L)'] = round(products['Stress-Weighted Water Use (ml)'] / 1000, 2)
    products = products.drop(columns=['Freshwater Withdrawals (ml)', 'Stress-Weighted Water Use (ml)'])

    products['GHG Emission (g) / 100g'] = round(100 * products['GHG Emission (g)'] / products['Weight (g)'], 2)
    products['N lost (g) / 100g'] = round(100 * products['N lost (g)'] / products['Weight (g)'], 2)
    products['Freshwater Withdrawals (L) / 100g'] = round(
        100 * products['Freshwater Withdrawals (L)'] / products['Weight (g)'], 2)
    products['Stress-Weighted Water Use (L) / 100g'] = round(
        100 * products['Stress-Weighted Water Use (L)'] / products['Weight (g)'], 2)
    print(products)
    return products

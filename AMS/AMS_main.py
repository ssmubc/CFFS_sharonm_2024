import pandas as pd
import os
from AMS_step1_data_processing import *
from AMS_step2_data_cleaning import *
from AMS_step3_mapping import *
from AMS_step4_labelling import *
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from datetime import datetime

if __name__ == '__main__':
    path = "/Users/jennylee/CFFS-PyCharm/notebooks/"
    os.chdir(path)
    print(os.getcwd())

    # items = pd.read_csv(f"/Users/jennylee/CFFS-PyCharm/notebooks/data/AMS/preprocessed/Independent_items2022-12-25.csv")
    items = pd.read_csv(f"/Users/jennylee/CFFS-PyCharm/notebooks/data/AMS/preprocessed/Child_parent_df.csv")

    # Step 2
    df = construct_empty_conversion_df()
    new_df = convert_units(items, df)
    new_df.to_csv("data/AMS/conversions/Converted_Units11.csv", index=False)
    print(new_df)

    # std_df = items that have standard units and are automatically converted
    # conv_df = items that do not have standard units and need to be manually converted
    conv_df, std_df = find_nonstd_units(new_df)
    print(conv_df)
    print(std_df)
    conv_check = pd.read_csv("../data/AMS/conversions/Converted_Units.csv")

    for ind, row in conv_df.iterrows():
        if row["ConversionId"] in conv_check["ConversionId"].unique().tolist():
            conv_df = conv_df.drop(ind)

    conv_df.to_csv("data/AMS/conversions/NonStd_Units.csv", index=False)
    # Before proceeding to the next step, manually adjust the conversions in file `AMS/conversions/NonStd_Units.csv`.

    all_df = add_nonstd_units(std_df, conv_check)
    all_df.to_csv("data/AMS/conversions/Converted_Units12.csv", index=False)
    print("ALL____DF")
    print(all_df)

    # Step 3
    ghge_factors = pd.read_csv("../data/external/ghge_factors.csv")
    nitro_factors = pd.read_csv("../data/external/nitrogen_factors.csv")
    water_factors = pd.read_csv("../data/external/water_factors.csv")

    df = assign_category_ID(all_df)
    assigned_df = pd.read_csv("../data/AMS/preprocessed/Category_Assigned_new.csv")
    conversion_id = assigned_df["ConversionId"].tolist()

    df_cols = ["ConversionId","Multiplier","ConvertFromQty","ConvertFromUom","ConvertToQty","ConvertToUom", "Category"]
    unassigned_df = pd.DataFrame(columns=df_cols)
    for ind, row in df.iterrows():
        if row["ConversionId"] not in conversion_id:
            unassigned_df = unassigned_df.append(row)
    print(unassigned_df)

    unassigned_df.to_csv("data/AMS/preprocessed/Category_Unassigned.csv", index=False)
    #
    # # Duplicate df manually and save it under the name "Category_Unassigned". Copy and paste its content to "Category_Assigned".
    # df = pd.read_csv("data/AMS/preprocessed/Category_Assigned.csv")
    # df['Category'] = df['Category'].astype('int')
    # print(df.dtypes)
    # # for ind, row in assigned_df.iterrows():
    # #     if row["Category"] == 0:
    # #         print("Category unassigned. Please revise before proceeding forward.")
    # #         exit()
    # # df = pd.concat([assigned_df, df], axis=0)
    # # print(df)

    df = pd.read_csv("../data/AMS/preprocessed/Category_Assigned_new.csv")
    df = df.loc[df["Category"] != 0]
    df = df.drop_duplicates(subset=["ConversionId"])
    df = match_ghge_emissions(ghge_factors, df)
    df.to_csv("data/AMS/preprocessed/outcome_test3.csv", index=False)
    df = match_nitrogen_lost(nitro_factors, df)
    df = match_water_withdrawals(water_factors, df)
    df = match_products_to_items(items, df)
    print("000000000")
    print(df)
    df.to_csv("data/AMS/preprocessed/outcome_test0.csv", index=False)
    df = scale_emissions(df)
    df.to_csv("data/AMS/preprocessed/outcome_test8.csv", index=False)
    df = total_emission_by_food(df)
    df.to_csv("data/AMS/preprocessed/outcome_test7.csv", index=False)
    df = assign_weight(df)
    df.to_csv("data/AMS/preprocessed/outcome_test.csv", index=False)
    print(df)

    df = calculate_emissions_per_products(df)
    print("sdfsd fsefs")
    print(df.columns)
    df.to_csv("data/AMS/preprocessed/outcome_test4.csv", index=False)
    df = calculate_100g_emissions(df)
    df.to_csv("data/AMS/preprocessed/outcome_test5.csv", index=False)
    df = calculate_by_weight(df)
    df.to_csv("data/AMS/preprocessed/outcome_test6.csv", index=False)

    parent_prod = ["P-3", "P-1", "P-24", "P-22", "P-13", "P-20", 'P-20', 'P-21', 'P-25',
                   'P-18', 'P-27', 'P-5', 'P-12', 'P-28', 'P-2', 'P-15', 'P-17']

    # for ind, row in df.iterrows():
    #     if row["PrepId"] in parent_prod:
    #         df = df.drop(ind)

    df.to_csv("data/AMS/preprocessed/Labelled_per_Child_Items.csv", index=False)
    print(df)

    print("0sfsdf sdf")
    print(df)
    # df.to_csv("data/AMS/preprocessed/Items_Labelled.csv", index=False)




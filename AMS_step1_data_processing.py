import pandas as pd
import numpy as np
import os
from io import StringIO
import PyPDF2
import glob

path = '/Users/jennylee/CFFS-PyCharm'
os.chdir(path)
filepath = glob.glob(os.path.join(os.getcwd(), "notebooks", "data", "AMS", "*.pdf"))

def import_all_items():
    item_num = 0
    products_list = []
    item_prod_relations = {}
    prod_num_in_items = 0

    for file in filepath:
        #     print(file)

        def generate_items(pdf):
            file = open(str(pdf), "rb")
            pdfReader = PyPDF2.PdfFileReader(file)
            pageObj = pdfReader.getPage(0)
            myfile = pageObj.extractText()
            product = myfile.partition('\n')[0]
            products_list.append(product)
            myfile = myfile.split("\n", 4)[4]
            myfile = myfile.splitlines()
            df = pd.read_csv(StringIO("\n".join(myfile)), sep=" ", names=range(20), on_bad_lines="skip", quotechar=None,
                             quoting=3)

            amounts = df.iloc[:, 0:4]
            amounts_col = ["Single", "Double", "Triple", "Half"]
            amounts.columns = amounts_col
            ingredient = df.iloc[:, 5:]
            ingredient["Description"] = ingredient.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
            ingredient["Description"] = ingredient["Description"].str.replace("nan", "")
            ingredient['Description'] = ingredient['Description'].str.extract('(\d*\.*\d*\s*[A-Z].*$)')
            df = pd.concat([amounts, ingredient["Description"]], axis=1)

            df["ItemId"] = ""

            df[["Amount", "Unit"]] = df["Single"].str.extract(pat=r"(\d+\.?\d*)(.*)")
            ind_num = df[df["Amount"].isnull()].index.tolist()
            min_nan = min(ind_num)
            df = df.iloc[:min_nan]
            df["InventoryGroup"] = ""

            global prod_num_in_items

            df["PrepId"] = "P-" + str(prod_num_in_items)
            prod_num_in_items += 1
            df = df.rename(columns={"Amount": "Qty", "Unit": "UOM"})

            for ind, row in df.iterrows():
                global item_num
                df.loc[ind, "ItemId"] = "I-" + str(item_num)
                item_num += 1

            #         df["PakUOM"] = df["CaseUOM"]
            item_col_list = ["ItemId", "Description", "Qty", "UOM", "PrepId"]
            df = df[item_col_list]

            return df

        temp_df = generate_items(file)
        # global df
        df = pd.concat([df, temp_df], axis=0)

    return df


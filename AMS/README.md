# AMS (2022)

#### Contents
0. Data Structure
1. Items, Child Products, and Products
2. Explaining Workflow
3. Final Outcome

---


## 0. Data Structure
<img src="image/full_KFC_burger.png" width="800" height="400">

All recipes are derived from the **Flavour Lab** located in UBC Vancouver Campus. All data files are provided in **PDF formats**. Original recipe data can be found under `./data/AMS`. 

## 1. Items, Child Products, and Products

| ItemId        | Description       | Qty  | UOM | PrepId |
| -------------: |-------------:| -----:| -----:| -----:| 
| I-0      | Radish-Daikon | 1000.000 | g | P-0 |
| I-1      | 2022.3 Basic Pickling Liquid      |   1000.0 | g | P-0 |
| I-2 | Nori Kizami BTL      |   1.0 | g | P-1 |
| I-3 | 2022.3 Double Down Chicken      |   2.0 | PORT | P-1 |
| I-4 | 2022.3 Rice Patty Cake      |   1.0 | PATTY | P-1 |

- `Items`: Independent ingredients that are used in cooking a product. Each item is given its own **item number** (*e.g.*, I-0...) and is marked to belong to the specific recipe under the corresponding **product number** (*e.g.*, P-0...). 

| PrepId        | Description       | 
| -------------: |-------------:| 
| P-0      | Pickled Daikon | 
| P-1      | Full KFC Double Down      |  
| P-2 | Smoked Tofu Block      |   
| P-3 | Full Aloo Tikki Burger      |   
| P-4 | Pesto Cream      |   

- `Products` (aka "Preps"): Products that are made with **ingredients**. **Child products** are also included in this list. 

| ItemId        | Description       | Qty  | UOM | ProdId | PrepId |
| -------------: |-------------:| -----:| -----:| -----:| -----:| 
| I-3      | 2022.3 Double Down Chicken  | 2.0 | PORT | P-1 | P-20 |
| I-4      | 2022.3 Rice Patty Cake      |   1.0 | PATTY | P-1 | P-21 |
| I-13 | 2022.3 Mint Chutney    |   20.0 | g | P-3 | P-25 |
| I-19 | 2022.3 Aloo Tikki     |   1.0 | PATTY | P-3 | P-18 |
| I-58 | 2022.3 Thyme Oil |   1000.0 | g | P-10 | P-27 |

- `Child Products`: Products that are used in making another product. From the above dataset, child products are identified under **PrepId**, and corresponding parent products are idenfieid under **ProdId**. For example, item number I-3, Double Down Chicken, is equal to P-20 and will ultimately be used in making P-1, Full KFC Double Down.
  - Child products are usually identified by the keyword "2022.3" included in their description. 

## 2. Explaining Workflow
![AMS]("image/AMS_workflow.png")
<img src="image/AMS_workflow.png">




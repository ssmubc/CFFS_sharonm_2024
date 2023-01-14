# AMS (2022)

#### Contents
0. Data Structure
1. Items, Child Products, and Products
2. Explaining Workflow
3. Final Outcome


### 0. Data Structure
<img src="image/full_KFC_burger.png" width="800" height="400">

All recipes are derived from the **Flavour Lab** located in UBC Vancouver Campus. All data files are provided in **PDF formats**. Original recipe data can be found under `./data/AMS`. 

### 1. Items, Child Products, and Products
<img src="image/items_df.png" width="450" height="800">


| ItemId        | Description       | Qty  | UOM | PrepId |
| ------------- |:-------------:| -----:| -----:| -----:| 
| I-0      | Radish-Daikon | 1000.000 | g | P-0 |
| I-1      | 2022.3 Basic Pickling Liquid      |   1000.0 | g | P-0 |
| I-2 | Nori Kizami BTL      |   1.0 | g | P-1 |

- `Items`: Independent ingredients that are used in cooking a product. Each item is given its own **item number** (*e.g.*, I-0...) and is marked to belong to the specific recipe under the corresponding **product number** (*e.g.*, P-0...). 

<img src="image/prep_df.png" width="350" height="760">

- `Products`: Independent ingredients that are used in cooking a product. Each item is given its own **item number** (*e.g.*, I-0...) and is marked to belong to the specific recipe under the corresponding **product number** (*e.g.*, P-0...). 



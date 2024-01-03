import pandas as pd
import numpy as np
import dash
from dash import Dash, html, dcc, dash_table, ctx
import dash_bootstrap_components as dbc
from dash import callback_context
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import plotly
import os
import plotly.express as px
import plotly.graph_objects as go
import base64

OK = pd.read_csv("../data/final/2022_2023_CFFS_Outcomes/Data_Labelled_OK22-23_with_name.csv")
OK = OK.dropna(subset=["Category"])
OK["Restaurant"] = "Open Kitchen"

Gather = pd.read_csv("../data/final/2022_2023_CFFS_Outcomes/Data_Labelled_Gather22-23_with_name.csv")
Gather = Gather.dropna(subset=["Category"])
Gather["Restaurant"] = "Gather"

Feast = pd.read_csv("../data/final/2022_2023_CFFS_Outcomes/Data_Labelled_Feast22-23_with_name.csv")
Feast = Feast.dropna(subset=["Category"])
Feast["Restaurant"] = "Feast"

df = pd.concat([OK, Gather], axis=0)
df = df.reset_index().drop(["index"], axis=1)
df = pd.concat([df, Feast], axis=0)

df = df.rename(columns={"GHG Emission (g) / 100g": "GHG Emission",
                       "N lost (g) / 100g": "Nitrogen Lost",
                       "Freshwater Withdrawals (L) / 100g": "Freshwater Withdrawals",
                       "Combined Label":"Label"})

df.to_csv("data/final/2022_2023_CFFS_Outcomes/UBCFS_summary.csv")

print(df)
print(len(df))

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX, dbc_css])
image_path = "../image/ubc-logo.png"

server = app.server

encoded_image = base64.b64encode(open(image_path, "rb").read())

app.layout = html.Div([

    # Entire Row
    dbc.Row([
        # First Column
        dbc.Col([

            html.Div([
                # First Row under the column
                dbc.Row([dbc.Col(html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                                          style={"margin-top": "10px"}))],
                        style={"textAlign": "center", "margin-top": "18px", "margin-bottom": "10px"}),

                dbc.Row([dbc.Col(html.H1("Residance Hall Food Emission Labels",
                                         style={"textAlign": "center", "margin-bottom": "15px",
                                                "margin-top": "20px", "color": "white",
                                                "fontSize": 16}))]),

                dbc.Row([html.Label("Select Restaurant:", style={"color": "white"}),
                         dcc.Dropdown(id="restaurant_dropdown",
                                      options=[{"label": r, "value": r} for r in df["Restaurant"].unique().tolist()],
                                      value="Restaurant",
                                      multi=False,
                                      style={"margin-bottom": "10px"})]),

                dbc.Row([html.Label("Select Category:", style={"color": "white"}),
                         dcc.Dropdown(id="category_dropdown",
                                      options=[],
                                      value="Category",
                                      multi=False,
                                      style={"margin-bottom": "10px"})]),

                dbc.Row([html.Label("Select Menu Item:", style={"color": "white"}),
                         dcc.Dropdown(id="item_dropdown",
                                      options=[],
                                      value="Displayed Name",
                                      multi=False,
                                      style={"margin-bottom": "10px"})]),
            ]),

        ], width=3, style={'background-color': '#002145'}),

        # Second Column
        dbc.Col([

            html.Div([
                dbc.Row([
                    dash_table.DataTable(
                        style_table={'overflowX': 'auto'},
                        id="menu_item_table",
                        columns=[{"name": i, "id": i, "deletable": True, "selectable": True, "type": "numeric"}
                                 for i in df.loc[:, ["ProdId", "Description", "GHG Emission",
                                                     "Nitrogen Lost", "Freshwater Withdrawals", "Label"]]],
                        data=df.to_dict("records"),
                        selected_columns=[],
                        page_size=15,
                        selected_rows=[],
                        filter_action="native",
                        page_action="native",
                        style_as_list_view=True,
                        editable=True,
                        sort_action="native",
                        style_header={"backgroundColor": "rgb(12, 35, 68)",
                                      "fontweight": "bold", "color": "white",
                                      "font_size": "13px"},
                        style_cell={"font_family": "arial",
                                    "font_size": "12px",
                                    "text_align": "left"},
                        style_data={'backgroundColor': 'transparent'},
                        sort_mode="single")], style={"margin-top": "15px"}),

                dbc.Row([
                    dcc.Markdown(children="""
                    - All emission factors are calculated on basis of **100g** of the selected menu item. 
                    - Unit of measurement: GHG Emission (g), Nitrogen lost (g), Freshwater Withdrawals (L). 
                    """, style={"font_size": "15px"})
                ]),

                dbc.Row([
                    dcc.Markdown(id="markdown_results")
                ]),

            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dcc.Input(id="element_to_hide"),
                        dbc.CardBody([html.H4("Test")], className="text-center"),
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dcc.Input(id="element_to_hide2"),
                        html.Img(id="label_figure")
                    ])
                ], width=9)
            ], style={"margin-top": "10px", "margin-bottom": "10px", "width": "100%",
                      "margin-left": "10px", "margin-right": "10px", "display": "none"}),

            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        html.H2("Visualizations", style={"fontSize": 18, "textAlign": "center"}),
                        dbc.ButtonGroup([
                            dbc.Button("GHG Emissions", id="GHG_button", size="sm",
                                       style={"display": "inline-block", "verticalAlign": "middle",
                                              "background-color": "rgb(12, 35, 68)", "color": "white", 'width': '10em'},
                                       className="me-md-2"),
                            dbc.Button("Nitrogren Emissions", id="nitrogen_button", size="sm",
                                       style={"display": "inline-block", "verticalAlign": "middle",
                                              "background-color": "rgb(12, 35, 68)", "color": "white", 'width': '10em'},
                                       className="me-md-2"),
                            dbc.Button("Freshwater Withdrawals", id="freshwater_button", size="sm",
                                       style={"display": "inline-block", "verticalAlign": "middle",
                                              "background-color": "rgb(12, 35, 68)", "color": "white", 'width': '10em'},
                                       className="me-md-2")
                        ], className="border-0 bg-transparent"),

                    ], style={"border": "0px"}))
            ], style={"margin-top": "18px", "margin-bottom": "3px", "width": "100%",
                      "margin-left": "10px", "margin-right": "10px"}),

            html.Div(id="graph_content")

        ], width=9, style={'background-color': '#FFFFFF'}, className="dbc dbc-row-selectable")

    ], style={"height": "100vh"})

], style={"width": "100vw"})

@app.callback(
    Output("category_dropdown", "options"),
    [Input("restaurant_dropdown", "value")])
def get_category_per_restaurants(restaurant_dropdown):
    df_categorized = df[df["Restaurant"] == restaurant_dropdown]
    return [{"label": c, "value": c} for c in df_categorized["Category"].unique()]

@app.callback(
    Output("item_dropdown", "options"),
    [Input("category_dropdown", "value")],
    [Input("restaurant_dropdown", "value")])
def get_category_per_restaurants(category_dropdown, restaurant_dropdown):
    df_categorized = df[df["Restaurant"] == restaurant_dropdown]
    df_items = df_categorized[df_categorized["Category"] == category_dropdown]
    return [{"label": n, "value": n} for n in df_items["Displayed Name"].unique()]

@app.callback(
    Output("menu_item_table", "data"),
    [Input("restaurant_dropdown", "value")],
    [Input("category_dropdown", "value")],
    [Input("item_dropdown", "value")])
def get_selected_menu_item(restaurant_dropdown, category_dropdown, item_dropdown):
    if restaurant_dropdown is None:
        data = df.to_dict("records")
        return data
    if (restaurant_dropdown is None) & (category_dropdown is None) & (item_dropdown is None):
        data = df.to_dict("records")
    if restaurant_dropdown != None:
        df_categorized = df[df["Restaurant"] == restaurant_dropdown]
        data = df_categorized.to_dict("records")
    if (restaurant_dropdown != None) & (category_dropdown != None):
        df_categorized = df[df["Restaurant"] == restaurant_dropdown]
        df_items = df_categorized[df_categorized["Category"] == category_dropdown]
        data = df_items.to_dict("records")
    if (restaurant_dropdown != None) & (category_dropdown != None) & (item_dropdown != None):
        df_categorized = df[df["Restaurant"] == restaurant_dropdown]
        df_items = df_categorized[df_categorized["Category"] == category_dropdown]
        df_selected = df_items[df_items["Displayed Name"] == item_dropdown]
        data = df_selected.to_dict("records")
    return data


@app.callback(
    Output("markdown_results", "children"),
    [Input("restaurant_dropdown", "value")],
    [Input("category_dropdown", "value")],
    [Input("item_dropdown", "value")])
def get_label_displayed(restaurant_dropdown, category_dropdown, item_dropdown):
    df["Label"] = df["Label"].str.upper()
    if (item_dropdown == None) or (restaurant_dropdown == None) or (category_dropdown == None):
        return ""
    if category_dropdown == None:
        return ""
    else:
        df_label = df.loc[(df["Restaurant"] == restaurant_dropdown) & (df["Category"] == category_dropdown) & (
                    df["Displayed Name"] == item_dropdown), "Label"].values[0]
        # df_label = df[(df["Restaurant"] == restaurant_dropdown) & (df["Category"] == category_dropdown) & (
        #         df["Displayed Name"] == item_dropdown)].Label.item()
        print(df_label)
        return f"**Selected item is labelled as {df_label}.**"


@app.callback(
    Output("markdown_results", "style"),
    [Input("markdown_results", "children")])
def get_label_colored(markdown_results):
    output = markdown_results
    print(output)
    if "YELLOW" in output:
        color = {"color": "orange", "font_size": "15px"}
        return color
    if "RED" in output:
        color = {"color": "red", "font_size": "15px"}
        return color
    if "GREEN" in output:
        color = {"color": "green", "font_size": "15px"}
        return color
    else:
        color = {"color": "grey"}

@app.callback(
    Output("graph_content", "children"),
    [Input("GHG_button", "n_clicks")],
    [Input("nitrogen_button", "n_clicks")],
    [Input("freshwater_button", "n_clicks")])
#     [State("restaurant_dropdown", "value")],
#     [State("category_dropdown", "value")],
#     [State("item_dropdown", "value")])
def display_histogram(GHG_button, nitrogen_button, freshwater_button):
    OK = df.loc[df["Restaurant"] == "Open Kitchen"]
    Gather = df.loc[df["Restaurant"] == "Gather"]
    Feast = df.loc[df["Restaurant"] == "Feast"]
    all_colors = {"Open Kitchen": "#4E68B2",
                  "Gather": "#E85B66",
                  "Feast": "#82C48C"}

    def all_restaurants(feature):
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Boxplot"), shared_yaxes=False)
        fig.add_trace(go.Histogram(x=OK[feature], nbinsx=20, opacity=0.8, name="Open Kitchen",
                                   marker_color=all_colors["Open Kitchen"]), row=1, col=1)
        fig.add_trace(
            go.Histogram(x=Gather[feature], nbinsx=20, opacity=0.8, name="Gather", marker_color=all_colors["Gather"]),
            row=1, col=1)
        fig.add_trace(
            go.Histogram(x=Feast[feature], nbinsx=20, opacity=0.8, name="Feast", marker_color=all_colors["Feast"]),
            row=1, col=1)
        fig.add_trace(go.Box(y=OK[feature], name="Open Kitchen", marker_color=all_colors["Open Kitchen"]), row=1, col=2)
        fig.add_trace(go.Box(y=Gather[feature], name="Gather", marker_color=all_colors["Gather"]), row=1, col=2)
        fig.add_trace(go.Box(y=Feast[feature], name="Feast", marker_color=all_colors["Feast"]), row=1, col=2)

        fig.update_xaxes(row=1, col=2, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_xaxes(row=1, col=1, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_yaxes(row=1, col=2, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_yaxes(row=1, col=1, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_layout(plot_bgcolor="white", showlegend=True, legend_title="Restaurant",
                          title=feature + " Comparisons Across Restaurants", title_x=0.5)

        names = set()
        fig.for_each_trace(
            lambda trace:
            trace.update(showlegend=False)
            if (trace.name in names) else names.add(trace.name))

        return fig

    def specific_restaurant(df, feature):
        fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram", "Boxplot"), shared_yaxes=False)
        fig.add_trace(go.Histogram(x=df[feature], nbinsx=20, opacity=0.8), row=1, col=1)
        fig.add_trace(go.Box(y=df[feature]), row=1, col=2)

        fig.update_xaxes(title_text=feature, row=1, col=2, showline=True, linecolor="#002145", showgrid=True,
                         linewidth=1.2)
        fig.update_xaxes(title_text=feature, row=1, col=1, showline=True, linecolor="#002145", showgrid=True,
                         linewidth=1.2)
        fig.update_yaxes(row=1, col=2, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_yaxes(row=1, col=1, showline=True, linecolor="#002145", showgrid=True, linewidth=1.2)
        fig.update_layout(plot_bgcolor="white", showlegend=False)
        return fig

    ctx = dash.callback_context
    button_clicked = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_clicked == "GHG_button":
        fig = all_restaurants("GHG Emission")
        return dcc.Graph(id="GHG_graph", figure=fig)

    if button_clicked == "nitrogen_button":
        fig = all_restaurants("Nitrogen Lost")
        return dcc.Graph(id="nitrogen_graph", figure=fig)

    if button_clicked == "freshwater_button":
        fig = all_restaurants("Freshwater Withdrawals")
        return dcc.Graph(id="freshwater_graph", figure=fig)

if __name__ ==  "__main__":
    app.run_server(debug=True)


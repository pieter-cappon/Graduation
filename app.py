import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

''' Initialize app '''

app = dash.Dash(external_stylesheets=[dbc.themes.SANDSTONE])

app.title = "Smart Utrecht Forestry"

''' Df selection / cleaning'''

df = pd.read_csv("20200127bomen.csv", encoding='latin1')

df = df[["Nederlandse naam", "Wetenschappelijke naam", "Plantjaar", "Leeftijd", "Buurt", "Wijk", "Lat", "Long"]]

df['Leeftijd'] = df['Leeftijd'].replace(2011, 9)
df['Plantjaar'] = df['Plantjaar'].replace(9, 2011)
df['Leeftijd'] = df['Leeftijd'].replace(2001, 19)
df['Plantjaar'] = df['Plantjaar'].replace(19, 2001)
df.drop(130961, inplace=True)
df.dropna(inplace=True)

mean_ages = pd.read_csv('Mean_Age_Districts.csv')
mean_ages = mean_ages[['Wijk', 'Mean age']].round(2)

soorten_df = df.groupby(["Wijk", "Wetenschappelijke naam"])['Wetenschappelijke naam'].count().to_frame(name = 'Total').reset_index()

numofrows = df.shape[0]

SDI = [['Zuidwest', 0.03143715924225582], ['Noordoost',0.024968487434014773], ['Leidsche Rijn', 0.03309229444909943],['Binnenstad', 0.04614357174074194],['Oost',0.05202990663774153],['Overvecht', 0.0402352148912507], ['Vleuten - De Meern', 0.03453191369010953], ['West', 0.0314581835480503],['Zuid', 0.03581973362367767], ['Noordwest', 0.020158597647356048]]
SDI_df = pd.DataFrame(SDI, columns = ['District', 'Value'])

hor_bar = px.bar(SDI_df, x="Value", y="District", orientation='h')
hor_bar.update_layout(title_text="Simpson's Diversity Index")
hor_bar.update_layout(yaxis={'visible': False})
''' Create graph functions '''

# Distribution of age

bar = px.histogram(df, x="Leeftijd", y="Leeftijd", height= 350, color_discrete_sequence=["green"])
bar.update_layout(title_text="Age distribution", yaxis_title="Amount",xaxis_title="Age", height= 450)

boxplot = px.box(df, y="Wijk", x="Leeftijd", orientation='h')
boxplot.update_layout(title_text="Age distribution: per district")

age_table = ff.create_table(mean_ages)
age_table.update_layout(title_text='Average age per district')

# Map 
fig = px.scatter_mapbox(df, lat="Long", lon="Lat", hover_name="Wetenschappelijke naam", hover_data=["Nederlandse naam", "Leeftijd"],
                     zoom=11, height= 750, color="Leeftijd", color_continuous_scale='Greens', opacity=0.5)
fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, height=450)

# Treemap for diversity in species 

treemap = px.treemap(soorten_df, path=['Wijk', 'Wetenschappelijke naam'], values='Total', color_continuous_scale='algae', color='Total')
treemap.update_layout(title_text='Distribution of species')

# Indicators

# Dot Plot

numoftrees = go.Figure()

numoftrees.add_trace(go.Indicator(
    mode= "number",
    value= numofrows,
    title= {'text': "Aantal bomen"},
    domain= {'x': [0,0.5], 'y': [0.5,1]}
))

'''
numoftrees.add_trace(go.Indicator(
    mode= "number",
    value= len(df['Wetenschappelijke naam'].value_counts()),
    title= {'text': "Aantal soorten"},
    domain={'x':[0,0.5], 'y': [0,0.5]}
))

numoftrees.update_layout(
    font= dict(
        family="Open Sans",
))

'''

''' Pages '''


'''
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("Slider"),
                                    dcc.RangeSlider(
                                        id='age-slider',
                                        min=df['Leeftijd'].min(),
                                        max=df['Leeftijd'].max(),
                                        value=[0,244],
                                        step=1,
                                        marks={str(Leeftijd): str(Leeftijd) for Leeftijd in df['Leeftijd'].unique()}
                                    )  
                                ]
                            )
                        ),
                    ),
                    md=12,
                )
            ]
        ),
        '''

trees = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5('Spatial distribution and age of trees'),
                                    dcc.Graph(
                                        figure = fig
                                    )
                                ]
                            )
                        )
                    ]),
                ),              
            ]
        ),
        html.Br(),
        html.H2('Diversity'),
        html.Br(),        
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure= treemap
                        )
                    ]
                    ),
                    
                    md=6,
                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure= hor_bar
                        )
                    ]
                    ),
                    md=6,
                ),
            ]
        ),
        html.Br(),  
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure= bar
                        )
                    ]),
                    md=5,
                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure= boxplot
                        )
                    ]),
                    md=5,
                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            figure= age_table
                        )
                    ]),
                    md=2,
                ),
            ]
        )
    ]
)

fragstats = pd.read_csv('fragstats_Utrecht.csv')
fragstats.rename(columns={"total_area": "Total Area (ha)", "patch_density": "Patch Density", "largest_patch_index": "Largest Patch Index", "proportion_of_landscape": "Proportion Of Landscape (%)", "area_mn": "Mean Patch Area (ha)"}, inplace=True)
fragstats = fragstats[["Area", "Proportion Of Landscape (%)", "Total Area (ha)", "Patch Density", "Largest Patch Index",  "Mean Patch Area (ha)"]].round(3)

bubble = px.scatter(fragstats, x="Largest Patch Index", y="Patch Density",
	         size="Proportion Of Landscape (%)", 
                 hover_name="Area", size_max=60)
bubble.update_layout(margin={"r":5,"t":30,"l":4,"b":5})
bubble.update_layout(title_text="Patch Density vs. Largest Patch Index", yaxis_title='Patch Density', xaxis_title='Largest Patch Index')

table =  ff.create_table(fragstats)

fragmentation = html.Div(
    [   
        html.H2("Fragmentation Statistics"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        dcc.Graph(
                            figure= bubble
                        )
                    )
                )
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        dcc.Graph(
                            figure= table
                        )
                    )
                )
            ]
        ),
    ]
)

# the style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"
}

sidebar = html.Div(
    [
        html.H2("Smart Utrecht Forestry", className="display-4"),
        html.Hr(),
        html.P(
            "This dashboard displays the urban forestry of Utrecht, use the filters to select a district and get more insight in the urban forestry of this area.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Trees", href="/page-1", id="page-1-link"),
                dbc.NavLink("Fragmentation", href="/page-2", id="page-2-link"),
                dbc.NavLink("", href="/page-3", id="page-3-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
'''
@app.callback(
    [Output('age-map', 'figure')],
    [Input('age-slider', 'value')],
)
def update_map(selected_year):
    filtered_df = df[df.Leeftijd == selected_year]
    
    return {
    px.scatter_mapbox(filtered_df, lat="Long", lon="Lat", hover_name="Wetenschappelijke naam", hover_data=["Nederlandse naam", "Leeftijd"],
                     zoom=11, height= 750, color="Leeftijd", color_continuous_scale='Greens', opacity=0.5, mapbox_style="stamen-toner")
    }
'''
@app.callback(
    [Output(f"page-{i}-link", "active") for i in range(1, 4)],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/page-{i}" for i in range(1, 4)]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/page-1"]:
        return (trees)
    elif pathname == "/page-2":
        return (fragmentation)
    elif pathname == "/page-3":
        return html.P("Oh cool, this is page 3!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


if __name__ == "__main__":
    app.run_server(debug=True)
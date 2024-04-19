import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

# Load your cleaned dataset
df = pd.read_csv('../../pythonProject/data/healthy_lifestyle_city_2021_with_coords.csv')

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Global City Health Metrics", style={'textAlign': 'center'}),

    html.Div([
        html.Button("Select All", id="select-all", n_clicks=0),
        html.Button("Deselect All", id="deselect-all", n_clicks=0),
        dcc.Checklist(
            id='city-checklist',
            options=[{'label': city, 'value': city} for city in df['City'].unique()],
            value=df['City'].unique().tolist(),
            style={'height': '100%', 'overflowY': 'auto', 'display': 'block'}
        ),
        html.Hr(),
        html.H3("Select Columns", style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='column-selector',
            options=[{'label': col, 'value': col} for col in df.columns],
            value=['City', 'Rank', 'Happiness levels(Country)', 'Cost of a bottle of water(City)'],
            multi=True
        )
    ], style={'width': '20%', 'float': 'left', 'display': 'flex', 'flexDirection': 'column'}),

    html.Div([
        dcc.Graph(id='life-expectancy-map', config={'displayModeBar': False}),
        html.P("Note: The size of the circle represents the happiness level.", style={'textAlign': 'left', 'marginTop': '0px'}),
        dcc.Graph(id='scatter-plot', style={'paddingTop': '20px'}),
        dcc.Graph(id='extra-plot', style={'paddingTop': '20px'}),
        html.Div([
            html.H3("Details Table", style={'textAlign': 'center'}),
            dash_table.DataTable(
                id='details-table',
                style_table={'overflowX': 'auto', 'width': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'}
            )
        ], style={'width': 'auto', 'margin': 'auto'})
    ], style={'width': '80%', 'float': 'right'})
])


@app.callback(
    Output('city-checklist', 'value'),
    [Input('select-all', 'n_clicks'), Input('deselect-all', 'n_clicks')],
    [State('city-checklist', 'options'), State('city-checklist', 'value')]
)
def update_checklist(select_all_clicks, deselect_all_clicks, options, current_values):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['value'] is None:
        return current_values
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == "select-all":
        return [option['value'] for option in options]
    elif button_id == "deselect-all":
        return []
    return current_values

@app.callback(
    [Output('life-expectancy-map', 'figure'),
     Output('scatter-plot', 'figure'),
     Output('extra-plot', 'figure'),
     Output('details-table', 'data'),
     Output('details-table', 'columns')],
    [Input('city-checklist', 'value'), Input('column-selector', 'value')]
)
def update_output(selected_cities, selected_columns):
    filtered_df = df[df['City'].isin(selected_cities)]

    # Map showing life expectancy
    fig_map = px.scatter_geo(filtered_df,
                            lat='Latitude',
                            lon='Longitude',
                            size='Happiness levels(Country)',  # Circle size reflects happiness levels
                            hover_data={'City': True, 'Life expectancy(years) (Country)': True},
                            color='Life expectancy(years) (Country)',
                            color_continuous_scale='Viridis',
                            title='Life Expectancy of Selected Cities',
                            projection='natural earth',
                            size_max=15,  # Adjust maximum marker size
                            labels={'Life expectancy(years) (Country)': 'Life Expectancy'})  # Label for the color scale

    # Ensure the graph layout is updated to display all titles and legends correctly
    fig_map.update_layout(coloraxis_colorbar=dict(title='Life Expectancy'))


    # Update layout to show legends, including one for size
    
    fig_map.update_layout(legend_title_text='Happiness Level Scale')
    fig_map.update_traces(marker=dict(sizeref=2.*max(df['Happiness levels(Country)'])/(15**2),
                                    sizemode='area'),
                        selector=dict(type='scattergeo'))


    # Scatter plot for life expectancy vs happiness levels
    fig_scatter = px.scatter(filtered_df,
                             x='Happiness levels(Country)',
                             y='Life expectancy(years) (Country)',
                             color='City',
                             title='Life Expectancy vs Happiness Levels')

    # Extra plot for pollution vs cost of a bottle of water
    fig_extra = px.scatter(filtered_df,
                           x='Cost of a bottle of water(City)',
                           y='Pollution(Index score) (City)',
                           labels={'variable': 'Metric', 'Cost of a bottle of water(City)': 'Cost of a water bottle (£)'},
                           color='City',
                           title='Pollution vs Cost of a water bottle')

    # Data for the details table
    if selected_columns:
        table_data = filtered_df[selected_columns].to_dict('records')
        table_columns = [{'name': col, 'id': col} for col in selected_columns]
    else:
        table_data = []
        table_columns = []

    return fig_map, fig_scatter, fig_extra, table_data, table_columns

if __name__ == '__main__':
    app.run_server(debug=True)

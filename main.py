import dash
import dash_core_components as dcc
import dash_html_components as html
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics
# for api 
import quandl
import plotly.graph_objects as go
import numpy as np
from dash.dependencies import Input, Output
# create heatmap
import seaborn as sns
import pandas as pd

from config import QUANDL_API_KEY

# 
quandl.ApiConfig.api_key = QUANDL_API_KEY
{}
country_codes = {
    'inflation':{
    'usa': 'RATEINF/INFLATION_USA',
    'canada': 'RATEINF/INFLATION_CAN',
    'euro area': 'RATEINF/INFLATION_EUR',
    'france': 'RATEINF/INFLATION_FRA',
    'italy': 'RATEINF/INFLATION_ITA',
    'japan': 'RATEINF/INFLATION_JPN',
    'switzerland': 'RATEINF/INFLATION_CHE',
    'uk': 'RATEINF/INFLATION_GBR'

    },
    'cpi':{
    'usa':'RATEINF/CPI_USA',
    'canada': 'RATEINF/CPI_CAN',
    'germany': 'RATEINF/CPI_DEU',
    'euro area': 'RATEINF/CPI_EUR',
    'france': 'RATEINF/CPI_FRA',
    'italy': 'RATEINF/CPI_ITA',
    'japan': 'RATEINF/CPI_JPN',
    'switzerland': 'RATEINF/CPI_CHE',
    'uk': 'RATEINF/CPI_GBR'
}
}

# start dashboard
app = dash.Dash(__name__)
# layout of html page
app.layout = html.Div([
    html.H1('Country Data Dashboard', style={'textAlign': 'center', 'color': '#7FDBFF'}),

    html.Div([
        dcc.Dropdown(
            id='data-type-dropdown',
            options=[{'label': i.title(), 'value': i} for i in country_codes.keys()],
            value='inflation',
            style={'width': '40%', 'height': '50px', 'fontSize': '18px'}
        ),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': i.title(), 'value': i} for i in country_codes['inflation'].keys()],
            value='usa',
            style={'width': '40%', 'height': '50px', 'fontSize': '18px'}
        ),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),

    dcc.RangeSlider(
        id='year-slider',
        min=2000,
        max=2022,
        step=1,
        value=[2000, 2022],
        marks={str(year): str(year) for year in range(2000, 2023, 2)}
    ),

    html.Div([
        dcc.Graph(id='graph', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='prediction-graph', style={'width': '49%', 'display': 'inline-block'}),
    ]),

    html.Div([
        dcc.Graph(id='bar-chart', style={'width': '49%', 'display': 'inline-block'}),
        dcc.Graph(id='heatmap', style={'width': '49%', 'display': 'inline-block'}),
    ]),
], style={'padding': '10px'})

# callback function updates charts when changing filter
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('data-type-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_bar_chart(data_type, country):
    # Fetch the data from Quandl
    data = quandl.get(country_codes[data_type][country], start_date='2000-01-01', end_date='2022-12-31')
    
    # Calculate the yearly change in the data
    yearly_change = data['Value'].diff()
    
    # Create a bar chart with the yearly change data
    fig = go.Figure(data=go.Bar(x=yearly_change.index, y=yearly_change, name=f'Yearly Change in {data_type.title()} Rate'))
    
    # Update the layout of the figure
    fig.update_layout(title=f'Yearly Change in {data_type.title()} Over Time ({country.title()})', xaxis_title='Year', yaxis_title=f'Change in {data_type.title()} Rate')
    
    return fig
def update_country_dropdown(data_type):
    return [{'label': i.title(), 'value': i} for i in country_codes[data_type].keys()]

# callback update chart
@app.callback(
    Output('graph', 'figure'),
    [Input('data-type-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(data_type, country, year_range):
    # Fetch the data from Quandl
    data = quandl.get(country_codes[data_type][country], start_date=f'{year_range[0]}-01-01', end_date=f'{year_range[1]}-12-31')
    
    # Create a figure with the data
    fig = go.Figure(data=go.Scatter(x=data.index, y=data['Value'], mode='lines+markers', name=f'{data_type.title()} Rate'))
    
    # Update the layout of the figure
    fig.update_layout(title=f'{data_type.title()} Over Time ({country.title()})', xaxis_title='Year', yaxis_title=f'{data_type.title()} Rate')
    
    return fig

# callback update chart
@app.callback(
    Output('prediction-graph', 'figure'),
    [Input('data-type-dropdown', 'value'),
     Input('country-dropdown', 'value')]
)
def update_prediction_graph(data_type, country):
    # Fetch the data from Quandl
    data = quandl.get(country_codes[data_type][country], start_date='2000-01-01', end_date='2022-12-31')
    
    # Prepare the data for the predictive model
    X = np.array(range(len(data))).reshape(-1, 1)
    y = data['Value']
    
    # Split the data into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Create a Linear Regression model and train it using the training sets
    model = LinearRegression().fit(X_train, y_train)

    # Make predictions using the testing set
    y_pred = model.predict(X_test)

    # Create a figure for the predictions and add traces for actual and predicted values
    fig = go.Figure([
        go.Scatter(x=X_test.flatten(), y=y_test, mode='markers', name='Actual'),
        go.Scatter(x=X_test.flatten(), y=y_pred, mode='lines', name='Predicted')
    ])
    
    # Update the layout of the figure
    fig.update_layout(title=f'Predicted {data_type.title()} Over Time ({country.title()})', xaxis_title='Year', yaxis_title=f'{data_type.title()} Rate')

    return fig

dcc.Graph(id='heatmap'),

# callback update chart
@app.callback(
    Output('heatmap', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_heatmap(country):
    # Fetch the data for all data types from Quandl
    data = {data_type: quandl.get(country_codes[data_type][country], start_date='2000-01-01', end_date='2022-12-31')['Value'] for data_type in country_codes.keys()}
    
    correlation = pd.DataFrame(data).corr()
    
    # create heatmap
    fig = go.Figure(data=go.Heatmap(
    z=correlation.values,
    x=list(correlation.columns),
    y=list(correlation.index),
    colorscale='RdBu',  # Change the color scale
    zmin=-1,  # Ensure that the color scale goes from -1 to 1
    zmax=1,
    hoverongaps=False))

    # Update the layout of the figure
    fig.update_layout(
    title=f'Correlation Heatmap ({country.title()})',
    xaxis_title='Data Type',
    yaxis_title='Data Type',
    autosize=True,  
    margin=dict(l=50, r=50, b=100, t=100, pad=4),
)
    
    return fig

if __name__ == '__main__':
   app.run_server(debug=True)
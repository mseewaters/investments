import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import dash_table

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Retirement Savings Model"),
    
    html.Div([
        html.Div([
            html.Label("Current Investments ($)"),
            dcc.Input(id='current-investments', type='number', value=5000000, min=0),
            
            html.Label("Annual Investment Return (%)"),
            dcc.Input(id='annual-return', type='number', value=5.0, min=0, step=0.1),
            
            html.Label("Monthly Spend ($)"),
            dcc.Input(id='monthly-spend', type='number', value=10000, min=0)
        ], style={'width': '45%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label("Annual Inflation Rate (%)"),
            dcc.Input(id='annual-inflation', type='number', value=2.0, min=0, step=0.1),
            
            html.Label("Year of Retirement"),
            dcc.Input(id='retirement-year', type='number', value=2055, min=2025)
        ], style={'width': '45%', 'display': 'inline-block', 'marginLeft': '5%'})
    ]),
    
    dcc.Graph(id='savings-graph'),
    
    dash_table.DataTable(id='savings-table',
                         columns=[
                             {'name': 'Year', 'id': 'Year'},
                             {'name': 'Savings ($M)', 'id': 'Savings ($M)'},
                             {'name': 'Spend ($K)', 'id': 'Spend ($K)'},
                             {'name': 'Returns ($K)', 'id': 'Returns ($K)'}
                         ],
                         style_table={'overflowX': 'auto'})
])

@app.callback(
    [Output('savings-graph', 'figure'),
     Output('savings-table', 'data')],
    [Input('current-investments', 'value'),
     Input('annual-return', 'value'),
     Input('monthly-spend', 'value'),
     Input('annual-inflation', 'value'),
     Input('retirement-year', 'value')]
)
def update_graph_and_table(current_investments, annual_return, monthly_spend, annual_inflation, retirement_year):
    years = list(range(2025, 2075))
    savings_by_year = []
    spend_by_year = []
    returns_by_year = []
    savings = current_investments
    
    for year in years:
        savings *= (1 + annual_return / 100)
        returns = savings * annual_return / 100
        adjusted_spend = monthly_spend * 12 * (1 + annual_inflation / 100) ** (year - 2025)
        savings -= adjusted_spend
        
        savings_by_year.append(savings)
        spend_by_year.append(adjusted_spend)
        returns_by_year.append(returns)
    
    savings_plot = [round(s / 1_000_000, 2) for s in savings_by_year]
    spend_in_thousands = [round(s / 1_000, 2) for s in spend_by_year]
    returns_in_thousands = [round(r / 1_000, 2) for r in returns_by_year]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=savings_plot, mode='lines+markers', name='Savings ($M)'))
    fig.update_layout(title='Retirement Savings Projection', xaxis_title='Year', yaxis_title='Savings ($M)', grid=dict(visible=True))
    
    table_data = pd.DataFrame({
        'Year': years,
        'Savings ($M)': savings_plot,
        'Spend ($K)': spend_in_thousands,
        'Returns ($K)': returns_in_thousands
    }).to_dict('records')
    
    return fig, table_data

if __name__ == '__main__':
    app.run_server(debug=True)

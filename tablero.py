import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

coef_df=pd.read_csv('coef_df.csv')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H3("Modelo de Predicción de Productividad"),  
    html.H5("Ingrese los Parámetros"),  
    html.Div(["Ingrese el número de trabajadores del equipo (usualmente entre 5 y 70):",
              dcc.Input(id='no_of_workers', type='number', value=20)]),
    html.Br(),
    html.Div(["Ingrese la productividad objetivo del equipo (debe estar entre 0 y 1):",
              dcc.Input(id='targeted_productivity', type='number', value=0.7)]),
    html.Br(),
    html.Div(["Ingrese el tiempo asignado para la tarea en minutos estándar (usualmente entre 5 y 50):",
              dcc.Input(id='smv', type='number', value=40)]),
    html.Br(),
    html.Div(["Ingrese el incentivo financiero (usualmente menor a 100):",
              dcc.Input(id='incentive', type='number', value=70)]),
    html.Br(),
    html.Label("Use el slider para seleccionar el número de trabajadores inactivos debido a la interrupción de la productividad"),
    dcc.Slider(
        id='idle_men_slider',
        min=0,
        max=50,
        marks={str(men): str(men) for men in range(0,51)},
        step=1,
        value=5 
    ),
    html.Br(),
    html.H5("Resultados de Productividad"),
    dcc.Graph(id='graph_prod'),  # Componente de gráfica
    html.Div(id='productivity_summary')
])

@app.callback(
    [Output('graph_prod', 'figure'),
     Output('productivity_summary', 'children')],
    [Input('no_of_workers', 'value'),
     Input('targeted_productivity', 'value'),
     Input('smv', 'value'),
     Input('incentive', 'value'),
     Input('idle_men_slider', 'value')]
)
def update_figure(no_of_workers, targeted_productivity, smv, incentive, idle_men):
    # Calcular productividad
    productividades = []
    for i in range(1, 13):
        coefs = coef_df[f'Model_{i}']
        productividad = (coefs[0] +
                         coefs[1] * no_of_workers +
                         coefs[2] * targeted_productivity +
                         coefs[3] * smv +
                         coefs[4] * incentive +
                         coefs[5] * idle_men)
        productividad = max(0, min(1, productividad))
        productividades.append(productividad)
    
    max_productivity_index = productividades.index(max(productividades))
    min_productivity_index = productividades.index(min(productividades))
    max_team = f'Equipo {max_productivity_index + 1}'
    min_team = f'Equipo {min_productivity_index + 1}'

    # Texto resumen
    summary_text = f"Para los parámetros dados, el equipo con mayor productividad es el {max_team} y el equipo con menor productividad es el {min_team}."

    # Crear gráfica de barras
    equipos = [f'Equipo {i}' for i in range(1, 13)]
    fig = px.bar(x=equipos, y=productividades, labels={'x': 'Equipo', 'y': 'Predicción de Productividad'},
                 title="Predicción de Productividad por Equipo")
    fig.update_layout(yaxis=dict(range=[0, 1]))
    return fig,summary_text


if __name__ == '__main__':
    app.run_server( debug=True)

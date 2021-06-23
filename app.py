import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.A import A
from dash_html_components.Img import Img
from dash_html_components.Li import Li
from dash_html_components.Ul import Ul
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import graph as gp



css = [dbc.themes.BOOTSTRAP, 'static/styles.css']

app = dash.Dash(__name__, external_stylesheets=css)

df = gp.initalize()

fig = px.scatter(df, x='date', y='current', custom_data=['net'])



navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.NavItem(dbc.NavLink("Debits", href="/debit")),
        dbc.NavItem(dbc.NavLink("Credits", href="/credit")),
        dbc.NavItem(dbc.NavLink("Net Balance", href="/net")),
    ],
    color="#17a2b8",
    dark=True,
)

app.layout = html.Div(
  className='grid-row-container',
  children=[
    html.Div(
      className='grid-row-child',
      children=[
        html.Nav(
          className='navbar navbar-expand-sm navbar-light bg-light',
          children=[
            html.A(
              className='navbar-brand',
              href='/',
              children='Commerce GUI'
            ),              
            html.Div(
              className='collapse navbar-collapse',
              children=[
                html.Ul(
                  className='navbar-nav',
                  children=[
                    html.Li( 
                      className='nav-item',
                      children=[
                        html.A(
                          className='nav-link',
                          href='/',
                          children='Home'
                        )
                      ]
                    ),
                    html.Li( 
                      className='nav-item',
                      children=[
                        html.A(
                          className='nav-link',
                          href='/debit',
                          children='Debits'
                        )
                      ]
                    ),
                    html.Li( 
                      className='nav-item',
                      children=[
                        html.A(
                          className='nav-link',
                          href='/credit',
                          children='Credits'
                        )
                      ]
                    ),
                    html.Li( 
                      className='nav-item',
                      children=[
                        html.A(
                          className='nav-link',
                          href='/net',
                          children='Net Balance'
                        )
                      ]
                    ),
                  ]
                )
              ]
            ),
            html.Div(
              className='collapse navbar-collapse justify-content-end',
              children=[
                html.Ul(
                  className='navbar-nav',
                  children=[ 
                    html.Li(
                      className='nav-item',
                      children=[ 
                        html.A(
                          className='nav-link',
                          href='https://github.com/mitchhit234/commerceGUI',
                          children=[ 
                            html.Img(
                              src='static/github.png',
                              width=40,
                              height=40
                            )
                          ]
                        )
                      ]
                    )
                  ]
                )
              ]
            )
          ]
        )
      ]
    ),
    html.Div(
      className='grid-row-child',
      children=[
        html.Div(
          className='grid-col-container',
          children=[
            html.Div(
              className='grid-col-child',
              children=dcc.Graph(
                id='main',
                figure=fig,
                style=dict(width='100%',height='100%'),
                responsive=True    
              )
            ),
            html.Div(
              className='grid-col-child',
              children='Grid column 2'
            )
          ]
        )
      ]
    )
  ]
)










# html.Div([
#   dcc.Graph(
#     id='main',
#     figure=fig
#   )])


if __name__ == '__main__':
  app.run_server(debug=True)
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash_table.Format import Format, Group, Scheme, Symbol
import graph as gp



def render_template(fig,df):
  layout = html.Div([ 
    dcc.Location(id='url', refresh=False),
    html.Div(
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
                            dcc.Link(
                              'Home',
                              className='nav-link',
                              href='/'
                            )
                          ]
                        ),
                        html.Li( 
                          className='nav-item',
                          children=[
                            dcc.Link(
                              'Debits',
                              className='nav-link',
                              href='debit'
                            )
                          ]
                        ),
                        html.Li( 
                          className='nav-item',
                          children=[
                            dcc.Link(
                              'Credits',
                              className='nav-link',
                              href='credit'
                            )
                          ]
                        ),
                        html.Li( 
                          className='nav-item',
                          children=[
                            dcc.Link(
                              'Net Balance',
                              className='nav-link',
                              href='net'
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
                  className='grid-col-child graph',
                  children=dcc.Graph(
                    id='figure-content',
                    figure=fig,
                    style=dict(width='95%',height='95%'),
                    responsive=True    
                  )
                ),
                html.Div(
                  className='grid-col-child dash-table',
                  children=[
                    'Transaction Table',
                    dash_table.DataTable(
                      id='table-sorting',
                      columns=[{"name": i, "id": i} for i in df.columns],
                      data=df.to_dict('records'),
                      fixed_rows={'headers': True},
                      style_cell={
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'maxWidth': 500,
                        'textAlign': 'left'
                      },
                      style_cell_conditional=[
                        {
                          'if': {'column_id': 'NET'},
                          'textAlign': 'right'
                        }
                      ],
                      sort_action='custom',
                      sort_mode='single',
                      sort_by=[]
                    )
                  ]
                )
              ]
            )
          ]
        )
      ]
    )
  ])

  return layout
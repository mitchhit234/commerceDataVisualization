#Layout for the dash application
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from pathlib import Path
import graph as gp

ABSOLUTE = str(Path(__file__).parents[1])

#Easier to read template avaliable in static folder
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
                  children=[
                    html.Img(
                      src="assets/logo.png",
                    )
                  ]
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
                                  src="assets/github.png",
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
                    'ALL DATA',
                    dash_table.DataTable(
                      id='table-sorting',
                      columns=[{"name": i, "id": i} for i in df.columns],
                      data=gp.format_dict_for_table(df),
                      fixed_rows={'headers': True},
                      style_cell={
                        'textOverflow': 'ellipsis',
                        'maxWidth': 300,
                        'textAlign': 'left'
                      },
                      style_cell_conditional=[
                        {
                          'if': {'column_id': 'BALANCE'},
                          'textAlign': 'right',
                          'width': 100
                        },
                        {
                          'if': {'column_id': 'NET'},
                          'textAlign': 'right',
                          'width': 100
                        },
                        {
                          'if': {'column_id': 'CREDIT'},
                          'textAlign': 'right',
                          'width': 100
                        },
                        {
                          'if': {'column_id': 'DEBIT'},
                          'textAlign': 'right',
                          'width': 100
                        },
                      ],
                      sort_action='custom',
                      sort_mode='single',
                      sort_by=[],
                      #Prevents errors when data is small enough to actualy shorthen table size
                      #dash does not handle this well, starts infinite looping
                      style_table={
                          'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                          'minWidth': '600px', 'width': '600px', 'maxWidth': '600px'
                      }
                    ),
                    html.Div(
                      id='hover-table-container',
                      style = {'margin-top': '50px'},
                      children=[
                        "SELECT A DATA POINT",
                        dash_table.DataTable(
                          id = 'hover-table',
                          fixed_rows={'headers': True},
                          style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                          },
                          style_cell={
                            'textAlign': 'left'
                          },
                          style_cell_conditional=[
                            {
                              'if': {'column_id': 'DATE'},
                              'width': 111
                            },
                            {
                              'if': {'column_id': 'NET'},
                              'width': 100,
                              'textAlign': 'right'
                            },
                            {
                              'if': {'column_id': 'VALUE'},
                              'width': 70,
                              'textAlign': 'right'
                            },
                            {
                              'if': {'column_id': 'CREDIT'},
                              'width': 100,
                              'textAlign': 'right'
                            },
                            {
                              'if': {'column_id': 'DEBIT'},
                              'width': 100,
                              'textAlign': 'right'
                            },
                            {
                              'if': {'column_id': 'DESCRIPTION'},
                              'width': 300
                            },
                            {
                              'if': {'column_id': 'BALANCE'},
                              'width': 93,
                              'textAlign': 'right'
                            },
                          ],
                          columns=[{"name": i, "id": i} for i in df.columns],
                          data=[dict(DATE='',DESCRIPTION='',BALANCE='')],
                          style_table={
                          'minHeight': '0px', 'height': '220px', 'maxHeight': '220px',
                          'minWidth': '600px', 'width': '600px', 'maxWidth': '600px'
                          }
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
  ])

  return layout
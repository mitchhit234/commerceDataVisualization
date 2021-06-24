import dash_core_components as dcc
import dash_html_components as html
from numpy.core.getlimits import _discovered_machar

def render_template(fig):
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
                  className='grid-col-child',
                  children=dcc.Graph(
                    id='figure-content',
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
  ])

  return layout
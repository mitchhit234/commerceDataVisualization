import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import graph as gp
import template as t



css = [dbc.themes.BOOTSTRAP, 'static/styles.css']

app = dash.Dash(__name__, external_stylesheets=css)

df = gp.initalize()
df2 = gp.basic_df()


#Inital page
fig = gp.balance_plot(df)
app.layout = t.render_template(fig,df2)

@app.callback(Output('figure-content', 'figure'),
  [Input('url', 'pathname')]
)
def toggle_page(pathname):
  #Remove '/' from tabs other than home
  #for function input
  if len(pathname) > 1:
    pathname = pathname[1:]

  #Three valid tabs
  if pathname == 'debit' or pathname == 'credit' or pathname == 'net':
    fig = gp.specalized_plot(df,pathname)
  #Home page case or case when invalid url is entered
  else:
    fig = gp.balance_plot(df)

  return fig
  


# html.Div([
#   dcc.Graph(
#     id='main',
#     figure=fig
#   )])


if __name__ == '__main__':
  app.run_server(debug=True)
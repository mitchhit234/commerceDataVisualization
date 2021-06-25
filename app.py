import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import graph as gp
import template as t
import pandas as pd



css = [dbc.themes.BOOTSTRAP, 'static/styles.css']

app = dash.Dash(__name__, external_stylesheets=css)

#Base df with all the DB columns + net value
df = gp.initalize()

#We use different data frames for the different plots,
#for example we have a current column for the plot,
#and we delete columns from the table df and alter description
plot_df = gp.main_plot_df(df.copy())
table_df = gp.table_df(df.copy(),['num','credit','debit'])


#Inital page
fig = gp.balance_plot(plot_df)
app.layout = t.render_template(fig,table_df)


@app.callback(
  Output('table-sorting','data'),
  [Input('table-sorting', 'sort_by')]
)
def update_table(sort_by):
  dff = table_df.copy()
  if len(sort_by):
    dff = dff.sort_values(
      sort_by[0]['column_id'],
      ascending=sort_by[0]['direction'] == 'asc',
      inplace=False
    )

  return gp.format_dict_for_table(dff)



@app.callback(
  Output('figure-content', 'figure'),
  [Input('url', 'pathname')]
)
def toggle_page(pathname):
  #Remove '/' from tabs other than home
  #for function input
  if len(pathname) > 1:
    pathname = pathname[1:]

  #Three valid tabs
  if pathname == 'debit' or pathname == 'credit' or pathname == 'net':
    fig = gp.specalized_plot(plot_df,pathname)
  #Home page case or case when invalid url is entered
  else:
    fig = gp.balance_plot(plot_df)

  return fig



if __name__ == '__main__':
  app.run_server(debug=True)
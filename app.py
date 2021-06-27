import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import graph as gp
import template as t
import pandas as pd

global_pathname, global_sortby = '', []

css = [dbc.themes.BOOTSTRAP, 'static/styles.css']

app = dash.Dash(__name__, external_stylesheets=css)

#Base df with all the DB columns + net value
df = gp.initalize()
pre_change = df.copy()
df['date'] = gp.adjust_dates(df)

#We use different data frames for the different plots,
#for example we have a balance column for the plot,
#and we delete columns from the table df and alter description
#plot_df = gp.main_plot_df(df.copy())

table_df = gp.table_df(pre_change.copy(),['num','credit','debit','net'])

#Inital page
fig = gp.balance_plot(df)
app.layout = t.render_template(fig,table_df)


# @app.callback(
#   Output('table-sorting','data'),
#   [Input('table-sorting', 'sort_by'),
#   Input('url', 'pathname')], prevent_initial_call=True
# )
# def update_table(sort_by,pathname):
#   dff = gp.table_df(pre_change.copy(),['num','credit','debit','net'])
#   dff = gp.grab_base_and_col(pre_change.copy(),pathname)
#   if len(sort_by):
#     dff = dff.sort_values(
#       sort_by[0]['column_id'],
#       ascending=sort_by[0]['direction'] == 'asc',
#       inplace=False
#     )

#   return gp.format_dict_for_table(dff)



# @app.callback(
#   Output('figure-content', 'figure'),
#   [Input('url', 'pathname')], prevent_initial_call=True
# )
# def toggle_page(pathname):
#   #Remove '/' from tabs other than home
#   #for function input
#   if len(pathname) > 1:
#     pathname = pathname[1:]

#   #Three valid tabs
#   if pathname == 'debit' or pathname == 'credit' or pathname == 'net':
#     fig = gp.specalized_plot(df,pathname)
#   #Home page case or case when invalid url is entered
#   else:
#     fig = gp.balance_plot(df)

#   return fig




@app.callback(
  Output('figure-content', 'figure'),
  Output('table-sorting', 'columns'),
  Output('table-sorting','data'),
  [Input('url', 'pathname'),
  Input('table-sorting', 'sort_by')], prevent_initial_call=True
)
def update_page(pathname,sort_by):

  ctx = dash.callback_context

  fig = dash.no_update
  cols = dash.no_update

  #Remove '/' from tabs other than home
  #for function input
  if len(pathname) > 1:
    pathname = pathname[1:]


  #url was changed
  if ctx.triggered[0]['prop_id'] == 'url.pathname':
    fig = gp.specalized_plot(df,pathname)

    dff = gp.table_df(pre_change.copy(),[])
    dff = gp.grab_base_and_col(dff,pathname.upper())

    cols = [{"name": i, "id": i} for i in dff.columns]

  #table sort was changed
  else:

    if len(sort_by):
      col = sort_by[0]['column_id']

      dff = gp.table_df(pre_change.copy(),[])
      dff = gp.grab_base_and_col(dff,pathname.upper())

      if col in dff:    
        dff = dff.sort_values(
          col,
          ascending=sort_by[0]['direction'] == 'asc',
          inplace=False
        )
    else:
      dff = gp.table_df(pre_change.copy(),[])
      dff = gp.grab_base_and_col(dff,pathname.upper())

    cols = [{"name": i, "id": i} for i in dff.columns]


  table = gp.format_dict_for_table(dff)

  return fig, cols, table









# @app.callback(
#   Output('table-sorting','data'),
#   [Input('table-sorting', 'sort_by')], prevent_initial_call=True
# )
# def sorting_table(sort_by):

#   col = sort_by[0]['column_id']

#   dff = gp.table_df(pre_change.copy(),[])
#   dff = gp.grab_base_and_col(dff,col)


#   if len(sort_by):
#     if sort_by[0]['column_id'] in dff:
#       dff = dff.sort_values(
#         sort_by[0]['column_id'],
#         ascending=sort_by[0]['direction'] == 'asc',
#         inplace=False
#       )

#   return gp.format_dict_for_table(dff)

  




# @app.callback(
#   Output('figure-content', 'figure'),
#   Output('table-sorting','data'),
#   Output('table-sorting', 'columns'),
#   [Input('url', 'pathname')], prevent_initial_call=True
# )
# def update_pg(pathname):

#   ctx = dash.callback_context

#   #Remove '/' from tabs other than home
#   #for function input
#   if len(pathname) > 1:
#     pathname = pathname[1:]

#   fig = gp.specalized_plot(df,pathname)
  
#   dff = gp.table_df(pre_change.copy(),[])
#   dff = gp.grab_base_and_col(dff,pathname.upper())

#   cols = [{"name": i, "id": i} for i in dff.columns]

#   return fig, gp.format_dict_for_table(dff), cols







if __name__ == '__main__':
  app.run_server(debug=True)
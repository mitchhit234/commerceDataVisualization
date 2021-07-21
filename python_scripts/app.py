# Dash application file
# Handles app template loading and redirects
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import graph as gp
import template as t
import db_update as update
import pandas as pd
from datetime import date

global_pathname, global_sortby = '', []
css = [dbc.themes.BOOTSTRAP, 'assets/tyles.css']
app = dash.Dash(__name__, external_stylesheets=css)

@app.callback(
  Output('figure-content', 'figure'),
  Output('table-sorting', 'columns'),
  Output('table-sorting','data'),
  [Input('url', 'pathname'),
  Input('table-sorting', 'sort_by')], prevent_initial_call=True
)
def update_page(pathname,sort_by):

  ctx2 = dash.callback_context

  fig = dash.no_update
  cols = dash.no_update
  table = dash.no_update

  #Remove '/' from tabs other than home
  #for function input
  if len(pathname) > 1:
    pathname = pathname[1:]


  #url was changed
  if ctx2.triggered[0]['prop_id'] == 'url.pathname':
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


@app.callback(
  Output('hover-table', 'data'),
  Output('hover-table', 'columns'),
  [Input('figure-content', 'clickData'),
  Input('url', 'pathname')], prevent_initial_call=True
)
def update_hover(clickData,pathname):
  if clickData == None or dash.callback_context.triggered[0]['prop_id'] == 'url.pathname':  
    return None, []


  if pathname != "/":
    dt = clickData['points'][0]['x']
    to_remov = [x for x in toggle_cols if x != pathname[1:]]
    temp = gp.table_df(pre_change.copy(),to_remov)
    temp = temp[temp.DATE.str.contains(dt[:7])]
    ret = temp[temp[pathname[1:].upper()] != 0]
    ret = pd.DataFrame(gp.format_dict_for_table(ret))
  else:
    data = clickData['points'][0]
    wanted_values = ['x', 'y', 'customdata']
    d = {key: data[key] for key in wanted_values}
    d['x'] = date(year=int(d['x'][:4]), month=int(d['x'][5:7]), day=int(d['x'][8:10])).strftime('%b %d %Y')
    d['y'] = round(d['y'],2)
    ret = pd.DataFrame(data=d, index=[0])
    ret = ret.rename(columns={"x": "DATE", "y": "BALANCE", "customdata": "DESCRIPTION"})
    ret = ret[['DATE', 'DESCRIPTION', 'BALANCE']]
  return ret.to_dict('records'), [{"name": i, "id": i} for i in ret.columns]





if __name__ == '__main__':
  #updates the database from commerce alert emails
  #searches emails as deep as input
  #(may add deletion of emails later, don't want to start
  #out with deletion of emails)
  #update.update(20)

  #Base df with all the DB columns + net value
  df = gp.initalize()
  pre_change = df.copy()
  df['date'] = gp.adjust_dates(df)

  #We use different data frames for the different plots,
  #for example we have a balance column for the plot,
  #and we delete columns from the table df and alter description
  #plot_df = gp.main_plot_df(df.copy())

  toggle_cols = ['num', 'credit', 'debit', 'net', 'balance']
  to_remove = [x for x in toggle_cols if x != 'balance']

  table_df = gp.table_df(pre_change.copy(),to_remove)

  #Inital page
  fig = gp.balance_plot(df)
  app.layout = t.render_template(fig,table_df)

  app.run_server()

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

#load stylesheets
global_pathname, global_sortby = '', []
css = [dbc.themes.BOOTSTRAP, 'assets/styles.css']
app = dash.Dash(__name__, external_stylesheets=css)

#Handles interaction in regards to table sorting
#and page switching
@app.callback(
  Output('figure-content', 'figure'),
  Output('table-sorting', 'columns'),
  Output('table-sorting','data'),
  [Input('url', 'pathname'),
  Input('table-sorting', 'sort_by')], prevent_initial_call=True
)
def update_page(pathname,sort_by):
  #dash callback object to be used to determine the
  #origin of the input
  ctx2 = dash.callback_context

  #Default to no update
  fig = dash.no_update
  cols = dash.no_update
  table = dash.no_update

  #Remove '/' from tabs other than home
  #for function input
  if len(pathname) > 1:
    pathname = pathname[1:]


  #url was changed, generate the new figure and tables
  if ctx2.triggered[0]['prop_id'] == 'url.pathname':
    fig = gp.specalized_plot(df,pathname)

    dff = gp.table_df(pre_change.copy(),[])
    dff = gp.grab_base_and_col(dff,pathname.upper())

    cols = [{"name": i, "id": i} for i in dff.columns]

  #table sort was changed
  else:
    #sort by value is sort was specified
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
      #change to default sort if sorting was disabled
      dff = gp.table_df(pre_change.copy(),[])
      dff = gp.grab_base_and_col(dff,pathname.upper())

    cols = [{"name": i, "id": i} for i in dff.columns]

  #render table from dataframe, produce a dict for dash to read
  table = gp.format_dict_for_table(dff)

  return fig, cols, table


#Handles interaction in regards to hover and click events on figures
@app.callback(
  Output('hover-table', 'data'),
  Output('hover-table', 'columns'),
  [Input('figure-content', 'clickData'),
  Input('url', 'pathname')], prevent_initial_call=True
)
def update_hover(clickData,pathname):

  #Usual initial load state, make sure interactive table starts out with nothing
  if clickData == None or dash.callback_context.triggered[0]['prop_id'] == 'url.pathname':  
    return None, []

  #Interactive tables are rendered different between the home page and other pages
  if pathname != "/":
    #Find the point that was clicked
    dt = clickData['points'][0]['x']
    #Remove data points that aren't in the specified page
    to_remov = [x for x in toggle_cols if x != pathname[1:]]
    temp = gp.table_df(pre_change.copy(),to_remov)
    #Get the right transactions by date
    temp = temp[temp.DATE.str.contains(dt[:7])]
    ret = temp[temp[pathname[1:].upper()] != 0]
    #Generate the dict that will be the new interactive table output
    ret = pd.DataFrame(gp.format_dict_for_table(ret))
  else:
    #Find the point that was clicked
    data = clickData['points'][0]
    wanted_values = ['x', 'y', 'customdata']
    d = {key: data[key] for key in wanted_values}
    #Format the raw data for table format
    d['x'] = date(year=int(d['x'][:4]), month=int(d['x'][5:7]), day=int(d['x'][8:10])).strftime('%b %d %Y')
    d['y'] = round(d['y'],2)
    ret = pd.DataFrame(data=d, index=[0])
    #Set the column names to match the table column names
    ret = ret.rename(columns={"x": "DATE", "y": "BALANCE", "customdata": "DESCRIPTION"})
    ret = ret[['DATE', 'DESCRIPTION', 'BALANCE']]
  return ret.to_dict('records'), [{"name": i, "id": i} for i in ret.columns]




if __name__ == '__main__':
  #updates the database from commerce alert emails
  #searches emails as deep as input
  #(may add deletion of emails later, don't want to start
  #out with deletion of emails)
  update.update(40)

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

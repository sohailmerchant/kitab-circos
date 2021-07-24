# -*- coding: utf-8 -

import pandas as pd
import dash
import dash_bio as dashbio
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import os
from matplotlib import cm
from matplotlib.colors import rgb2hex
import requests



app = dash.Dash(__name__)

# Functions for building necessary datasets on the fly (set up for aggregate fields)

def mk_tracks (df, color):
    aligns = df[["id1", "id2", "bw1", "ew1", "bw2", "ew2"]].values.tolist()
    tracks = []


    for row in aligns:
          source_id = row[0]
          target_id = row[1]                
          source_start = row[2]
          source_end = row[3]
          target_start = row[4] 
          target_end = row[5]
          color = color
          tracks.append({"color": color, "source": {"id": source_id, "start": source_start, "end": source_end}, "target": {"id": target_id, "start": target_start, "end": target_end}})
    return tracks


def mk_histo (df, kind='w_match'):
    if kind == 'w_match':
        aligns = df[["id2", "bw2", "ew2", "w_match"]]
        aligns = aligns.rename(columns = {"id2" : "block_id", "bw2": "start", "ew2": "end", "w_match" : "value"})
        aligns = aligns.to_dict("records")
    if kind == 'percentage':
        aligns = aligns = df[["id2", "bw2", "ew2", "matches_percent"]]
        aligns = aligns.rename(columns = {"id2" : "block_id", "bw2": "start", "ew2": "end", "matches_percent" : "value"})
        aligns = aligns.to_dict("records")
    return aligns

# Get data locs - based on the script path

script_loc = os.path.dirname(__file__)
initial_data_path =  "./data/initial/"
tracks_loc = "./data/tracks/"
histo_loc = "./data/histo/"
cyto_loc = "./data/cyto/"
instruct_path = "./data/Use_instructions.md"

serve_url = "http://dev.kitab-project.org/aggregated01022021/"

# Load in necessary files from data folder
# Load in instructions

with open(instruct_path) as f:
    instructions = f.read()
    f.close()

# Load in list of texts for main dropdown and format as dictionary 

primaries = pd.read_csv(initial_data_path + "primaries.csv")
drop_list = primaries[["label", "value"]].to_dict("records")

# Load in a colour palette for layouts

palette = cm.get_cmap("tab20c")




# Layout of the app using css.Bootstrap (necessary in assets)

app.layout = html.Div([
        dcc.Store(id='align-store'),
        dcc.Store(id= 'select-store'),
        html.Div([
            html.Div([html.Img(src = app.get_asset_url('logo-small-2.png'), height = '80 px')], className = 'col-md-1'),
            html.Div([html.H1(children='Circos Viz - Prototype: A visualisation for viewing multiple books', style = {'textAlign' : 'center'})], className = 'col-md-11')], 
                     className = 'row'),
        html.Div(html.Br(), className = 'row', style = {'background-color' : '#8ba9cc'}),
        
            
        
        
        
        # First row of selectors - 4 columns
            html.Div([
                html.Div([html.H4('Select a book 1 to get a list of related texts, and sort according to death date or text reuse instances.')],
                           className = 'col-md-7', style = {'vertical-align':'text-top', 'textAlign' : 'center'}),
                    
                     html.Div(["Sort secondary booklist by:"], className = 'col-md-2', style = {'textAlign' : 'right'}),
                     html.Div([dcc.Dropdown(id = 'sort-options', options = [{"label": "reuse instances", "value" : "instances"}, {"label" : "Author death date", "value" : "d_date"}], value= "instances")],
                          className = 'col-md-3')],
                 className = 'row', style = {'background-color' : '#8ba9cc'}),
        
        # Second row of selectors - 4 columns
        html.Div([html.Div(['Select a book 1:'], 
                           className = 'col-md-1'),
            html.Div([dcc.Loading(dcc.Dropdown(id='demo-dropdown', options= [], value= []))], className = 'col-md-5'),                 
                  html.Div(["Books related to book 1:"], 
                              className = 'col-md-1'),
                     html.Div([dcc.Loading(dcc.Dropdown(id = 'book-checklist', options = [], value= []))], 
                          className = 'col-md-5')],
                 className = 'row', style = {'background-color' : '#8ba9cc'}),
  

        
        
 
        
        # Row for the date filters + explainer
        html.Div([
        html.Div(children = "Filter selectors by author death date", className = 'col-md-1'),
        html.Div([dcc.RangeSlider(id='b1-date-select', 
                                  min=0, 
                                  max=1450, 
                                  step = 1, 
                                  value = [0, 1000], 
                                  marks={0: {'label' : '0 AH'},
                                         1540: {'label' : '1450 AH'}},
                                  tooltip = {'always_visible' : True , 'placement' : 'bottom'})],
                 className = 'col-md-5'),
        html.Div([],
                 className = 'col-md-1'),
        html.Div([dcc.RangeSlider(id='b2-date-select', 
                                  min=0, 
                                  max=1450, 
                                  step = 1, 
                                  value = [0, 1000], 
                                  marks={0: {'label' : '0 AH'},
                                         1540: {'label' : '1450 AH'}},
                                  tooltip = {'always_visible' : True , 'placement' : 'bottom'})], className = 'col-md-5')
        
        # End of row for date filters
        ],
        className = 'row', style = {'background-color' : '#dcdcdc'}),
        
        # Blank row for spacing
        
        html.Div([html.Br()], className = 'row'),
        # Row to hold Circos and options/reading tabs
        
        html.Div([
            
        # Box for Circos  
            html.Div([dcc.Loading(dashbio.Circos(
                id='my-dashbio-circos',
                layout= [],
                enableDownloadSVG = True,
                selectEvent={"1": "hover", "0": "click", "2": "both"},
                size = 1200,
                tracks=[{
                    'type': 'CHORDS',
                    'data': [], 
                    'opacity' : 1,
                    'config': {
                        'tooltipContent': {
                            'source': 'source',
                            'sourceID': 'id',
                            'target': 'target',
                            'targetID': 'id',
                            'targetEnd': 'end'
                            }
                        },
            
            },
                {'type':'HISTOGRAM',
                 'data' : []}
                    ],
            config={
                'innerRadius': 250,
                'outerRadius': 350
                
                },
                enableZoomPan = True))],
                     
                     className = 'col-md-8'),
        
        # Tabs for options
            html.Div([
                dcc.Tabs(id='viewing-options',
                value = 'options',
                className = 'row',
                children = [
                    dcc.Tab(label='Circos Options',
                            value = 'options',
                            className='btn btn-light',
                            selected_className = 'btn btn-dark',
                            children = [html.Div([html.Br()], className='row'), 
                                        "Choose a main text for comparison:",
                                dcc.Dropdown(id = 'prim-text', options = [], value = [], clearable = False),
                                daq.BooleanSwitch(id = 'all-check', label="Show Reuse for all texts", on=False),
                                "Current text selection:",
                                dcc.Dropdown(id = 'book-checklist-all', options=drop_list, value=[], multi=True),
                                html.Div([html.Br()], className='row'),
                                html.Div("Add histograms to show text reuse statistics for the main text:"),
                                html.Div([dcc.RadioItems(id = 'histo-choose', options=[{'label': 'Show text reuse percentages', 'value': 'percentage'},
                                                       {'label': 'Show text reuse word counts      ', 'value': 'w_match'},
                                                       {'label': 'Show Neither', 'value' : 'neither'}],
                                                       value = 'neither')], className = 'col-md-7' ),
                                html.Div([html.Br(), html.Br()], className='row'),
                                 html.Button('Regenerate Circos Graph', id='gen_button', n_clicks=0, className = 'btn btn-light'),
                                 html.Div([html.Br(), html.Br()], className='row')
                                 ]),
                    dcc.Tab(label='Alignment data',
                            value = 'data',
                            className='btn btn-light',
                            selected_className = 'btn btn-dark',
                            children = [html.Div(id='circos-output'),
                                        html.Br(),
                                        html.Div(id='feedback', children = [], className= 'col-md-11', style = {'background-color' : '#8ba9cc'})]),
                    dcc.Tab(label='How to use',
                            value = 'how_to',
                            className = 'btn btn-light',
                            selected_className = 'btn btn-dark',
                            children = [html.Div([dcc.Markdown(instructions)], className= "row", style = {'maxHeight' : '500px', 'overflow' : 'scroll', 'paddingLeft' : '20px', 'paddingRight' : '5px'})])]                         
                ),
                html.Div(id='tab-content', className='row')],
                className = 'col-md-4', style = {'background-color' : '#dcdcdc'})
            
            
            ], className ='row')
        
        # End of container
        ],
                 className = 'container-fluid')


# Callbacks commented out below to explain functions:
# Callback to filter the book 1 field
    
@app.callback(dash.dependencies.Output('demo-dropdown', 'options'),
              dash.dependencies.Input('b1-date-select', 'value'))

def filter_b1(date_range):
    filtered_primaries = primaries[primaries["Date"].between(date_range[0], date_range[1])]
    return filtered_primaries[["label", "value"]].to_dict("records")
            
# Callback to get alignment data from the chords, when clicked

@app.callback(
    dash.dependencies.Output('circos-output', 'children'),
    [dash.dependencies.Input('my-dashbio-circos', 'eventDatum'),     
     dash.dependencies.Input('align-store', 'data'),
     dash.dependencies.Input('select-store', 'data')]
)
def update_allign(value, data, data_select):
    if value is not None:
        b1 = value["source"]["id"]
        b2 = value["target"]["id"]
        b1_label = data_select[b1]
        b2_label = data_select[b2]
        address = b1 + "." + str(value["source"]["start"])        
        strings = data[b1 + "_" + b2][address]
        formatted = html.Div([html.Div([html.Div(b1_label, className = 'col-md-6'),
                        html.Div(b2_label, className = 'col-md-6')],
                 className = 'row', style = {'background-color' : '#8ba9cc'}),
                    html.Div([html.Div(strings[0], className = 'col-md-6', style = {'fontSize' : 16}),
                        html.Div(strings[1], className = 'col-md-6', style = {'fontSize' : 16})],
                 className = 'row', style = {'maxHeight' : '500px', 'overflow' : 'scroll'})])
        
        
        
        return formatted

    

    else:    
        return 'There is no data. Click on a data point to get alignment information.'
    
 # Callback to get the book 2 list and populate the dropdown
    
@app.callback(dash.dependencies.Output('book-checklist', 'options'),     
    [dash.dependencies.Input('demo-dropdown', 'value'), 
     dash.dependencies.Input('sort-options', 'value'),
     dash.dependencies.Input('b2-date-select', 'value')]
)
def update_dropdown(value, sort, date_range):

    if not value == [] and not value == None:
        secondary_select = pd.read_csv(initial_data_path + "secondaries/" + value + ".csv")
        if sort == "instances":
            secondary_select = secondary_select.sort_values(by = ["instances"], ascending = False)
        if sort == "d_date":
            secondary_select = secondary_select.sort_values(by = ["date_B2"])
    
        secondary_select = secondary_select[secondary_select["date_B2"].between(date_range[0], date_range[1])]
        secondary_select = secondary_select[["label", "value"]].to_dict("records")
    
    else:
        secondary_select = []

            
    return secondary_select

# Callback to populate the text selection based on the user's selected book 1 and other books they click on
    
@app.callback([dash.dependencies.Output('book-checklist-all', 'value'),
               dash.dependencies.Output('book-checklist', 'value')],
              [dash.dependencies.Input('demo-dropdown', 'value'),
               dash.dependencies.Input('book-checklist-all', 'value'),
     dash.dependencies.Input('book-checklist', 'value')])

def populate_select(prim, exist, new):
    
    if not prim == [] and prim != None and prim not in exist:
        exist.append(prim)
    if not new == [] and new not in exist:
        exist.append(new)
    

    
    return exist, []

# Callback to populate the dropdown that allows the user to choose a main text for their comparisons

@app.callback([dash.dependencies.Output('prim-text', 'options'),
               dash.dependencies.Output('prim-text', 'value')],
               dash.dependencies.Input('book-checklist-all', 'value'))

def populate_prim(values):
    
    if values == None or values == []:
        return [], []
    
    else:
        options = []
        for value in values:
            all_labels = primaries[["label", "value"]]
            option = all_labels[all_labels["value"] == value].values.tolist()
            try:
                options.append({"label" : option[0][0], "value" : option[0][1]})
            except: IndexError
    if len(options) == 0:
        return [], []
    else:
        return options, options[0]["value"]
    
   
    
            
# Callback that produces the Circos diagram (the layout and the tracks) based on the user's choices.

@app.callback([dash.dependencies.Output('my-dashbio-circos', 'layout'),
                dash.dependencies.Output('my-dashbio-circos', 'tracks'),
               dash.dependencies.Output('gen_button', 'n_clicks'),
               dash.dependencies.Output('feedback', 'children'),
                dash.dependencies.Output('align-store', 'data'), 
                dash.dependencies.Output('select-store', 'data')],
    [dash.dependencies.Input('prim-text', 'value'),     
      dash.dependencies.Input('book-checklist-all', 'value'),      
      dash.dependencies.Input('all-check', 'on'),
      dash.dependencies.Input('gen_button', 'n_clicks'),
      dash.dependencies.Input('feedback', 'children'),
      dash.dependencies.Input('histo-choose', 'value'),
      dash.dependencies.Input('align-store', 'data'),
      dash.dependencies.Input('select-store', 'data')],
    state = [dash.dependencies.State('my-dashbio-circos', 'layout'),
             dash.dependencies.State('my-dashbio-circos', 'tracks')])

def change_graph(primary, books, all_check, clicks, error, histo, store, select_store, current_layout, current_track):
   
    
   
    if clicks == 0:
        current_track[0].update(
                    data=current_track[0]["data"],
                    type='CHORDS',
                    config={
                        'tooltipContent': {
                            'source': 'source',
                            'sourceID': 'id',
                            'target': 'target',
                            'targetID': 'id',
                            'targetEnd': 'end'},
                        'color' : {'name': 'color'}
                        })
        return current_layout, current_track, 0, error, store, select_store
    
    if clicks > 1:
        current_track[0].update(
                    data=current_track[0]["data"],
                    type='CHORDS',
                    config={
                        'tooltipContent': {
                            'source': 'source',
                            'sourceID': 'id',
                            'target': 'target',
                            'targetID': 'id',
                            'targetEnd': 'end'},
                        'color' : {'name': 'color'}
                        })
        return current_layout, current_track, 0, error, store, select_store

        
    
    if clicks == 1:
        error = [html.Div(dcc.Markdown('**Issues with your selection:**'), className = 'row')]
        new_layout = []
        new_track = []
        new_histo = []
        store = {}
        select_store = {}
        if not books == [] and not books == None:      
            col_count = 0
            
            for book in books:
                    selected = primaries[primaries["value"] == book].values.tolist()
                    color = rgb2hex(palette(col_count))
                    if book == primary:
                        prim_color = color
                    col_count = col_count + 1
                    try:
                        new_layout.append({"len" : selected[0][2], "color" : color, "label" : selected[0][0], "id" : book})
                        select_store[book] = selected[0][0]
                        
                    except IndexError:
                        continue
            all_books_copy = books[:]            
            primary_loc = serve_url + primary + "/" + primary + "_"
            all_books_copy.remove(primary)
            ref_copy = all_books_copy[:]
            used_books = []
            for book in all_books_copy:
                url = primary_loc + book + ".csv"
                check = requests.get(url)
                if check.status_code == 200:
                    data = pd.read_csv(url, sep= "\t")
                    tracks = mk_tracks(data, prim_color)
                    new_track.extend(tracks)
                    
                    # Adding alignment series to datastore
                    to_store = data[["id1", "bw1", "s1", "s2"]]                    
                    to_store["address"] = to_store["id1"] + "." + to_store["bw1"].astype(str)

                    to_store = dict(zip(to_store['address'], zip(to_store['s1'], to_store['s2'])))
                    store[primary + "_" + book] = to_store
                   
                    
                        
                    
                    if histo == 'w_match':
                        new_histo.extend(mk_histo(data, 'w_match'))
                            
                    if histo == 'percentage':
                        new_histo.extend(mk_histo(data, 'percentage'))
                            
                
                            
                else:
                    error.append(html.Div([html.Br(), dcc.Markdown('**No passim files found for:** ' +  select_store[primary] + ' **and** ' + select_store[book])], className = 'row'))
                
                
                if all_check and len(books) > 2:
                    book_loc = serve_url + book + "/" + book + "_"
                    used_books.append(book)
                                     
                    for book2 in ref_copy:
                        if book2 not in used_books:
                            url = book_loc + book2 + ".csv"
                            check = requests.get(url)
                            if check.status_code == 200:
                                    data2 = pd.read_csv(url, sep= "\t")
                                    tracks = mk_tracks(data2, "rgb(219, 24, 122)")                                    
                                    new_track.extend(tracks)
                                    
                                    # Adding alignment series to datastore
                                    to_store2 = data2[["id1", "bw1", "s1", "s2"]]                    
                                    to_store2["address"] = to_store2["id1"] + "." + to_store2["bw1"].astype(str)

                                    to_store2 = dict(zip(to_store2['address'], zip(to_store2['s1'], to_store2['s2'])))
                                    store[book + "_" + book2] = to_store2
                                    
                                    
                                    
                            else:
                                  error.append(html.Div([html.Br(), dcc.Markdown('**No passim files found for:** ' +  select_store[book] + ' **and** ' + select_store[book2])], className = 'row'))
                        
                
                    
                current_track[0].update(
                    data=new_track,
                    type='CHORDS',
                    
                    config={
                        'tooltipContent': {
                            'source': 'source',
                            'sourceID': 'id',
                            'target': 'target',
                            'targetID': 'id',
                            'targetEnd': 'end'},
                        'color' : {'name': 'color'},
                        'opacity': 0.9
                        }
                    )
                
                if new_histo != []:
                    current_track[1].update(
                        data=new_histo,
                        type = 'HISTOGRAM')
                    
            

                
            
            return new_layout, current_track, 0, error, store, select_store
    
    

if __name__ == '__main__':
    app.run_server(debug=True)
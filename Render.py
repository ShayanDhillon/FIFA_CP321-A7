from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

Data = pd.DataFrame({
    "Year" : [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018, 2022],
    "Winner": ["URY", "ITA", "ITA", "URY", "DEU", "BRA", "BRA", "GBR", "BRA", "DEU", "ARG", "ITA", "ARG", "DEU", "BRA", "FRA", "BRA", "ITA", "ESP", "DEU", "FRA", "ARG"],
    "Second": ["ARG", "CZE", "HUN", "BRA", "HUN", "SWE", "CZE", "DEU", "ITA", "NLD", "NLD", "DEU", "DEU", "ARG", "ITA", "BRA", "DEU", "FRA", "NLD", "ARG", "CRO", "FRA"]
})
unique_countries = pd.concat([Data['Winner'], Data['Second']]).unique()
c_opts = [{'label': country, 'value': country} for country in sorted(unique_countries)]

app = Dash(__name__)
server = app.server

# Requires Dash 2.17.0 or later
app.layout = [
    html.H1(children='FIFA Soccer World Cup winners', style={'textAlign':'center'}),
    dcc.RadioItems(id='FIFA-rep',
                   options= ['View All Winners', 'Select A Country', 'Select A Year'],
                   value= 'View All Winners'),
    #dcc.Input(id="FIFA-input", type="text", placeholder="Enter a Country",  value="", style={'display': 'block','margin':'auto'}),
    dcc.Dropdown(id="FIFA-country",
                options=c_opts,
                placeholder="Select a Country...",
                value='ARG'
                ),
    dcc.Dropdown(id="FIFA-year",
                 options=[{'label': year, 'value': year} for year in Data["Year"]],
                 placeholder="Select a Year...",
                 value=1930, style={'display': 'block','margin':'auto'}),
    dcc.Graph(id="FIFA-graph")
]

#SHOWING CERTAIN FIELDS
@callback(
    [Output('FIFA-country', 'style'),
     Output('FIFA-year', 'style')],
    Input('FIFA-rep', 'value')
)
def toggle_inputs(selected_option):
    # Default styles (hidden)
    input_style = {'display': 'none'}
    year_style = {'display': 'none'}
    
    if selected_option == 'Select A Country':
        input_style = {'display': 'block','margin':'auto'}  
    elif selected_option == 'Select A Year':
        year_style = {'display': 'block','margin':'auto'}   
    
    return input_style, year_style


#SHOWING GRAPHS
@callback(
    Output('FIFA-graph', 'figure'),
    [Input('FIFA-rep', 'value'), Input('FIFA-country', 'value'), Input('FIFA-year', 'value')]
)
def update_graph(options, country, year):
    winners = Data["Winner"].value_counts().reset_index()
    winners.columns = ["Country", "Wins"]

    if(options == 'View All Winners'): 

        return display_winners(winners)
    
    elif(options == 'Select A Country'):

        if(country is None):
            return valid_error('Select a Country to see data!')
        

        return display_country_wins(winners, country)
    

    else:
        if(year is None):
            return valid_error('Select a year to see data!')

        return display_by_year(year)



def display_winners(winners):
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=winners['Country'],
        z=winners['Wins'],
        locationmode="ISO-3",
        colorscale="Sunsetdark",
        marker_line_color='green',  
        marker_line_width=1.35,
        colorbar_title="World Cup Wins"
    ))
    fig.update_layout(
        title="World Cup Wins by Country",
        geo=dict(showcoastlines=True, projection_type="natural earth")
    )
    return fig

def display_country_wins(winners, country):
    winning_years = Data[Data['Winner'] == country]
    win_count = len(winning_years)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=winning_years['Year'],
        y=[1]*win_count,  #  y-value for all markers
        mode='markers+text',
        marker=dict(
            size=16,
            color='gold',
            symbol='star',
            line=dict(width=1, color='darkgoldenrod')
        ),
        text=[f"WIN {year}" for year in winning_years['Year']],
        textposition="top center",
        hovertext=[f"Won a Championship in {year}" for year in winning_years['Year']],
        name="Wins"
    ))
    
    # win count annotation
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=1.1,
        text=f"{country} has won {win_count} World Cups",
        showarrow=False,
        font=dict(size=16, weight='bold')
    )
    
    fig.update_layout(
        title=f"{country}'s World Cup History",
        yaxis=dict(showticklabels=False, range=[0.9, 1.1]),
        xaxis=dict(title="Year"),
        showlegend=False,
        margin=dict(t=100)
    )
    
    return fig

def display_by_year(year):
    fig = go.Figure()

    #make custum data to plot on world map!
    Data_years = Data[Data['Year'] == year].iloc[0]
    first = Data_years['Winner']
    second = Data_years['Second']

    fig.add_trace(
        go.Choropleth(
            locations=[first,second],
            z=[1,0],
            locationmode="ISO-3",
            colorscale=[[0, 'silver'], [1, 'gold']],
            marker_line_color='green',  
            marker_line_width=1.35,
            hoverinfo="text",
            hovertext=[f"{first}: Winner in {year}", f"{second}: Runner-up in {year}"],
            showscale=False
            
        )
    )

    fig.update_layout(
        title=f"World Cup Winner & Runner-up in {year}",
        showlegend=False,
        margin=dict(t=100),
        geo=dict(showcoastlines=True, projection_type="natural earth")
    )

    fig.add_annotation(
        x=0.5,y=-0.1,
        xref="paper",
        yref="paper",
        text=f"<span style='color:gold'>■</span> Winner: {first}  |  " +
             f"<span style='color:silver'>■</span> Runner-up: {second}",
        showarrow=False,
        font=dict(size=16),
        align="center"
    )

    


    return fig




def valid_error(e="Please enter a valid value to view the chart!"):
    fig = go.Figure()
    fig.add_annotation(
        text=e,
        #center text
        xref="paper", yref="paper", 
        x=0.5,  
        font=dict(size=24, color="red"),
        showarrow=False
    )
    return fig
    
if __name__ == '__main__':
    app.run(debug=True)




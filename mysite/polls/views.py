from django.shortcuts import render
import folium
from folium.plugins import HeatMap
import pandas as pd
import pgeocode
from pretty_html_table import build_table
import mysql.connector

def fetchReviews(zip):
    db_connection = mysql.connector.connect(user="admin", password="yeet")
    db_cursor = db_connection.cursor()
    db_cursor.execute("USE cs179g;")

# Create your views here.
def zipToCoord(zip):
    nomi = pgeocode.Nominatim('us')
    query = nomi.query_postal_code(zip)
    data = [query["latitude"],query["longitude"]]
    return data

def topList(request):
    
    db_connection = mysql.connector.connect(user="admin", password="yeet")
    db_cursor = db_connection.cursor()
    db_cursor.execute("USE cs179g;")
    db_cursor.execute("SELECT * FROM BusinessSentiment ORDER BY rating DESC LIMIT 10;")
    #Get overall best restaruants from the database
    
    sample_list = [['Pizza Hut','4.7', 92507],
                    ['Papa John\'s','4.3', 84720],
                    ['Domino\'s','4.1', 80013]]


    #Get best restaurants in the Zip Code if one is entered
    params = request.POST
    zip = params.get("zip_code")
    if zip:
        db_cursor.reset()
        query1 = "SELECT * FROM BusinessSentiment WHERE postal_code = " + zip+ " ORDER BY rating DESC LIMIT 10;"
        db_cursor.execute(query1)
        sample_list = [['KFC','4.1', 91505],
                    ['Bea Bea\'s','4.0', 91505],
                    ['Domino\'s','3.9', 91505]]
    
    df = pd.DataFrame(db_cursor.fetchall(), columns = ['restaurant','zip_code','lat','long','rating'])
    df = df.rename(columns={'restaurant': 'Name',\
        'zip_code': 'Zip Code',\
        'lat': 'Latitude',\
        'long': 'Longitude',\
        'rating': 'Rating'})
    table = build_table(df, 'blue_light')
    return table

def worstList(request):
    #Get overall worst restaruants from the database
    db_connection = mysql.connector.connect(user="admin", password="yeet")
    db_cursor = db_connection.cursor()
    db_cursor.execute("USE cs179g;")
    db_cursor.execute("SELECT * FROM BusinessSentiment ORDER BY rating ASC LIMIT 10;")
    
    sample_list = [['Chuck E Cheese\'s','0.6', 92507],
                    ['Arby\'s','0.2', 92506],
                    ['Jack in the Box','0.4', 92504]]

    #Get worst restaurants in the Zip Code if one is entered
    params = request.POST
    zip = params.get("zip_code")
    if zip:
        db_cursor.reset()
        query1 = "SELECT * FROM BusinessSentiment WHERE postal_code = " + zip + " ORDER BY rating ASC LIMIT 10;"
        db_cursor.execute(query1)
        sample_list = [['Chili\'s','0.1', 91505],
                       ['Tony\'s Italian Deli','0.2', 91505],
                       ['Popeye\'s','0.6', 91505]]
    
    df = pd.DataFrame(db_cursor.fetchall(), columns = ['restaurant','zip_code','lat','long','rating'])
    df = df.rename(columns={'restaurant': 'Name',\
        'zip_code': 'Zip Code',\
        'lat': 'Latitude',\
        'long': 'Longitude',\
        'rating': 'Rating'})
    table = build_table(df, 'red_light')
    return table

def heatmap(request):
    # Default Map Coords for the center of the US
    map_coords = [37.0902, -95.7129]
    db_connection = mysql.connector.connect(user="admin", password="yeet")
    db_cursor = db_connection.cursor()
    db_cursor.execute("USE cs179g;")
    
    # Retreive the zip code if one is entered and update map to reflect
    params = request.POST

    zip = params.get("zip_code")
    if zip:
        map_coords = zipToCoord(zip)

    db_cursor.execute("SELECT * FROM BusinessSentiment ORDER BY rating DESC LIMIT 1000;")

    #Fetch coord data of all positive reviews of that ZIP Code

    positive_list = [[33.953350,-117.396156, 1, "Pizza Hut",4.7],
                    [37.953350,-120.396156, 1,'Pizza Hut',4.7],
                    [39.093150,-113.836156, 1,'Papa John\'s',4.3],
                    [40.953350,-109.396156, 1,'Domino\'s',4.1],
                    [34.19184, -118.38897, 1,'Pizza Hut',4.7],
                    [34.28184, -118.41897, 1,'Papa John\'s',4.3],
                    [34.18184, -118.44697, 1,'Domino\'s',4.1]]
                    
                    
    pos_df = pd.DataFrame(db_cursor.fetchall(), columns = ['restaurant','zip_code','lat','long','rating'])
    db_cursor.reset()
    db_cursor.execute("SELECT * FROM BusinessSentiment ORDER BY rating ASC LIMIT 1000;")
    #Fetch coord data of all negative reviews of that ZIP code
    negative_list = [[34.953350,-117.396156, 1, "Chuck E Cheese\'s", 0.6],
                     [34.18084, -118.30897,1 , "Chili\'s", 0.1],
                     [34.19184, -118.40897,1 , "Tony\'s Italian Deli", 0.2],
                     [34.1814, -118.30897,1 , "Popeye's", 0.6]]

    neg_df = pd.DataFrame(db_cursor.fetchall(), columns = ['restaurant','zip_code','lat','long','rating'])
    neg_df = neg_df[['lat','long','rating','restaurant','zip_code']]
    pos_df = pos_df[['lat','long','rating','restaurant','zip_code']]
    pos_df['lat'] =pos_df['lat'].astype(float)
    neg_df['lat'] =neg_df['lat'].astype(float)
    pos_df['long'] =pos_df['long'].astype(float)
    neg_df['long'] =neg_df['long'].astype(float)
    pos_df['rating'] =pos_df['rating'].astype(float)
    neg_df['rating'] =neg_df['rating'].astype(float)
    m = folium.Map(map_coords, zoom_start = (10 if zip else 4))
    pos_grp = folium.FeatureGroup(name='Postive Review Heat Map')
    neg_grp = folium.FeatureGroup(name='Negative Review Heat Map')
    #Create the Heat Maps of the reviews
    
    HeatMap(pos_df.iloc[: , :3], min_opacity=7,blur = 18).add_to(pos_grp)
    HeatMap(neg_df.iloc[: , :3], min_opacity=7,blur = 18, gradient={.4: 'purple', .65: 'red', 1: 'beige'}).add_to(neg_grp)
    
    

    # Add markers to top 10 restaruants and bottom 10
    for i in range(len(pos_df)):
        folium.Marker(
            location = [pos_df.iloc[i]['lat'], pos_df.iloc[i]['long']],
            popup = pos_df.iloc[i]['restaurant'] + " "+ str(pos_df.iloc[i]['rating']),
            icon=folium.Icon(color='green')
        ).add_to(pos_grp)

    for i in range(len(neg_df)):
        folium.Marker(
            location = [neg_df.iloc[i]['lat'], neg_df.iloc[i]['long']],
            popup = neg_df.iloc[i]['restaurant'] + " "+ str(neg_df.iloc[i]['rating']),
            icon=folium.Icon(color='red')
        ).add_to(neg_grp)

    pos_grp.add_to(m)
    neg_grp.add_to(m)

    folium.LayerControl().add_to(m)

    return m._repr_html_()

def index(request):

    context = {'my_map': heatmap(request),
            'top_list': topList(request),
            'worst_list': worstList(request)}
    return render(request, "index.html",context)
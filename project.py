import pandas as pd
import folium
from folium import plugins
import numpy as np
import geocoder
import cufflinks as cf
import plotly.io as pio
import eel 
import webbrowser
cf.go_offline()
cf.set_config_file(offline=False, world_readable=True)
hoteltags_geo=pd.read_pickle('./data/clean_hoteltag.pkl')
similarityDF=np.load('./data/tagcosine.npy')

def new_recommendations_tags(name,city, cosine_similarities):
    
    recommended_hotels = []
    
    #get input city index
    city_index= list(hoteltags_geo[hoteltags_geo.city==city].index)
    
    # gettin the index of the hotel that matches the name
    idx = hoteltags_geo[(hoteltags_geo.hotel_name == name)].index[0]
    
    # creating a Series with the similarity scores in descending order
    score_series = pd.Series(cosine_similarities[idx]).sort_values(ascending = False)

    # getting the indexes of  similar hotels
    top_10_indexes = list(score_series.index)
    
    # populating the list with the names of the matching hotels
    for i in range(len(top_10_indexes)):
        if top_10_indexes[i] not in city_index:
            pass
        else:
            recommended_hotels.append(hoteltags_geo[hoteltags_geo.index==top_10_indexes[i]]['hotel_name'].values[0])

    # populating a dictionary of size 10 containing hotel name and lat and longitude 
    h = hoteltags_geo[['hotel_name','lat_x','lng_x']].to_dict(orient='records')
    l = {k['hotel_name']: [k['lat_x'], k['lng_x']] for k in h}
    if {hotel: l[hotel] for hotel in recommended_hotels }=={}:
        print("There are no hotels of similar hotel")
    else:
        output= {hotel: l[hotel] for hotel in recommended_hotels[:10]}
        newoutput={i:output for i in range(1,len(output)+1)}
        return newoutput

def get_hotel_fn(mydict,city):
    loc2 = geocoder.osm(city)

    # map
    main_map = folium.Map(location=[loc2.lat, loc2.lng], zoom_start=13)
    folium.raster_layers.TileLayer('Open Street Map').add_to(main_map)

    # loop through dict
    for i in range (1,len(mydict)+1):
        folium.Marker(location=list(mydict[i].values())[i-1],tooltip=list(mydict[i].keys())[i-1]
                      ,popup=list(mydict[i].keys())[i-1],
                     icon=plugins.BeautifyIcon(number=i,
                                               icon='bus',
                                            border_color='blue',
                                            border_width=0.5,
                                            text_color='red',
                                            inner_icon_style='margin-top:0px;')).add_to(main_map)
     
    return main_map

# to populate and pin recommended list of hotels
@eel.expose
def prediction (hotel_name,city):
    map1=get_hotel_fn(new_recommendations_tags(hotel_name,city,similarityDF), city)
    # map1=get_hotel_fn(new_recommendations_tags('Hilton Diagonal Mar Barcelona','Vienna',similarityDF),'Vienna')
    map1.save('map.html')
    webbrowser.open_new_tab('map.html')
    # print ("hello world ")
# predict('Hilton Diagonal Mar Barcelona', 'Vienna')


eel.init("frontend")
eel.start("index.html")
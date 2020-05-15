#!/usr/bin/env python
# coding: utf-8

# # Capstone Project - The Battle of Neighbourhoods

# ## Business Problem section

# ### Background
# Hong Kong, one of the most popular and international metropolitans in Asia. With the long immigrant history, Hong Kong becomes a diverse cultural and ethnical city, where people could enjoy wide varieties of entertainment, access to delicious cuisine from all around the world.
# 
# According to the UN Human Development Index, Hong Kong is a highly developed territory with long life expectancies in the world. 
# Besides, Hong Kong is one of the most densely city in the world with over 7.4 million people of various nationalities in a 1,100 km^2 territory. 
# Watching movie is a popular leisure activity among the world and provide people the opportunity to access multicultural lifestyle and drive the society to change. 
# 
# However, according to the data from Wikipedia, Hong Kong currently only has 60 cinema centres, with providing 259 screens and around 40,000 seats in total. Comparing to the city population, this is a very minor number. As mentioned from a report written by “World Cities Culture Forum”, Hong Kong’ Number of cinema screens per 100,000 population is 2.8, which far lack behind others developed cities in Asia, such as Taipei with 7.9, Seoul with 5.8, Shenzhen with 4.9 and Singapore with 4.2. 
# 
# Based on the above founding, ABC corporation consider Hong Kong is a potential market and have room to launch the new cinema centre in Hong Kong. 
# As watching movie is a time spending leisure and will occupy the time during afternoon and at night, so the new cinema location should surround by the restaurants, shops, or shopping malls. Besides, as Hong Kong well developed a transportation network with public transport rates exceeding 90 percent, so the distance from public transportation to cinema is vital to drive the traffic from other districts.  And the new cinema location should within 5 minutes walking distance from public transport.
# 
# We select 5 potential location to build the new cinema centre, so the business problem for our project is “Which is the ideal location we should suggested to ABC corporation?”
# 
# 
# - Central - Infinitus Plaza Shopping Arcade
# - Kwun Tong - Yue Man Square
# - Tuen Mun - V City
# - Tsuen Wan - Nan Fung CCentre
# - Ssp - West Kowloon Centre
# - Hang Hau - East Point City 

# ### Data Requirement 
# 
# Hong Kong Cinema List https://hkmovie6.com/cinema
# - To obtain the current cinema details, including their names, location
# - Transformed the data with Pandas into Data frame for further analysis
# - Gathered the geographical coordinates of the cinema with Geopy
# 
# Foursquare API
# - To get the most common venues around the current cinema
# - To get the surround venues around the possible new cinema location 
# 
# Districts of Hong Kong  https://en.wikipedia.org/wiki/Districts_of_Hong_Kong
# - Observes the distribution on current cinema and screen per 100,000
# - Gathered the geographical coordinates of the districts with Geopy
# - Transformed the data with Pandas into Data frame for further analysis

# In[1]:


#Import required libraries

get_ipython().system('pip install folium')
get_ipython().system('pip install bs4')
get_ipython().system('pip install lxml')
get_ipython().system('pip install -U googlemaps')

import googlemaps #Google map api for geo location
import requests 
import urllib.request
from urllib.request import urlopen
import time
from bs4 import BeautifulSoup #Soup for scraping online date source 
import numpy as np 
import pandas as pd

import folium #for map creation

from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

print('Libraries imported.')


# ## Methodology 
# 
# 
# 
# 
# ### Data preparation and pre-processing
# - Scraping Hong Kong Cinema List from HKMovie6 website and Districts of Hong Kong from Wikipedia   
# - Using pandas to turns Table in Wikipedia to a DataFrame
# - Getting Coordinates of Cinema and Major Districts
# - get the coordinates of these 18 major districts using geocoder class of Geopy client

# In[2]:


#Retrieve the list of current Cinemas in Hong Kong
url = 'https://hkmovie6.com/cinema'
try:
    page = urllib.request.urlopen(url)
except:
    print("An error occured.")

soup = BeautifulSoup(page,'html.parser')
#print(soup.prettify())


# In[3]:


#Digest the Data from Soup to DataFrame

Name =[]
Address=[]

names = soup.find_all('div', class_ = 'cinemaName f row')
for name in names:
    temp = name.get_text()
    Name.append(temp)

locations = soup.find_all('div', class_= 'sub f ai-center')
for location in locations:
    temp = location.get_text()
    Address.append(temp)

import pandas as pd

Cinema = pd.DataFrame()
Cinema['Name'] = Name
Cinema['Address'] = Address
Cinema.columns = ['Cinema','Address']
Cinema.replace('\n', '', regex=True, inplace=True)
print('The number of cinemas in Hong Kong is', Cinema.shape[0])
Cinema.head()


# In[4]:


#Check if any missing value
Cinema.isna().sum()


# In[ ]:





# In[5]:


gmaps = googlemaps.Client(key = '#')


# In[6]:


#Revised the address to correct one
Cinema['Address'][42] = '香港柴灣柴灣道333號永利中心地下'
Cinema['Address'][46] = '旺角 亞皆老街8號朗豪坊'


# In[7]:


#Add columns to Cinema DataFrame for geo location info.
Cinema['Eng_Address'] = None
Cinema['Latitude'] = None
Cinema['Longitude'] = None
Cinema['District'] = None
Cinema['Region'] = None


# In[8]:


#Loading Geo location from Google Api

for i in range(len(Cinema)):
    geo_result = gmaps.geocode(Cinema['Address'][i])
    FAdd = geo_result[0]['formatted_address']
    lat = geo_result[0]['geometry']['location']['lat']
    lng = geo_result[0]['geometry']['location']['lng']
    name = geo_result[0]['address_components'][-3]['long_name']
    region = geo_result[0]['address_components'][-2]['long_name']
    Cinema.loc[i,'Eng_Address'] = FAdd
    Cinema.loc[i,'Latitude'] = lat
    Cinema.loc[i,'Longitude'] = lng
    Cinema.loc[i,'District'] = name
    Cinema.loc[i,'Region'] = region
    
Cinema


# In[9]:


#Revised the data
Cinema['District'][52] = 'Tuen Mun'
Cinema['Region'][52] = 'New Territories'
Cinema['District'][42] = 'Chai Wan'
Cinema['Region'][42] = 'Hong Kong Island'
Cinema['District'][46] = 'Mong Kok'
Cinema['Region'][46] = 'Kowloon'
Cinema['Cinema'][56] = 'L Cinema Shau Kei Wan'
Cinema.drop('Eng_Address',axis=1,inplace=True)
Cinema.Cinema = Cinema.Cinema.str.strip()
Cinema.head()


# In[10]:


#Save the File
Cinema.to_csv("Cinema_pre.csv",index=False)


# In[ ]:





# In[11]:


#Retrieve the District information of Hong Kong
url = 'https://en.wikipedia.org/wiki/Districts_of_Hong_Kong'
try:
    page = urllib.request.urlopen(url)
except:
    print("An error occured.")
    
soup = BeautifulSoup(page,'html.parser')
print('Page Scrapped.')


# In[12]:


#Collect data in process
right_table=soup.find('table', class_='wikitable sortable')

A=[]
B=[]
C=[]
D=[]
E=[]
F=[]

for row in right_table.findAll('tr'):
    cells=row.findAll('td')
    if len(cells)==6:
        A.append(cells[0].find(text=True))
        B.append(cells[1].find(text=True))
        C.append(cells[2].find(text=True))
        D.append(cells[3].find(text=True))
        E.append(cells[4].find(text=True))
        F.append(cells[5].find(text=True))
print('Data Collected.')            


# In[13]:


#Build DataFrame
df = pd.DataFrame()
df['District'] = A
df['Chinese'] = B
df['Population'] = C
df['Area(km²)'] = D
df['Density(/km²)'] = E
df['Region'] = F
df


# In[14]:


#Create the DateFrame for District's Geo location

import pandas as pd

location = {
'Central and Western': [22.28666,114.15497],
'Eastern': [22.28411,114.22414],
'Southern': [22.24725,114.15884],
'Wan Chai': [22.27968,114.17168],
'Sham Shui Po': [22.33074,114.1622],
'Kowloon City': [22.3282,114.19155],
'Kwun Tong': [22.31326,114.22581],
'Wong Tai Sin': [22.33353,114.19686],
'Yau Tsim Mong': [22.31236,114.17077],
'Islands': [22.26114,113.94608],
'Kwai Tsing': [22.34441,114.09898],
'North': [22.49471,114.13812],
'Sai Kung': [22.38143,114.27052],
'Sha Tin': [22.38715,114.19534],
'Tai Po': [22.45085,114.16422],
'Tsuen Wan': [22.36281,114.12907],
'Tuen Mun': [22.39163,113.977089],
'Yuen Long': [22.44559,114.02218]
}
locationdf = pd.DataFrame.from_dict(location).T
locationdf.reset_index(inplace=True)
locationdf.rename(columns={'index':'District', 0:'Latitude',1:'Longitude'},inplace=True)
locationdf


# In[15]:


District = df.join(locationdf.set_index('District'), on='District')
HKI = District[District['Region']=='Hong Kong Island']
NT = District[District['Region']=='New Territories']
KL = District[District['Region']=='Kowloon']


# In[16]:


#Save the File
District.to_csv("District.csv",index=False)
District.head()


# In[17]:


District.groupby('Region').sum()


# As shopping mall provides varities of shops to customers, incuding differnent cusine restaturants, boutiques, supermarkets and shops, and most of the mall are close to public transport in Hong Kong, making the mall to be a suitable place of building new cinema. 
# In fact, accroding to the report from a local property agent, currently over 70% of cinemas are located in large scale shopping malls.
# 
# As above, we suggest the below 5 shopping malls to build the new cinema, 
# 
# * Central - Infinitus Plaza Shopping Arcade
# * #Kwun Tong - Yue Man Square
# * Tuen Mun - V City
# * Tsuen Wan - Nan Fung CCentre
# * Ssp - Dragon Centre
# * Hang Hau - East Point City

# In[18]:


#Create DataFrame for Possible location
temp = {
'Central':['Infinitus Plaza'],
'Tuen Mun':['V City'],
'Tsuen Wan':['Nan Fung Centre'],
'Sham Shui Po':['Dragon Centre'],
'Hang Hau':['East Point City']
}

possible_location = pd.DataFrame.from_dict(temp).T
possible_location.reset_index(inplace=True)
possible_location.rename(columns={'index':'District', 0:'Location'},inplace=True)


# In[19]:


possible_location['Latitude'] = None
possible_location['Longitude'] = None


for i in range(len(possible_location['Location'])):
    geolocator = Nominatim()
    location = geolocator.geocode(possible_location['Location'][i])
    latitude = location.latitude
    longitude = location.longitude
    possible_location.loc[i,'Latitude'] = latitude
    possible_location.loc[i,'Longitude'] = longitude
    
possible_location


# In[ ]:





# In[20]:


top_10_cinema = [
'星影匯',
'英皇戲院（尖沙咀iSQUARE）',
'海運戲院',
'UA MegaBox',
'MOVIE TOWN - 新城市廣場',
'UA Cine Moko',
'MY CINEMA YOHO MALL',
'Cinema City 朗豪坊',
'Festival Grand Cinema',
'MCL 德福戲院']
#The Grand Cinema is closed down, so ''MCL 德福戲院' is included


# In[ ]:





# In[21]:


#Get the geo location of Hong Kong
address = 'Hong Kong'

geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print(latitude, longitude)
print(location)

# Foursquare API
CLIENT_ID = '#' # Put Your Client Id
CLIENT_SECRET = '#' # Put You Client Secret 
VERSION = '20200508'
print('Your credentails:')
print('CLIENT_ID: Hidden')
print('CLIENT_SECRET: Hidden')

LIMIT = 100
lat = latitude
lng = longitude
radius = 500


# In[22]:


categories={'Food': '4d4b7105d754a06374d81259',
    'Shop & Service': '4d4b7105d754a06378d81259',
    'Bus Stop': '52f2ab2ebcbc57f1066b8b4f',
    'Metro Station': '4bf58dd8d48988d1fd931735',
    'Arts & Entertainment': '4d4b7104d754a06370d81259'}

categories = pd.DataFrame.from_dict(categories,orient='index')
categories.reset_index(inplace=True)
categories.rename(columns={'index':'Categories',0:'ID'},inplace=True)
categories


# In[23]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)

    
        for i in range(len(categories)):
            cid = categories.loc[i,'ID']
            cate = categories.loc[i,'Categories']
            # create the API request URL
            url = 'https://api.foursquare.com/v2/venues/explore?categoryId={}&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
                cid,
                CLIENT_ID, 
                CLIENT_SECRET, 
                VERSION, 
                lat, 
                lng, 
                radius, 
                LIMIT)

            # make the GET request
            results = requests.get(url).json()["response"]['groups'][0]['items']

            # return only relevant information for each nearby venue
            venues_list.append([(
                name, 
                lat, 
                lng, 
                cate,
                v['venue']['name'], 
                v['venue']['location']['lat'], 
                v['venue']['location']['lng'],  
                v['venue']['categories'][0]['name']) for v in results])

            nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
            nearby_venues.columns = ['Neighborhood', 
                      'Neighborhood Latitude', 
                      'Neighborhood Longitude',
                      'Category',
                      'Venue', 
                      'Venue Latitude', 
                      'Venue Longitude', 
                      'Venue Category']

    return(nearby_venues)


# In[24]:


Cinema_venues = getNearbyVenues(names=Cinema['Cinema'],
                                   latitudes=Cinema['Latitude'],
                                   longitudes=Cinema['Longitude']
                                  )


# In[25]:


Cinema_venues.groupby('Neighborhood').count().head()


# In[26]:


Count_table = Cinema_venues.groupby(['Neighborhood','Category']).count()
Count_table.drop(['Neighborhood Longitude','Venue','Venue Latitude','Venue Longitude','Venue Category'],axis=1,inplace = True)
Count_table.reset_index(inplace=True)
Count_table.rename(columns={'Neighborhood':'Cinema','Neighborhood Latitude':'Count'},inplace=True)
Count_table.head()


# In[27]:


Cinema_venues_count = Count_table.pivot(index = 'Cinema',columns='Category', values='Count').fillna(0)
#Cinema_venues_count.rename(columns={'Category':'Category',},inplace=True)
Cinema_venues_count.reset_index(inplace=True)
Cinema_venues_count.head()


# In[28]:


tmp = []
#pd.DataFrame()

for cin in top_10_cinema:
    tmp.append(Cinema_venues_count[Cinema_venues_count['Cinema'] == cin])
cin_ven_data = pd.concat(tmp)
cin_ven_data.reset_index(inplace=True)
cin_ven_data.drop(['index'],axis=1,inplace=True)
tmp = cin_ven_data.set_index('Cinema')
del tmp.index.name
cin_ven_data = tmp


# In[ ]:





# In[29]:


# Search Possible location nearby venues 
Possible_location_venues = getNearbyVenues(names=possible_location['Location'],
                                   latitudes=possible_location['Latitude'],
                                   longitudes=possible_location['Longitude']
                                  )


# In[30]:


temp = Possible_location_venues
temp = temp.groupby(['Neighborhood','Category']).count()
temp.reset_index(inplace=True)
temp.drop(['Neighborhood Longitude','Venue','Venue Latitude','Venue Longitude','Venue Category'],axis=1,inplace = True)
temp.rename(columns={'Neighborhood':'Location','Neighborhood Latitude':'Count'},inplace=True)
tmp = temp.pivot(index = 'Location',columns='Category', values='Count').fillna(0)
del tmp.index.name
Possible_location_count = tmp
Possible_location_count


# In[ ]:





# ### Data Visualization
# - Using Bar, Pie, Box Chart to visualize the data
# - Using folium library to visualize the geographic location of cinemas (Map)
# - Foursquare Location Data
# - Search the existing cinema and 100 venues surrounded them with radius 500 meters (around 5 minutes walks)

# In[31]:


print('From the Data, Hong Kong currently have '+ str(len(Cinema)) + ' Cinema.')
Cinema_by_District = Cinema.groupby('District').count()
Cinema_by_District.drop(['Address','Latitude','Longitude','Region'],axis=1,inplace=True)
Cinema_by_District.rename(columns={'Cinema':'Count'},inplace=True)
Cinema_by_District['Count'] = Cinema_by_District['Count'].astype(int)
Cinema_by_District.sort_values('Count',ascending = False).head(7)


# In[32]:


Cinema_by_District.plot(kind='bar',figsize=(20, 8))
plt.xlabel('District')
plt.ylabel('Count')
plt.title('Cinema distribution by Location') # add title to the plot

plt.show()


# From the Data, Hong Kong currently have 64 Cinemas.
# 
# 3 Areas have the most of the Cinemas - 5 Cinemas, which are Causeway Bay, Mong Kok, Tsim Sha Tsui. They are the most croweded areas in Hong Kong for people to enjoy leisure time.
# 
# Followed by 4 Areas have - 3 Cinemas, which are Tuen Mun, Kowloon Bay, Central, Tsuen Wan. 
# 
# The 7 Areas mentioned abover account for 42% of total amoount of Cinames in Hong Kong. 

# In[33]:


Cinema_by_Region = Cinema.groupby('Region').count()
Cinema_by_Region.drop(['Address','Latitude','Longitude','District'],axis=1,inplace=True)
Cinema_by_Region.rename(columns={'Cinema':'Count'},inplace=True)
Cinema_by_Region['Percentage'] = Cinema_by_Region['Count']/Cinema_by_Region['Count'].sum()*100
Cinema_by_Region


# In[34]:


Cinema_by_Region['Count'].plot(kind='pie',figsize=(20, 8),autopct='%1.1f%%',startangle=90,pctdistance=1.3,shadow=False)

plt.axis('equal')
plt.title('Cinema distribution by Region') 
plt.legend(labels=Cinema_by_Region.index, loc='upper left') 

plt.show()


# 42% or 27 Cinemas are located in Kowloon. And Hong Kong Island has the least number of Cinemas, which is 17 Cinemas or 26%. 

# In[35]:


df['Population'] = df['Population'].str.replace(",", "").astype(int)
df['Density(/km²)'] = df['Density(/km²)'].str.replace(",", "").astype(float)
df['Area(km²)'].astype(float)

HKI_pp = df[df['Region']=='Hong Kong Island']['Population'].sum()
NT_pp = df[df['Region']=='New Territories']['Population'].sum()
KL_pp = df[df['Region']=='Kowloon']['Population'].sum()

HKI_Density = HKI_pp / (df[df['Region']=='Hong Kong Island']['Area(km²)'].astype(float).sum())
NT_Density = NT_pp / (df[df['Region']=='New Territories']['Area(km²)'].astype(float).sum())
KL__Density = KL_pp / (df[df['Region']=='Kowloon']['Area(km²)'].astype(float).sum())


# In[37]:


Dict = {'Hong Kong Island':HKI_Density,'New Territories':NT_Density, 'Kowloon': KL__Density}
Density = pd.DataFrame.from_dict(Dict,orient='index')
Density = Density.rename(columns={0:'Density'})

Density.plot(kind='bar',figsize=(20, 8))

plt.xlabel('Region')
plt.ylabel('Density(/km²)')
plt.title('Region Density Graph') # add title to the plot

plt.show()
Density


# From the graph, Kowloon is the crowded region in Hong Kong, which is 3 times as Hong Kong Island. 

# In[38]:


District_Density = District
District_Density['Density(/km²)'] = District_Density['Density(/km²)'].str.replace(",", "").astype(float) #replace(",", "")
District_Density = District_Density [['District', 'Density(/km²)' , 'Region']]
District_Density.sort_values(by=['Density(/km²)'],inplace=True, ascending=False)
District_Density = District_Density.reset_index()
District_Density = District_Density.drop(['index'],axis=1)


# In[39]:


District_Density = District_Density.drop('Region',axis=1)
District_Density = District_Density.set_index('District')
District_Density


# In[40]:


District_Density.plot(kind='bar',figsize=(20, 8))

plt.xlabel('District')
plt.ylabel('Density(/km²)')
plt.title('District Density Graph') # add title to the plot

plt.show()


# The most crowded district in Hong Kong is Kwun Tong, followed by Wong Tai Sin, Yau Tsim Mong, Sham Shui Po, and Kowloon City. 
# All of these districts are 40,000 ppl/km². 
# 
# Besides, the higher the district population density will provide a higher chance people will visit the local facilities, especially during weekend or holiday.

# In[41]:


#Get the geo location of Hong Kong
address = 'Hong Kong'

geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print(address + 'Geographical location is' + str(latitude) + ',' str(longitude))


# In[ ]:


#Visulization

HK_map = folium.Map(location=[latitude,longitude],zoom_start = 11)


for lat, lng, dis, reg in zip(HKI.Latitude, HKI.Longitude, HKI.District, HKI.Region):
    label = folium.Popup(str(dis) + str(reg), parse_html=True)
    folium.CircleMarker(
        [lat,lng],
        radius = 35,
        color = 'blue',
        popup = label,
        fill = False,
        fill_color = 'blue',
        fill_opacity = 0.01
    ).add_to(HK_map)

    
for lat, lng, dis, reg in zip(KL.Latitude, KL.Longitude, KL.District, KL.Region):
    label = folium.Popup(str(dis) +',' + str(reg), parse_html=True)
    folium.CircleMarker(
        [lat,lng],
        radius = 35,
        color = 'yellow',
        popup = label,
        fill = False,
        fill_color = 'yellow',
        fill_opacity = 0.01
    ).add_to(HK_map)

for lat, lng, dis, reg in zip(NT.Latitude, NT.Longitude, NT.District, NT.Region):
    label = folium.Popup(str(dis) +',' + str(reg), parse_html=True)
    folium.CircleMarker(
        [lat,lng],
        radius = 35,
        color = 'green',
        popup = label,
        fill = False,
        fill_color = 'green',
        fill_opacity = 0.01
    ).add_to(HK_map)

for lat, lng, name, reg in zip(Cinema.Latitude, Cinema.Longitude, Cinema.Cinema, Cinema.District):
    label = folium.Popup(str(name) + ',' +str(reg), parse_html=True)
    folium.CircleMarker(
        [lat,lng],
        radius = 5,
        color = 'magenta',
        popup = label,
        fill = True,
        fill_color = 'magenta',
        fill_opacity = 0.8
    ).add_to(HK_map)
    
for lat, lng, name, reg in zip(possible_location.Latitude, possible_location.Longitude, possible_location.Location, possible_location.District):
    label = folium.Popup(str(name) +',' + str(reg), parse_html=True)
    folium.CircleMarker(
        [lat,lng],
        radius = 10,
        color = 'red',
        popup = label,
        fill = True,
        fill_color = 'red',
        fill_opacity = 0.8
    ).add_to(HK_map)
    
HK_map
    
    


# From the above visualization, around 40% of Kowloon Cinemas are located at Yau Tsim Mong District, our possible locations are in other areas to avoid direct keen competition with other Cinemas. 
# 
# Besides, for possible location – Sham Shui Po and Hang Hau, there are no existing competitors in the district. The possible location – Tsuen Wan and Central will directly complete with 4 and 3 currently Cinemas respectively once we decided to locate our new Cinema in these districts, so we need to further consider other factor to make better decision. 
# 
# 

# In[ ]:


fig = plt.figure() # create figure

ax0 = fig.add_subplot(1, 2, 1) # add subplot 1 (1 row, 2 columns, first plot)
ax1 = fig.add_subplot(1, 2, 2) # add subplot 2 (1 row, 2 columns, second plot). See tip below**

# Subplot 1: Box plot
cin_ven_data.plot(kind='box', color='blue', vert=False, figsize=(20, 6), ax=ax0) # add to subplot 1
ax0.set_title('Box Plots of Immigrants from China and India (1980 - 2013)')
ax0.set_xlabel('Number of Immigrants')
ax0.set_ylabel('Countries')

# Subplot 2: Line plot
Possible_location_count.plot(kind='bar',figsize=(20, 6), ax=ax1) # add to subplot 2
ax1.set_title ('Line Plots of Immigrants from China and India (1980 - 2013)')
ax1.set_ylabel('Number of Immigrants')
ax1.set_xlabel('Years')

plt.show()


# From the above left box graph, this shown the variation in the public transportation (including Metro station and Bus stop) and Art & Entertainment are not large.
# However, we can see a bigger variance in Shop & Service and Food Categories, so for the new cinema location, we tend to select the location with above the average in these aspects.
# 
# From the above right graph, Infinitus Plaza is the most superior location in all aspects, especially in Shop & Service, and Shops categories, which can induce the people to stay longer within the district. 
# On the other hand, the other 4 possible locations are similar in all aspects.

# In[42]:


cin_ven_data.describe()


# In[43]:


Mark = Possible_location_count
Mark['Mark'] = ((Possible_location_count['Arts & Entertainment']-cin_ven_data['Arts & Entertainment'].mean()+
Possible_location_count['Bus Stop']-cin_ven_data['Bus Stop'].mean()+
Possible_location_count['Food']-cin_ven_data['Food'].mean()+
Possible_location_count['Metro Station']-cin_ven_data['Metro Station'].mean()+
Possible_location_count['Shop & Service']-cin_ven_data['Shop & Service'].mean())/5)
Mark


# ## Conclusion

# In[44]:


Summary = pd.DataFrame()
tmpa = ['Dragon Centre','East Point City','Infinitus Plaza','Nan Fung Centre','V City']
tmpb = ['Sham Shui Po','Hang Hau', 'Causeway bay','Tsuen Wan','Tsum Mun']
tmpc = [0,0,3,3,4]
tmpd = [4,14,8,13,12]
Summary['Location'] = tmpa
Summary['District'] = tmpb
Summary['Number of Cinema in 500m'] = tmpc
Summary['Population Density'] = tmpd
Summary['Mark'] = Possible_location_count['Mark']
Summary


# ### Conclusion
# 
# All in all, we need to base on the above data to the business question “Where is the most suitable location for launching the new cinema?”.
# 
# First, we can eliminate the option “Nan Fung Centre” and “V City” since there are 3 and 4 cinemas respectively within the districts. Building a new cinema in these districts will directly complete with the existing cinemas, which cannot guarantee a high count of visits due to the potential customers are shared. More, the two locations are located near the border part of Hong Kong, which is far apart from the city centre. So the public transportation are not convenient for these two locations, only 3 Bus stops and 1 Metro Station for “Nan Fung Centre” and 5 Bus stops and no Metro Station for “V City”, also inconvenient transportation will prohibit the visitors outside the district.
# 
# Next, we can eliminate the option “East Point City, Hang Hau”, although there is no cinema currently in the district, however, as it also located near the border part of Hong Kong with 5 Bus stops and 1 Metro Station, plus the lowest number of Arts & Entertainment (3) and Shop & Service (25), which is lower the attractiveness of the district, visitors outside the district are seldom to visit “Hang Hau”.  Besides, the population density is the lowest among the 5 possible locations.
# 
# Last, we need to select the suitable location between “Dragon Centre, Sham Shui Po” and “Infinitus Plaza, Causeway Bay”. Although there is no cinema currently in the district “Sham Shui Po”, and the population density is the largest among the 5 possible locations, however, “Sham Shui Po” is the district with the lowest per person income district and people may not willing to spend to much in their leisure time. In contrast, location “Infinitus Plaza, Causeway Bay” is more superior location in most aspects. 
# 
# Infinitus Plaza is the city centre of Hong Kong Island, coming with lot of offices are in this district, Infinitus Plaza can reach the visitors and citizens from other districts. More, this is ranked 8 with population density among the 18 districts, which provided a large potential customer base for our new cinema. Besides, in the nearby venues’ matrix, Infinitus Plaza are ranked number 1 in all aspects. Public transportation is convenient near Infinitus Plaza, there are 17 Bus stops, 1 metro station nearby. More, there are 21 Arts & Entertainment, 94 Food & Restaurants and 86 Shop & Services, which can provide enough attraction points for people to spend their afternoon or night-time. 
# 
# Although there are 3 existing cinemas there, however, with the large number of potential customers, including local distract citizens, office workers and visitors outside distract, with the great number of attraction points, choosing Infinitus Plaza to build the new cinema is the most suitable location. 
# 

# ### Reference: 
# Indicator of Cuture(Hong Kong): http://www.worldcitiescultureforum.com/cities/hong-kong/data
# 
# List of Cinema in Hong Kong: https://hkmovie6.com/cinema
# 
# List of Top 10 popular Cinema in Hong Kong: https://post76.hk/thread-286507-1-1.html
# 
# Lack of long term development plan of Hong Kong Cineam Industry: 
# https://www.hk01.com/01%E8%A7%80%E9%BB%9E/288700/%E6%88%B2%E9%99%A2%E7%99%BC%E5%B1%95%E4%BB%8D%E6%AC%A0%E9%95%B7%E9%81%A0%E8%A6%8F%E5%8A%83-%E5%95%8F%E9%A1%8C%E8%B1%88%E6%AD%A2-%E8%B7%A8%E5%A2%83%E8%B3%80%E6%AD%B2
# 

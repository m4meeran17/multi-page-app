import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
import datetime as dtm
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

headers = ['url', 'city', 'date', 'sessions', 'bounceRate', 'pageViews', 'avgSessionDuration']
dtypes = {"url":str,"city":str,"date":str,"sessions":int,"bounceRate":float,"pageViews":int,"avgSessionDuration":str}

def con():
    #mongodb connection
    client = MongoClient()
    #point the client at mongo URI
    client = MongoClient('mongodb+srv://dev_dat_2020:dev_dat_2020@cluster0-d2mfc.mongodb.net')
    #select database
    return client['dat-dev']
def getTrends(db):
    print("Getting trends collection...!!")    
    trends_details = db.trends
    print("Collection retrieved..!!!")
    trends_df_mongo = pd.DataFrame(list(trends_details.find())
    # ,dtype=dtypes
    )
    print("DataFrame created..!!!")
    return trends_df_mongo


def app():
    st.title('Trends')
    st.write('Edvoy Trends')
    db = con()
    #Loading Collection
    trendsDF = getTrends(db)
    print("Preprocessing..!!!")
    institutionDF = trendsDF.loc[trendsDF.url.str.contains(r"edvoy.com/institutions/(\w.*)")]
    institutionDF['temp'] = institutionDF.url.str.replace("edvoy.com/institutions/","")
    institutionDF['univName'] = institutionDF.temp.apply(
        lambda x: x
        .split("/")[0]
        .replace("www.","")
        .replace("edvoy.com","")
        .replace("staging.","")
        .replace("qa.","")
        )
    institutionDF.loc[institutionDF.univName.str.contains("\.com"),'univName'] = np.NaN
    institutionDF.dropna(subset=['univName'],inplace=True)

    # groupByUniv = institutionDF.groupby(by=['univName'],dropna=True,as_index=False)['pageViews'].sum()
    # groupByUnivCity = institutionDF.groupby(by=['univName','city'],dropna=True,as_index=False)['pageViews'].sum()
    # groupByUniv.sort_values(by="pageViews",ascending=False,inplace=True)
    # groupByUnivCity.sort_values(by="pageViews",ascending=False,inplace=True)

    
    today = dtm.date.today()
    yesterday =  today - dtm.timedelta(days=1)
    # print(today,yesterday)
    start_date = st.date_input('Start date', yesterday)
    end_date = st.date_input('End date', today)
    print(start_date,end_date)
    if start_date < end_date:
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
        print("Aggregating...!!")
        dateFilterDF = institutionDF.loc[institutionDF.date.isin(pd.date_range(start_date, end_date))]
        groupByUniv = dateFilterDF.groupby(by=['univName'],dropna=True,as_index=False)['pageViews'].sum()
        # groupByUnivCity = dateFilterDF.groupby(by=['univName','city'],dropna=True,as_index=False)['pageViews'].sum()
        groupByUniv.sort_values(by="pageViews",ascending=False,inplace=True)
        # groupByUnivCity.sort_values(by="pageViews",ascending=False,inplace=True)
        st.dataframe(groupByUniv)
        # st.dataframe(groupByUnivCity)
    else:
        st.error('Error: End date must fall after start date.')
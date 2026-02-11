import os
import psycopg2
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from datetime import timedelta

load_dotenv()

conn  = psycopg2.connect(host=os.environ['DB_HOST'],
                         user=os.environ['DB_USER'],
                         database=os.environ['DB_NAME'],
                         password=os.environ['DB_PASSWORD'],
                         port=int(os.environ['DB_PORT']))


#--------------------------------------------------------------------
def sql2pandas(sql_request):
   """
   Given a SQL request, use a cursor to extract the data and convert
   them into a pandas dataframe.

   Parameters
   ----------
   str
         SQL request to extract the data

   Returns
   -------
   pandas.core.frame.DataFrame
         requested data
   """

   cursor = conn.cursor()
   cursor.execute(sql_request)

   columns = cursor.description
   result = [{columns[index][0]: column for index, column in enumerate(value)}
                        for value in cursor.fetchall()]

   return pd.DataFrame(result)

#--------------------------------------------------------------------
def read_temperatures(conn,stations_itn=[]):
   """
   Read the csv file containing the data into a pandas DataFrame. The times
   are converted into datetime object.

   Parameters
   ----------
   conn: psycopg2.extensions.connection
         Connection to the database
   stations_itn: list or tuple
         list of the stations to be considered to calculate the ITN.

   Returns
   -------
   stations: pandas.core.frame.DataFrame
         data of the stations extracted
   temp_hourly: pandas.core.frame.DataFrame
         hourly measurement of the air, min and max temperature
   temp_daily: pandas.core.frame.DataFrame
         daily record of the min, max and 'mean' temperature
   """

   sql_request = """SELECT
                       *
                    FROM
                       weather_station
                 """
   if(len(stations_itn)>0):
      sql_request += f"""WHERE
                            code in {stations_itn}"""
#   stations = pd.read_sql(sql_request, con=conn)
   stations = sql2pandas(sql_request)



   sql_request = f"""SELECT
                        w.station_id,s.nom,
                        w.validity_time as dh_utc,
                        w.t as temperature,
                        w.tx as temp_max,
                        w.tn as temp_min
                     FROM
                        weather_horairetempsreel as w
                        JOIN weather_station as s
                           ON s.id = w.station_id
                     WHERE
                        station_id in {tuple(stations['id'])}
                 """
#   temp_hourly = pd.read_sql(sql_request, con=conn)
   temp_hourly = sql2pandas(sql_request)
   temp_hourly['dh_utc'] = pd.to_datetime(temp_hourly['dh_utc'])



   sql_request = f"""SELECT
                        w.station_id,s.nom,
                        w.date, w.tx as temp_max,
                        w.tn as temp_min,w.tntxm as temp_mean
                     FROM
                        weather_quotidienne as w
                        JOIN weather_station as s
                           ON s.id = w.station_id
                     WHERE
                        station_id in {tuple(stations['id'])}
                 """
#   temp_daily = pd.read_sql(sql_request, con=conn)
   temp_daily = sql2pandas(sql_request)
   temp_daily['date'] = pd.to_datetime(temp_daily['date'])

   return stations,temp_hourly,temp_daily

#--------------------------------------------------------------------
def separate_by_station(df,index='',columns='',values='',freq='h'):
   """
   Pivot the data to get one column for each meteorological station.

   Parameters
   ----------
   df: pandas.core.frame.DataFrame
         temperature data to pivot
   index: str
         column to use as the new frame's index
   columns: str
         column to use as the new frame's columns
   values: str
         column(s) to use as the new frame's values
   freq: str
         time frequency of the new frame

   Returns
   -------
   pandas.core.frame.DataFrame
         temperature records, with one column per station
   """

   assert (index != '') & (columns != '') & (values != ''), \
            'Cannot pivot, missing arguments'

   cols = df.columns
   data_temp = pd.pivot_table(df,index=index,
                                 columns=columns,
                                 values=values)

   return data_temp.asfreq(freq).astype(float)

#--------------------------------------------------------------------
def correct_temperatures_Reims(df):
   """
   Correct the temperatures of the Reims-Prunay station due to the location
   difference with the former Reims-Courcy station.
   This fonction might be updated in the future if a better correction
   is find (discussion in issue #25 of GitHub).

   Not tested because the data are not modelled.

   Parameters
   ----------
   pandas.core.frame.DataFrame
         temperature records, with one column per station

   Returns
   -------
   pandas.core.frame.DataFrame
         temperature records, with one column per station that include
         correction for the Reims-Prunay station.
   """

   # Reims-Prunay: keep only the data after Reims-Courcy was decommissioned
   corrected_df = df.copy()
   corrected_df = corrected_df.loc[pd.notnull(test['Reims-Courcy']),
                     'Reims-Prunay']=float('nan')

   # Correction based on the difference in the mean TNTXM between
   # the two stations during the two years of overlap
   corrected_df['Reims-Prunay'] = corrected_df['Reims-Prunay']+0.29

   return corrected_df

#--------------------------------------------------------------------
def calculate_min_temperature(df):
   """
   Derive the daily minimale temperature from 18h (J-1) to 18h (J) UTC

   Parameters
   ----------
   pandas.core.frame.DataFrame
         temperature records, with one column per station

   Returns
   -------
   pandas.core.frame.DataFrame
         derived minimum temperature for each station
   """
   # initiate
   temp_min = df.resample('D').max()

   for day in temp_min.index:
      row = temp_min.loc[temp_min.index == day]

      init  = day+timedelta(days = -1,hours = 18)
      final = day+timedelta(hours = 18)
      init_str,final_str = init.isoformat(),final.isoformat()

      records = df[init_str:final_str]
      # return NaN if less than 24h of data
      if(len(records.index) < 25):
         temp_min.loc[temp_min.index == day] = row*float('nan')
         continue

      for col in records.columns:
         row[col] = records[col].min()
      temp_min.loc[temp_min.index == day] = row

   return temp_min

#--------------------------------------------------------------------
def calculate_max_temperature(df):
   """
   Derive the daily maximale temperature from 6h (J) to 6h (J+1) UTC

   Parameters
   ----------
   pandas.core.frame.DataFrame
         temperature records, with one column per station

   Returns
   -------
   pandas.core.frame.DataFrame
         derived maximale temperature for each station
   """
   # initiate
   temp_max = df.resample('D').min()

   for day in temp_max.index:
      row = temp_max.loc[temp_max.index == day]

      init  = day+timedelta(hours = 6)
      final = day+timedelta(days = 1,hours = 6)
      init_str,final_str = init.isoformat(),final.isoformat()

      records = df[init_str:final_str]
      # return NaN if less than 24h of data
      if(len(records.index) < 25):
         temp_max.loc[temp_max.index == day] = row*float('nan')
         continue

      for col in records.columns:
         row[col] = records[col].max()
      temp_max.loc[temp_max.index == day] = row

   return temp_max

#--------------------------------------------------------------------
def itn_calculation(df):
   """
   Extract only the temperature records and create on column for each station.

   Parameters
   ----------
   pandas.core.frame.DataFrame
         daily temperature records, with one column per station

   Returns
   -------
   pandas.core.frame.DataFrame
         computed ITN following the method of InfoClimat
   """

   temp_min  = df['temp_min']
   temp_max  = df['temp_max']

   temp_mean = (temp_max+temp_min)/2

   return temp_mean.mean(axis=1)

#--------------------------------------------------------------------
def calculate_return_itn():
   """
   Main part of the script.

   Parameters
   ----------

   Returns
   -------
   numpy.ndarray
         array Nx2 containing the date and ITN
   """

   stations_itn = ('6088001','13054001','14137001','16089001',
                   '20148001','21473001',
                   '25056001', # Besançon - Thise?
                   '26198001',
                   '29075001','30189001','31069001','33281001',
                   '35281001','36063001','44020001','45055001',
                   '47091001',
                   '51449002', # Reims - Prunay
                   '51183001', # Reims - Courcy
                   '54526001','58160001','59343001','63113001',
                   '64549001',
                   '66164002', # Perpignan - Rivesaltes?
                   '67124001','69029001',
                   '72008001','73054001','75114001','86027001')

   stations,temp_hourly,temp_daily = read_temperatures(conn,
                                                stations_itn=stations_itn)



   hourly_temp_per_station  = separate_by_station(temp_hourly,
                                                  index='dh_utc',
                                                  columns='nom',
                                                  values='temperature',
                                                  freq='h')
   daily_records_by_station = separate_by_station(temp_daily,
                                                  index='date',
                                                  columns='nom',
                                                  values=['temp_min','temp_max',
                                                          'temp_mean'],
                                                  freq='D')


   if(('Reims-Courcy' in stations['nom'])&
      ('Reims-Prunay' in stations['nom'])):
      hourly_temp_per_station_corr  = correct_temperatures_Reims(hourly_temp_per_station)
      daily_records_by_station_corr = correct_temperatures_Reims(daily_records_by_station)



   assert (hourly_temp_per_station.dtypes == float).all(), \
             'Data are not in the proper format.'

   itn = itn_calculation(daily_records_by_station)
   dates  = itn.index.strftime('%Y-%m-%d').to_numpy()
   values = itn.values

   return np.array([(d,v) for d,v in zip(dates,values)])

#--------------------------------------------------------------------


#results = calculate_return_itn()
#print(results)

#exec(open('weather/calcul_itn.py').read())




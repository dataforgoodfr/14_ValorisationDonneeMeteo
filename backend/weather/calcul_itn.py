import pandas as pd
from datetime import timedelta


#--------------------------------------------------------------------
def read_data(filename):
   """
   Read the csv file containing the data into a pandas DataFrame. The times
   are converted into datetime object.

   Parameters
   ----------
   str
         path and name of the csv file

   Returns
   -------
   pandas.core.frame.DataFrame
         meteorological data from InfoClimat
   """

   data = pd.read_csv(filename,skiprows=10,header=None,delimiter=';')

   # Merge the two lines corresponding to the header
   cols = data[:2].fillna('').agg(' '.join, axis=0).values
   data = data[2:]
   data.columns = cols

   data = data.rename(columns={'station_id string': 'station_id',
                            'dh_utc YYYY-MM-DD hh:mm:ss': 'dh_utc'})
   data['dh_utc'] = pd.to_datetime(data['dh_utc'])

   return data

#--------------------------------------------------------------------
def extract_temperatures(df):
   """
   Extract only the temperature records and create on column for each station.

   Parameters
   ----------
   pandas.core.frame.DataFrame
         full meteoroological data from InfoClimat

   Returns
   -------
   pandas.core.frame.DataFrame
         temperature records, with one column per station
   """

   cols = df.columns
   data_temp = df.pivot(index=cols[0],
                        columns=cols[1],
                        values=cols[2])

   return data_temp.asfreq("h").astype(float)

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

      records = temp_per_station[init_str:final_str]
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

      records = temp_per_station[init_str:final_str]
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
         temperature records, with one column per station

   Returns
   -------
   pandas.core.frame.DataFrame
         computed ITN following the method of InfoClimat
   """

   temp_min  = calculate_min_temperature(df)
   temp_max  = calculate_max_temperature(df)

   temp_mean = (temp_max+temp_min)/2

   return temp_mean.mean(axis=1)

#--------------------------------------------------------------------

filename = 'data/export_infoclimat.csv'
data = read_data(filename)

temp_per_station = extract_temperatures(data[['dh_utc','station_id',
                                              'temperature °C']])

assert (temp_per_station.dtypes == float).all(), 'Data are not in the proper format.'

itn = itn_calculation(temp_per_station)

#exec(open('calcul_itn.py').read())





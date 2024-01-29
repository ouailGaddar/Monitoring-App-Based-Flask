from matplotlib import pyplot as plt
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import json
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler
def fetch_weather_data_between_dates(latitude, longitude, start_date, end_date):
    # Setup the Open-Meteo API client with cache and retry on error
    
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max"]
    }

    # Fetch weather data
    responses = openmeteo.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_data = {
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s"),
            end=pd.to_datetime(daily.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ).strftime('%d-%m-%Y').tolist(),
        "temperature_2m_max": daily.Variables(0).ValuesAsNumpy().tolist(),
        "temperature_2m_min": daily.Variables(1).ValuesAsNumpy().tolist(),
        "temperature_2m_mean": daily.Variables(2).ValuesAsNumpy().tolist(),
        "precipitation_sum": daily.Variables(3).ValuesAsNumpy().tolist(),
        "rain_sum": daily.Variables(4).ValuesAsNumpy().tolist(),
        "snowfall_sum": daily.Variables(5).ValuesAsNumpy().tolist(),
        "precipitation_hours": daily.Variables(6).ValuesAsNumpy().tolist(),
        "wind_speed_10m_max": daily.Variables(7).ValuesAsNumpy().tolist()
    }

    return json.dumps(daily_data)

def predict_future_weather(weather_data, target_date):
    # Convertir la chaîne JSON en DataFrame
    df = pd.read_json(weather_data)

    # Sélectionner les caractéristiques du modèle
    model_features = ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "rain_sum", "snowfall_sum", "wind_speed_10m_max"]

    # Sélectionner la cible de prédiction
    model_target = "precipitation_sum"

    # Convertir la colonne "date" en format datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')

    # Diviser les données en ensembles d'entraînement et de test
    X_train = df[model_features]
    y_train = df[model_target]

    # Initialiser le modèle de régression linéaire
    model = LinearRegression()

    # Entraîner le modèle
    model.fit(X_train, y_train)

    # Prédire la météo pour la date cible
    target_date_data = df[df['date'] == target_date].fillna(df[model_features].mean())

    if not target_date_data.empty:
        prediction_data = target_date_data[model_features]
        weather_prediction = model.predict(prediction_data)[0]
        # Ajuster la prédiction à zéro si elle est négative
        weather_prediction = max(0, weather_prediction)
        return weather_prediction
    else:
        # Si la date cible n'est pas présente, utiliser les données les plus récentes pour prédire
        latest_data = df.tail(1)[model_features].fillna(df[model_features].mean())
        weather_prediction = model.predict(latest_data)[0]
        # Ajuster la prédiction à zéro si elle est négative
        weather_prediction = max(0, weather_prediction)
        return weather_prediction



def predict_precipitation_sum_between_dates(weather_data, start_date, end_date):
    
    results_dict = {}

    # Convertir les dates de début et de fin en objets datetime
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    # Boucle sur chaque jour entre start_date et end_date
    current_date = start_date
    while current_date <= end_date:
        # Convertir la date en format de chaîne pour la prédiction
        target_date_str = current_date.strftime('%Y-%m-%d')

        # Prédire la météo (precipitation_sum) pour la date actuelle
        weather_prediction = predict_future_weather(weather_data, target_date_str)

        
        results_dict[target_date_str] = weather_prediction

        
        current_date += timedelta(days=1)

    return results_dict

if __name__ == '__main__' :
   
    latitude = 52.52
    longitude = 13.41
    start_date = "2022-07-01"
    end_date = "2024-01-20"

    
    weather_data = fetch_weather_data_between_dates(latitude, longitude, start_date, end_date)
    start_date1 = datetime.strptime("2024-02-01", "%Y-%m-%d")
    end_date1 = datetime.strptime("2024-03-20", "%Y-%m-%d")


    predictions_dict = predict_precipitation_sum_between_dates(weather_data,start_date1,end_date1)
   
    predictions_df = pd.DataFrame(list(predictions_dict.items()), columns=['date', 'precipitation_sum'])
    predictions_df['date'] = pd.to_datetime(predictions_df['date'], format='%Y-%m-%d')

    plt.figure(figsize=(10, 6))
    plt.plot(predictions_df['date'], predictions_df['precipitation_sum'], marker='o', linestyle='-', color='b')
    plt.title('Prédictions de precipitation_sum entre {} et {}'.format(start_date1, end_date1))
    plt.xlabel('Date')
    plt.ylabel('Précipitation Sum')
    plt.grid(True)
    plt.show()


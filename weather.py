import requests
import ujson
import utime

station_id1 = "KLCI"
station_id2 = "KDAW"

def get_current_temperature_and_humidity():
    def fetch_data(station_id):
        observations_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        headers = {'User-Agent': 'weather app (your_email@example.com)'}
        response = requests.get(observations_url, headers=headers)

        if response.status_code != 200:
            return None, f"Error: Received status code {response.status_code} from the API", "", ""
        
        try:
            observation_data = ujson.loads(response.text)
        except ValueError:
            return None, "Error: Response is not valid JSON", "", ""
        
        # Extract temperature
        current_temperature = observation_data['properties']['temperature']['value']
        if current_temperature is not None:
            current_temperature = (current_temperature * 9/5) + 32  # Convert from Celsius to Fahrenheit
        
        # Extract humidity
        current_humidity = observation_data['properties']['relativeHumidity']['value']
        if current_humidity is not None:
            current_humidity = round(current_humidity)  # Round to nearest whole number
        
        # Check if both temperature and humidity data were available
        if current_temperature is not None and current_humidity is not None:
            return station_id, current_temperature, "F", f"{current_humidity}%"
        else:
            return None, "Data not available", "", ""
    
    station_id, temperature, temp_unit, humidity = fetch_data(station_id1)
    if station_id is None:
        station_id, temperature, temp_unit, humidity = fetch_data(station_id2)
    
    return station_id, temperature, temp_unit, humidity

# Example usage
#station_id, temperature, temp_unit, humidity = get_current_temperature_and_humidity()
#if temp_unit:  # Check if temperature data was available
#    print(f"Current temperature {station_id}: {temperature} {temp_unit}, Humidity: {humidity}")
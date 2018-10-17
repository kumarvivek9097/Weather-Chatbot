import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    
    res = processRequest(req)
    
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#processing the request from dialogflow
def processRequest(req):
    
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    observation = owm.weather_at_place(city)
    w = observation.get_weather()
    latlon_res = observation.get_location()
    lat=str(latlon_res.get_lat())
    lon=str(latlon_res.get_lon())
     
    wind_res=w.get_wind()
    wind_speed=str(wind_res.get('speed'))
    
    humidity=str(w.get_humidity())
    
    celsius_result=w.get_temperature('celsius')
    temp_min_celsius=str(celsius_result.get('temp_min'))
    temp_max_celsius=str(celsius_result.get('temp_max'))
    
    fahrenheit_result=w.get_temperature('fahrenheit')
    temp_min_fahrenheit=str(fahrenheit_result.get('temp_min'))
    temp_max_fahrenheit=str(fahrenheit_result.get('temp_max'))
    speech = "Today the weather in " + city + ": \n" + "Temperature in Celsius:\nMax temp :"+temp_max_celsius+".\nMin Temp :"+temp_min_celsius+".\nTemperature in Fahrenheit:\nMax temp :"+temp_max_fahrenheit+".\nMin Temp :"+temp_min_fahrenheit+".\nHumidity :"+humidity+".\nWind Speed :"+wind_speed+"\nLatitude :"+lat+".\n  Longitude :"+lon
    
    return {
        "speech": speech,
        "displayText": speech,
        "source": "dialogflow-weather-by-satheshrgs"
        }

def makeResponse(req):
    if req.get("result").get("action") != "fetchWeatherForecast":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    date = parameters.get("date")
    if city is None:
        return None
    r=requests.get('http://api.openweathermap.org/data/2.5/forecast?q='+city+'&appid=06f070197b1f60e55231f8c46658d077')
    json_object = r.json()
    weather=json_object['list']
    for i in range(0,30):
        if date in weather[i]['dt_txt']:
            condition= weather[i]['weather'][0]['description']
            break
    speech = "The forecast for"+city+ "for "+date+" is "+condition
    return {
    "speech": speech,
    "displayText": speech,
    "source": "apiai-weather-webhook"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')

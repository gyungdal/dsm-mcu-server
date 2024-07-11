from flask import Flask, request, render_template, jsonify
from dataclasses import dataclass
import sqlite3
        
@dataclass
class Sensor:
    lux : float
    temp : float
    humi : float
    altitude : float
    battery : float

@dataclass
class History(Sensor):
    index : int
    

@dataclass
class Device:
    sensor : Sensor
    led_status: list
    buzzer : float
    
app = Flask(__name__)

lastSensor : Sensor = Sensor(500,32.4,58.2,8000,80.5)
device : Device = Device(lastSensor, [0,0,1], 300)

@app.route('/upload')
def upload():
    global lastSensor
    lastSensor.lux = float(request.args.get('lux'))
    lastSensor.temp = float(request.args.get('temp'))
    lastSensor.humi = float(request.args.get('humi'))
    lastSensor.altitude = float(request.args.get('altitude'))
    lastSensor.battery = float(request.args.get('battery'))

    with sqlite3.connect(database="test.db") as connector:
        cursor =  connector.cursor()
        SQL = "CREATE TABLE IF NOT EXISTS sensor (id INTEGER PRIMARY KEY AUTOINCREMENT, lux REAL,temp REAL,humi REAL,altitude REAL,battery REAL)"
        SQL = f"INSERT INTO sensor (lux, temp, humi, altitude, battery) values (?,?,?,?,?)"
        cursor.execute(SQL, (lastSensor.lux, lastSensor.temp, lastSensor.humi, lastSensor.altitude, lastSensor.battery))
        connector.commit()
        cursor.close()
    print(f"sensor : {lastSensor}")
    if lastSensor.lux > 20:
        device.led_status[0] = 1
    else:
        device.led_status[0] = 0
    if lastSensor.temp > 26:
        device.led_status[1] = 1
    else:
        device.led_status[1] = 0
    if lastSensor.humi > 60:
        device.led_status[2] = 1
    else:
        device.led_status[2] = 0
    if lastSensor.battery < 20:
        device.buzzer = 4000
    else:
        device.buzzer = 0
    
    return jsonify(device)
    

@app.route('/get')
def get():
    global device
    return jsonify(device)

@app.route('/data')
def data_list():
    ret = list()
    with sqlite3.connect(database="test.db") as connector:
        cursor =  connector.cursor()
        SQL = "SELECT * from sensor"
        cursor.execute(SQL)
        # ret = cursor.fetchall()
        for data in cursor.fetchall():
            ret.append(History(data[1],data[2],data[3],data[4],data[5],data[0]))
        cursor.close()
    return ret

@app.route('/')
def index():
    return render_template("index.html")

with sqlite3.connect(database="test.db") as connector:
    cursor =  connector.cursor()
    SQL = "CREATE TABLE IF NOT EXISTS sensor (id INTEGER PRIMARY KEY AUTOINCREMENT, lux REAL,temp REAL,humi REAL,altitude REAL,battery REAL)"
    cursor.execute(SQL)
    connector.commit()
    cursor.close()

app.run(host='0.0.0.0', debug=True, port="5000")
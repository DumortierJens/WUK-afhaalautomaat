from repositories.DataRepository import DataRepository
from helpers.SMTPClient import SMTPClient
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, send
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS

from helpers.TemperatureSensor import TemperatureSensor
from helpers.Detector import Detector
from helpers.LcdDisplay import LcdDisplay
from helpers.Lock import Lock
from helpers.NextionDisplay import NextionDisplay

from subprocess import check_output
import threading, time, datetime, json, os, hashlib


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret!'
app.config['JWT_SECRET_KEY'] = 'Secret!'

socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False, ping_timeout=1)
jwt = JWTManager(app)

CORS(app)

api_endpoint = '/api/v1'


# SMTP client
smtp_client = SMTPClient()
alert_email = '' # Email of reciever alert
alert_interval = datetime.timedelta(hours=12)


# region Hardware Code
# region Hardware Variables


# Temperature sensor
temperature_sensor_w1_id = '28-01202c2b9593'

temperature_sensor_alert_last_send = datetime.datetime.now() - alert_interval
temperature_sensor_min = 0
temperature_sensor_max = 25


# Detector
pin_detector = 17


# Lcd Display
pin_lcd_rs = 20
pin_lcd_e = 21
pins_lcd_data = [6, 13, 19, 26]


# Locks
pin_lock_1 = 27
pin_lock_1_feedback = 22
pin_lock_2 = 24
pin_lock_2_feedback = 23


# Nextion Display
nextion_display_port = '/dev/serial0'
nextion_display_baud = 9600


# endregion
# region Callbacks


# Callback detector
def callback_detector(detector : Detector):
    
    # Detector detected
    if detector.status:
        print('Detection detected')
        DataRepository.add_history_action('Detector', 'Detection')
        nextion_display.wake_up()
    
    # Detector detect nothing
    else:
        print('No detection detected')
        DataRepository.add_history_action('Detector', 'Detection Stopped')

    # Get last detection from database and send it to the clients
    data = DataRepository.get_last_detection()
    socketio.emit('B2F_last_detection', json.dumps({'lastDetection': data}, default=DataRepository.default_serializer))


# Callback locks
def callback_lock_feedback(lock : Lock):
    
    # If the lock is open
    if lock.status:
        print(f'Lock {lock.id} opened')
        DataRepository.add_history_action(f'Lock {lock.id}', 'Lock Opened')
    
    # If the lock is closed
    else:
        print(f'Lock {lock.id} closed')
        DataRepository.add_history_action(f'Lock {lock.id}', 'Lock Closed')
        nextion_display.set_page(0)

    # Get last lock stotus of the lock and send it to the clients
    data = DataRepository.get_locker_lock_status(lock.id)
    socketio.emit('F2B_locker_lock_status', json.dumps({'lock': data}, default=DataRepository.default_serializer))


# endregion
# region Functions


# Get IP Adresses By Port
def get_ip_addresses(port):
    try:
        return str(check_output(['ifconfig', port])).split('inet ')[1].split(' ')[0]
    except:
        return "Not connected"


def verify_credentials(order_id, code):
    locker_keys = []
    
    if order_id != '' and code != '':
        for locker_id in locks.keys():
            
            locker_credentials = DataRepository.get_locker_credentials(locker_id)
            if order_id == locker_credentials['orderid'] and code == locker_credentials['code']:
                locker_keys.append(locker_id)
    
    return locker_keys


# endregion
# region Main hardware


# Init classes of devices
temperature_sensor = TemperatureSensor(temperature_sensor_w1_id)
detector = Detector(pin_detector, callback_detector)
lcd_display = LcdDisplay(pin_lcd_rs, pin_lcd_e, pins_lcd_data)  
nextion_display = NextionDisplay(nextion_display_port, nextion_display_baud)
locks = {
    1: Lock(1, pin_lock_1, pin_lock_1_feedback, callback_lock_feedback),
    2: Lock(2, pin_lock_2, pin_lock_2_feedback, callback_lock_feedback)
}


# Main hardware loop
def main_loop_hardware():
    print('*** Main hardware thread started ***')
    
    try:
        while True:
            nextion_display_input = nextion_display.read()
           
            if nextion_display_input:
                nextion_display_input_arr = nextion_display_input.split(' ')

                # Client has inserted the orderid
                if nextion_display_input_arr[0] == 'bnr_ok':
                    
                    if nextion_display_input_arr[1] != '':
                        order_id = int(nextion_display_input_arr[1])
                    else:
                        order_id = ''

                # Client has inserted the code
                if nextion_display_input_arr[0] == 'code_ok':
                    
                    if nextion_display_input_arr[1] != '':
                        code = int(nextion_display_input_arr[1])
                    else:
                        code = ''

                    # Verify locker credentials
                    locker_keys = verify_credentials(order_id, code)
                    if locker_keys != []:
                        print(f'Credentials correct: {order_id} {code}')
                        nextion_display.set_page(3)
                        for locker_key in locker_keys:
                            print(f'Opening locker {locker_key}')
                            locks[locker_key].open()
                            DataRepository.update_locker_status(locker_key, 3)
                    else:
                        print(f'Credentials incorrect: {order_id} {code}')
                        nextion_display.set_page(4)
    
    except KeyboardInterrupt as ex:
        pass


# endregion
# endregion


# region Flask Code

# region Threads

def measure_temperature():
    global temperature_sensor_alert_last_send
    print('*** Measure temperature thread started ***')

    while True:
        time.sleep(60)
        current_temperature = temperature_sensor.temperature
        DataRepository.add_history_action('Temperature Sensor', 'Temperature Measurement', current_temperature)
        socketio.emit('B2F_current_temperature', {'temperature': current_temperature})

        if datetime.datetime.now() - temperature_sensor_alert_last_send > alert_interval:
            if current_temperature > temperature_sensor_max:
                smtp_client.send_mail(alert_email, 'Temperatuur te hoog!', f'Huidige temperatuur in de locker is {current_temperature} °C.')
                temperature_sensor_alert_last_send = datetime.datetime.now()
            elif current_temperature < temperature_sensor_min: 
                smtp_client.send_mail(alert_email, 'Temperatuur te laag!', f'Huidige temperatuur in de locker is {current_temperature} °C.')
                temperature_sensor_alert_last_send = datetime.datetime.now()


def display_ip_addresses():
    print('*** Display ip-addresses thread started ***')

    while True:
        eth0 = get_ip_addresses('eth0').rjust(15, ' ')
        wlan0 = get_ip_addresses('wlan0').rjust(15, ' ')
        
        lcd_display.set_cursor_position(0, 0)
        lcd_display.write_message("L{0}".format(eth0)+"W{0}".format(wlan0))

        if wlan0 != 'Not connected  ':
            nextion_display.set_text('ip', wlan0)
        elif eth0 != 'Not connected  ':
            nextion_display.set_text('ip', eth0)

        time.sleep(60)

# endregion

# region API endpoints


# Root endpoint
@app.route('/')
def root_endpoint():
    return "Server is running."


# Shutdown
@app.route(api_endpoint + '/shutdown', methods=['POST'])
@jwt_required()
def shutdown():
    print('Shutdown Raspberry Pi')
    os.system("shutdown")
    return jsonify(message="Raspberry Pi is shutting down."), 200


# Authentication
@app.route(api_endpoint + '/login', methods=['POST'])
def login():
    form_data = DataRepository.json_or_formdata(request)
    username = form_data['username']
    password = form_data['password']
    
    user = DataRepository.get_user(form_data['username'])
    if user is not None:

        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), user['salt'], 100000)
        if user['password'] == new_key:
            print(f'User logged in: {username}')
            expires = datetime.timedelta(hours=1)
            access_token = create_access_token(identity=username, expires_delta=expires)
            return jsonify(access_token=access_token), 200

    return jsonify(message="Username and/or password are incorrect"), 401

@app.route(api_endpoint + '/users/validate', methods=['GET'])
@jwt_required()
def validate():
    current_user = get_jwt_identity()
    return jsonify(username=current_user), 200


# History data endpoints
@app.route(api_endpoint + '/history/temperature', methods=['GET'])
@jwt_required()
def temperature_history():

    if request.method == 'GET':
        data = DataRepository.get_history_temperature(5000)
        if data is not None:
            return jsonify(history=data), 200
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/history/detection', methods=['GET'])
@jwt_required()
def detection_history():

    if request.method == 'GET':
        data = DataRepository.get_history_detection(500)
        if data is not None:
            return jsonify(history=data), 200
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/history/locks', methods=['GET'])
@jwt_required()
def locks_history():

    if request.method == 'GET':
        data = DataRepository.get_history_locks(500)
        if data is not None:
            return jsonify(history=data), 200
        else:
            return jsonify(response='error'), 404


# Locker endpoins
@app.route(api_endpoint + '/lockers', methods=['GET'])
@jwt_required()
def lockers():

    if request.method == 'GET':
        data = DataRepository.get_lockers()
        if data is not None:
            return jsonify(lockers=data), 200
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/lockers/<id>', methods=['GET'])
@jwt_required()
def locker(id):

    if request.method == 'GET':
        data = DataRepository.get_locker_details(id)
        if data is not None:
            return jsonify(locker=data), 200
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/lockers/<id>/code', methods=['GET', 'PUT'])
@jwt_required()
def locker_code(id):

    if request.method == 'GET':
        data = DataRepository.get_locker_credentials(id)
        if data is not None:
            return jsonify(credentials=data), 200
        else:
            return jsonify(response='error'), 404

    if request.method == 'PUT':
        form_data = DataRepository.json_or_formdata(request)

        code = form_data['code']

        res = DataRepository.update_locker_code(id, code)
        if res is not None:
            return jsonify(response=res), 201
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/lockers/<id>/status', methods=['GET', 'PUT'])
@jwt_required()
def locker_status(id):

    if request.method == 'GET':
        data = DataRepository.get_locker_status(id)
        if data is not None:
            return jsonify(status=data), 200
        else:
            return jsonify(response='error'), 404

    if request.method == 'PUT':
        form_data = DataRepository.json_or_formdata(request)

        status = form_data['status']

        res = DataRepository.update_locker_status(id, status)
        if res is not None:
            return jsonify(response=res), 201
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/lockers/<id>/order', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def locker_order(id):
    
    if request.method == 'GET':
        data = DataRepository.get_locker_order(id)
        if data is not None:
            return jsonify(order=data), 200
        else:
            return jsonify(response='error'), 404

    if request.method == 'PUT':
        form_data = DataRepository.json_or_formdata(request)
        
        orderid = form_data['orderid']
        name = None if form_data['name'] == '' else form_data['name']
        email = None if form_data['email'] == '' else form_data['email']
        tel = None if form_data['tel'] == '' else form_data['tel']
        description = None if form_data['description'] == '' else form_data['description']

        res_update_order = DataRepository.update_or_insert_order(orderid, name, email, tel, description)
        res_update_locker = DataRepository.update_locker_order(id, orderid, 2)

        if res_update_locker is not None and res_update_order is not None:
            return jsonify(response_update_locker=res_update_locker, response_update_order=res_update_order), 201
        else:
            return jsonify(response='error'), 404

    if request.method == 'DELETE':
        res = DataRepository.delete_locker_order(id)
        if res is not None:
            return jsonify(response=res), 200
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/lockers/<id>/lock/open', methods=['POST'])
@jwt_required()
def open_locker(id):
    
    if request.method == 'POST':
        locks[int(id)].open()
        return jsonify(response='Lock opened')

@app.route(api_endpoint + '/lockers/statuses', methods=['GET'])
@jwt_required()
def locker_statuses():

    if request.method == 'GET':
        data = DataRepository.get_locker_statuses()
        if data is not None:
            return jsonify(statuses=data), 200
        else:
            return jsonify(response='error'), 404

@app.route(api_endpoint + '/orders/<id>', methods=['GET'])
@jwt_required()
def order(id):

    if request.method == 'GET':
        data = DataRepository.get_order(id)
        if data is not None:
            return jsonify(order=data), 200
        else:
            return jsonify(response='error'), 404


# Socket IO
@socketio.on_error()        
def error_handler(e):
    print(e)

@socketio.on('connect')
def initial_connection():
    print('A new client connect')

@socketio.on('F2B_current_temperature')
def current_temperature():
    emit('B2F_current_temperature', {'temperature': temperature_sensor.temperature})

@socketio.on('F2B_last_detection')
def last_detection():
    data = DataRepository.get_last_detection()
    emit('B2F_last_detection', json.dumps({'lastDetection': DataRepository.get_last_detection()}, default=DataRepository.default_serializer))

@socketio.on('F2B_locker_lock_status')
def locker_lock_status(id):
    data = DataRepository.get_locker_lock_status(id)
    emit('F2B_locker_lock_status', json.dumps({'lock': data}, default=DataRepository.default_serializer))

@socketio.on('F2B_locker_open_lock')
def locker_lock_open(locker_id):
    locks[int(locker_id)].open()


# endregion
# endregion


if __name__ == '__main__':
    try: 
        
        # Start main hardware thread
        main_hardware_thread = threading.Thread(target=main_loop_hardware, daemon=True)
        main_hardware_thread.start()

        # Start display ip addresses thread
        display_ip_addresses_thread = threading.Thread(target=display_ip_addresses, daemon=True)
        display_ip_addresses_thread.start()  

        # Start measure temperature thread
        measure_temperature_thread = threading.Thread(target=measure_temperature, daemon=True)
        measure_temperature_thread.start()  

        # Start socketio
        print("**** Program started ****")
        socketio.run(app, debug=False, host='0.0.0.0')
    
    except KeyboardInterrupt as ex:
        pass

    finally:
        [locks[lock].close() for lock in locks]
        detector.close()
        lcd_display.close()
        nextion_display.close()
        print('Program ended')

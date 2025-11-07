from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'status': True,
        'message': 'Vehicle API is running!',
        'usage': 'GET /api?vehicle_no=UP61S6030'
    })

@app.route('/api', methods=['GET', 'POST'])
def vehicle_api():
    # Get vehicle number
    if request.method == 'POST':
        vehicle_no = request.form.get('vehicle_no') or (request.json.get('vehicle_no') if request.is_json else None)
    else:
        vehicle_no = request.args.get('vehicle_no')
    
    if not vehicle_no:
        return jsonify({'status': False, 'error': 'vehicle_no required'}), 400
    
    # Call GTPlay API
    url = "https://gtplay.in/API/vehicle_challan_info/testapi.php"
    data = f'vehicle_no={vehicle_no}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'okhttp/5.1.0',
        'Accept-Encoding': 'gzip',
        'Content-Length': str(len(data)),
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('status') == True:
            return jsonify({
                'status': True,
                'message': 'Success',
                'data': result.get('data', {})
            })
        else:
            return jsonify({
                'status': False,
                'message': result.get('error', 'Not found')
            }), 404
            
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment (Render automatically sets this)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

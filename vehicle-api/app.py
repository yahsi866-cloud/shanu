from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Home page with HTML form
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚗 Vehicle Challan Checker</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px; 
                background: #f5f5f5;
            }
            .container { 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            input, button { 
                padding: 12px; 
                margin: 10px 0; 
                width: 100%; 
                border: 1px solid #ddd; 
                border-radius: 5px; 
                font-size: 16px;
            }
            button { 
                background: #007bff; 
                color: white; 
                border: none; 
                cursor: pointer; 
                font-weight: bold;
            }
            button:hover { background: #0056b3; }
            .result { 
                margin-top: 20px; 
                padding: 15px; 
                border-radius: 5px; 
                background: #f8f9fa; 
                display: none;
            }
            .success { background: #d4edda; border: 1px solid #c3e6cb; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; }
            .loading { display: none; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Vehicle Challan Checker</h1>
            <p>Enter your vehicle number to check details</p>
            
            <input type="text" id="vehicleInput" placeholder="e.g., UP61S6030" required>
            <button onclick="checkVehicle()">Check Vehicle Details</button>
            
            <div id="loading" class="loading">
                <p>🔍 Searching... Please wait</p>
            </div>
            
            <div id="result" class="result"></div>
        </div>

        <script>
            async function checkVehicle() {
                const vehicleNo = document.getElementById('vehicleInput').value.trim();
                const resultDiv = document.getElementById('result');
                const loadingDiv = document.getElementById('loading');
                
                if (!vehicleNo) {
                    alert('Please enter vehicle number');
                    return;
                }
                
                // Show loading
                loadingDiv.style.display = 'block';
                resultDiv.style.display = 'none';
                
                try {
                    const response = await fetch('/api/check-vehicle', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ vehicle_no: vehicleNo })
                    });
                    
                    const data = await response.json();
                    
                    // Hide loading
                    loadingDiv.style.display = 'none';
                    resultDiv.style.display = 'block';
                    
                    if (data.status === true) {
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = formatSuccessResponse(data.data);
                    } else {
                        resultDiv.className = 'result error';
                        resultDiv.innerHTML = `<strong>❌ Error:</strong> ${data.message || 'Vehicle not found'}`;
                    }
                    
                } catch (error) {
                    loadingDiv.style.display = 'none';
                    resultDiv.style.display = 'block';
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `<strong>🔴 Network Error:</strong> ${error.message}`;
                }
            }
            
            function formatSuccessResponse(data) {
                return `
                    <h3>✅ Vehicle Found!</h3>
                    <p><strong>🚗 Vehicle:</strong> ${data.maker_model || 'N/A'}</p>
                    <p><strong>📝 Number:</strong> ${data.registration_no || 'N/A'}</p>
                    <p><strong>👤 Owner:</strong> ${data.owner_name || 'N/A'}</p>
                    <p><strong>🏛️ Authority:</strong> ${data.registration_authority || 'N/A'}</p>
                    <p><strong>⛽ Fuel:</strong> ${data.fuel_type || 'N/A'}</p>
                    <p><strong>🎨 Color:</strong> ${data.vehicle_color || 'N/A'}</p>
                    <p><strong>📅 Registration:</strong> ${data.registration_date || 'N/A'}</p>
                    <p><strong>✅ RC Status:</strong> ${data.rc_status || 'N/A'}</p>
                    <p><strong>🛡️ Insurance Upto:</strong> ${data.insurance_upto || 'N/A'}</p>
                    <p><strong>🏥 Fitness Upto:</strong> ${data.fitness_upto || 'N/A'}</p>
                `;
            }
            
            // Enter key support
            document.getElementById('vehicleInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    checkVehicle();
                }
            });
        </script>
    </body>
    </html>
    '''

# API endpoint
@app.route('/api/check-vehicle', methods=['POST'])
def check_vehicle():
    try:
        data = request.json
        vehicle_no = data.get('vehicle_no', '').strip().upper()
        
        if not vehicle_no:
            return jsonify({
                'status': False,
                'message': 'Vehicle number is required'
            })
        
        # GTPlay API call
        url = "https://gtplay.in/API/vehicle_challan_info/testapi.php"
        form_data = f'vehicle_no={vehicle_no}'
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'okhttp/5.1.0',
            'Accept-Encoding': 'gzip',
            'Content-Length': str(len(form_data)),
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }
        
        response = requests.post(url, data=form_data, headers=headers, timeout=10)
        api_result = response.json()
        
        return jsonify(api_result)
        
    except requests.exceptions.Timeout:
        return jsonify({
            'status': False,
            'message': 'API request timeout'
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': False,
            'message': f'Network error: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f'Server error: {str(e)}'
        })

# Health check endpoint for Render
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

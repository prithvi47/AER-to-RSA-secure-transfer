import os
import shutil
import multiprocessing
import time
from stem.control import Controller
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Create templates directory if it doesn't exist
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Create basic HTML templates
with open(os.path.join(TEMPLATES_DIR, 'index.html'), 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>File Download</title>
</head>
<body>
    <h1>File Download</h1>
    <p>Filename: {{ filename }}</p>
    <p>Size: {{ filesize }} bytes</p>
    <a href="/download">Download File</a>
</body>
</html>
''')

with open(os.path.join(TEMPLATES_DIR, '404.html'), 'w') as f:
    f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>404 - Not Found</title>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The requested page could not be found.</p>
</body>
</html>
''')

@app.route('/')
def index():
    filename = app.config.get("FILE_NAME", "unknown")
    filesize = app.config.get("FILE_SIZE", 0)
    return render_template("index.html", filename=filename, filesize=filesize)

@app.route('/download')
def download():
    file_dir = app.config.get("FILE_DIR", "")
    file_name = app.config.get("FILE_NAME", "")
    
    if not file_dir or not file_name:
        return "File not configured", 404
        
    return send_from_directory(file_dir, file_name, as_attachment=True)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

class TorShare:
    def __init__(self):
        self.controller = None
        self.control_ports = [9051, 9151]
        self.hostname = None
        self.hidden_service_dir = None
        self.app_process = None

    def connect(self):
        for controlport in self.control_ports:
            try:
                self.controller = Controller.from_port(port=controlport)
                print(f"Connected to Tor controller on port {controlport}")
                return True
            except Exception as e:
                print(f"Failed to connect to port {controlport}: {e}")
        return False

    def authenticate(self):
        try:
            self.controller.authenticate()
            print("Authenticated with Tor controller")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def is_connected(self):
        return self.controller is not None

    def create_service(self, filepath):
        if not os.path.exists(filepath):
            print(f"File does not exist: {filepath}")
            return False
            
        try:
            # Create hidden service directory
            self.hidden_service_dir = os.path.join(os.getcwd(), 'hidden_service')
            os.makedirs(self.hidden_service_dir, exist_ok=True)
            
            # Create hidden service
            result = self.controller.create_ephemeral_hidden_service({80: 5000})
            self.hostname = result.service_id + '.onion'
            
            self._set_file_config(filepath)
            
            # Start Flask app in a separate process
            self.app_process = multiprocessing.Process(
                target=app.run, 
                kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False}
            )
            self.app_process.daemon = True
            self.app_process.start()
            
            print(f"Hidden service created: {self.hostname}")
            print(f"Serving file: {filepath}")
            return True
            
        except Exception as e:
            print(f"Failed to create hidden service: {e}")
            return False

    def stop_service(self):
        if self.controller:
            try:
                self.controller.remove_ephemeral_hidden_service(self.hostname.replace('.onion', ''))
                print("Hidden service stopped")
            except:
                pass
            self.controller.close()
        
        if self.app_process and self.app_process.is_alive():
            self.app_process.terminate()
            self.app_process.join()

    def _set_file_config(self, filepath):
        app.config["FILE_DIR"] = os.path.dirname(filepath) or os.getcwd()
        app.config["FILE_NAME"] = os.path.basename(filepath)
        app.config["FILE_SIZE"] = os.path.getsize(filepath)

if __name__ == '__main__':
    # Test the Flask app directly
    app.config["FILE_DIR"] = os.getcwd()
    app.config["FILE_NAME"] = "test.txt"
    app.config["FILE_SIZE"] = 100
    app.run(host='127.0.0.1', port=5000, debug=True)
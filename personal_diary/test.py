from flask import Flask; app = Flask(__name__); @app.route('/'); def hello(): return 'OK'; app.run(debug=True)

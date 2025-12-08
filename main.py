import os 
from src import create_app
from src.config.dev_config import DevConfig
from flask_cors import CORS, cross_origin


app = create_app()
dev_config = DevConfig()
CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {
        "origins": [
            "https://seapptaskmanagementclient.vercel.app",
            "http://localhost:5173",
            "https://seapptaskmanagementclient.vercel.app/",
            "http://localhost:5173/",
        ]
    }}
)

url = 'http://localhost:' + str(dev_config.PORT) 


@app.route('/my-testing') 
def index():
    return {
        "success": True , 
        "message": "Testing thanh cong"
    }

if __name__ == '__main__': 
    port = int(os.environ.get('port')) 
    app.run(port = port , host='0.0.0.0')
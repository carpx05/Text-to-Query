from src import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host=Config.FLASK_HOST, port=5000)
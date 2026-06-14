import webbrowser
import threading
from app import create_app

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    app = create_app()
    threading.Timer(1.2, open_browser).start()
    print("\n🚀 CodeLife is starting...")
    print("📡 Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=False, port=5000)

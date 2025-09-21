from backend.app import create_app

app = create_app()

@app.route('/')
def home():
    return "Reservia - Resource Reservation Management System"

if __name__ == '__main__':
    app.run(debug=True)
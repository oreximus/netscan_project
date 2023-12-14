from flask import Flask, render_template

# Create a Flask application
app = Flask(__name__)


# landing page and aurthintication 
@app.route('/')
def index():
    return render_template("index.html")


# Run the Flask app if this script is the main program
if __name__ == '__main__':
    app.run()


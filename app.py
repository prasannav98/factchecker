from flask import Flask, render_template, request
import fact_checking
import wikipedia_pages
from fuzzywuzzy import fuzz
from fact_checking import compute_confidence_score


# Initialize the Flask app
app = Flask(__name__)

# Flask route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    print("Route accessed")  # Add this to verify route is accessed
    if request.method == 'POST':
        print("Form submitted")  # Add this to verify form submission
        claim = request.form['claim']
        print(f"Claim received: {claim}")  # Check if claim is received correctly
        claim = request.form['claim']
        output = fact_checking.fact_check_system(claim)
        
        return render_template('index.html', result=output)
    
    return render_template('index.html', result=None)


# Run the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

from flask import Flask, render_template, request
import pandas as pd
import json
import re
from rapidfuzz import process

app = Flask(__name__)

# Load and clean dataset
df = pd.read_csv("blue_papers.csv")
df = df[['STATE', 'YEAR', 'MAKE', 'MODEL', 'MODEL_NUMBER', 'LENGTH', 'AVERAGE_PRICE']].dropna()
rv_data = df.to_dict(orient='records')
states = sorted(df['STATE'].unique())

# City-to-state mapping for travel goal detection
city_to_state = {
    "new orleans": "louisiana", "baton rouge": "louisiana", "houston": "texas", "austin": "texas",
    "dallas": "texas", "phoenix": "arizona", "chicago": "illinois", "los angeles": "california",
    "san diego": "california", "orlando": "florida", "miami": "florida", "seattle": "washington",
    "denver": "colorado", "atlanta": "georgia", "nashville": "tennessee", "boston": "massachusetts",
    "minneapolis": "minnesota", "charlotte": "north carolina", "philadelphia": "pennsylvania",
    "portland": "oregon", "columbus": "ohio", "detroit": "michigan", "kansas city": "missouri",
    "san antonio": "texas", "san jose": "california", "jacksonville": "florida", "el paso": "texas",
    "fort worth": "texas", "memphis": "tennessee", "oklahoma city": "oklahoma", "milwaukee": "wisconsin"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    ai_results = []
    ai_explanation = ""

    if request.method == 'POST' and 'search_submit' in request.form:
        query = request.form['query'].lower()
        matched_rvs = rv_data
        max_price = None
        state_match = None

        # Match based on full state name
        state_match = next((state for state in states if state.lower() in query), None)

        # Fuzzy match city to infer state
        if not state_match:
            result = process.extractOne(query, city_to_state.keys(), score_cutoff=80)
            if result:
                best_city, _, _ = result
                state_match = city_to_state[best_city].title()

        # Fuzzy match state if city didn’t work
        if not state_match:
            best_state, score, _ = process.extractOne(query, [s.lower() for s in states], score_cutoff=80)
            if best_state:
                state_match = next((s for s in states if s.lower() == best_state), None)

        if state_match:
            matched_rvs = [rv for rv in matched_rvs if rv['STATE'].lower() == state_match.lower()]

        # Try to find price in query
        price_match = re.search(r'\$?(\d{2,3},?\d{3})', query)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            if price_str.isdigit():
                max_price = int(price_str)
                matched_rvs = [rv for rv in matched_rvs if int(rv['AVERAGE_PRICE']) <= max_price]

        # Sort matches by price ascending
        matched_rvs = sorted(matched_rvs, key=lambda x: int(x['AVERAGE_PRICE']))

        if matched_rvs:
            ai_results = matched_rvs
            ai_explanation = f"Here are some great RVs we found {f'in {state_match}' if state_match else ''}{f' under ${max_price:,}' if max_price else ''}."
        else:
            ai_explanation = "Sorry, we couldn't find any RVs that match your travel goals."

    return render_template('index.html', ai_results=ai_results, ai_explanation=ai_explanation)

if __name__ == '__main__':
    app.run(debug=True)

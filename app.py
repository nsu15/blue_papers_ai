from flask import Flask, render_template, request
import pandas as pd
import json
import re
from rapidfuzz import process
<<<<<<< HEAD

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
=======
import smtplib
from email.mime.text import MIMEText
 

app = Flask(__name__) 

# Load and clean the dataset
df = pd.read_csv("blue_papers.csv")
df = df[['STATE', 'YEAR', 'MAKE', 'MODEL', 'MODEL_NUMBER', 'LENGTH', 'AVERAGE_PRICE']].dropna()

# Convert the dataset to a list of dictionaries
rv_data = df.to_dict(orient='records')

# Create unique sorted dropdown options
states = sorted(df['STATE'].unique())
years = sorted(df['YEAR'].unique(), reverse=True)
prices = sorted(df['AVERAGE_PRICE'].dropna().unique().astype(int).tolist())

# City-to-state mapping
city_to_state = {
    "new orleans": "louisiana", "baton rouge": "louisiana", "houston": "texas", "austin": "texas", 
    "dallas": "texas", "phoenix": "arizona", "chicago": "illinois", "los angeles": "california", 
    "san diego": "california", "orlando": "florida", "miami": "florida", "seattle": "washington", 
>>>>>>> b04ef9d2edd5037f5eae2a22f96d3b7385caa8dc
    "denver": "colorado", "atlanta": "georgia", "nashville": "tennessee", "boston": "massachusetts",
    "minneapolis": "minnesota", "charlotte": "north carolina", "philadelphia": "pennsylvania",
    "portland": "oregon", "columbus": "ohio", "detroit": "michigan", "kansas city": "missouri",
    "san antonio": "texas", "san jose": "california", "jacksonville": "florida", "el paso": "texas",
    "fort worth": "texas", "memphis": "tennessee", "oklahoma city": "oklahoma", "milwaukee": "wisconsin"
}
<<<<<<< HEAD

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
=======
def send_feedback_email(feedback_text):
    sender_email = "theedetdatacompany@gmail.com"
    sender_password = "xczvrzavowzaleyb"  # Use Gmail App Password, not your main password
    recipient_email = "theedetdatacompany@gmail.com"
    
    subject = "New Feedback from The Blue Papers"
    body = f"User feedback:\n\n{feedback_text}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("✅ Feedback email sent successfully.")
    except Exception as e:
        print("❌ Failed to send feedback email:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    estimate_results = None
    chat_history = []
    feedback_message = ""
    query = ""
    selected_state = selected_year = selected_price = None

    if request.method == 'POST':
        if 'estimate_submit' in request.form:
            selected_state = request.form.get('state')
            selected_year = request.form.get('year')
            selected_price = request.form.get('price_range')

            filtered_rvs = rv_data

            if selected_state:
                filtered_rvs = [rv for rv in filtered_rvs if rv['STATE'] == selected_state]

            if selected_year and selected_year.isdigit():
                filtered_rvs = [rv for rv in filtered_rvs if int(rv['YEAR']) == int(selected_year)]

            if selected_price and selected_price.isdigit():
                filtered_rvs = [rv for rv in filtered_rvs if int(rv['AVERAGE_PRICE']) <= int(selected_price)]

            estimate_results = sorted(filtered_rvs, key=lambda x: int(x['AVERAGE_PRICE']), reverse=True)

        elif 'search_submit' in request.form:
            query = request.form['query'].lower()
            matched_rvs = rv_data
            max_price = None
            state_match = None

            # Try exact state match
            state_match = next((state for state in states if state.lower() in query), None)

            # Fuzzy match city to find state if state not found
            if not state_match:
                city_names = list(city_to_state.keys())
                best_city, score, _ = process.extractOne(query, city_names, score_cutoff=80)
                if best_city:
                    state_match = city_to_state[best_city].title()

            # If still no match, fuzzy match the state name itself
            if not state_match:
                best_state, score, _ = process.extractOne(query, [s.lower() for s in states], score_cutoff=80)
                if best_state:
                    for s in states:
                        if s.lower() == best_state:
                            state_match = s
                            break

            # Filter RVs by matched state
            if state_match:
                matched_rvs = [rv for rv in matched_rvs if rv['STATE'].lower() == state_match.lower()]

            # Extract price using regex
            price_match = re.search(r'\$?(\d{2,3},?\d{3})', query)
            if price_match:
                price_str = price_match.group(1).replace(',', '')
                if price_str.isdigit():
                    max_price = int(price_str)
                    matched_rvs = [rv for rv in matched_rvs if int(rv['AVERAGE_PRICE']) <= max_price]

            # Sort by price ascending
            matched_rvs = sorted(matched_rvs, key=lambda x: int(x['AVERAGE_PRICE']))

            if matched_rvs:
                ai_results = matched_rvs
                ai_explanation = f"Here are some great RVs we found {f'in {state_match}' if state_match else ''}{f' under ${max_price:,}' if max_price else ''}."
            else:
                ai_results = []
                ai_explanation = "Sorry, we couldn't find any RVs that match your travel goals."

            chat_history = [
                type('Message', (), {"role": "user", "content": query}),
            ]

        elif 'feedback_submit' in request.form:
            feedback = request.form['feedback']
            print("User Feedback:", feedback)
            send_feedback_email(feedback)  # Send email when feedback is submitted   
            feedback_message = "We appreciate your input!"
        else:
            print("No recognized submit button found.")
        
    return render_template('index.html',
                       states=states,
                       years=years,
                       prices=prices,
                       estimate_results=estimate_results,
                       chat_history=chat_history,
                       feedback_message=feedback_message,
                       query=query,
                       selected_state=selected_state,
                       selected_year=selected_year,
                       selected_price=selected_price,
                       ai_results=ai_results if 'ai_results' in locals() else [],
                       ai_explanation=ai_explanation if 'ai_explanation' in locals() else "",
                       rv_data=json.dumps(rv_data))

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)


>>>>>>> b04ef9d2edd5037f5eae2a22f96d3b7385caa8dc

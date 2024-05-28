from flask import Flask, render_template, request, jsonify
import requests
import logging

app = Flask(__name__, static_url_path='/static')
logging.basicConfig(level=logging.DEBUG)

API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=AIzaSyBt_UKi-gC5PM9VsIZ0TjoJMAVKsYM0KVU"

DEFAULT_TEXT = "Please generate the complete code with syntax."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form['search_query']
    if search_query:
        response = generate_story(DEFAULT_TEXT + search_query)  
        logging.debug(f"API response: {response}")
        if response and 'candidates' in response:
            story_content, safety_ratings = extract_story_and_safety(response)
            if story_content:
                if is_safe_content(safety_ratings):
                    story_content = story_content.replace('*', "")  
                    return jsonify(success=True, code_suggestion=story_content)
                else:
                    error_msg = "Failed to generate code due to safety concerns. Please try again with a different query."
                    return jsonify(success=False, error=error_msg)
        error_msg = "Failed to generate code. Please try again."
        return jsonify(success=False, error=error_msg)
    else:
        error_msg = "Please enter a valid prompt."
        return jsonify(success=False, error=error_msg)

def generate_story(prompt):
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def extract_story_and_safety(response):
    candidates = response.get('candidates', [])
    if candidates:
        candidate = candidates[0]
        content = candidate.get('content', {}).get('parts', [])
        if content:
            story_content = content[0].get('text', '')
        else:
            story_content = None
        safety_ratings = candidate.get('safetyRatings', [])
        return story_content, safety_ratings
    return None, None

def is_safe_content(safety_ratings):
    for rating in safety_ratings:
        if rating['probability'] == 'HIGH':
            return False
    return True

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
from medical_ai import ask_questions

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.remote_addr
    user_message = request.json.get('message', '').strip()

    if not user_message:
        return jsonify({'response': "Please describe your symptoms clearly."})

    response = ask_questions(user_id, user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)

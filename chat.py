import openai
import os
from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": ["https://animechatbot.pythonanywhere.com/"]}})
limiter = Limiter(get_remote_address, app=app,  default_limits=["10 per minute"])


openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
@limiter.limit("10 per minute")  # Customize the rate limit as needed
def ask():
    user_input = request.form['user_input']
    conversation_history = request.form['conversation_history']

    if not user_input or not conversation_history:
        abort(400, "Invalid input")
    

    # Provide context and desired behavior to the chatbot
    chatbot_instructions = (
        "Your name is Luffy. You will talk and act like Luffy. Ask follow up question to the user about themselves if appropriate. Try to end a sentence with an action. Your laugh is Shishishi. You are the embodiment of Luffy from One Piece. "
    )

    # Convert conversation_history to a list of messages
    conversation_lines = conversation_history.strip().split('\n')
    messages = [{"role": "system", "content": chatbot_instructions}]

    for line in conversation_lines:
        role, content = line.split(': ', 1)
        if role.lower() == "ai":
            role = "assistant"
        messages.append({"role": role.lower(), "content": content})

    # Add the current user input to the messages
    messages.append({"role": "user", "content": user_input})


    # Interact with the GPT-3.5 Turbo API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    ai_reply = response['choices'][0]['message']['content'].strip()
    return jsonify({'ai_reply': ai_reply})

if __name__ == '__main__':
    app.run(debug=True)

from flask import (
    Flask,
    render_template,
    request,
    Response,
    stream_with_context,
    jsonify,
    session,
    redirect,
    url_for,
    make_response
)
import openai
import os
import secrets
import requests

from config import OPENAI_API_KEY

# Configure OpenAI key for downstream calls
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Retrieval API base URL (FastAPI service)
RETRIEVAL_API_URL = os.environ.get("RETRIEVAL_API_URL", "http://127.0.0.1:8001")

GENERATIVE_MODEL = "gpt-4o-mini"

client = openai.OpenAI()

app = Flask(__name__)



sys_prompt = f"""
    You are a concise, faithful, and thoughtful latter-day saint. Your job is to answer your friend's question by quoting from the list of scriptures provided. 

    Use some of the scriptures to support your thinking, but you don't have to quote from all of them. You should use two short paragraphs to synthesize what is shared in the verses. and help your friend understand the answer to their question.
    
    """

chat_history = [
    {"role": "system", "content": sys_prompt},
]

def check_retrieval_health_or_fail():
    try:
        resp = requests.get(f"{RETRIEVAL_API_URL}/health", timeout=5)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Retrieval API unavailable at {RETRIEVAL_API_URL}") from e

check_retrieval_health_or_fail()

def fetch_scriptures(question: str, model: str) -> str:
    """Call the FastAPI retrieval service to get scriptures string."""
    try:
        resp = requests.post(
            f"{RETRIEVAL_API_URL}/retrieve",
            json={"question": question, "generative_model": model},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("scriptures_string", "")
    except Exception as e:
        app.logger.exception("Error calling retrieval API: %s", e)
        return ""

def get_unique_id(response):
    unique_id = request.cookies.get('user_id')
    if not unique_id:
        unique_id = secrets.token_hex()
        response.set_cookie('user_id', unique_id)
    return unique_id

def get_chat_history(unique_id):
    if 'chat_histories' not in app.config:
        app.config['chat_histories'] = {}
    if unique_id not in app.config['chat_histories']:
        app.config['chat_histories'][unique_id] = [{"role": "system", "content": sys_prompt}]
    return app.config['chat_histories'][unique_id]

def set_chat_history(unique_id, chat_history):
    app.config['chat_histories'][unique_id] = chat_history


@app.route("/", methods=["GET"])
def index():
    response = make_response(render_template("index.html"))
    unique_id = get_unique_id(response)
    chat_history = get_chat_history(unique_id)
    return response


@app.route("/chat", methods=["POST"])
def chat():
    unique_id = request.cookies.get('user_id')
    if not unique_id:
        return jsonify(success=False, message="User not identified")
    chat_history = get_chat_history(unique_id)
    question = request.json["message"]
    chat_history.append({"role": "user", "content": question})
    scriptures_string = fetch_scriptures(question, GENERATIVE_MODEL)
    assistant_content = "Here are some scriptures that may be helpful:\n" + scriptures_string
    chat_history.append({"role": "assistant", "content": assistant_content})
    set_chat_history(unique_id, chat_history)
    
    
    return jsonify(success=True)


@app.route("/stream", methods=["GET"])
def stream():
    def generate():
        unique_id = request.cookies.get('user_id')
        if not unique_id:
            return jsonify(success=False, message="User not identified")
        chat_history = get_chat_history(unique_id)
        assistant_response_content = ""
        
        prev_content = chat_history[-1]['content'].replace("\n", "<br>")

        
        yield f"data: {prev_content}\n\n"

        with client.chat.completions.create(
            model=GENERATIVE_MODEL,
            messages=chat_history,
            stream=True,
        ) as stream:
            for chunk in stream:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    # Accumulate the content only if it's not None
                    assistant_response_content += chunk.choices[0].delta.content
                    data_to_add = chunk.choices[0].delta.content.replace("\n", "<br>")
                    yield f"data: {data_to_add}\n\n"
                if chunk.choices[0].finish_reason == "stop":
                    break  # Stop if the finish reason is 'stop'

        # Once the loop is done, append the full message to chat_history
        chat_history.append(
            {"role": "assistant", "content": assistant_response_content}
        )
        set_chat_history(unique_id, chat_history)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/reset", methods=["POST"])
def reset_chat():
    unique_id = request.cookies.get('user_id')
    if not unique_id:
        return jsonify(success=False, message="User not identified")
    _ = get_chat_history(unique_id)
    return jsonify(success=True)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('chat_history', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return redirect(url_for('index'))

if __name__ == "__main__":

   app.secret_key = secrets.token_hex()
   app.run(host='0.0.0.0', port=5000)

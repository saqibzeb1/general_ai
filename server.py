from flask import Flask, render_template, request, jsonify
import threading
import google.generativeai as genai
import time
import os

def start():
    
    print ('--- INITIALIZING MODEL ---')
    
    KEY = "AIzaSyD8s8NqDu8ZJ6SvY9x2uwrF3EIWqFrSATs" 
    pdf_file = "info.pdf" 
    name = "info.pdf"

    genai.configure(api_key=KEY)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        system_instruction=[
            "You are a helpful transcriber that can accurately transcribe text from images and PDFs.",
            "Your mission is to transcribe text from the provided PDF, image or any other kind of files",
        ],
    )

    return model

def processFile(path_input): 
    uploaded_file = genai.upload_file(path=path_input)
    print (uploaded_file)

    pdfFile = genai.get_file(uploaded_file.name)
    print(f"File URI: {pdfFile.uri}")

    return pdfFile


def processFile(path_input):
    uploaded_file = genai.upload_file(path=path_input)
    print (uploaded_file)

    while uploaded_file.state != 2:
        print (uploaded_file.state)
        time.sleep(1)
        uploaded_file = genai.get_file(uploaded_file.name)
    
    print(uploaded_file)

    pdfFile = genai.get_file(uploaded_file.name)
    print(f"File URI: {pdfFile.uri}")

    return pdfFile





    # prompt = "Is this file content related to health department or education department"
    # print("Making LLM inference request...")
    # response = model.generate_content([pdfFile, prompt], request_options={"timeout": 600})
    # print(response.text)

# Create the Flask app
model = start()
app = Flask(__name__)
@app.route('/')
def home():
    start()
    return render_template('mybot.html')

@app.route('/chat', methods=['POST'])
def chat():
    response = "Connection Failed...."
    user_message = request.json.get('message')
    input_file_path = request.json.get('path')
    print (user_message)
    if user_message is None:
        return jsonify({"response": "No message received"}), 400
    else:
        if (input_file_path):
            file_processed = processFile(input_file_path)
            model_response = model.generate_content([file_processed, user_message], request_options={"timeout": 600})
            response = model_response.text
        else:      
            model_response = model.generate_content(user_message)
            response = model_response.text

    return jsonify({"response": response})

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
   
    return jsonify({"file_path": file_path})

def run_flask_app():
    print("Server running on http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)

run_flask_app()


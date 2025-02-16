from flask import Flask, render_template, request, jsonify
import threading
import google.generativeai as genai
import time
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from uuid import uuid4
from datetime import datetime, timezone
import markdown
import html
import requests
import json
from dotenv import load_dotenv
load_dotenv()

from llama_parse import LlamaParse
from llama_index.core import SimpleDirectoryReader

def start():
    load_dotenv()    
    print ('--- INITIALIZING MODEL ---')
    
    KEY = os.getenv('GEMINI_API_KEY')

    genai.configure(api_key=KEY)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-8b",
        # model_name="gemini-1.5-pro-latest",
        system_instruction=[
            "Carefully go through the entire code files provided",
            "Analyze the files thoroughly considering all minor details before responding ",
            "Answer the questions asked related to file shortly and precisely",
            "Consider the chat context before responding, but don't include the previous responses while responding. ONly respond the current question being asked, while keeping the conversation context thoroughly in consideration",
            "when asked to return code, only return code with minor related explanation of key concepts if required"
        ],
        # system_instruction=[
        #     "You are a helpful transcriber that can accurately transcribe text from images and PDFs. and videos",
        #     "Your mission is to transcribe text from the provided PDF, image or any other kind of files",
        #     "You can help with general queries and answer question for asked queries incase no input files are provided"
        # ],
        

    )
    return model

def processFile(file_name, path_input, storage_name):
    try:
        if storage_name is None:
            records = get_record_by_name(file_name)
            if records:
                print("\n\n existing \n\n\n")
                storage_name = records[0]['storage_name']
            if storage_name is None:
                print("\n\n new \n\n\n\n")
                uploaded_file = genai.upload_file(path=path_input)
                print(uploaded_file)

                while uploaded_file.state != 2:
                    print(uploaded_file.state)
                    time.sleep(1)
                    uploaded_file = genai.get_file(uploaded_file.name)
                storage_name = uploaded_file.name
                add_record_file(uploaded_file.display_name, uploaded_file.name, uploaded_file.state, uploaded_file.expiration_time)

                print(uploaded_file)

        pdfFile = genai.get_file(storage_name)
        print(f"File URI: {pdfFile.uri}")

        # print('\n\n\n\n\n  pdfFile got \n\n\n\n\n\n', pdfFile, '\n\n\n\n\n\n\n\n')

        return pdfFile
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return retryProcessFile(file_name, path_input) 

def retryProcessFile(file_name, path_input):
    print(f"Handling error for file: {file_name}, retrying...")

    try:
        file_mark_expired(file_name)
        uploaded_file = genai.upload_file(path=path_input)
        print(uploaded_file)

        while uploaded_file.state != 2:
            print(uploaded_file.state)
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)
        
        storage_name = uploaded_file.name
        add_record_file(uploaded_file.display_name, uploaded_file.name, uploaded_file.state, uploaded_file.expiration_time)

        print(f"Retry successful, file uploaded: {uploaded_file}")
        return uploaded_file

    except Exception as retry_error:
        print(f"Retry failed: {str(retry_error)}")
        return None


def parseFile(filepath):
    # set up parser
    parser = LlamaParse(
        result_type="text"
    )

    file_extractor = {".pdf": parser}
    documents = SimpleDirectoryReader(input_files=[filepath], file_extractor=file_extractor).load_data()
    for document in documents:
        simplified_text = document.text
        print(simplified_text)
    print(documents)
    return simplified_text

def add_record_file(display_name, storage_name, state, expiry):
    """Add a record to Firestore."""
    # Generate UUID
    record_uuid = str(uuid.uuid4())

    # Create a new record in Firestore
    doc_ref = db.collection('files').document(record_uuid)
    doc_ref.set({
        'display_name': display_name,
        'storage_name': storage_name,
        'state': state,
        'expiry': expiry,
        'uuid': record_uuid,
        'is_expired': False
    })

    return record_uuid

def get_record_by_name(display_name):
    db = firestore.client()
    records = db.collection('files')\
                .where('display_name', '==', display_name).stream()
    
    valid_records = [record.to_dict() for record in records if not record.to_dict().get('is_expired', False)]
    print ('\n\n\n\n\nvalid records: \n\n\n\n', valid_records, '\n\n\n\n\n')
    return valid_records

def file_mark_expired(display_name):
    db = firestore.client()
    records = db.collection('files')\
                .where('display_name', '==', display_name).stream()

    for record in records:
        record_id = record.id
        db.collection('files').document(record_id).update({'is_expired': True})
        print(f"Record {record_id} marked as expired.")

def add_record_chat(conv_id, message, filename, display_filename, file_path):
    """Add a record to Firestore."""
    # Generate UUID
    record_uuid = str(uuid.uuid4())

    doc_ref = db.collection('chat_history').document(record_uuid)
    doc_ref.set({
        'conv_id': conv_id,
        'message': message,
        'attached_file': filename,
        'attached_file_path': file_path,
        'attached_file_display': display_filename,
        'created_date': datetime.now(timezone.utc),
        'uuid': record_uuid,
        'is_deleted': False
    })

    return record_uuid

def get_chats():
    """ Get chats from firestore """
    print ("\n\n\n\n 1 \n\n\n\n\n")

    chat_ref = db.collection('chat_history') \
             .where('is_deleted', '==', False) \
             .order_by('created_date', direction='DESCENDING')
    
    chats = chat_ref.get()
    chat_records = [chat.to_dict() for chat in chats]

    return chat_records

def get_chat_by_conv_id(conv_id):
    """ Get a chat by conversation ID from Firestore """
    chat_ref = db.collection('chat_history').where('conv_id', '==', conv_id).limit(1)
    chat = chat_ref.get()

    return chat[0].to_dict() if chat else None

def update_chat_history(conv_id, user_ques, model_resp, conversation_context, storage_name):
    chat_rec = get_chat_by_conv_id(conv_id)

    if chat_rec:
        if 'content' in chat_rec and isinstance(chat_rec['content'], list) and chat_rec['content']:
            chat_rec['content'].append({
                "role": "user",
                "text": user_ques
            })
            chat_rec['content'].append({
                "role": "model",
                "text": model_resp
            })
            
            db.collection('chat_history').document(chat_rec['uuid']).update({
                'content': chat_rec['content'],
                'conversation_context': conversation_context,
                'attached_file' : storage_name
            })
        else:
            content = [
                {
                    "role": "user",
                    "text": user_ques
                },
                {
                    "role": "model",
                    "text": model_resp
                }
            ]
            db.collection('chat_history').document(chat_rec['uuid']).update({
                'content': content,
                'conversation_context': conversation_context,
                'attached_file' : storage_name
            })





def set_missing_created_dates():
    chat_ref = db.collection('chat_history')
    chats = chat_ref.get()

    # for chat in chats:
    #     if 'created_date' not in chat.to_dict():
    #         print (chat.id)
    #         chat_ref.document(chat.id).update({'created_date': datetime(2024, 10, 1, tzinfo=timezone.utc)})

    for chat in chats:
        if 'is_deleted' not in chat.to_dict():
            print (chat.id)
            chat_ref.document(chat.id).update({'is_deleted': False})





app = Flask(__name__)
model = start()
cred = credentials.Certificate('/home/saqib/Desktop/firebase_credentials.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()





@app.route('/')
def home():
    start()
    # set_missing_created_dates()
    chat_history = get_chats()
    return render_template('mybot.html',  chat_history=chat_history)



@app.route('/get_chat_content/<conv_id>', methods=['GET'])
def get_chat(conv_id):
    print ('\n\n\n in get chat \n\n\conv id: n', conv_id)
    chat_record = get_chat_by_conv_id(conv_id) 
    print ('\n\n\nchat record\n', chat_record)

    
    if chat_record:
        return jsonify(chat_record)
    return jsonify({"error": "Chat not found"}), 404




def get_response_local(user_message, file_path):
    load_dotenv()
    url = os.getenv("LLM_LOCAL")
    url = url+'/api/generate'
    file_pretext = 'Considering the follwing as raw text extracted from a PDF document, '


    if file_path and file_path != '':
        print ('\n processing file... \n\n')
        file_content = parseFile(file_path)
        print (file_content)
        user_message = file_pretext+file_content+'.....' + user_message
        print ('\n\n file processed ...\n')
    
    data = {
        "model": "llama3.2:1b",
        "prompt": user_message
    }

    try:
        print ('\n\n\nawaiting response from local model....\n\n')
        response = requests.post(url, json=data, stream=True)  
        response.raise_for_status() 

        full_text = ''
        for chunk in response.iter_lines():
            if chunk:
                data = json.loads(chunk.decode('utf-8'))
                full_text += data.get("response", "")
                if data.get("done"):
                    break
        print(full_text)

        return full_text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")






conversation_context = {}
@app.route('/chat', methods=['POST'])
def chat():
    global conversation_context
    user_message = request.json.get('message')
    input_file_path = request.json.get('path')
    conversation_id = request.json.get('conversation_id')
    use_local_model = request.json.get('use_local_model')
    is_new_conversation = False
    storage_name = None
    print ('\n\n\n conv id \n\n\n\n', conversation_id)

    if use_local_model == 'local':
        response = get_response_local(user_message, input_file_path)
        return jsonify({"response": response})

    if user_message is None:
        return jsonify({"response": "No message received"}), 400
    user_ques = {
        "role": "user",
        "text": user_message
    }

    if conversation_id is None or conversation_id == '':
        print ('\n\n\n new conv \n\n\n\n')
        conversation_id = str(uuid4())  
        conversation_context[conversation_id] = []
        is_new_conversation = True
    else:
        chat_conv = get_chat_by_conv_id(conversation_id)
        conversation_context = chat_conv['conversation_context'] if 'conversation_context' in chat_conv else None
        storage_name = chat_conv['attached_file'] if 'attached_file' in chat_conv else None
        print ('\n\n\n\n\n  storage_name got \n\n\n\n\n\n', storage_name, '\n\n\n\n\n\n\n\n')

    if conversation_context is None:
        conversation_context = {} 

    conversation_history = conversation_context.get(conversation_id, []) if conversation_context else []
    conversation_history.append(user_message)

    print ('\n\n\n\n\n  input_file_path got \n\n\n\n\n\n', input_file_path, '\n\n\n\n\n\n\n\n')

    if ( (input_file_path and input_file_path != '' and input_file_path != None) or (storage_name and storage_name != '' and storage_name != None)):
        input_file_name = request.json.get('filename')

        file_processed = processFile(input_file_name, input_file_path, storage_name)
        # print ('\n\n\n\n file_processed sent \n\n\n\n', file_processed, '\n\n\n\n\n')
        storage_name = file_processed.name
        model_response = model.generate_content(
            [file_processed] + conversation_history,
            request_options={"timeout": 600}
        )

        if is_new_conversation:
            add_record_chat(conversation_id, user_message, file_processed.name, file_processed.display_name, input_file_path)
    else:
        model_response = model.generate_content(
            conversation_history,
            request_options={}
        )

        if is_new_conversation:
            add_record_chat(conversation_id, user_message, None, None, None)
    
    response = model_response.candidates[0].content.parts[0].text
    conversation_history.append(response)
    conversation_context[conversation_id] = conversation_history
    
    user_ques = {
        "role": "user",
        "text": user_message
    }
    
    model_resp = {
        "role": "model",
        "text": response
    }
    update_chat_history(conversation_id, user_ques, model_resp, conversation_context, storage_name)

    return jsonify({"response": response, "conversation_id": conversation_id})





@app.route('/upload', methods=['POST'])
def upload():
    print ("\n upload called  \n")
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    print (request.files)

    file = request.files['file']
    file_path = os.path.join('uploads', file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)
   
    return jsonify({"file_path": file_path,"file_name": file.filename})

@app.route('/delete_chat/<conv_id>', methods=['POST'])
def delete_chat_by_conv_id(conv_id):
 
    print (conv_id)

    # Get the chat reference
    chat_ref = db.collection('chat_history').where('conv_id', '==', conv_id).limit(1)
    chat = chat_ref.get()
    
    if chat:
        chat_doc = chat[0]  # Get the first document
        chat_ref = db.collection('chat_history').document(chat_doc.id)
        chat_ref.update({'is_deleted': True})  # Set is_deleted to True
        
        return {"message": "Chat deleted successfully"}, 200  # Success response
    else:
        return {"message": "Chat not found"}, 404  # Not found response




def run_flask_app():
    print("Server running on http://127.0.0.1:5000/")
    app.run(debug=True, use_reloader=False)

run_flask_app()


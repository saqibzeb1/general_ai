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

# Set your API key here

import asyncio
from google import genai
# genai.configure(api_key='AIzaSyD8s8NqDu8ZJ6SvY9x2uwrF3EIWqFrSATs')

async def main():
    # genai.configure(api_key='AIzaSyD8s8NqDu8ZJ6SvY9x2uwrF3EIWqFrSATs')

    model_id = "gemini-2.0-flash-exp"
    config = {"response_modalities": ["AUDIO"]}

    client = genai.Client(api_key="AIzaSyD8s8NqDu8ZJ6SvY9x2uwrF3EIWqFrSATs", http_options={'api_version': 'v1alpha'})
    async with client.aio.live.connect(model=model_id, config=config) as session:
        message = "Hello? Gemini, are you there?"
        print("> ", message, "\n")
        await session.send(message, end_of_turn=True)

        async for response in session.receive():
            print(response)


if __name__ == "__main__":
    asyncio.run(main())









# def start():
#     load_dotenv()    
#     print ('--- INITIALIZING MODEL ---')
    
#     KEY = os.getenv('GEMINI_API_KEY')

#     genai.configure(api_key=KEY)

#     model = genai.GenerativeModel(
#         model_name="gemini-2.0-flash-exp",
#         config = {"response_modalities": ["AUDIO"]}
#         # model_name="gemini-1.5-pro-latest",
#         # system_instruction=[
#         #     "You are a helpful transcriber that can accurately transcribe text from images and PDFs. and videos",
#         #     "Your mission is to transcribe text from the provided PDF, image or any other kind of files",
#         #     "You can help with general queries and answer question for asked queries incase no input files are provided"
#         # ],
        

#     )
#     return model

# model = start()
# conversation_history = "tell me a joke"
# model_response = model.generate_content(
#     conversation_history,
#     request_options={}
# )

# print (model_response.candidates)

# response = model_response.candidates[0].content.parts[0].text

# print (response)



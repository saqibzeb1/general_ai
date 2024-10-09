from flask import Flask, render_template, request, jsonify
import threading
import google.generativeai as genai
import time

def start():
    genai.configure(api_key=KEY)

    file_path = "files\info.pdf"  
    uploaded_file = genai.upload_file(path=file_path)
    print (uploaded_file)
    
    pdfFile = genai.get_file(uploaded_file.name)
    print(f"File URI: {pdfFile.uri}")


    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        system_instruction=[
            "You are a helpful transcriber that can accurately transcribe text from images and PDFs.",
            "Your mission is to transcribe text from the provided PDF file.",
        ],
    )

    prompt = "Is this file content related to health department or education department"
    print("Making LLM inference request...")
    response = model.generate_content([pdfFile, prompt], request_options={"timeout": 600})
    print(response.text)


start()


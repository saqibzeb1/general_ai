from flask import Flask, render_template, request, jsonify
import threading
import google.generativeai as genai
import time


def start():
    KEY = "AIzaSyD8s8NqDu8ZJ6SvY9x2uwrF3EIWqFrSATs" 
    pdf_file = "info.pdf" 
    name = "info.pdf"

    genai.configure(api_key=KEY)

    file_path = "files\info.pdf"  
    uploaded_file = genai.upload_file(path=file_path)
    print (uploaded_file)
    
    pdfFile = genai.get_file(uploaded_file.name)
    print(f"File URI: {pdfFile.uri}")

    # while pdfFile.state.name == "PROCESSING":
    #     print(".", end="")
    #     time.sleep(10)
    #     pdfFile = genai.get_file(pdfFile.name)

    # if pdfFile.state.name == "FAILED":
    #     raise ValueError(pdfFile.state.name)

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


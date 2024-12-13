#!/usr/bin/env python
# coding: utf-8

# In[8]:


import streamlit as st
import openai
import pinecone
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as LangOpenAI
from langchain.vectorstores import Pinecone as LangPinecone
import jsonlines
from PyPDF2 import PdfReader
import json


# In[9]:


import os
from pinecone import Pinecone, ServerlessSpec

# Initialize Pinecone with your API key
pc = Pinecone(api_key="d8f32a14-b0b1-40bf-bbc1-b93f9f8b6c8d")

# Example: Create a new index if it doesn't exist
if 'taxease' not in pc.list_indexes().names():
    pc.create_index(
        name='taxease',
        dimension=1536,  # Specify the dimension of your embeddings
        metric='euclidean',  # You can change this depending on your needs
        spec=ServerlessSpec(
            cloud='aws',
            region='us-west-2'
        )
    )

# Connect to the "taxease" index
index = pc.Index("taxease")


# In[10]:


import streamlit as st
from PIL import Image

# Adding custom CSS for buttons and layout
st.markdown("""
    <style>
    .stButton>button {
        background-color: #6200ea;
        color: white;
        border-radius: 10px;
        font-size: 16px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #3700b3;
    }

    .stTextInput input {
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("TaxEase AI")

# Subtitle and description for better user guidance
st.subheader("Upload your tax documents (PDF or JSONL) for analysis.")
st.markdown(
    """
    **TaxEase AI** helps you analyze and query your tax documents using advanced AI techniques.
    Upload a tax document below to get started.
    """
)

# Add a placeholder for the image to make the UI more interactive
image = Image.open('image.webp')  # Replace with the correct image path
st.image(image, caption='TaxEase AI', use_column_width=True)

# Custom file uploader with enhanced design
uploaded_file = st.file_uploader("Drag and drop a JSONL or PDF file here", type=["jsonl", "pdf"])

# Display a message if no file is uploaded
if uploaded_file is None:
    st.warning("Please upload a file to proceed.")
else:
    # Your file processing code here
    st.success(f"Successfully uploaded: {uploaded_file.name}")




# Preprocess and load JSONL data
def load_jsonl_data(file):
    with jsonlines.open(file) as reader:
        return [entry for entry in reader]

def preprocess_jsonl(file):
    data = []
    with open(file, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    json_line = json.loads(line)
                    data.append({
                        "id": f"jsonl-{len(data)}",
                        "text": f"{json_line['prompt']} {json_line['completion']}",
                        "metadata": json_line
                    })
                except json.JSONDecodeError as e:
                    st.warning(f"Skipping invalid JSON line: {line}")
    return data

# Preprocess PDF data
def preprocess_pdf(file):
    reader = PdfReader(file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text()

    chunks = pdf_text.split("\n\n")
    return [
        {
            "id": f"pdf-{i}",
            "text": chunk.strip(),
            "metadata": {"source": "PDF", "page": i}
        }
        for i, chunk in enumerate(chunks) if chunk.strip()
    ]

# Handle file types
if uploaded_file is not None:
    if uploaded_file.type == "application/jsonl":
        data = preprocess_jsonl(uploaded_file)
        st.write(f"Loaded {len(data)} records from the JSONL file.")
    elif uploaded_file.type == "application/pdf":
        data = preprocess_pdf(uploaded_file)
        st.write(f"Extracted {len(data)} chunks from the PDF.")

    # Set up Pinecone index and store data
    index_name = "taxease"  # Example index name
    try:
        index = pinecone.Index(index_name)
    except Exception as e:
        st.error(f"Failed to connect to Pinecone: {e}")

    # Add data to Pinecone index (for simplicity, assuming it's a text embedding model)
    for record in data:
        index.upsert([(record['id'], record['text'])])

    # Create the retrieval-based QA chain
    retriever = LangPinecone(index=index, namespace="default", embedding_function="openai")
    qa_chain = RetrievalQA.from_chain_type(
        LangOpenAI(), retriever=retriever
    )

    # Input field for conversation
    user_input = st.text_input("Ask a question:")

    if user_input:
        response = qa_chain.run(user_input)
        st.write(response)


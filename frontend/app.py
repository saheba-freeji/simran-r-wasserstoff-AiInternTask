import streamlit as st
import requests
import os
import json
from pathlib import Path

# Constants
API_URL = "http://localhost:8000"

# Set up page config
st.set_page_config(
    page_title="Document Theme Identifier",
    page_icon="📚",
    layout="wide"
)

def main():
    st.title("📚 Document Theme Identifier")
    st.write("Upload documents and analyze themes across them")

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("OpenAI API Key", type="password")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    # Main area
    tab1, tab2 = st.tabs(["Upload Documents", "Chat & Analysis"])

    with tab1:
        st.header("Document Upload")
        uploaded_files = st.file_uploader(
            "Upload documents (PDF, DOCX, Images)", 
            accept_multiple_files=True,
            type=["pdf", "docx", "png", "jpg", "jpeg"]
        )

        if uploaded_files:
            with st.spinner("Processing documents..."):
                for file in uploaded_files:
                    # Save file temporarily
                    temp_dir = Path("temp")
                    temp_dir.mkdir(exist_ok=True)
                    temp_path = temp_dir / file.name
                    
                    with open(temp_path, "wb") as f:
                        f.write(file.getvalue())
                    
                    # Upload to API
                    try:
                        files = {"file": open(temp_path, "rb")}
                        response = requests.post(f"{API_URL}/upload", files=files)
                        response.raise_for_status()
                        st.success(f"Uploaded {file.name}")
                    except Exception as e:
                        st.error(f"Error uploading {file.name}: {str(e)}")
                    finally:
                        # Cleanup
                        temp_path.unlink(missing_ok=True)
    
    with tab2:
        st.header("Theme Analysis")
        query = st.text_input("Enter your query")
        
        if query:
            # Check if any documents have been uploaded
            try:
                docs_response = requests.get(f"{API_URL}/documents")
                if docs_response.status_code == 200:
                    docs = docs_response.json()
                    if not docs:
                        st.warning("Please upload some documents first.")
                        return
            except Exception as e:
                st.error(f"Error checking documents: {str(e)}")
                return

            with st.spinner("Analyzing..."):
                try:
                    # Send the chat request
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={"query": query},
                        headers={"Content-Type": "application/json"}
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    # Display themes
                    if "themes" in result and result["themes"]:
                        for theme in result["themes"]:
                            with st.expander(f"Theme: {theme['name']}", expanded=True):
                                st.write(theme["description"])
                                st.write("Supporting Documents:")
                                for doc in theme["supporting_documents"]:
                                    st.write(f"- {doc['document_id']}: {doc['citation']}")
                    else:
                        st.info("No clear themes were identified in the documents for this query.")
                    
                    # Display raw responses
                    if "raw_responses" in result and result["raw_responses"]:
                        with st.expander("Document Details", expanded=False):
                            for doc in result["raw_responses"]:
                                st.write(f"**Document {doc['document_id']}**")
                                st.write(f"Citation: {doc['citation']}")
                                st.text(doc["answer"])
                                st.write("---")
                                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

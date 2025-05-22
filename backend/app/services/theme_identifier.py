from typing import List, Dict, Any
from openai import OpenAI
from app.models.document import Theme, DocumentResponse
import json

class ThemeIdentifier:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def identify_themes(self, document_responses: List[DocumentResponse]) -> List[Theme]:
        """Identify themes from document responses using OpenAI"""
        try:
            if not document_responses:
                return []

            # Prepare the prompt
            context = "\n\n".join([
                f"Document {resp.document_id}:\n{resp.answer}\nCitation: {resp.citation}"
                for resp in document_responses
            ])
            
            prompt = f"""Analyze these document excerpts and identify key themes:

{context}

Format output exactly as this example:
Theme 1 – [Theme Name]:
Documents (DOC001, DOC002) [brief explanation of how these documents support the theme]

Theme 2 – [Theme Name]:
[Document IDs] [brief explanation with focus on regulatory/legal aspects]

Format your response as JSON with this structure:
{{
    "themes": [
        {{
            "name": "Theme name",
            "description": "Theme description",
            "supporting_documents": ["DOC001", "DOC002"]
        }}
    ]
}}"""
            
            # Make API call with proper error handling
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a document analysis expert. Your responses must be valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            content = response.choices[0].message.content
            themes_data = json.loads(content)
            
            themes = []
            for theme_data in themes_data["themes"]:
                # Find the full document responses for supporting documents
                supporting_docs = [
                    resp for resp in document_responses
                    if resp.document_id in theme_data["supporting_documents"]
                ]
                
                themes.append(Theme(
                    name=theme_data["name"],
                    description=theme_data["description"],
                    supporting_documents=supporting_docs
                ))
            
            return themes
                
        except Exception as e:
            print(f"Error in theme identification: {str(e)}")
            raise Exception(f"Failed to identify themes: {str(e)}")

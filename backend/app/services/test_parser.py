# from app.services.document_parser import DocumentParser

# parser = DocumentParser()
# result = parser.parse_file("files/DOC01.pdf") # replace with your file path
# print(result["text"][:500])

from app.services.document_parser import DocumentParser
import os

parser = DocumentParser()

for test_file in ["files/DOC02.pdf", "files/doc2.jpg", "files/DOC02.docx"]:
    if os.path.exists(test_file):
        result = parser.parse_file(test_file)
        print(f"\n--- Parsed {test_file} ---")
        print(result["text"][:500], "...\n")
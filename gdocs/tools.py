from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

class AppendToDocInput(BaseModel):
    document_id: str = Field(..., description="The ID of the Google Document to modify (found in the URL).")
    content: str = Field(..., description="The text content to append to the document.")
    insert_timestamp: Optional[bool] = Field(False, description="Whether to prefix the content with the current timestamp.")
    heading_level: Optional[str] = Field(None, description="Optional heading level (e.g. 'HEADING_1', 'HEADING_2', 'NORMAL_TEXT').")

def append_to_google_doc(creds, input_data: AppendToDocInput) -> dict:
    """
    Appends text to the end of a Google Document.
    Returns success status, document ID, and updated revision information.
    """
    try:
        service = build("docs", "v1", credentials=creds)
        
        # Determine the length of the document to know where to insert
        document = service.documents().get(documentId=input_data.document_id).execute()
        
        # Find the end index of the document
        content_items = document.get('body').get('content')
        end_index = content_items[-1].get('endIndex') - 1 if content_items else 1
        
        text_to_insert = input_data.content
        if input_data.insert_timestamp:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            text_to_insert = f"[{timestamp}]\n{text_to_insert}"
            
        if not text_to_insert.endswith('\n'):
            text_to_insert += '\n'

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': end_index,
                    },
                    'text': text_to_insert
                }
            }
        ]
        
        # If a heading level is requested, format the inserted text
        if input_data.heading_level:
            requests.append({
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': end_index,
                        'endIndex': end_index + len(text_to_insert)
                    },
                    'paragraphStyle': {
                        'namedStyleType': input_data.heading_level
                    },
                    'fields': 'namedStyleType'
                }
            })

        result = service.documents().batchUpdate(
            documentId=input_data.document_id, body={'requests': requests}).execute()
            
        return {
            "success": True,
            "document_id": result.get('documentId'),
            "updated_revision_id": result.get('replies', [{}])[0].get('insertText', {}).get('revisionId', 'unknown'),
            "status_message": "Content appended successfully"
        }
        
    except HttpError as error:
        return {
            "success": False,
            "error_message": f"An error occurred calling Google Docs API: {error}"
        }
    except Exception as error:
        return {
            "success": False,
            "error_message": f"An unexpected error occurred: {error}"
        }

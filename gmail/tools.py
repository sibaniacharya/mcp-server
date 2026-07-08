import base64
from email.message import EmailMessage
from typing import List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

# Input schema for the MCP tool
class SendEmailInput(BaseModel):
    recipient: str = Field(..., description="The email address of the recipient.")
    subject: str = Field(..., description="The subject of the email.")
    body: str = Field(..., description="The plain text body of the email.")
    cc: Optional[List[str]] = Field(None, description="Optional CC email addresses.")
    bcc: Optional[List[str]] = Field(None, description="Optional BCC email addresses.")
    html_body: Optional[str] = Field(None, description="Optional HTML formatted body of the email.")

def send_email(creds, input_data: SendEmailInput) -> dict:
    """
    Sends an email using the authenticated user's Gmail account.
    Returns a dictionary with success status, message ID, timestamp, etc.
    """
    try:
        service = build("gmail", "v1", credentials=creds)
        
        message = EmailMessage()
        
        if input_data.html_body:
            message.set_content(input_data.body)
            message.add_alternative(input_data.html_body, subtype='html')
        else:
            message.set_content(input_data.body)

        message["To"] = input_data.recipient
        message["From"] = "me"
        message["Subject"] = input_data.subject
        
        if input_data.cc:
            message["Cc"] = ", ".join(input_data.cc)
        if input_data.bcc:
            message["Bcc"] = ", ".join(input_data.bcc)

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        
        return {
            "success": True,
            "message_id": send_message["id"],
            "thread_id": send_message["threadId"],
            "status_message": "Email sent successfully"
        }

    except HttpError as error:
        return {
            "success": False,
            "error_message": f"An error occurred calling Gmail API: {error}"
        }
    except Exception as error:
        return {
            "success": False,
            "error_message": f"An unexpected error occurred: {error}"
        }

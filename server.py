import os
import asyncio
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.requests import Request
import uvicorn
import mcp.types as types

from auth.oauth import get_credentials
from gmail.tools import send_email, SendEmailInput
from gdocs.tools import append_to_google_doc, AppendToDocInput

# Initialize the MCP Server
app = Server("mcp-google-workspace")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    List tools available in this MCP server.
    """
    return [
        types.Tool(
            name="send_email",
            description="Send an email using the authenticated user's Gmail account.",
            inputSchema=SendEmailInput.model_json_schema()
        ),
        types.Tool(
            name="append_to_google_doc",
            description="Append formatted text to a Google Document.",
            inputSchema=AppendToDocInput.model_json_schema()
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """
    Handle tool execution requests from the MCP client.
    """
    try:
        # Load credentials just-in-time
        creds = get_credentials()
        
        if name == "send_email":
            # Validate input arguments against Pydantic schema
            input_data = SendEmailInput(**arguments)
            # Execute tool logic
            result = send_email(creds, input_data)
            
            # Format output as MCP TextContent
            if result.get("success"):
                text_result = f"Email sent successfully. Message ID: {result.get('message_id')}"
            else:
                text_result = f"Error sending email: {result.get('error_message')}"
                
            return [types.TextContent(type="text", text=text_result)]
            
        elif name == "append_to_google_doc":
            # Validate input arguments against Pydantic schema
            input_data = AppendToDocInput(**arguments)
            # Execute tool logic
            result = append_to_google_doc(creds, input_data)
            
            # Format output as MCP TextContent
            if result.get("success"):
                text_result = f"Content appended successfully to document ID: {result.get('document_id')}"
            else:
                text_result = f"Error appending to document: {result.get('error_message')}"
                
            return [types.TextContent(type="text", text=text_result)]
            
        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Tool execution failed: {str(e)}")]


transport = SseServerTransport("/messages")

async def handle_sse(request: Request):
    async with transport.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

async def handle_messages(request: Request):
    await transport.handle_post_message(request.scope, request.receive, request._send)

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

def main():
    """
    Start the MCP server using SSE transport on the port specified by Railway.
    """
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

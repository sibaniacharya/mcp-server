# MCP Google Workspace Server

A generic **Model Context Protocol (MCP)** server that exposes Gmail and Google Docs capabilities as standard MCP tools. This server allows AI agents (like Claude, Cursor, ChatGPT) to interact with Google Workspace APIs seamlessly.

## Features

Provides the following tools:
- `send_email`: Send an email through the authenticated user's Gmail account.
- `append_to_google_doc`: Append text/content to an existing Google Document.

## Prerequisites

1. **Python 3.10+**
2. **Google Cloud Console Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project.
   - Enable **Gmail API** and **Google Docs API**.
   - Configure the OAuth consent screen (Desktop App).
   - Create OAuth 2.0 Client ID credentials.
   - Download the JSON file, rename it to `credentials.json`, and place it in the root of this project.

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Because this server implements the standard stdio transport for MCP, it can be launched directly via an MCP client configuration. 

For testing, you can use the official `mcp-inspector`:

```bash
npx @modelcontextprotocol/inspector python server.py
```

### Initial Authentication
The first time you run the server and invoke a tool, it will open a local web browser to authenticate with Google Workspace. Upon successful authentication, a `token.json` file will be generated locally.

## Example Usage in Cursor
Add this to your MCP configuration in Cursor (or similar client):

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

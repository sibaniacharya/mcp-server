# Build a Generic MCP Server for Gmail and Google Docs Integration

We will build a production-ready Model Context Protocol (MCP) server that exposes Gmail and Google Docs capabilities as standardized MCP tools. The server will provide `send_email` and `append_to_google_doc` tools, handle Google OAuth 2.0 authentication securely, and comply with the MCP specification, acting as a bridge between AI agents and Google Workspace APIs.

## Implementation Phases

### Phase 1: Project Setup and Authentication
- Initialize Python environment and `requirements.txt`.
- Implement `auth/oauth.py` using `google-auth-oauthlib` to handle Google OAuth 2.0 flow and token storage.
- Set up Google Cloud Console, enable APIs, and download `credentials.json`.

### Phase 2: Core MCP Server Initialization
- Create `server.py`.
- Initialize `mcp.server.Server` and set up standard stdio transport.

### Phase 3: Gmail Integration
- Implement `gmail/tools.py` with the `send_email` tool.
- Add input validation using Pydantic.
- Register `send_email` in `server.py` and map it to the Gmail tool function.

### Phase 4: Google Docs Integration
- Implement `gdocs/tools.py` with the `append_to_google_doc` tool.
- Add input validation and timestamping capabilities.
- Register `append_to_google_doc` in `server.py`.

### Phase 5: Testing and Documentation
- Run local tests using `mcp-inspector`.
- Verify OAuth flow, email sending, and document appending.
- Write `docs/README.md` with complete setup instructions.

## Proposed Changes

We will set up the Python project structure and create modules for authentication, Gmail, and Google Docs integration.

### MCP Google Workspace Server

#### requirements.txt
Will include dependencies: `mcp`, `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`.

#### server.py
The main entry point that initializes the MCP server, sets up the stdio transport, and registers the tools.

#### auth/oauth.py
Handles the OAuth 2.0 flow using `google-auth-oauthlib`, loading/saving tokens, and managing secure credentials storage.

#### gmail/tools.py
Contains the implementation of the `send_email` tool, interacting with the Gmail API, and ensuring proper input validation and error handling.

#### gdocs/tools.py
Contains the implementation of the `append_to_google_doc` tool, calling the Google Docs API to append formatted text and handling potential errors.

#### docs/README.md
Documentation with setup instructions, Google Cloud Console configuration steps (to obtain `credentials.json`), and example MCP client configurations.

## Verification Plan

### Automated Tests
- Unit tests that mock Google API services to verify proper MCP tool input validation and structure.
- Tests to ensure that error responses follow the expected MCP format (e.g. invalid email addresses, missing document IDs).

### Manual Verification
- **OAuth:** Run the server manually and ensure the browser pops up for Google Workspace consent and generates a `token.json`.
- **Gmail Tool:** Start the server with `mcp-inspector` or Cursor, invoke the `send_email` tool, and verify an actual email is received.
- **Docs Tool:** Invoke `append_to_google_doc` and check the specified Google Document to verify the text was successfully appended.

# Deployment Plan: Deploying MCP Google Workspace Server on Railway

This document outlines the steps required to modify and deploy this MCP (Model Context Protocol) server to [Railway](https://railway.app/). 

Currently, this server is designed to run locally using the `stdio` transport and file-based authentication (`credentials.json`, `token.json`). Deploying to a cloud platform like Railway requires moving to an HTTP-based transport (SSE) and managing secrets via environment variables.

## Phase 1: Architectural Changes (Required)

Before deploying to Railway, the following code changes must be made to the project:

### 1. Transport Update: Switch from `stdio` to `SSE`
Railway applications must listen for HTTP requests on a specific port. MCP provides Server-Sent Events (SSE) for remote deployment.
- [ ] Install a web framework like Starlette or FastAPI (`pip install fastapi uvicorn`).
- [ ] Update `server.py` to use `mcp.server.sse.sse_server` instead of `mcp.server.stdio.stdio_server`.
- [ ] Ensure the server binds to the `PORT` environment variable provided by Railway (e.g., `0.0.0.0:$PORT`).

### 2. Secret Management Update
Cloud platforms do not support manual file uploads out-of-the-box easily, and committing secrets is a security risk.
- [ ] **Google Credentials**: Convert the contents of `credentials.json` and `token.json` into base64-encoded strings and store them as environment variables (e.g., `GOOGLE_CREDENTIALS_B64`, `GOOGLE_TOKEN_B64`).
- [ ] Update `auth/oauth.py` to decode these environment variables at runtime and write them to temporary files or load them directly into memory for Google Auth.
- *(Alternative)*: Switch from an OAuth Desktop app flow to a Google Cloud Service Account, which only requires a single JSON key that can be loaded from an environment variable.

### 3. Startup Configuration
- [ ] Ensure `requirements.txt` is fully up-to-date with the new web framework dependencies.
- [ ] Create a `Procfile` or `railway.json` (or just set the Start Command in Railway) to run the server. For example: `uvicorn server:app --host 0.0.0.0 --port $PORT`.

## Phase 2: Railway Deployment Setup

Once the code modifications are pushed to a GitHub repository, you can deploy to Railway:

### 1. Project Creation
- [ ] Log in to [Railway.app](https://railway.app/) and click **New Project**.
- [ ] Select **Deploy from GitHub repo** and choose this project's repository.
- [ ] Railway will automatically detect the Python environment via `requirements.txt`.

### 2. Environment Variables Configuration
In the Railway Dashboard, go to your service's **Variables** tab and add the necessary secrets:
- `PORT`: (Railway sets this automatically, but ensure your code uses it).
- `GOOGLE_CREDENTIALS_B64`: (Base64 string of your `credentials.json`).
- `GOOGLE_TOKEN_B64`: (Base64 string of your `token.json`).

### 3. Build and Start
- [ ] Go to the **Settings** tab in Railway.
- [ ] Under **Deploy**, ensure the **Start Command** is configured correctly (e.g., `uvicorn server:app --host 0.0.0.0 --port $PORT`).
- [ ] Wait for the build and deployment to finish.

## Phase 3: Networking and Usage

### 1. Generate a Public URL
- [ ] In the Railway Dashboard, go to the **Networking** tab for your service.
- [ ] Click **Generate Domain** to get a public HTTPS URL for your MCP server.

### 2. Configure the MCP Client
To use the remote MCP server with an application like Claude Desktop, you will need to update the client configuration to connect via SSE instead of spawning a local process.

Example `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "google-workspace-remote": {
      "command": "curl",
      "args": ["-s", "https://YOUR_RAILWAY_URL/sse"]
    }
  }
}
```
*(Note: Some MCP clients support direct SSE URL configuration natively without using `curl` as a bridge, depending on client capabilities).*

## Immediate Action Items
1. Refactor `server.py` to use an HTTP framework (FastAPI/Starlette) and MCP's SSE transport.
2. Refactor the `auth/oauth.py` to accept Google credentials from environment variables.
3. Push the updated code to GitHub.
4. Link the repository to Railway.

#!/usr/bin/env python3
"""
Confluence MCP Server (Stdio transport)
Provides Confluence Wiki tools for Antigravity, Claude Code, and other MCP clients.
Uses Atlassian REST API with Basic Auth (email + API token).
"""

import os
import sys
import json
import re
import html
from urllib.parse import quote
import requests
from requests.auth import HTTPBasicAuth

# 1. Load configuration
def load_env():
    # Traverse upward from script directory to find .env.local or .env
    cur = os.path.dirname(os.path.abspath(__file__))
    candidates = []
    for _ in range(5):
        candidates.append(os.path.join(cur, ".env.local"))
        candidates.append(os.path.join(cur, ".env"))
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    candidates.extend([
        os.path.join(os.getcwd(), ".env.local"),
        os.path.join(os.getcwd(), ".env"),
    ])
    for p in candidates:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() not in os.environ:
                            os.environ[k.strip()] = v.strip()
            break

load_env()

CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL", "https://seolakim195.atlassian.net/wiki").rstrip("/")
CONFLUENCE_EMAIL = os.environ.get("CONFLUENCE_EMAIL", "")
CONFLUENCE_API_TOKEN = os.environ.get("CONFLUENCE_API_TOKEN", "")

def get_auth():
    if not CONFLUENCE_EMAIL or not CONFLUENCE_API_TOKEN:
        raise ValueError("CONFLUENCE_EMAIL or CONFLUENCE_API_TOKEN is not configured in environment or .env.local")
    return HTTPBasicAuth(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)

def html_to_text(html_content):
    """Simple converter from storage HTML to readable text for LLM."""
    if not html_content:
        return ""
    text = html_content
    # Replace table tags for better reading
    text = re.sub(r'<tr[^>]*>', '\n| ', text)
    text = re.sub(r'</t[dh]>', ' | ', text)
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n# \1\n', text)
    # Strip any other tags
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# 2. Confluence API Client functions
def get_page(page_id):
    auth = get_auth()
    url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}?expand=body.storage,version,space"
    resp = requests.get(url, auth=auth, headers={"Accept": "application/json"}, timeout=15)
    if resp.status_code != 200:
        return {"error": f"Failed to get page {page_id}: {resp.status_code} {resp.text}"}
    
    data = resp.json()
    storage_val = data.get("body", {}).get("storage", {}).get("value", "")
    webui_link = data.get("_links", {}).get("base", "") + data.get("_links", {}).get("webui", "")
    
    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "space_key": data.get("space", {}).get("key"),
        "version": data.get("version", {}).get("number"),
        "url": webui_link or f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={page_id}",
        "readable_text": html_to_text(storage_val),
        "storage_html": storage_val
    }

def search_pages(query, limit=10):
    auth = get_auth()
    # If query does not look like CQL, formulate a text search CQL
    if "=" not in query and "~" not in query:
        cql = f'text ~ "{query}" OR title ~ "{query}"'
    else:
        cql = query
        
    url = f"{CONFLUENCE_URL}/rest/api/content/search?cql={quote(cql)}&limit={limit}&expand=version,space"
    resp = requests.get(url, auth=auth, headers={"Accept": "application/json"}, timeout=15)
    if resp.status_code != 200:
        return {"error": f"Search failed: {resp.status_code} {resp.text}"}
    
    results = []
    for item in resp.json().get("results", []):
        results.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "type": item.get("type"),
            "space_key": item.get("space", {}).get("key"),
            "version": item.get("version", {}).get("number"),
            "url": f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={item.get('id')}"
        })
    return {"results": results, "total": len(results)}

def update_page(page_id, body_storage, title=None, version_comment=None):
    auth = get_auth()
    # 1. Fetch current version and title
    curr_url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}?expand=version"
    curr_resp = requests.get(curr_url, auth=auth, headers={"Accept": "application/json"}, timeout=15)
    if curr_resp.status_code != 200:
        return {"error": f"Failed to retrieve current page version: {curr_resp.status_code} {curr_resp.text}"}
    
    curr_data = curr_resp.json()
    curr_version = curr_data.get("version", {}).get("number", 1)
    new_version = curr_version + 1
    page_title = title if title else curr_data.get("title", "")
    
    payload = {
        "id": page_id,
        "type": "page",
        "title": page_title,
        "version": {
            "number": new_version,
            "message": version_comment or "Updated via Confluence MCP"
        },
        "body": {
            "storage": {
                "value": body_storage,
                "representation": "storage"
            }
        }
    }
    
    update_url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}"
    resp = requests.put(
        update_url,
        auth=auth,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=payload,
        timeout=20
    )
    if resp.status_code != 200:
        return {"error": f"Failed to update page {page_id}: {resp.status_code} {resp.text}"}
    
    res_data = resp.json()
    return {
        "success": True,
        "id": res_data.get("id"),
        "title": res_data.get("title"),
        "version": res_data.get("version", {}).get("number"),
        "message": f"Successfully updated page {page_id} to version {new_version}"
    }

def create_page(space_key, title, body_storage, parent_id=None):
    auth = get_auth()
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": body_storage,
                "representation": "storage"
            }
        }
    }
    if parent_id:
        payload["ancestors"] = [{"id": str(parent_id)}]
        
    url = f"{CONFLUENCE_URL}/rest/api/content"
    resp = requests.post(
        url,
        auth=auth,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=payload,
        timeout=20
    )
    if resp.status_code not in (200, 201):
        return {"error": f"Failed to create page: {resp.status_code} {resp.text}"}
        
    res_data = resp.json()
    return {
        "success": True,
        "id": res_data.get("id"),
        "title": res_data.get("title"),
        "space_key": space_key,
        "version": res_data.get("version", {}).get("number"),
        "url": f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={res_data.get('id')}"
    }

# 3. Tool Definitions
TOOLS = [
    {
        "name": "confluence_get_page",
        "description": "Get Confluence page metadata and contents (both readable text and storage HTML) by page ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "The Confluence page ID (e.g. '360539')"
                }
            },
            "required": ["page_id"]
        }
    },
    {
        "name": "confluence_search",
        "description": "Search Confluence pages using text query or CQL (Confluence Query Language).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords to search or CQL expression"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default: 10)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "confluence_update_page",
        "description": "Update an existing Confluence page with new content in storage format.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "Confluence page ID to update"
                },
                "body_storage": {
                    "type": "string",
                    "description": "New content in Confluence storage format (XHTML)"
                },
                "title": {
                    "type": "string",
                    "description": "Optional page title if changing title"
                },
                "version_comment": {
                    "type": "string",
                    "description": "Optional change summary / commit message for Confluence history"
                }
            },
            "required": ["page_id", "body_storage"]
        }
    },
    {
        "name": "confluence_create_page",
        "description": "Create a new Confluence page in a specific space.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "space_key": {
                    "type": "string",
                    "description": "Target Confluence space key (e.g. '~712020ed6696cba1a44b4683098b6834093514')"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the page"
                },
                "body_storage": {
                    "type": "string",
                    "description": "Page body in storage format (XHTML)"
                },
                "parent_id": {
                    "type": "string",
                    "description": "Optional parent page ID"
                }
            },
            "required": ["space_key", "title", "body_storage"]
        }
    }
]

# 4. JSON-RPC Handling
def handle_tool_call(name, args):
    try:
        if name == "confluence_get_page":
            res = get_page(args.get("page_id"))
        elif name == "confluence_search":
            res = search_pages(args.get("query"), args.get("limit", 10))
        elif name == "confluence_update_page":
            res = update_page(
                args.get("page_id"),
                args.get("body_storage"),
                args.get("title"),
                args.get("version_comment")
            )
        elif name == "confluence_create_page":
            res = create_page(
                args.get("space_key"),
                args.get("title"),
                args.get("body_storage"),
                args.get("parent_id")
            )
        else:
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
                "isError": True
            }
        
        if isinstance(res, dict) and "error" in res:
            return {
                "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}],
                "isError": True
            }
        
        return {
            "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]
        }
    except Exception as e:
        return {
            "content": [{"type": "text", "text": f"Exception calling {name}: {str(e)}"}],
            "isError": True
        }

def send_response(response_dict):
    out = json.dumps(response_dict)
    sys.stdout.write(out + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        
        msg_id = req.get("id")
        method = req.get("method")
        
        if method == "initialize":
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "confluence-mcp",
                        "version": "1.0.0"
                    }
                }
            })
        elif method == "notifications/initialized":
            # Client acknowledging initialization, no reply required
            pass
        elif method == "ping":
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {}
            })
        elif method == "tools/list":
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": TOOLS
                }
            })
        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            call_result = handle_tool_call(name, arguments)
            send_response({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": call_result
            })
        else:
            if msg_id is not None:
                send_response({
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                })

if __name__ == "__main__":
    main()


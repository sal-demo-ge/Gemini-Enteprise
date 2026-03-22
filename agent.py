"""
Google Sheets ADK Agent — Vertex AI + Gemini 3.1 Pro
Reads, writes, and updates a Google Sheet via OAuth 2.0.
"""

import os
from google.adk.agents import LlmAgent
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

# ── Auth ──────────────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_FILE = "token.pickle"
CREDENTIALS_FILE = "credentials.json"  # Downloaded from Google Cloud Console


def get_sheets_service():
    """Authenticate via OAuth 2.0 and return a Sheets API service object."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("sheets", "v4", credentials=creds)


# Shared service instance
_service = None


def _get_service():
    global _service
    if _service is None:
        _service = get_sheets_service()
    return _service


# ── Tools ─────────────────────────────────────────────────────────────────────

def read_sheet(spreadsheet_id: str, range_notation: str) -> dict:
    """
    Read data from a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet (from its URL).
        range_notation: A1 notation range, e.g. "Sheet1!A1:D10".

    Returns:
        A dict with a 'values' key containing a list of rows (each row is a list of cell values).
    """
    try:
        result = (
            _get_service()
            .spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_notation)
            .execute()
        )
        values = result.get("values", [])
        return {"success": True, "values": values, "rows": len(values)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def append_rows(spreadsheet_id: str, range_notation: str, rows: list) -> dict:
    """
    Append one or more rows to a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_notation: A1 notation range indicating where to start appending, e.g. "Sheet1!A1".
        rows: A list of rows to append. Each row is a list of cell values,
              e.g. [["Alice", 30, "Engineer"], ["Bob", 25, "Designer"]].

    Returns:
        A dict confirming the number of rows appended.
    """
    try:
        body = {"values": rows}
        result = (
            _get_service()
            .spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=range_notation,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        updates = result.get("updates", {})
        return {
            "success": True,
            "rows_appended": len(rows),
            "updated_range": updates.get("updatedRange"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_cells(spreadsheet_id: str, range_notation: str, values: list) -> dict:
    """
    Update existing cells in a Google Sheet.

    Args:
        spreadsheet_id: The ID of the spreadsheet.
        range_notation: A1 notation of the exact range to update, e.g. "Sheet1!B2:C3".
        values: A 2D list of values matching the range dimensions,
                e.g. [["Updated Name", "New Value"], ["Another", "Row"]].

    Returns:
        A dict confirming the cells updated.
    """
    try:
        body = {"values": values}
        result = (
            _get_service()
            .spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_notation,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        return {
            "success": True,
            "updated_range": result.get("updatedRange"),
            "updated_cells": result.get("updatedCells"),
            "updated_rows": result.get("updatedRows"),
            "updated_columns": result.get("updatedColumns"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ── Agent ─────────────────────────────────────────────────────────────────────

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID_HERE")

sheets_agent = LlmAgent(
    # Gemini 3.1 Pro via Vertex AI (requires GOOGLE_CLOUD_PROJECT + GOOGLE_CLOUD_LOCATION env vars
    # and GOOGLE_GENAI_USE_VERTEXAI=TRUE)
    model="gemini-3.1-pro",
    name="sheets_agent",
    description="An agent that can read, write, and update a connected Google Sheet.",
    instruction=f"""You are a helpful data assistant with access to a Google Sheet (ID: {SPREADSHEET_ID}).

You can:
- READ data from any range in the sheet
- APPEND new rows of data
- UPDATE existing cells

When the user asks you to interact with the sheet:
1. Determine the correct tool to use (read_sheet, append_rows, or update_cells).
2. Use sensible A1 notation ranges (e.g. "Sheet1!A1:Z100" to read all data).
3. Always confirm the result back to the user clearly.
4. If an operation fails, report the error and suggest how to fix it.

Default sheet tab name is "Sheet1" unless the user specifies otherwise.
""",
    tools=[read_sheet, append_rows, update_cells],
)

# Expose as `agent` for ADK runner / adk web
agent = sheets_agent

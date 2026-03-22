# Google Sheets ADK Agent

A Python ADK agent powered by **Gemini 2.5 Pro on Vertex AI** that reads, writes, and
updates a Google Sheet — designed to pair with a Gemini Enterprise agent.

---

## Prerequisites

- Python 3.11+
- A Google Cloud project with **Vertex AI API** enabled
- Gemini 3.1 Pro available in your region (e.g. `us-central1`)
- A Google Sheet and OAuth 2.0 credentials

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Enable Google Sheets API & create OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Library**
2. Enable **Google Sheets API**
3. Go to **APIs & Services** → **Credentials** → **Create Credentials** → **OAuth client ID**
4. Choose **Desktop app**, download the JSON, and save it as `credentials.json` in this folder

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your values
```

Key values to set:
| Variable | Description |
|---|---|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI region (e.g. `us-central1`) |
| `SPREADSHEET_ID` | ID from your Google Sheet URL |

### 4. Authenticate with Google Cloud (ADC)

```bash
gcloud auth application-default login
```

### 5. Run the agent

**Interactive terminal:**
```bash
adk run agent.py
```

**Browser-based dev UI:**
```bash
adk web agent.py
```

On first run, a browser window will open for Google OAuth — sign in to grant
Sheets access. A `token.pickle` file is saved for subsequent runs.

---

## Tools available to the agent

| Tool | Description |
|---|---|
| `read_sheet` | Read any range (e.g. `Sheet1!A1:Z100`) |
| `append_rows` | Add new rows below existing data |
| `update_cells` | Overwrite specific cells by range |

---

## Example prompts

```
"Read all data from Sheet1"
"Append a new row: ['John', 'Doe', 'john@example.com']"
"Update cell B3 to 'Completed'"
"Show me what's in columns A through D"
```

---

## Connecting to your Gemini Enterprise Agent

This agent is designed to act as a **data layer tool** for a Gemini Enterprise
agent. To connect them:

1. Deploy this agent to **Vertex AI Agent Engine**:
   ```bash
   adk deploy agent.py --project $GOOGLE_CLOUD_PROJECT --region $GOOGLE_CLOUD_LOCATION
   ```
2. In your Gemini Enterprise agent configuration, register the deployed
   Agent Engine endpoint as a tool/connector.
3. The Gemini agent can then delegate all sheet operations to this Claude-powered agent.

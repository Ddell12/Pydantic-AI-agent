# Google Drive RAG Pipeline

This RAG (Retrieval Augmented Generation) pipeline watches for files that are created, updated, or deleted in Google Drive. It automatically processes these files, extracts text content, and stores the content with embeddings in a Supabase database with PGVector support.

## Features

- Monitors Google Drive for file changes (creation, updates, deletion)
- Processes text documents and PDFs
- Extracts text content and splits into chunks of 400 characters (no overlap)
- Creates embeddings using OpenAI's embedding model
- Stores content and embeddings in Supabase with PGVector
- Automatically removes records when files are deleted from Google Drive

## Requirements

- Python 3.8+
- Google Drive API credentials
- Supabase account with database access
- OpenAI API key

## Installation

1. Install the required dependencies:

```bash
pip install -r RAG_Pipeline/requirements.txt
```

2. Set up your environment variables in `.env`:

```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
LLM_API_KEY=your_openai_api_key
```

3. Set up Google Drive API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials as `credentials.json` and place it in the project directory

## Database Setup

Before running the pipeline, you need to set up the Supabase database:

```bash
python -m RAG_Pipeline.main --setup
```

This will:
- Enable the pgvector extension
- Create the documents table with the required columns and indexes

## Usage

Run the pipeline with:

```bash
python -m RAG_Pipeline.main
```

Optional arguments:
- `--setup`: Set up the database before starting the watcher
- `--credentials`: Path to Google Drive API credentials file (default: credentials.json)
- `--token`: Path to Google Drive API token file (default: token.json)
- `--interval`: Interval in seconds between checks for changes (default: 60)
- `--folder-id`: ID of the specific Google Drive folder to watch (and its subfolders)

Examples:

```bash
# Watch all of Google Drive with 30 second intervals
python -m RAG_Pipeline.main --interval 30

# Watch only a specific folder and its subfolders
python -m RAG_Pipeline.main --folder-id "1ABC123XYZ456_GoogleDriveFolderID"
```

## Database Schema

The pipeline uses a `documents` table with the following columns:

- `id` (SERIAL PRIMARY KEY): Auto-incrementing ID
- `content` (TEXT): Content of the text chunk
- `metadata` (JSONB): Contains file_id, file_url, and file_title
- `embedding` (VECTOR): OpenAI embedding vector

## How It Works

1. The pipeline authenticates with Google Drive API
2. It periodically checks for changes in Google Drive (either all files or within a specific folder and its subfolders)
3. When a file is created or updated:
   - The file is downloaded
   - Text is extracted from the file
   - The text is split into chunks of 400 characters
   - OpenAI embeddings are created for each chunk
   - Any existing records for the file are deleted from Supabase
   - The new chunks and embeddings are inserted into Supabase
4. When a file is deleted from Google Drive:
   - All records for that file are deleted from Supabase

## Supported File Types

- PDF documents
- Plain text files
- HTML files
- CSV files
- Google Docs

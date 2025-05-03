# Docker Compose Setup for Pydantic AI Agent (Production)

This Docker Compose configuration simplifies the production environment setup for the Pydantic AI Agent by containerizing the application components while leveraging cloud services for infrastructure.

## Services Included

- **Agent**: The main Pydantic AI agent with Streamlit UI
- **RAG Pipeline**: Service for processing and indexing documents from Google Drive
- **MCP Server**: Deno server for code execution (optional)
- **PostgreSQL**: Included for local development/testing only (disabled in production)

## Cloud Services Used

- **OpenAI**: For LLM and embedding models
- **Supabase**: Hosted database with pgvector for RAG and document storage
- **Google Drive**: For document source in the RAG pipeline
- **Brave Search**: For web search capability

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)
- OpenAI API key
- Supabase project with pgvector extension enabled
- Brave Search API key
- Google Drive API credentials

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_key
SUPABASE_POSTGRES_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Brave Search API
BRAVE_API_KEY=your_brave_api_key
```

## Getting Started

1. Set up Google Drive API credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (choose "Desktop App" when prompted)
   - Download the credentials JSON file and save it in a `credentials` directory:
     ```bash
     mkdir -p credentials
     # Place your credentials.json file in this directory
     ```

2. Configure the Google Drive RAG pipeline:
   - Edit `4_Pydantic_AI_Agent/RAG_Pipeline/Google_Drive/config.json` to specify the folders to watch
   - Example:
     ```json
     {
       "watch_directory": "your_google_drive_folder_id"
     }  
     ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the Streamlit UI:
   - Open http://localhost:8501 in your browser

## Database Setup

Before using the agent, you need to set up the necessary tables in your Supabase project:

1. Navigate to the SQL Editor in your Supabase dashboard
2. Run each of the following SQL scripts from the `4_Pydantic_AI_Agent/sql` directory:
   - `documents.sql`: Creates the documents table with vector embeddings
   - `document_metadata.sql`: Creates the document metadata table
   - `document_rows.sql`: Creates the table for tabular data
   - `execute_sql_rpc.sql`: Creates the RPC function for executing SQL queries

## Customizing Configuration

You can modify the `docker-compose.yml` file to:
- Change model selections
- Adjust environment variables
- Add or remove services

## Local Development

For local development and testing, you can use the included PostgreSQL service:

```bash
docker-compose --profile dev up -d
```

This will start the PostgreSQL service along with the other services.

## Stopping the Services

To stop all services:
```bash
docker-compose down
```

## Troubleshooting

- **API Key Issues**: Ensure all API keys are correctly set in the `.env` file
- **Google Drive Authentication**: Check that the credentials.json file is correctly placed and has the right permissions
- **Database Connection Problems**: Verify your Supabase connection string is correct
- **Missing Tables**: Confirm that all required SQL scripts have been executed in Supabase

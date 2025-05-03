# AI Agent Mastery Project Planning

This document outlines the high-level design for building the MVP of our AI Agent Mastery agent built with Pydantic AI and based on our n8n agent prototype. This agent will have Agentic RAG capabilities, short term and long term memory, and the ability to search the internet, analyze images, and execute code it creates.

We will be able to configure this agent to run entirely locally! There is not a separate agent for the local AI implementation like there is with n8n - that is one of the beauties of coding the agent ourself.

## System Architecture

Our system will consist of the following components (more complex UI with React will come later):

```
                    +----------------+
                    | Streamlit UI   |
                    +--------+-------+
                             |
                    +--------v-------+
                    |   AI Agent     |
                    +--------+-------+
                             |
          +------------------+------------------+
          |                  |                  |
+---------v------+  +--------v-------+  +------v--------+
| Document Store |  | Memory System  |  |  Agent Tools  |
+---------+------+  +--------+-------+  +------+--------+
          |                  |                  |
          |         +--------v-------+          |
          +-------->| Vector Database|<---------+
                    +----------------+
```

### Key Components:

1. **Document Processing Pipeline**
   - File type detection
   - Text extraction (PDF, TXT, DOC, etc.)
   - Tabular data handling (CSV, Excel)
   - Chunking and embedding

2. **Vector Database Integration**
   - Supabase/PostgreSQL with pgvector
   - Document storage and retrieval
   - Metadata management

3. **Memory System**
   - Short-term conversation memory
   - Long-term memory extraction and storage
   - Memory deduplication mechanism

4. **AI Agent**
   - LLM integration (with both local and cloud options)
   - Tool selection and execution
   - Agentic RAG integration

5. **Agent Tools**
   - Web search
   - Image analysis
   - Code execution
   - SQL query generation and execution

6. **Basic User Interface**
   - Streamlit-based chat interface
   - Session management

## Development Phases

The project is organized into five major development phases:

### Phase 1: Core RAG Pipeline
Build the foundation for document processing, text chunking, embedding generation, and vector database integration.

### Phase 2: Memory System
Implement short-term and long-term memory systems with deduplication.

### Phase 3: Agent Implementation
Create the AI agent framework with model abstraction, tool registry, and execution logic.

### Phase 4: Agent Tools
Develop various tools for the agent including document tools, web tools, and utility tools.

### Phase 5: Basic User Interface
Build a simple Streamlit interface for interacting with the agent.

## Environment Configuration

The system will use environment variables for configuration, allowing flexibility in deployment scenarios:

```python
# Base URL for the OpenAI compatible instance
LLM_BASE_URL=

# API key for your LLM provider
LLM_API_KEY=

# The LLM you want to use for the agents.
LLM_CHOICE=

# Base URL for the OpenAI compatible instance that has embedding models
EMBEDDING_BASE_URL=

# API key for your embedding model provider
EMBEDDING_API_KEY=

# The embedding model you want to use for RAG
EMBEDDING_MODEL_CHOICE=

# Supabase configuration
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
```

## File Structure

```
ai-agent-mastery/
├── .env.example               # Example environment variables
├── requirements.txt           # Project dependencies
├── README.md                  # Project documentation
├── PLANNING.md                # This planning document
├── TASKS.md                   # Implementation tasks
├── agent.py                   # Main agent implementation
├── prompt.py                  # Prompt templates
├── tools.py                   # Agent tools
├── streamlit_ui.py            # Streamlit user interface
├── tests/                     # Test directory
│   ├── test_agent.py          # Agent tests
│   ├── test_tools.py          # Tools tests
├── RAG_Pipeline/              # RAG Pipeline components
│   ├── common/                # Common RAG functionality
│   │   ├── db_handler.py      # DB operations for RAG
│   │   ├── text_processor.py  # Functions to prep text for vector DB
│   │   └── tests/             # Tests for common components
│   ├── Google_Drive/          # Google Drive integration
│   │   ├── main.py            # Entrypoint script to start the Google Drive RAG pipeline
│   │   ├── drive_watcher.py   # Main logic to watch for Google Drive changes and insert into the vector DB
│   │   └── tests/             # Tests for Google Drive components
│   └── Local_Files/           # Local file processing
│   │   ├── main.py            # Entrypoint script to start the local file RAG pipeline
│   │   ├── drive_watcher.py   # Main logic to watch for local file changes and insert into the vector DB
│   │   └── tests/             # Tests for local file RAG components
```

## Testing Strategy

Our testing approach covers testing individual components in isolation to start.

## Future Enhancements

The following enhancements are planned for future iterations of the course:

1. **Advanced React-based Frontend**
   - More interactive UI components
   - Better visualization of RAG results
   - Enhanced file management

2. **Containerization with Docker**
   - Docker setup for development environment
   - Docker Compose for multi-container deployment
   - Container orchestration for production

## Enhanced Architecture (Proposed)

Based on analysis of the current implementation, the following architectural improvements are recommended:

### 1. Enhanced Agent Architecture

```
                      +-------------------+
                      |   Streamlit UI    |
                      +--------+----------+
                               |
                      +--------v----------+
                      |    Agent Core     |
                      |  +-------------+  |
                      |  | Planning &  |  |
                      |  | Reasoning   |  |
                      |  +-------------+  |
                      |  | Tool        |  |
                      |  | Selection   |  |
                      |  +-------------+  |
                      |  | Evaluation  |  |
                      |  | System      |  |
                      |  +-------------+  |
                      +--------+-----------+
                               |
        +--------------------+-+-------------------+
        |                    |                     |
+-------v--------+  +--------v-------+  +---------v---------+
| Document Store |  | Memory System  |  |  Agent Tools      |
| +-----------+ |  | +-----------+  |  | +---------------+ |
| | Hybrid    | |  | | Tiered    |  |  | | Tool Registry | |
| | Search    | |  | | Memory    |  |  | +---------------+ |
| +-----------+ |  | +-----------+  |  | | Meta-Tools    | |
| | Re-ranking| |  | | Reflection|  |  | +---------------+ |
| +-----------+ |  | +-----------+  |  | | Error Handling| |
+-------+--------+  +--------+-------+  | +---------------+ |
        |                    |          +---------+---------+
        |           +--------v-------+            |
        +---------->| Vector Database|<-----------+
                    +----------------+
```

### 2. Enhanced Memory Architecture

```
+---------------------------+
|      Memory System        |
+---------------------------+
|                           |
| +---------------------+   |
| | Short-term Memory   |   |
| | (Conversation)      |   |
| +---------------------+   |
|                           |
| +---------------------+   |
| | Medium-term Memory  |   |
| | (Session Context)   |   |
| +---------------------+   |
|                           |
| +---------------------+   |
| | Long-term Memory    |   |
| | (User Preferences)  |   |
| +---------------------+   |
|                           |
| +---------------------+   |
| | Memory Reflection   |   |
| | & Summarization     |   |
| +---------------------+   |
|                           |
+---------------------------+
```

## Development Roadmap

The following roadmap outlines the recommended improvements to be implemented in future iterations:

### Phase 6: Enhanced Planning and Reasoning
- Implement ReAct (Reasoning and Acting) patterns
- Add dedicated planning step in agent workflow
- Develop structured thinking mechanisms for complex reasoning tasks

### Phase 7: Tool Selection and Optimization
- Create intelligent tool selection mechanism
- Implement tool usage tracking and analytics
- Develop meta-tools for complex task chains

### Phase 8: Advanced Memory System
- Implement tiered memory architecture
- Add memory summarization capabilities
- Create memory reflection mechanisms
- Develop relevance-based memory management

### Phase 9: Resilience and Error Handling
- Add comprehensive error recovery strategies
- Implement automatic retries with exponential backoff
- Create fallback mechanisms for tool failures
- Add validation of tool outputs

### Phase 10: Conversation Management
- Implement topic tracking across conversation turns
- Add conversation summarization for lengthy interactions
- Create user preference learning system
- Improve handling of ambiguous queries

### Phase 11: Enhanced RAG Capabilities
- Implement hybrid search (semantic + keyword)
- Add re-ranking of search results based on relevance
- Develop cross-document reasoning capabilities
- Create guided retrieval strategies

### Phase 12: Evaluation and Learning
- Implement self-evaluation of responses
- Add user feedback collection and processing
- Create logging for successful and unsuccessful interactions
- Implement A/B testing for different response strategies

### Phase 13: Agent Personality and Communication
- Define consistent personality in system prompt
- Add support for different communication styles
- Improve handling of emotional context
- Implement multi-modal communication

### Phase 14: Security and Authentication
- Add proper authentication for agent and tools
- Implement rate limiting
- Create audit logging for sensitive operations
- Add content filtering for inputs and outputs

### Phase 15: Technical Improvements
- Centralize configuration management
- Further modularize tools into separate files
- Improve documentation with comprehensive docstrings
- Enhance testing with integration and end-to-end tests
- Implement caching for expensive operations
- Add observability with logging, metrics, and tracing
- Containerize the application with Docker
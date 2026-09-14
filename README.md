# AI Engineering Analyzer

> An AI-powered engineering assistant that analyzes GitHub repositories using specialized AI agents, Retrieval-Augmented Generation (RAG), vector search, and code intelligence.

## Overview

**AI Engineering Analyzer** is a developer-focused platform that analyzes a GitHub repository and generates an engineering report covering areas such as:

* Architecture
* Security
* Testing
* Dependencies
* Docker configuration
* Code quality
* Potential technical risks

Instead of sending an entire codebase to an LLM, the system builds a searchable knowledge base of the repository using **embeddings + vector search**. Specialized AI agents retrieve the most relevant parts of the codebase before performing their analysis.

The project is designed primarily as a **learning and portfolio project** to explore modern Python backend development, AI agents, RAG, vector databases, cloud deployment, and containerization.

---

## Key Features

### Repository Analysis

Users can provide a public GitHub repository URL.

The system:

1. Validates the repository.
2. Retrieves the repository contents.
3. Scans and filters relevant files.
4. Splits source code and documentation into chunks.
5. Generates embeddings.
6. Stores embeddings in Qdrant.
7. Runs specialized AI agents.
8. Critiques the generated findings.
9. Produces a final engineering report.

### Specialized AI Agents

The analysis is divided into specialized agents rather than relying on a single LLM prompt.

Current planned agents:

| Agent              | Responsibility                                          |
| ------------------ | ------------------------------------------------------- |
| Planner Agent      | Determines what analysis needs to be performed          |
| Architecture Agent | Evaluates project structure and architectural patterns  |
| Security Agent     | Identifies potential security issues                    |
| Testing Agent      | Evaluates tests and potentially untested critical paths |
| Dependency Agent   | Reviews dependency configuration                        |
| Docker Agent       | Reviews Dockerfiles and container configuration         |
| Critic Agent       | Reviews findings and challenges unsupported conclusions |
| Report Agent       | Produces the final engineering report                   |

---

# RAG Architecture

The project uses **Retrieval-Augmented Generation** to provide agents with relevant repository context.

Instead of:

```text
Entire Repository
       ↓
      LLM
       ↓
    Analysis
```

the system uses:

```text
Repository
    ↓
File Scanner
    ↓
Chunking
    ↓
Embeddings
    ↓
Qdrant
    ↓
Semantic Retrieval
    ↓
Relevant Code / Documentation
    ↓
AI Agent
    ↓
Analysis
```

This allows agents to retrieve only the pieces of the repository that are relevant to the current task.

---

# Technology Stack

## Frontend

* **Next.js**
* **TypeScript**

The frontend provides a lightweight interface for:

* Submitting repositories
* Monitoring analysis progress
* Viewing agent execution status
* Viewing engineering scores
* Viewing detailed findings
* Viewing the final report

The frontend is intentionally kept lightweight so the primary focus remains on backend and AI engineering.

---

## Backend

* **Python**
* **FastAPI**
* **Pydantic**

FastAPI acts as the primary API layer and coordinates repository analysis, RAG processing, agent execution, and report generation.

---

## AI / LLM

### OpenAI

OpenAI models are used for:

* Agent reasoning
* Code analysis
* Finding generation
* Critique
* Report generation

### LangChain

LangChain is used selectively for AI application components such as:

* Prompt templates
* Retrievers
* Tools
* Structured outputs
* RAG components
* Agent integrations

The project aims to understand the underlying AI/RAG concepts rather than hiding the entire implementation behind a framework.

### Hugging Face

Hugging Face is used to experiment with:

* Open-source embedding models
* Sentence-transformer models
* Alternative embedding approaches
* Local/open-source model inference

The project will allow experimentation between different embedding models and comparison of retrieval quality.

---

# Vector Database

## Qdrant

Qdrant is used as the project's vector database.

Repository content is converted into embeddings and stored alongside metadata such as:

```text
repository
file path
language
chunk index
file type
```

Example:

```text
Repository
    ↓
auth/middleware.py
    ↓
Chunk
    ↓
Embedding
    ↓
Qdrant
```

When an agent needs information, it performs semantic retrieval against Qdrant.

---

# Database

## MongoDB Atlas

MongoDB stores application-level information such as:

```text
Repositories
Analyses
Agent Runs
Findings
Reports
```

MongoDB and Qdrant have intentionally separate responsibilities.

### MongoDB

Stores application state and structured information.

### Qdrant

Stores embeddings and supports semantic/vector search.

---

# High-Level Architecture

```text
                         ┌──────────────────┐
                         │     Next.js      │
                         │    Frontend      │
                         └────────┬─────────┘
                                  │
                                  │ REST API
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │ Python Backend   │
                         └────────┬─────────┘
                                  │
                         ┌────────▼────────┐
                         │ Agent            │
                         │ Orchestrator     │
                         └────────┬────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
       Architecture          Security             Testing
          Agent               Agent                Agent
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  │
                                  ▼
                           Critic Agent
                                  │
                                  ▼
                           Report Agent
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
              Qdrant                           MongoDB
          Vector Database                  Application Data
```

---

# Repository Analysis Pipeline

```text
GitHub Repository
        │
        ▼
Repository Scanner
        │
        ▼
File Filtering
        │
        ▼
Code / Documentation Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Qdrant
        │
        ▼
Planner Agent
        │
        ├──────────────┐
        │              │
        ▼              ▼
Architecture      Security
Agent             Agent
        │              │
        ├──────────────┤
        │              │
        ▼              ▼
Testing          Dependency
Agent              Agent
        │              │
        └───────┬──────┘
                ▼
          Docker Agent
                │
                ▼
          Critic Agent
                │
                ▼
          Report Agent
                │
                ▼
     Engineering Report
```

# AI Multi-Agent Tutoring System 🎓

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![LLM API](https://img.shields.io/badge/LLM-Gemini%20API-purple.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) An intelligent, multi-agent AI tutoring system designed to provide personalized assistance in Mathematics and Physics. This project leverages Google's Agent Development Kit (ADK) principles, the Gemini API for advanced language understanding, and a modular architecture for extendability.

## ✨ Features

* **Multi-Agent Architecture**: A central Tutor Orchestrator agent delegates tasks to specialized Math and Physics agents.
* **Intelligent Query Classification**: Automatically determines the subject of a student's query (Math, Physics, or General).
* **Specialized Agents**:
    * **Math Agent**: Solves mathematical problems, explains concepts, and uses a built-in calculator tool.
    * **Physics Agent**: Explains physics concepts, looks up physical constants and formulas using dedicated tools.
* **Tool Usage**: Agents utilize tools to perform specific tasks:
    * Calculator for mathematical computations.
    * Lookup for physical constants and formulas.
    * Conversation history and learning progress tracking.
* **Conversation History & Context Management**: Agents remember previous interactions within a session to provide context-aware and personalized responses.
* **Learning Progress Tracking**: The system can track a student's understanding level of different concepts.
* **Web Interface**: A user-friendly chat interface built with FastAPI and basic HTML/CSS/JavaScript.
* **Powered by Gemini API**: Utilizes Google's Gemini models for natural language understanding and response generation.

## 🏛️ System Architecture

This AI Tutor is built on a multi-agent system design, inspired by Google's Agent Development Kit (ADK) principles. The architecture emphasizes modularity, tool usage, and intelligent orchestration.

```mermaid
graph LR
    UserInterface["🌐 Web Interface (FastAPI + HTML/JS)"] -->|User Query| APIServer[" FastAPI App (app.py)"];
    APIServer -->|Process Query| OrchestrationEntryPoint["MultiAgentTutoringSystem (main.py)"];

    subgraph MATS_Subgraph [Multi-Agent Tutoring System Orchestration]
        direction LR
        OrchestrationEntryPoint -->|Initial Query| TutorOrchestratorAgent["👤 Tutor Orchestrator Agent"];
        TutorOrchestratorAgent -- uses --> ClassifierTool["classify_student_query (Tool)"];
        ClassifierTool -- runs --> InternalClassifierAgent["🤖 Internal Query Classifier Agent (LLM)"];
        
        TutorOrchestratorAgent -- uses --> ConversationHistoryToolsGroup["📚 Conversation History Tools"];
        
        OrchestrationEntryPoint -- If Math Query --> MathSpecialistAgent["✖️ Math Specialist Agent"];
        OrchestrationEntryPoint -- If Physics Query --> PhysicsSpecialistAgent["🔬 Physics Specialist Agent"];
        OrchestrationEntryPoint -- If General Query --> TutorOrchestratorAgent;

        MathSpecialistAgent -- uses --> CalculatorToolInstance["🧮 Calculator Tool"];
        MathSpecialistAgent -- uses --> ConversationHistoryToolsGroup;
        PhysicsSpecialistAgent -- uses --> ConstantsFormulasToolInstance["🔍 Constants & Formulas Tool"];
        PhysicsSpecialistAgent -- uses --> ConversationHistoryToolsGroup;
    end

    subgraph AllTools [Tools]
        direction TB
        CalculatorToolInstance
        ConstantsFormulasToolInstance
        ConversationHistoryToolsGroup
        ClassifierTool
    end
    
    TutorOrchestratorAgent -->|LLM Interaction| GeminiAPI["🧠 Gemini API"];
    MathSpecialistAgent -->|LLM Interaction| GeminiAPI;
    PhysicsSpecialistAgent -->|LLM Interaction| GeminiAPI;
    InternalClassifierAgent -->|LLM Interaction| GeminiAPI;

    style UserInterface fill:#D6EAF8,stroke:#333,stroke-width:2px
    style APIServer fill:#D1F2EB,stroke:#333,stroke-width:2px
    style OrchestrationEntryPoint fill:#FCF3CF,stroke:#333,stroke-width:2px
    style MATS_Subgraph fill:#FEF9E7,stroke:#CCC,stroke-width:1px,color:#333
    style AllTools fill:#FDEDEC,stroke:#CCC,stroke-width:1px,color:#333
    style GeminiAPI fill:#E8DAEF,stroke:#333,stroke-width:2px

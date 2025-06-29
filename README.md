# 🩺 Interactive Medical Assistant AI

A comprehensive medical assistant AI agent with **intelligent conversation flow** and **automatic memory management**. Built with Model Context Protocol (MCP), Groq LLM, and advanced NLP for natural patient interactions.

## 🌟 **NEW: Interactive Medical Chatbot**

Our latest feature provides a **truly conversational medical assistant** that:
- 🗣️ Conducts natural, empathetic conversations
- 🧠 Automatically extracts and stores medical information
- 📋 Guides patients through structured assessments
- 🔄 Maintains context across multiple interactions
- ⚡ Intelligently manages three types of memory

## 🧠 **Three-Memory Architecture**

### 1. **📅 Episodic Memory** (SQLite)
- Stores dated patient events (visits, symptoms, diagnoses)
- Tracks treatment history and outcomes
- Provides temporal context for patient care

### 2. **🧠 Semantic Memory** (SQLite)
- Stores static medical facts (conditions, allergies, medications)
- Uses intelligent text search for fact retrieval
- Enables context-aware medical knowledge access

### 3. **👤 Behavioral Memory** (SQLite)
- Tracks patient behavior patterns (missed appointments, preferences)
- Records communication preferences and adherence patterns
- Enables personalized care approaches

## 🚀 **Key Features**

### **Interactive Conversation Flow**
- **Natural Assessment**: Guides patients through medical assessment naturally
- **Empathetic Responses**: Uses appropriate medical communication tone
- **Context Awareness**: Remembers conversation history and patient information
- **Intelligent Follow-ups**: Asks relevant questions based on responses

### **Automatic Memory Management**
- **Smart Extraction**: Automatically identifies symptoms, conditions, medications
- **Priority Classification**: Categorizes information by medical importance
- **Confidence Scoring**: Assigns confidence levels to extracted information
- **Cross-Memory Integration**: Stores information in appropriate memory systems

### **Advanced Intelligence**
- **Critical Alert Detection**: Identifies emergency symptoms and allergies
- **Pattern Recognition**: Detects behavioral patterns and preferences
- **Context Enhancement**: Uses existing patient data to improve accuracy
- **Conversation State Management**: Tracks conversation progress intelligently

## 🛠️ **Technology Stack**

- **Frontend**: Streamlit (Modern web UI)
- **AI Model**: Groq (Llama 3.1 70B)
- **Memory Protocol**: Model Context Protocol (MCP)
- **Databases**: SQLite (All three memory types)
- **NLP**: Advanced pattern matching + LLM extraction
- **Package Manager**: UV (Python package management)

## 📦 **Installation & Setup**

### Prerequisites
- Python 3.10+
- UV package manager
- Groq API key

### 1. Clone and Setup
```bash
# Navigate to your project directory
cd your-project-directory

# Install dependencies with UV
uv sync
```

### 2. Environment Variables
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Database Initialization
The SQLite databases will be created automatically on first run:
- `medical_memory.db` - For episodic memory (visits)
- `behavioral_memory.db` - For behavioral memory (patterns)
- `semantic_memory.db` - For semantic memory (facts)

## 🚀 **Quick Start**

### **Option 1: Interactive Chatbot (Recommended)**
```bash
uv run python run_interactive_chatbot.py
```
Choose option 1 for the advanced conversational interface.

### **Option 2: Web Interface**
```bash
uv run streamlit run medical_assistant_ui.py
```
Access at: http://localhost:8501

### **Option 3: Simple Chat**
```bash
uv run python app.py
```

## 💻 **Using the Interactive Chatbot**

### **Conversation Flow**
1. **Greeting**: Chatbot introduces itself warmly
2. **Patient Info**: Asks for name and patient ID
3. **Chief Complaint**: Explores main health concern
4. **Symptom Assessment**: Systematic symptom evaluation
5. **Medical History**: Gathers relevant medical background
6. **Lifestyle Assessment**: Explores relevant lifestyle factors
7. **Summary Confirmation**: Reviews and confirms information
8. **Next Steps**: Provides recommendations and next steps

### **Automatic Information Extraction**
The chatbot automatically identifies and stores:

**Critical Information (Highest Priority)**
- 🚨 Allergies and adverse reactions
- 🚨 Emergency symptoms
- 🚨 Critical medications

**Medical Facts (High Priority)**
- 🏥 Medical conditions and diagnoses
- 💊 Current medications and dosages
- 👨‍👩‍👧‍👦 Family medical history

**Behavioral Patterns (Medium Priority)**
- 📞 Communication preferences
- ⏰ Appointment preferences
- 💊 Medication adherence patterns

**Current Symptoms (Variable Priority)**
- 😷 Current symptoms and severity
- 📅 Recent health events
- 🔄 Symptom progression

## 🧠 **Intelligent Memory Logic**

### **Priority Classification**
- **CRITICAL**: Allergies, emergency conditions, life-threatening symptoms
- **HIGH**: Chronic conditions, current medications, significant symptoms
- **MEDIUM**: Lifestyle factors, mild symptoms, preferences
- **LOW**: General notes, minor preferences

### **Confidence Scoring**
- **High (0.8-1.0)**: Clear, explicit medical statements
- **Medium (0.6-0.8)**: Implied or contextual information
- **Low (0.0-0.6)**: Uncertain or ambiguous information

### **Smart Storage Logic**
- **Semantic Memory**: Facts that don't change (allergies, chronic conditions)
- **Episodic Memory**: Time-based events (symptoms, visits, treatments)
- **Behavioral Memory**: Patterns and preferences (communication, scheduling)

### **Context Enhancement**
- Cross-references new information with existing patient data
- Improves confidence scores based on consistency
- Detects contradictions and flags for clarification

## 🎯 **Example Conversation**

```
Assistant: Hello! I'm your medical assistant. I'm here to help you with your
health concerns. Could you please tell me your name and patient ID?

Patient: Hi, I'm Sarah Johnson, patient ID P123. I'm having chest pain.
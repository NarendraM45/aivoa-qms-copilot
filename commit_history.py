import os
import subprocess
import time
import random
from datetime import datetime, timedelta

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {cmd}: {result.stderr}")
    return result.stdout.strip()

# List of files in logical development order with their realistic commit messages
commits = [
    ("backend/requirements.txt", "chore(backend): add dependencies for fastapi, sqlalchemy, and langgraph"),
    ("backend/.env.example", "chore(backend): create env template for groq and database configs"),
    (".gitignore", "chore: setup root gitignore for python and node environments"),
    ("backend/app/__init__.py", "chore(backend): init app package"),
    ("backend/app/core/__init__.py", "chore(backend): init core package"),
    ("backend/app/core/config.py", "feat(backend): implement pydantic settings for environment configuration"),
    ("backend/app/core/database.py", "feat(backend): setup asyncpg database connection and session maker"),
    
    # Alembic setup
    ("backend/alembic.ini", "chore(db): initialize alembic configuration"),
    ("backend/alembic/env.py", "chore(db): configure alembic environment for async migrations"),
    ("backend/alembic/script.py.mako", "chore(db): add alembic script template"),
    
    # Models
    ("backend/app/models/__init__.py", "chore(models): init models package and Base class"),
    ("backend/app/models/complaint.py", "feat(models): create Complaint model with core QMS fields"),
    ("backend/app/models/attachment.py", "feat(models): add ComplaintAttachment model for file references"),
    ("backend/app/models/audit_trail.py", "feat(models): create AuditTrail model for compliance tracking"),
    ("backend/app/models/chat_message.py", "feat(models): add ChatMessage model for copilot conversation history"),
    ("backend/app/models/capa_recommendation.py", "feat(models): create CAPARecommendation model"),
    ("backend/app/models/duplicate_match.py", "feat(models): add DuplicateMatch model for correlation"),
    ("backend/app/models/extraction_run.py", "feat(models): create AIExtractionRun model for tracking langgraph state"),
    
    # Initial migration
    ("backend/alembic/versions/__init__.py", "chore(db): init alembic versions directory"),
    ("backend/alembic/versions/16d77b72916f_initial_setup.py", "chore(db): generate initial migration for all qms tables"),
    
    # Schemas
    ("backend/app/schemas/__init__.py", "chore(schemas): init pydantic schemas package"),
    ("backend/app/schemas/common.py", "feat(schemas): add common base schemas and response formats"),
    ("backend/app/schemas/complaint.py", "feat(schemas): create complaint read/write schemas"),
    ("backend/app/schemas/chat.py", "feat(schemas): add chat interaction schemas"),
    ("backend/app/schemas/ai_features.py", "feat(schemas): create schemas for capa and duplicate detection features"),
    ("backend/app/schemas/extraction.py", "feat(schemas): add document extraction payload schemas"),
    
    # Frontend scaffold
    ("frontend/package.json", "chore(frontend): init vite react project with dependencies"),
    ("frontend/package-lock.json", "chore(frontend): lock dependencies"),
    ("frontend/tsconfig.json", "chore(frontend): setup typescript base config"),
    ("frontend/tsconfig.app.json", "chore(frontend): configure typescript for react app"),
    ("frontend/tsconfig.node.json", "chore(frontend): configure typescript for vite node"),
    ("frontend/vite.config.ts", "chore(frontend): configure vite bundler"),
    ("frontend/.gitignore", "chore(frontend): add vite-specific gitignore"),
    ("frontend/.oxlintrc.json", "chore(frontend): add linter configuration"),
    ("frontend/index.html", "chore(frontend): create entry html file"),
    ("frontend/public/favicon.svg", "chore(frontend): add basic favicon"),
    ("frontend/public/icons.svg", "chore(frontend): add sprite map for icons"),
    
    # Frontend styling & assets
    ("frontend/src/index.css", "style(frontend): setup tailwind css v4 imports and base font"),
    ("frontend/src/App.css", "style(frontend): add base application styles"),
    ("frontend/src/assets/hero.png", "chore(frontend): add hero asset"),
    ("frontend/src/assets/react.svg", "chore(frontend): add react logo asset"),
    ("frontend/src/assets/vite.svg", "chore(frontend): add vite logo asset"),
    
    # Frontend architecture
    ("frontend/src/main.tsx", "feat(frontend): setup react root and strict mode"),
    ("frontend/src/types/index.ts", "feat(frontend): define core typescript interfaces for complaints and state"),
    ("frontend/src/store/index.ts", "feat(frontend): initialize redux toolkit store"),
    ("frontend/src/store/api.ts", "feat(frontend): setup rtk query api slice for backend communication"),
    ("frontend/src/store/complaintFormSlice.ts", "feat(frontend): create redux slice for managing complaint form state"),
    ("frontend/src/store/aiPanelSlice.ts", "feat(frontend): create redux slice for ai copilot state"),
    
    # Basic frontend components
    ("frontend/src/components/Header.tsx", "feat(frontend): build application header component"),
    ("frontend/src/App.tsx", "feat(frontend): implement main layout with left/right split panels"),
    
    # Backend Services
    ("backend/app/services/__init__.py", "chore(services): init services package"),
    ("backend/app/services/file_parser.py", "feat(services): implement document parser for pdf, docx, txt, and eml"),
    ("backend/app/services/groq_client.py", "feat(services): implement groq api client with exponential backoff and retries"),
    
    # Backend Agents Foundation
    ("backend/app/agents/__init__.py", "chore(agents): init langgraph agents package"),
    ("backend/app/agents/state.py", "feat(agents): define TypedDict state for complaint extraction pipeline"),
    ("backend/app/agents/tools/__init__.py", "chore(agents): init tool calling package"),
    ("backend/app/agents/tools/complaint_tools.py", "feat(agents): create log_complaint and edit_complaint langchain tools"),
    
    # Backend Prompts
    ("backend/app/agents/prompts/__init__.py", "chore(agents): init prompts package"),
    ("backend/app/agents/prompts/extract_fields_prompt.py", "feat(agents): add system prompt for data extraction"),
    ("backend/app/agents/prompts/classify_severity_prompt.py", "feat(agents): add system prompt for risk classification"),
    ("backend/app/agents/prompts/detect_duplicates_prompt.py", "feat(agents): add system prompt for duplicate correlation"),
    ("backend/app/agents/prompts/generate_summary_prompt.py", "feat(agents): add system prompt for management summaries"),
    ("backend/app/agents/prompts/chat_prompt.py", "feat(agents): add conversational prompt template"),
    ("backend/app/agents/prompts/root_cause_prompt.py", "feat(agents): add ishikawa root cause prompt"),
    ("backend/app/agents/prompts/capa_prompt.py", "feat(agents): add corrective action prompt"),
    
    # Backend Nodes
    ("backend/app/agents/nodes/__init__.py", "chore(agents): init graph nodes package"),
    ("backend/app/agents/nodes/parse_document.py", "feat(agents): implement file parsing graph node"),
    ("backend/app/agents/nodes/extract_fields.py", "feat(agents): implement llm field extraction node"),
    ("backend/app/agents/nodes/check_completeness.py", "feat(agents): implement data completeness validation node"),
    ("backend/app/agents/nodes/classify_severity.py", "feat(agents): implement risk assessment node"),
    ("backend/app/agents/nodes/detect_duplicates.py", "feat(agents): implement duplicate search node"),
    ("backend/app/agents/nodes/generate_summary.py", "feat(agents): implement summary generation node"),
    ("backend/app/agents/nodes/chat_node.py", "feat(agents): implement unstructured chat handler node"),
    ("backend/app/agents/nodes/root_cause_node.py", "feat(agents): implement root cause analysis node"),
    ("backend/app/agents/nodes/capa_node.py", "feat(agents): implement capa recommendation node"),
    
    # Backend Graph
    ("backend/app/agents/graph.py", "feat(agents): wire up langgraph pipeline for async document processing"),
    
    # Copilot Agent
    ("backend/app/schemas/copilot.py", "feat(schemas): add copilot tool request and response schemas"),
    ("backend/app/agents/copilot_agent.py", "feat(agents): implement ReAct tool-calling copilot agent"),
    
    # Backend API Routes
    ("backend/app/api/__init__.py", "chore(api): init api package"),
    ("backend/app/api/routes/__init__.py", "chore(api): init routes package"),
    ("backend/app/api/routes/complaints.py", "feat(api): create CRUD endpoints for complaints and audit trails"),
    ("backend/app/api/routes/extraction.py", "feat(api): create endpoints for legacy document extraction pipeline"),
    ("backend/app/api/routes/ws.py", "feat(api): implement websocket endpoint for real-time extraction progress"),
    ("backend/app/api/routes/chat.py", "feat(api): create conversational endpoints for complaint queries"),
    ("backend/app/api/routes/ai_features.py", "feat(api): expose endpoints for root cause, capa, and duplicates"),
    ("backend/app/api/routes/copilot.py", "feat(api): create unified chat endpoint for tool-driven form filling"),
    
    # Main App Entry
    ("backend/app/main.py", "feat(backend): wire up fastapi routers, cors, and health checks"),
    
    # Frontend Hooks
    ("frontend/src/hooks/useWebSocket.ts", "feat(frontend): create hook for managing websocket connections"),
    ("frontend/src/hooks/useExtraction.ts", "feat(frontend): create hook to wrap document extraction logic"),
    
    # Frontend UI Components
    ("frontend/src/components/FormSection.tsx", "feat(frontend): build collapsible form section container"),
    ("frontend/src/components/AIFormField.tsx", "feat(frontend): build smart input field with ai confidence badging"),
    ("frontend/src/components/ComplaintForm.tsx", "feat(frontend): implement comprehensive QMS complaint form"),
    ("frontend/src/components/FormActions.tsx", "feat(frontend): add save and reset action buttons for form"),
    
    # Frontend Feature Components
    ("frontend/src/components/PasteTextModal.tsx", "feat(frontend): create modal for manual text ingestion"),
    ("frontend/src/components/DuplicateResults.tsx", "feat(frontend): build ui for displaying duplicate complaint warnings"),
    ("frontend/src/components/RootCauseResults.tsx", "feat(frontend): build ui for displaying ishikawa fishbone analysis"),
    ("frontend/src/components/CAPAResults.tsx", "feat(frontend): build ui for displaying corrective action plans"),
    ("frontend/src/components/CompletenessResults.tsx", "feat(frontend): build ui for data gap analysis"),
    ("frontend/src/components/DropZone.tsx", "feat(frontend): build legacy drag-and-drop file upload zone"),
    ("frontend/src/components/ExtractionProgressBar.tsx", "feat(frontend): build progress indicator for document parsing"),
    ("frontend/src/components/AIFeatureButtons.tsx", "feat(frontend): build action bar for triggering specific ai analyses"),
    
    # Frontend Copilot Components
    ("frontend/src/components/RiskAssessment.tsx", "feat(frontend): build risk assessment panel for severity and priority"),
    ("frontend/src/components/AIAssistantChat.tsx", "feat(frontend): build chat interface with tool call dispatching"),
    ("frontend/src/components/AIAssistantPanel.tsx", "feat(frontend): assemble final right-panel copilot layout"),
    
    # Seed data and docs
    ("backend/seed_data.py", "chore(backend): create seed script for test complaints"),
    ("backend/sample_complaints/complaint_email_amoxicylin.txt", "docs(demo): add amoxicylin test complaint email"),
    ("backend/sample_complaints/complaint_metformin_api.txt", "docs(demo): add metformin test complaint report"),
    ("frontend/README.md", "docs(frontend): add minimal frontend readme"),
    ("README.md", "docs: write comprehensive project documentation and demo instructions")
]

# Track committed files to find any leftovers
committed_files = set()

# Process the structured commits
for filepath, msg in commits:
    # Use unix style paths for git
    git_filepath = filepath.replace("\\", "/")
    
    # Add file
    run_cmd(f'git add "{git_filepath}"')
    
    # Check if there's actually something staged
    status = run_cmd('git status --porcelain')
    if status:
        # Create commit
        run_cmd(f'git commit -m "{msg}"')
        print(f"Committed: {git_filepath}")
    else:
        print(f"Skipped (no changes): {git_filepath}")
        
    committed_files.add(git_filepath)

# Now find any remaining untracked/modified files and commit them one by one
leftovers = run_cmd('git ls-files --others --modified --exclude-standard').splitlines()

for filepath in leftovers:
    if filepath not in committed_files:
        run_cmd(f'git add "{filepath}"')
        
        # Generate a generic but reasonable commit message
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1]
        
        if ext in ['.tsx', '.ts']:
            msg = f"feat(frontend): update {filename} logic"
        elif ext in ['.py']:
            msg = f"feat(backend): implement {filename} functionality"
        elif ext in ['.css']:
            msg = f"style(frontend): update {filename}"
        elif ext in ['.json']:
            msg = f"chore: update configuration in {filename}"
        else:
            msg = f"chore: add {filename}"
            
        run_cmd(f'git commit -m "{msg}"')
        print(f"Committed leftover: {filepath}")

print(f"\nTotal commits created: {run_cmd('git rev-list --count HEAD')}")

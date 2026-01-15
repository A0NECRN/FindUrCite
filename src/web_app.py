import streamlit as st
import sys
import os
import time
import json
from utils import get_output_dir, save_json, load_json

import shutil

sys.path.append(os.path.dirname(__file__))

from main import ResearchPipeline
from cache import AnalysisCache

st.set_page_config(
    page_title="FindUrCite AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* Card Styling */
    .stExpander {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 0.5rem;
    }
    
    .stExpander > details > summary {
        font-weight: 600;
        color: #1f2937;
    }

    /* Chat Messages */
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #eef2ff;
        border: 1px solid #c7d2fe;
    }
    .chat-message.bot {
        background-color: #f3f4f6;
        border: 1px solid #e5e7eb;
    }
    .chat-message .avatar {
      width: 45px; height: 45px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px; background: white; border: 1px solid #ddd;
      margin-right: 15px;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Paper Context Highlight */
    .highlight-paper {
        border-left: 4px solid #6366f1;
        padding: 10px 15px;
        margin: 10px 0;
        background-color: #f8fafc;
        border-radius: 0 8px 8px 0;
        color: #475569;
        font-size: 0.9em;
    }
    
    /* Status Bar */
    .stProgress > div > div > div > div {
        background-color: #4f46e5;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px;
        padding: 4px 16px;
        background-color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #eef2ff;
        color: #4f46e5;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)

def get_project_root_dir():
    # Use the research_results directory as the root for all projects
    return get_output_dir()

def get_session_file():
    # Helper to get the session file path based on current project
    project_dir = st.session_state.get("current_project_dir", os.path.join(get_project_root_dir(), "Default_Project"))
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    return os.path.join(project_dir, "session_state.json")

def save_session():
    state = {
        "messages": st.session_state.get("messages", []),
        "papers": st.session_state.get("papers", []),
        "logs": st.session_state.get("logs", []),
        "status": st.session_state.get("status", ""),
        "progress": st.session_state.get("progress", 0),
        "user_input": st.session_state.get("user_input_val", "")
    }
    # Ensure paper status is saved
    for p in st.session_state.papers:
        if 'status' not in p:
            p['status'] = 'inbox' # Default status
            
    save_json(state, get_session_file())

def load_session_state():
    session_file = get_session_file()
    data = load_json(session_file)
    if data:
        st.session_state.messages = data.get("messages", [])
        st.session_state.papers = data.get("papers", [])
        # Backfill status if missing
        for p in st.session_state.papers:
            if 'status' not in p:
                p['status'] = 'inbox'
                
        st.session_state.logs = data.get("logs", [])
        st.session_state.status = data.get("status", "")
        st.session_state.progress = data.get("progress", 0)
        return data.get("user_input", "")
    return ""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "papers" not in st.session_state:
    st.session_state.papers = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "status" not in st.session_state:
    st.session_state.status = ""
if "progress" not in st.session_state:
    st.session_state.progress = 0

# last_input will be loaded after project selection


# --- Helper Functions ---
def update_paper_status(paper_id, new_status, useful_type=None):
    for p in st.session_state.papers:
        if p['paper']['paperId'] == paper_id:
            p['status'] = new_status
            if useful_type:
                p['useful_type'] = useful_type
            save_session()
            st.rerun()
            break

def render_paper_card(item, mode="inbox", read_only=False):
    paper = item['paper']
    paper_id = paper.get('paperId', str(hash(paper['title']))) # Fallback ID
    
    with st.expander(f"📄 {paper['title'][:40]}...", expanded=False):
        st.markdown(f"**Year:** {paper.get('year')} | **Venue:** {paper.get('venue')}")
        st.markdown(f"**Authors:** {', '.join(paper.get('authors', [])[:2])}")
        
        # PDF Download
        pdf_path = item.get('pdf_path')
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button("📥 PDF", f, file_name=os.path.basename(pdf_path), key=f"dl_{paper_id}_{time.time()}")
        elif paper.get('openAccessPdf'):
            url = paper.get('openAccessPdf', {}).get('url')
            if url:
                st.markdown(f"[🌐 Open PDF]({url})")
        
        # Analysis Score
        if 'analysis' in item:
            score = item['analysis'].get('relevance_score', 0)
            st.markdown(f"**Score:** {score}/10")

        st.divider()
        
        # Action Buttons
        # Info sections should be visible even in read_only mode, but action buttons hidden
        col_a, col_b = st.columns(2)
        
        if mode == "inbox":
            # Show Reasoning/Critique
            if 'analysis' in item:
                analysis = item['analysis']
                with st.expander("🧐 Why this paper?", expanded=True):
                    if analysis.get('match_reasoning'):
                        st.markdown(f"**Match:** {analysis['match_reasoning']}")
                    if analysis.get('defense'):
                        st.markdown(f"**Defense:** {analysis['defense']}")
            
            if not read_only:
                with col_a:
                    useful_type = st.selectbox("Type", ["Support", "Technique", "Benchmark"], key=f"type_{paper_id}", label_visibility="collapsed")
                    if st.button("✅ Keep", key=f"keep_{paper_id}"):
                        update_paper_status(paper_id, "useful", useful_type)
                with col_b:
                    if st.button("🗑️ Reject", key=f"rej_{paper_id}"):
                        update_paper_status(paper_id, "rejected")
        
        elif mode == "useful":
            st.success(f"Type: {item.get('useful_type', 'General')}")
            if 'analysis' in item:
                    with st.expander("💡 Key Contribution", expanded=False):
                        st.markdown(item['analysis'].get('match_reasoning', ''))
            
            if not read_only:
                if st.button("⏪ Move to Inbox", key=f"back_{paper_id}"):
                    update_paper_status(paper_id, "inbox")
                
        elif mode == "rejected":
            st.error("Rejected / 已驳回")
            if 'analysis' in item:
                    with st.expander("❌ Rejection Reason / 驳回原因", expanded=True):
                        critique = item['analysis'].get('critique', '')
                        if not critique:
                                # Try to find critique in debate events? simplified: just show low score reason
                                critique = "Low relevance score."
                        st.markdown(critique)

            if not read_only:
                if st.button("⏪ Move to Inbox", key=f"back_rej_{paper_id}"):
                    update_paper_status(paper_id, "inbox")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/student-center.png", width=80)
    st.title("FindUrCite")
    st.caption("AI-Powered Research Assistant")
    
    st.divider()
    
    # --- Project Management ---
    st.markdown("### 📂 Project Management")
    
    root_dir = get_project_root_dir()
    if not os.path.exists(root_dir): os.makedirs(root_dir)
    
    # Filter only directories
    projects = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
    if not projects:
        projects = ["Default_Project"]
        if not os.path.exists(os.path.join(root_dir, "Default_Project")):
            os.makedirs(os.path.join(root_dir, "Default_Project"))
            
    if "current_project_name" not in st.session_state:
        st.session_state.current_project_name = projects[0]
        
    # Ensure current project is in list
    if st.session_state.current_project_name not in projects:
         st.session_state.current_project_name = projects[0]

    selected_project = st.selectbox("Current Project", projects, index=projects.index(st.session_state.current_project_name))
    
    with st.expander("➕ Create New Project"):
        new_proj_name = st.text_input("New Project Name", placeholder="MyNewResearch", help="Create a separate workspace for a different research topic. Keeps data isolated.")
        if st.button("Create Project"):
            if new_proj_name and new_proj_name not in projects:
                # Sanitize name
                safe_name = "".join([c for c in new_proj_name if c.isalnum() or c in (' ', '_', '-')]).strip()
                if safe_name:
                    os.makedirs(os.path.join(root_dir, safe_name))
                    st.session_state.current_project_name = safe_name
                    st.success(f"Created {safe_name}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid name")
            elif new_proj_name in projects:
                st.error("Project exists!")

    # Delete Project Logic
    if st.session_state.current_project_name != "Default_Project":
        with st.expander("🗑️ Delete Project"):
            st.warning(f"Are you sure you want to delete '{st.session_state.current_project_name}'? This action cannot be undone.")
            if st.button("Confirm Delete", type="primary"):
                try:
                    shutil.rmtree(os.path.join(root_dir, st.session_state.current_project_name))
                    st.session_state.current_project_name = "Default_Project"
                    st.toast("Project deleted successfully!", icon="🗑️")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting project: {e}")

    # Switch Project Logic
    if selected_project != st.session_state.current_project_name:
        st.session_state.current_project_name = selected_project
        # Reset State for new project
        st.session_state.messages = []
        st.session_state.papers = []
        st.session_state.logs = []
        st.session_state.status = ""
        st.session_state.progress = 0
        if "user_input_val" in st.session_state: del st.session_state.user_input_val
        st.rerun()

    # Set Current Project Dir in Session
    st.session_state.current_project_dir = os.path.join(root_dir, st.session_state.current_project_name)
    
    # Load session state for the selected project
    # We do this here to ensure 'last_input' is available for the main area
    last_input = load_session_state() if "user_input_val" not in st.session_state else st.session_state.get("user_input_val", "")

    st.divider()
    
    # Load model name from environment variable (set by run.bat) or default
    default_model = os.environ.get("MODEL_NAME", "qwen2.5:7b")
    model_name = st.text_input("Ollama Model", value=default_model)
    
    st.subheader("Configuration")
    # Base output dir is now the project dir, but we allow user to see it (read-only mostly)
    base_output_dir = st.text_input("Project Dir", value=st.session_state.current_project_dir, disabled=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("🧹 Clear Cache"):
            AnalysisCache().clear()
            st.toast("Cache cleared successfully!", icon="🧹")
            time.sleep(0.5)
            st.rerun()
            
    with col_c2:
        if st.button("🔄 New Research", help="Clear current results and start over within this project."):
             st.session_state.messages = []
             st.session_state.papers = []
             st.session_state.logs = []
             st.session_state.status = ""
             st.session_state.progress = 0
             save_session()
             st.rerun()
    
    st.divider()
    st.markdown("### 📊 Status")
    status_placeholder = st.empty()
    if st.session_state.status:
        status_placeholder.info(st.session_state.status)
        
    progress_bar = st.progress(st.session_state.progress)
    
    st.divider()
    st.markdown("### 📚 Literature Manager / 文献管理")
    
    lit_manager_placeholder = st.empty()

    def render_literature_manager(placeholder, read_only=False):
        with placeholder.container():
            # Categorize papers
            inbox_papers = [p for p in st.session_state.papers if p.get('status', 'inbox') == 'inbox']
            useful_papers = [p for p in st.session_state.papers if p.get('status') == 'useful']
            rejected_papers = [p for p in st.session_state.papers if p.get('status') == 'rejected']
            
            tab_inbox, tab_useful, tab_rejected = st.tabs([
                f"📥 Inbox / 收件箱 ({len(inbox_papers)})", 
                f"✅ Useful / 有用 ({len(useful_papers)})", 
                f"🗑️ Rejected / 已驳回 ({len(rejected_papers)})"
            ])
            
            with tab_inbox:
                for p in inbox_papers:
                    render_paper_card(p, "inbox", read_only)
                    
            with tab_useful:
                for p in useful_papers:
                    render_paper_card(p, "useful", read_only)
                    
            with tab_rejected:
                for p in rejected_papers:
                    render_paper_card(p, "rejected", read_only)
    
    # Initial render
    render_literature_manager(lit_manager_placeholder, read_only=False)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Research Context")
    user_input = st.text_area("Enter your abstract, research idea, or draft:", height=400, 
                              value=last_input if last_input else "Retrieval-Augmented Generation for Code Repositories",
                              key="user_input_area")
    
    start_btn = st.button("🚀 Start Deep Research", type="primary")
    
    st.divider()
    st.subheader("📜 System Logs")
    log_container = st.container(height=400)
    for log in st.session_state.logs:
        log_container.text(log)

with col2:
    st.subheader("💬 Multi-Agent Debate Live Feed")
    chat_container = st.container(height=800)
    for msg in st.session_state.messages:
        with chat_container:
            with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                if msg.get("paper_context"):
                    st.markdown(f"<div class='highlight-paper'>📄 <b>Context:</b> {msg['paper_context']}</div>", unsafe_allow_html=True)
                st.markdown(msg["content"])

# Removed old render_paper_card and loop as it is now inside sidebar logic above

if start_btn and user_input:
    st.session_state.messages = []
    st.session_state.papers = []
    st.session_state.logs = []
    st.session_state.progress = 0
    st.session_state.status = "Initializing..."
    st.session_state.user_input_val = user_input
    save_session()
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_output_dir = os.path.join(base_output_dir, timestamp)
    
    pipeline = ResearchPipeline(
        model=model_name,
        output_dir=run_output_dir,
        pdf_dir=os.path.join(run_output_dir, "pdfs")
    )
    
    status_placeholder.info("Initializing...")
    
    try:
        step = 0
        total_steps = 10 
        
        for event in pipeline.run(user_input):
            if event['type'] == 'log':
                log_msg = f"[{time.strftime('%H:%M:%S')}] {event['content']}"
                st.session_state.logs.append(log_msg)
                log_container.text(log_msg)
            
            elif event['type'] == 'status':
                status_msg = f"👉 {event['content']}"
                st.session_state.status = status_msg
                status_placeholder.info(status_msg)
                step += 1
                progress_val = min(step/total_steps, 1.0)
                st.session_state.progress = progress_val
                progress_bar.progress(progress_val)

            elif event['type'] == 'paper_found':
                paper_obj = {'paper': event['paper'], 'status': 'inbox'}
                st.session_state.papers.append(paper_obj)
                # Update sidebar (read only during search to avoid key collision/rerun issues)
                render_literature_manager(lit_manager_placeholder, read_only=True)
            
            elif event['type'] == 'paper_analyzed':
                item = event['item']
                found = False
                for p in st.session_state.papers:
                    if p['paper'].get('paperId') == item['paper'].get('paperId') or p['paper'].get('title') == item['paper'].get('title'):
                        p['analysis'] = item['analysis']
                        if 'codes' in item: p['codes'] = item['codes']
                        
                        score = item['analysis'].get('relevance_score', 0)
                        
                        # Fix: If score is high (approved), move to useful if not already there
                        # But user might want to manually review.
                        # Let's keep it in Inbox but sort/highlight?
                        # Or move to useful if strictly approved?
                        # For now, let's auto-reject low scores, and keep high scores in inbox but updated.
                        
                        if score < 4 and p['status'] == 'inbox':
                            p['status'] = 'rejected'
                        elif score >= 7 and p['status'] == 'inbox':
                            p['status'] = 'useful'
                        # Ensure 'status' persists if it was manually moved
                        
                        found = True
                        break
                if not found:
                     paper_obj = item
                     if item['analysis'].get('relevance_score', 0) < 4:
                        paper_obj['status'] = 'rejected'
                     elif item['analysis'].get('relevance_score', 0) >= 7:
                        paper_obj['status'] = 'useful'
                     else:
                        paper_obj['status'] = 'inbox'
                     st.session_state.papers.append(paper_obj)
                
                # Update sidebar
                render_literature_manager(lit_manager_placeholder, read_only=True)
            
            elif event['type'] == 'pdf_ready':
                log_msg = f"[{time.strftime('%H:%M:%S')}] PDF Downloaded: {event['paper']['title'][:30]}..."
                st.session_state.logs.append(log_msg)
                log_container.text(log_msg)
                
                found = False
                for p in st.session_state.papers:
                    if p['paper'].get('paperId') == event['paper'].get('paperId') or p['paper'].get('title') == event['paper'].get('title'):
                        p['pdf_path'] = event['pdf_path']
                        found = True
                        break
                if not found:
                     st.session_state.papers.append({'paper': event['paper'], 'pdf_path': event['pdf_path']})
                
            elif event['type'] == 'debate_event':
                data = event['data']
                role = data.get('role', 'system')
                content = data.get('content', '')
                paper_title = event.get('paper_title')
                
                msg_obj = {"role": "system", "content": content, "avatar": "⚙️", "paper_context": paper_title}
                
                if role == 'student':
                    msg_obj = {"role": "assistant", "content": content, "avatar": "🧑‍🎓", "paper_context": paper_title}
                elif role == 'advisor':
                    msg_obj = {"role": "assistant", "content": content, "avatar": "👨‍🏫", "paper_context": paper_title}
                
                st.session_state.messages.append(msg_obj)
                with chat_container:
                    with st.chat_message(msg_obj["role"], avatar=msg_obj["avatar"]):
                        if msg_obj.get("paper_context"):
                            st.markdown(f"<div class='highlight-paper'>📄 <b>Context:</b> {msg_obj['paper_context']}</div>", unsafe_allow_html=True)
                        st.markdown(msg_obj["content"])
            
            elif event['type'] == 'result':
                st.session_state.status = "Research Completed!"
                st.session_state.progress = 1.0
                status_placeholder.success("Research Completed!")
                progress_bar.progress(1.0)
                
                synthesis = event.get('synthesis')
                if synthesis:
                    content = f"### 🧠 Global Synthesis\n**State of the Art**: \n{synthesis.get('state_of_art_summary')}\n**Gap Analysis**: \n{synthesis.get('gap_analysis')}\n**Strategic Recommendations**: \n{synthesis.get('strategic_recommendations')}"
                    msg_obj = {"role": "assistant", "content": content, "avatar": "🧠", "paper_context": "Final Report"}
                    st.session_state.messages.append(msg_obj)
                    with chat_container:
                         with st.chat_message("assistant", avatar="🧠"):
                            st.markdown(content)

                report_path = os.path.join(event['output_dir'], "research_result.md")
                if os.path.exists(report_path):
                    with open(report_path, "r", encoding="utf-8") as f:
                        st.download_button("📥 Download Full Report", f, file_name="research_result.md")
                            
            elif event['type'] == 'error':
                st.error(event['content'])
            
            save_session()
        
        # Final render with interactivity enabled
        render_literature_manager(lit_manager_placeholder, read_only=False)
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
        import traceback
        st.text(traceback.format_exc())

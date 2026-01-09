import streamlit as st
import sys
import os
import time
import json
from utils import get_output_dir, save_json, load_json

sys.path.append(os.path.dirname(__file__))

from main import ResearchPipeline

st.set_page_config(
    page_title="FindUrCite AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
    }
    .chat-message.user {
        background-color: #2b313e
    }
    .chat-message.bot {
        background-color: #475063
    }
    .chat-message .avatar {
      width: 20%;
    }
    .chat-message .message {
      width: 80%;
    }
    h1, h2, h3 {
        color: #0e1117;
    }
    .stButton>button {
        width: 100%;
    }
    .highlight-paper {
        border-left: 5px solid #FF4B4B;
        padding-left: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
        background-color: #f0f2f6;
        color: #31333F;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

SESSION_FILE = os.path.join(get_output_dir(), "session_state.json")

def save_session():
    state = {
        "messages": st.session_state.get("messages", []),
        "papers": st.session_state.get("papers", []),
        "logs": st.session_state.get("logs", []),
        "status": st.session_state.get("status", ""),
        "progress": st.session_state.get("progress", 0),
        "user_input": st.session_state.get("user_input_val", "")
    }
    save_json(state, SESSION_FILE)

def load_session_state():
    data = load_json(SESSION_FILE)
    if data:
        st.session_state.messages = data.get("messages", [])
        st.session_state.papers = data.get("papers", [])
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

last_input = load_session_state() if "user_input_val" not in st.session_state else st.session_state.get("user_input_val", "")

with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/student-center.png", width=80)
    st.title("FindUrCite")
    st.caption("AI-Powered Research Assistant")
    
    st.divider()
    
    model_name = st.text_input("Ollama Model", value="qwen2.5:7b")
    
    st.subheader("Configuration")
    base_output_dir = st.text_input("Output Dir", value=get_output_dir())
    
    st.divider()
    st.markdown("### 📊 Status")
    status_placeholder = st.empty()
    if st.session_state.status:
        status_placeholder.info(st.session_state.status)
        
    progress_bar = st.progress(st.session_state.progress)
    
    st.divider()
    st.markdown("### 📚 Found Papers")
    papers_container = st.container()

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

def render_paper_card(paper, pdf_path=None):
    with papers_container:
        with st.expander(f"📄 {paper['title'][:40]}...", expanded=False):
            st.markdown(f"**Year:** {paper.get('year')} | **Venue:** {paper.get('venue')}")
            st.markdown(f"**Authors:** {', '.join(paper.get('authors', [])[:2])}")
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=os.path.basename(pdf_path), key=f"dl_{paper['paperId']}_{time.time()}")
            elif paper.get('openAccessPdf'):
                url = paper.get('openAccessPdf', {}).get('url')
                if url and url.startswith("http"):
                    st.markdown(f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;"><button style="background-color: transparent; border: 1px solid #4CAF50; color: #4CAF50; padding: 5px 10px; border-radius: 5px; cursor: pointer;">🌐 Open PDF Link</button></a>', unsafe_allow_html=True)
                else:
                    st.caption("PDF Link Unavailable")
            elif paper.get('url'):
                url = paper.get('url')
                if url and url.startswith("http"):
                    st.markdown(f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;"><button style="background-color: transparent; border: 1px solid #2196F3; color: #2196F3; padding: 5px 10px; border-radius: 5px; cursor: pointer;">🔗 View Paper</button></a>', unsafe_allow_html=True)
                else:
                    st.caption("Paper Link Unavailable")

for p in st.session_state.papers:
    render_paper_card(p['paper'], p.get('pdf_path'))

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
                paper_obj = {'paper': event['paper']}
                st.session_state.papers.append(paper_obj)
                render_paper_card(event['paper'])
            
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
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
        import traceback
        st.text(traceback.format_exc())

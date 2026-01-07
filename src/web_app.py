
import streamlit as st
import sys
import os
import time
import json

# Add src to sys.path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from main import ResearchPipeline

st.set_page_config(
    page_title="FindUrCite AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for chat-like experience
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
        color: #31333F; /* Dark text for better contrast */
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/student-center.png", width=80)
    st.title("FindUrCite")
    st.caption("AI-Powered Research Assistant with Multi-Agent Debate")
    
    st.divider()
    
    model_name = st.text_input("Ollama Model", value="qwen2.5:7b")
    
    st.subheader("Configuration")
    base_output_dir = st.text_input("Output Dir", value=os.path.abspath(os.path.join("tests", "research_output")))
    base_pdf_dir = st.text_input("PDF Dir", value=os.path.abspath(os.path.join("tests", "downloads")))
    
    st.divider()
    st.markdown("### 📊 Status")
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    
    st.divider()
    st.markdown("### 📚 Found Papers")
    papers_container = st.container()

# Main Area
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Research Context")
    user_input = st.text_area("Enter your abstract, research idea, or draft:", height=400, 
                              value="Retrieval-Augmented Generation for Code Repositories",
                              help="The AI will analyze this text to generate search queries and evaluate papers.")
    
    start_btn = st.button("🚀 Start Deep Research", type="primary")
    
    st.divider()
    st.subheader("📜 System Logs")
    log_container = st.container(height=400)

with col2:
    st.subheader("💬 Multi-Agent Debate Live Feed")
    # This container will hold the chat messages
    chat_container = st.container(height=800)

# Session state to hold chat history if needed, but for now we stream directly
if "messages" not in st.session_state:
    st.session_state.messages = []

def render_message(role, content, avatar=None, paper_context=None):
    with chat_container:
        with st.chat_message(role, avatar=avatar):
            if paper_context:
                st.markdown(f"<div class='highlight-paper'>📄 <b>Context:</b> {paper_context}</div>", unsafe_allow_html=True)
            st.markdown(content)

def render_paper_card(paper, pdf_path=None):
    with papers_container:
        with st.expander(f"📄 {paper['title'][:40]}...", expanded=False):
            st.markdown(f"**Year:** {paper.get('year')} | **Venue:** {paper.get('venue')}")
            st.markdown(f"**Authors:** {', '.join(paper.get('authors', [])[:2])}")
            if pdf_path and os.path.exists(pdf_path):
                 # Streamlit download button for local file
                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=os.path.basename(pdf_path), key=f"dl_{paper['paperId']}")
            elif paper.get('openAccessPdf'):
                # st.link_button("🌐 Open PDF Link", paper.get('openAccessPdf', {}).get('url'))
                # Use HTML for safe external link in new tab
                url = paper.get('openAccessPdf', {}).get('url')
                if url and url.startswith("http"):
                    st.markdown(f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;"><button style="background-color: transparent; border: 1px solid #4CAF50; color: #4CAF50; padding: 5px 10px; border-radius: 5px; cursor: pointer;">🌐 Open PDF Link</button></a>', unsafe_allow_html=True)
                else:
                    st.caption("PDF Link Unavailable")
            elif paper.get('url'):
                # st.link_button("🔗 View Paper", paper.get('url'))
                url = paper.get('url')
                if url and url.startswith("http"):
                    st.markdown(f'<a href="{url}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;"><button style="background-color: transparent; border: 1px solid #2196F3; color: #2196F3; padding: 5px 10px; border-radius: 5px; cursor: pointer;">🔗 View Paper</button></a>', unsafe_allow_html=True)
                else:
                    st.caption("Paper Link Unavailable")

if start_btn and user_input:
    # Clear previous run
    st.session_state.messages = []
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_output_dir = f"{base_output_dir}_{timestamp}"
    
    pipeline = ResearchPipeline(
        model=model_name,
        output_dir=run_output_dir,
        pdf_dir=base_pdf_dir
    )
    
    status_placeholder.info("Initializing...")
    
    try:
        step = 0
        for event in pipeline.run(user_input):
            # Handle Logs
            if event['type'] == 'log':
                log_container.text(f"[{time.strftime('%H:%M:%S')}] {event['content']}")
            
            # Handle Status
            elif event['type'] == 'status':
                status_placeholder.info(f"👉 {event['content']}")
                step += 1
                progress_bar.progress(min(step/6, 1.0)) # Rough estimate

            # Handle Found Paper Event (New)
            elif event['type'] == 'paper_found':
                render_paper_card(event['paper'])
            
            # Handle PDF Ready Event (New)
            elif event['type'] == 'pdf_ready':
                # Re-render card with PDF button? Streamlit appends, so this is tricky.
                # Ideally we update state or just log it. 
                # For simplicity, we just add a small note or re-render.
                # Since 'papers_container' is a container, appending works but might clutter.
                # Let's just log it in the log container and maybe add a special "PDF Ready" toast.
                log_container.text(f"[{time.strftime('%H:%M:%S')}] PDF Downloaded: {event['paper']['title'][:30]}...")
                # We can't easily update the previous expander without unique keys and reruns.
                # So we will just show it in the log for now, or add a new card at the bottom of the list.
                # A better way is to rely on the 'paper_found' event which we added earlier, 
                # but 'pdf_ready' comes later.
                # Let's just create a new card for "Downloaded PDFs" or update the log.
                render_paper_card(event['paper'], event['pdf_path'])

            # Handle Debate Events (The Chat)
            elif event['type'] == 'debate_event':
                data = event['data']
                role = data.get('role', 'system')
                content = data.get('content', '')
                paper_title = event.get('paper_title')
                
                if role == 'student':
                    render_message("assistant", content, avatar="🧑‍🎓", paper_context=paper_title)
                elif role == 'advisor':
                    render_message("assistant", content, avatar="👨‍🏫", paper_context=paper_title)
                elif role == 'system':
                    render_message("system", f"_{content}_", avatar="⚙️", paper_context=paper_title)
            
            # Handle Result
            elif event['type'] == 'result':
                status_placeholder.success("Research Completed!")
                progress_bar.progress(1.0)
                
                with chat_container:
                    st.divider()
                    st.header("🎉 Final Synthesis & Report")
                    
                    synthesis = event.get('synthesis')
                    if synthesis:
                        with st.chat_message("assistant", avatar="🧠"):
                            st.markdown("### 🧠 Global Synthesis")
                            st.markdown(f"**State of the Art**: \n{synthesis.get('state_of_art_summary')}")
                            st.markdown(f"**Gap Analysis**: \n{synthesis.get('gap_analysis')}")
                            st.success(f"**Strategic Recommendations**: \n{synthesis.get('strategic_recommendations')}")

                    report_path = os.path.join(event['output_dir'], "research_result.md")
                    if os.path.exists(report_path):
                        with open(report_path, "r", encoding="utf-8") as f:
                            st.download_button("📥 Download Full Report", f, file_name="research_result.md")
                            
            elif event['type'] == 'error':
                st.error(event['content'])
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
        # st.exception(e) # Uncomment for debug

import os
import streamlit as st
from datetime import datetime
from azure.identity import ClientSecretCredential
from azure.ai.projects import AIProjectClient


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="RPX Market Validation Agent",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="auto"  # Auto-collapse on mobile
)


# =========================
# CUSTOM STYLING - RESPONSIVE
# =========================
st.markdown("""
<style>
    :root {
        --primary: #1e3a8a;
        --primary-light: #3b82f6;
        --accent: #f59e0b;
        --accent-dark: #d97706;
        --bg-light: #f9fafb;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --border: #e5e7eb;
        --success: #10b981;
        --error: #ef4444;
    }
    
    * {
        box-sizing: border-box;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    }
    
    /* Remove default padding and adjust */
    .main { 
        padding-top: 0.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* ==================== HEADER ==================== */
    .header-container {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: 2.5rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.15);
        color: white;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.95;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(30, 58, 138, 0.1);
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 1rem;
        color: #1e3a8a;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* ==================== CHAT MESSAGES ==================== */
    .user-message {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
    }
    
    .user-message .stChatMessage {
        max-width: 85%;
        background: linear-gradient(135deg, #2563eb 0%, #60a5fa 100%);
        color: white;
    }
    
    .assistant-message {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 1rem;
    }
    
    .assistant-message .stChatMessage {
        max-width: 95%;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        color: #1f2937;
    }
    
    .assistant-message .stChatMessage p {
        color: #1f2937 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    .assistant-message .stChatMessage strong {
        color: #1e3a8a !important;
        font-weight: 700 !important;
    }
    
    .assistant-message .stChatMessage li {
        color: #1f2937 !important;
        font-size: 0.95rem !important;
    }
    
    .assistant-message .stChatMessage h1,
    .assistant-message .stChatMessage h2,
    .assistant-message .stChatMessage h3 {
        color: #1e3a8a !important;
        font-weight: 700 !important;
    }
    
    .stChatMessage {
        border-radius: 12px;
        padding: 1rem 1.25rem;
        transition: all 0.3s ease;
        word-wrap: break-word;
        overflow-wrap: break-word;
        color: #1f2937 !important;
    }
    
    .stChatMessage * {
        color: #1f2937 !important;
    }
    
    .stChatMessage p {
        color: #1f2937 !important;
        font-size: 0.95rem !important;
    }
    
    .stChatMessage ul, .stChatMessage ol {
        color: #1f2937 !important;
    }
    
    .stChatMessage li {
        color: #1f2937 !important;
    }
    
    .stChatMessage span {
        color: #1f2937 !important;
    }
    
    .stChatMessage:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    
    /* ==================== CHAT INPUT ==================== */
    .stChatInputContainer {
        padding: 1rem 0 0 0;
    }
    
    .stChatInput {
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        background: white !important;
        transition: all 0.3s ease;
        font-size: 0.95rem;
    }
    
    .stChatInput:focus {
        border-color: var(--primary-light) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* ==================== SIDEBAR ==================== */
    .stSidebar {
        background: linear-gradient(180deg, #f9fafb 0%, white 100%);
    }
    
    .stSidebar h3 {
        color: var(--primary);
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }
    
    .stSidebar p, .stSidebar li {
        font-size: 0.9rem;
        line-height: 1.5;
        color: var(--text-primary);
    }
    
    .stSidebar strong {
        color: var(--primary);
        font-weight: 600;
    }
    
    .sidebar-section {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
    }
    
    .sidebar-section h3 {
        color: var(--primary);
        margin: 0 0 0.75rem 0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* ==================== STATES & BOXES ==================== */
    .thinking {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-secondary);
        font-style: italic;
        font-size: 0.95rem;
    }
    
    .thinking::after {
        content: '';
        display: inline-block;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--text-secondary);
        animation: dots 1.4s infinite;
    }
    
    @keyframes dots {
        0%, 60%, 100% { opacity: 0; }
        30% { opacity: 1; }
    }
    
    .error-box {
        background: #fee2e2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    
    .success-box {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    hr {
        border: none;
        border-top: 1px solid var(--border);
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left: 4px solid var(--primary-light);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #1f2937;
    }
    
    .info-box h3 {
        margin: 0 0 0.75rem 0;
        font-size: 1rem;
        color: #1e3a8a;
        font-weight: 700;
    }
    
    .info-box p {
        color: #1f2937 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    
    .info-box ul {
        margin: 0;
        padding-left: 1.5rem;
        font-size: 0.9rem;
        color: #1f2937;
    }
    
    .info-box li {
        margin-bottom: 0.5rem;
        line-height: 1.5;
        color: #1f2937 !important;
    }
    
    .info-box strong {
        color: #1e3a8a;
        font-weight: 700;
    }
    
    /* ==================== TABLET (iPad) - 768px ==================== */
    @media (max-width: 768px) {
        .main {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
        
        .info-box {
            color: #1f2937;
        }
        
        .info-box h3 {
            color: #1e3a8a;
        }
        
        .info-box p, .info-box li {
            color: #1f2937 !important;
        }
        
        .stSidebar h3 {
            font-size: 0.9rem;
            margin-top: 0.75rem;
            margin-bottom: 0.5rem;
        }
        
        .stSidebar p, .stSidebar li {
            font-size: 0.85rem;
            line-height: 1.4;
        }
        
        .header-container {
            padding: 2rem 1rem;
            margin-bottom: 1rem;
            border-radius: 10px;
        }
        
        .header-container h1 {
            font-size: 1.5rem;
        }
        
        .header-container p {
            font-size: 0.85rem;
        }
        
        .user-message .stChatMessage {
            max-width: 90%;
        }
        
        .assistant-message .stChatMessage {
            max-width: 100%;
        }
        
        .stChatMessage {
            padding: 0.9rem 1rem;
            border-radius: 10px;
        }
        
        .sidebar-section {
            padding: 0.9rem;
            margin-bottom: 0.8rem;
        }
        
        .sidebar-section h3 {
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
        }
    }
    
    /* ==================== MOBILE (up to 480px) ==================== */
    @media (max-width: 480px) {
        .main {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            padding-top: 0.25rem;
        }
        
        .stSidebar {
            padding: 0.75rem;
        }
        
        .stSidebar h3 {
            font-size: 0.95rem;
            font-weight: 700;
            margin: 1.25rem 0 0.75rem 0;
            color: var(--primary);
        }
        
        .stSidebar h3:first-child {
            margin-top: 0;
        }
        
        .stSidebar p, .stSidebar li {
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
        }
        
        .stSidebar strong {
            font-size: 0.9rem;
        }
        
        .stMetric {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 0.75rem;
        }
        
        .stMetricLabel {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        .stMetricValue {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .header-container {
            padding: 1.5rem 1rem;
            margin-bottom: 0.75rem;
            border-radius: 8px;
        }
        
        .header-container h1 {
            font-size: 1.25rem;
            letter-spacing: 0;
        }
        
        .header-container p {
            font-size: 0.75rem;
        }
        
        .status-badge {
            font-size: 0.75rem;
            padding: 0.4rem 0.75rem;
            margin-top: 0.75rem;
        }
        
        .user-message {
            margin-bottom: 0.75rem;
        }
        
        .user-message .stChatMessage {
            max-width: 95%;
        }
        
        .assistant-message .stChatMessage {
            max-width: 100%;
        }
        
        .stChatMessage {
            padding: 0.75rem 0.9rem;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #1f2937;
        }
        
        .stChatMessage p {
            color: #1f2937 !important;
            font-size: 0.9rem !important;
            line-height: 1.6 !important;
        }
        
        .stChatMessage strong {
            color: #1e3a8a !important;
            font-weight: 700 !important;
        }
        
        .stChatMessage li {
            color: #1f2937 !important;
            font-size: 0.9rem !important;
        }
        
        .stChatInputContainer {
            padding: 0.75rem 0 0 0;
        }
        
        .stChatInput {
            font-size: 0.9rem !important;
        }
        
        .sidebar-section {
            padding: 0.75rem;
            margin-bottom: 0.6rem;
            border-radius: 8px;
        }
        
        .sidebar-section h3 {
            font-size: 0.75rem;
            margin-bottom: 0.5rem;
        }
        
        .sidebar-section p {
            font-size: 0.8rem;
        }
        
        .info-box {
            padding: 0.75rem;
            border-left-width: 3px;
            color: #1f2937;
        }
        
        .info-box h3 {
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            color: #1e3a8a;
            font-weight: 700;
        }
        
        .info-box p {
            font-size: 0.85rem;
            line-height: 1.5;
            margin: 0.5rem 0;
            color: #1f2937 !important;
        }
        
        .info-box ul {
            font-size: 0.8rem;
            padding-left: 1rem;
            color: #1f2937;
        }
        
        .info-box li {
            margin-bottom: 0.25rem;
            line-height: 1.4;
            color: #1f2937 !important;
        }
        
        .info-box strong {
            display: block;
            margin-top: 0.75rem;
            font-size: 0.85rem;
            color: #1e3a8a;
            font-weight: 700;
        }
        
        .error-box {
            padding: 0.75rem;
            font-size: 0.9rem;
        }
        
        .thinking {
            font-size: 0.85rem;
        }
        
        hr {
            margin: 0.75rem 0;
        }
    }
    
    /* ==================== SMALL MOBILE (up to 360px) ==================== */
    @media (max-width: 360px) {
        .header-container h1 {
            font-size: 1.1rem;
        }
        
        .stChatMessage {
            font-size: 0.85rem;
            padding: 0.65rem 0.75rem;
        }
        
        .sidebar-section p {
            font-size: 0.75rem;
        }
    }
    
    /* ==================== TOUCH FRIENDLY ==================== */
    @media (hover: none) and (pointer: coarse) {
        button {
            min-height: 44px;
            padding: 0.75rem 1.5rem;
        }
        
        .stChatMessage:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
    }
</style>
""", unsafe_allow_html=True)


# =========================
# ENVIRONMENT VARIABLES
# =========================
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
AGENT_ID = os.getenv("AZURE_AI_AGENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

missing_vars = [
    name for name, value in {
        "AZURE_AI_PROJECT_ENDPOINT": PROJECT_ENDPOINT,
        "AZURE_AI_AGENT_ID": AGENT_ID,
        "AZURE_TENANT_ID": TENANT_ID,
        "AZURE_CLIENT_ID": CLIENT_ID,
        "AZURE_CLIENT_SECRET": CLIENT_SECRET,
    }.items()
    if not value
]

if missing_vars:
    st.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    st.info("Please set the required environment variables in your deployment.")
    st.stop()


# =========================
# AUTHENTICATION & CLIENT
# =========================
@st.cache_resource
def get_project_client():
    """Initialize and cache the Azure AI Project client."""
    try:
        credential = ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=credential,
            allow_preview=True,
        )
        return client
    except Exception as e:
        st.error(f"Failed to authenticate: {str(e)}")
        st.stop()


project_client = get_project_client()
openai_client = project_client.get_openai_client(agent_name=AGENT_ID)


# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False


# =========================
# HEADER SECTION - RESPONSIVE
# =========================

# Check screen size (rough estimate based on Streamlit's behavior)
# On mobile, Streamlit automatically switches to single column
try:
    # Desktop/Tablet layout
    col1, col2 = st.columns([0.65, 0.35])
    
    with col1:
        st.markdown("""
        <div class="header-container">
            <h1>💬 RPX Market Validation</h1>
            <p>AI-powered research assistant for strategic market insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="header-container" style="background: linear-gradient(135deg, #065f46 0%, #059669 100%); display: flex; flex-direction: column; justify-content: center;">
            <div class="status-badge" style="background: rgba(255, 255, 255, 0.2); color: #ffffff;">
                <div class="status-dot"></div>
                Agent Connected
            </div>
            <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.95; color: #ffffff;">
                <strong>Ready to assist</strong><br>
                Ask market research questions
            </div>
        </div>
        """, unsafe_allow_html=True)
except:
    # Fallback to single column (mobile detection)
    st.markdown("""
    <div class="header-container">
        <h1>💬 RPX Market Validation</h1>
        <p>AI-powered research assistant for strategic market insights</p>
        <div class="status-badge">
            <div class="status-dot"></div>
            Agent Connected
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# SIDEBAR - RESPONSIVE
# =========================
with st.sidebar:
    st.markdown("### 🎯 Guide")
    st.markdown("""
    **How to use this agent:**
    
    1. **Ask questions** about market validation, customer research, or competitive analysis
    2. **Get insights** from AI analysis of your market data
    3. **Refine queries** based on the responses
    
    **Example questions:**
    - What are current trends in our market?
    - How do we validate customer demand?
    - What are our competitors doing?
    """)
    
    st.divider()
    
    st.markdown("### 📊 Session Info")
    
    # Metrics - responsive without columns
    metrics_col1, metrics_col2 = st.columns([1, 1], gap="small")
    with metrics_col1:
        st.metric("Messages", len(st.session_state.messages))
    with metrics_col2:
        status_text = "0:00" if not st.session_state.messages else "Active"
        st.metric("Status", status_text)
    
    st.divider()
    
    st.markdown("### ⚙️ Options")
    
    if st.button("🔄 Clear Chat History", key="clear_btn", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_started = False
        st.rerun()
    
    st.markdown("""
    ---
    
    ### 💡 Tips
    
    - **Be specific** with your questions for better insights
    - **Follow up** on responses to dive deeper
    - **Reference data** you have for context
    - Questions are processed in real-time
    """)


# =========================
# MAIN CHAT AREA
# =========================
st.markdown("---")

# Display chat history
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div class="info-box">
            <h3 style="margin-top: 0;">👋 Welcome to RPX Market Validation Agent</h3>
            <p style="line-height: 1.5; margin: 0.75rem 0;">
                Start a conversation by asking questions about market research, 
                customer validation, competitive analysis, or market trends.
            </p>
            <strong style="display: block; margin-top: 1rem;">Try asking:</strong>
            <ul style="margin-top: 0.5rem; line-height: 1.6;">
                <li>"What are the key market segments?"</li>
                <li>"How do we validate customer demand?"</li>
                <li>"What's the competitive landscape?"</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(
                message["role"],
                avatar="👤" if message["role"] == "user" else "🤖"
            ):
                st.markdown(message["content"])


# =========================
# USER INPUT & RESPONSE
# =========================
prompt = st.chat_input(
    "Ask the RPX Agent anything about market validation...",
    key="user_input"
)

if prompt:
    st.session_state.conversation_started = True
    
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Display assistant response with loading state
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        
        try:
            with placeholder.container():
                st.markdown('<div class="thinking">Analyzing your question</div>', unsafe_allow_html=True)
            
            # Call the Azure Foundry agent
            response = openai_client.responses.create(input=prompt)
            
            # Extract answer from response
            answer = getattr(response, "output_text", None)
            
            if not answer:
                answer_parts = []
                for output in getattr(response, "output", []) or []:
                    for content in getattr(output, "content", []) or []:
                        if getattr(content, "type", None) == "output_text":
                            text = getattr(content, "text", None)
                            if text:
                                answer_parts.append(text)
                        else:
                            text = getattr(content, "text", None)
                            if text:
                                answer_parts.append(text)
                
                answer = "\n\n".join(answer_parts) if answer_parts else None
            
            if not answer:
                answer = str(response)
            
            # Display the answer
            with placeholder.container():
                st.markdown(answer)
            
            # Add to message history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
        
        except Exception as e:
            error_msg = f"⚠️ **Error processing request:**\n\n{str(e)}"
            with placeholder.container():
                st.markdown(f'<div class="error-box">{error_msg}</div>', unsafe_allow_html=True)
            
            # Still add error to history for context
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })


# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); font-size: 0.9rem; padding: 0 0.5rem;">
    <p style="margin: 0.5rem 0;">RPX Market Validation Agent | Powered by Azure AI Foundry</p>
    <p style="font-size: 0.85rem; margin: 0; opacity: 0.8;">This agent provides insights based on provided information. Always validate findings independently.</p>
</div>
""", unsafe_allow_html=True)
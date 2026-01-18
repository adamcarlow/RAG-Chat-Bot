import streamlit as st
from langchain_xai import ChatXAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Board Game Rules Assistant", layout="wide")

XAI_API_KEY = os.getenv("XAI_API_KEY")  # Set in .env file
MODEL_NAME = "grok-4-1-fast-reasoning"  # Options: "grok-4", "grok-3-latest", "grok-3-fast"

PROMPT_TEMPLATE = """\
You are an expert board game rules specialist. Your job is to help players understand game rules, clarify confusing situations, and explain how to play.

When answering:
- Be clear and precise about game mechanics
- Use examples when helpful to illustrate rules
- If a rule interaction is ambiguous, explain the most common interpretation
- Reference specific sections or page numbers from the rulebook when possible

Use **only** the information from the provided rulebook context below.

Rulebook Context:
{context}

Player's Question: {question}

Answer:"""

# ─── Functions ────────────────────────────────────────────────────────────
def get_llm():
    return ChatXAI(model=MODEL_NAME, temperature=0.2, api_key=XAI_API_KEY)

@st.cache_data(show_spinner=False)
def extract_text_from_pdf(pdf_path: str | Path) -> str:
    try:
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        text = "\n\n".join(doc.page_content for doc in docs)
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# ─── UI ────────────────────────────────────────────────────────────────────

# Header with board game theme
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <span style="font-size: 4rem;">🎲 🎯 🃏</span>
        <h1 style="margin-top: 0;">Board Game Rules Assistant</h1>
        <p style="color: gray;">Upload a rulebook, ask questions, get answers instantly</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar with tips
with st.sidebar:
    st.markdown("### 🎮 How to Use")
    st.markdown("""
    1. **Upload** your game's rulebook PDF
    2. **Ask** any rules question
    3. **Get** instant answers
    """)

    st.markdown("---")
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    - *"How do I set up the game?"*
    - *"What happens when I roll doubles?"*
    - *"Can I trade on my first turn?"*
    - *"How do I win?"*
    """)

    st.markdown("---")
    st.markdown("### 🎲 Supported Games")
    st.markdown("Any board game with a PDF rulebook!")
    st.markdown("*Catan, Monopoly, Ticket to Ride, Wingspan, and more...*")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a game rulebook (PDF)",
    type=["pdf"],
    help="Upload the PDF rulebook for any board game"
)

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_dir = Path("temp_pdfs")
    temp_dir.mkdir(exist_ok=True)
    
    temp_path = temp_dir / uploaded_file.name
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract text (cached)
    with st.spinner("Extracting text from PDF..."):
        context = extract_text_from_pdf(temp_path)
    
    if not context:
        st.stop()

    st.success(f"📖 Rulebook loaded • {len(context):,} characters")

    # Show a little preview
    with st.expander("📄 Preview rulebook text"):
        st.markdown(f"```\n{context[:600]}...\n```")

    # Question input
    st.markdown("### ❓ Ask a Rules Question")
    question = st.text_input("Your question:",
                            placeholder="How do I set up the game?",
                            key="question_input",
                            label_visibility="collapsed")

    if question and question.strip():
        if st.button("🎯 Get Answer", type="primary"):
            with st.spinner("🎲 Consulting the rulebook..."):
                llm = get_llm()

                prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
                chain_input = {"context": context, "question": question}
                formatted_prompt = prompt.format(**chain_input)

                try:
                    response = llm.invoke(formatted_prompt)
                    answer = response.content

                    st.markdown("### 📜 Answer")
                    st.info(answer)
                    
                except Exception as e:
                    st.error(f"Error while running model:\n{e}")

# Cleanup hint
st.markdown("---")
if st.button("🗑️ Clear uploaded rulebooks", help="Removes uploaded PDFs from disk"):
    try:
        for file in Path("temp_pdfs").glob("*.pdf"):
            file.unlink()
        st.success("Rulebooks cleared!")
    except:
        st.warning("Could not delete some files")

st.markdown("---")
st.caption("Powered by grok-4-1-fast-reasoning • xAI")

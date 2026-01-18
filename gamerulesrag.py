import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# ─── Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Board Game Rules Assistant", layout="wide")

# Get API key from Streamlit secrets (cloud) or .env file (local)
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"  # Free models: "llama-3.3-70b-versatile", "mixtral-8x7b-32768"

# RAG Configuration
CHUNK_SIZE = 2000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
TOP_K_CHUNKS = 4  # Number of relevant chunks to retrieve per rulebook

PROMPT_TEMPLATE = """\
You are an expert board game rules specialist. Your job is to help players understand game rules, clarify confusing situations, and explain how to play.

When answering:
- Be clear and precise about game mechanics
- Use examples when helpful to illustrate rules
- If a rule interaction is ambiguous, explain the most common interpretation
- Reference the game name and specific sections when possible

Use **only** the information from the provided rulebook context below.

Relevant Rulebook Sections:
{context}

Player's Question: {question}

Answer:"""

# ─── Functions ────────────────────────────────────────────────────────────
def get_llm():
    return ChatGroq(model=MODEL_NAME, temperature=0.2, api_key=GROQ_API_KEY)

@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Load the embedding model (cached to avoid reloading)."""
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def load_and_chunk_pdf(pdf_path: str | Path, game_name: str):
    """Load PDF and split into chunks, adding game name to metadata."""
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    # Add game name to metadata
    for doc in documents:
        doc.metadata['game'] = game_name

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    return chunks

def create_vector_store(chunks, embeddings):
    """Create FAISS vector store from chunks."""
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store

def retrieve_relevant_chunks(vector_stores: dict, selected_games: list, question: str, k: int = TOP_K_CHUNKS):
    """Retrieve the most relevant chunks from selected games."""
    all_docs = []

    for game_name in selected_games:
        if game_name in vector_stores:
            docs = vector_stores[game_name].similarity_search(question, k=k)
            all_docs.extend(docs)

    return all_docs

# Initialize session state for multiple rulebooks
if "rulebooks" not in st.session_state:
    st.session_state.rulebooks = {}  # {game_name: vector_store}

# Auto-load pre-included rulebooks
RULEBOOKS_DIR = Path(__file__).parent / "rulebooks"
if RULEBOOKS_DIR.exists() and not st.session_state.get("preloaded"):
    embeddings = get_embeddings()
    for pdf_file in RULEBOOKS_DIR.glob("*.pdf"):
        game_name = pdf_file.stem.replace("_", " ").title()
        if game_name not in st.session_state.rulebooks:
            try:
                chunks = load_and_chunk_pdf(pdf_file, game_name)
                if chunks:
                    vector_store = create_vector_store(chunks, embeddings)
                    st.session_state.rulebooks[game_name] = vector_store
            except Exception:
                pass  # Skip files that can't be processed
    st.session_state.preloaded = True

# ─── UI ────────────────────────────────────────────────────────────────────

# Header with board game theme
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <span style="font-size: 4rem;">🎲 🎯 🃏</span>
        <h1 style="margin-top: 0;">Board Game Rules Assistant</h1>
        <p style="color: gray;">Upload rulebooks, ask questions, get answers instantly</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Sidebar with tips and uploaded games
with st.sidebar:
    st.markdown("### 🎮 How to Use")
    st.markdown("""
    1. **Upload** one or more rulebook PDFs
    2. **Select** which game(s) to query
    3. **Ask** any rules question
    4. **Get** instant answers
    """)

    st.markdown("---")
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    - *"How do I set up the game?"*
    - *"What happens when I roll doubles?"*
    - *"Compare the victory conditions"*
    - *"How do I win?"*
    """)

    st.markdown("---")
    st.markdown("### 📚 Loaded Rulebooks")
    if st.session_state.rulebooks:
        for game in st.session_state.rulebooks.keys():
            st.markdown(f"- {game}")
    else:
        st.markdown("*No rulebooks loaded yet*")

# File uploader - multiple files
uploaded_files = st.file_uploader(
    "Upload game rulebooks (PDF)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload one or more PDF rulebooks"
)

if uploaded_files:
    temp_dir = Path("temp_pdfs")
    temp_dir.mkdir(exist_ok=True)

    embeddings = get_embeddings()

    for uploaded_file in uploaded_files:
        # Use filename without extension as game name
        game_name = Path(uploaded_file.name).stem

        # Check if already processed
        if game_name not in st.session_state.rulebooks:
            temp_path = temp_dir / uploaded_file.name

            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner(f"📄 Processing {game_name}..."):
                chunks = load_and_chunk_pdf(temp_path, game_name)

                if not chunks:
                    st.error(f"❌ Could not extract text from {game_name}. The PDF may be image-based or empty.")
                    continue

                vector_store = create_vector_store(chunks, embeddings)
                st.session_state.rulebooks[game_name] = vector_store

            st.success(f"✅ {game_name} loaded")

# Show game selector and question input if we have rulebooks
if st.session_state.rulebooks:
    st.markdown("---")

    # Game selector
    st.markdown("### 🎯 Select Rulebook(s) to Query")
    game_options = list(st.session_state.rulebooks.keys())

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_games = st.multiselect(
            "Select games:",
            options=game_options,
            default=[],
            label_visibility="collapsed"
        )
    with col2:
        if st.button("Select All"):
            selected_games = game_options
            st.rerun()

    if selected_games:
        # Question input
        st.markdown("### ❓ Ask a Rules Question")
        question = st.text_input(
            "Your question:",
            placeholder="How do I set up the game?" if len(selected_games) == 1 else "Compare the setup for these games",
            key="question_input",
            label_visibility="collapsed"
        )

        if question and question.strip():
            if st.button("🎯 Get Answer", type="primary"):

                # Retrieve relevant chunks from selected games
                with st.spinner("🔍 Finding relevant sections..."):
                    relevant_docs = retrieve_relevant_chunks(
                        st.session_state.rulebooks,
                        selected_games,
                        question
                    )

                    # Format context with game names
                    context_parts = []
                    for doc in relevant_docs:
                        game = doc.metadata.get('game', 'Unknown')
                        context_parts.append(f"[{game}]\n{doc.page_content}")
                    context = "\n\n---\n\n".join(context_parts)

                # Generate answer
                with st.spinner("🎲 Generating answer..."):
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
    else:
        st.warning("Please select at least one rulebook to query.")

# Cleanup
st.markdown("---")
if st.button("🗑️ Clear all rulebooks", help="Removes all uploaded PDFs and clears cache"):
    try:
        for file in Path("temp_pdfs").glob("*.pdf"):
            file.unlink()
        st.session_state.rulebooks = {}
        st.success("All rulebooks cleared!")
        st.rerun()
    except Exception as e:
        st.warning(f"Could not delete some files: {e}")

st.markdown("---")
st.caption("Powered by Llama 3.3 • Groq | Embeddings: all-MiniLM-L6-v2 | Vector Store: FAISS")

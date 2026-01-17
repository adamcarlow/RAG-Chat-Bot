import streamlit as st
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
import os
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="PDF Q&A • Llama 3.2", layout="wide")

MODEL_NAME = "llama3.2:3b"
# You can change this prompt template style to your liking
PROMPT_TEMPLATE = """\
You are a helpful research assistant.
Answer the question concisely and accurately using **only** the information from the provided context.

Context:
{context}

Question: {question}

Answer:"""

# ─── Functions ────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Initializing LLM...")
def get_llm():
    return ChatOllama(model=MODEL_NAME, temperature=0.2)

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
st.title("PDF Question Answering")
st.caption(f"using • Llama 3.2 3B • Ollama")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your research paper (PDF)",
    type=["pdf"],
    help="Only PDF files are supported"
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

    st.success(f"PDF loaded • {len(context):,} characters")
    
    # Show a little preview
    with st.expander("First 600 characters of extracted text"):
        st.markdown(f"```\n{context[:600]}...\n```")

    # Question input
    question = st.text_input("Your question:", 
                            placeholder="What is the main contribution of this paper?",
                            key="question_input")

    if question and question.strip():
        if st.button("Get Answer", type="primary"):
            with st.spinner("Thinking..."):
                llm = get_llm()
                
                prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
                chain_input = {"context": context, "question": question}
                formatted_prompt = prompt.format(**chain_input)
                
                try:
                    response = llm.invoke(formatted_prompt)
                    answer = response.content
                    
                    st.subheader("Answer")
                    st.markdown(answer)
                    
                except Exception as e:
                    st.error(f"Error while running model:\n{e}")

# Cleanup hint
if st.button("🗑️ Clear temporary files", help="Removes uploaded PDFs from disk"):
    try:
        for file in Path("temp_pdfs").glob("*.pdf"):
            file.unlink()
        st.success("Temporary files removed!")
    except:
        st.warning("Could not delete some files")

st.markdown("---")
st.caption("Local • Private • No data leaves your computer")
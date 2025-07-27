import os
import streamlit as st
from dotenv import load_dotenv
from utils.rag_pipeline import (
    load_pdf_text,
    text_to_chunks,
    create_vectorstore,
    load_vectorstore,
    get_qa_chain
)

# Load API key from .env
load_dotenv()

# Page Configuration
st.set_page_config(page_title="RAG LawBot", layout="centered")
st.title("⚖️ RAG LawBot")

# Paths
vectorstore_path = "vectorstore"
faiss_index_file = os.path.join(vectorstore_path, "index.faiss")
data_dir = "data"
os.makedirs(data_dir, exist_ok=True)

# Session State
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "question" not in st.session_state:
    st.session_state.question = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""

# --- PDF Upload Centered ---
st.markdown("### 📄 Upload your legal document (PDF)")
with st.form("upload_form"):
    uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if uploaded_file is None:
            st.error("❌ Please upload a PDF before submitting.")
        else:
            file_path = os.path.join(data_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            st.success(f"✅ Uploaded: {uploaded_file.name}")

            with st.spinner("Processing document..."):
                raw_text = load_pdf_text(file_path)
                chunks = text_to_chunks(raw_text)
                create_vectorstore(chunks, persist_path=vectorstore_path)
                st.session_state.pdf_uploaded = True
                st.success("📚 Document indexed successfully!")

# --- Action Options After Upload ---
if st.session_state.pdf_uploaded and os.path.exists(faiss_index_file):
    try:
        vs = load_vectorstore(persist_path=vectorstore_path)
        qa_chain = get_qa_chain(vs)

        st.markdown("### 🤖 What would you like to do?")
        action = st.radio(
            "Select an option:",
            ["🗣️ Ask Questions", "📝 Generate Summary", "🔍 Run Legal Analysis"],
            index=0,
            horizontal=True,
        )

        # --- 1. Conversational QA ---
        if action == "🗣️ Ask Questions":
            st.session_state.question = st.text_input(
                "💬 Ask a legal question:",
                value=st.session_state.question,
                key="question_input"
            )

            ask_col, clear_col = st.columns(2)

            if ask_col.button("Ask"):
                if st.session_state.question.strip():
                    with st.spinner("Answering..."):
                        result = qa_chain(st.session_state.question)
                        st.session_state.answer = result["result"]
                else:
                    st.warning("Please enter a question.")

            if clear_col.button("Clear"):
                st.session_state.question = ""
                st.session_state.answer = ""
                st.rerun()

            if st.session_state.answer:
                st.markdown(f"**📌 Answer:** {st.session_state.answer}")

        # --- 2. Generate Summary ---
        elif action == "📝 Generate Summary":
            if st.button("Generate Summary"):
                with st.spinner("Summarizing..."):
                    summary_prompt = (
                        "Give a bullet-point summary of the uploaded legal document in simple language."
                    )
                    result = qa_chain(summary_prompt)
                    st.markdown("**📝 Summary:**")
                    for line in result["result"].split("\n"):
                        st.markdown(f"- {line.strip()}")

        # --- 3. Legal Risk/Clause Analysis ---
        elif action == "🔍 Run Legal Analysis":
            if st.button("Run Analysis"):
                with st.spinner("Analyzing document..."):
                    analysis_prompt = (
                        "Give a detailed legal analysis of the uploaded document. "
                        "Mention potential risks, legal obligations, and any important clauses."
                    )
                    result = qa_chain(analysis_prompt)
                    st.markdown(f"**📊 Analysis:**\n\n{result['result']}")

    except Exception as e:
        st.error(f"❌ Error loading vectorstore: {str(e)}")

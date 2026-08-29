# -------------------------------
# IMPORTS
# -------------------------------
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# -------------------------------
# CREATE VECTOR DATABASE
# -------------------------------
def create_vector_db(text):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=120,
        chunk_overlap=20
    )

    chunks = text_splitter.split_text(text)

    if not chunks:
        raise ValueError("No content found in file")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_texts(chunks, embeddings)

    return db, len(chunks)


# -------------------------------
# LOAD LLM (NOT NEEDED HERE)
# -------------------------------
def load_llm():
    return None   # Not using generator


# -------------------------------
# GET ANSWER (EXTRACTIVE RAG)
# -------------------------------
def get_answer(db, generator, query):

    results = db.similarity_search_with_score(query, k=3)

    best_score = results[0][1]

    # Reject irrelevant queries
    if best_score > 1.5:
        return "I don't know", []

    docs = [doc for doc, score in results]

    # Combine top chunks
    context = " ".join([doc.page_content for doc in docs])

    # Split into sentences
    sentences = context.split(".")

    query_words = query.lower().split()

    best_sentence = ""
    max_score = 0

    for sentence in sentences:
        sentence_lower = sentence.lower()

        # Skip very short sentences (like titles)
        if len(sentence.strip()) < 20:
            continue

        # Count matching words
        match_count = sum(1 for word in query_words if word in sentence_lower)

        if match_count > max_score:
            max_score = match_count
            best_sentence = sentence.strip()

    # Fallback
    if not best_sentence:
        for sentence in sentences:
            if len(sentence.strip()) > 20:
                best_sentence = sentence.strip()
                break

    return best_sentence, [doc.page_content for doc in docs]
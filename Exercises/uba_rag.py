import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, WikipediaLoader 
from langchain_text_splitters import CharacterTextSplitter 
from langchain_community.vectorstores import Chroma 
from config import load_embeddings, load_google_llm  

# -------------------------------
# Load Data and Build Vector Store
# -------------------------------
embeddings = load_embeddings()  

# PDF 
pdf_loader = PyPDFLoader('./data/university_of_bamenda.pdf') 
pdf_docs = pdf_loader.load()  

# Web 
urls_data = ["https://uniba.cm/"] 
web_loader = WebBaseLoader(urls_data) 
web_docs = web_loader.load()  

# Wikipedia 
about_loader = WikipediaLoader(query="University of Bamenda About", load_max_docs=1) 
about_docs = about_loader.load()  

history_loader = WikipediaLoader(query="University of Bamenda History", load_max_docs=1) 
history_docs = history_loader.load()  

home_loader = WikipediaLoader(query="University of Bamenda", load_max_docs=1) 
home_docs = home_loader.load()  

all_docs = pdf_docs + web_docs + about_docs + history_docs + home_docs 
print(f"📚 Loaded {len(all_docs)} total documents.")  

text_splitter = CharacterTextSplitter(     
    separator="\n\n",     
    chunk_size=1000,     
    chunk_overlap=200,     
    length_function=len,     
    is_separator_regex=False 
)  

page_contents = [doc.page_content for doc in all_docs] 
chunks = text_splitter.create_documents(page_contents)  

print(f"✅ Total number of chunks after combining: {len(chunks)}")  

vector_db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_uba") 
retriever = vector_db.as_retriever(search_kwargs={"k": 3})  

# -------------------------------
# Helper Functions
# -------------------------------
def is_uba_question(question: str) -> bool:     
    keywords = [         
        "bamenda", "university of bamenda", "uba", "uniba",         
        "prof.", "dr.", "campus", "faculty", "department",         
        "admission", "courses", "tuition", "fees", "library",         
        "research", "students", "staff", "programs",         
        "scholarships", "events"     
    ]     
    q = question.lower()     
    return any(keyword in q for keyword in keywords)  

def answer_question(question: str):     
    if not is_uba_question(question):         
        return "⚠️ I only answer questions about the University of Bamenda."     
    docs = retriever.get_relevant_documents(question)      

    if not docs:         
        return "⚠️ I don’t know from the available documents."      

    context = "\n\n".join([f"[Source {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs)])     
    prompt = f""" You are an AI assistant for the University of Bamenda. 
    Use the following context to answer the question. 
    If the answer is not in the context, say "I don’t know from the available documents."  

    Context: {context}  

    Question: {question}  

    Answer (with sources if possible): """     
    llm = load_google_llm()     
    response = llm.invoke(prompt)      

    return f"{response}"   

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.title("🤖 University of Bamenda AI Assistant")
    st.write("Ask me anything about the University of Bamenda!")

    question = st.text_input("❓ Your question:")

    if st.button("Get Answer"):
        if question.strip():
            answer = answer_question(question)
            st.markdown(f"💡 **Answer:** {answer}")
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()

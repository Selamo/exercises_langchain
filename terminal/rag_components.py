from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pprint import pprint
from langchain_text_splitters import CharacterTextSplitter
from config import load_google_llm, load_google_chat_model, load_embeddings
from langchain_community.vectorstores import Chroma, FAISS

embeddings=load_embeddings()
loader=PyPDFLoader('./data/cameroon_history.pdf')
# text_loader=TextLoader('./data/ai.txt')
# final_text=text_loader.load()
load_data=loader.load()
# print("My loaded data is: ",load_data)

# print(f"My first document is: {load_data}")
# STEP 2 CHUNKING/SPLITTING
text_splitter=CharacterTextSplitter(
    separator="\n\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False
    
)

# # SPLIT TEXT
# When You Want to use the create_documents method instead of split_documents
# Python Comprehension Syntax
page_contents =[doc.page_content for doc in load_data]
text1=text_splitter.create_documents(page_contents)

# to get metadata, use split_documents instead
text = text_splitter.split_documents(load_data)

# print(text[0],"\n\n",text1[0])
# EMBEDDINGS AND VECTOR STORE

vector_db=Chroma.from_documents(text,embeddings, persist_directory="./chroma_db")

prompt="Who was the first president of Cameroon"
response=vector_db.similarity_search(prompt)
print(f"My response is:  {response}")
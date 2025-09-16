from langchain_community.document_loaders import PyPDFLoader, TextLoader
loader=PyPDFLoader('./data/ai.pdf')
text_loader=TextLoader('./data/ai.txt')
final_text=text_loader.load()
print("My loaded text data is: ",final_text)
load_data=loader.load()
# print("My loaded data is: ",load_data)

# print(load_data[0].page_content)
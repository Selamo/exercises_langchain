from langchain_community.document_loaders import WebBaseLoader

urls_data=[
    # "bbc.com/news",
    "https://mynews.crtv.cm/",
    "https://edition.cnn.com/world"
]

loader=WebBaseLoader(urls_data)
docs=loader.load()

for page in docs:
    print(f"SCRAPE CONTENT for {page.metadata} IS: ", page.page_content[:300],"\n\n")
    
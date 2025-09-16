from config import load_google_chat_model


chat_model=load_google_chat_model()
# print(f"My chat model is: {chat_model}")

messages=[
    ("system","You are a helpful assistant and you play the role of a football analyst."),
    ("user","translate the following sentence to French. I love programming language for llms")
]

response=chat_model.invoke(messages)
# Task: We want to stream the response

for part in chat_model.stream("Who won the last champions league final in 1000 words?"):
    print(part.content, end="", flush=True)


# Streaming
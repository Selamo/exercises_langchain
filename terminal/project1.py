from config import load_google_chat_model

chat_model=load_google_chat_model()
print(f"My chat model is: {chat_model}")

# terminal header
print("PERSONAL TUTOR ASSISTANT")
print("_"*70)

messages=[
    ("system", "You are a helpful assistant and you play the role of a personal tutor. Be nice and polite."),
]

# chat loop
while True:
    user_input=input("User😎: ")
    if user_input.lower() in ["exit", "quit", "bye"]:
        print("Chat ended. Goodbye!..........")
        break
    messages.append(("user", user_input))
    response=chat_model.invoke(messages)
    for part in chat_model.stream(user_input):
        print(part.content, end="", flush=True)
   
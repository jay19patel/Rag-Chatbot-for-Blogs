from langchain.schema import HumanMessage
from graph import chatbot

def main():
    print("Simple Chatbot (type 'exit' to quit)")
    print("-" * 40)

    while True:
        user_msg = input("You: ")
        if user_msg.lower() == 'exit':
            break

        # Human message add karo
        initial_state = {"messages": [HumanMessage(content=user_msg)]}

        # Sahi config with thread_id
        config_temp = {
            "configurable": {
                "thread_id": "1"
            }
        }

        try:
            # Get AI response
            response = chatbot.invoke(initial_state, config=config_temp)
            ai_msg = response['messages'][-1].content
            print("AI:", ai_msg)
            print()
        except Exception as e:
            print(f"Error: {e}")

    # Show conversation history
    print("\nConversation History:")
    print("-" * 40)
    config_temp = {
        "configurable": {
            "thread_id": "1"
        }
    }

    try:
        messages = chatbot.get_state(config_temp).values['messages']
        for msg in messages:
            if hasattr(msg, 'content'):
                role = "You" if msg.__class__.__name__ == "HumanMessage" else "AI"
                print(f"{role}: {msg.content}")
    except Exception as e:
        print(f"Could not retrieve history: {e}")

if __name__ == "__main__":
    main()
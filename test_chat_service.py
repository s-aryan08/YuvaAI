from backend.database import SessionLocal
from backend.chat_service import (
    create_conversation,
    chat,
    get_conversation_history
)


def test_chat():

    db = SessionLocal()

    try:

        print("Creating conversation...")

        conversation = create_conversation(
            db,
            "My First YuvaAI Chat"
        )

        print("Conversation ID:", conversation.id)

        print("\nSending message to YuvaAI...")

        response = chat(
            db,
            conversation.id,
            "Hello YuvaAI! Introduce yourself."
        )

        print("\nYuvaAI:", response["assistant_message"])

        print("\nConversation history:")

        history = get_conversation_history(
            db,
            conversation.id
        )

        for message in history:
            print(message["role"], ":", message["content"])

        print("\nCHAT SERVICE WORKING!")

    except Exception as error:

        db.rollback()
        print("ERROR:", error)

    finally:

        db.close()


if __name__ == "__main__":
    test_chat()
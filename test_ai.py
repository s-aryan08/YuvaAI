from backend.ai_engine import generate_response

print("YUVA AI is starting...\n")

question = input("You: ")

try:

    answer = generate_response(question)

    print("\nYuvaAI:", answer)

except Exception as error:

    print("\nError:", error)
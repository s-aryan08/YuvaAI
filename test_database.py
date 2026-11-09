from backend.database import test_connection

print("Starting YuvaAI database test...\n")

success = test_connection()

if success:
    print("\nYUVA AI DATABASE READY!")
else:
    print("\nPLEASE CHECK DATABASE CONFIGURATION.")
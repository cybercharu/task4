from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\sharm\OneDrive\Desktop\vscode_files\Internship\fastapi_project\git_project\app\.env")

MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#print(MONGO_URI)
#print(SECRET_KEY)
#print(ALGORITHM)
#print(ACCESS_TOKEN_EXPIRE_MINUTES)

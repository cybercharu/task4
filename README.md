# Movie Library API
### A FastAPI-based RESTful API that allows admins to manage movie entries and consumers to rent/return movies
##### Features
- JWT Authentication
- Role-based access control (Admin & Consumer)
##### Install dependencies
pip install -r requirements.txt
##### Technologies Used
-Mongodb
-Python
-FastAPI
##### How to run this project
uvicorn app.main:app --reload
-To see documentation : after running above command a http link generates (open this in browser) then write /docs or /redoc in url. 
For example: http://localhost:8000/docs 
##### Refrence link to the interactive API document provided by FastAPI
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?h=to#update-the-token-path-operation

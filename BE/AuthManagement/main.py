from fastapi import FastAPI, HTTPException, Depends,File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from database import SessionLocal, engine
from models2 import *
from shcemas2 import *
from fastapi.middleware.cors import CORSMiddleware  


from summarize import *

# Initialize FastAPI App
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, use specific URLs to limit access
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash the password securely
        hashed_password = bcrypt.hash(user.password)

        # Create new user object
        new_user = User(
            full_name=user.full_name,
            email=user.email,
            password=hashed_password
        )
        
        # Add user to the database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Response
        return {"message": "User registered successfully", "user": {"id": new_user.id, "email": new_user.email}}

    except Exception as e:
        # Log the exception and raise HTTP error
        print(f"Error during user registration: {e}")  # Debugging
        raise HTTPException(status_code=500, detail="An error occurred while registering the user")


@app.post("/login")
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify the password
    if not bcrypt.verify(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # In a real-world application, you would generate a JWT token here
    return {"message": "Login successful", "user": {"id": user.id, "email": user.email, "full_name": user.full_name}}


# Ensure the upload directory exists


@app.post("/upload_course/")
async def upload_course(
    name: str = Form(...), 
    user_id: int = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    UPLOAD_DIRECTORY = "./uploads/"
    try:
        # Save the file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"        
        # Generate a public URL (adjust according to your server setup)
        file_url = UPLOAD_DIRECTORY+filename

        with open(file_url, "wb") as f:
            f.write(await file.read())

            
        text=extract_text_from_pdf(file_url)
        prompt="make a summary for this in english:"+text
        response = llm.invoke(prompt)
        exam=llm.invoke("generate an exam without answers based on this:"+response.content)
        correction=llm.invoke("generate organised correction for this exam:"+exam.content)
        # Simulate saving to the database
       
        data =Course(name=name,
            pdf_files= file_url,
            user_id= user_id,
            summary=response.content,
            exam=exam.content,
            exam_correction=correction.content
            )
        db.add(data)
        db.commit()
        db.refresh(data)
        cours=db.query(Course).filter(Course.pdf_files==data.pdf_files ).all()
        cour=cours[0]
        serialized_course ={
                "id": cour.id,
                "name": cour.name,
                "pdf_files": cour.pdf_files,
                "summary": cour.summary,
                "created_at": cour.created_at.isoformat(),
                "user_id": cour.user_id,
                "conversation": cour.conversation or None,
                "exam":cour.exam,
                "exam_correction":cour.exam_correction

            }
            
        
 
        
        # Return the response
        return JSONResponse(content={"message": "Course uploaded successfully!", "course": serialized_course}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/courses/{user_id}/")
async def get_courses_by_user(user_id: int, db: Session = Depends(get_db)):
    try:
        # Query the database for all courses with the given user_id
        courses = db.query(Course).filter(Course.user_id == user_id).all()

        if not courses:
            raise HTTPException(status_code=404, detail="No courses found for this user")

        # Serialize the courses to JSON-compatible format
        courses_response = [course for course in courses]
        print("aaaa:",courses_response)

        # Return the courses
        return {"courses": courses_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




















   

from fastapi import FastAPI, HTTPException, Depends, Form
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from models import Train
from pydantic import BaseModel

app = FastAPI(
    title="My First FastApi Project ",
    description="This is a project was created to learn FastApi framework and was tested by me Chubko ",
    version="1.1.2",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Deadpoolio the Amazing",
        "url": "http://x-force.example.com/contact/",
        "email": "misha.chubko@example.com",
    }
)

SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc://admin:123456789@DESKTOP-V6MD99V\\MSSQLSERVER1/TrainRoutes?driver=SQL+Server"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функція створення сесії
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    try:
        # Створюємо нову сесію
        with SessionLocal() as db:
            # Виконуємо запит до БД
            result = db.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"Підключення до бази даних успішне.{value}")
    except Exception as e:
        print(f"Помилка підключення до бази даних: {e}")

@app.on_event("shutdown")
def shutdown():
    print("Shutdown event")

@app.get("/")
async def read_root():
    return {"Hello": "World"}

templates = Jinja2Templates(directory="templates")

@app.get("/train-management", response_class=HTMLResponse)
async def train_management(request: Request):
    return templates.TemplateResponse("train_crud.html", {"request": request})

# @app.get("/items/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: int):
#     # Створення контексту для шаблону (змінні, які будуть доступні у шаблоні)
#     context = {"request": request, "id": id}
#     # Рендеринг HTML-шаблону з контекстом
#     return templates.TemplateResponse("item.html", context)

# @app.get("/home")
# async def get_home(request: Request):
#     return templates.TemplateResponse("home.html", {"request": request})



# Pydantic модель для вхідних даних Train
class TrainCreate(BaseModel):
    TrainName: str
    TrainType: str

# Pydantic модель для входных данных Train
class TrainUpdate(BaseModel):
    train_id: int
    train_name: str
    train_type: str

# CRUD-операції

# Create
@app.post("/trains/")
async def create_train(TrainName: str = Form(...), TrainType: str = Form(...), db: Session = Depends(get_db)):
    print(f"Received: TrainName={TrainName}, TrainType={TrainType}")  
    new_train = Train(TrainName=TrainName, TrainType=TrainType)
    db.add(new_train)
    db.commit()
    db.refresh(new_train)
    return {"success": True, "created_train": new_train}

# Read
@app.get("/trains/{train_id}")
async def read_train(train_id: int, db: Session = Depends(get_db)):
    train = db.query(Train).filter(Train.TrainID == train_id).first()
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

# Update
@app.post("/trains/update", response_class=HTMLResponse)
async def update_train(
    train_id: int = Form(...),
    train_name: str = Form(None),
    train_type: str = Form(None),
    db: Session = Depends(get_db)
):
    train = db.query(Train).filter(Train.TrainID == train_id).first()
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    
    if train_name:
        train.TrainName = train_name
    if train_type:
        train.TrainType = train_type
    
    db.commit()
    message = f"Train successfully updated: {train.TrainName} ({train.TrainType})"
    return templates.TemplateResponse("message.html", {"request": request, "message": message})

# Delete
@app.post("/trains/delete", response_model=dict)
async def delete_train(TrainID: int = Form(...), db: Session = Depends(get_db)):
    train = db.query(Train).filter(Train.TrainID == TrainID).first()
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    db.delete(train)
    db.commit()
    return {"success": True, "message": "Train deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

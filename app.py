from fastapi import FastAPI, HTTPException, Depends
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

# templates = Jinja2Templates(directory="templates")

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

# Pydantic модель для оновлення даних Train
class TrainUpdate(BaseModel):
    TrainName: str
    TrainType: str

# CRUD-операції

# Create
@app.post("/trains/")
async def create_train(train_create: TrainCreate, db: Session = Depends(get_db)):
    new_train = Train(TrainName=train_create.TrainName, TrainType=train_create.TrainType)
    db.add(new_train)
    db.commit()
    db.refresh(new_train)
    return new_train

# Read
@app.get("/trains/{train_id}")
async def read_train(train_id: int, db: Session = Depends(get_db)):
    train = db.query(Train).filter(Train.TrainID == train_id).first()
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

# Update
@app.put("/trains/{train_id}")
async def update_train(train_id: int, train_update: TrainUpdate, db: Session = Depends(get_db)):
    train = db.query(Train).filter(Train.TrainID == train_id).first()
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    train.TrainName = train_update.TrainName
    train.TrainType = train_update.TrainType
    db.commit()
    return train

# Delete
@app.delete("/trains/{train_id}")
async def delete_train(train_id: int, db: Session = Depends(get_db)):
    train = db.query(Train).filter(Train.TrainID == train_id).first()
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    db.delete(train)
    db.commit()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

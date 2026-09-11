from fastapi import FastAPI, Depends
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List
from pydantic import BaseModel


# Configuración DB
DATABASE_URL = "sqlite:///./items.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

Base.metadata.create_all(bind=engine)

# Modelo SQLAlchemy
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default="")
    price = Column(Float)
    tags = Column(String)  # Guardamos las etiquetas como texto separado por comas

Base.metadata.create_all(bind=engine)

# Modelo Pydantic
class Item(BaseModel):
    name: str
    description: str = ""
    price: float
    tags: List[str] = []

# FastAPI
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-para-la-tienda-paisa.vercel.app"],  # dirección del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/items/", response_model=list[Item])
def list_items(db: Session = Depends(get_db)):
    items = db.query(ItemDB).all()
    return items


@app.get("/items/")
def list_items(db: Session = Depends(get_db)):
    items = db.query(ItemDB).all()
    return items


# IA simple: recomendar productos por etiquetas
@app.get("/recommend/{tag}")
def recommend(tag: str, db: Session = Depends(get_db)):
    items = db.query(ItemDB).filter(ItemDB.tags.like(f"%{tag}%")).all()
    return {"recommendations": [item.name for item in items]}

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        return {"error": f"Item con id {item_id} no encontrado"}
    db.delete(item)
    db.commit()
    return {"message": f"Item con id {item_id} eliminado con éxito"}

@app.get("/")
def read_root():
    return {"message": "Backend Tienda Paisa activo"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("proyecto1_ventas:app", host="127.0.0.1", port=8000, reload=True)

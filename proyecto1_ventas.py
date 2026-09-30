

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import List
from pydantic import BaseModel
import os

# 🔧 Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./items.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🧩 Modelo SQLAlchemy
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default="")
    price = Column(Float)
    tags = Column(String)  # Guardamos las etiquetas como texto separado por comas

Base.metadata.create_all(bind=engine)

# 🧩 Modelo Pydantic
class Item(BaseModel):
    name: str
    description: str = ""
    price: float
    tags: List[str] = []

# 🚀 Inicialización de FastAPI
app = FastAPI()

# 🌐 Configuración CORS (para Vercel y local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://front3-eight.vercel.app",  # dominio público del frontend
        "http://localhost:3000"             # para pruebas locales
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📦 Crear producto
@app.post("/items/")
def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemDB(
        name=item.name,
        description=item.description,
        price=item.price,
        tags=",".join(item.tags)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item {item.name} creado con éxito"}

# 📋 Listar productos
@app.get("/items/")
def list_items(db: Session = Depends(get_db)):
    items = db.query(ItemDB).all()
    return items

# 🤖 Recomendaciones por etiqueta
@app.get("/recommend/{tag}")
def recommend(tag: str, db: Session = Depends(get_db)):
    items = db.query(ItemDB).filter(ItemDB.tags.like(f"%{tag}%")).all()
    return {"recommendations": [item.name for item in items]}

# 🗑️ Eliminar producto
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if not item:
        return {"error": f"Item con id {item_id} no encontrado"}
    db.delete(item)
    db.commit()
    return {"message": f"Item con id {item_id} eliminado con éxito"}

# 🏠 Ruta raíz
@app.get("/")
def read_root():
    return {"message": "Backend Tienda Paisa activo"}

# ⚙️ Configuración para local y Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("proyecto1_ventas:app", host="0.0.0.0", port=8000)


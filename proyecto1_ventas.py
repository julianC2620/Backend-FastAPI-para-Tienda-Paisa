

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

# 🔧 Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./items.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 🧩 Modelo ORM
class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    tags = Column(String)

Base.metadata.create_all(bind=engine)

# 🚀 Inicialización de FastAPI
app = FastAPI()

# 🌐 Configuración CORS (para Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend-para-la-tienda-paisa.vercel.app"],  # dominio de tu frontend
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

# 📦 Endpoint para listar productos
@app.get("/items/")
def list_items(db: Session = Depends(get_db)):
    items = db.query(ItemDB).all()
    return items

# 🏠 Ruta raíz opcional
@app.get("/")
def read_root():
    return {"message": "Backend Tienda Paisa activo"}

# ⚙️ Configuración para local y Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("proyecto1_ventas:app", host="0.0.0.0", port=port)

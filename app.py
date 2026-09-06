
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Time, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi import FastAPI, HTTPException
from datetime import date, time

# crear una instancia de FastAPI
app = FastAPI()

# crear una base de datos SQLite
Base = declarative_base()
engine = create_engine("sqlite:///./app.db", echo=True)

# crear una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# crear una clase que represente un producto en la tabla de la base de datos

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True, nullable=False)
    nombre = Column(String, index=True, unique=True, nullable=False)
    precio = Column(Float, nullable=False)

#crear las tablas en el archivo si no existen
Base.metadata.create_all(bind=engine)

# agregar un producto a la base de datos
@app.post("/productos/")
def agregar_producto(nombre: str, precio: float):
    db = SessionLocal()
    nuevo_producto = Producto(nombre=nombre, precio=precio)
    db.add(nuevo_producto)
    try:
        db.commit()
        db.refresh(nuevo_producto)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al agregar el producto: ")
    db.close()
    return {"id": nuevo_producto.id, "nombre": nuevo_producto.nombre, "precio": nuevo_producto.precio}

# obtener todos los productos de la base de datos
@app.get("/productos/")
def obtener_productos():
    db = SessionLocal()
    productos = db.query(Producto).all()
    db.close()
    return productos

# obtener un producto por su id
@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int):
    db = SessionLocal()
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    db.close()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

#actualizar un producto por su id
@app.put("/productos/{producto_id}")
def actualizar_producto(producto_id: int, nombre: str, precio: float):
    db = SessionLocal()
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.nombre = nombre
    producto.precio = precio
    try:
        db.commit()
        db.refresh(producto)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar el producto")
    db.close()
    return {"id": producto.id, "nombre": producto.nombre, "precio": producto.precio}

#eliminar un producto por su id
@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int):
    db = SessionLocal()
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    try:
        db.delete(producto)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al eliminar el producto")
    db.close()
    return {"detail": "Producto eliminado correctamente"}

# endpoints para gestionar ventas sobre un sólo producto

# crear una clase que represente una venta en la tabla de la base de datos
class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_total = Column(Float, nullable=False)

# crear las tablas en el archivo si no existen
Base.metadata.create_all(bind=engine)

# crear una venta para un producto
@app.post("/ventas/")
def crear_venta(producto_id: int, cantidad: int, fecha: date, hora: time):
    db = SessionLocal()
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    precio_total = producto.precio * cantidad
    nueva_venta = Venta(fecha=fecha, hora=hora, producto_id=producto_id, cantidad=cantidad, precio_total=precio_total)
    db.add(nueva_venta)
    try:
        db.commit()
        db.refresh(nueva_venta)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear la venta")
    db.close()
    return {"id": nueva_venta.id, "fecha": nueva_venta.fecha, "hora": nueva_venta.hora, "producto_id": nueva_venta.producto_id, "cantidad": nueva_venta.cantidad, "precio_total": nueva_venta.precio_total}

# obtener todas las ventas de la base de datos
@app.get("/ventas/")
def obtener_ventas():
    db = SessionLocal()
    ventas = db.query(Venta).all()
    db.close()
    return ventas

# obtener una venta por su id
@app.get("/ventas/{venta_id}")
def obtener_venta(venta_id: int):
    db = SessionLocal()
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    db.close()
    if venta is None:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

# actualizar una venta por su id
@app.put("/ventas/{venta_id}")
def actualizar_venta(venta_id: int, cantidad: int, fecha: date, hora: time):
    db = SessionLocal()
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if venta is None:
        db.close()
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    producto = db.query(Producto).filter(Producto.id == venta.producto_id).first()
    if producto is None:
        db.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    venta.cantidad = cantidad
    venta.fecha = fecha
    venta.hora = hora
    venta.precio_total = producto.precio * cantidad
    try:
        db.commit()
        db.refresh(venta)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar la venta")
    db.close()
    return {"id": venta.id, "fecha": venta.fecha, "hora": venta.hora, "producto_id": venta.producto_id, "cantidad": venta.cantidad, "precio_total": venta.precio_total}

# eliminar una venta por su id
@app.delete("/ventas/{venta_id}")
def eliminar_venta(venta_id: int):
    db = SessionLocal()
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if venta is None:
        db.close()
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    try:
        db.delete(venta)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al eliminar la venta")
    db.close()
    return {"detail": "Venta eliminada correctamente"}
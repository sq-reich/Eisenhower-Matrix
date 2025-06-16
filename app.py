from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from database import SessionLocal, engine
from models import Task, Property, Base

# DB-Tabellen erstellen
Base.metadata.create_all(bind=engine)

# App-Setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# DB-Zugriffsfunktion
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Weiterleitung zur Matrix
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")

# DASHBOARD: Eisenhower-Matrix
@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    todos = db.query(Task).options(joinedload(Task.property)).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "todos": todos
    })

# KALENDER
@app.get("/calendar")
async def calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})

# TODO-LISTE
@app.get("/todos")
def todos(request: Request, db: Session = Depends(get_db)):
    todos = db.query(Task).options(joinedload(Task.property)).all()
    return templates.TemplateResponse("todos.html", {
        "request": request,
        "todo_list": todos,
        "current_date": datetime.today().strftime("%Y-%m-%d")
    })

# NEUE Aufgabe + Eigenschaften hinzufügen
@app.post("/add")
def add_task(
    request: Request,
    title: str = Form(...),
    importance: bool = Form(False),
    urgency: bool = Form(False),
    db: Session = Depends(get_db)
):
    new_task = Task(title=title.strip())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    new_property = Property(
        importance=importance,
        urgency=urgency,
        completed=False,
        task_id=new_task.id
    )
    db.add(new_property)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_303_SEE_OTHER)

# STATUS (done) toggeln
@app.post("/update/{task_id}")
def update_status(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or not task.property:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")

    task.property.completed = not task.property.completed
    db.commit()

    return JSONResponse(content={"complete": task.property.completed}, status_code=200)


# LÖSCHEN einer Aufgabe
@app.get("/delete/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

# BEARBEITEN einer Aufgabe (Titel, Wichtigkeit, Dringlichkeit)
@app.post("/edit/{task_id}")
def edit_task(
    
    task_id: int,
    title: str = Form(...),
    importance: bool = Form(False),
    urgency: bool = Form(False),
    db: Session = Depends(get_db)
):
    print("EDIT:", task_id, title, importance, urgency)
    # Task holen
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")

    if not task.property:
        raise HTTPException(status_code=404, detail="Eigenschaften fehlen zur Aufgabe")

    # Aktualisieren
    task.title = title.strip()
    task.property.importance = importance
    task.property.urgency = urgency

    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_303_SEE_OTHER)

# ALLE Aufgaben löschen
@app.post("/clear")
def clear_all(db: Session = Depends(get_db)):
    db.query(Property).delete()
    db.query(Task).delete()
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_303_SEE_OTHER)

from fastapi import FastAPI, Depends, Request, Form, status, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date

import models
from database import SessionLocal, engine

from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

# App-Setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/calendar")
async def calendar(request: Request):
    return templates.TemplateResponse("calendar.html", {"request": request})

# Todos anzeigen
@app.get("/todos")
def todos(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    today = date.today().strftime("%Y-%m-%d")
    return templates.TemplateResponse("todos.html", {
        "request": request,
        "todo_list": todos,
        "current_date": today
    })

# ToDo hinzufügen mit Validierung
@app.post("/add")
def add(
    request: Request,
    title: str = Form(...),
    due_date: str = Form(None),
    priority: str = Form("medium"),
    db: Session = Depends(get_db)
):
    due_date_obj = None
    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungültiges Datum")
        
        if due_date_obj < date.today():
            raise HTTPException(status_code=400, detail="Datum darf nicht in der Vergangenheit liegen.")

    new_todo = models.Todo(
        title=title.strip(),
        due_date=due_date_obj,
        priority=priority
    )
    db.add(new_todo)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_303_SEE_OTHER)

# Status toggeln (POST, JSON Response)
@app.post("/update/{todo_id}")
def update(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo nicht gefunden")
    
    todo.complete = not todo.complete
    db.commit()

    return JSONResponse(
        content={"complete": todo.complete},
        status_code=200
    )

# ToDo löschen
@app.get("/delete/{todo_id}")
def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if todo:
        db.delete(todo)
        db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@app.post("/edit/{todo_id}")
def edit_todo(
    todo_id: int,
    title: str = Form(...),
    due_date: str = Form(None),
    priority: str = Form("medium"),
    db: Session = Depends(get_db)
):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo nicht gefunden")

    todo.title = title.strip()
    todo.priority = priority

    if due_date:
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Ungültiges Datum")

        if due_date_obj < date.today():
            raise HTTPException(status_code=400, detail="Datum darf nicht in der Vergangenheit liegen.")

        todo.due_date = due_date_obj
    else:
        todo.due_date = None

    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/clear")
def clear_all_todos(request: Request, db: Session = Depends(get_db)):
    db.query(models.Todo).delete()
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_303_SEE_OTHER)

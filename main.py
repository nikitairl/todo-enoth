from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
from database import engine, session

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db():
    """Provides a context manager for a database session.

    Yields a database session object that can be used to query or modify the
    database. Once the context is exited, the session is automatically closed.

    Returns
    -------
    context manager
        A context manager for a database session.
    """
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    """
    Handle GET requests to the home page.

    :param request: the incoming request.
    :param db: the database session to use.
    :return: a TemplateResponse containing the rendered index.html template.
    """
    todos = db.query(models.ToDo).order_by(models.ToDo.id.desc())
    return templates.TemplateResponse(
        "index.html", {"request": request, "todos": todos}
    )


@app.post("/add")
async def add(request: Request, task: str = Form(...), db: Session = Depends(get_db)):
    """
    Add a new task to the database.

    Args:
        request (Request): The incoming HTTP request.
        task (str): The description of the task to add.
        db (Session): The current database session.

    Returns:
        RedirectResponse: A redirect response to the home page.
    """
    todo = models.ToDo(task=task)
    db.add(todo)
    db.commit()
    return RedirectResponse(
        url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/complete/{todo_id}")
async def complete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    Complete a to-do item.

    Args:
        request (fastapi.Request): The incoming request.
        todo_id (int): The ID of the to-do item to complete.
        db (sqlalchemy.orm.Session, optional): The database session. Defaults to
            Depends(get_db).

    Returns:
        fastapi.responses.RedirectResponse: A redirect response to the home page.
    """
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    todo.completed = True
    db.commit()
    return RedirectResponse(
        url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/edit/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    Get a specific todo item from the database and render the edit page.

    Arguments:
    - request (Request): the HTTP request object.
    - todo_id (int): the ID of the todo item to edit.
    - db (Session): the database session dependency.

    Returns:
    - TemplateResponse: the HTTP response with the rendered edit page.
    """
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "todo": todo})


@app.post("/edit/{todo_id}")
async def add(
    request: Request,
    todo_id: int,
    task: str = Form(...),
    completed: bool = Form(False),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Edit a TODO item with the given todo_id in the database.

    Args:
        request (Request): The incoming request.
        todo_id (int): The ID of the TODO item to edit.
        task (str, optional): The new task description. Defaults to Form(...).
        completed (bool, optional): Whether the task is completed. Defaults to Form(False).
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        RedirectResponse: A redirect response to the home page with status code 200 OK.
    """
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    todo.task = task
    todo.completed = completed
    db.commit()
    return RedirectResponse(
        url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER
    )


@app.get("/delete/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    """
    Delete a ToDo item from the database.

    Args:
        request: A Request object representing the HTTP request.
        todo_id: An integer representing the ID of the ToDo item to delete.
        db: A Session object representing the database session.

    Returns:
        A RedirectResponse object that redirects to the home page with a 200 OK status code.
    """
    todo = db.query(models.ToDo).filter(models.ToDo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(
        url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER
    )

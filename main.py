from fastapi import FastAPI

from src.routes import notes, tags, contacts

app = FastAPI()

app.include_router(tags.router, prefix='/api')
app.include_router(notes.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}

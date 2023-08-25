import asyncio
import logging
from fastapi_limiter import FastAPILimiter
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import redis.asyncio as redis


from src.routes import contact, auth, users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static"), name="static")

app.include_router(auth.router)
app.include_router(contact.router, prefix='/api')



app.include_router(auth.router, prefix='/api')
app.include_router(contact.router, prefix='/api')
app.include_router(users.router, prefix='/api')

async def task():
    await asyncio.sleep(3)
    print("send email")
    return True

@app.on_event("startup")
async def startup():
    r = await redis.Redis(host='localhost', port=6379, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
async def read_root(background_tasks: BackgroundTasks):
    background_tasks.add_task(task)
    return {"message": "Contacts API"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="localhost", reload=True, log_level="info")

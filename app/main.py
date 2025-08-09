from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(title="anka-tech-backend")

    @app.get("/")
    async def root():
        return {"message": "hello from FastAPI"}

    return app

app = create_app()

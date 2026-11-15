from fastapi import FastAPI

app = FastAPI(title="Calculator",)


@app.get("/health")
def health():
    return {"status": "ok"}
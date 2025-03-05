from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/dashboard")
html_file_path = Path(__file__).parent / ".." / "templates" / "index.html"


@router.get("/")
async def get() -> HTMLResponse:
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

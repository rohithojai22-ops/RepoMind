import base64
import httpx
from .config import settings

TEXT_EXTENSIONS = {
    ".py":"python",".js":"javascript",".jsx":"javascript",".ts":"typescript",
    ".tsx":"typescript",".java":"java",".cpp":"cpp",".cc":"cpp",".c":"c",
    ".h":"c",".hpp":"cpp",".go":"go",".rs":"rust",".rb":"ruby",".php":"php",
    ".cs":"csharp",".sql":"sql",".html":"html",".css":"css",".md":"markdown",
    ".json":"json",".yml":"yaml",".yaml":"yaml",".sh":"shell",".txt":"text"
}
IGNORE_DIRS = {".git","node_modules","dist","build",".next","venv",".venv","__pycache__",".idea"}

def parse_repo_url(url: str):
    cleaned = url.rstrip("/").replace(".git", "")
    parts = cleaned.split("/")
    if len(parts) < 2 or "github.com" not in cleaned:
        raise ValueError("Use a GitHub repository URL such as https://github.com/owner/repo")
    return parts[-2], parts[-1]

async def fetch_repo_files(url: str):
    owner, repo = parse_repo_url(url)
    headers = {"Accept":"application/vnd.github+json"}
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1")
        r.raise_for_status()
        tree = r.json().get("tree", [])
        results = []

        for item in tree:
            path = item.get("path","")
            if item.get("type") != "blob" or any(x in IGNORE_DIRS for x in path.split("/")):
                continue
            lower = path.lower()
            ext = "." + lower.rsplit(".",1)[-1] if "." in lower else ""
            if ext not in TEXT_EXTENSIONS or item.get("size",0) > 200_000:
                continue

            cr = await client.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref=HEAD")
            if cr.status_code != 200:
                continue
            data = cr.json()
            if data.get("encoding") != "base64":
                continue
            try:
                content = base64.b64decode(data["content"]).decode("utf-8")
            except UnicodeDecodeError:
                continue

            results.append({"path":path,"language":TEXT_EXTENSIONS[ext],"content":content})

        return owner, repo, results

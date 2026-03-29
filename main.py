import os
import httpx
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
app = FastAPI(
    title = "ClaudeOps",
    description = "AI agent pipeline that turns GitLab issues into merge requests",
    version = "1.0.0",
)

class GitLabClient:
    def __init__(self, base_url: str, token: str, project_id: str):
        self.base_url = base_url.rstrip("/")
        self.project_id = project_id
        self.headers = {
            "PRIVATE-TOKEN": token,
            "Content-Type": "application/json",
        }
        self.api_base = f"{self.base_url}/api/v4/projects/{project_id}"

    async def create_branch(self, branch_name: str, from_branch: str = "main") -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.api_base}/repository/branches",
                headers = self.headers,
                json = {
                    "branch": branch_name, 
                    "ref": from_branch,
                    "author_name": "ClaudeOps",
                    "author_email": "bot@claudeops.ai"
                },
            )
            r.raise_for_status()
            
            return r.json()

async def test(gitlab: GitLabClient):
    try:
        await gitlab.create_branch(
            branch_name = "test", 
            from_branch = "main"
        )
        
        print("Branch created")
    except Exception as e:
        print(e)
        
@app.get("/test")
async def testa():
    gitlab = GitLabClient(
        base_url = os.getenv("GITLAB_URL"),
        token = os.getenv("GITLAB_TOKEN"),
        project_id = os.getenv("GITLAB_PROJECT_ID"),
    )
    
    await test(gitlab)
    
    return {
        "status": "done"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gitlab_url": os.getenv("GITLAB_URL"),
        "project_id": os.getenv("GITLAB_PROJECT_ID"),
        "token_set": bool(os.getenv("GITLAB_TOKEN")),
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host = "0.0.0.0", 
        port = 8000, 
        reload = True
    )
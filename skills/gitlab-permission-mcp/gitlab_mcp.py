# GitLab 仓库权限管理 MCP

通过 Agent/MCP 控制 GitLab 仓库权限，支持：
- 根据邮箱查找用户
- 添加/删除仓库成员
- 设置权限级别（只读/开发者/维护者等）

## 使用方法

### 1. 配置 GitLab Access Token

在环境变量中设置：
```bash
export GITLAB_TOKEN="your-personal-access-token"
export GITLAB_URL="https://gitlab.com"  # 或自建 GitLab 地址
```

Token 需要以下权限：
- `read_api`
- `read_user`
- `write_repository` (用于添加成员)

### 2. 使用示例

```
请帮我给 user@example.com 添加仓库 mygroup/myproject 的只读权限
```

或直接调用 MCP：

```
add_gitlab_member(email="user@example.com", repo="mygroup/myproject", access_level="reporter")
```

## GitLab 访问级别

| 级别 | 常量 | 描述 |
|------|------|------|
| 10 | guest | 来宾（仅查看） |
| 20 | reporter | **只读（Reporter）** |
| 30 | developer | 开发者 |
| 40 | maintainer | 维护者 |
| 50 | owner | 所有者 |

## 实现代码

```python
"""
GitLab 仓库权限管理 MCP
"""
import os
import requests
from typing import Optional


class GitLabPermissionManager:
    def __init__(self, token: str = None, url: str = "https://gitlab.com"):
        self.token = token or os.environ.get("GITLAB_TOKEN")
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "PRIVATE-TOKEN": self.token,
            "Content-Type": "application/json"
        })
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """根据邮箱查找用户"""
        response = self.session.get(
            f"{self.url}/api/v4/users",
            params={"search": email}
        )
        response.raise_for_status()
        users = response.json()
        
        for user in users:
            if user.get("email") == email:
                return user
        
        # 如果精确匹配没找到，尝试模糊搜索
        if users:
            return users[0]
        return None
    
    def get_project(self, repo: str) -> Optional[dict]:
        """根据仓库路径查找项目"""
        # URL 编码
        project_path = repo.replace("/", "%2F")
        response = self.session.get(
            f"{self.url}/api/v4/projects/{project_path}"
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def add_member(
        self,
        email: str,
        repo: str,
        access_level: str = "reporter"
    ) -> dict:
        """添加仓库成员"""
        # 访问级别映射
        access_levels = {
            "guest": 10,
            "reporter": 20,
            "developer": 30,
            "maintainer": 40,
            "owner": 50
        }
        
        level = access_levels.get(access_level.lower(), 20)
        
        # 查找用户
        user = self.get_user_by_email(email)
        if not user:
            raise ValueError(f"未找到邮箱为 {email} 的用户")
        
        # 查找项目
        project = self.get_project(repo)
        if not project:
            raise ValueError(f"未找到仓库 {repo}")
        
        # 添加成员
        response = self.session.post(
            f"{self.url}/api/v4/projects/{project['id']}/members",
            json={
                "user_id": user["id"],
                "access_level": level
            }
        )
        
        # 如果已存在，更新权限
        if response.status_code == 409:
            # 先移除再添加
            self.remove_member(email, repo)
            response = self.session.post(
                f"{self.url}/api/v4/projects/{project['id']}/members",
                json={
                    "user_id": user["id"],
                    "access_level": level
                }
            )
        
        response.raise_for_status()
        return response.json()
    
    def remove_member(self, email: str, repo: str) -> bool:
        """移除仓库成员"""
        user = self.get_user_by_email(email)
        if not user:
            return False
        
        project = self.get_project(repo)
        if not project:
            return False
        
        response = self.session.delete(
            f"{self.url}/api/v4/projects/{project['id']}/members/{user['id']}"
        )
        return response.status_code in [200, 204]
    
    def list_members(self, repo: str) -> list:
        """列出仓库成员"""
        project = self.get_project(repo)
        if not project:
            return []
        
        response = self.session.get(
            f"{self.url}/api/v4/projects/{project['id']}/members/all"
        )
        response.raise_for_status()
        return response.json()


# MCP 工具函数
def add_gitlab_member(email: str, repo: str, access_level: str = "reporter") -> str:
    """MCP 工具：添加 GitLab 仓库成员"""
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        return "错误：请设置 GITLAB_TOKEN 环境变量"
    
    manager = GitLabPermissionManager()
    
    try:
        result = manager.add_member(email, repo, access_level)
        return f"✅ 成功添加 {email} 到仓库 {repo}，权限级别：{access_level}"
    except Exception as e:
        return f"❌ 错误：{str(e)}"


def remove_gitlab_member(email: str, repo: str) -> str:
    """MCP 工具：移除 GitLab 仓库成员"""
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        return "错误：请设置 GITLAB_TOKEN 环境变量"
    
    manager = GitLabPermissionManager()
    
    try:
        manager.remove_member(email, repo)
        return f"✅ 成功从仓库 {repo} 移除成员 {email}"
    except Exception as e:
        return f"❌ 错误：{str(e)}"


def list_gitlab_members(repo: str) -> str:
    """MCP 工具：列出仓库成员"""
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        return "错误：请设置 GITLAB_TOKEN 环境变量"
    
    manager = GitLabPermissionManager()
    
    try:
        members = manager.list_members(repo)
        if not members:
            return f"仓库 {repo} 没有成员"
        
        result = [f"仓库 {repo} 的成员："]
        for m in members:
            result.append(f"- {m['name']} ({m['username']}): {m['access_level']}")
        return "\n".join(result)
    except Exception as e:
        return f"❌ 错误：{str(e)}"

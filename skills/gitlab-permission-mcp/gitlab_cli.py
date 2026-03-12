#!/usr/bin/env python3
"""
GitLab Permission MCP - 命令行工具
"""
import os
import sys

# 如果没有环境变量，显示设置说明
if not os.environ.get("GITLAB_TOKEN"):
    print("=" * 50)
    print("GitLab Permission MCP - 快速开始")
    print("=" * 50)
    print("\n请先设置环境变量：")
    print()
    print("  export GITLAB_TOKEN='your-personal-access-token'")
    print("  export GITLAB_URL='https://gitlab.com'  # 或自建 GitLab")
    print()
    print("创建 Token 方法：")
    print("  1. 登录 GitLab")
    print("  2. 点击头像 → Settings → Access Tokens")
    print("  3. 创建 Token，勾选: read_api, write_repository")
    print()
    sys.exit(1)

from gitlab_mcp import (
    GitLabPermissionManager,
    add_gitlab_member,
    remove_gitlab_member,
    list_gitlab_members
)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python gitlab_cli.py add <email> <repo> [权限级别]")
        print("  python gitlab_cli.py remove <email> <repo>")
        print("  python gitlab_cli.py list <repo>")
        print()
        print("权限级别: guest, reporter(默认), developer, maintainer, owner")
        sys.exit(1)
    
    cmd = sys.argv[1]
    manager = GitLabPermissionManager()
    
    if cmd == "add":
        if len(sys.argv) < 4:
            print("错误：需要提供邮箱和仓库")
            sys.exit(1)
        
        email = sys.argv[2]
        repo = sys.argv[3]
        level = sys.argv[4] if len(sys.argv) > 4 else "reporter"
        
        result = manager.add_member(email, repo, level)
        print(f"✅ 成功添加 {email} 到 {repo}，权限: {level}")
        
    elif cmd == "remove":
        if len(sys.argv) < 4:
            print("错误：需要提供邮箱和仓库")
            sys.exit(1)
        
        email = sys.argv[2]
        repo = sys.argv[3]
        
        manager.remove_member(email, repo)
        print(f"✅ 成功从 {repo} 移除 {email}")
        
    elif cmd == "list":
        if len(sys.argv) < 3:
            print("错误：需要提供仓库")
            sys.exit(1)
        
        repo = sys.argv[2]
        members = manager.list_members(repo)
        
        print(f"\n仓库 {repo} 的成员：")
        for m in members:
            print(f"  - {m['name']} ({m['username']}): {m['access_level']}")
    
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()

---
name: gitlab-permission-mcp
description: 通过 Agent 控制 GitLab 仓库权限，自动添加/移除成员，设置只读/开发/维护权限
version: 1.0.0
author: forzyh
tags: [gitlab, mcp, permission, automation]
---

# GitLab 仓库权限管理 MCP

通过 Agent 自动控制 GitLab 仓库成员权限。

## 触发场景

- 用户要求给某人添加 GitLab 仓库权限
- 用户要求移除仓库成员
- 用户要求查看仓库成员列表

## 前置要求

1. **GitLab Access Token**：
   - 登录 GitLab → Settings → Access Tokens
   - 创建 Personal Access Token
   - 勾选权限：`read_api`, `read_user`, `write_repository`

2. **设置环境变量**：
   ```
   GITLAB_TOKEN=your-token
   GITLAB_URL=https://gitlab.com  # 或自建 GitLab 地址
   ```

## 使用示例

### 添加只读权限
```
请帮我给 user@example.com 添加仓库 mygroup/myproject 的只读权限
```

### 添加开发者权限
```
请把 developer@example.com 添加到 frontend-team/webapp 仓库，权限是开发者
```

### 移除成员
```
请把 user@example.com 从 backend-api 仓库中移除
```

### 查看成员列表
```
列出 devops/project 仓库的所有成员
```

## 权限级别

| 级别 | 关键词 | 描述 |
|------|--------|------|
| 10 | guest | 来宾 - 仅可查看 |
| 20 | **reporter** | **只读** - 可拉取代码 |
| 30 | developer | 开发者 - 可推送代码 |
| 40 | maintainer | 维护者 - 可管理设置 |
| 50 | owner | 所有者 - 完全控制 |

## API 参考

### 添加成员
```python
add_gitlab_member(
    email="user@example.com",
    repo="group/project",
    access_level="reporter"  # 默认只读
)
```

### 移除成员
```python
remove_gitlab_member(
    email="user@example.com",
    repo="group/project"
)
```

### 列出成员
```python
list_gitlab_members(repo="group/project")
```

## 实现逻辑

1. **查找用户** - 根据邮箱在 GitLab 中搜索用户
2. **查找仓库** - 根据路径查找项目
3. **添加成员** - 调用 GitLab API 添加成员并设置权限级别
4. **返回结果** - 反馈操作结果

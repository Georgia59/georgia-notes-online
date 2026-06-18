# GitHub Pages 配置说明

本项目按公开 GitHub Pages 下载站设计。

## 推荐设置

1. 在 GitHub 创建一个公开仓库。
2. 将本地仓库推送到 GitHub。
3. 打开仓库的 Settings。
4. 进入 Pages。
5. Source 选择 Deploy from a branch。
6. Branch 选择 `main`。
7. Folder 选择 `/ (root)`。
8. 保存后等待 GitHub Pages 生成网址。

## 为什么使用根目录发布

当前项目的 `index.html`、`assets/`、`data/`、`files/` 都在仓库根目录。使用根目录发布最简单，后续 Codex 只需要维护这些文件即可。

## 发布流程

1. 生成资料到 `review/课程目录/`。
2. 用户检查并确认可以公开发布。
3. 使用 `scripts/publish_review_file.py` 将成品移动到 `files/课程目录/`，并更新 `data/files.json` 和 `tasks/task-log.md`。
4. 运行：

```powershell
conda run -n py312 python scripts/pre_publish_check.py
conda run -n py312 python scripts/validate_files.py
```

5. 提交并推送到 GitHub。

## 注意事项

- `local-sources/` 是本地原始资料区，不发布。
- `review/` 是待检查区，不发布待检查文件。
- `files/` 是公开下载区，只有确认后的成品才能进入。
- 不要在公开文件中写入本地路径、原始文件名、患者隐私、同学信息或学校内部敏感信息。

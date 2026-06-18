# 待检查区

这里用于存放已经生成、但还没有经过用户最终确认的成品文件。

工作流：

1. Codex 从本地原始资料生成复习资料。
2. 生成品先保存到 `review/课程目录/`。
3. 用户检查内容、格式、隐私和版权风险。
4. 用户明确要求发布后，再移动到 `files/课程目录/`。
5. 发布时更新 `data/files.json` 和 `tasks/task-log.md`。
6. 发布前运行 `scripts/pre_publish_check.py` 和 `scripts/validate_files.py`。

本目录下的待检查文件默认不上传 GitHub。


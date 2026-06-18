# 待发布检查区

这里只用于存放用户明确要求“准备上传到网站”或“生成发布草案”的成品文件。

规则：

1. 普通资料生成完成后，不自动放入本目录。
2. 只有用户明确要求上传、发布、放入 `review/` 或生成发布草案时，Codex 才能把文件复制到本目录。
3. 进入本目录的文件必须同时生成 `*.publish-draft.json`，供用户检查网页文案和发布元数据。
4. 用户确认草案后，才可以将文件发布到 `files/课程目录/`。
5. 发布时更新 `data/files.json` 和 `tasks/task-log.md`。
6. 发布前运行 `scripts/pre_publish_check.py` 和 `scripts/validate_files.py`。

本目录下的待检查文件默认不上传 GitHub。


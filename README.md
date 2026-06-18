# Georgia 的医学学习资料输出中心

这个仓库是一个由 Codex 维护的医学本科课程复习资料输出中心。它不是普通云盘，重点保存已经加工好的学习成品、下载网页、模板、任务记录和自动化脚本。

原始 PPT、PDF、Word 可以留在本地电脑，不默认上传到 GitHub。生成后的成品文件统一放入 `files/课程目录/`，并通过 `data/files.json` 更新下载网页。

## 文件分类

当前课程目录：

- `files/imaging/`：医学影像学
- `files/diagnostics/`：诊断学
- `files/preventive-medicine/`：预防医学
- `files/pharmacoeconomics/`：药物经济学
- `files/surgery/`：外科学
- `files/others/`：其他课程或临时资料

当前阶段先固定使用以上 6 类。后续新增课程时，新增 `files/新课程目录/`，并在 `data/files.json` 的 `category` 中使用对应目录名即可；维护脚本不限制 category 必须属于以上 6 类。

命名规则：

```text
日期-英文短名-类型.扩展名
```

示例：

```text
2026-06-17-acute-osteomyelitis-review.pdf
```

## 如何新增资料

1. Codex 读取本地原始资料。
2. 按 `templates/` 中的模板生成复习资料。
3. 将待检查成品先保存到对应的 `review/课程目录/`。
4. 同时生成 `review/课程目录/文件名.publish-draft.json`，写入标题、简介、来源、标签、目标路径和网站链接。
5. 用户检查内容、格式、隐私、版权风险和发布草案。
6. 用户明确要求发布后，再根据草案移动到对应的 `files/课程目录/`。
7. 使用 `scripts/publish_review_file.py --metadata review/课程目录/文件名.publish-draft.json` 发布文件。
8. 在 `tasks/task-log.md` 记录任务。
9. 运行 `scripts/pre_publish_check.py` 和 `scripts/validate_files.py` 自检。

## 如何更新下载网站

下载网站是 `index.html`。它会读取 `data/files.json`，按课程分类展示文件，并生成下载按钮。

当新增或修改资料后，只要 `data/files.json` 更新，GitHub Pages 页面就会同步展示最新列表。

页面可以显示来源类型，例如“本地 PPT 整理”“教材整理”“错题整理”。不要在公开页面显示原始文件名、本地路径或内部资料编号。

下载站和正式输出资料应包含免责声明：资料仅用于课程学习与考试复习，不作为临床诊疗依据；待核实内容需以教材、指南或授课材料为准。

下载站只负责收纳和展示已经生成的成品文件，不预设必须生成哪种格式。每次任务可以根据当时策略选择 PDF、Word、PPT、HTML 或其他适合下载的文件类型。

同一份笔记可以上传多个格式版本。为便于网页合并展示，多格式版本应使用相同的 `note_id`，例如同一主题的 PDF、Word、HTML 都写 `acute-osteomyelitis-review`。网页会把它们显示为同一条笔记，并提供多个下载选项。

首页资料卡片的核心信息是：名称、 一句话简介、下载方式。课程、日期、来源、标签作为辅助信息展示。`description` 应尽量写成一句话，方便手机端快速浏览。

下载站按课程分区展示资料，不设置全站搜索。每个课程区块保留本课程内部搜索，适合在某一科目下快速找到笔记。

`data/files.json` 的字段规范见 `docs/files-json-fields.md`。简单说，字段规范就是每条下载记录应该写哪些信息、哪些字段必填、哪些内容不能公开写入。这样网页、脚本和以后 Codex 自动维护时都能按同一套格式工作。

GitHub Pages 发布配置见 `docs/github-pages-setup.md`。推荐使用公开仓库、`main` 分支、根目录发布。

## 不能上传的内容

- 患者隐私、病历号、身份证号、手机号、照片等可识别个人的信息
- 同学、老师或学校内部人员个人信息
- 学校内部敏感资料
- 未经明确要求上传的原始 PPT、PDF、Word
- 来源不明且可能侵犯版权的材料
- 原始文件名、本地路径、内部资料编号等不适合公开展示的信息

## 给 Codex 的日常任务指令模板

```text
请读取我本地的 [资料路径]，按 [模板名称] 生成 [本次需要的文件格式]。
课程分类放到 [imaging/diagnostics/preventive-medicine/pharmacoeconomics/surgery/others]。
请先保存成品到 review/[课程目录]/，并生成 publish-draft.json 给我检查。
我确认发布后，再根据草案移动到 files/[课程目录]/，更新 data/files.json 和 tasks/task-log.md，并运行发布前检查。
不要上传原始资料。
```

如果课程不在当前 6 类中，先新增一个英文短目录名，再将资料放入对应目录。

示例：

```text
请读取本地的急性骨髓炎课程资料，
按 disease-note-template 生成本次需要的复习资料格式。
课程分类放到 imaging。
先保存到 review/imaging/ 等我检查；我确认发布后，再更新下载网站和任务日志，并运行自检。
```

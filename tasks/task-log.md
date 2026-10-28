# 任务记录

## 2026-10-28

- 导入课程大纲板块 pages/syllabi.html，汇总九门课、290 个教学单元及 3,690 条可勾选学习要点，支持课程内搜索、展开或收起及浏览器保存复习进度。
- 在本学期进度首页、课程资料和佛脚刷题页面追加课程大纲入口；沿用现有首页、资料栏目、课程安排及进度存储，使用独立的大纲勾选记录。

- 课程资料页固定为“儿科学、外科学、其他”三个栏目，其余科目统一归入“其他”；资料卡片增加原课程名称，保留所有下载、预览与多格式合并。首次进入优先显示儿科学资料。

- 将本学期进度设为网站默认首页 index.html，原课程资料迁移至 courses.html；更新导航和返回链接，并保留旧进度网址跳转。
- 进度首页复用网站公共样式，新建 assets/progress.css、assets/progress.js 与 data/schedule.json，采用暖白背景、棕橙按钮与圆角卡片，适配手机布局。
- 保留 436 条课程安排和原有本地存储键，延续已有完成记录；补充存储不可用与课程加载失败时的提示。

- 新增本学期进度页面 `pages/progress.html`，导入 436 条课程安排，保留班级、日期范围、学科与形式筛选及浏览器本地完成记录。
- 首页与佛脚刷题页面导航按“本学期进度、课程资料、佛脚刷题”排列，新增页面提供相同顺序的导航。
- 移除教师字段中夹带的联系号码，修正连续节次识别，补充本地进度保存说明和学习用途免责声明。

## 2026-06-29

- 新增半自动后台页面 `admin.html`：支持浏览器内编辑 `data/files.json`、新增/复制/删除记录、调整顺序、基础校验、复制或下载 JSON 草稿；该页面不直接写入 GitHub。

## 2026-06-26

- 覆盖更新流行病学期末复习笔记（五部分）第一部分 PDF：重做“基础概念与描述性流行病学”，补全描述性研究样本含量影响因素、公式、抽样方法、质量控制和覆盖检查表；路径：`files/epidemiology/2026-06-18-epidemiology-final-review-notes/01-basics-descriptive-epidemiology.pdf`。

## 2026-06-18

- 新增佛脚刷题入口模块：`data/banks.json`、`pages/banks.html`、`images/banks/`、`scripts/validate_banks.py`，支持搜索、复制佛脚码、二维码展示和分章节题库合集。
- 发布佛脚刷题入口：预防医学章节刷题码，类型：Collection，章节数：13，路径：`pages/banks.html`，日期：2026-06-18。
- 优化佛脚刷题入口：来源改为“预防医学学习指导题目整理”，删除题库介绍展示，章节列表改为章节名、题库码和小复制按钮。
- 调整预防医学章节刷题码顺序：按章节编号升序展示，并移除页面额外生成的列表序号。

## 2026-06-17

- 初始化医学学习资料输出中心骨架。
- 创建课程文件夹、下载网页、索引数据、模板和维护脚本。
- 暂未处理任何真实医学资料。
- 明确公开下载站和正式输出资料必须包含学习用途免责声明。
- 明确当前先固定 6 个课程目录，后续新增科目时保持 category 和目录可扩展。
- 明确下载站只作为成品文件仓库，不预设每次任务必须生成的文件格式。
- 增加同一笔记多格式合并展示规则：通过 `note_id` 聚合，并显示多个下载选项。
- 明确首页卡片以名称、 一句话简介、下载方式为核心信息。
- 去掉全站搜索，改为每个课程区块内部搜索。
- 增加 `review/` 待检查区和 `local-sources/` 本地原始资料区。
- 增加 `.gitignore`、`.nojekyll`、字段规范文档和发布前检查脚本。
- 增加 `scripts/publish_review_file.py`，用于将已确认文件从 `review/` 发布到 `files/` 并更新索引。
- 将下载站首页改为 Claude-like 暖白配色、加大课程导航、单课程内容面板和居中免责声明。
- 发布资料：预防医学名词解释汇总，类型：PDF，路径：`files/preventive-medicine/2026-06-18-preventive-medicine-terms-summary.pdf`，日期：2026-06-18。
- 将首页右上角改为动态资料统计，移除卡片标签展示，并将预防医学名词解释来源改为“预防医学学习指导”。
- 调整发布草案流程：普通生成不自动进入 `review/`；只有用户明确要求上传、发布或生成发布草案时，才复制到 `review/` 并生成 `*.publish-draft.json`。
- 发布资料：外科学课本整理，类型：Collection，文件数：19，路径：`files/surgery/2026-06-18-surgery-general-textbook-notes/`，日期：2026-06-18。
- 发布资料：流行病学期末复习笔记（五部分），类型：Collection，文件数：5，路径：`files/epidemiology/2026-06-18-epidemiology-final-review-notes/`，日期：2026-06-18。
- 发布资料：预防医学名词解释汇总，类型：HTML 在线预览，文件数：1，路径：`notes/preventive-medicine/index.html`，日期：2026-06-18。

## 2026-06-19

- 增加 HTML 在线预览功能：`data/files.json` 支持 `previewUrl` 和 `downloadUrl`，首页显示“在线预览”按钮，并将预防医学名词解释 HTML 迁移到 `notes/preventive-medicine/index.html`。
- 接入两个外部学习站点入口：影像学笔记站和医学英语背单词；入口放在首页顶部导航，直接跳转到对应 GitHub Pages，不写入 `data/files.json`。

## 2026-06-20

- 将影像学笔记站和医学英语背单词从顶部导航移入课程索引，作为 `data/files.json` 中的 HTML 在线预览条目展示。
- 扩展文件索引规则：允许外部 GitHub Pages 学习站点使用外部 `previewUrl`，并在没有下载文件时省略 `path` 和 `downloadUrl`。
- 发布资料：诊断学实验诊断 NovaForge 笔记集，类型：Collection，文件数：5，路径：`files/diagnostics/2026-06-29-diagnostics-novaforge-lab-notes/`，日期：2026-06-29。
- 发布资料：实验诊断主观病例分析 16 分模板库，类型：PDF，文件数：1，路径：`files/diagnostics/2026-06-29-lab-diagnostics-subjective-cases-template.pdf`，日期：2026-06-29。
- 发布资料：实验诊断 A1+A2 选择题冲刺包，类型：PDF，文件数：1，路径：`files/diagnostics/2026-06-29-lab-diagnostics-a1-a2-crash-pack.pdf`，日期：2026-06-29。
- 发布资料：化验单分析课堂病例：主观题四句模板笔记，类型：PDF，文件数：1，路径：`files/diagnostics/2026-06-30-lab-diagnostics-lab-form-cases-four-sentence-template.pdf`，日期：2026-06-30。
- 发布资料：胰腺外科学：结构化中文学习版，类型：EPUB，文件数：1，路径：`files/surgery/2026-08-14-pancreatic-surgery-structured-chinese-ebook.epub`，日期：2026-08-14。
- 发布资料：胰腺外科学：结构化中文学习版，类型：PDF，文件数：1，路径：`files/surgery/2026-08-14-pancreatic-surgery-structured-chinese-ebook.pdf`，日期：2026-08-14。
- 发布资料：儿科学时间数据速查：生长发育、计划免疫与婴儿喂养，类型：PDF，文件数：1，路径：`files/pediatrics/2026-09-09-pediatrics-timeline-data-notes.pdf`，日期：2026-09-09。
- 发布资料：临床技能训练课程原文讲义（2026-2027学年第一学期），类型：PDF，文件数：1，路径：`files/surgery/2026-09-11-clinical-skills-course-textbook-extract.pdf`，日期：2026-09-11。
- 发布资料：儿科学腹泻病综合笔记，类型：PDF，文件数：1，路径：`files/pediatrics/2026-10-19-pediatrics-diarrhea-integrated-notes.pdf`，日期：2026-10-19。

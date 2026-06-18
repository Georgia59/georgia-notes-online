# data/files.json 字段规范

`data/files.json` 是下载站的文件索引。它是一个 JSON 数组，每一条记录代表一个可下载成品文件。

## 字段说明

| 字段 | 是否必填 | 说明 |
| --- | --- | --- |
| `note_id` | 推荐 | 同一份笔记多格式版本共用的稳定英文短名，例如 `acute-osteomyelitis-review`。网页会用它合并下载选项。 |
| `course` | 必填 | 页面显示的课程名称，例如 `医学影像学`。 |
| `category` | 必填 | 对应 `files/` 下的目录名，例如 `imaging`。 |
| `title` | 必填 | 卡片名称，也是用户看到的资料标题。 |
| `type` | 必填 | 文件类型或下载按钮名称，例如 `PDF`、`Word`、`PPT`、`HTML`。 |
| `date` | 必填 | 生成或发布日期，格式为 `YYYY-MM-DD`。 |
| `path` | 必填 | 仓库内相对路径，必须指向 `files/` 下的成品文件。 |
| `source` | 必填 | 公开可显示的来源类型，例如 `本地 PPT 整理`、`教材整理`、`错题整理`。不要写原始文件名或本地路径。 |
| `description` | 必填 | 一句话简介，适合手机端快速浏览。 |

## 多格式笔记

同一份笔记如果有 PDF、Word、HTML 等多个版本，应写成多条记录，但使用相同的 `note_id`。

```json
[
  {
    "note_id": "acute-osteomyelitis-review",
    "course": "医学影像学",
    "category": "imaging",
    "title": "急性骨髓炎影像学复习笔记",
    "type": "PDF",
    "date": "2026-06-18",
    "path": "files/imaging/2026-06-18-acute-osteomyelitis-review.pdf",
    "source": "本地 PPT 整理",
    "description": "围绕急性骨髓炎的影像表现、鉴别诊断和考试易错点整理。"
  },
  {
    "note_id": "acute-osteomyelitis-review",
    "course": "医学影像学",
    "category": "imaging",
    "title": "急性骨髓炎影像学复习笔记",
    "type": "Word",
    "date": "2026-06-18",
    "path": "files/imaging/2026-06-18-acute-osteomyelitis-review.docx",
    "source": "本地 PPT 整理",
    "description": "围绕急性骨髓炎的影像表现、鉴别诊断和考试易错点整理。"
  }
]
```

## 章节资料集

如果一类资料由多个章节文件组成，但不想在首页显示成很多小卡片，可以使用 `collection` 记录。首页会显示一张资料集卡片，卡片内展开章节下载列表。

```json
{
  "note_id": "surgery-general-textbook-notes",
  "kind": "collection",
  "course": "外科学",
  "category": "surgery",
  "title": "外科学总论课本整理",
  "type": "Collection",
  "date": "2026-06-18",
  "path": "files/surgery/2026-06-18-surgery-general-textbook-notes/",
  "source": "课本整理",
  "description": "按章节整理外科学总论重点内容，适合期末复习和考前查漏。",
  "items": [
    {
      "title": "绪论",
      "type": "PDF",
      "path": "files/surgery/2026-06-18-surgery-general-textbook-notes/01-introduction.pdf"
    },
    {
      "title": "外科无菌原则",
      "type": "PDF",
      "path": "files/surgery/2026-06-18-surgery-general-textbook-notes/02-asepsis.pdf"
    }
  ]
}
```

collection 的 `path` 指向资料集目录，`items[].path` 指向每个章节文件。公开页面不显示本地原始路径，也不显示原始资料文件名。

如果同一个章节同时有 PDF、Word、HTML 等多个格式，章节可以写成 `files` 数组。网页会把章节名放在左侧，把每个格式显示成独立按钮，用户必须点击具体格式按钮才能下载。

```json
{
  "title": "外科病人的代谢及营养治疗",
  "files": [
    {
      "type": "PDF",
      "path": "files/surgery/2026-06-18-surgery-general-textbook-notes/06-surgical-metabolism-nutrition.pdf"
    },
    {
      "type": "Word",
      "path": "files/surgery/2026-06-18-surgery-general-textbook-notes/06-surgical-metabolism-nutrition.docx"
    }
  ]
}
```

## 禁止写入

- 本地绝对路径，例如 Windows 或 macOS/Linux 的用户目录路径
- 原始文件名、内部资料编号、班级资料编号
- 患者、同学、老师或学校内部敏感信息
- 未确认公开风险的原始 PPT、PDF、Word

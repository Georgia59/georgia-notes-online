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
| `tags` | 必填 | 标签数组，例如 `["骨感染", "MRI", "考试复习"]`。 |
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
    "tags": ["骨感染", "MRI", "考试复习"],
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
    "tags": ["骨感染", "MRI", "考试复习"],
    "description": "围绕急性骨髓炎的影像表现、鉴别诊断和考试易错点整理。"
  }
]
```

## 禁止写入

- 本地绝对路径，例如 Windows 或 macOS/Linux 的用户目录路径
- 原始文件名、内部资料编号、班级资料编号
- 患者、同学、老师或学校内部敏感信息
- 未确认公开风险的原始 PPT、PDF、Word

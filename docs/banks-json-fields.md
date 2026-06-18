# data/banks.json 字段规范

`data/banks.json` 用于维护佛脚刷题入口。它只保存佛脚码、二维码和公开说明，不保存题目原文。

## 单个题库

```json
{
  "course": "实验诊断学",
  "title": "实验诊断学期末选择题题库",
  "code": "ABC123",
  "status": "已整理",
  "lastUpdated": "2026-06-18",
  "source": "课堂题库 + 错题整理",
  "note": "适合考前冲刺刷选择题。",
  "qr": "images/banks/lab-diagnostics.png"
}
```

`qr` 可为空字符串或省略；如果填写，图片必须放在 `images/banks/` 下。

## 分章节题库

如果一个主标题下面有多个章节佛脚码，使用 `kind: "collection"` 和 `items`。

```json
{
  "kind": "collection",
  "course": "外科学",
  "title": "外科学总论章节刷题",
  "status": "已整理",
  "lastUpdated": "2026-06-18",
  "source": "章节题库整理",
  "note": "按章节导入佛脚刷题，适合跟随复习进度使用。",
  "items": [
    {
      "title": "绪论",
      "code": "ABC123",
      "status": "已整理",
      "lastUpdated": "2026-06-18",
      "source": "章节题库整理",
      "note": "适合先刷基础概念。"
    },
    {
      "title": "外科无菌原则",
      "code": "DEF456"
    }
  ]
}
```

章节项可以继承主记录的 `status`、`lastUpdated`、`source` 和 `note`。如果章节有自己的二维码，可在章节项内填写 `qr`。

## 公开边界

- 不上传题目原文。
- 不上传老师内部题库文件、学校敏感资料或同学个人信息。
- 不写本地绝对路径。
- 不写原始文件名或内部资料编号。

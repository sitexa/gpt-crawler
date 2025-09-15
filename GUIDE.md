## 📋 gpt-crawler使用总结

### 1. 配置网页地址

编辑 [config.ts](file:///Users/xnpeng/aiproject/gpt-crawler/config.ts) 文件来配置爬取参数：

```typescript
import { Config } from "./src/config";

export const defaultConfig: Config = {
  url: "https://novel.tingroom.com/html/36/174.html", // 起始URL
  match: "https://novel.tingroom.com/html/36/**", // 匹配模式，爬取同系列页面
  selector: "body", // CSS选择器，选择要抓取的内容
  maxPagesToCrawl: 50, // 最大爬取页面数
  outputFileName: "novel_output.json", // 输出文件名
  maxTokens: 2000000, // 最大token数
  resourceExclusions: [
    // 排除的资源文件类型
    "png",
    "jpg",
    "jpeg",
    "gif",
    "svg",
    "css",
    "js",
    "ico",
    "woff",
    "woff2",
    "ttf",
    "eot",
    "otf",
    "mp4",
    "mp3",
    "webm",
    "ogg",
    "wav",
    "flac",
    "aac",
    "zip",
    "tar",
    "gz",
    "rar",
    "7z",
  ],
};
```

**关键配置说明：**

- `url`: 爬取的起始网页地址
- `match`: 匹配模式，决定哪些页面会被爬取
- `selector`: CSS选择器，指定要提取的内容部分
- `maxPagesToCrawl`: 控制爬取规模
- `outputFileName`: 结果保存的文件名

### 2. 运行爬虫程序

按照以下步骤执行：

```bash
# 1. 安装依赖（使用pnpm）
pnpm install playwright

# 2. 安装浏览器引擎
pnpm exec playwright install

# 3. 运行爬虫程序
node dist/src/main.js
```

**注意事项：**

- 必须先安装Playwright浏览器引擎
- 使用预编译的JavaScript文件运行
- 程序会显示爬取进度和状态

### 3. 保存结果

- 爬取结果自动保存为JSON格式文件
- 文件名在config.ts中的`outputFileName`字段指定
- 如果文件已存在，会生成带序号的新文件,如[novel_output-1.json]
- 输出文件包含爬取到的所有网页内容和元数据

### 4. 验证结果

爬取完成后可以检查：

- 输出文件大小（本次爬取结果为880KB）
- 文件修改时间确认是最新的
- 可以打开JSON文件查看具体内容

### 5. 处理结果

运行下面程序，将novel_output-1.json 清洗并分段保存为novel_paragraph.json

`python process_chapters.py`

### 6，分段保存为文本文件

运行下面程序，将hp_paragraph.json拆分成按段保存的txt文件。

`python hp_process_chapters.py` 

## 特别说明

- 爬取了两部小说，处理程序有区别，保存两套程序和输出结果。

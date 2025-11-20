# 通用文本处理程序

## 功能说明

这个程序可以处理任何包含"Chapter X"格式章节的文本文件，具有以下功能：

1. **文本清理**：删除中文和不可识别的非ASCII字符
2. **HTML实体解码**：自动解码HTML实体编码（如&uacute; → ú）
3. **无意义内容过滤**：删除长数字字符串、单词片段、标点符号碎片、字母组合、特殊符号、括号字符等
4. **章节切分**：按"Chapter X"或"chapter x"模式自动切分文档，统一输出为"Chapter X"格式
5. **格式化输出**：标题与段落、段落与段落间空2行
6. **自动命名**：根据原文件名自动生成输出文件名和文件夹

## 使用方法

### 基本用法
```bash
python text_processor.py <输入文件路径>
```

### 示例
```bash
# 处理JaneEyre.txt
python text_processor.py txt/JaneEyre.txt

# 处理PrideAndPrejudice.txt  
python text_processor.py txt/PrideAndPrejudice.txt

# 处理DavidCopperfield.txt（默认）
python text_processor.py
```

## 输出格式

- **文件夹**：以原文件名命名（不含扩展名）
- **文件命名**：`{书名}-ch-XX.txt`
- **格式**：标题后空2行，段落间空2行

## 示例输出

处理`txt/JaneEyre.txt`后：
- 创建文件夹：`JaneEyre/`
- 生成文件：`JaneEyre-ch-01.txt`, `JaneEyre-ch-02.txt`, ...

处理`txt/PrideAndPrejudice.txt`后：
- 创建文件夹：`PrideAndPrejudice/`
- 生成文件：`PrideAndPrejudice-ch-01.txt`, `PrideAndPrejudice-ch-02.txt`, ...

## 支持的文件格式

- 任何包含"Chapter X"格式章节的文本文件
- 支持中英文混合文本（中文会被自动清理）
- 支持UTF-8编码

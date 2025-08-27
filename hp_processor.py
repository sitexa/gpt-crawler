import json
import re

def extract_english_content(html_content):
    """根据用户提供的章节分界模式提取完整英文章节内容"""
    # 移除HTML标签
    clean_text = re.sub(r'<[^>]+>', '', html_content)
    
    # 1. 首先尝试查找章节标题后的英文内容
    # 章节标题模式："Chapter XX Title"
    chapter_title_pattern = r'Chapter \d+[^\n]*?\n'
    title_match = re.search(chapter_title_pattern, clean_text)
    
    if title_match:
        # 从章节标题后开始查找英文内容
        after_title = clean_text[title_match.end():]
        
        # 查找英文段落开始模式 - 大写字母开头的句子
        english_start_patterns = [
            r'([A-Z][A-Za-z\s,\'"\?\!\-\.]+)',  # 普通英文句子
            r'("[A-Z][^"]*")',  # 引号内的对话
            r'([A-Z]+[\s\!]+)',  # 全大写感叹
        ]
        
        start_pos = None
        for pattern in english_start_patterns:
            start_match = re.search(pattern, after_title)
            if start_match:
                start_pos = title_match.end() + start_match.start(1)
                break
    
    if not title_match or start_pos is None:
        # 2. 备用方案：查找任何英文内容开始
        fallback_patterns = [
            r'([A-Z][A-Za-z]+[^\n]*)',  # 任何大写字母开头的行
            r'("[A-Z][^"]*")',  # 对话
            r'([A-Z]+[\s\!]+)',  # 感叹
        ]
        
        start_pos = None
        for pattern in fallback_patterns:
            start_match = re.search(pattern, clean_text)
            if start_match:
                start_pos = start_match.start(1)
                break
        
        if start_pos is None:
            return ""
    
    # 3. 查找英文内容结束位置
    text_from_start = clean_text[start_pos:]
    
    # 寻找中文开始的位置作为英文结束
    chinese_patterns = [
        r'\n\s*[\u4e00-\u9fff]+',  # 换行后的中文
        r'\n\n\s*[\u4e00-\u9fff]+',  # 双换行后的中文
        r'[\u4e00-\u9fff]{3,}',  # 连续3个以上中文字符
    ]
    
    end_pos = len(text_from_start)  # 默认到文本末尾
    for pattern in chinese_patterns:
        chinese_match = re.search(pattern, text_from_start)
        if chinese_match:
            end_pos = chinese_match.start()
            break
    
    english_content = text_from_start[:end_pos]
    
    # 4. 清理英文内容
    if english_content:
        # 移除HTML实体
        english_content = re.sub(r'&[a-zA-Z]+;', '', english_content)
        
        # 移除单词后的数字注释标记（如 likeness3, unreasonably4）
        english_content = re.sub(r'([a-zA-Z])\d+', r'\1', english_content)
        
        # 保留原文分段，只清理多余的空格但保留换行符
        # 将多个连续空格替换为单个空格，但保留换行符
        english_content = re.sub(r'[ \t]+', ' ', english_content)  # 只压缩空格和制表符
        # 清理多个连续换行符为双换行符（段落分隔）
        english_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', english_content)
        # 移除行首行尾的空格但保留换行符
        lines = english_content.split('\n')
        lines = [line.strip() for line in lines]
        english_content = '\n'.join(lines).strip()
        
        # 移除可能的页面导航文字
        unwanted_patterns = [
            r'首页.*?经典英文小说',
            r'版权.*?QQ',
            r'点击.*?快捷键',
            r'上一篇.*?下一篇',
            r'下一篇:.*?\(快捷键:.*?\)',
            r'上一篇:.*?\(快捷键:.*?\)',
            r'Chapter \d+.*?下一篇:.*?\n',
            r'Chapter \d+.*?上一篇:.*?\n',
            r'返回目录',
            r'欢迎访问.*?只需30秒',
            r'\d+\s+\w+\s+.*?参考例句',
            r'点击收听单词发音',
            r'在线英语听力室.*?注册帐号',
            r'设为首页.*?关键词列表',
            r'©英文小说网.*?鲁ICP备.*?号'
        ]
        
        for pattern in unwanted_patterns:
            english_content = re.sub(pattern, '', english_content, flags=re.DOTALL)
        
        # 最后再次清理多余的连续空格，但保留换行符
        english_content = re.sub(r'[ \t]+', ' ', english_content)  # 只压缩空格和制表符
        english_content = english_content.strip()
    
    return english_content
    
def split_into_paragraphs(content):
    """将章节内容按段落分割并组织成嵌套结构"""
    if not content:
        return {"paragraphs": {}}
    
    # 在段落分割之前，清理章节导航信息和章节标题
    import re
    
    # 清理导航信息
    navigation_patterns = [
        r'Chapter \d+[^\n]*?下一篇:[^\n]*?\n',
        r'Chapter \d+[^\n]*?上一篇:[^\n]*?\n',
        r'下一篇:\s*Chapter[^\n]*?\([^\)]*?\)\s*',
        r'上一篇:\s*Chapter[^\n]*?\([^\)]*?\)\s*',
        r'Chapter \d+[^\n]*?\(快捷键:[^\)]*?\)',
        r'^[^\n]*?快捷键:[^\n]*?\n'
    ]
    
    for pattern in navigation_patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # 清理章节标题行（类似"Chapter 1 The Boy Who Lived \nChapter 2 The Vanishing Glass"）
    # 移除开头的章节标题行
    chapter_title_patterns = [
        r'^Chapter \d+[^\n]*\nChapter \d+[^\n]*\n',  # 连续两行章节标题
        r'^Chapter \d+[^\n]*\n',  # 单行章节标题（在开头）
        r'^Chapter \d+[^\n]*$',  # 单行章节标题（无换行）
    ]
    
    for pattern in chapter_title_patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # 额外清理：移除开头可能残留的章节标题片段
    content = re.sub(r'^[^\n]*Chapter \d+[^\n]*\n', '', content, flags=re.MULTILINE)
    
    # 清理可能的空行
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = content.strip()
    
    # 首先按双换行符分割
    paragraphs = content.split('\n\n')
    
    # 如果只有一个段落，尝试按句号后跟换行符分割
    if len(paragraphs) == 1 and len(paragraphs[0]) > 1000:  # 太长的单个段落
        # 按句号+换行符分割段落
        text = paragraphs[0]
        # 正则：句号后面跟着换行符和大写字母或引号
        import re
        split_pattern = r'(?<=[.!?])\s*\n(?=[A-Z"]|\u201c)'
        split_parts = re.split(split_pattern, text)
        
        if len(split_parts) > 1:
            paragraphs = []
            current_paragraph = ""
            for part in split_parts:
                part = part.strip()
                if part:
                    if current_paragraph and len(current_paragraph + " " + part) > 800:  # 段落不要太长
                        paragraphs.append(current_paragraph)
                        current_paragraph = part
                    elif current_paragraph:
                        current_paragraph += "\n" + part
                    else:
                        current_paragraph = part
            
            if current_paragraph:
                paragraphs.append(current_paragraph)
    
    # 过滤掉空段落并去除前后空格
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    # 如果仍然只有一个很长的段落，按固定字数分割
    if len(paragraphs) == 1 and len(paragraphs[0]) > 1500:
        text = paragraphs[0]
        # 按约1000字符分割，在句号后分割
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        paragraphs = []
        current_paragraph = ""
        
        for sentence in sentences:
            if current_paragraph and len(current_paragraph + " " + sentence) > 1000:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = sentence
            elif current_paragraph:
                current_paragraph += " " + sentence
            else:
                current_paragraph = sentence
        
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
    
    # 构建段落字典
    paragraph_dict = {}
    for i, paragraph in enumerate(paragraphs, 1):
        paragraph_key = f"paragraph {i}"
        paragraph_dict[paragraph_key] = paragraph
    
    return {"paragraphs": paragraph_dict}

# 读取原始文件
with open('hp_output-1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

processed_chapters = []

for item in data:
    # 提取章节号
    title = item['title']
    chapter_match = re.search(r'Chapter \d+', title)
    if not chapter_match:
        continue
    
    chapter = chapter_match.group()
    html_content = item['html']
    
    # 使用新的提取方法
    english_content = extract_english_content(html_content)
    
    # 检查是否有足够的内容
    if english_content and len(english_content) > 50:  # 降低到至少50字符
        # 从title中提取小说名称
        # 标题格式类似："Chapter 17 The Man With Two Faces_Harry Potter and the Sorcerer's Stone哈利波特与魔法石_儿童英文小说"
        title_parts = title.split('_')
        if len(title_parts) >= 2:
            # 提取小说标题部分
            novel_title_part = title_parts[1]  # "Harry Potter and the Sorcerer's Stone哈利波特与魔法石"
            
            # 寻找中英文分界点，通常是中文字符开始的地方
            import re
            chinese_match = re.search(r'[\u4e00-\u9fff]+', novel_title_part)
            if chinese_match:
                # 找到中文开始位置
                chinese_start = chinese_match.start()
                english_title = novel_title_part[:chinese_start].strip()
                chinese_title = novel_title_part[chinese_start:].strip()
                
                if english_title and chinese_title:
                    display_title = f"{chinese_title}_{english_title}"
                    novel_name = english_title
                else:
                    display_title = novel_title_part
                    novel_name = novel_title_part
            else:
                # 没有中文，全部是英文
                display_title = novel_title_part
                novel_name = novel_title_part
        else:
            # 如果分割失败，使用原始标题
            display_title = title
            novel_name = "Unknown"
        
        # 将内容按段落组织
        content_structure = split_into_paragraphs(english_content)
        
        processed_chapter = {
            "title": display_title,
            "novel": novel_name, 
            "chapter": chapter,
            "content": content_structure
        }
        processed_chapters.append(processed_chapter)

# 按章节号排序
def get_chapter_number(chapter):
    match = re.search(r'\d+', chapter['chapter'])
    return int(match.group()) if match else 0

processed_chapters.sort(key=get_chapter_number)

# 保存处理后的数据
with open('hp_parapgraph.json', 'w', encoding='utf-8') as f:
    json.dump(processed_chapters, f, indent=2, ensure_ascii=False)

print(f'处理完成，共提取 {len(processed_chapters)} 个章节')
for chapter in processed_chapters[:3]:  # 显示前3个章节的信息
    paragraphs = chapter['content']['paragraphs']
    total_length = sum(len(p) for p in paragraphs.values())
    print(f"{chapter['chapter']}: {len(paragraphs)} 个段落，共 {total_length} 个字符")
    if paragraphs:
        first_paragraph = list(paragraphs.values())[0]
        print(f"第一段: {first_paragraph[:100]}...")
    print("---")
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
    """将章节内容按段落分割并组织成嵌套结构，确保每个段落字符数小于4096"""
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
    
    # 清理章节标题行
    chapter_title_patterns = [
        r'^Chapter \d+[^\n]*\nChapter \d+[^\n]*\n',
        r'^Chapter \d+[^\n]*\n',
        r'^Chapter \d+[^\n]*$',
    ]
    
    for pattern in chapter_title_patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE)
    
    # 额外清理：移除开头可能残留的章节标题片段
    content = re.sub(r'^[^\n]*Chapter \d+[^\n]*\n', '', content, flags=re.MULTILINE)
    
    # 清理可能的空行
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = content.strip()
    
    # 智能段落分割，确保字符数限制
    MAX_PARAGRAPH_LENGTH = 2000
    MIN_PARAGRAPH_LENGTH = 1000  # 避免段落过短
    
    # 首先按双换行符分割成初始段落
    initial_paragraphs = content.split('\n\n')
    initial_paragraphs = [p.strip() for p in initial_paragraphs if p.strip()]
    
    # 如果没有双换行符分割，尝试其他分割方式
    if len(initial_paragraphs) == 1:
        # 按句号后跟换行符分割
        split_pattern = r'(?<=[.!?])\s*\n(?=[A-Z"]|\u201c)'
        split_parts = re.split(split_pattern, content)
        if len(split_parts) > 1:
            initial_paragraphs = [p.strip() for p in split_parts if p.strip()]
    
    # 智能合并和分割段落
    final_paragraphs = []
    current_paragraph = ""
    
    for paragraph in initial_paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # 检查是否为对话段落（包含引号）
        is_dialogue = bool(re.search(r'["\u201c\u201d]', paragraph))
        
        # 如果当前段落为空，直接添加
        if not current_paragraph:
            current_paragraph = paragraph
        else:
            # 计算合并后的长度
            combined_length = len(current_paragraph) + len(paragraph) + 2  # +2 for \n\n
            
            # 决定是否合并
            should_merge = False
            
            if combined_length <= MAX_PARAGRAPH_LENGTH:
                # 如果合并后不超过限制
                current_is_dialogue = bool(re.search(r'["\u201c\u201d]', current_paragraph))
                
                # 对话段落合并策略：
                # 1. 两个都是对话且当前段落较短时合并
                # 2. 两个都是非对话段落时合并
                # 3. 当前段落过短时强制合并
                if (current_is_dialogue and is_dialogue and len(current_paragraph) < MIN_PARAGRAPH_LENGTH * 2) or \
                   (not current_is_dialogue and not is_dialogue) or \
                   len(current_paragraph) < MIN_PARAGRAPH_LENGTH:
                    should_merge = True
            
            if should_merge:
                current_paragraph += "\n\n" + paragraph
            else:
                # 不合并，保存当前段落并开始新段落
                if len(current_paragraph) > MAX_PARAGRAPH_LENGTH:
                    # 当前段落过长，需要分割
                    split_paragraphs = split_long_paragraph(current_paragraph, MAX_PARAGRAPH_LENGTH)
                    final_paragraphs.extend(split_paragraphs)
                else:
                    final_paragraphs.append(current_paragraph)
                current_paragraph = paragraph
    
    # 处理最后一个段落
    if current_paragraph:
        if len(current_paragraph) > MAX_PARAGRAPH_LENGTH:
            split_paragraphs = split_long_paragraph(current_paragraph, MAX_PARAGRAPH_LENGTH)
            final_paragraphs.extend(split_paragraphs)
        else:
            final_paragraphs.append(current_paragraph)
    
    # 构建段落字典
    paragraph_dict = {}
    for i, paragraph in enumerate(final_paragraphs, 1):
        paragraph_key = f"paragraph {i}"
        paragraph_dict[paragraph_key] = paragraph.strip()
    
    return {"paragraphs": paragraph_dict}

def split_long_paragraph(paragraph, max_length):
    """将过长的段落分割成多个较短的段落"""
    import re
    
    if len(paragraph) <= max_length:
        return [paragraph]
    
    # 按句子分割
    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    
    result_paragraphs = []
    current_part = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 如果单个句子就超过限制，强制分割
        if len(sentence) > max_length:
            if current_part:
                result_paragraphs.append(current_part.strip())
                current_part = ""
            
            # 按逗号或分号分割长句子
            parts = re.split(r'(?<=[,;])\s+', sentence)
            temp_part = ""
            for part in parts:
                if len(temp_part + part) > max_length:
                    if temp_part:
                        result_paragraphs.append(temp_part.strip())
                    temp_part = part
                else:
                    temp_part += (" " if temp_part else "") + part
            if temp_part:
                current_part = temp_part
        else:
            # 检查添加这个句子是否会超过限制
            test_length = len(current_part) + len(sentence) + (1 if current_part else 0)
            
            if test_length > max_length and current_part:
                # 超过限制，保存当前部分并开始新部分
                result_paragraphs.append(current_part.strip())
                current_part = sentence
            else:
                # 不超过限制，添加到当前部分
                current_part += (" " if current_part else "") + sentence
    
    # 添加最后一部分
    if current_part:
        result_paragraphs.append(current_part.strip())
    
    return result_paragraphs

# 读取原始文件
with open('hp_output.json', 'r', encoding='utf-8') as f:
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
import json
import re

def extract_english_content(html_content):
    """根据用户提供的章节分界模式提取完整英文章节内容"""
    # 移除HTML标签
    clean_text = re.sub(r'<[^>]+>', '', html_content)
    
    # 查找章节开头模式：中文后面跟两个换行符再跟英文
    # 章节开头模式："原版名著免费领。\n\n MY father's family name being Pirrip,"
    chapter_start_pattern = r'[\u4e00-\u9fff]+.*?\n\n\s*([A-Z][A-Za-z\s]+)'
    
    # 查找章节结尾模式：英文后面跟4个换行符再跟中文  
    # 章节结尾模式："But, now I was frightened again, and ran home without stopping.\n\n \n\n我父亲的姓是皮利普，"
    chapter_end_pattern = r'([A-Za-z][^\n]*?)\n\n\s*\n\n[\u4e00-\u9fff]+'
    
    # 寻找章节开始位置
    start_match = re.search(chapter_start_pattern, clean_text)
    if start_match:
        # 使用匹配组1的开始位置，即英文部分的开始
        start_pos = start_match.start(1)
    else:
        # 如果没找到标准模式，尝试寻找"MY father's family name being Pirrip"等开头
        fallback_pattern = r'(MY father\'s family name being Pirrip|IT [A-Z]|I [A-Z]|THE [A-Z]|AFTER [A-Z])'
        start_match = re.search(fallback_pattern, clean_text)
        if not start_match:
            return ""
        start_pos = start_match.start()
    
    # 寻找章节结束位置
    # 从开始位置后查找结尾模式
    text_from_start = clean_text[start_pos:]
    end_match = re.search(chapter_end_pattern, text_from_start)
    
    if end_match:
        # 找到结尾，提取到结尾位置
        end_pos = start_pos + end_match.end(1)
        english_content = clean_text[start_pos:end_pos]
    else:
        # 没找到标准结尾，寻找中文开始的位置作为结尾
        chinese_pattern = r'\n\s*[\u4e00-\u9fff]+'
        chinese_match = re.search(chinese_pattern, text_from_start)
        if chinese_match:
            end_pos = start_pos + chinese_match.start()
            english_content = clean_text[start_pos:end_pos]
        else:
            # 如果都没找到，取剩余所有内容
            english_content = text_from_start
    
    # 清理英文内容
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
            r'返回目录',
            r'欢迎访问.*?只需30秒',
            r'\d+\s+\w+\s+.*?参考例句',
            r'点击收听单词发音'
        ]
        
        for pattern in unwanted_patterns:
            english_content = re.sub(pattern, '', english_content)
        
        # 最后再次清理多余的连续空格，但保留换行符
        english_content = re.sub(r'[ \t]+', ' ', english_content)  # 只压缩空格和制表符
        english_content = english_content.strip()
    
    return english_content

def split_long_paragraph(paragraph, max_length=2000, min_length=1000):
    """
    将长段落拆分为符合长度要求的短段落
    
    Args:
        paragraph: 原始段落文本
        max_length: 最大段落长度
        min_length: 最小段落长度
    
    Returns:
        list: 拆分后的段落列表
    """
    if len(paragraph) <= max_length:
        return [paragraph]
    
    # 按句子分割（以句号、问号、感叹号结尾）
    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    
    result_paragraphs = []
    current_paragraph = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 如果当前段落加上新句子超过最大长度，且当前段落不为空
        if current_paragraph and len(current_paragraph + " " + sentence) > max_length:
            # 如果当前段落长度符合要求，保存它
            if len(current_paragraph) >= min_length:
                result_paragraphs.append(current_paragraph)
                current_paragraph = sentence
            else:
                # 当前段落太短，强制添加句子
                current_paragraph += " " + sentence
        else:
            # 添加句子到当前段落
            if current_paragraph:
                current_paragraph += " " + sentence
            else:
                current_paragraph = sentence
    
    # 添加最后一个段落
    if current_paragraph:
        result_paragraphs.append(current_paragraph)
    
    return result_paragraphs


def split_into_paragraphs(content):
    """将章节内容按段落分割并组织成嵌套结构，控制段落长度"""
    if not content:
        return {"paragraphs": {}}
    
    # 按双换行符分割段落
    paragraphs = content.split('\n\n')
    
    # 过滤掉空段落并去除前后空格
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    # 段落长度控制参数
    MAX_PARAGRAPH_LENGTH = 2000
    MIN_PARAGRAPH_LENGTH = 1000
    
    # 构建段落字典
    paragraph_dict = {}
    paragraph_counter = 1
    
    for paragraph in paragraphs:
        # 拆分长段落
        split_paragraphs = split_long_paragraph(paragraph, MAX_PARAGRAPH_LENGTH, MIN_PARAGRAPH_LENGTH)
        
        for split_para in split_paragraphs:
            paragraph_key = f"paragraph {paragraph_counter}"
            paragraph_dict[paragraph_key] = split_para
            paragraph_counter += 1
    
    return {"paragraphs": paragraph_dict}

# 读取原始文件
with open('ge_output.json', 'r', encoding='utf-8') as f:
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
    if english_content and len(english_content) > 100:  # 至少100字符
        # 将内容按段落组织
        content_structure = split_into_paragraphs(english_content)
        
        processed_chapter = {
            "title": "Great Expectations远大前程",
            "novel": "Great Expectations", 
            "chapter": chapter,
            "content": content_structure
        }
        processed_chapters.append(processed_chapter)

# 按章节号排序
processed_chapters.sort(key=lambda x: int(re.search(r'\d+', x['chapter']).group()))

# 保存处理后的数据
with open('ge_paragraphs.json', 'w', encoding='utf-8') as f:
    json.dump(processed_chapters, f, indent=2, ensure_ascii=False)

print(f'处理完成，共提取 {len(processed_chapters)} 个章节')
print("段落长度控制统计：")
for chapter in processed_chapters[:3]:  # 显示前3个章节的信息
    paragraphs = chapter['content']['paragraphs']
    total_length = sum(len(p) for p in paragraphs.values())
    paragraph_lengths = [len(p) for p in paragraphs.values()]
    min_len = min(paragraph_lengths) if paragraph_lengths else 0
    max_len = max(paragraph_lengths) if paragraph_lengths else 0
    avg_len = sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0
    
    print(f"{chapter['chapter']}: {len(paragraphs)} 个段落，共 {total_length} 个字符")
    print(f"  段落长度范围: {min_len}-{max_len} 字符，平均: {avg_len:.0f} 字符")
    if paragraphs:
        first_paragraph = list(paragraphs.values())[0]
        print(f"  第一段: {first_paragraph[:100]}...")
    print("---")
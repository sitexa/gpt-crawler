#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1984小说专用文本处理程序
功能：
1. 删除中文和不可识别的非ASCII字符
2. 按"Part X Chapter Y"格式切分文档，输出为"Chapter Y"格式
3. 保存为1984-ch-XX.txt格式，放在1984/文件夹中
4. 格式化输出：标题与段落、段落与段落间空2行
"""

import re
import os
import unicodedata
import sys
import html

# 常量定义
# 文本清理相关常量
MIN_ASCII_PRINTABLE = 32          # ASCII可打印字符最小值
MAX_ASCII_PRINTABLE = 126         # ASCII可打印字符最大值
MIN_LATIN_EXTENDED = 128          # 拉丁字母扩展最小值
MAX_LATIN_EXTENDED = 255          # 拉丁字母扩展最大值

# 段落过滤相关常量
MIN_VALID_LINE_LENGTH = 15        # 有效行的最小长度
MAX_SHORT_LINE_LENGTH = 10        # 短行的最大长度
MAX_NUMERIC_ID_LENGTH = 8         # 数字ID的最大长度
MAX_FRAGMENT_LENGTH = 20          # 碎片的最大长度
MAX_WORD_FRAGMENT_LENGTH = 35     # 单词片段的最大长度
MAX_NO_SPACE_LENGTH = 40          # 无空格行的最大长度

# 段落拆分相关常量
DEFAULT_MAX_WORDS = 160           # 默认每段最大词数
PARAGRAPH_SPACING = 2             # 段落间空行数

# 文件名格式相关常量
CHAPTER_NUMBER_PADDING = 2        # 章节编号填充位数
OUTPUT_DIR_NAME = 'novels'        # 输出目录名称

def clean_text(text):
    """
    清理文本，删除中文和不可识别的非ASCII字符
    保留基本的ASCII字符和常见的标点符号
    """
    # 首先解码HTML实体编码
    text = html.unescape(text)
    
    # 保留的字符：字母、数字、基本标点符号、空格、换行符
    allowed_chars = set(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        '0123456789'
        ' .,!?;:"\'()-[]{}@#$%^&*+=<>/\\|`~'
        '\n\r\t'
    )
    
    cleaned_text = ''
    for char in text:
        # 检查字符是否在允许的字符集中
        if char in allowed_chars:
            cleaned_text += char
        # 保留ASCII可打印字符
        elif ord(char) >= MIN_ASCII_PRINTABLE and ord(char) <= MAX_ASCII_PRINTABLE:
            cleaned_text += char
        # 保留换行符和制表符
        elif char in '\n\r\t':
            cleaned_text += char
        # 保留重音字符（拉丁字母扩展）
        elif ord(char) >= MIN_LATIN_EXTENDED and ord(char) <= MAX_LATIN_EXTENDED:
            cleaned_text += char
        # 其他字符（包括中文）都删除
    
    # 清理多余的点号和空行
    cleaned_text = clean_redundant_punctuation(cleaned_text)
    
    return cleaned_text

def clean_redundant_punctuation(text):
    """
    清理多余的点号、空行和单词片段
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 去除行首行尾空白
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
            
        # 跳过只包含点号的行
        if line.replace('.', '').replace(' ', '') == '':
            continue
            
        # 跳过只包含单个点号的行
        if line == '.':
            continue
            
        # 跳过只包含长数字的行（超过指定位数的连续数字，可能是时间戳或ID）
        if line.isdigit() and len(line) > MAX_NUMERIC_ID_LENGTH:
            continue
            
        # 跳过只包含标点符号和数字的短行（如 ?(1861111)）
        if len(line) < MIN_VALID_LINE_LENGTH and any(c in line for c in '?()') and not any(c.isalpha() for c in line):
            continue
            
        # 跳过只包含标点符号和单个字母的短行（如 ?I, !I?）
        if len(line) < MAX_SHORT_LINE_LENGTH and any(c in line for c in '?!-') and sum(c.isalpha() for c in line) <= 1:
            continue
            
        # 跳过只包含字母和问号的短行（如 fH?, ?jj??, nq?, ff?）
        if len(line) < MAX_SHORT_LINE_LENGTH and '?' in line and all(c.isalpha() or c == '?' for c in line):
            continue
            
        # 跳过只包含单个字母的行（如单独的 I）
        if len(line) == 1 and line.isalpha():
            continue
            
        # 跳过只包含2-3个字母的短行（如 OK, JJ, IJ）
        if 2 <= len(line) <= 3 and line.isalpha():
            continue
            
        # 跳过只包含字母和特殊符号的短行（如 NRA*）
        if len(line) < MAX_SHORT_LINE_LENGTH and any(c in line for c in '*@#$%^&+=') and line.replace('*', '').replace('@', '').replace('#', '').replace('$', '').replace('%', '').replace('^', '').replace('&', '').replace('+', '').replace('=', '').isalpha():
            continue
            
        # 跳过只包含字母和括号的短行（如 T()）
        if len(line) < MAX_SHORT_LINE_LENGTH and any(c in line for c in '()') and line.replace('(', '').replace(')', '').isalpha():
            continue
            
        # 跳过以点号开头的单词片段（通常是清理过程中产生的碎片）
        if line.startswith('.') and len(line) < MAX_FRAGMENT_LENGTH:
            continue
            
        # 跳过只包含标点符号和少量字母的行（可能是清理碎片）
        if len(line) < MAX_SHORT_LINE_LENGTH and not any(c.isalpha() for c in line):
            continue
            
        # 跳过看起来像被分割的单词片段（包含特殊字符且长度较短）
        if len(line) < MAX_WORD_FRAGMENT_LENGTH and any(c in line for c in "'`") and not line.endswith(('.', '!', '?')):
            continue
            
        # 跳过只包含小写字母且没有空格的行（可能是单词片段）
        if len(line) < MAX_FRAGMENT_LENGTH and line.islower() and ' ' not in line and not line.endswith(('.', '!', '?')):
            continue
            
        # 跳过看起来像被错误连接的单词片段（包含大小写混合且没有空格）
        if len(line) < MAX_NO_SPACE_LENGTH and not ' ' in line and not line.endswith(('.', '!', '?')) and any(c.isupper() for c in line) and any(c.islower() for c in line):
            continue
            
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def split_into_chapters(text):
    """
    按"Part X Chapter Y"格式切分文档
    返回章节列表，每个章节包含标题和内容
    """
    # 使用正则表达式匹配章节标题（支持"Part X Chapter Y"格式）
    chapter_pattern = r'^Part\s+\d+\s+Chapter\s+\d+'
    
    # 按行分割文本
    lines = text.split('\n')
    
    chapters = []
    current_chapter = None
    current_content = []
    
    for line in lines:
        # 检查是否是章节标题
        if re.match(chapter_pattern, line.strip()):
            # 如果之前有章节，先保存
            if current_chapter is not None:
                chapters.append({
                    'title': current_chapter,
                    'content': '\n'.join(current_content).strip()
                })
            
            # 开始新章节，提取章节号
            line_clean = line.strip()
            # 从"Part X Chapter Y"中提取Chapter Y
            chapter_match = re.search(r'Chapter\s+(\d+)', line_clean)
            if chapter_match:
                chapter_num = chapter_match.group(1)
                current_chapter = f"Chapter {chapter_num}"
            else:
                current_chapter = line_clean
            current_content = []
        else:
            # 添加到当前章节内容
            if current_chapter is not None:
                current_content.append(line)
    
    # 保存最后一个章节
    if current_chapter is not None:
        chapters.append({
            'title': current_chapter,
            'content': '\n'.join(current_content).strip()
        })
    
    return chapters

def split_long_paragraph(paragraph, max_words=DEFAULT_MAX_WORDS):
    """
    将过长的段落按句子拆分，确保每个子段落不超过指定词数
    """
    # 如果段落不够长，直接返回
    word_count = len(paragraph.split())
    if word_count <= max_words:
        return [paragraph]
    
    # 按句子分割（按句号、问号、感叹号分割）
    sentence_endings = ['.', '!', '?']
    sentences = []
    current_sentence = ""
    
    i = 0
    while i < len(paragraph):
        char = paragraph[i]
        current_sentence += char
        
        if char in sentence_endings:
            # 检查是否是真正的句子结尾（后面跟空格、换行或文本结束）
            if i == len(paragraph) - 1 or paragraph[i + 1].isspace():
                sentences.append(current_sentence.strip())
                current_sentence = ""
        i += 1
    
    # 如果还有剩余的句子（没有以句号等结尾）
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    # 如果没有找到句子分割点，按逗号和分号分割
    if len(sentences) <= 1:
        sentences = []
        current_sentence = ""
        for char in paragraph:
            current_sentence += char
            if char in [',', ';']:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
    
    # 将句子组合成合适长度的段落
    sub_paragraphs = []
    current_sub_paragraph = ""
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        # 如果当前句子加上已有内容超过限制，则开始新段落
        if current_word_count + sentence_words > max_words and current_sub_paragraph:
            sub_paragraphs.append(current_sub_paragraph.strip())
            current_sub_paragraph = sentence
            current_word_count = sentence_words
        else:
            # 添加到当前段落
            if current_sub_paragraph:
                current_sub_paragraph += " " + sentence
            else:
                current_sub_paragraph = sentence
            current_word_count += sentence_words
    
    # 添加最后一个段落
    if current_sub_paragraph.strip():
        sub_paragraphs.append(current_sub_paragraph.strip())
    
    # 如果拆分后还是没有结果，按词数强制拆分
    if not sub_paragraphs:
        words = paragraph.split()
        for i in range(0, len(words), max_words):
            sub_paragraph = ' '.join(words[i:i + max_words])
            sub_paragraphs.append(sub_paragraph)
    
    return sub_paragraphs

def format_chapter_content(title, content):
    """
    格式化章节内容
    标题与段落、段落与段落间空2行
    对过长段落进行拆分，确保每个段落不超过160个词
    """
    # 按行分割内容，每行作为一个段落
    lines = content.split('\n')
    paragraphs = []
    
    for line in lines:
        line = line.strip()
        if line:  # 非空行作为一个段落
            # 对长段落进行拆分
            sub_paragraphs = split_long_paragraph(line, max_words=DEFAULT_MAX_WORDS)
            paragraphs.extend(sub_paragraphs)
    
    # 格式化输出
    formatted_content = title + '\n' * (PARAGRAPH_SPACING + 1)  # 标题后空行
    
    for i, paragraph in enumerate(paragraphs):
        formatted_content += paragraph
        if i < len(paragraphs) - 1:  # 不是最后一个段落
            formatted_content += '\n' * (PARAGRAPH_SPACING + 1)  # 段落间空行
    
    return formatted_content

def process_1984_file(input_file='txt/1984.txt'):
    """
    处理1984文本文件
    """
    if not os.path.exists(input_file):
        print(f"错误：文件 {input_file} 不存在")
        return
    
    # 设置输出目录
    book_name = '1984'
    output_dir = os.path.join(OUTPUT_DIR_NAME, book_name)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"正在读取文件: {input_file}")
    
    # 读取原始文件
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        original_text = f.read()
    
    print("正在清理文本...")
    # 清理文本
    cleaned_text = clean_text(original_text)
    
    print("正在切分章节...")
    # 切分章节
    chapters = split_into_chapters(cleaned_text)
    
    print(f"找到 {len(chapters)} 个章节")
    
    # 处理每个章节
    for i, chapter in enumerate(chapters, 1):
        print(f"正在处理第 {i} 章: {chapter['title']}")
        
        # 格式化内容
        formatted_content = format_chapter_content(
            chapter['title'], 
            chapter['content']
        )
        
        # 保存到文件
        output_file = os.path.join(output_dir, f'{book_name}-ch-{i:0{CHAPTER_NUMBER_PADDING}d}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
    
    print(f"处理完成！所有章节已保存到 {output_dir}/ 目录中")
    print(f"共生成 {len(chapters)} 个文件")

def main():
    """
    主函数，支持命令行参数
    """
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，使用指定的文件
        input_file = sys.argv[1]
    else:
        # 默认处理1984
        input_file = 'txt/1984.txt'
    
    process_1984_file(input_file)

if __name__ == '__main__':
    main()
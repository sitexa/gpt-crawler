#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文本处理程序
功能：
1. 删除中文和不可识别的非ASCII字符
2. 按"Chapter X"切分文档
3. 保存为{书名}-ch-XX.txt格式，放在{书名}/文件夹中
4. 格式化输出：标题与段落、段落与段落间空2行
"""

import re
import os
import unicodedata
import sys

def clean_text(text):
    """
    清理文本，删除中文和不可识别的非ASCII字符
    保留基本的ASCII字符和常见的标点符号
    """
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
        elif ord(char) >= 32 and ord(char) <= 126:
            cleaned_text += char
        # 保留换行符和制表符
        elif char in '\n\r\t':
            cleaned_text += char
        # 其他字符（包括中文）都删除
    
    return cleaned_text

def split_into_chapters(text):
    """
    按"Chapter X"切分文档
    返回章节列表，每个章节包含标题和内容
    """
    # 使用正则表达式匹配章节标题
    chapter_pattern = r'^Chapter \d+'
    
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
            
            # 开始新章节
            current_chapter = line.strip()
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

def format_chapter_content(title, content):
    """
    格式化章节内容
    标题与段落、段落与段落间空2行
    """
    # 按行分割内容，每行作为一个段落
    lines = content.split('\n')
    paragraphs = []
    
    for line in lines:
        line = line.strip()
        if line:  # 非空行作为一个段落
            paragraphs.append(line)
    
    # 格式化输出
    formatted_content = title + '\n\n'  # 标题后空2行
    
    for i, paragraph in enumerate(paragraphs):
        formatted_content += paragraph
        if i < len(paragraphs) - 1:  # 不是最后一个段落
            formatted_content += '\n\n'  # 段落间空2行
    
    return formatted_content

def get_book_name_from_file(input_file):
    """
    从文件路径中提取书名
    例如：txt/JaneEyre.txt -> JaneEyre
    """
    # 获取文件名（不含路径和扩展名）
    filename = os.path.basename(input_file)
    book_name = os.path.splitext(filename)[0]
    return book_name

def process_text_file(input_file):
    """
    处理任意文本文件
    """
    if not os.path.exists(input_file):
        print(f"错误：文件 {input_file} 不存在")
        return
    
    # 获取书名
    book_name = get_book_name_from_file(input_file)
    output_dir = book_name
    
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
        output_file = os.path.join(output_dir, f'{book_name}-ch-{i:02d}.txt')
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
        # 默认处理David Copperfield
        input_file = 'txt/DavidCopperfield.txt'
    
    process_text_file(input_file)

if __name__ == '__main__':
    main()

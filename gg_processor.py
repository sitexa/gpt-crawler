#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用文本处理程序
功能：
1. 删除中文和非ASCII字符
2. 按"Chapter X"切分文档
3. 保存为gg-ch-x.txt格式
4. 格式化段落间距（标题与段落之间，段落与段落之间空2行）
"""

import os
import re
import sys
from pathlib import Path


def clean_text(text):
    """
    清理文本：删除中文和非ASCII字符
    """
    # 删除中文字符（Unicode范围：\u4e00-\u9fff）
    text = re.sub(r'[\u4e00-\u9fff]', '', text)
    
    # 保留ASCII字符、换行符、制表符和基本标点符号
    # 只保留可打印的ASCII字符（32-126）和空白字符（9, 10, 13）
    cleaned_chars = []
    for char in text:
        # 保留ASCII可打印字符和基本空白字符
        if ord(char) >= 32 and ord(char) <= 126:
            cleaned_chars.append(char)
        elif char in ['\n', '\r', '\t']:
            cleaned_chars.append(char)
        # 其他字符（包括非ASCII字符）将被删除
    
    return ''.join(cleaned_chars)


def split_by_chapters(text):
    """
    按"Chapter X"模式切分文本
    """
    # 使用正则表达式匹配Chapter模式
    chapter_pattern = r'(?i)^Chapter\s+(\d+)$'
    
    # 按行分割文本
    lines = text.split('\n')
    chapters = []
    current_chapter = []
    current_chapter_num = None
    
    for line in lines:
        line = line.strip()
        
        # 检查是否是章节标题
        match = re.match(chapter_pattern, line)
        if match:
            # 如果已有章节内容，保存当前章节
            if current_chapter and current_chapter_num is not None:
                chapter_content = '\n'.join(current_chapter).strip()
                if chapter_content:
                    chapters.append((current_chapter_num, chapter_content))
            
            # 开始新章节
            current_chapter_num = int(match.group(1))
            current_chapter = [line]  # 包含章节标题
        else:
            # 添加到当前章节
            current_chapter.append(line)
    
    # 保存最后一个章节
    if current_chapter and current_chapter_num is not None:
        chapter_content = '\n'.join(current_chapter).strip()
        if chapter_content:
            chapters.append((current_chapter_num, chapter_content))
    
    return chapters


def format_chapter_content(content):
    """
    格式化章节内容：标题与段落之间，段落与段落之间空2行
    """
    lines = content.split('\n')
    formatted_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            # 跳过空行
            i += 1
            continue
        
        # 添加当前行
        formatted_lines.append(line)
        
        # 检查下一行是否为空
        next_line_empty = (i + 1 >= len(lines)) or (not lines[i + 1].strip())
        
        if not next_line_empty:
            # 如果下一行不为空，添加两个空行
            formatted_lines.append('')
            formatted_lines.append('')
        
        i += 1
    
    return '\n'.join(formatted_lines)


def process_text_file(input_file, output_dir="gg"):
    """
    处理文本文件的主函数
    """
    try:
        # 读取输入文件
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        print(f"正在处理文件: {input_file}")
        print(f"原始文件大小: {len(content)} 字符")
        
        # 清理文本
        cleaned_content = clean_text(content)
        print(f"清理后文件大小: {len(cleaned_content)} 字符")
        
        # 按章节切分
        chapters = split_by_chapters(cleaned_content)
        print(f"找到 {len(chapters)} 个章节")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 保存每个章节
        for chapter_num, chapter_content in chapters:
            # 格式化章节内容
            formatted_content = format_chapter_content(chapter_content)
            
            # 生成输出文件名
            output_filename = f"gg-ch-{chapter_num:02d}.txt"
            output_file_path = output_path / output_filename
            
            # 写入文件
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            print(f"已保存: {output_file_path}")
        
        print(f"处理完成！所有文件已保存到 {output_dir}/ 目录")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        sys.exit(1)


def main():
    """
    主函数
    """
    if len(sys.argv) != 2:
        print("用法: python gg_processor.py <输入文件路径>")
        print("示例: python gg_processor.py txt/TheGreatGatsby.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：文件 {input_file} 不存在")
        sys.exit(1)
    
    # 处理文件
    process_text_file(input_file)


if __name__ == "__main__":
    main()

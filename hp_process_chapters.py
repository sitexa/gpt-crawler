#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理哈利波特段落JSON文件，按章节拆分为独立的txt文件
"""

import json
import os
import re
from pathlib import Path


def extract_chapter_number(chapter_str):
    """从章节字符串中提取章节号"""
    match = re.search(r'Chapter (\d+)', chapter_str)
    if match:
        return int(match.group(1))
    return 0


def format_paragraph_text(paragraph_text):
    """
    格式化段落文本：
    - 双换行符分隔段落
    - 单换行符分隔句子
    """
    # 将文本按双换行符分割成段落
    paragraphs = paragraph_text.split('\n\n')
    
    formatted_paragraphs = []
    for paragraph in paragraphs:
        # 清理段落内容，移除多余的空白字符
        paragraph = paragraph.strip()
        if paragraph:
            # 确保句子之间用单换行符分隔
            # 将句子分割并重新组合
            sentences = []
            for line in paragraph.split('\n'):
                line = line.strip()
                if line:
                    sentences.append(line)
            
            # 用单换行符连接句子
            formatted_paragraph = '\n'.join(sentences)
            formatted_paragraphs.append(formatted_paragraph)
    
    # 用双换行符连接段落
    return '\n\n'.join(formatted_paragraphs)


def process_chapters(json_file_path, output_dir):
    """
    处理哈利波特章节JSON文件
    
    Args:
        json_file_path: JSON文件路径
        output_dir: 输出目录路径
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"开始处理 {len(data)} 个章节...")
    
    for chapter_data in data:
        # 提取章节信息
        chapter_str = chapter_data.get('chapter', '')
        chapter_number = extract_chapter_number(chapter_str)
        
        if chapter_number == 0:
            print(f"警告：无法提取章节号 from '{chapter_str}'")
            continue
        
        # 构建标题行（只使用chapter字段）
        header = f"{chapter_str}\n"
        
        # 获取段落内容
        content = chapter_data.get('content', {})
        paragraphs = content.get('paragraphs', {})
        
        if not paragraphs:
            print(f"警告：章节 {chapter_number} 没有段落内容")
            continue
        
        # 合并所有段落
        all_text = []
        for para_key, para_text in paragraphs.items():
            if para_text and para_text.strip():
                all_text.append(para_text.strip())
        
        # 格式化文本
        formatted_text = format_paragraph_text('\n\n'.join(all_text))
        
        # 组合标题和内容
        final_text = header + "\n" + formatted_text
        
        # 生成文件名
        filename = f"hp_ch_{chapter_number:02d}.txt"
        file_path = output_path / filename
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_text)
        
        print(f"已保存章节 {chapter_number}: {filename}")
    
    print(f"处理完成！文件保存在 {output_path.absolute()}")


def main():
    """主函数"""
    # 文件路径
    json_file = "hp_parapgraph.json"
    output_dir = "./hp"
    
    # 检查输入文件是否存在
    if not os.path.exists(json_file):
        print(f"错误：找不到文件 {json_file}")
        return
    
    try:
        process_chapters(json_file, output_dir)
    except Exception as e:
        print(f"处理过程中出现错误：{e}")


if __name__ == "__main__":
    main()

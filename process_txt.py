import os
import re
import html

# 处理下载的文本，1，标题行；2，段落行；3，非ASCII字符；4，外文字符；
# 直接运行，会处理txt目录下的所有txt文件。

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Decode HTML entities
    content = html.unescape(content)

    # Specific fixes for One Hundred Years of Solitude and other potential issues
    content = content.replace('úrsula', 'Úrsula')
    content = content.replace('Jos ', 'José ')
    content = content.replace('Macon-do', 'Macondo')
    content = content.replace('Aureli-ano', 'Aureliano')

    # Remove non-ASCII characters - REMOVED to allow decoded unicode characters
    # content = re.sub(r'[^\x00-\x7F]+', '', content)

    # Split into lines and strip whitespace
    lines = [line.strip() for line in content.splitlines()]
    
    # Filter out empty lines
    lines = [line for line in lines if line]

    # Join with double newlines to ensure blank lines between paragraphs/chapters
    new_content = '\n\n'.join(lines)

    # Add a final newline
    if new_content:
        new_content += '\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Processed {filepath}")

def main():
    txt_dir = 'txt'
    if not os.path.exists(txt_dir):
        print(f"Directory '{txt_dir}' not found.")
        return

    for filename in os.listdir(txt_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(txt_dir, filename)
            process_file(filepath)

if __name__ == '__main__':
    main()

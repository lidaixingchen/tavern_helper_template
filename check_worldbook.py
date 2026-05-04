import os
import re
import sys

# 设置标准输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def get_referenced_files(index_path):
    """从 index.yaml 中提取所有引用的文件"""
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取所有 文件: xxx 的引用
    pattern = r'文件:\s*(.+)'
    matches = re.findall(pattern, content)

    # 转换路径格式
    files = []
    for match in matches:
        file_path = match.strip()
        # 将反斜杠转换为正斜杠
        file_path = file_path.replace('\\', '/')
        # 移除 "世界书/" 前缀（如果有的话）
        if file_path.startswith('世界书/'):
            file_path = file_path[4:]  # 移除 "世界书/"
        files.append(file_path)

    return files

def get_existing_files(worldbook_dir):
    """获取世界书目录下所有 yaml 文件"""
    files = []
    for root, dirs, filenames in os.walk(worldbook_dir):
        for filename in filenames:
            if filename.endswith('.yaml'):
                # 获取相对路径
                rel_path = os.path.relpath(os.path.join(root, filename), worldbook_dir)
                # 去掉 .yaml 后缀
                rel_path = rel_path.replace('\\', '/').replace('.yaml', '')
                files.append(rel_path)
    return files

def main():
    index_path = 'src/AIDM/index.yaml'
    worldbook_dir = 'src/AIDM/世界书'

    print('=== 检查世界书条目与实际文件 ===\n')

    # 获取引用的文件
    referenced_files = get_referenced_files(index_path)
    print(f'【index.yaml 中引用的文件】共 {len(referenced_files)} 个\n')

    # 获取实际存在的文件
    existing_files = get_existing_files(worldbook_dir)
    print(f'【实际存在的世界书文件】共 {len(existing_files)} 个\n')

    # 检查引用但不存在的文件
    print('=== 检查引用但不存在的文件 ===\n')
    missing_files = []
    for ref in referenced_files:
        if ref not in existing_files:
            missing_files.append(ref)
            print(f'[MISSING] 世界书/{ref}.yaml')

    if not missing_files:
        print('[OK] 所有引用的文件都存在')

    # 检查存在但未引用的文件
    print('\n=== 检查存在但未引用的文件 ===\n')
    unreferenced_files = []
    for file in existing_files:
        if file not in referenced_files:
            unreferenced_files.append(file)
            print(f'[UNREFERENCED] 世界书/{file}.yaml')

    if not unreferenced_files:
        print('[OK] 所有文件都已被引用')

    # 统计
    print('\n=== 统计 ===')
    print(f'引用的文件总数: {len(referenced_files)}')
    print(f'实际存在的文件: {len(existing_files)}')
    print(f'缺失的文件: {len(missing_files)}')
    print(f'未引用的文件: {len(unreferenced_files)}')

if __name__ == '__main__':
    main()

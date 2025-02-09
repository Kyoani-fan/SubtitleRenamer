import os
import re

def commonprefix(l):
    """找出列表中最长公共前缀"""
    if not l: return ''
    s1 = min(l)
    s2 = max(l)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1

def commonsuffix(l):
    """找出列表中最长公共后缀"""
    if not l: return ''
    s1 = min(l)[::-1]
    s2 = max(l)[::-1]
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i][::-1]
    return s1[::-1]

def extract_id(filename, prefix, suffix):
    """从文件名中去除公共前缀和后缀，剩下的部分视为ID"""
    filename_no_ext = os.path.splitext(filename)[0]  # 去除扩展名
    id_part = filename_no_ext.replace(prefix, '').replace(suffix, '')
    match = re.search(r'\d{1,3}(?=v\d)?', id_part)  # 使用正向断言匹配序号及可能的版本信息前的部分
    if match:
        return str(int(match.group()))  # 将找到的数字部分转为整数再转回字符串，去掉前导零
    return None

def get_files_by_extension(directory, extensions):
    """获取特定扩展名的所有文件"""
    files = []
    for file in os.listdir(directory):
        if any(file.endswith(ext) for ext in extensions):
            files.append(file)
    return files

def main():
    directory = '.'  # 当前目录
    video_extensions = ['.mkv', '.mp4', '.avi', '.mov', '.flv', '.wmv']
    subtitle_extensions = ['.srt', '.ass']

    # 获取媒体文件和字幕文件
    video_files = get_files_by_extension(directory, video_extensions)
    subtitle_files = get_files_by_extension(directory, subtitle_extensions)

    if not video_files or not subtitle_files:
        print("未找到任何媒体文件或字幕文件")
        return

    # 找到所有媒体文件名的最长公共前缀和后缀
    prefix = commonprefix(video_files)
    suffix = commonsuffix(video_files)

    # 提取视频文件的id
    video_ids = {extract_id(video, prefix, suffix): video for video in video_files}

    # 检查是否有重复的字幕文件序号
    subtitle_counter = {}
    for subtitle in subtitle_files:
        id = extract_id(subtitle, prefix, suffix)
        if id not in subtitle_counter:
            subtitle_counter[id] = [subtitle]
        else:
            subtitle_counter[id].append(subtitle)

    # 判断是否存在重复序号并处理
    has_duplicates = any(len(subtitles) > 1 for subtitles in subtitle_counter.values())
    language_code = None
    if has_duplicates:
        print("选择语言")
        language_code = input("请输入语言代号：")

    # 如果有重复序号，则根据用户输入的语言代号过滤字幕文件
    if language_code:
        filtered_subtitle_counter = {}
        for id, subtitles in subtitle_counter.items():
            if len(subtitles) > 1:
                filtered_subtitles = [sub for sub in subtitles if language_code in sub]
                filtered_subtitle_counter[id] = filtered_subtitles
            else:
                filtered_subtitle_counter[id] = subtitles
        subtitle_counter = filtered_subtitle_counter

    # 重命名字幕文件
    for id, subtitles in subtitle_counter.items():
        if id in video_ids:
            video_name = os.path.splitext(video_ids[id])[0]  # 去除扩展名
            for subtitle in subtitles:
                new_name = f"{video_name}{os.path.splitext(subtitle)[1]}"
                os.rename(os.path.join(directory, subtitle), os.path.join(directory, new_name))
                print(f"{id}:  {subtitle} -> {new_name}")

if __name__ == "__main__":
    main()
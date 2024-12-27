# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : audio_generate.py
# Time       : 2024/12/27 13:27
# Author     : Feiren Cheng
# Description: 
"""
import asyncio
import datetime
import os
from pathlib import Path

from edge_tts import Communicate
from styles.global_style import style
import streamlit as st
import sys
import os
import subprocess
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

style()

tab1 = st.tabs(["**音频生成**"])[0]
output_file_path = "cache/audio_generate/audios"
st.session_state.output_file_audio = output_file_path

# 初始化 session_state
if 'text_content' not in st.session_state:
    st.session_state.text_content = ''

if 'res_audio' not in st.session_state:
    st.session_state.res_audio = ''

def merge_audio_files(input_dir, output_file, audio_extensions=('.mp3', '.wav', '.m4a')):
    """
    合并指定目录下的所有音频文件

    参数:
        input_dir: 输入音频文件所在的目录
        output_file: 输出文件的路径
        audio_extensions: 要处理的音频文件扩展名元组
    """
    # 确保输入目录存在
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"输入目录 {input_dir} 不存在")

    # 获取所有音频文件并排序
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(input_path.glob(f"*{ext}"))
    audio_files.sort()

    if not audio_files:
        raise ValueError(f"在 {input_dir} 中没有找到音频文件")

    # 生成临时的文件列表
    list_file = input_path / "audiolist.txt"
    with open(list_file, 'w', encoding='utf-8') as f:
        for audio_file in audio_files:
            # 使用相对路径
            f.write(f"file '{audio_file.name}'\n")

    try:
        # 使用FFmpeg合并音频文件
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(list_file),
            '-c', 'copy',
            str(output_file)
        ]

        # 执行FFmpeg命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("FFmpeg错误输出：", result.stderr)
            raise RuntimeError("FFmpeg合并失败")

        print(f"音频合并成功！输出文件：{output_file}")

    finally:
        # 清理临时文件
        if list_file.exists():
            list_file.unlink()


async def text_to_audio(text, voice="zh-CN-YunyangNeural", output_file="temp.mp3"):
    communicate = Communicate(text, voice)
    await communicate.save(output_file)


async def process_texts(texts, voice="zh-CN-YunyangNeural", base_output_path="output"):
    tasks = []
    for index, text in enumerate(texts):
        output_file = f"{base_output_path}/{index}.mp3"
        task = asyncio.create_task(text_to_audio(text, voice, output_file))
        tasks.append(task)
    await asyncio.gather(*tasks)


def process_audio_files(directory):
    files_size = len(os.listdir(directory))
    durations = {}
    for index in range(files_size):
        file_path = os.path.join(directory, f"{index}.mp3")
        durations[index] = file_path
    return durations


async def main_generate_audio(texts):
    print("\n\033[1;34m🚀 任务开始执行\033[0m")
    print(f"\n\033[1;34m🚀 {texts}\033[0m")
    now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    voice = "zh-CN-YunyangNeural"  # 使用 Azure 提供的神经网络语音
    base_output_path = os.path.join(output_file_path, f"final_audio_{now_time}")
    st.session_state.output_file_audio_path = base_output_path
    if not os.path.exists(base_output_path):
        os.makedirs(base_output_path, exist_ok=True)
    text_list = texts.split("。")
    await process_texts(text_list, voice, base_output_path)
    if len(text_list) > 1:
        out_file = f"{base_output_path}/res.mp3"
        merge_audio_files(base_output_path, f"{base_output_path}/res.mp3", "mp3")
        st.session_state.res_audio = out_file
    else:
        st.session_state.res_audio = f"{base_output_path}/0.mp3"
    st.session_state.is_success = True
    print("\033[1;34m🎉 生成成功！\033[0m")

with tab1:
    col1, col2 = st.columns([0.75, 0.25])  # 置顶标题、执行按钮流程模块
    # 标题模块
    with col1:
        st.write("")
        st.write("")
        st.subheader("TTS")
        st.caption("generate audio")
        txt = st.text_area(label="请输入：", max_chars=500, height=150, value=st.session_state.text_content)
        # 当文本发生变化时更新 session_state
        if txt != st.session_state.text_content:
            st.session_state.text_content = txt

    with col2:
        st.write("")
        st.write("")
        if st.button("**开始生成**", type="primary", use_container_width=True):
            asyncio.run(main_generate_audio(st.session_state.text_content))
        if "res_audio" in st.session_state:
            with open(st.session_state.res_audio, "rb") as file_steam:
                st.download_button(
                    label="**音频下载**",
                    data=file_steam,
                    key='audio_download',
                    file_name='res.mp3',
                    use_container_width=True,
                    type="primary")

    st.write("")
    with st.expander("**Audition / 试听**", expanded=True, icon=":material/graphic_eq:"):
        col6, col7 = st.columns([0.9999999, 0.0000001])

    with col6:
        try:
            st.caption("音频音轨")
            audio_file = open(st.session_state.res_audio, "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes)
        except:
            try:
                audio_bytes = st.session_state.res_audio.getvalue()
                st.audio(audio_bytes)
            except:
                st.info(
                    "##### 音轨预览区域 \n\n&nbsp;**生成后自动显示",
                    icon=":material/view_in_ar:")
                st.write("")

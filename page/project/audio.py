import os
import json
import toml
import time
from pathlib import Path
import datetime
import streamlit as st
import streamlit_antd_components as sac

from config.config import load_config, ModelMappins
from styles.global_style import style
from utils.public import (FileToMp3, OpenaiWhisperResult, runWhisperSeperateProc, translate, local_translate,
                          generate_srt_from_result, generate_srt_from_result_2, srt_mv, parse_srt_file, convert_to_srt,
                          show_video, add_font_settings, srt_to_ass, srt_to_vtt, srt_to_sbv)

style()

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

path = os.getcwd() + "/"
llms_path = "config/llms.toml"
whisper_path = "config/whisper.toml"
font_data_path = "config/font.txt"
audio_config_path = "config/audio.toml"
prompt_config_path = "config/prompt.json"
project_config_path = "config/project.toml"
audio_cache_path = path + "cache/audio/"

with open(font_data_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()
    fonts = [line.strip() for line in lines]

LOCAL_CONFIG = load_config()
prompt = LOCAL_CONFIG.prompt
home_key = LOCAL_CONFIG.llms["Home"]["key"]  # home
home_url = LOCAL_CONFIG.llms["Home"]["url"]
home_model = LOCAL_CONFIG.llms["Home"]["model"]

local_key = LOCAL_CONFIG.llms["Local"]["key"]  # Local
local_url = LOCAL_CONFIG.llms["Local"]["url"]
local_model = LOCAL_CONFIG.llms["Local"]["model"]

custom_key = LOCAL_CONFIG.llms["Custom"]["key"]  # Custom
custom_base = LOCAL_CONFIG.llms["Custom"]["url"]
custom_model = LOCAL_CONFIG.llms["Custom"]["model"]

global_key = LOCAL_CONFIG.llms["Global"]["key"]  # Global
global_url = LOCAL_CONFIG.llms["Global"]["url"]

chatgpt_key = LOCAL_CONFIG.llms["ChatGPT"]["key"]  # Openai
chatgpt_url = LOCAL_CONFIG.llms["ChatGPT"]["url"]

claude_key = LOCAL_CONFIG.llms["Claude"]["key"]  # claude
claude_url = LOCAL_CONFIG.llms["Claude"]["url"]

gemini_key = LOCAL_CONFIG.llms["Gemini"]["key"]  # Gemini
gemini_url = LOCAL_CONFIG.llms["Gemini"]["url"]

deepseek_key = LOCAL_CONFIG.llms["DeepSeek"]["key"]  # deepseek
deepseek_url = LOCAL_CONFIG.llms["DeepSeek"]["url"]

kimi_key = LOCAL_CONFIG.llms["Kimi"]["key"]  # kimi
kimi_base = LOCAL_CONFIG.llms["Kimi"]["url"]

chatglm_key = LOCAL_CONFIG.llms["ChatGLM"]["key"]  # chatglm
chatglm_url = LOCAL_CONFIG.llms["ChatGLM"]["url"]

ai01_key = LOCAL_CONFIG.llms["Yi"]["key"]  # 01
ai01_url = LOCAL_CONFIG.llms["Yi"]["url"]

whisper_mode = LOCAL_CONFIG.whisper["Mode"]["WhisperMode"]  # whisper_mode

whisper_temp = LOCAL_CONFIG.whisper["OpenAI"]["Temp"]  # whisper_temp
whisper_prompt = LOCAL_CONFIG.whisper["OpenAI"]["Prompt"]  # whisper_mode

faster_gpu = LOCAL_CONFIG.whisper["Faster"]["GPU"]  # faster_gpu
faster_vad = LOCAL_CONFIG.whisper["Faster"]["VAD"]  # faster_vad
faster_temp = LOCAL_CONFIG.whisper["Faster"]["Temp"]  # faster_temp
faster_prompt = LOCAL_CONFIG.whisper["Faster"]["Prompt"]  # faster_prompt
faster_min_vad = LOCAL_CONFIG.whisper["Faster"]["min_vad"]  # faster_min_vad
faster_beam_size = LOCAL_CONFIG.whisper["Faster"]["beam_size"]  # faster_beam_size

faster_local_path = LOCAL_CONFIG.whisper["Faster_Local"]["path"]  # 模型路径
faster_local_gpu = LOCAL_CONFIG.whisper["Faster_Local"]["GPU"]  # GPU 加速
faster_local_vad = LOCAL_CONFIG.whisper["Faster_Local"]["VAD"]  # VAD
faster_local_temp = LOCAL_CONFIG.whisper["Faster_Local"]["Temp"]  # 温度
faster_local_prompt = LOCAL_CONFIG.whisper["Faster_Local"]["Prompt"]  # 提示词
faster_local_min_vad = LOCAL_CONFIG.whisper["Faster_Local"]["min_vad"]  # 最小 VAD 持续时间
faster_local_beam_size = LOCAL_CONFIG.whisper["Faster_Local"]["beam_size"]  # Beam Size

language = LOCAL_CONFIG.audio["whisper"]["language_list"]
openai_whisper_model_list = LOCAL_CONFIG.audio["whisper"]["openai_whisper_model_list"]
faster_whisper_model_list = LOCAL_CONFIG.audio["whisper"]["faster_whisper_model_list"]
language_index = LOCAL_CONFIG.audio["whisper"]["language_index"]
openai_whisper_model_index = LOCAL_CONFIG.audio["whisper"]["openai_whisper_model_index"]
faster_whisper_model_index = LOCAL_CONFIG.audio["whisper"]["faster_whisper_model_index"]
faster_whisper_model_local_index = LOCAL_CONFIG.audio["whisper"]["faster_whisper_model_local_index"]

translate_index = LOCAL_CONFIG.audio["translate"]["translate_index"]
language2 = LOCAL_CONFIG.audio["translate"]["language_list"]
language2_index1 = LOCAL_CONFIG.audio["translate"]["language_index1"]
language2_index2 = LOCAL_CONFIG.audio["translate"]["language_index2"]
wait_time_setting = LOCAL_CONFIG.audio["translate"]["wait_time"]
prompt_pre_setting = LOCAL_CONFIG.audio["translate"]["prompt"]
system_prompt = LOCAL_CONFIG.prompt[prompt_pre_setting]["system_prompt"].replace("{language1}",
                                                                                 language2_index1).replace(
    "{language2}", language2_index2)
user_prompt = LOCAL_CONFIG.prompt[prompt_pre_setting]["user_prompt"].replace("{language1}", language2_index1).replace(
    "{language2}", language2_index2)

srt_setting = LOCAL_CONFIG.audio["subtitle"]["srt"]
audio_readme = LOCAL_CONFIG.audio["other"]["first"]

translation_dict = ModelMappins.translation_dict


@st.dialog("使用提示")
def AudioReadme():
    st.write("""
    ## 欢迎首次使用 AI全自动音频翻译 功能！

    为了确保顺利运行并获得最佳体验，请关闭此弹窗后，前往页面中的**参数设置**模块，进行必要的参数配置。
    
    请务必根据您的需求及时调整设置，以提高翻译的准确性和效率。

    更多参考资源：
    - 📘 [相关教程](https://blog.chenyme.top/blog/aavt-install)
    - 📂 [项目地址](https://github.com/Chenyme/Chenyme-AAVT)
    - 💬 [交流群组](https://t.me/+j8SNSwhS7xk1NTc9)
    
    """)
    st.write("")

    if st.button("**我已知晓&nbsp;&nbsp;&nbsp;不再弹出**", type="primary", use_container_width=True,
                 key="blog_first_button"):
        with open(audio_config_path, 'w', encoding="utf-8") as f:
            LOCAL_CONFIG.audio["other"]["first"] = True
            toml.dump(LOCAL_CONFIG.audio, f)
        st.session_state.read = True
        st.rerun()
    st.write("")


if not audio_readme:
    AudioReadme()
if "save" in st.session_state:
    st.toast("参数已成功保存", icon=":material/verified:")
    del st.session_state["save"]
if "read" in st.session_state:
    st.toast("欢迎使用 ~", icon=":material/verified:")
    del st.session_state["read"]
if "upload" in st.session_state:
    st.toast("文件上传成功！", icon=":material/verified:")
    del st.session_state["upload"]

tab1, tab2 = st.tabs(["**音频识别**", "**参数设置**"])
with tab2:
    @st.dialog("语言说明")
    def Audio_lang():
        st.write(
            "**强制指定视频语言会提高识别准确度，但也可能会造成识别出错。** \n\n`自动识别` - 自动检测语言 (Auto Detect) \n\n`zh` - 中文 (Chinese) - 中文 \n\n`en` - 英语 (English) - English \n\n`ja` - 日语 (Japanese) - 日本語 \n\n`th` - 泰语 (Thai) - ภาษาไทย \n\n`de` - 德语 (German) - Deutsch \n\n`fr` - 法语 (French) - français \n\n`ru` - 俄语 (Russian) - Русский \n\n`ko` - 韩语 (Korean) - 한국어 \n\n`vi` - 越南语 (Vietnamese) - Tiếng Việt \n\n`it` - 意大利语 (Italian) - Italiano \n\n`ar` - 阿拉伯语 (Arabic) - العربية \n\n`es` - 西班牙语 (Spanish) - Español \n\n`bn` - 孟加拉语 (Bengali) - বাংলা \n\n`pt` - 葡萄牙语 (Portuguese) - Português \n\n`hi` - 印地语 (Hindi) - हिंदी")


    AudioSave = st.container()
    AudioSetting = st.container(border=True)

    with AudioSetting:
        st.write("#### Whisper 识别参数 ")
        st.write("")
        if whisper_mode == "OpenAIWhisper - API":
            st.write("###### 识别模型")
            st.caption("使用 OpenAI API 支持调用的 Whisper 模型 ")
            openai_whisper_model_index = st.selectbox("Whisper 模型", openai_whisper_model_list,
                                                      openai_whisper_model_list.index(openai_whisper_model_index),
                                                      label_visibility="collapsed")
            st.write("")
        if whisper_mode == "FasterWhisper - AutoDownload":
            st.write("###### 识别模型")
            st.caption("使用 FasterWhisper 支持调用的 Whisper 模型 ")
            faster_whisper_model_index = st.selectbox("Whisper 模型", faster_whisper_model_list,
                                                      faster_whisper_model_list.index(faster_whisper_model_index),
                                                      label_visibility="collapsed")
        if whisper_mode == "FasterWhisper - LocalModel":
            st.write("###### 识别模型")
            st.caption(
                "使用已部署到本地的 FasterWhisper 模型 | [支持的模型](https://huggingface.co/Systran) | [使用教程](https://blog.chenyme.top/blog/aavt-install#bfd48658b23b)")
            model_names = os.listdir(faster_local_path)
            try:
                faster_whisper_model_local_index = st.selectbox("Whisper 本地模型", model_names,
                                                                model_names.index(faster_whisper_model_local_index),
                                                                label_visibility="collapsed")
            except:
                faster_whisper_model_local_index = st.selectbox("Whisper 本地模型", model_names)
        st.write("")
        if whisper_mode != "OpenAIWhisper - API":
            st.write("###### 视频语言")
            st.caption("强制指定视频语言")
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                language_index = st.selectbox('Media 语言', language, index=language.index(language_index),
                                              label_visibility="collapsed")
            with col2:
                if st.button("**?**", use_container_width=True):
                    Audio_lang()

        st.write("")
        st.write("#### LLMs 翻译参数 ")
        st.write("")
        st.write("###### 翻译引擎")
        st.caption("翻译模块使用的引擎，请确保您已在全局设置中配置对应的引擎参数！")
        items_list = [sac.CasItem('无需翻译'),
                      sac.CasItem('Local / 本地模型', icon='house-up-fill')]
        model_dict = ModelMappins.model_dict
        for privider, models_list in model_dict.items():
            items_list.append(sac.CasItem(privider, icon='folder2', children=[
                sac.CasItem(model, icon='folder2-open') for model in models_list
            ]))

        translate_index = sac.cascader(items=items_list, label='', search=True, index=translate_index, return_index=True)
        if translate_index != [0]:
            st.write("")
            col1, col2 = st.columns(2)
            with col1:
                st.write("###### 原始语言")
                st.caption("文件的原始语言")
                language2_index1 = st.selectbox('原始语言', language2, index=language2.index(language2_index1),
                                                label_visibility="collapsed")
            with col2:
                st.write("###### 目标语言")
                st.caption("文件的目标语言")
                language2_index2 = st.selectbox('目标语言', language2, index=language2.index(language2_index2),
                                                label_visibility="collapsed")
            st.write("")
            st.write("###### 翻译提示词")
            st.caption("翻译使用的提示词，可前往全局设置-翻译设置中配置新的提示词")
            try:
                prompt_pre_setting = st.selectbox('预设 prompt', prompt.keys(),
                                                  index=list(prompt.keys()).index(prompt_pre_setting),
                                                  label_visibility="collapsed")
            except:
                prompt_pre_setting = st.selectbox('预设 prompt', prompt.keys(), label_visibility="collapsed")
            st.write("")
            st.write("###### API 调用间隔 / s")
            st.caption(
                "翻译时API的调用间隔。请参阅您的API服务商文档中的 每分钟调用最大限制速率 进行适当调整，若翻译时遇到报错 429：`Too Many Requests`、`RateLimitError` 请适当增大间隔。")
            wait_time_setting = st.number_input('翻译间隔(s)', min_value=0.0, max_value=5.0, value=wait_time_setting,
                                                step=0.1, label_visibility="collapsed")

        st.write("")
        st.write("#### Subtitle 字幕参数 ")
        st.write("")
        st.write("###### 双语字幕")
        st.caption("选择双语字幕的显示样式")
        srt_choose = ["关闭", "原始语言为首", "目标语言为首"]
        srt_setting = st.selectbox('双语字幕', srt_choose, index=srt_choose.index(srt_setting),
                                   label_visibility="collapsed")
        st.write("")

    with AudioSave:
        col1, col2 = st.columns([0.75, 0.25])
        st.write("")
        with col2:
            st.write("")
            st.write("")
            if st.button("**保存更改**", use_container_width=True, type="primary"):
                with open(audio_config_path, 'w', encoding="utf-8") as f:
                    LOCAL_CONFIG.audio["whisper"]["language_index"] = language_index
                    LOCAL_CONFIG.audio["whisper"]["openai_whisper_model_index"] = openai_whisper_model_index
                    LOCAL_CONFIG.audio["whisper"]["faster_whisper_model_index"] = faster_whisper_model_index
                    LOCAL_CONFIG.audio["whisper"]["faster_whisper_model_local_index"] = faster_whisper_model_local_index

                    LOCAL_CONFIG.audio["translate"]["translate_index"] = translate_index
                    LOCAL_CONFIG.audio["translate"]["language_index1"] = language2_index1
                    LOCAL_CONFIG.audio["translate"]["language_index2"] = language2_index2
                    LOCAL_CONFIG.audio["translate"]["wait_time"] = wait_time_setting
                    LOCAL_CONFIG.audio["translate"]["prompt"] = prompt_pre_setting

                    LOCAL_CONFIG.audio["subtitle"]["srt"] = srt_setting

                    toml.dump(LOCAL_CONFIG.audio, f)
                    st.session_state.save = True
                    st.rerun()
        with col1:
            st.write("")
            st.write("")
            st.write("### 更改参数设置")
            st.caption("Changing Parameter Settings")

with tab1:
    # 配置处理
    faster_whisper_model_local_index = faster_local_path + "/" + faster_whisper_model_local_index

    col1, col2 = st.columns([0.75, 0.25])  # 置顶标题、执行按钮流程模块

    # 标题模块
    with col1:
        st.write("")
        st.write("")
        st.subheader("AI 全自动音频翻译")
        st.caption("AI Automatic Audio Translation")

    # 执行按钮流程模块
    with col2:
        st.write("")
        st.write("")
        if st.button("**开始识别**", type="primary", use_container_width=True):
            if "uploaded_file_audio" in st.session_state:
                uploaded_file_audio = st.session_state.uploaded_file_audio
                print("\n" + "=" * 50)
                print("\n\033[1;39m*** Chenyme-AAVT AI音频识别 ***\033[0m")
                st.toast('任务开始执行！请勿在运行时切换菜单或修改参数!', icon=":material/rocket_launch:")

                msg_ved = st.toast('正在对音频进行预处理', icon=":material/graphic_eq:")
                current_time = datetime.datetime.now().strftime("_%Y%m%d%H%M%S")
                st.session_state.audio_name_original = uploaded_file_audio.name.split('.')[0]
                st.session_state.audio_name = "output." + uploaded_file_audio.name.split('.')[-1]
                output_file = audio_cache_path + st.session_state.audio_name_original + current_time
                os.makedirs(output_file)
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                with open(output_file + '/' + st.session_state.audio_name, "wb") as file:
                    file.write(uploaded_file_audio.getbuffer())
                msg_ved.toast("音频预处理完成", icon=":material/graphic_eq:")

                print("\n\033[1;34m🚀 任务开始执行\033[0m")
                print(f"\033[1;34m📂 本次任务目录:\033[0m\033[1;34m {output_file} \033[0m")
                print("\033[1;33m⚠️ 请不要在任务运行期间切换菜单或修改参数！\033[0m")

                msg_whs = st.toast("正在识别音频内容", icon=":material/troubleshoot:")
                if whisper_mode == "OpenAIWhisper - API":
                    result = OpenaiWhisperResult(chatgpt_key, chatgpt_url,
                                                 f"{output_file}/{st.session_state.audio_name}",
                                                 openai_whisper_model_index, whisper_prompt, whisper_temp)
                if whisper_mode == "FasterWhisper - AutoDownload":
                    result = runWhisperSeperateProc(f"{output_file}/{st.session_state.audio_name}", faster_gpu,
                                                    faster_whisper_model_index, faster_prompt, faster_temp, faster_vad,
                                                    language_index, faster_beam_size, faster_min_vad)
                if whisper_mode == "FasterWhisper - LocalModel":
                    result = runWhisperSeperateProc(f"{output_file}/{st.session_state.audio_name}", faster_local_gpu,
                                                    faster_whisper_model_local_index, faster_local_prompt,
                                                    faster_local_temp, faster_local_vad, language_index,
                                                    faster_local_beam_size, faster_local_min_vad)
                if 'error' in result:
                    print(f"\033[1;31m❌ Whisper识别异常: {result['error']}\033[0m")
                    st.error(f"处理失败，错误信息：{result['error']}")
                    st.stop()
                print("\033[1;34m🎉 Whisper 识别成功！\033[0m")
                msg_whs.toast("音频内容识别完成", icon=":material/colorize:")
                print("\033[1;34m🎉 音频内容识别完成！\033[0m")
                translate_option = translation_dict[tuple(translate_index)]
                if translate_option != '无需翻译':
                    msg_tra = st.toast("正在翻译字幕", icon=":material/translate:")
                    if '本地模型' in translate_option:
                        result = local_translate(system_prompt, user_prompt, local_key, local_url, local_model, result,
                                                 srt_setting)
                    elif 'gemini' in translate_option:
                        result = translate(system_prompt, user_prompt, gemini_key, gemini_url, translate_option, result,
                                           wait_time_setting, srt_setting)
                    elif 'yi' in translate_option:
                        result = translate(system_prompt, user_prompt, ai01_key, ai01_url, translate_option, result,
                                           wait_time_setting, srt_setting)
                    elif 'gpt' in translate_option:
                        result = translate(system_prompt, user_prompt, chatgpt_key, chatgpt_url, translate_option,
                                           result, wait_time_setting, srt_setting)
                    elif 'moonshot' in translate_option:
                        result = translate(system_prompt, user_prompt, kimi_key, kimi_base, translate_option, result,
                                           wait_time_setting, srt_setting)
                    elif 'glm' in translate_option:
                        result = translate(system_prompt, user_prompt, chatglm_key, chatglm_url, translate_option,
                                           result, wait_time_setting, srt_setting)
                    elif 'deepseek' in translate_option:
                        result = translate(system_prompt, user_prompt, deepseek_key, deepseek_url, translate_option,
                                           result, wait_time_setting, srt_setting)
                    elif 'claude' in translate_option:
                        result = translate(system_prompt, user_prompt, claude_key, claude_url, translate_option, result,
                                           wait_time_setting, srt_setting)
                    print("\033[1;34m🎉 字幕翻译已完成！\033[0m")
                    msg_tra.toast("翻译任务结束！", icon=":material/translate:")

                msg_srt = st.toast('正在生成SRT字幕文件', icon=":material/edit_note:")
                print("\n\033[1;35m*** 正在生成 SRT 字幕文件 ***\033[0m\n")
                srt_content = generate_srt_from_result(result)
                with open(output_file + "/output.srt", 'w', encoding='utf-8') as srt_file:
                    srt_file.write(srt_content)
                st.session_state.output_file_audio = output_file

                print("\033[1;34m🎉 任务成功结束！\033[0m")
                print("\n" + "=" * 50 + "\n")
            else:
                st.toast("请先在工具栏中上传音频文件！", icon=":material/release_alert:")

    st.write("")
    with st.expander("**Audio Preview / 音轨预览**", expanded=True, icon=":material/graphic_eq:"):
        col6, col7 = st.columns([0.9999999, 0.0000001])

    st.write("")
    col1, col2 = st.columns([0.75, 0.25])
    with col2:
        with st.expander("**Tool / 工具**", expanded=True, icon=":material/construction:"):
            st.caption("上传文件")


            @st.dialog("上传音频文件")
            def upload_audio():
                st.write("在这里上传您需要处理的视频文件。")
                st.write(
                    "请注意，除关闭 CMD 外，执行任务后无法取消任务！请勿在执行时点击任何 项目按钮 或 切换菜单，以免导致识别报错！")
                st.write("")
                uploaded_file_audio = st.file_uploader("上传您的音频文件", type=["mp3", "mpga", "m4a", "wav"],
                                                       label_visibility="collapsed")
                st.write("")
                if st.button("**点击上传**", use_container_width=True, type="primary"):
                    st.session_state.uploaded_file_audio = uploaded_file_audio
                    st.session_state.upload = True
                    st.rerun()
                st.write("")


            if st.button('**文件上传**', use_container_width=True, type="primary", key="upload_audio_button"):
                upload_audio()

            st.caption("字幕工具")
            if st.button('**保存修改**', use_container_width=True, type="primary", key="audio_change"):
                try:
                    with open(st.session_state.output_file_audio + "/output.srt", 'w', encoding='utf-8') as srt_file:
                        srt_file.write(st.session_state.srt_content_new_audio)
                    st.toast("已成功保存", icon=":material/task_alt:")
                except:
                    st.toast("未检测到运行后的字幕文件", icon=":material/error:")

            if st.button('**打开目录**', use_container_width=True, type="primary", key="audio_open"):
                try:
                    os.startfile(st.session_state.output_file_audio)
                    st.toast("注意：文件夹已成功打开，可能未置顶显示，请检查任务栏！", icon=":material/task_alt:")
                except:
                    st.toast("未进行识别，目录尚未生成！", icon=":material/error:")
            st.divider()

            if st.toggle("**更多功能**"):
                st.caption("字幕轴高度")
                height = st.number_input("高度显示", min_value=300, step=100, value=550, label_visibility="collapsed")
                st.session_state.height_audio = height
                st.caption("其他字幕格式")
                try:
                    captions_option = st.radio('更多字幕格式导出', ('VTT', 'ASS', 'SBV'), index=0,
                                               label_visibility="collapsed")
                    if captions_option == 'VTT':
                        vtt_content = srt_to_vtt(st.session_state.srt_content_new_audio)
                        st.download_button(
                            label="**VTT 下载**",
                            data=vtt_content.encode('utf-8'),
                            key='vtt_download',
                            file_name='output.vtt',
                            mime='text/vtt',
                            use_container_width=True,
                            type="primary"
                        )
                    elif captions_option == 'ASS':
                        sbv_content = srt_to_ass(st.session_state.srt_content_new_audio, "Arial", "18", "#FFFFFF")
                        st.download_button(
                            label="**ASS 下载**",
                            data=sbv_content.encode('utf-8'),
                            key='ass_download',
                            file_name='output.ass',
                            mime='text/ass',
                            use_container_width=True,
                            type="primary"
                        )
                    elif captions_option == 'SBV':
                        sbv_content = srt_to_sbv(st.session_state.srt_content_new_audio)
                        st.download_button(
                            label="**SBV 下载**",
                            data=sbv_content.encode('utf-8'),
                            key='sbv_download',
                            file_name='output.sbv',
                            mime='text/sbv',
                            use_container_width=True,
                            type="primary"
                        )
                except:
                    if st.button('**下载字幕**', use_container_width=True, type="primary"):
                        st.toast("未检测到字幕生成！", icon=":material/error:")

            if "height_audio" not in st.session_state:
                st.session_state.height_audio = 550

    with col1:
        with st.expander("**Subtitle Preview / 字幕预览**", expanded=True, icon=":material/subtitles:"):
            try:
                st.caption("字幕时间轴")
                with open(st.session_state.output_file_audio + "/output.srt", 'r', encoding='utf-8') as srt_file:
                    srt_content = srt_file.read()
                srt_data1 = parse_srt_file(srt_content, srt_setting)
                edited_data = st.data_editor(srt_data1, height=st.session_state.height_audio, hide_index=True,
                                             use_container_width=True)
                srt_data2 = convert_to_srt(edited_data, srt_setting)
                st.session_state.srt_content_new_audio = srt_data2
            except:
                st.info(
                    "##### 结果预览区域 \n\n&nbsp;\n\n**生成完毕后会在此区域自动显示字幕时间轴**\n\n 运行前，请在右侧使用上传文件工具导入你的音频文件！ \n\n&nbsp;\n\n&nbsp;",
                    icon=":material/view_in_ar:")
                st.write("")

    with col6:
        try:
            st.caption("音频音轨")
            audio_file = open(f"{st.session_state.output_file_audio}/{st.session_state.audio_name}", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes)
        except:
            try:
                audio_bytes = st.session_state.uploaded_file_audio.getvalue()
                st.audio(audio_bytes)
            except:
                st.info(
                    "##### 音轨预览区域 \n\n&nbsp;**运行后自动显示 | 查看 [项目文档](https://blog.chenyme.top/blog/aavt-install) | 加入 [交流群组](https://t.me/+j8SNSwhS7xk1NTc9)**",
                    icon=":material/view_in_ar:")
                st.write("")

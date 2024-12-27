# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : config.py
# Time       : 2024/12/27 13:34
# Author     : Feiren Cheng
# Description: 
"""
import json
import os

import toml


class ModelMappins(object):
    translation_dict = {
        (0,): '无需翻译',
        (1,): 'Local / 本地模型',
        (2, 3): 'gpt-3.5-turbo',
        (2, 4): 'gpt-4o-mini',
        (2, 5): 'gpt-4',
        (2, 6): 'gpt-4-turbo',
        (2, 7): 'gpt-4o',
        (8, 9): 'claude-3-opus',
        (10, 8): 'claude-3-sonnet',
        (11, 8): 'claude-3-haiku',
        (12, 13): 'gemini-pro',
        (12, 14): 'gemini-1.0-pro',
        (12, 15): 'gemini-1.5-flash',
        (12, 16): 'gemini-1.5-pro',
        (17, 18): 'deepseek-chat',
        (17, 19): 'deepseek-coder',
        (20, 21): 'moonshot-v1-8k',
        (20, 22): 'moonshot-v1-32k',
        (20, 23): 'moonshot-v1-128k',
        (24, 25): 'glm-4',
        (24, 26): 'glm-4-0520',
        (24, 27): 'glm-4-flash',
        (24, 28): 'glm-4-air',
        (24, 29): 'glm-4-airx',
        (30, 31): 'yi-spark',
        (30, 32): 'yi-medium',
        (30, 33): 'yi-medium-200k',
        (30, 34): 'yi-vision',
        (30, 35): 'yi-large',
        (30, 36): 'yi-large-rag',
        (30, 37): 'yi-large-turbo',
        (30, 38): 'yi-large-preview'
    }

    model_dict = {'OpenAI / ChatGPT': ['gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-4', 'gpt-4-turbo', 'gpt-4o'],
                  'Anthropic / Claude': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                  '谷歌公司 / Gemini': ['gemini-pro', 'gemini-1.0-pro', 'gemini-1.5-flash', 'gemini-1.5-pro'],
                  '深度求索 / DeepSeek': ['deepseek-chat', 'deepseek-coder'],
                  '月之暗面 / Kimi': ['moonshot-v1-8k', 'moonshot-v1-32k', 'moonshot-v1-128k'],
                  '智谱清言 / ChatGLM': ['glm-4', 'glm-4-0520', 'glm-4-flash', 'glm-4-air', 'glm-4-airx'],
                  '零一万物 / Yi': ['yi-spark', 'yi-medium', 'yi-medium-200k', 'yi-vision', 'yi-large', 'yi-large-rag',
                                    'yi-large-turbo', 'yi-large-preview']}


class ConfigManager(object):

    def load_config(self, config_path: str):
        with open(config_path, 'r', encoding="utf-8") as config_file:
            if config_path.endswith('.json'):
                conf_json = json.load(config_file)
            else:
                conf_json = toml.load(config_file)
            filename = os.path.basename(config_path).split('.')[0]
            setattr(self, filename, conf_json)


def load_config():
    LOCAL_CONFIG = ConfigManager()
    LOCAL_CONFIG.load_config("config/project.toml")
    LOCAL_CONFIG.load_config("config/prompt.json")
    LOCAL_CONFIG.load_config("config/whisper.toml")
    LOCAL_CONFIG.load_config("config/llms.toml")
    LOCAL_CONFIG.load_config("config/audio.toml")
    LOCAL_CONFIG.load_config("config/translate.toml")
    LOCAL_CONFIG.load_config("config/video.toml")
    return LOCAL_CONFIG


if __name__ == '__main__':
    cm = ConfigManager()
    cm.load_config("project.toml")
    print()

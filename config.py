#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI GPT批处理术语抽取配置文件
包含API配置、模型参数、处理配置和提示词设置
"""

import os
from typing import List, Dict, Any

# =============================================================================
# API 配置
# =============================================================================

# OpenAI API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-mU6afVlo8m1nykBk6c8f7f0496574eF8B13584EaB885346d")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.ai-gaochao.cn/v1")

# 模型配置
DEFAULT_MODEL = "gpt-5"

# =============================================================================
# 模型API参数兼容性配置
# =============================================================================

MODEL_API_PARAMS = {
    # 使用max_completion_tokens的新版本模型
    "new_models": ["gpt-5", "2025", "gpt-4o-2024-08-06"],
    # 使用max_tokens的传统模型
    "legacy_models": ["gpt-4", "gpt-3.5", "gpt-4-turbo"]
}

def get_token_param_name(model: str) -> str:
    """
    根据模型名称返回正确的token参数名
    
    Args:
        model: 模型名称
        
    Returns:
        str: 'max_completion_tokens' 或 'max_tokens'
    """
    model_lower = model.lower()
    
    # 检查是否是新版本模型
    for new_model in MODEL_API_PARAMS["new_models"]:
        if new_model.lower() in model_lower:
            return "max_completion_tokens"
    
    # 默认使用传统参数
    return "max_tokens"

# =============================================================================
# 批处理参数配置
# =============================================================================

BATCH_CONFIG = {
    "temperature": 0,  # 完全确定性输出，用于建立绝对基线
    "max_output_tokens": 128000,  # 通用的最大输出token数（会根据模型自动转换为正确的参数名）
    "check_interval": 5,  # 状态检查间隔（秒）
    "max_wait_time": 3600,  # 最大等待时间（秒）
    "requests_per_minute": 30,  # 每分钟请求限制（降低）
    "max_concurrent": 10,  # 最大并发请求数（降低以提高稳定性）
}

# =============================================================================
# 提示词配置
# =============================================================================

# 术语提取模式
EXTRACTION_MODE = {
    "bilingual": True,  # True=双语模式, False=单语模式（可在运行时修改）
}

SYSTEM_PROMPT = """
You are a precise keyword extraction system. Your task is to extract ONLY the bilingual term pairs from the "关键词" (Chinese keywords) and "Keywords" (English keywords) sections of academic papers. Ignore all other content including abstracts, body text, references, etc.
"""

def get_user_prompt(text: str, bilingual: bool = True) -> str:
    """
    Modified version: Extracts only from keyword sections
    """
    if bilingual:
        # Use regular string (not f-string) to avoid processing {text} placeholder
        return """
Your response must contain only a JSON object with no additional text.

Task: Extract ONLY the bilingual term pairs from the keyword sections:
- Find the "关键词" section (Chinese keywords)
- Find the "Keywords" section (English keywords)
- Match corresponding terms between both sections
- Ignore all other content (abstract, body, references, etc.)

Output format - a JSON object with one field "terms" containing an array:
{{
  "terms": [
    {{"eng_term": "English keyword", "zh_term": "中文关键词"}},
    {{"eng_term": "another keyword", "zh_term": "另一个关键词"}}
  ]
}}

Text to analyze:
{text}
"""
    else:
        return """
Your response must contain only a JSON object with no additional text.

Task: Extract ONLY terms from the "Keywords" or "关键词" section. Ignore all other content.

Output format - a JSON object with one field "terms" containing an array:
{{
  "terms": [
    {{"term": "keyword1"}},
    {{"term": "keyword2"}}
  ]
}}

Text to analyze:
{text}
"""


# =============================================================================
# 输出格式配置
# =============================================================================

OUTPUT_FORMATS = {
    "json": {
        "extension": ".json",
        "description": "JSON格式，保留完整结构信息"
    },
    "csv": {
        "extension": ".csv", 
        "description": "CSV格式，便于Excel处理"
    },
    "excel": {
        "extension": ".xlsx",
        "description": "Excel格式，带样式和统计信息"
    },
    "tbx": {
        "extension": ".tbx",
        "description": "TBX格式，术语管理标准XML格式"
    },
    "txt": {
        "extension": ".txt",
        "description": "纯文本格式，便于阅读"
    }
}

# =============================================================================
# 文件处理配置
# =============================================================================

# 支持的输入文件格式
SUPPORTED_INPUT_FORMATS = [".txt", ".json", ".csv", ".md"]

# 智能文本分割配置
TEXT_SPLITTING = {
    "default_chunk_size": 12000,  # 默认块大小（字符）- 约3K tokens，为输出预留空间
    "default_overlap_size": 800,  # 默认重叠大小（字符）
    "min_chunk_size": 1000,  # 最小块大小（字符）
    "max_chunk_size": 400000,  # 最大块大小（字符）- 约100K tokens，预留28K给输出和提示词
    "min_overlap_size": 100,  # 最小重叠大小（字符）
    "max_overlap_ratio": 0.1,  # 最大重叠比例
    "enable_whole_document_mode": True,  # 启用整文档模式选项
    "whole_document_threshold": 300000,  # 小于此字符数时可选择整文档处理（约75K tokens）
}

# =============================================================================
# 术语处理配置
# =============================================================================

TERM_PROCESSING = {
    "enable_deduplication": True,  # 启用术语去重
    "case_sensitive_matching": False,  # 术语匹配是否区分大小写
    "max_merged_contexts": 3,  # 最多合并的上下文数量
    "max_merged_definitions": 3,  # 最多合并的定义数量
    "min_context_length": 20,  # 最小上下文长度（过滤太短的上下文）
    "min_definition_length": 10,  # 最小定义长度
    
    # 术语质量控制
    "quality_controls": {
        "min_term_length": 2,  # 最小术语长度
        "max_term_length": 100,  # 最大术语长度
        "exclude_generic_words": [  # 排除的通用词汇
            "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"
        ],
        "required_categories": [  # 必须的分类列表（严格单一分类）
            "Aircraft & Platforms", "Weapons & Munitions", "Avionics & Electronics",
            "Flight Systems & Controls", "Weapons Integration", "Guidance & Navigation",
            "Safety & Security", "Testing & Operations", "Personnel & Organization",
            "Technical Components"
        ],
        "professional_indicators": [  # 专业术语指示词
            "system", "unit", "component", "device", "equipment", "platform", "weapon",
            "missile", "aircraft", "radar", "sensor", "navigation", "guidance", "control"
        ],
        "deduplication_rules": {  # 去重规则
            "merge_similar_terms": True,  # 合并相似术语
            "prefer_full_forms": True,  # 优先完整形式
            "standardize_abbreviations": True  # 标准化缩写
        }
    }
}

# =============================================================================
# 文件处理参数
# =============================================================================

FILE_PROCESSING = {
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "encoding": "utf-8",
    "supported_pdf_extractors": ["pdfplumber", "pymupdf", "pdfminer"],
    "supported_doc_extractors": ["python-docx", "docx2txt"],
    "fallback_encoding": ["gbk", "gb2312", "latin1"],
}

# =============================================================================
# 日志配置
# =============================================================================

LOGGING_CONFIG = {
    "level": "INFO",  # 日志级别: DEBUG/INFO/WARNING/ERROR (调试时可改为DEBUG)
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_enabled": True,  # 是否启用文件日志
    "console_enabled": True,  # 是否启用控制台输出
    "file_rotation": {
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
}

# 快速切换到DEBUG模式（开发/调试时取消下面的注释）
# LOGGING_CONFIG["level"] = "DEBUG"

# =============================================================================
# 验证和工具函数
# =============================================================================

def validate_config() -> bool:
    """
    验证配置有效性
    
    Returns:
        bool: 配置是否有效
    """
    # 检查API密钥
    if OPENAI_API_KEY == "your-openai-api-key-here":
        print("警告: 请设置正确的OpenAI API密钥")
        return False
    
    # 检查模型配置
    if not DEFAULT_MODEL:
        print("错误: 未设置默认模型")
        return False
    
    # 检查批处理配置
    required_batch_keys = ["temperature", "max_output_tokens", "max_concurrent"]
    for key in required_batch_keys:
        if key not in BATCH_CONFIG:
            print(f"错误: 批处理配置缺少必要参数: {key}")
            return False
    
    # 检查文本分割配置
    if TEXT_SPLITTING["default_chunk_size"] > TEXT_SPLITTING["max_chunk_size"]:
        print("错误: 默认块大小不能大于最大块大小")
        return False
    
    return True
def get_model_info(model: str) -> Dict[str, Any]:
    """
    获取模型信息
    
    Args:
        model: 模型名称
        
    Returns:
        Dict: 模型信息字典
    """
    return {
        "name": model,
        "token_param": get_token_param_name(model),
        "is_new_model": any(new_model.lower() in model.lower() 
                           for new_model in MODEL_API_PARAMS["new_models"]),
        "max_context": 128000 if "gpt-4" in model.lower() else 4096,
    }

def get_supported_formats() -> List[str]:
    """
    获取支持的文件格式列表
    
    Returns:
        List[str]: 支持的文件扩展名列表
    """
    return SUPPORTED_INPUT_FORMATS + [".pdf", ".docx", ".doc"]

def get_processing_stats() -> Dict[str, Any]:
    """
    获取处理统计信息
    
    Returns:
        Dict: 统计信息字典
    """
    return {
        "supported_formats": len(get_supported_formats()),
        "default_chunk_size": TEXT_SPLITTING["default_chunk_size"],
        "max_concurrent": BATCH_CONFIG["max_concurrent"],
        "quality_controls_enabled": len(TERM_PROCESSING["quality_controls"]),
    }

# =============================================================================
# 配置验证和初始化
# =============================================================================

if __name__ == "__main__":
    # 配置验证
    if validate_config():
        print("✅ 配置验证通过")
        print(f"默认模型: {DEFAULT_MODEL}")
        print(f"Token参数: {get_token_param_name(DEFAULT_MODEL)}")
        
        # 显示配置摘要
        stats = get_processing_stats()
        print(f"支持格式: {stats['supported_formats']} 种")
        print(f"默认块大小: {stats['default_chunk_size']:,} 字符")
        print(f"最大并发: {stats['max_concurrent']}")
    else:
        print("❌ 配置验证失败")
        exit(1)

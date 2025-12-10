#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件类型检测和文本提取模块
支持多种文件格式的智能检测和文本提取，包括PDF、DOCX、图片OCR等
"""

import os
import logging
import importlib.util
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Union

# 配置日志
logger = logging.getLogger(__name__)

# =============================================================================
# 依赖检查和导入
# =============================================================================

class DependencyManager:
    """依赖管理器"""
    
    def __init__(self):
        self.available_modules = {}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """检查可选依赖"""
        # PDF处理 - 使用pdfminer.six + PyPDF2备用
        if importlib.util.find_spec('pdfminer'):
            self.available_modules['pdf'] = ['pdfminer.six']
        elif importlib.util.find_spec('PyPDF2'):
            self.available_modules['pdf'] = ['PyPDF2']
        else:
            self.available_modules['pdf'] = []
        
        # DOCX处理
        if importlib.util.find_spec('docx'):
            self.available_modules['docx'] = ['python-docx']
        else:
            self.available_modules['docx'] = []
        
        # 文件类型检测
        if importlib.util.find_spec('magic'):
            self.available_modules['magic'] = ['python-magic']
        else:
            self.available_modules['magic'] = []

        self._log_dependencies()
    
    def _log_dependencies(self):
        """记录依赖状态"""
        for module, deps in self.available_modules.items():
            if deps:
                logger.info(f"✅ {module.upper()} 支持: {', '.join(deps)}")
            else:
                logger.warning(f"⚠️  {module.upper()} 不可用")
    
    def is_available(self, module: str) -> bool:
        """检查模块是否可用"""
        return bool(self.available_modules.get(module, []))


# 全局依赖管理器
deps = DependencyManager()


# =============================================================================
# 文件类型检测
# =============================================================================

class FileTypeDetector:
    """文件类型检测器"""
    
    # 支持的MIME类型映射
    SUPPORTED_TYPES = {
        'text': ['text/plain', 'text/html', 'text/xml', 'application/xml'],
        'pdf': ['application/pdf'],
        'docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        'doc': ['application/msword'],
        'image': ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp', 'image/gif']
    }
    
    @staticmethod
    def detect_file_type(file_path: str) -> Tuple[str, str]:
        """
        检测文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[str, str]: (文件类型, MIME类型)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 首先尝试使用python-magic
        if deps.is_available('magic'):
            try:
                import magic
                mime_type = magic.from_file(file_path, mime=True)
                return FileTypeDetector._categorize_mime_type(mime_type), mime_type
            except Exception as e:
                logger.warning(f"Magic检测失败: {e}")
        
        # 回退到基于扩展名的检测
        return FileTypeDetector._detect_by_extension(file_path)
    
    @staticmethod
    def _detect_by_extension(file_path: str) -> Tuple[str, str]:
        """基于文件扩展名检测类型"""
        ext = Path(file_path).suffix.lower()
        
        # 扩展名映射
        extension_map = {
            '.txt': ('text', 'text/plain'),
            '.md': ('text', 'text/markdown'),
            '.html': ('text', 'text/html'),
            '.xml': ('text', 'application/xml'),
            '.pdf': ('pdf', 'application/pdf'),
            '.docx': ('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            '.doc': ('doc', 'application/msword'),
            '.jpg': ('image', 'image/jpeg'),
            '.jpeg': ('image', 'image/jpeg'),
            '.png': ('image', 'image/png'),
            '.tiff': ('image', 'image/tiff'),
            '.bmp': ('image', 'image/bmp'),
            '.gif': ('image', 'image/gif'),
        }
        
        return extension_map.get(ext, ('unknown', 'application/octet-stream'))
    
    @staticmethod
    def _categorize_mime_type(mime_type: str) -> str:
        """根据MIME类型分类"""
        for category, mime_list in FileTypeDetector.SUPPORTED_TYPES.items():
            if mime_type in mime_list:
                return category
        return 'unknown'


# =============================================================================
# 文本提取器
# =============================================================================

class TextExtractor:
    """文本提取器基类"""
    
    def extract(self, file_path: str) -> List[str]:
        """提取文本的抽象方法"""
        raise NotImplementedError


class PlainTextExtractor(TextExtractor):
    """纯文本提取器"""
    
    def extract(self, file_path: str) -> List[str]:
        """提取纯文本文件内容"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                    if content:
                        logger.info(f"成功使用 {encoding} 编码读取文件")
                        return [content]
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"读取文件失败: {e}")
                break
        
        raise ValueError(f"无法读取文件 {file_path}，尝试了所有编码")


class PDFExtractor(TextExtractor):
    """PDF文本提取器 - 纯文本提取（不支持扫描版PDF）"""

    def __init__(self, dependencies: DependencyManager):
        """初始化PDF提取器"""
        self.deps = dependencies
        logger.debug("PDFExtractor初始化: 纯文本提取模式")
    
    def extract(self, file_path: str) -> List[str]:
        """
        提取PDF文件内容（仅支持可复制文本的PDF）

        注意: 不支持扫描版PDF，请使用文字版PDF文件
        """
        if not deps.is_available('pdf'):
            raise RuntimeError("PDF处理库不可用，请安装 pdfminer.six")

        logger.info(f"📄 提取PDF文本: {Path(file_path).name}")

        # 优先使用pdfminer.six
        if 'pdfminer.six' in deps.available_modules['pdf']:
            return self._extract_with_pdfminer(file_path)
        else:
            # 备用方案：PyPDF2
            return self._extract_with_pypdf2(file_path)

    def _extract_with_pdfminer(self, file_path: str) -> List[str]:
        """使用pdfminer.six提取PDF文本"""
        try:
            from pdfminer.high_level import extract_text
            from pdfminer.layout import LAParams
            from pathlib import Path
            import re

            # 优化的布局参数（学术文档专用）
            laparams = LAParams(
                line_overlap=0.5,
                char_margin=2.0,
                line_margin=0.5,
                word_margin=0.3,  # 确保单词正确分离
                boxes_flow=0.5,
                detect_vertical=True,
                all_texts=True
            )

            full_text = extract_text(file_path, laparams=laparams)

            # 检查提取的文本质量
            text_stripped = full_text.strip() if full_text else ""

            # 如果提取失败就直接报错
            if not full_text or not text_stripped:
                raise ValueError(
                    f"❌ PDF文本提取失败或内容为空\n"
                    f"   文件: {Path(file_path).name}\n"
                    f"   可能原因: 扫描版PDF（不支持）、加密PDF、损坏文件\n"
                    f"   建议: 使用可复制文本的PDF文件"
                )
            elif len(text_stripped) < 50:
                raise ValueError(
                    f"❌ PDF文本提取内容过少（{len(text_stripped)}字符）\n"
                    f"   文件: {Path(file_path).name}\n"
                    f"   可能原因: 扫描版PDF（不支持）\n"
                    f"   建议: 使用可复制文本的PDF文件"
                )

            # 智能文本后处理
            full_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', full_text)  # 小写后跟大写
            full_text = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', full_text)  # 连续大写后跟单词
            full_text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', full_text)  # 数字后跟字母
            full_text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', full_text)  # 字母后跟数字
            full_text = re.sub(r'\s+', ' ', full_text)  # 清理多余空格

            # 返回处理后的文本
            texts = [full_text.strip()]
            logger.info(f"✅ 成功提取PDF文本: {len(full_text)} 字符")
            return texts

        except Exception as e:
            logger.error(f"❌ pdfminer.six提取失败: {e}")

            # 尝试PyPDF2备用
            if 'PyPDF2' in deps.available_modules['pdf']:
                logger.info("尝试使用PyPDF2备用方案...")
                return self._extract_with_pypdf2(file_path)

            raise ValueError(f"PDF文件处理失败: {str(e)}")

    def _extract_with_pypdf2(self, file_path: str) -> List[str]:
        """使用PyPDF2提取PDF文本（备用方法）"""
        try:
            import PyPDF2

            texts = []
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for i, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text()
                        if text and text.strip():
                            # 简单的文本后处理
                            import re
                            text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
                            text = re.sub(r'([A-Z]{2,})([A-Z][a-z])', r'\1 \2', text)
                            text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)
                            text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)
                            text = re.sub(r'\s+', ' ', text)
                            texts.append(text.strip())
                    except Exception as e:
                        logger.warning(f"第{i}页提取失败: {e}")
                        continue
            
            if not texts:
                raise ValueError("PDF文件为空或无法提取文本")
            
            logger.info(f"使用PyPDF2成功提取 {len(texts)} 页")
            return texts
            
        except Exception as e:
            logger.error(f"PyPDF2提取失败: {e}")
            raise ValueError(f"PDF文件处理失败: {e}")
    
    def extract_with_custom_params(self, file_path: str, **custom_params) -> List[str]:
        """使用自定义参数提取PDF文本"""
        # 临时更新参数
        original_params = self.layout_params.copy()
        self.layout_params.update(custom_params)
        
        try:
            return self.extract(file_path)
        finally:
            # 恢复原始参数
            self.layout_params = original_params


class DOCXExtractor(TextExtractor):
    """DOCX文档提取器"""
    
    def extract(self, file_path: str) -> List[str]:
        """提取DOCX文件内容"""
        if not deps.is_available('docx'):
            raise RuntimeError("DOCX处理库不可用，请安装 python-docx")
        
        try:
            from docx import Document
            
            doc = Document(file_path)
            paragraphs = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    paragraphs.append(text)
            
            if not paragraphs:
                raise ValueError("DOCX文件为空或无文本内容")
            
            # 将段落合并为完整文档
            full_text = '\n\n'.join(paragraphs)
            logger.info(f"成功提取DOCX文档，共 {len(paragraphs)} 个段落")
            
            return [f"[DOCX文档]\n{full_text}"]
            
        except Exception as e:
            logger.error(f"DOCX提取失败: {e}")
            raise ValueError(f"DOCX文件处理失败: {e}")


# =============================================================================
# 主文件处理器
# =============================================================================

class FileProcessor:
    """统一文件处理器（轻量版 - 仅支持文字版PDF）"""

    def __init__(self):
        """初始化文件处理器"""
        self.deps = DependencyManager()
        self.extractors = self._init_extractors()

    def _init_extractors(self) -> Dict[str, TextExtractor]:
        """初始化提取器"""
        extractors = {
            'text': PlainTextExtractor(),
        }

        # PDF提取器（纯文本提取模式）
        if self.deps.is_available('pdf'):
            logger.info("📄 初始化PDF提取器: 纯文本提取模式")
            extractors['pdf'] = PDFExtractor(self.deps)

        # DOCX文档提取器
        if self.deps.is_available('docx'):
            extractors['docx'] = DOCXExtractor()
            extractors['doc'] = DOCXExtractor()  # 使用相同的提取器

        logger.info(f"📦 文件处理器初始化完成: 支持 {len(extractors)} 种文件类型")
        return extractors
    
    def process_file(self, file_path: str) -> Tuple[str, List[str]]:
        """
        处理文件并提取文本
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[str, List[str]]: (文件类型, 提取的文本列表)
        """
        try:
            # 检测文件类型
            file_type, mime_type = FileTypeDetector.detect_file_type(file_path)
            logger.info(f"检测到文件类型: {file_type} ({mime_type})")
            
            # 获取对应的提取器
            extractor = self.extractors.get(file_type)
            if not extractor:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            # 提取文本
            texts = extractor.extract(file_path)
            
            # 验证结果
            if not texts or not any(text.strip() for text in texts):
                raise ValueError("文件中未提取到有效文本")
            
            logger.info(f"成功处理文件 {Path(file_path).name}: {len(texts)} 个文本块")
            return file_type, texts
            
        except Exception as e:
            logger.error(f"文件处理失败 {file_path}: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式列表"""
        formats = ['txt', 'md', 'html', 'xml']  # 基础文本格式
        
        if 'pdf' in self.extractors:
            formats.append('pdf')
        
        if 'docx' in self.extractors:
            formats.extend(['docx', 'doc'])
        
        if 'image' in self.extractors:
            formats.extend(['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif'])
        
        return formats
    
    def get_processor_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return {
            "supported_formats": self.get_supported_formats(),
            "available_extractors": list(self.extractors.keys()),
            "dependencies": deps.available_modules,
            "ocr_enabled": 'image' in self.extractors,
        }
    
    # =============================================================================
    # 便捷方法（保持向后兼容）
    # =============================================================================
    
    def extract_text_file(self, file_path: str) -> List[str]:
        """提取文本文件（向后兼容）"""
        file_type, texts = self.process_file(file_path)
        return texts
    
    def extract_pdf_text(self, file_path: str) -> List[str]:
        """提取PDF文本（向后兼容）"""
        if 'pdf' not in self.extractors:
            raise RuntimeError("PDF处理器不可用")
        return self.extractors['pdf'].extract(file_path)
    
    def extract_docx_text(self, file_path: str) -> List[str]:
        """提取DOCX文本（向后兼容）"""
        if 'docx' not in self.extractors:
            raise RuntimeError("DOCX处理器不可用")
        return self.extractors['docx'].extract(file_path)
    
    def extract_image_text(self, file_path: str) -> List[str]:
        """提取图片文本（向后兼容）"""
        if 'image' not in self.extractors:
            raise RuntimeError("OCR处理器不可用")
        return self.extractors['image'].extract(file_path)


# =============================================================================
# 工具函数
# =============================================================================

def create_file_processor(tesseract_path: Optional[str] = None) -> FileProcessor:
    """
    创建文件处理器实例
    
    Args:
        tesseract_path: Tesseract路径
        
    Returns:
        FileProcessor: 文件处理器实例
    """
    return FileProcessor(tesseract_path)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict: 文件信息
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    file_type, mime_type = FileTypeDetector.detect_file_type(file_path)
    
    return {
        "name": path.name,
        "size": path.stat().st_size,
        "extension": path.suffix,
        "type": file_type,
        "mime_type": mime_type,
        "is_supported": file_type in ['text', 'pdf', 'docx', 'doc', 'image'],
    }


if __name__ == "__main__":
    # 简单测试
    processor = create_file_processor()
    info = processor.get_processor_info()
    
    print("文件处理器信息:")
    print(f"支持格式: {info['supported_formats']}")
    print(f"可用提取器: {info['available_extractors']}")
    print(f"OCR功能: {'启用' if info['ocr_enabled'] else '禁用'}")
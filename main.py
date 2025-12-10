#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI GPT批处理术语抽取 - 主程序
提供简单的命令行界面和快速配置选项
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

# 导入我们的模块
try:
    from gpt_processor import GPTProcessor, load_texts_from_file
    from config import (
        OPENAI_API_KEY, OPENAI_BASE_URL, BATCH_CONFIG,
        SYSTEM_PROMPT, get_user_prompt, TEXT_SPLITTING
    )
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有必要的文件都在当前目录中")
    sys.exit(1)


class TermExtractionApp:
    """术语抽取应用类"""
    
    def __init__(self):
        self.api_key = None
        self.processor = None
        
    # =============================================================================
    # API密钥管理
    # =============================================================================
    
    def setup_api_key(self) -> bool:
        """设置API密钥"""
        # 优先级: 命令行参数 > 环境变量 > 配置文件 > 用户输入
        if self.api_key:
            return True
            
        # 检查环境变量
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key and env_key != "your-openai-api-key-here":
            self.api_key = env_key
            return True
            
        # 检查配置文件
        if OPENAI_API_KEY != "your-openai-api-key-here":
            self.api_key = OPENAI_API_KEY
            return True
            
        # 用户输入
        return self._prompt_for_api_key()
    
    def _prompt_for_api_key(self) -> bool:
        """提示用户输入API密钥"""
        print("🔑 请输入您的OpenAI API密钥:")
        print("   您可以在 https://platform.openai.com/api-keys 获取API密钥")
        api_key = input("API密钥: ").strip()
        
        if api_key:
            self.api_key = api_key
            
            # 询问是否保存到环境变量
            save_env = input("是否保存到环境变量? (y/N): ").strip().lower()
            if save_env in ['y', 'yes', '是']:
                print(f"请在您的shell配置文件中添加:")
                print(f"export OPENAI_API_KEY='{api_key}'")
            
            return True
        
        print("❌ 未提供API密钥")
        return False
    
    # =============================================================================
    # 输入处理
    # =============================================================================
    
    def get_input_texts(self) -> List[str]:
        """获取输入文本"""
        print("\n📝 请选择输入方式:")
        print("1. 从文件读取")
        print("2. 直接输入文本")
        print("3. 使用示例文本")
        
        while True:
            choice = input("选择方式 (1-3): ").strip()
            
            if choice == "1":
                return self._load_from_file()
            elif choice == "2":
                return self._input_texts_directly()
            elif choice == "3":
                return self._use_sample_texts()
            else:
                print("❌ 无效选择，请重试")
    
    def _input_texts_directly(self) -> List[str]:
        """直接输入文本"""
        texts = []
        print("\n✏️ 请输入文本 (每行一个，输入空行结束):")
        
        while True:
            text = input().strip()
            if not text:
                break
            texts.append(text)
        
        if not texts:
            print("❌ 未输入任何文本")
        else:
            print(f"✅ 输入了 {len(texts)} 个文本")
        
        return texts
    
    def _use_sample_texts(self) -> List[str]:
        """使用示例文本"""
        sample_texts = [
            "BWB-UCAV模型采用翼身融合体构型，在低速风洞试验中测得升阻比为12.5，失速攻角为18°。",
            "通过PIV粒子图像测速技术和CFD计算流体力学仿真，分析了不同攻角下的流场特征和压力分布。",
            "复合材料蜂窝夹芯结构具有高比强度和比刚度，CFRP碳纤维增强塑料广泛应用于航空器主承力结构。",
            "飞行器采用先进的飞控系统FCS，集成了GPS全球定位系统和INS惯性导航系统，实现自主飞行。",
            "风洞试验采用六分量天平测量气动力和力矩，雷诺数Re为2.4×10^6，马赫数Ma为0.3。"
        ]
        
        print(f"✅ 使用 {len(sample_texts)} 个示例文本")
        return sample_texts
    
    # =============================================================================
    # 文件处理
    # =============================================================================
    
    def _load_from_file(self) -> List[str]:
        """从文件加载文本 - 默认处理file preparation文件夹中的所有文件"""
        prep_files = self._scan_preparation_folder()
        
        if prep_files:
            return self._handle_preparation_files(prep_files)
        else:
            print(f"\n📁 'file preparation' 文件夹为空或不存在")
            print("💡 建议将要处理的文件放入 'file preparation' 文件夹中")
            return self._select_from_other_locations()
    
    def _scan_preparation_folder(self) -> List[Path]:
        """扫描file preparation文件夹"""
        prep_dir = Path("file preparation")
        supported_extensions = ["*.txt", "*.pdf", "*.docx", "*.doc", "*.md", "*.csv"]
        
        prep_files = []
        if prep_dir.exists():
            for ext in supported_extensions:
                prep_files.extend(prep_dir.glob(ext))
        
        return prep_files
    
    def _handle_preparation_files(self, prep_files: List[Path]) -> List[str]:
        """处理preparation文件夹中的文件"""
        self._display_file_list(prep_files, "file preparation")
        
        print("\n🔄 处理选项:")
        print("1. 处理所有文件 (推荐)")
        print("2. 选择单个文件")
        print("3. 选择其他位置的文件")
        
        while True:
            choice = input("选择处理方式 (1-3): ").strip()
            
            if choice == "1":
                return self._process_multiple_files(prep_files)
            elif choice == "2":
                return self._select_single_file(prep_files)
            elif choice == "3":
                return self._select_from_other_locations()
            else:
                print("❌ 无效选择，请重试")
    
    def _display_file_list(self, files: List[Path], location: str):
        """显示文件列表"""
        print(f"\n📁 在 '{location}' 中找到 {len(files)} 个文件:")
        total_size = 0
        
        for i, file in enumerate(files, 1):
            file_size = file.stat().st_size
            total_size += file_size
            size_str = self._format_file_size(file_size)
            file_type = file.suffix.upper()
            print(f"  {i}. {file.name} {size_str} [{file_type}]")
        
        total_size_str = self._format_file_size(total_size)
        print(f"\n📊 总计: {len(files)} 个文件，{total_size_str}")
    
    def _format_file_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"({size} bytes)"
        elif size < 1024 * 1024:
            return f"({size/1024:.1f} KB)"
        else:
            return f"({size/(1024*1024):.1f} MB)"
    
    def _process_multiple_files(self, files: List[Path]) -> List[str]:
        """处理多个文件"""
        all_texts = []
        
        # 获取分割配置
        chunk_size, use_smart_splitter, overlap_size = self._get_splitting_config()
        
        print(f"\n🔄 开始处理 {len(files)} 个文件...")
        
        for i, file_path in enumerate(files, 1):
            try:
                print(f"\n📄 处理文件 {i}/{len(files)}: {file_path.name}")
                texts = self._process_single_file_content(
                    file_path, chunk_size, use_smart_splitter, overlap_size
                )
                all_texts.extend(texts)
                print(f"  ✅ 成功提取 {len(texts)} 个文本块")
                
            except Exception as e:
                print(f"  ❌ 处理文件 {file_path.name} 失败: {e}")
                continue
        
        print(f"\n✅ 批量处理完成！总共获得 {len(all_texts)} 个文本块")
        return all_texts
    
    def _select_single_file(self, files: List[Path]) -> List[str]:
        """选择单个文件处理"""
        print("\n📋 请选择要处理的文件:")
        for i, file in enumerate(files, 1):
            file_size = file.stat().st_size
            size_str = self._format_file_size(file_size)
            print(f"{i}. {file.name} {size_str}")
        
        while True:
            try:
                choice = input("选择文件 (输入编号): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    file_path = files[idx]
                    break
                else:
                    print("❌ 无效编号")
            except ValueError:
                print("❌ 请输入数字")
        
        return self._process_single_file(file_path)
    
    def _select_from_other_locations(self) -> List[str]:
        """从其他位置选择文件"""
        supported_files = self._scan_other_locations()
        
        if supported_files:
            self._display_file_list(supported_files, "其他位置")
            
            while True:
                try:
                    choice = input("选择文件 (输入编号): ").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(supported_files):
                        file_path = supported_files[idx]
                        break
                    else:
                        print("❌ 无效编号")
                except ValueError:
                    print("❌ 请输入数字")
        else:
            file_path = Path(input("请输入文件路径: ").strip())
        
        return self._process_single_file(file_path)
    
    def _scan_other_locations(self) -> List[Path]:
        """扫描其他位置的文件"""
        supported_files = []
        supported_extensions = ["*.txt", "*.pdf", "*.docx", "*.doc", "*.md", "*.csv"]
        
        # 检查extracted_texts目录
        extracted_dir = Path("extracted_texts")
        if extracted_dir.exists():
            for ext in supported_extensions:
                supported_files.extend(extracted_dir.glob(ext))
        
        # 检查当前目录的支持文件
        for ext in supported_extensions:
            current_files = list(Path(".").glob(ext))
            # 排除file preparation文件夹中的文件
            for file in current_files:
                if not str(file).startswith("file preparation"):
                    supported_files.append(file)
        
        return supported_files
    
    # =============================================================================
    # 文本分割配置
    # =============================================================================
    
    def _get_splitting_config(self) -> Tuple[Optional[int], bool, int]:
        """获取文本分割配置"""
        print("\n📝 文本分割配置:")
        print("1. 智能分割 (推荐) - 按段落和语义边界分割")
        print("2. 整文档处理 - 利用128K上下文处理完整文档")
        print("3. 按段落处理 - 适合短文本或单行术语")
        
        while True:
            choice = input("选择分割方式 (1-3, 默认1): ").strip() or "1"
            if choice in ["1", "2", "3"]:
                break
            print("❌ 无效选择，请重试")
        
        if choice == "1":
            return self._get_smart_splitting_config()
        elif choice == "2":
            return self._get_whole_document_config()
        else:
            return None, False, 0  # 按段落处理
    
    def _get_smart_splitting_config(self) -> Tuple[int, bool, int]:
        """获取智能分割配置"""
        default_chunk = TEXT_SPLITTING["default_chunk_size"]
        default_overlap = TEXT_SPLITTING["default_overlap_size"]
        min_chunk = TEXT_SPLITTING["min_chunk_size"]
        max_chunk = TEXT_SPLITTING["max_chunk_size"]
        
        # 获取块大小
        while True:
            try:
                chunk_size = int(input(
                    f"请输入块大小 (字符数, {min_chunk}-{max_chunk}, 默认{default_chunk}): "
                ) or str(default_chunk))
                
                if chunk_size < min_chunk:
                    print(f"⚠️  块大小过小，建议至少{min_chunk}字符")
                    continue
                if chunk_size > max_chunk:
                    print(f"⚠️  块大小过大，建议不超过{max_chunk}字符")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效数字")
        
        # 获取重叠大小
        while True:
            try:
                overlap_size = int(input(
                    f"请输入重叠大小 (字符数, 默认{default_overlap}): "
                ) or str(default_overlap))
                
                max_overlap = int(chunk_size * TEXT_SPLITTING["max_overlap_ratio"])
                if overlap_size >= chunk_size:
                    print("⚠️  重叠大小不能大于等于块大小")
                    continue
                if overlap_size > max_overlap:
                    ratio_percent = int(TEXT_SPLITTING['max_overlap_ratio'] * 100)
                    print(f"⚠️  重叠大小过大，不应超过块大小的{ratio_percent}% ({max_overlap}字符)")
                    continue
                break
            except ValueError:
                print("❌ 请输入有效数字")
        
        return chunk_size, True, overlap_size
    
    def _get_whole_document_config(self) -> Tuple[int, bool, int]:
        """获取整文档处理配置"""
        threshold = TEXT_SPLITTING.get("whole_document_threshold", 300000)
        print(f"\n🔄 整文档模式:")
        print(f"   • 适用于 ≤ {threshold:,} 字符的文档 (约{threshold//4000:.0f}K tokens)")
        print(f"   • 利用模型的128K总上下文")
        print(f"   • 预留28K tokens给提示词和输出")
        print(f"   • 一次性处理完整文档，减少信息丢失")
        return threshold, True, 0  # 整文档模式，无重叠
    
    # =============================================================================
    # 文件处理核心逻辑
    # =============================================================================
    
    def _process_single_file(self, file_path: Path) -> List[str]:
        """处理单个文件"""
        chunk_size, use_smart_splitter, overlap_size = self._get_splitting_config()
        return self._process_single_file_content(
            file_path, chunk_size, use_smart_splitter, overlap_size
        )
    
    def _process_single_file_content(
        self,
        file_path: Path,
        chunk_size: Optional[int],
        use_smart_splitter: bool,
        overlap_size: int
    ) -> List[str]:
        """处理单个文件内容"""
        try:
            texts = load_texts_from_file(
                str(file_path),
                chunk_size=chunk_size,
                use_smart_splitter=use_smart_splitter,
                overlap_size=overlap_size
            )
            
            # 智能分割器已经在内部添加了文件标识，这里不需要重复添加
            if use_smart_splitter and chunk_size:
                return texts
            else:
                # 为简单分割添加来源标识
                return self._add_file_labels(texts, file_path.name)
                
        except Exception as e:
            print(f"❌ 加载文件失败: {e}")
            return []
    
    def _add_file_labels(self, texts: List[str], filename: str) -> List[str]:
        """为文本添加文件标签"""
        file_texts = []
        for j, text in enumerate(texts, 1):
            if len(texts) > 1:
                labeled_text = f"[文件: {filename} - 第{j}部分]\n{text}"
            else:
                labeled_text = f"[文件: {filename}]\n{text}"
            file_texts.append(labeled_text)
        return file_texts
    
    # =============================================================================
    # 输出配置
    # =============================================================================
    
    def select_output_format(self) -> str:
        """选择输出格式"""
        formats = {
            "1": "json",
            "2": "csv", 
            "3": "excel",
            "4": "tbx",
            "5": "txt"
        }
        
        print("\n📊 请选择输出格式:")
        print("1. JSON (结构化数据)")
        print("2. CSV (表格数据)")
        print("3. Excel (带样式和统计信息)")
        print("4. TBX (术语管理标准XML格式)")
        print("5. TXT (纯文本)")
        
        while True:
            choice = input("选择格式 (1-5): ").strip()
            if choice in formats:
                return formats[choice]
            print("❌ 无效选择，请重试")
    
    def select_model(self) -> str:
        """选择模型"""
        from config import DEFAULT_MODEL
        print(f"\n🤖 使用模型: {DEFAULT_MODEL}")
        return DEFAULT_MODEL
    
    def select_extraction_mode(self) -> bool:
        """选择术语提取模式（单语/双语）"""
        print("\n🌐 请选择术语提取模式:")
        print("1. 双语模式 (推荐) - 同时提取英文和中文术语")
        print("2. 单语模式 - 仅提取原文术语（中文文档提取中文，英文文档提取英文）")
        print("\n💡 提示:")
        print("  - 双语模式: 适合建立双语术语库、辅助翻译、学习材料")
        print("  - 单语模式: 适合快速提取、降低成本、保持原文格式")
        
        while True:
            choice = input("\n请选择 (1-2，默认1): ").strip() or "1"
            if choice == "1":
                print("✅ 已选择: 双语模式")
                return True  # bilingual=True
            elif choice == "2":
                print("✅ 已选择: 单语模式")
                return False  # bilingual=False
            else:
                print("❌ 无效选择，请输入1或2")
    
    def handle_output_generation(self, results: dict, source_files: List[str], model: str) -> List[str]:
        """
        处理输出文件生成，支持重复选择不同格式
        
        Args:
            results: 处理结果
            source_files: 源文件列表
            model: 使用的模型
            
        Returns:
            List[str]: 生成的文件路径列表
        """
        if not results or not results.get('merged_results'):
            print("❌ 没有可用的处理结果")
            return []
        
        merged_results = results['merged_results']
        generated_files = []
        
        # 提取元数据用于文件命名
        source_filename = self.processor._extract_source_filename(source_files)
        model_name = model.replace("-", "").replace(".", "")  # 清理模型名用于文件名
        total_terms = self.processor._count_total_terms(merged_results)
        
        print(f"\n🎉 术语抽取完成！")
        print(f"📊 共提取 {total_terms} 个术语")
        print(f"📁 来源文件: {source_filename}")
        
        while True:
            print("\n" + "="*50)
            output_format = self.select_output_format()
            
            try:
                # 生成指定格式的文件
                output_file = self.processor.save_processed_results(
                    merged_results, 
                    output_format,
                    source_filename,
                    model_name,
                    total_terms
                )
                
                generated_files.append(output_file)
                print(f"✅ {output_format.upper()}文件已生成: {output_file}")
                
            except Exception as e:
                print(f"❌ 生成{output_format.upper()}文件失败: {e}")
                continue
            
            # 询问是否继续生成其他格式
            print(f"\n📋 已生成的文件:")
            for i, file_path in enumerate(generated_files, 1):
                file_format = file_path.split('.')[-1].upper()
                print(f"  {i}. {file_format}格式: {file_path}")
            
            while True:
                continue_choice = input("\n是否生成其他格式的文件? (y/N): ").strip().lower()
                if continue_choice in ['y', 'yes', '是']:
                    break
                elif continue_choice in ['n', 'no', '否', '']:
                    return generated_files
                else:
                    print("❌ 请输入 y/yes/是 或 n/no/否")
        
        return generated_files
    
    # =============================================================================
    # 批处理执行
    # =============================================================================
    
    def _extract_source_files(self, texts: List[str]) -> List[str]:
        """从文本中提取来源文件名"""
        import re
        source_files = []
        
        for text in texts:
            # 查找文本开头的文件标识
            match = re.search(r'\[文件: ([^\]]+)\]', text)
            if match:
                filename = match.group(1)
                # 移除部分标识，只保留文件名
                filename = re.sub(r' - 第\d+部分$', '', filename)
                source_files.append(filename)
            else:
                source_files.append("")
        
        return source_files
    
    def run_batch_processing(
        self,
        texts: List[str],
        model: str,
        bilingual: bool = True
    ) -> Optional[dict]:
        """运行批处理（不包含输出格式,只进行抽取）"""
        if not self.processor:
            # 获取base_url配置
            base_url = os.getenv("OPENAI_BASE_URL", OPENAI_BASE_URL)
            self.processor = GPTProcessor(
                api_key=self.api_key,
                base_url=base_url
            )
        
        print(f"\n🚀 开始批处理任务")
        print(f"📝 文本数量: {len(texts)}")
        print(f"🤖 使用模型: {model}")
        print(f"🌐 提取模式: {'双语' if bilingual else '单语'}")
        print("-" * 50)
        
        try:
            # 提取来源文件信息
            source_files = self._extract_source_files(texts)
            
            # 获取用户提示词模板（传入bilingual参数）
            user_prompt_template = get_user_prompt("{text}", bilingual=bilingual)
            
            # 运行处理流程，但不保存最终结果
            results = self.processor.run_extraction_only(
                texts=texts,
                system_prompt=SYSTEM_PROMPT,
                user_prompt_template=user_prompt_template,
                model=model,
                temperature=BATCH_CONFIG["temperature"],
                max_tokens=BATCH_CONFIG["max_output_tokens"],
                max_concurrent=BATCH_CONFIG["max_concurrent"],
                description="军事航天术语抽取任务",
                source_files=source_files
            )
            
            return results
            
        except Exception as e:
            print(f"❌ 批处理失败: {e}")
            return None
    
    # =============================================================================
    # 主程序流程
    # =============================================================================
    
    def run(self):
        """运行主程序"""
        print("🎉 欢迎使用OpenAI GPT批处理术语抽取工具!")
        print("=" * 50)

        # 1. 设置API密钥
        if not self.setup_api_key():
            return

        print("✅ API密钥设置成功")

        # 2. 选择提取模式（单语/双语）
        bilingual = self.select_extraction_mode()

        # 3. 获取输入文本
        texts = self.get_input_texts()
        if not texts:
            print("❌ 没有输入文本，程序退出")
            return

        # 4. 选择模型
        model = self.select_model()
        print(f"✅ 选择模型: {model}")

        # 5. 运行批处理（只进行抽取，不保存最终结果）
        results = self.run_batch_processing(texts, model, bilingual)

        if results:
            # 6. 抽取完成后，选择输出格式并支持重复选择
            source_files = self._extract_source_files(texts)
            generated_files = self.handle_output_generation(results, source_files, model)

            if generated_files:
                print(f"\n🎉 所有处理完成!")
                print(f"📁 文件保存位置: batch_results/ 目录")
                print(f"📊 共生成 {len(generated_files)} 个文件")
            else:
                print("⚠️  未生成任何输出文件")

        else:
            print("❌ 批处理失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="OpenAI GPT批处理术语抽取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py                           # 交互式模式
  python main.py --api-key YOUR_KEY       # 指定API密钥
  python main.py --file sample.txt        # 指定输入文件
  python main.py --format csv             # 指定输出格式
        """
    )
    
    parser.add_argument("--api-key", help="OpenAI API密钥")
    parser.add_argument("--file", help="输入文件路径")
    parser.add_argument("--format", choices=["json", "csv", "txt"], 
                       default="json", help="输出格式")
    parser.add_argument("--model", help="使用的模型")
    parser.add_argument("--chunk-size", type=int, help="文本分块大小")
    
    args = parser.parse_args()
    
    # 创建应用实例
    app = TermExtractionApp()
    
    # 设置API密钥
    if args.api_key:
        app.api_key = args.api_key
    
    # 非交互模式
    if args.file:
        _run_non_interactive_mode(app, args)
    else:
        # 交互模式
        app.run()


def _run_non_interactive_mode(app: TermExtractionApp, args):
    """运行非交互模式"""
    print("🤖 非交互模式运行")
    
    # 设置API密钥
    if not app.setup_api_key():
        return
    
    # 加载文本
    try:
        # 使用默认配置：智能分割，如果没有指定chunk_size则按段落处理
        chunk_size = args.chunk_size or TEXT_SPLITTING["default_chunk_size"]
        texts = load_texts_from_file(
            args.file,
            chunk_size=chunk_size if args.chunk_size else None,
            use_smart_splitter=True,
            overlap_size=TEXT_SPLITTING["default_overlap_size"]
        )
        print(f"✅ 从文件加载了 {len(texts)} 个文本")
    except Exception as e:
        print(f"❌ 加载文件失败: {e}")
        return
    
    # 选择模型
    from config import DEFAULT_MODEL
    model = args.model or DEFAULT_MODEL
    
    # 运行批处理
    results = app.run_batch_processing(texts, args.format, model)
    
    if results:
        print("✅ 批处理完成!")
        for key, value in results.items():
            if value:
                print(f"  {key}: {value}")
    else:
        print("❌ 批处理失败")


if __name__ == "__main__":
    main()
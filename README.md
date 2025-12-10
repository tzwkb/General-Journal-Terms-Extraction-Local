# 🌐 General Journal Terms Extraction Tool

<div align="center">

**AI-Powered Bilingual Terminology Extraction System**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI GPT-5](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)
[![讯飞OCR](https://img.shields.io/badge/讯飞OCR-云端API-orange.svg)](https://www.xfyun.cn/)

</div>

---

## 🎯 核心特性

### ✨ v2.0 核心功能

- **🌐 双语术语提取** - 同时生成英文和中文术语对照（可选）
- **📑 智能分批** - 自动分批处理大型扫描版PDF（10页/10MB阈值），避免内存溢出
- **🔁 自动重试机制** - 批次失败时智能重试（最多3次），大幅提高OCR成功率
- **💾 实时保存** - OCR处理过程中实时保存中间结果，防止数据丢失
- **🎛️ 模式选择** - 用户可自由选择单语或双语模式

### 🚀 强大功能

#### 文档处理
- ✅ **智能PDF处理** - 基于pdfminer.six的高精度文本提取
- ✅ **智能分批处理** - 大型PDF（>10页或10MB）自动分批OCR，避免内存溢出
- ✅ **自动重试机制** - 批次失败时自动重试（最多3次），提高成功率
- ✅ **多格式支持** - PDF、DOCX、TXT、JSON、CSV、Markdown
- ✅ **智能文本分割** - 按语义边界分割，保持上下文完整

#### 术语提取
- ✅ **AI驱动** - GPT-4o专业术语识别
- ✅ **双语输出** - 英文+中文术语对照（可选单语模式）
- ✅ **缩写展开** - 自动提取缩写词完整形式
- ✅ **智能去重** - 基于双语组合的精准去重
- ✅ **领域优化** - 针对军事、航空航天、医疗、国防领域优化

#### 输出格式
- 📊 **JSON** - 结构化数据，便于程序处理
- 📋 **CSV** - 表格数据，Excel兼容（UTF-8-BOM）
- 📈 **Excel** - 带样式和统计信息的专业报表
- 🔤 **TXT** - 双语对照的纯文本格式
- 🏷️ **TBX** - 符合ISO 30042标准的术语交换格式（可导入CAT工具）

#### 工作流优化
- ✅ **并发处理** - 多线程并发提取，速度提升10倍
- ✅ **进度追踪** - 实时显示处理进度和预计时间
- ✅ **错误容错** - 单个批次失败不影响整体处理

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / Linux / macOS
- **OpenAI API Key**: 需要有效的API密钥
- **网络连接**: 需要稳定的网络连接
- **内存**: 建议4GB+（云端OCR，本地资源占用低）
- **磁盘空间**: 至少500MB（临时文件）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd "Term Extraction Tool_GPT"
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置API密钥

**OpenAI API（必需）**

方法1：环境变量（推荐）
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

方法2：配置文件
```python
# 编辑 config.py
OPENAI_API_KEY = "your-api-key-here"
OPENAI_BASE_URL = "https://api.openai.com/v1"  # 可选：自定义API端点
```

### 基本使用

#### 方式1：交互式模式（推荐）

```bash
python main.py
```

**交互流程：**

```
🎉 欢迎使用OpenAI GPT批处理术语抽取工具!

1. 选择输入方式
   ├─ 从文件读取 (推荐)
   ├─ 直接输入文本
   └─ 使用示例文本

2. 选择模型
   └─ 默认: gpt-4o

3. 选择提取模式 ⭐ 新功能
   ├─ 双语模式 (推荐) - 英文+中文对照
   └─ 单语模式 - 仅提取原文术语

4. 自动处理
   ├─ 检测文件类型
   ├─ 扫描版PDF自动OCR（科大讯飞云端）
   ├─ 大型PDF自动分批处理
   └─ 实时保存进度

5. 选择输出格式
   ├─ JSON / CSV / Excel
   ├─ TBX / TXT
   └─ 支持生成多种格式
```

#### 方式2：命令行模式

```bash
# 指定文件处理
python main.py --file document.pdf

# 自定义参数
python main.py --model gpt-4-turbo --format csv
```

---

## 📁 项目结构

```
Term Extraction Tool_GPT/
├── 📄 核心文件
│   ├── main.py                    # 主程序入口
│   ├── config.py                  # 配置文件（API、提示词、参数）
│   ├── gpt_processor.py           # GPT API处理和批处理
│   ├── file_processor.py          # 文件处理和OCR调度
│   └── text_splitter.py           # 智能文本分割
│
├── 📁 工作目录
    ├── file preparation/          # 📥 输入文档目录
    ├── extracted_texts/           # 📝 OCR提取的文本
    └── batch_results/             # 📊 术语提取结果

```

---

## 🌐 双语术语提取

### 输出格式对比

#### 双语模式（推荐）

**JSON格式：**
```json
{
  "terms": [
    {
      "eng_term": "Inertial Measurement Unit (IMU)",
      "zh_term": "惯性测量单元"
    },
    {
      "eng_term": "Global Positioning System (GPS)",
      "zh_term": "全球定位系统"
    }
  ]
}
```

**Excel格式：**

| 序号 | 英文术语 | 中文术语 | 来源文件 | 模型 |
|------|----------|----------|----------|------|
| 1 | Inertial Measurement Unit (IMU) | 惯性测量单元 | 词典.pdf | gpt-4o |
| 2 | Global Positioning System (GPS) | 全球定位系统 | 词典.pdf | gpt-4o |

#### 单语模式

**JSON格式：**
```json
{
  "terms": [
    {"term": "惯性测量单元 (IMU, Inertial Measurement Unit)"},
    {"term": "全球定位系统 (GPS, Global Positioning System)"}
  ]
}
```

### 适用场景

| 模式 | 适用场景 | 优势 |
|------|----------|------|
| **双语** | 建立双语术语库、辅助翻译、学习材料 | 完整对照、便于翻译 |
| **单语** | 快速提取、降低成本、保持原文 | 速度快、成本低 |

---


---

## 📑 智能分批处理

### 触发条件

对于扫描版PDF，当满足以下条件之一时自动启用分批处理：

- 📄 **页数** > 50页
- 💾 **文件大小** > 50MB

### 处理流程

```
检测大型PDF (238页, 105MB)
  ↓
自动分批 (每批20页)
  ↓
┌─────────────────────────────────┐
│ 批次1: 页1-20                    │
│ ├─ 分割PDF → 临时文件           │
│ ├─ OCR识别 (45秒)               │
│ ├─ 💾 保存到 xxx_batch_ocr.txt  │  ← 实时保存
│ └─ 清理临时文件                 │
├─────────────────────────────────┤
│ 批次2: 页21-40                   │
│ ├─ OCR识别 (42秒)               │
│ ├─ 💾 追加到 xxx_batch_ocr.txt  │  ← 实时追加
│ └─ ...                          │
├─────────────────────────────────┤
│ ...继续处理剩余批次              │
└─────────────────────────────────┘
  ↓
🎉 处理完成
  └─ 完整结果: extracted_texts/xxx_batch_ocr.txt
```

### 实时监控进度

处理过程中可以随时打开 `extracted_texts/` 目录查看：

```
extracted_texts/
  └── 英俄汉导航与运动控制词典_batch_ocr.txt
      ├── [批次 1: 页1-20]  ✅
      ├── [批次 2: 页21-40] ✅
      ├── [批次 3: 页41-60] ✅ 
      └── [批次 4: 页61-80] 🔄 处理中...
```

### 性能优化

**配置调整**（`config.py`）：

```python
PDF_OCR_CONFIG = {
    "batch_threshold_pages": 10,      # 触发阈值：页数（从50降低到10）
    "batch_threshold_mb": 10,         # 触发阈值：文件大小（从50MB降低到10MB）
    "batch_size": 10,                 # 每批处理页数（从20降低到10）
    "enable_batch_processing": True,  # 功能开关
    "max_retries": 3,                 # 单个批次失败时的最大重试次数
    "retry_delay": 2,                 # 重试之间的延迟（秒）
}
```

---

## 🎛️ 配置说明

### API设置

```python
# config.py

# API密钥配置
OPENAI_API_KEY = "your-api-key-here"
OPENAI_BASE_URL = "https://api.openai.com/v1"

# 模型选择
DEFAULT_MODEL = "gpt-4o"  # 推荐：高质量
# 可选: "gpt-4o-mini" (经济), "gpt-4-turbo" (平衡)
```

### 批处理参数

```python
BATCH_CONFIG = {
    "temperature": 0.1,              # 稳定性（0-1，越低越稳定）
    "max_output_tokens": 128000,     # 最大输出token
    "max_concurrent": 10,            # 并发请求数
    "requests_per_minute": 30,       # 速率限制
}
```

### 文本分割策略

```python
TEXT_SPLITTING = {
    "default_chunk_size": 12000,       # 每块字符数
    "default_overlap_size": 800,       # 块间重叠
    "max_chunk_size": 400000,          # 最大块大小
    "whole_document_threshold": 300000,# 整文档阈值
}
```

### 术语提取模式

```python
EXTRACTION_MODE = {
    "bilingual": True,  # True=双语, False=单语
}
```

### 提示词定制

```python
# 系统提示词
SYSTEM_PROMPT = """You are a senior military, aerospace, medical, and defense terminology extraction specialist..."""

# 用户提示词（支持单语/双语）
def get_user_prompt(text: str, bilingual: bool = True):
    # 返回定制化提示词
```

---

## 📋 使用示例

### 示例1：处理扫描版PDF词典

```bash
# 1. 将PDF放入 file preparation/ 目录
# 2. 运行程序
python main.py

# 3. 选择双语模式
🌐 请选择术语提取模式:
1. 双语模式 (推荐)
2. 单语模式
请选择 (1-2): 1

# 4. 自动处理
📑 检测到大型PDF，将分批处理（每批20页）
🔄 正在识别批次 1/12...
✅ 批次 1 完成，耗时 45.3秒
💾 批次 1 结果已保存
📈 总进度: 8.3% (1/12)

# 5. 生成Excel报表
📊 请选择输出格式:
选择格式 (1-5): 3
✅ Excel文件已生成
```

**预期结果：**
- OCR时间：约1-2分钟/页（取决于网络速度）
- 术语提取：20-30分钟（238页PDF）
- 输出文件：`batch_results/词典_20251022_143045_gpt4o_1500terms.xlsx`
- 中间文本：`extracted_texts/词典_batch_ocr.txt`

### 示例2：快速单语提取

```bash
python main.py

# 选择单语模式
🌐 请选择术语提取模式: 2

# 输出CSV格式
📊 请选择输出格式: 2
```

**优势：**
- 处理速度更快
- Token使用更少（降低约15-20%）
- 总体成本更低

### 示例3：批量处理文件夹

```bash
# 1. 预先提取所有PDF文本
python extract_pdf_texts.py

# 2. 批量术语提取
python main.py
# 选择: 从文件读取 → 处理所有文件
```

---

## 📊 输出格式详解

### 1. JSON格式

**用途：** 程序处理、API集成

```json
{
  "custom_id": "merged_terms",
  "extracted_terms": {
    "terms": [
      {
        "eng_term": "Unmanned Aerial Vehicle (UAV)",
        "zh_term": "无人机",
        "source_files": ["document.pdf"]
      }
    ],
    "total_terms": 1500,
    "duplicates_removed": 230
  },
  "usage": {"total_tokens": 45000},
  "model": "gpt-4o",
  "created": 1729584000
}
```

### 2. CSV格式

**用途：** Excel导入、数据分析

```csv
custom_id,英文术语,中文术语,来源文件,模型,token使用
merged_terms,Inertial Navigation System (INS),惯性导航系统,词典.pdf,gpt-4o,1250
```

**编码：** UTF-8-BOM（Excel直接兼容，无乱码）

### 3. Excel格式

**用途：** 人工审核、团队协作

**特性：**
- ✨ 专业样式（表头蓝色、边框、居中对齐）
- 📊 统计信息工作表（总术语数、Token使用、生成时间）
- 📏 自动列宽调整
- 🎨 条件格式（可选）

### 4. TBX格式

**用途：** CAT工具（Trados、MemoQ等）

**标准：** ISO 30042（TermBase eXchange）

```xml
<termEntry id="term_1">
  <langGrp xml:lang="en">
    <term>Inertial Navigation System</term>
  </langGrp>
  <langGrp xml:lang="zh">
    <term>惯性导航系统</term>
  </langGrp>
</termEntry>
```

### 5. TXT格式

**用途：** 简单查看、打印、备份

```
=== 结果 1: merged_terms ===
提取的术语数量: 1500

1. Inertial Navigation System (INS)
   惯性导航系统
   
2. Global Positioning System (GPS)
   全球定位系统
```

---

## 🔧 高级功能

### 智能文本分割

**策略：**
- **整文档模式**: <300K字符 → 单个上下文处理
- **智能分割**: 按段落和语义边界分割
- **按段落处理**: 适合短文本和术语表

**配置：**
```python
# 在运行时选择
📝 文本分割配置:
1. 智能分割 (推荐)
2. 整文档处理
3. 按段落处理
```

### 并发批处理

**优势：**
- 多线程并发API调用
- 速度提升5-10倍
- 自动速率限制

**配置：**
```python
BATCH_CONFIG = {
    "max_concurrent": 10,  # 并发数（根据API限制调整）
    "requests_per_minute": 30,  # 速率限制
}
```

### 断点恢复系统

**自动保存：**
- 每处理5个文件自动保存
- 每10分钟自动保存
- 完成后自动删除

**手动管理：**
```bash
# 列出所有检查点
python checkpoint_tool.py list

# 查看详细信息
python checkpoint_tool.py show <checkpoint-id>

# 删除检查点
python checkpoint_tool.py delete <checkpoint-id>
```

### 去重算法

**单语模式：**
```python
term_key = term.lower()  # 忽略大小写
```

**双语模式：**
```python
term_key = f"{eng_term.lower()}|{zh_term}"  # 组合键
```

**策略：**
- 优先选择首字母大写的版本
- 合并多个来源文件信息
- 保留最完整的术语形式

---


## 📦 依赖说明

### 核心依赖

```
# GPT术语抽取核心依赖
openai>=1.10.0              # GPT API集成
tiktoken>=0.5.1             # Token计数

# PDF处理
pdfminer.six>=20231228      # PDF文本提取
PyPDF2==3.0.1              # PDF分割（分批OCR用）

# 文档处理
python-docx==0.8.11         # DOCX支持

# OCR功能（科大讯飞云端API）
requests>=2.31.0            # HTTP客户端，用于调用讯飞OCR API
Pillow>=10.0.0             # 图像处理（可选）

# Excel输出支持
openpyxl>=3.1.0            # Excel输出
```

### 可选依赖

```
python-magic==0.4.27        # 文件类型检测
python-magic-bin==0.4.14    # Windows magic支持
```

---

## 📄 许可证

本项目为专有软件，专为军事、航空航天和国防领域的术语提取应用设计。

---

## 🤝 贡献指南

本工具面向专业国防和航空航天应用。如需定制化或企业部署，请联系开发团队。

---

## 🔗 相关文档

- [双语术语提取功能说明](BILINGUAL_FEATURES.md) - 详细的双语功能文档
- [提取模式对比](EXTRACTION_MODES.md) - 单语vs双语全面对比
- [配置文件](config.py) - 完整配置选项说明

---

<div align="center">

**🌟 Star this repo if you find it helpful! 🌟**


</div>

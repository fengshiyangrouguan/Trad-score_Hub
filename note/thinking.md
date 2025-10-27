## 1️⃣ 分层理解

### a) `scorelang/`

* **职责**：专注于 **乐谱语言的解析与表示**

  * Lexer → Token
  * Parser → AST
  * AST + Visitor + Renderers → 可渲染输出
* **特点**：

  * 独立于 Web/API/Service
  * 不处理业务逻辑、存储或请求
  * 提供纯粹的 DSL 处理能力（类似 `markdown` 库）
* **结果**：生成 AST 或可渲染对象

### b) `app/`（同级层）

* **职责**：应用服务层，协调整个流程

  * 调用 `scorelang` 的 Parser / AST / Renderers
  * 封装成 **Service / Factory / Registry**
  * 提供统一接口给 API / CLI / 后端
* **特点**：

  * 处理业务逻辑（选择谱种、选择输出格式）
  * 可以加入日志、缓存、异常处理等

---


## 当前文件架构：

```
backend/src
├── api/                         ← 对外接口层（HTTP / REST / FastAPI）
│   ├── main.py                  ← API 启动入口
│   ├── routes/                  ← 路由处理
│   │   └── score_routes.py
│   └── deps.py                  ← 依赖注入、认证、数据库
│
├── app/                         ← 应用服务层
│   ├── services.py              ← 核心业务协调（Parser + Renderer + Generator）
│
├── scorelang/                   ← 核心乐谱语言模块
|
└── tests/                        ← 测试用例
    ├── test_service.py
    ├── test_parser_pipa.py
    ├── test_parser_guqin.py
    ├── test_lexer.py
    └── test_renderers.py

```

```
scorelang/
├── __init__.py

├── lexer/                       # 词法分析（Tokenize）
│   ├── __init__.py
│   ├── lexer.py                 # 正则词法分析器

├── parser/                      # 将 Token 流转为 AST
│   ├── __init__.py
│   ├── base_parser.py           # 抽象 Parser 基类（接口定义）
│   ├── pipa_parser.py           # 琵琶谱 Parser
│   ├── guqin_parser.py          # 古琴谱 Parser
│   └── parser_factory.py        # Parser Factory / Registry

├── ast/                         # AST 节点 + Visitor + 渲染
│   ├── __init__.py
│   ├── nodes.py                 # AST 节点类 (DocumentNode, ScoreNode, TextNode 等)
│   ├── visitor.py               # Visitor 遍历 AST
│   ├── transforms.py            # AST 规范化 / 优化 pass
│   └── renderers/               # 渲染模块
│       ├── __init__.py
│       ├── text_renderer.py
│       ├── svg_renderer.py
│       ├── musicxml_renderer.py
│       └── midi_renderer.py

├── domain/                      # 数据模型（可选：AST → Domain 转换）
│   ├── __init__.py
│   └── models.py                # ScoreUnit, TextUnit, ScoreDocument

├── converters/                  # 高层生成器接口（包装 Renderer）
│   ├── __init__.py
│   ├── base_generator.py
│   ├── termuxed_generator.py
│   ├── png_generator.py
│   ├── musicxml_generator.py
│   └── midi_generator.py

├── config/                      # 配置文件存放
│   ├── map_pipa.toml
│   └── map_guqin.toml

└── utils/                       # 工具类/公共功能
    ├── __init__.py
    ├── logger.py
    ├── config_loader.py         # TOML/JSON 加载工具
    └── exceptions.py            # ParseError / ValidationError

```


## 输入流程概览

假设输入的是琵琶谱文本（`score_text`），输出可能是文本谱或 PNG 图像。

```
score_text (字符串输入)
      │
      ▼
app/services.py → ScoreService.process_parsing()
      │
      ▼
Parser Factory (scorelang/core/parser_factory.py)
      │
      └─> 选择具体 Parser：PipaParser
            │
            ▼
Lexer (scorelang/core/lexer/lexer.py)
      │
      ▼
Token 流
      │
      ▼
Parser (PipaParser)
      │
      └─> 将 Token 流解析为 AST（DocumentNode → ScoreNode / TextNode）
            │
            ▼
AST Visitor / 转换 pass (可选)
      │
      ▼
AST Renderers (scorelang/core/ast/renderers/)
      │
      ├─> TextRenderer → 文本谱
      ├─> SVGRenderer → 矢量图
      └─> MusicXMLRenderer / MIDIRenderer → 标准乐谱
      │
      ▼
Converters (scorelang/converters/)
      │
      └─> 对外包装、保存文件、提供统一接口
      │
      ▼
ScoreService 返回 ScoreDocument 或渲染结果
      │
      ▼
API / CLI 返回结果
```

## 分步解释

1. **外部输入**

   * 用户提供琵琶谱文本或文件
   * 调用 Service 层（`ScoreService.process_parsing(score_text)`）

2. **Parser Factory 选择 Parser**

   * `score_type="pipa"` → Factory 返回 `PipaParser` 实例
   * Factory 内部根据谱种选择合适 Lexer/Parser 配置（map_pipa.toml）

3. **Lexer → Token 流**

   * 正则词法分析器把文本切分为 Token
   * Token 类型（MAIN_CHAR, RHYTHM_MOD, TIME_MOD, TEXT_UNIT 等）

4. **Parser → AST**

   * Parser 将 Token 组织成 AST（DocumentNode 下包含 ScoreNode、TextNode、SectionNode 等）
   * 可执行 Visitor 遍历和规范化 Pass（比如处理火标记、时值归一化）

5. **Renderer → 输出表示**

   * 文本渲染器 / SVG 渲染器 / MusicXML / MIDI
   * AST → 目标格式

6. **Converters → 对外接口**

   * 将渲染结果包装成文件或字符串
   * Service 层统一返回给 API/CLI

7. **API / CLI 返回**

   * JSON、PNG、文本谱等形式返回给调用者


# 2025.10.25

### pipa_layout_pass可以生成一个renderlist（类似css），一页生成一个list，而不是去修改node，形成耦合
### 应该用一个style_map同时控制layout_config和renderer
### layout_config 应更名为 layout_rules_generator
### layoutpass生成command时就可以不传入font size，font color等等，以此做到更个性化的设计

# 2025.10.26

## 将**乐理的语义**与**最终的视觉符号**分离解耦合

**（AST 存储标准化乐理标识）确保 AST 的纯粹性和可移植性。**

### 最终确认的架构方案

我们将采用以下三层分离的模式：

| 架构层 | 存储内容 | 映射/职责 | 谁在使用？ |
| :--- | :--- | :--- | :--- |
| **Parser / AST** | **标准乐理标识** (例如：`Marker.ARPEGGIO`, `Rhythm.DOTTED`) | **Parser** 负责将输入符号 (`/py`) $\to$ 标准乐理标识 (`ARPEGGIO`)。 | Layout Pass |
| **LayoutMetrics** | **乐理标识 $\to$ 渲染类型** (`ARPEGGIO` $\to$ `DOT_MARKER`) | **Layout Pass** 查询此映射，以知道要生成哪个 Render Command。 | Layout Pass |
| **StyleManager** | **渲染类型 $\to$ 符号字符** (`DOT_MARKER` $\to$ `"乐"`) | **Renderer** 查询此映射，以知道要画哪个字符。 | Renderer |

-----

### 示例实现

#### 1\. AST Node 存储乐理标识 (Parser 负责标准化)

AST Node 包含一个枚举或常量，表示**乐理意图**，而不是用户输入或视觉符号：

```python
# AST Node (例如 ScoreUnitNode)
class ScoreUnitNode(BaseModel):
    # 存储乐理标识（不再是原始输入 '/py'）
    bottom_marker_intent: MarkerIntent = MarkerIntent.ARPEGGIO 
    # MarkerIntent.ARPEGGIO, MarkerIntent.TREMOLO, etc.
```

#### 2\. LayoutMetrics 存储 **乐理标识 $\to$ Render Command Type** 映射

LayoutMetrics 负责将乐理标识转换为 Layout Pass 所需的 **Render Command 类型**：

```python
# LayoutMetrics 配置
class LayoutMetrics:
    def __init__(self, config):
        # 存储乐理意图到渲染类型的映射
        self.intent_to_command_map = config['marker_map'] 
        # {'ARPEGGIO': 'DOT_MARKER', 'TREMOLO': 'LINE_MARKER'} 
        # ...

    def get_command_type(self, intent: str) -> str:
        return self.intent_to_command_map.get(intent)
```

#### 3\. Layout Pass 行为 (查询 LayoutMetrics)

Layout Pass 根据 AST 的意图查询 LayoutMetrics，然后调度指令：

```python
def _layout_bottom_marker(self, node: ScoreUnitNode, unit_x):
    intent = node.bottom_marker_intent # 获取乐理意图 "ARPEGGIO"

    # 1. 查询意图/指令类型
    command_type = self.layout_metrics.get_command_type(intent) # 结果是 "DOT_MARKER"

    if not command_type:
        return

    # 2. 计算几何位置 (不变)
    bottom_mod_pos = self._calculate_position(...)
    
    # 3. 调度指令 (基于查询结果)
    if command_type == "DOT_MARKER":
        self.builder.add_dot_marker(position=bottom_mod_pos)
    elif command_type == "LINE_MARKER":
        self.builder.add_line_marker(position=bottom_mod_pos)
    # ...
```

### 总结

  * **AST 纯净：** 无论想用圆点、方块还是其他符号来表示某个含义，`node.bottom_marker_intent` 永远都是 `ARPEGGIO`。
  * **解耦：** 想修改符号：
      * 只需修改 `LayoutMetrics` 中的映射：`'ARPEGGIO': 'LINE_MARKER'`。
      * **不需要修改 Parser 代码。**
      * **不需要修改 Layout Pass 代码。** (它只需要在 `if/elif` 中处理所有可能的 `command_type`)。

实现高程度的配置化和职责分离。

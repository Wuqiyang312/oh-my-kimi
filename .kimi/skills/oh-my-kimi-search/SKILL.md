---
name: oh-my-kimi-search
description: |
  使用 Oh My Kimi 插件进行文件搜索和内容搜索。
  当用户需要以下功能时触发：
  (1) 查找文件 - "查找所有 Python 文件"
  (2) 搜索文件内容 - "搜索包含某内容的文件"
  (3) 查找 TODO/FIXME - "查找代码中的 TODO"
  (4) 按模式查找 - "搜索某种类型的文件"
  (5) 正则搜索 - "查找函数定义"
---

# Oh My Kimi - 文件搜索

专注于文件查找和内容搜索的工具集合。

## 工具概览

| 工具 | 用途 | 典型场景 |
|------|------|----------|
| `smart_glob` | 文件模式匹配查找 | 查找特定类型文件、按目录查找 |
| `smart_grep` | 文件内容搜索 | 查找代码模式、搜索 TODO/FIXME |

---

## smart_glob - 文件查找

基于 glob 模式查找文件，支持 `**/*.py` 等高级模式。

### 核心参数
- `pattern` (必需): 匹配模式，如 `"**/*.py"`, `"src/**/*.ts"`
- `path`: 搜索目录，默认当前工作目录
- `limit`: 结果数量限制，默认 100

### 典型用法
```json
// 查找所有 Python 文件
{"pattern": "**/*.py"}

// 在 src 目录查找 TypeScript 文件
{"pattern": "**/*.ts", "path": "./src"}

// 查找配置文件，限制 20 个
{"pattern": "*.json", "limit": 20}

// 查找测试文件
{"pattern": "test_*.py"}

// 查找所有 Markdown 文档
{"pattern": "**/*.md"}
```

### 适用场景
- 批量查找特定类型文件
- 定位代码文件范围后再用 smart_grep 搜索
- 统计某类文件数量
- 查找配置文件或文档

---

## smart_grep - 内容搜索

基于正则表达式搜索文件内容，支持多种输出模式。

### 核心参数
- `pattern` (必需): 正则表达式模式
- `include`: 文件类型过滤，如 `"*.py"`, `"*.{ts,tsx}"`
- `output_mode`: 输出模式
  - `content`: 显示匹配行内容
  - `files_with_matches`: 仅显示文件路径（默认）
  - `count`: 统计匹配数量
- `head_limit`: 结果数量限制
- `path`: 搜索目录

### 典型用法
```json
// 查找所有函数定义
{"pattern": "^def ", "include": "*.py", "output_mode": "content"}

// 查找 TODO/FIXME 并统计数量
{"pattern": "TODO|FIXME", "output_mode": "count"}

// 查找类定义，限制 20 个结果
{"pattern": "^class ", "include": "*.py", "head_limit": 20}

// 搜索所有导入语句
{"pattern": "^import |^from ", "include": "*.py", "output_mode": "content"}

// 查找特定字符串
{"pattern": "config", "output_mode": "files_with_matches"}

// 在特定目录搜索
{"pattern": "function", "path": "./src", "include": "*.js"}
```

### 适用场景
- 查找代码模式（函数、类、导入）
- 搜索 TODO/FIXME/HACK 标记
- 查找特定字符串在哪些文件中
- 统计某模式出现次数
- 代码重构前的影响范围分析

---

## 组合使用技巧

### 技巧 1: 先定位范围，再搜索内容
```
1. smart_glob "src/**/*.py" → 获取 Python 文件列表
2. smart_grep "TODO" --include "*.py" → 在这些文件中搜索 TODO
```

### 技巧 2: 查找重复代码
```
smart_grep "some_function_pattern" --output_mode "content"
→ 查看某段代码在哪些文件中重复出现
```

### 技巧 3: 快速定位文件
```
smart_glob "**/*config*" → 查找配置文件
smart_grep "API_KEY" → 查找包含密钥的文件
```

---

## 常见任务速查

| 任务 | 工具 | 参数示例 |
|------|------|----------|
| 找所有 Python 文件 | smart_glob | `{"pattern": "**/*.py"}` |
| 找测试文件 | smart_glob | `{"pattern": "test_*.py"}` |
| 查找 TODO | smart_grep | `{"pattern": "TODO", "output_mode": "content"}` |
| 查找函数定义 | smart_grep | `{"pattern": "^def ", "include": "*.py"}` |
| 查找类定义 | smart_grep | `{"pattern": "^class ", "include": "*.py"}` |
| 查找未使用的导入 | smart_grep | `{"pattern": "^import \|from "}` |
| 统计某模式出现次数 | smart_grep | `{"pattern": "pattern", "output_mode": "count"}` |

---

## 注意事项

1. **路径处理**: 所有路径都相对于当前工作目录
2. **性能**: 大型项目搜索可能需要较长时间
3. **正则表达式**: smart_grep 使用 Python re 模块语法
4. **自动排除**: 工具自动排除 node_modules, __pycache__, .git 等目录
5. **glob 模式**: `**` 表示递归匹配任意层级子目录

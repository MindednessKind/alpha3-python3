# alpha3-python3

ALPHA3 是一个字母数字 shellcode 编码器，可以把原始 x86/x64 shellcode 编码为只包含允许字符集的 shellcode，并在运行时通过前置 decoder 还原和执行原始代码。

本仓库基于 SkyLined 的 ALPHA3 做了 Python 3 迁移和可用性修复，目标是保留原有命令行使用方式，同时让项目在现代 Python 3 环境中可以直接运行。

## 当前状态

- 支持 Python 3 运行，已在 Python 3.12 上验证。
- 修复 Python 2 语法、隐式相对导入、二进制 stdin/stdout、文件输出等问题。
- 补齐 decoder `.bin` 文件，不再要求用户先运行 SkyBuild 才能编码。
- 保留 `.asm` 源文件，`io.ReadFile()` 在 `.bin` 缺失时仍可尝试用 NASM 从同名 `.asm` 自动生成。
- `--test` 已迁移到 Python 3；在非 Windows 环境会明确提示 Testival 测试需要 Windows。

## 环境要求

- Python 3.8+
- NASM，可选但建议安装。仓库已包含生成好的 `.bin`，正常编码不需要重新生成；当 `.bin` 缺失或需要重建时才需要 NASM。
- Windows + Testival，仅在运行 `--test` 时需要。

## 基本用法

查看帮助：

```bash
python3 ALPHA3.py --help
```

编码 x86 ascii mixedcase shellcode，假设 EAX 指向编码后 shellcode 起始地址：

```bash
python3 ALPHA3.py x86 ascii mixedcase eax \
  --input=test/w32-writeconsole-shellcode.bin \
  --output=/tmp/alpha3-x86.bin
```

编码 x64 ascii mixedcase shellcode，假设 RAX 指向编码后 shellcode 起始地址：

```bash
python3 ALPHA3.py x64 ascii mixedcase rax \
  --input=test/w64-writeconsole-shellcode.bin \
  --output=/tmp/alpha3-x64.bin
```

也可以通过 stdin/stdout 使用：

```bash
python3 ALPHA3.py x86 ascii mixedcase eax < raw.bin > encoded.bin
```

注意：ALPHA3 原算法要求输入 shellcode 不包含 NULL 字节。

## 支持的编码器

当前 `python3 ALPHA3.py --help` 会列出完整 base address 示例。主要类别如下：

- `x64 ascii mixedcase`: `RAX RCX RDX RBX RSP RBP RSI RDI`
- `x86 ascii lowercase`: `ECX EDX EBX`
- `x86 ascii mixedcase`: 通用寄存器、内存寄存器、`i32`、countslide、SEH GetPC
- `x86 ascii uppercase`: 通用寄存器和内存寄存器
- `x86 latin-1 mixedcase`: CALL GetPC
- `x86 utf-16 uppercase`: Unicode uppercase decoder

## 目录说明

- `ALPHA3.py`: 命令行入口和 encoder 调度。
- `encode.py`: 通用编码算法。
- `charsets.py`: 字符集和合法字符表。
- `io.py`: 文件读写、长路径处理、`.asm` 到 `.bin` 的兜底生成。
- `print_functions.py`: 控制台输出和进度显示。
- `x86/`: x86 decoder 和 encoder 注册。
- `x64/`: x64 decoder 和 encoder 注册。
- `test/`: Testival 测试程序和测试 shellcode。
- `TREE.md`: 当前项目文件树。
- `NAVIGATION.md`: 实现完成情况和关键功能位置。

## 验证命令

语法检查：

```bash
python3 -m py_compile ALPHA3.py encode.py io.py charsets.py print_functions.py test/__init__.py
```

功能 smoke test：

```bash
python3 ALPHA3.py --help
python3 ALPHA3.py x86 ascii mixedcase eax --input=test/w32-writeconsole-shellcode.bin --output=/tmp/alpha3-x86.bin
python3 ALPHA3.py x64 ascii mixedcase rax --input=test/w64-writeconsole-shellcode.bin --output=/tmp/alpha3-x64.bin
```

非 Windows 环境下运行 `--test` 会返回可控提示：

```text
Encoder tests require Windows/Testival and cannot run on this platform.
```

## 授权

原项目版权和授权说明见 `COPYRIGHT.txt`。

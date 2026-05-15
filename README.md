# alpha3-python3

SkyLined 的 ALPHA3，搬到 Python 3 上来了。

ALPHA3 干的事很简单：把你的 x86/x64 shellcode 编码成只含特定字符集的字节（比如 `ascii mixedcase`），前面拼一段 decoder stub，运行时先自解码再跳到真正的 payload。

我做的事就两件：Python 2 → 3 的迁移，以及把 decoder 的 `.bin` 直接放进仓库。clone 下来就能跑，不用折腾 SkyBuild。

## 当前状态

Python 3.12 下日常使用没问题。迁移过程中处理了老语法、隐式相对导入、二进制 stdin/stdout 这些 2→3 的经典坑。

decoder `.bin` 已经全部到位，正常用不需要装 NASM。只有 `.bin` 丢了或者你想自己重新编译 decoder 时才会去找 NASM。

内置的 `--test` 还在，但它依赖 Windows + Testival。非 Windows 下跑会告诉你平台不对，不会直接炸。

x64 额外加了两层验证：Unicorn 仿真跑一遍，再在真实 Linux x86_64 进程里执行编码后的 `execve("/bin//sh")` 确认能拿到 shell。

## 依赖

- Python 3.8+
- NASM — 可选，`.bin` 都带了
- Unicorn — 跑 `test/validate_x64_shellcode.py` 时要
- gcc + Linux x86_64 — 跑 `test/validate_x64_execve_shell.py` 时要
- Windows + Testival — 跑内置 `--test` 时要

## 用法

看帮助，列出所有 encoder 和 base address 写法：

```bash
python3 ALPHA3.py --help
```

x86 编码，假设 EAX 指向编码后 shellcode 起始：

```bash
python3 ALPHA3.py x86 ascii mixedcase eax \
  --input=test/w32-writeconsole-shellcode.bin \
  --output=/tmp/alpha3-x86.bin
```

x64 同理，换架构换寄存器，RAX 指向起始：

```bash
python3 ALPHA3.py x64 ascii mixedcase rax \
  --input=test/w64-writeconsole-shellcode.bin \
  --output=/tmp/alpha3-x64.bin
```

管道也行：

```bash
python3 ALPHA3.py x86 ascii mixedcase eax < raw.bin > encoded.bin
```

注意：输入 shellcode 不能有 NULL 字节，这是原算法的限制。

## 支持的编码器

跑 `--help` 看完整列表。常用的：

- `x64 ascii mixedcase` — RAX RCX RDX RBX RSP RBP RSI RDI
- `x86 ascii lowercase` — ECX EDX EBX
- `x86 ascii mixedcase` — 通用寄存器、内存寄存器、i32、countslide、SEH GetPC
- `x86 ascii uppercase` — 通用寄存器、内存寄存器
- `x86 latin-1 mixedcase` — CALL GetPC
- `x86 utf-16 uppercase` — Unicode uppercase decoder

## 目录结构

- `ALPHA3.py` — 入口，encoder 调度
- `encode.py` — 编码算法
- `charsets.py` — 字符集定义
- `io.py` — 文件读写，`.asm` → `.bin` 兜底
- `print_functions.py` — 控制台输出
- `x86/` — x86 decoder + encoder
- `x64/` — x64 decoder + encoder
- `test/` — 测试 shellcode 和验证脚本

## 验证

快速检查语法没坏：

```bash
python3 -m py_compile ALPHA3.py encode.py io.py charsets.py print_functions.py test/__init__.py
```

跑一遍基础编码确认能出东西：

```bash
python3 ALPHA3.py x86 ascii mixedcase eax --input=test/w32-writeconsole-shellcode.bin --output=/tmp/alpha3-x86.bin
python3 ALPHA3.py x64 ascii mixedcase rax --input=test/w64-writeconsole-shellcode.bin --output=/tmp/alpha3-x64.bin
```

依赖齐全的话可以继续跑 x64 验证：

```bash
python3 test/validate_x64_shellcode.py
python3 test/validate_x64_execve_shell.py
```

非 Windows 下跑 `--test` 会看到：

```text
Encoder tests require Windows/Testival and cannot run on this platform.
```

这是正常的。

## 授权

两部分：

- Python 3 迁移和新增内容 — MIT License，MindednessKind <mindednesskind@gmail.com>，见 `LICENSE`
- 原始 ALPHA3 代码和 decoder 资产 — Berend-Jan "SkyLined" Wever 的版权，BSD-3-Clause-style，详见 `COPYRIGHT.txt` 和 `LICENSE`

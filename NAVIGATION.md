# 交接导航

本文记录当前 `alpha3-python3` 项目的完成情况、实现功能和关键代码位置。

## 完成情况

- Python 3 迁移已完成。
  - Python 2 的 `print >>`、`dict.keys().sort()`、`exit()` 等旧写法已处理。
  - 包内隐式相对导入已改成 Python 3 显式相对导入。
  - stdin/stdout 和文件读写按二进制数据处理，内部仍保持原 ALPHA3 的 Latin-1 字节字符串模型。
- decoder `.bin` 已补齐。
  - `x86/` 和 `x64/` 下当前有 66 个 decoder `.bin`。
  - `.asm` 源文件仍保留。
  - `io.ReadFile()` 在 `.bin` 缺失时可尝试通过 NASM 从同名 `.asm` 自动生成。
- 命令行编码功能可用。
  - `--input` / `--output` 可用。
  - stdin/stdout 可用。
  - x86/x64 代表性 encoder 已通过 smoke test。
- `test/__init__.py` 已迁移到 Python 3。
  - Windows/Testival 环境可继续使用原测试逻辑。
  - 非 Windows 环境不会导入即崩溃，会返回明确提示。
- 已新增项目协作指南。
  - `AGENTS.md` 是英文版 contributor/agent 规则入口。
  - `AGENTS-cn.md` 保留中文 agent 工作约定。
- 已新增 x64 shellcode 仿真验证脚本。
  - `test/validate_x64_shellcode.py` 使用 Unicorn 验证 `x64 ascii mixedcase rax` 编码结果可解码并执行。
- 已新增 x64 get-shell 进程级验证脚本。
  - `test/validate_x64_execve_shell.py` 生成 NULL-free Linux x86_64 `execve("/bin//sh")` payload，使用 `x64 ascii mixedcase rax` 编码，再通过临时 C harness 设置 `RAX` 为 decoder 基址并执行编码结果。
  - 验证方式是向被拉起的 `/bin/sh` 发送 marker 命令，确认 shell stdout 返回 `ALPHA3_EXECVE_SHELL_OK\n`。

## 关键入口地址

### 命令行入口

- `ALPHA3.py`
  - `ParseCommandLine()`: 解析 settings、arguments、switches、flags。
  - `Main()`: 根据 `--help`、`--test` 或编码模式调度 encoder。
  - `CheckEncodedShellcode()`: 检查输出是否符合目标字符集。
  - `toInt()`: 解析十进制或 `0x` 十六进制整数。

### I/O 和 `.bin` 处理

- `io.py`
  - `_EnsureBinaryFromAssembly(binary_path)`: 当 `.bin` 不存在时，尝试调用 `nasm -f bin` 从同名 `.asm` 生成。
  - `ReadFile(file_name, path=None)`: 二进制读文件并按 Latin-1 转成内部字符串。
  - `WriteFile(file_name, contents, path=None)`: 将内部字符串或 bytes 写成二进制文件。
  - `LongPath()` / `ShortPath()`: 保留原 Windows 长路径处理逻辑。

### 核心编码算法

- `encode.py`
  - `encodeData()`: 通用数据编码流程，拼接 decoder 和 encoded payload。
  - `bx_IMUL_30_XOR_by()`: x86/x64 ascii mixedcase 常用编码函数。
  - `bx_IMUL_10_ADD_by()`: unicode uppercase 编码函数。
  - `wyx_IMUL_30_SHR_8_XOR_bx()`: x86 lowercase 编码函数。
  - `dwx_IMUL_by()` / `dwx_IMUL_30_XOR_dwy()`: i32/base address 相关编码函数。
  - `injectCodes()`: 把动态编码出的立即数填入 decoder 模板。

### 字符集

- `charsets.py`
  - `valid_character_encodings`: 支持的编码名。
  - `valid_character_casings`: 支持的大小写约束。
  - `valid_chars`: 字符串形式的合法字符集合。
  - `valid_charcodes`: 整数形式的合法字符集合。
  - `charcode_fmtstr`: 错误报告中的字节格式。

### 输出

- `print_functions.py`
  - `PrintWrappedLine()`、`PrintInfo()`、`PrintStatus()` 等命令行输出工具。
  - `g_output_verbosity_level` 控制 verbose 输出。

## Encoder 注册位置

顶层聚合：

- `x86/__init__.py`: 聚合 x86 ascii、latin-1、utf-16 encoder。
- `x64/__init__.py`: 聚合 x64 encoder。

x64:

- `x64/ascii/mixedcase/rm64/__init__.py`
  - 名称：`AscMix (r64)`
  - base address：`RAX RCX RDX RBX RSP RBP RSI RDI`
  - decoder 资源：同目录 `RAX.bin`、`RCX.bin` 等。

### 执行级验证

- `test/validate_x64_shellcode.py`
  - 对 `x64 ascii mixedcase rax` 编码结果做 Unicorn 仿真，确认 decoder 还原原始 ORW payload，并拦截 Linux syscall 验证 stdout。
- `test/validate_x64_execve_shell.py`
  - 对 `x64 ascii mixedcase rax` 编码结果做真实进程级验证。
  - payload 为 NULL-free `execve("/bin//sh")` shellcode。
  - 临时 harness 使用 RWX `mmap` 装载编码后 shellcode，设置 `RAX=region` 后调用 decoder；shell 成功执行 marker 命令即视为 get-shell 可行。

x86 ascii mixedcase:

- `x86/ascii/mixedcase/rm32/__init__.py`
  - 名称：`AscMix 0x30 (rm32)`
  - base address：通用寄存器、内存寄存器、`[ESP-4]`、`ECX+2`、`ESI+4`、`ESI+8`
  - decoder 资源：同目录 `.bin`
- `x86/ascii/mixedcase/i32/__init__.py`
  - 名称：`AscMix 0x30 (i32)`
  - base address：立即数地址，如 `0x09090900`
- `x86/ascii/mixedcase/getpc/countslide/rm32/__init__.py`
  - 名称：`AscMix Countslide (rm32)`
  - base address：`countslide:EAX+offset~uncertainty` 等
- `x86/ascii/mixedcase/getpc/countslide/i32/__init__.py`
  - 名称：`AscMix Countslide (i32)`
  - base address：`countslide:address~uncertainty`
- `x86/ascii/mixedcase/getpc/seh/xpsp3/__init__.py`
  - 名称：`AscMix SEH GetPC (XPsp3)`
  - base address：`seh_getpc_xpsp3`

x86 ascii lowercase:

- `x86/ascii/lowercase/rm32/__init__.py`
  - 名称：`AscLow 0x30 (rm32)`
  - base address：`ECX EDX EBX`

x86 ascii uppercase:

- `x86/ascii/uppercase/rm32/__init__.py`
  - 名称：`AscUpp 0x30 (rm32)`
  - base address：通用寄存器和内存寄存器。

x86 latin-1:

- `x86/latin_1/mixedcase/getpc/call/__init__.py`
  - 名称：`Latin1Mix CALL GetPC`
  - base address：`call`

x86 utf-16:

- `x86/utf_16/uppercase/rm32/__init__.py`
  - 名称：`UniUpper 0x10 (rm32)`
  - base address：通用寄存器和部分内存形式。

## 验证记录

建议交接后先运行：

```bash
python3 -m py_compile ALPHA3.py encode.py io.py charsets.py print_functions.py test/__init__.py
python3 ALPHA3.py --help
python3 ALPHA3.py x86 ascii mixedcase eax --input=test/w32-writeconsole-shellcode.bin --output=/tmp/alpha3-x86.bin
python3 ALPHA3.py x64 ascii mixedcase rax --input=test/w64-writeconsole-shellcode.bin --output=/tmp/alpha3-x64.bin
python3 test/validate_x64_shellcode.py
python3 test/validate_x64_execve_shell.py
```

非 Windows 环境下：

```bash
python3 ALPHA3.py --test
```

预期会返回：

```text
Encoder tests require Windows/Testival and cannot run on this platform.
```

## 已知约束

- 输入 shellcode 必须 NULL-free。
- `test/validate_x64_execve_shell.py` 需要 Linux x86_64、`gcc`，并要求运行环境允许临时进程使用 RWX `mmap` 执行 shellcode。
- `--test` 依赖 Windows Testival `.exe`，Linux 下只能验证 CLI 和编码输出。
- 如果删除 `.bin` 后需要自动重建，系统必须安装 NASM。
- `older_versions.zip` 为原项目历史资料，当前运行路径不依赖它。

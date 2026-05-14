# 项目文件树

生成时间基于当前工作区状态。已排除 `.git/` 和 `__pycache__/`。

```text
.
├── .agents/
├── .codex/
├── test/
│   ├── __init__.py
│   ├── TESTIVAL.txt
│   ├── w32-testival.exe
│   ├── w32-testival.pdb
│   ├── w32-writeconsole-shellcode.bin
│   ├── w64-testival.exe
│   ├── w64-testival.pdb
│   ├── w64-writeconsole-shellcode.bin
│   └── validate_x64_shellcode.py
├── x64/
│   ├── ascii/
│   │   ├── mixedcase/
│   │   │   ├── rm64/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── build_config.py
│   │   │   │   ├── encode JMP offset.py
│   │   │   │   ├── RAX.asm
│   │   │   │   ├── RAX.bin
│   │   │   │   ├── RBP.asm
│   │   │   │   ├── RBP.bin
│   │   │   │   ├── RBX.asm
│   │   │   │   ├── RBX.bin
│   │   │   │   ├── RCX.asm
│   │   │   │   ├── RCX.bin
│   │   │   │   ├── RDI.asm
│   │   │   │   ├── RDI.bin
│   │   │   │   ├── RDX.asm
│   │   │   │   ├── RDX.bin
│   │   │   │   ├── RSI.asm
│   │   │   │   ├── RSI.bin
│   │   │   │   ├── RSP.asm
│   │   │   │   └── RSP.bin
│   │   │   ├── __init__.py
│   │   │   └── build_config.py
│   │   ├── __init__.py
│   │   └── build_config.py
│   ├── __init__.py
│   └── build_config.py
├── x86/
│   ├── ascii/
│   │   ├── lowercase/
│   │   │   ├── rm32/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── build_config.py
│   │   │   │   ├── EBX.asm
│   │   │   │   ├── EBX.bin
│   │   │   │   ├── ECX.asm
│   │   │   │   ├── ECX.bin
│   │   │   │   ├── EDX.asm
│   │   │   │   └── EDX.bin
│   │   │   ├── __init__.py
│   │   │   └── build_config.py
│   │   ├── mixedcase/
│   │   │   ├── getpc/
│   │   │   │   ├── countslide/
│   │   │   │   │   ├── i32/
│   │   │   │   │   │   ├── [i32] - ECX.asm
│   │   │   │   │   │   ├── [i32] - ECX.bin
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   └── build_config.py
│   │   │   │   │   ├── rm32/
│   │   │   │   │   │   ├── [EAX+i32] - EDX.asm
│   │   │   │   │   │   ├── [EAX+i32] - EDX.bin
│   │   │   │   │   │   ├── [EBX+i32] - EDX.asm
│   │   │   │   │   │   ├── [EBX+i32] - EDX.bin
│   │   │   │   │   │   ├── [ECX+i32] - EDX.asm
│   │   │   │   │   │   ├── [ECX+i32] - EDX.bin
│   │   │   │   │   │   ├── [EDI+i32] - EDX.asm
│   │   │   │   │   │   ├── [EDI+i32] - EDX.bin
│   │   │   │   │   │   ├── [EDX+i32] - EDX.asm
│   │   │   │   │   │   ├── [EDX+i32] - EDX.bin
│   │   │   │   │   │   ├── [ESI+i32] - EDX.asm
│   │   │   │   │   │   ├── [ESI+i32] - EDX.bin
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── build_config.py
│   │   │   │   │   │   └── build_info.txt
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── build_config.py
│   │   │   │   │   └── readme.txt
│   │   │   │   ├── seh/
│   │   │   │   │   ├── xpsp3/
│   │   │   │   │   │   ├── [ESI].asm
│   │   │   │   │   │   ├── [ESI].bin
│   │   │   │   │   │   ├── __init__.py
│   │   │   │   │   │   ├── build_config.py
│   │   │   │   │   │   ├── ESI+4.asm
│   │   │   │   │   │   └── ESI+4.bin
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── build_config.py
│   │   │   │   ├── __init__.py
│   │   │   │   └── build_config.py
│   │   │   ├── i32/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── build_config.py
│   │   │   │   ├── dwx_IMUL_30_XOR_dwy.asm
│   │   │   │   ├── dwx_IMUL_30_XOR_dwy.bin
│   │   │   │   ├── dwx_IMUL_by.asm
│   │   │   │   └── dwx_IMUL_by.bin
│   │   │   ├── rm32/
│   │   │   │   ├── [EAX].asm
│   │   │   │   ├── [EAX].bin
│   │   │   │   ├── [EBP].asm
│   │   │   │   ├── [EBP].bin
│   │   │   │   ├── [EBX].asm
│   │   │   │   ├── [EBX].bin
│   │   │   │   ├── [ECX].asm
│   │   │   │   ├── [ECX].bin
│   │   │   │   ├── [EDI].asm
│   │   │   │   ├── [EDI].bin
│   │   │   │   ├── [EDX].asm
│   │   │   │   ├── [EDX].bin
│   │   │   │   ├── [ESI].asm
│   │   │   │   ├── [ESI].bin
│   │   │   │   ├── [ESP-4].asm
│   │   │   │   ├── [ESP-4].bin
│   │   │   │   ├── [ESP].asm
│   │   │   │   ├── [ESP].bin
│   │   │   │   ├── __init__.py
│   │   │   │   ├── build_config.py
│   │   │   │   ├── EAX.asm
│   │   │   │   ├── EAX.bin
│   │   │   │   ├── EBP.asm
│   │   │   │   ├── EBP.bin
│   │   │   │   ├── EBX.asm
│   │   │   │   ├── EBX.bin
│   │   │   │   ├── ECX+2.asm
│   │   │   │   ├── ECX+2.bin
│   │   │   │   ├── ECX.asm
│   │   │   │   ├── ECX.bin
│   │   │   │   ├── EDI.asm
│   │   │   │   ├── EDI.bin
│   │   │   │   ├── EDX.asm
│   │   │   │   ├── EDX.bin
│   │   │   │   ├── ESI+4.asm
│   │   │   │   ├── ESI+4.bin
│   │   │   │   ├── ESI+8.asm
│   │   │   │   ├── ESI+8.bin
│   │   │   │   ├── ESI.asm
│   │   │   │   ├── ESI.bin
│   │   │   │   ├── ESP.asm
│   │   │   │   └── ESP.bin
│   │   │   ├── __init__.py
│   │   │   └── build_config.py
│   │   ├── uppercase/
│   │   │   ├── i32/
│   │   │   │   └── howto.txt
│   │   │   ├── rm32/
│   │   │   │   └── ... 省略：包含 EAX/ECX/EDX/EBX/ESP/EBP/ESI/EDI 及内存形式的 .asm/.bin
│   │   │   ├── __init__.py
│   │   │   └── build_config.py
│   │   ├── __init__.py
│   │   └── build_config.py
│   ├── latin_1/
│   │   └── mixedcase/getpc/call/ECX+2.asm 与 ECX+2.bin
│   ├── utf_16/
│   │   └── uppercase/rm32/ 下的 EAX/ECX/EDX/EBX/EBP/ESI/EDI .asm/.bin
│   ├── __init__.py
│   └── build_config.py
├── ALPHA3.cmd
├── ALPHA3.py
├── AGENTS.md
├── AGENTS-cn.md
├── BUILD.txt
├── build_config.py
├── build_info.txt
├── charsets.py
├── COPYRIGHT.txt
├── encode.py
├── io.py
├── older_versions.zip
├── print_functions.py
├── README.md
├── REVIEW.md
├── .gitignore
├── TREE.md
└── NAVIGATION.md
```

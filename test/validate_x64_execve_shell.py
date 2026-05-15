#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import charsets


ENCODER_ARGS = ("x64", "ascii", "mixedcase", "rax")
SHELL_MARKER = b"ALPHA3_EXECVE_SHELL_OK\n"
SHELL_COMMAND = b"printf 'ALPHA3_EXECVE_SHELL_OK\\n'; exit\n"

# Null-free Linux x86_64 shellcode:
#   execve("/bin//sh", ["/bin//sh", NULL], NULL)
#   exit(127) if execve unexpectedly returns.
EXECVE_SHELLCODE_HEX = (
    "4831d25248bb2f62696e2f2f7368534889e752574889e66a3b580f05"
    "6a7f5f6a3c580f05"
)


class ValidationError(RuntimeError):
    pass


def _require_local_execve_environment() -> None:
    machine = platform.machine().lower()
    if platform.system() != "Linux" or machine not in {"x86_64", "amd64"}:
        raise ValidationError("Process-level execve validation requires Linux x86_64")
    if shutil.which("gcc") is None:
        raise ValidationError("Process-level execve validation requires gcc")


def _encode_payload(raw_payload: bytes, temp_dir: Path) -> bytes:
    payload_path = temp_dir / "execve-shell.bin"
    encoded_path = temp_dir / "encoded.bin"
    payload_path.write_bytes(raw_payload)

    command = [
        sys.executable,
        str(REPO_ROOT / "ALPHA3.py"),
        *ENCODER_ARGS,
        f"--input={payload_path}",
        f"--output={encoded_path}",
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValidationError(
            "Encoding failed:\n"
            f"stdout={completed.stdout.decode('latin-1', errors='replace')}\n"
            f"stderr={completed.stderr.decode('latin-1', errors='replace')}"
        )
    if completed.stderr:
        raise ValidationError(
            f"Encoder wrote to stderr: {completed.stderr.decode('latin-1', errors='replace')}"
        )
    return encoded_path.read_bytes()


def _assert_valid_charset(encoded_payload: bytes) -> None:
    valid_bytes = set(charsets.valid_chars["ascii"]["mixedcase"].encode("latin-1"))
    invalid = [
        f"{index}:{byte:02x}"
        for index, byte in enumerate(encoded_payload)
        if byte not in valid_bytes
    ]
    if invalid:
        raise ValidationError(
            "Encoded payload contains non-mixedcase-ascii bytes: " + ", ".join(invalid)
        )


def _compile_harness(encoded_payload: bytes, temp_dir: Path) -> Path:
    byte_values = ", ".join(f"0x{byte:02x}" for byte in encoded_payload)
    source_path = temp_dir / "execve_harness.c"
    binary_path = temp_dir / "execve_harness"
    source_path.write_text(
        f"""#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

static const unsigned char encoded_shellcode[] = {{
  {byte_values}
}};

int main(void) {{
  size_t shellcode_size = sizeof(encoded_shellcode);
  void *region = mmap(0, shellcode_size, PROT_READ | PROT_WRITE | PROT_EXEC,
      MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  if (region == MAP_FAILED) {{
    perror("mmap");
    return 111;
  }}
  memcpy(region, encoded_shellcode, shellcode_size);
  __asm__ volatile (
      "mov %[base], %%rax\\n\\t"
      "call *%[entry]\\n\\t"
      "mov $112, %%edi\\n\\t"
      "mov $60, %%eax\\n\\t"
      "syscall\\n\\t"
      :
      : [base] "r" (region), [entry] "r" (region)
      : "rax", "rdi", "rcx", "r11", "memory");
  __builtin_unreachable();
}}
""",
        encoding="ascii",
    )
    completed = subprocess.run(
        ["gcc", "-Wall", "-Wextra", "-O0", str(source_path), "-o", str(binary_path)],
        cwd=temp_dir,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValidationError(
            "Harness compilation failed:\n"
            f"stdout={completed.stdout.decode('utf-8', errors='replace')}\n"
            f"stderr={completed.stderr.decode('utf-8', errors='replace')}"
        )
    return binary_path


def _run_harness(binary_path: Path) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [str(binary_path)],
            input=SHELL_COMMAND,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ValidationError("Harness timed out waiting for shell command output") from error


def validate() -> dict[str, object]:
    _require_local_execve_environment()
    raw_payload = bytes.fromhex(EXECVE_SHELLCODE_HEX)
    if b"\x00" in raw_payload:
        raise ValidationError("Raw payload must be NULL-free for ALPHA3")

    with tempfile.TemporaryDirectory(prefix="alpha3-execve-shell-") as temp_name:
        temp_dir = Path(temp_name)
        encoded_payload = _encode_payload(raw_payload, temp_dir)
        _assert_valid_charset(encoded_payload)
        harness_path = _compile_harness(encoded_payload, temp_dir)
        completed = _run_harness(harness_path)

    if completed.returncode != 0:
        raise ValidationError(
            f"Harness returned {completed.returncode}, expected shell exit 0:\n"
            f"stdout={completed.stdout!r}\n"
            f"stderr={completed.stderr!r}"
        )
    if completed.stdout != SHELL_MARKER:
        raise ValidationError(
            "Shell command produced unexpected stdout:\n"
            f"expected={SHELL_MARKER!r}\n"
            f"actual={completed.stdout!r}\n"
            f"stderr={completed.stderr!r}"
        )
    if completed.stderr:
        raise ValidationError(f"Shell command wrote to stderr: {completed.stderr!r}")

    return {
        "raw_payload_hex": raw_payload.hex(),
        "encoded_length": len(encoded_payload),
        "encoded_sha256": hashlib.sha256(encoded_payload).hexdigest(),
        "shell_stdout": completed.stdout.decode("ascii"),
    }


def main() -> int:
    result = validate()
    print("Execve shell validation succeeded")
    print(f"encoder={' '.join(ENCODER_ARGS)}")
    print(f"raw_payload_hex={result['raw_payload_hex']}")
    print(f"encoded_length={result['encoded_length']}")
    print(f"encoded_sha256={result['encoded_sha256']}")
    print(f"shell_stdout={result['shell_stdout']!r}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as error:
        print(f"Execve shell validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from unicorn import Uc, UcError, UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_64
from unicorn.x86_const import (
    UC_X86_REG_RAX,
    UC_X86_REG_RBX,
    UC_X86_REG_RBP,
    UC_X86_REG_RCX,
    UC_X86_REG_RDI,
    UC_X86_REG_RDX,
    UC_X86_REG_RIP,
    UC_X86_REG_RSI,
    UC_X86_REG_RSP,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import charsets


ENCODER_ARGS = ("x64", "ascii", "mixedcase", "rax")
DECODER_PATH = REPO_ROOT / "x64" / "ascii" / "mixedcase" / "rm64" / "RAX.bin"

RAW_PAYLOAD_HEX = (
    "31c05048bb666c61672e747874534889e731f66a02580f05974889e66a405a31c00f05"
    "6a015f4889c26a01580f056a3c5831ff0f05"
)
EXPECTED_FILE_NAME = b"flag.txt"
EXPECTED_FILE_DATA = b"alpha3 validation via emulator\n"

CODE_BASE = 0x100000
STACK_BASE = 0x400000
STACK_SIZE = 0x20000


class ValidationError(RuntimeError):
    pass


@dataclass
class OpenFile:
    data: bytes
    offset: int = 0


@dataclass
class EmulatorState:
    payload_entry: int
    encoded_end: int
    phase: str = "decode"
    decode_reached_entry: bool = False
    stdout: bytearray = field(default_factory=bytearray)
    next_fd: int = 3
    fd_table: dict[int, OpenFile] = field(default_factory=dict)
    exit_code: int | None = None


def _read_c_string(uc: Uc, address: int, max_length: int = 0x100) -> bytes:
    data = bytearray()
    for offset in range(max_length):
        byte = bytes(uc.mem_read(address + offset, 1))
        if byte == b"\x00":
            return bytes(data)
        data.extend(byte)
    raise ValidationError("CString was not terminated")


def _handle_syscall(uc: Uc, state: EmulatorState, address: int) -> None:
    syscall_nr = uc.reg_read(UC_X86_REG_RAX) & 0xFFFFFFFFFFFFFFFF
    arg0 = uc.reg_read(UC_X86_REG_RDI) & 0xFFFFFFFFFFFFFFFF
    arg1 = uc.reg_read(UC_X86_REG_RSI) & 0xFFFFFFFFFFFFFFFF
    arg2 = uc.reg_read(UC_X86_REG_RDX) & 0xFFFFFFFFFFFFFFFF
    next_rip = address + 2

    if syscall_nr == 2:  # open
        path = _read_c_string(uc, arg0)
        if path != EXPECTED_FILE_NAME:
            raise ValidationError(f"Unexpected open path: {path!r}")
        fd = state.next_fd
        state.next_fd += 1
        state.fd_table[fd] = OpenFile(EXPECTED_FILE_DATA)
        uc.reg_write(UC_X86_REG_RAX, fd)
    elif syscall_nr == 0:  # read
        fd = arg0 & 0xFFFFFFFF
        if fd not in state.fd_table:
            raise ValidationError(f"Unexpected read fd: {fd}")
        handle = state.fd_table[fd]
        chunk = handle.data[handle.offset : handle.offset + arg2]
        if chunk:
            uc.mem_write(arg1, chunk)
        handle.offset += len(chunk)
        uc.reg_write(UC_X86_REG_RAX, len(chunk))
    elif syscall_nr == 1:  # write
        fd = arg0 & 0xFFFFFFFF
        data = bytes(uc.mem_read(arg1, arg2))
        if fd != 1:
            raise ValidationError(f"Unexpected write fd: {fd}")
        state.stdout.extend(data)
        uc.reg_write(UC_X86_REG_RAX, len(data))
    elif syscall_nr == 60:  # exit
        state.exit_code = arg0 & 0xFFFFFFFF
        uc.reg_write(UC_X86_REG_RAX, 0)
    else:
        raise ValidationError(f"Unexpected syscall number: {syscall_nr}")

    uc.reg_write(UC_X86_REG_RIP, next_rip)
    uc.emu_stop()


def _code_hook(uc: Uc, address: int, size: int, state: EmulatorState) -> None:
    if state.phase == "decode" and address == state.payload_entry:
        state.decode_reached_entry = True
        uc.emu_stop()
        return
    if bytes(uc.mem_read(address, 2)) == b"\x0f\x05":
        _handle_syscall(uc, state, address)


def _encode_payload(raw_payload: bytes) -> bytes:
    with tempfile.TemporaryDirectory(prefix="alpha3-validate-") as temp_dir:
        payload_path = Path(temp_dir) / "payload.bin"
        payload_path.write_bytes(raw_payload)
        command = [
            sys.executable,
            str(REPO_ROOT / "ALPHA3.py"),
            *ENCODER_ARGS,
            f"--input={payload_path}",
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
    return completed.stdout


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


def _build_emulator(encoded_payload: bytes) -> tuple[Uc, EmulatorState]:
    decoder_bytes = DECODER_PATH.read_bytes()
    payload_entry_offset = len(decoder_bytes) - 1
    mapped_code_size = 0x1000 * ((len(encoded_payload) + 0xFFF) // 0x1000 + 1)

    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    uc.mem_map(CODE_BASE, mapped_code_size)
    uc.mem_map(STACK_BASE, STACK_SIZE)
    uc.mem_write(CODE_BASE, encoded_payload)

    uc.reg_write(UC_X86_REG_RIP, CODE_BASE)
    uc.reg_write(UC_X86_REG_RAX, CODE_BASE)
    uc.reg_write(UC_X86_REG_RSP, STACK_BASE + STACK_SIZE - 0x1000)
    uc.reg_write(UC_X86_REG_RBX, 0x4242424242424242)
    uc.reg_write(UC_X86_REG_RBP, 0x4343434343434343)
    uc.reg_write(UC_X86_REG_RCX, 0x4444444444444444)
    uc.reg_write(UC_X86_REG_RDX, 0x4545454545454545)
    uc.reg_write(UC_X86_REG_RSI, 0x1111111111111111)
    uc.reg_write(UC_X86_REG_RDI, 0x2222222222222222)

    state = EmulatorState(
        payload_entry=CODE_BASE + payload_entry_offset,
        encoded_end=CODE_BASE + len(encoded_payload),
    )
    uc.hook_add(UC_HOOK_CODE, _code_hook, state)
    return uc, state


def _run_until_stop(uc: Uc, state: EmulatorState) -> None:
    start = uc.reg_read(UC_X86_REG_RIP)
    uc.emu_start(start, state.encoded_end)


def validate() -> dict[str, object]:
    raw_payload = bytes.fromhex(RAW_PAYLOAD_HEX)
    if b"\x00" in raw_payload:
        raise ValidationError("Raw payload must be NULL-free for ALPHA3")

    encoded_payload = _encode_payload(raw_payload)
    _assert_valid_charset(encoded_payload)

    uc, state = _build_emulator(encoded_payload)
    try:
        _run_until_stop(uc, state)
    except UcError as error:
        raise ValidationError(f"Decoder emulation failed: {error}") from error

    if not state.decode_reached_entry:
        raise ValidationError("Decoder never transferred control to the decoded payload")

    decoded_region = bytes(uc.mem_read(state.payload_entry, len(raw_payload) + 1))
    expected_decoded_region = raw_payload + b"\x00"
    if decoded_region != expected_decoded_region:
        raise ValidationError(
            "Decoded payload mismatch:\n"
            f"expected={expected_decoded_region.hex()}\n"
            f"actual={decoded_region.hex()}"
        )

    state.phase = "execute"
    while state.exit_code is None:
        try:
            _run_until_stop(uc, state)
        except UcError as error:
            raise ValidationError(f"Payload execution failed: {error}") from error

    stdout = bytes(state.stdout)
    if stdout != EXPECTED_FILE_DATA:
        raise ValidationError(
            "ORW payload produced unexpected stdout:\n"
            f"expected={EXPECTED_FILE_DATA!r}\n"
            f"actual={stdout!r}"
        )
    if state.exit_code != 0:
        raise ValidationError(f"Payload exited with {state.exit_code}, expected 0")

    return {
        "raw_payload_hex": raw_payload.hex(),
        "encoded_payload": encoded_payload.decode("ascii"),
        "encoded_length": len(encoded_payload),
        "encoded_sha256": hashlib.sha256(encoded_payload).hexdigest(),
        "payload_entry_offset": state.payload_entry - CODE_BASE,
        "stdout": stdout.decode("ascii"),
    }


def main() -> int:
    result = validate()
    print("Validation succeeded")
    print(f"encoder={' '.join(ENCODER_ARGS)}")
    print(f"raw_payload_hex={result['raw_payload_hex']}")
    print(f"encoded_length={result['encoded_length']}")
    print(f"payload_entry_offset=0x{result['payload_entry_offset']:x}")
    print(f"encoded_sha256={result['encoded_sha256']}")
    print(f"stdout={result['stdout']!r}")
    print(f"encoded_payload={result['encoded_payload']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)

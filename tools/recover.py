"""Extract selected original function metadata and dependency evidence."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64, CS_OP_IMM, CS_OP_MEM
from capstone.x86 import X86_REG_RIP
from macho import MachO

TARGETS = {
    "lua_absindex": "__Z12lua_absindexP9lua_Statei",
    "lua_gettop": "__Z10lua_gettopP9lua_State",
    "lua_settop": "__Z10lua_settopP9lua_Statei",
    "lua_type": "__Z8lua_typeP9lua_Statei",
    "lua_toboolean": "__Z13lua_tobooleanP9lua_Statei",
    "lua_pushnil": "__Z11lua_pushnilP9lua_State",
    "lua_pushnumber": "__Z14lua_pushnumberP9lua_Stated",
    "lua_pushboolean": "__Z15lua_pushbooleanP9lua_Statei",
    "setupCompiler": "__ZN5LuaVM13setupCompilerERN4Luau14CompileOptionsE",
    "compileWrapper": "__ZN5LuaVM7compileERKNSt3__112basic_stringIcNS0_11char_traitsIcEENS0_9allocatorIcEEEENS_13CompileTargetEi",
    "loadWrapper": "__ZN5LuaVM4loadEP9lua_StateRKN3RBX15ProtectedStringEPKcii",
    "Instance_new": "__ZN3RBX3Lua14InstanceBridge11newInstanceEP9lua_State",
    "Instance_register": "__ZN3RBX3Lua14InstanceBridge13registerClassEP9lua_State",
    "lua_newstate": "__Z12lua_newstatePFPvS_S_mmES_",
    "luaL_newstate": "__Z13luaL_newstatev",
    "lua_close": "__Z9lua_closeP9lua_State",
    "luaD_rawrunprotected": "__Z20luaD_rawrunprotectedP9lua_StatePFvS0_PvES1_",
    "stack_init": "__ZL10stack_initP9lua_StateS0_",
    "f_luaopen": "__ZL9f_luaopenP9lua_StatePv",
    "close_state": "__ZL11close_stateP9lua_State",
    "luaM_new_": "__Z9luaM_new_P9lua_Statemh",
    "luaS_hash": "__Z9luaS_hashPKcm",
    "luau_load": "__Z9luau_loadP9lua_StatePKcS2_mi",
    "lua_pcall": "__Z9lua_pcallP9lua_Stateiii",
    "SizeClassConfig": "__ZN15SizeClassConfigC2Ev",
    "newblock": "__ZL8newblockP9lua_Statei",
    "newpage": "__ZL7newpageP9lua_StatePP8lua_Pageiii",
    "newclasspage": "__ZL12newclasspageP9lua_StatePP8lua_PageS3_hb",
    "luaM_free_": "__Z10luaM_free_P9lua_StatePvmh",
    "luaM_realloc_": "__Z13luaM_realloc_P9lua_StatePvmmh",
    "freeblock": "__ZL9freeblockP9lua_StateiPv",
    "freepage": "__ZL8freepageP9lua_StatePP8lua_PageS2_",
    "freeclasspage": "__ZL13freeclasspageP9lua_StatePP8lua_PageS3_S2_h",
    "freestack": "__ZL9freestackP9lua_StateS0_",
    "luaM_newgco_": "__Z12luaM_newgco_P9lua_Statemh",
    "luaM_freegco_": "__Z13luaM_freegco_P9lua_StateP8GCObjectmhP8lua_Page",
    "luaS_resize": "__Z11luaS_resizeP9lua_Statei",
    "luaS_newlstr": "__Z12luaS_newlstrP9lua_StatePKcm",
    "luaT_init": "__Z9luaT_initP9lua_State",
    "luaH_new": "__Z8luaH_newP9lua_Stateii",
    "setarrayvector": "__ZL14setarrayvectorP9lua_StateP8LuaTablei",
    "setnodevector": "__ZL13setnodevectorP9lua_StateP8LuaTablei",
    "luaO_log2": "__Z9luaO_log2j",
}
SOURCE_FILES = ["script/LuaVM.c", "script/InstanceBridge.c", "_free/_free_l.part001.c",
                "_free/_free_l.part002.c", "_free/_free_s.part007.c",
                "_free/_free_f.part001.c", "_free/_free_c.part082.c",
                "_free/_free_n.part004.c", "_external/_s/SizeClassConfig.c"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--dump", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    addresses, source_records = {}, {}
    for relative in SOURCE_FILES:
        source = (args.dump / relative).read_text(encoding="utf-8")
        for match in re.finditer(r"^// Address: (0x[0-9a-fA-F]+) \| Name: (.+)$", source, re.M):
            name = match[2].strip()
            if name in TARGETS.values():
                address = int(match[1], 16)
                addresses[name] = address
                source_records[name] = {"file": relative, "line": source.count("\n", 0, match.start())+1}
    assert set(addresses) == set(TARGETS.values()), "Some target functions are missing from the dump"
    disassembler = Cs(CS_ARCH_X86, CS_MODE_64)
    disassembler.detail = True
    with MachO(args.binary) as binary:
        required_addresses = set(addresses.values())
        functions = {}
        for label, name in TARGETS.items():
            address = addresses[name]
            code = binary.function_bytes(address)
            instructions, calls, references = [], [], set()
            for instruction in disassembler.disasm(code, address):
                entry = {"address": hex(instruction.address), "bytes": instruction.bytes.hex(),
                         "mnemonic": instruction.mnemonic, "operands": instruction.op_str}
                instructions.append(entry)
                if instruction.mnemonic == "call":
                    target = instruction.operands[0]
                    if target.type == CS_OP_IMM:
                        calls.append({"site": hex(instruction.address), "target": hex(target.imm)})
                        required_addresses.add(target.imm)
                    else: calls.append({"site": hex(instruction.address), "indirect": instruction.op_str})
                for operand in instruction.operands:
                    if operand.type == CS_OP_MEM and operand.mem.base == X86_REG_RIP:
                        references.add(instruction.address + instruction.size + operand.mem.disp)
            required_addresses.update(references)
            functions[label] = {"name": name, "address": hex(address), "size": len(code),
                "sha256": hashlib.sha256(code).hexdigest(), "source": source_records[name],
                "instructions": instructions, "calls": calls, "data_references": [hex(item) for item in sorted(references)]}
        symbols = {}
        constants = {}
        for name, address, kind, section in binary.symbols():
            if address in required_addresses:
                symbols.setdefault(address, []).append(name.decode("utf-8", "replace"))
            if b"kSpecialGlobals" in name or b"kLibrariesWithConstants" in name or b"kUserdataCompileTypes" in name:
                constants[name.decode("utf-8", "replace")] = hex(address)
        for function in functions.values():
            assert function["name"] in symbols.get(int(function["address"], 16), []), "Binary/dump symbol mismatch"
            for call in function["calls"]:
                if "target" in call: call["symbols"] = symbols.get(int(call["target"], 16), [])
        arrays = {}
        for name, text_address in constants.items():
            values = []
            address = int(text_address, 16)
            for index in range(128):
                pointer = struct.unpack("<Q", binary.read(address+index*8, 8))[0]
                if pointer == 0: break
                try: value = binary.string(pointer)
                except (ValueError, UnicodeDecodeError):
                    values.append({"unresolved_pointer": hex(pointer)})
                    break
                values.append(value)
            arrays[name] = {"address": text_address, "values": values}
        report = {"binary": str(args.binary.resolve()), "dump": str(args.dump.resolve()),
            "function_count": len(functions), "functions": functions,
            "compiler_arrays": arrays, "reference_symbols": {hex(k): v for k, v in symbols.items()}}
        (args.out / "recovery.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        for label, function in functions.items():
            listing = [f"; {function['name']}", f"; original address {function['address']}, source {function['source']}"]
            for instruction in function["instructions"]:
                listing.append(f"{instruction['address']}: {instruction['bytes']:24} {instruction['mnemonic']:8} {instruction['operands']}")
            (args.out / f"{label}.asm.txt").write_text("\n".join(listing)+"\n", encoding="utf-8")
        print(json.dumps({"functions_verified": len(functions), "compiler_arrays": arrays,
            "Instance_new_direct_calls": len(functions["Instance_new"]["calls"]),
            "report": str(args.out / "recovery.json")}, indent=2))


if __name__ == "__main__": main()

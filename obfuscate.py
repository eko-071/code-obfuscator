#!/usr/bin/env python3

import re
import sys
import argparse
import random
from collections import OrderedDict

# CONFIGURATION
LEVELS = ["mild", "moderate", "extreme"]

# Identifiers that must never be renamed
RESERVED = {
    # C keywords
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "int", "long", "register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while",
    # Standard library
    "printf", "scanf", "malloc", "free", "strlen", "strcpy", "strcmp", "memcpy",
    "fopen", "fclose", "fread", "fwrite", "exit", "NULL", "stdin", "stdout", "stderr",
    # Entry point
    "main"
}

# Visually confusing names for extreme mode (all valid C identifiers)
CONFUSING = [
    "O0", "l1", "Il", "lI", "O0l", "l1I", "I1l", "OO0", "ll1", "Ill", "lll", "III",
    "oO0", "O0o", "_O", "_0", "_l", "_I", "__O", "__0", "__l", "__I", "O_0", "l_1",
    "I_l", "_O0", "_l1", "_Il", "OOO", "lll1", "IlI", "lIl", "IIl", "O0O0", "l1l1",
    "IlIl", "O00O", "l11l", "oOoO", "Oo0O", "oO0o", "lO0l", "IlO0", "OlIl", "lIO0",
    "O0Il", "Il0O", "lO0I"
]

# Tokenizer regex — captures all C token types
TOKEN_REGEX = re.compile(
    r'(?P<comment>/\*.*?\*/|//[^\n]*)|'
    r'(?P<string>"(?:[^"\\]|\\.)*")|'
    r'(?P<charlit>\'(?:[^\'\\]|\\.)*\')|'
    r'(?P<preproc>^\#[^\n]*)|'
    r'(?P<number>0[xX][0-9a-fA-F]+|0[0-7]+|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)|'
    r'(?P<ident>[A-Za-z_]\w*)|'
    r'(?P<op><<=|>>=|<<|>>|->|&&|\|\||[+\-*/%&|^~!<>=?:]=?|==|!=|<=|>=|\+\+|--)|'
    r'(?P<punct>[{}()\[\];,.])|'
    r'(?P<ws>\s+)',
    re.VERBOSE | re.MULTILINE | re.DOTALL
)

# TOKENIZATION
def tokenize(code):
    return [(m.lastgroup, m.group()) for m in TOKEN_REGEX.finditer(code)]

def detokenize(tokens):
    return "".join(value for _, value in tokens)

# NAME GENERATION
def generate_names(count, style):
    """Generate obfuscated variable names."""
    if style == "mild":
        pool = list("xyzqwkjvnmftbpdr") + [a + b for a in "xyzqw" for b in "0123456789"]
    elif style == "moderate":
        pool = [p + b for p in ["_", "__", "___"] for b in "xyzqwkjvnmftbpdr0123456789"]
    else:  # extreme
        pool = list(CONFUSING)
        while len(pool) < count:
            pool.append(random.choice(CONFUSING) + random.choice(["_", "0", "1"]))
    random.shuffle(pool)
    return pool[:count]

# TRANSFORMATION PASSES
def strip_comments(tokens):
    return [(k, v) for k, v in tokens if k != "comment"]

def rename_identifiers(tokens, level):
    # Find all renameable identifiers (frequency-sorted)
    freq = OrderedDict()
    for kind, value in tokens:
        if kind == "ident" and value not in RESERVED:
            freq[value] = freq.get(value, 0) + 1
    
    # Generate mapping (most frequent get shortest names)
    sorted_idents = sorted(freq.items(), key=lambda x: -x[1])
    names = generate_names(len(sorted_idents), level)
    mapping = {orig: names[i] for i, (orig, _) in enumerate(sorted_idents)}
    
    # Apply mapping
    renamed = []
    for kind, value in tokens:
        if kind == "ident" and value in mapping:
            renamed.append((kind, mapping[value]))
        else:
            renamed.append((kind, value))
    
    return renamed, mapping

def compress_whitespace(tokens, level):
    """Collapse whitespace based on level."""
    result = []
    for i, (kind, value) in enumerate(tokens):
        if kind != "ws":
            result.append((kind, value))
            continue
        
        prev = result[-1] if result else ("", "")
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ("", "")
        
        if level in ("mild", "moderate"):
            result.append(("ws", "\n" if "\n" in value else " "))
        else:  # extreme
            # Always preserve newlines around preprocessor directives
            if nxt[0] == "preproc" or prev[0] == "preproc":
                result.append(("ws", "\n"))
            # Keep space between adjacent identifiers/numbers
            elif prev[0] in ("ident", "number") and nxt[0] in ("ident", "number"):
                result.append(("ws", " "))
            # Otherwise drop whitespace
    
    return result

def flatten_code(code, level):
    """Collapse code to minimum lines (extreme only)."""
    if level != "extreme":
        return code
    
    lines = code.split("\n")
    result = []
    buffer = ""
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if buffer:
                result.append(buffer.strip())
                buffer = ""
            result.append(stripped)
        else:
            buffer += " " + stripped
    
    if buffer:
        result.append(buffer.strip())
    
    return "\n".join(result)

def inject_macros(code, level):
    """Insert macro definitions for operators."""
    if level == "mild":
        return code
    
    macros = [
        "#define _OB_A(a,b) ((a)+(b))",
        "#define _OB_S(a,b) ((a)-(b))",
        "#define _OB_M(a,b) ((a)*(b))",
        "#define _OB_LT(a,b) ((a)<(b))",
        "#define _OB_GT(a,b) ((a)>(b))",
        "#define _OB_EQ(a,b) ((a)==(b))",
        "#define _OB_N(a) (!(a))"
    ]
    
    # Replace operators with macros (only outside strings)
    parts = re.split(r'("(?:[^"\\]|\\.)*")', code)
    for i in range(0, len(parts), 2):  # Only even indices (non-strings)
        parts[i] = re.sub(r'\b(\w+)\s*\+\s*(\w+)\b', r'_OB_A(\1,\2)', parts[i])
        parts[i] = re.sub(r'\b(\w+)\s*\-\s*(\w+)\b', r'_OB_S(\1,\2)', parts[i])
        parts[i] = re.sub(r'\b(\w+)\s*\*\s*(\w+)\b', r'_OB_M(\1,\2)', parts[i])
    code = "".join(parts)
    
    # Insert macros after last #include
    lines = code.split("\n")
    insert_pos = next((i + 1 for i, l in enumerate(lines) if l.strip().startswith("#include")), 0)
    for macro in reversed(macros):
        lines.insert(insert_pos, macro)
    
    return "\n".join(lines)

def obfuscate_numbers(code, level):
    """Replace numbers with equivalent expressions (extreme only)."""
    if level != "extreme":
        return code
    
    def replace(match):
        n = int(match.group(0))
        choices = [str(n)]
        
        if n >= 0:
            choices.append(hex(n))
        if 0 < n < 256:
            choices.append(f"0{oct(n)[2:]}")  # C octal: 0-prefix
            choices.append(f"(0xFF&{hex(n)})")
        if n > 1:
            a, b = random.randint(1, n - 1), 0
            b = n - a
            choices.append(f"({a}+{b})")
        if n > 0 and (n & (n - 1)) == 0:  # Power of 2
            choices.append(f"(1<<{n.bit_length() - 1})")
        
        return random.choice(choices)
    
    # Only replace outside strings
    parts = re.split(r'("(?:[^"\\]|\\.)*")', code)
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(r'\b(\d+)\b', replace, parts[i])
    
    return "".join(parts)

# MAIN PIPELINE
def obfuscate(code, level="moderate"):
    # Tokenize
    tokens = tokenize(code)
    
    # Strip comments
    tokens = strip_comments(tokens)
    
    # Rename identifiers
    tokens, mapping = rename_identifiers(tokens, level)
    
    # Compress whitespace
    tokens = compress_whitespace(tokens, level)
    
    # Back to string
    code = detokenize(tokens)
    
    # String-level transforms
    code = flatten_code(code, level)
    code = inject_macros(code, level)
    code = obfuscate_numbers(code, level)
    
    return code, mapping

# CLI
def main():
    parser = argparse.ArgumentParser(description="C code obfuscator")
    parser.add_argument("input", nargs="?", help="Input file (omit for stdin)")
    parser.add_argument("-o", "--output", help="Output file (omit for stdout)")
    parser.add_argument("-l", "--level", default="moderate", choices=LEVELS)
    parser.add_argument("--map", action="store_true", help="Show rename map")
    parser.add_argument("--levels", action="store_true", help="List levels")
    args = parser.parse_args()
    
    if args.levels:
        print("\nObfuscation levels:\n")
        print("  mild     — Rename vars, strip comments, compress whitespace")
        print("  moderate — mild + macro-based operator obfuscation")
        print("  extreme  — moderate + number tricks, line flattening\n")
        return
    
    # Read input
    if args.input:
        with open(args.input) as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    
    # Obfuscate
    result, mapping = obfuscate(code, args.level)
    
    # Show mapping if requested
    if args.map:
        max_len = max(len(k) for k in mapping) if mapping else 0
        print(f"\n{len(mapping)} identifiers renamed:\n")
        for orig, obf in mapping.items():
            print(f"  {orig:<{max_len}}  →  {obf}")
        print()
    
    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
# Code Obfuscator

A simple code obfuscator written in Python. It converts perfectly legible C code into unreadable spaghetti code.

## Features

- Token-based C lexer
- Identifier renaming
- Comment stripping
- Whitespace compression
- Macro-based operator obfuscation
- Number obfuscation (hex, octal, bitshifts, arithmetic)
- Line flattening

## Purpose

- Horrify your friends with illegible code (you probably don't need a program's help with that)
- Ensure that your employers will never want to lay you off

## Usage

No dependencies required.

```bash
git clone https://github.com/eko-071/code-obfuscator
cd code-obfuscator
```

```bash
python obfuscate.py input.c                 # moderate level, stdout
python obfuscate.py input.c -o output.c     # write to file
python obfuscate.py input.c -l extreme      # maximum obfuscation
python obfuscate.py input.c --map           # show rename mapping
python obfuscate.py --levels                # list levels
```

## Obfuscation Levels

1. **mild** — Rename variables, strip comments, compress whitespace  
2. **moderate** — mild + macro-based operator obfuscation  
3. **extreme** — moderate + number tricks, line flattening, confusing identifiers

C keywords, standard library functions, and `main` are never renamed.

## Example

Sample C code to calculate the first n Fibonacci numbers:

```c
#include <stdio.h>

int fibonacci(int n) {
    if (n <= 0) return 0;
    if (n == 1) return 1;
    int prev = 0;
    int curr = 1;
    for (int i = 2; i <= n; i++) {
        int next = prev + curr;
        prev = curr;
        curr = next;
    }
    return curr;
}

int main() {
    for (int i = 0; i < 10; i++) {
        printf("fib(%d) = %d\n", i, fibonacci(i));
    }
    return 0;
}
```

**Mild level:**
```c
#include <stdio.h>
int x5(int w9) {
if (w9 <= 0) return 0;
if (w9 == 1) return 1;
int f = 0;
int w1 = 1;
for (int q = 2; q <= w9; q++) {
int q6 = f + w1;
f = w1;
w1 = q6;
}
return w1;
}
int main() {
for (int q = 0; q < 10; q++) {
printf("fib(%d) = %d\n", q, x5(q));
}
return 0;
}
```

**Moderate level:**
```c
#include <stdio.h>
#define _OB_A(a,b) ((a)+(b))
#define _OB_S(a,b) ((a)-(b))
#define _OB_M(a,b) ((a)*(b))
#define _OB_LT(a,b) ((a)<(b))
#define _OB_GT(a,b) ((a)>(b))
#define _OB_EQ(a,b) ((a)==(b))
#define _OB_N(a) (!(a))
int _3(int __m) {
if (__m <= 0) return 0;
if (__m == 1) return 1;
int ___0 = 0;
int ___q = 1;
for (int _q = 2; _q <= __m; _q++) {
int _0 = _OB_A(___0,___q);
___0 = ___q;
___q = _0;
}
return ___q;
}
int main() {
for (int _q = 0; _q < 10; _q++) {
printf("fib(%d) = %d\n", _q, _3(_q));
}
return 0;
}
```

**Extreme level:**
```c
#include <stdio.h>
#define _OB_A(a,b) ((a)+(b))
#define _OB_S(a,b) ((a)-(b))
#define _OB_M(a,b) ((a)*(b))
#define _OB_LT(a,b) ((a)<(b))
#define _OB_GT(a,b) ((a)>(b))
#define _OB_EQ(a,b) ((a)==(b))
#define _OB_N(a) (!(a))
int __l(int O0Il){if(O0Il<=0x0)return 0;if(O0Il==(0xFF&0x1))return 0x1;int _O0=0;int oO0=01;for(int lO0I=(0xFF&0x2);lO0I<=O0Il;lO0I++){int l1l1=_OB_A(_O0,oO0);_O0=oO0;oO0=l1l1;}return oO0;}int main(){for(int lO0I=0x0;lO0I<012;lO0I++){printf("fib(%d) = %d\n",lO0I,__l(lO0I));}return 0x0;}
```
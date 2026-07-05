---
title: compile_commands.json setup
layout: default
nav_order: 3
---

# compile_commands.json setup

The clang backend needs a compilation database — a `compile_commands.json` that
records the exact command used to compile each translation unit. Most C/C++
build systems can emit one.

## Why it is needed

Header resolution depends on include paths (`-I`), defines (`-D`), and the
language standard. Without them a scanner is guessing. The compile database
hands the preprocessor the same flags the compiler used, so includes resolve
correctly.

## Generating it

**CMake** — add one flag:

```bash
cmake -S . -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

CMake writes `build/compile_commands.json`.

**Ninja**:

```bash
ninja -t compdb > compile_commands.json
```

**Make and others** — use [Bear](https://github.com/rizsotto/Bear):

```bash
bear -- make
```

## Pointing uzcy at it

In `auto` mode, `uzcy` searches for `compile_commands.json` at the root and then
recursively. To be explicit:

```bash
uzcy run --path . --compile-db build/compile_commands.json
```

## No database?

Then skip it. `auto` mode falls back to the [text backend](backends.md), which
needs no setup and works on any tree — with the accuracy limits noted there.

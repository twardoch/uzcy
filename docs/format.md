---
title: used_by block format
layout: default
nav_order: 4
---

# used_by block format

The block is a contract. `uzcy` writes it, reads it back, and rewrites it —
so its shape is fixed.

## Shape

```c
// <used_by>
// - path/to/first_user.c
// - path/to/second_user.h
// </used_by>
```

- Opens with a line whose stripped content is exactly `// <used_by>`.
- One `// - <path>` line per file that directly includes this one.
- Closes with a line whose stripped content is exactly `// </used_by>`.
- Paths are POSIX, relative to the scanned root, sorted, de-duplicated.

## Placement

On the first run, the block is inserted after any leading comment header (a
run of `//` lines, or a `/* ... */` banner) and the blank line that follows it.
If there is no header, it goes at the very top. A blank line is kept between the
block and the first line of code.

## Idempotency

`uzcy` finds an existing block by its `// <used_by>` / `// </used_by>` markers
and replaces its contents. Running twice with no code change leaves the file
byte-for-byte identical — including its original line endings (`\n` or `\r\n`)
and trailing newline.

## Removal

If a file is no longer included by anything, its block is removed on the next
run. Files that never had a block and have no users are left untouched.

## Safety

Writes are atomic: `uzcy` writes a temp file in the same directory and replaces
the original, so an interrupted run never leaves a half-written source file.
Pass `--backup DIR` to copy originals before editing.

# FORCE TNUM

This script forces the 'tnum' (tabular numbers) feature in a font by using `pyftsubset` to create a new font file with the 'tnum' feature enabled by default.

### Why does this script exist?

Because Canva is a stupid piece of software that does not support the 'tnum' feature in fonts, and there is no way to force it to use tabular numbers. This script creates a new font file that has the 'tnum' feature enabled by default, allowing you to use tabular numbers in Canva (or any other software that does not support the 'tnum' feature).

**Why?** – because tabular numbers just look better for some fonts

### How to use this script

```bash
uv run force_tnum.py <path_to_font_file>
```

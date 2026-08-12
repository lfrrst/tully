# The per-function entry

Four labelled paragraphs, in this order, every time. Consistency across sections
is what makes the finished document usable as a reference rather than readable as
an essay.

### <exact signature, as written>

**What it does.** The business purpose, one or two sentences a partner could
read.

**How it does it.** The actual mechanism — the algorithm, the order of
operations, the masks, the fallback ladder — with `file.ext:NNN` citations, each
verified by reading the file at that line. Where the mechanism has a worked
consequence, work it: a numeric example beats a description.

**What it relies on.** The load-bearing assumptions, specifically. "Assumes the
column is named exactly X" is useful; "assumes valid input" is not. Column
names, file shapes, dtypes, upstream state, config keys, ordering relative to
other calls.

**Failure modes.** What happens when the reliance is violated. Does it raise,
silently coerce, drop rows, return empty? Say which.

## The depth target

The natural failure here is writing an essay about the code instead of a
reference to it. Three elegant paragraphs summarising what a module does will
read better than twenty entries and will be useless to the maintainer who needs
to know what one particular function assumes.

Check a section against these before considering it finished:

- **A heading per function**, matching the actual name, so the document is
  searchable by symbol.
- **All four labels under each**, in the same order.
- **Roughly one line citation per 50 words.** Below that the document has
  stopped being anchored to the code; a section carrying two citations for a
  400-line module was written from memory.
- **Private helpers included** where they carry real logic. These are frequently
  where the finding is, because nobody reviews them.

For a 10,000-line tool the finished code review runs 40,000–60,000 words. That
is fine — it is a reference, not an essay. What is not fine is padding it with
restatement: every paragraph should carry a fact a reader could not get from the
code faster themselves.

If a section is short because the module genuinely is, say so and move on. If it
is short because it summarises, go back.

## Module-level material

Module-level constants, hard-coded account numbers, default configurations and
sentinel values get their own subsections. They are what someone changes, and
they are where a change does damage.

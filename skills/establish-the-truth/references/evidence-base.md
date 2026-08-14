# The evidence base

Every figure in every deliverable is quoted from this file, and every figure in
this file names the run it came from. That is the whole point of it: the most
common error a verification pass catches is a figure that was true of a
different run, and a manifest that makes the run identifier a structural
requirement rather than a convention removes the possibility.

Write it to `evidence/01-evidence-base.md`. Fields in this order.

## Header

    TOOL: <name as the user calls it>
    VERSION: <as stamped by the tool at runtime, not as documented>
    STAGED-AT: <the scratch path the code was copied to>
    EXECUTED: yes | no
    REASON-NOT-EXECUTED: <required when EXECUTED is no; omit otherwise>
    OWN-TEST-SUITE: PASS <n> / FAIL <n> | ABSENT

`VERSION` is the runtime stamp, not the changelog's. Archived runs are routinely
produced by older builds than the one deployed, and a review that assumes
otherwise is reviewing something nobody is using.

`OWN-TEST-SUITE` carries the exact count. The most quotable sentence in a review
of this kind is usually "all N of its own assertions pass against the defect
below", and it needs N.

## Inputs

One row per input actually used.

    | Input | Path | Real or synthetic | Notes |

A review run on synthetic data proves the code runs; it does not tell you what
the client's file will do. Where an input is synthetic, say so here, because
every figure derived from it inherits the qualification.

## Runs

One section per run, at least two.

    ### RUN <run-id>
    SETTINGS: <the settings that make this run different from the others>
    PATH: evidence/runs/<run-id>/

    FIGURES
    | Figure | Value | How measured |

"How measured" is a command or an operation, not an adjective — `wc -l on
output.csv minus the header`, `sum of column AMOUNT in the deliverable`,
`count of rows where ACCOUNT is blank`. If it cannot be written as an
operation, it was not measured.

Pick settings that exercise genuinely different paths — a different mode, a
different period, a different population. Two runs give you a comparison; one
gives you an anecdote.

## Unreconciled observations

    | # | What the run said or produced | Why it could not be reconciled |

Anything the run says that cannot be tied to something: a warning naming a
mechanism, a figure that disagrees with the documentation, a file the docs say
exists that does not. Each of these is a thread, and they are where the best
findings come from. Record them here without resolving them — resolution is the
finding hunt's job, and an observation resolved too early is an observation
nobody else can re-examine.

## When the tool cannot be executed

Write the file anyway, with `EXECUTED: no` and the reason. Then say plainly, at
the top of every deliverable that follows, that no figure in it was verified by
execution. A review that cannot run the thing is worth much less, and the reader
must know that before they rely on it.

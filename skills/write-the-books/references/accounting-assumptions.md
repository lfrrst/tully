# Accounting assumptions

The standard list every checklist starts from. Work it in order, every time, and give every item a verdict. The list is fixed so that every engagement starts from the same thinking. The verdicts are what make each book specific to its own project.

Each item gives the **definition**, meaning the accounting assumption itself, stated in general terms; **for the tool**, meaning what to establish about this deliverable; **in the code**, meaning where a tool puts the assumption into effect; and **feeds**, the audit assertions it bears on, as defined in `audit-assertions.md`. The conventional basic assumptions and principles (economic entity, going concern, time period and the rest) are placed inside these twelve rather than listed separately. The table at the end shows where each one is worked.

## How to work it

**Every item gets one of two verdicts.**

- **Applies.** Say how this deliverable relies on the assumption and where the tool puts it into effect: a setting from the evidence base, with its `RUN`, or a `file.ext:NNN` citation from the layer maps. Every test in PARTs A to C traces to an item marked applies, to a finding, or to a control.
- **Does not apply.** Give one fact about this deliverable that anyone can check, such as "single currency: the source trial balance has no currency column and every amount is in USD". Write no test for it.

"Not considered" is not a verdict, and an item with no verdict reads as one that was checked and found irrelevant. Where you cannot tell whether an item applies, it applies, and finding out is the first test written for it.

**The list is a floor, not a ceiling.** If the project rests on an assumption that none of these covers, add it as a row after item 12, with the same two fields. Don't bend it to fit the nearest item. If the same extra keeps turning up across engagements, propose it for this file.

**Where the verdicts go.** A table in checklist §1, with one row per item: the assumption, the verdict, how the deliverable relies on it or the fact that rules it out, and the IDs of the tests that trace to it. All twelve rows go in, including the ones that do not apply, because the reviewer needs to see that the whole list was considered.

## The list

### 1. Reporting entity

**Definition.** The economic entity assumption. An entity's transactions are accounted for separately from those of its owners and of every other entity, so a set of books describes one entity and nothing else. In a group, the reporting entity can be a consolidation of several legal entities, and its boundary is whatever the financial statements say it is.

**For the tool.** Whose books these are, and where the entity boundary sits: company codes, intercompany balances, consolidation or elimination, and any balance that could land in the wrong entity.

*In the code:* entity or company fields, filters on them, and any join that crosses entities. *Feeds:* rights and obligations, existence.

### 2. Basis of accounting

**Definition.** The framework the amounts are prepared under: US GAAP, IFRS, the income-tax basis, cash or modified cash, or another special-purpose framework. Under GAAP and IFRS the basis includes two basic assumptions. The accrual assumption means revenue is recognised when earned and expense when incurred, not when cash moves. The going-concern assumption means the entity is expected to keep operating for the foreseeable future. Where going concern fails, the liquidation basis replaces it, and measurement changes with it.

**For the tool.** Which basis the source is on, which basis the target expects, and whether they are the same. Also whether any step converts between bases, for example cash to accrual or book to tax.

*In the code:* mode flags and basis switches, and adjustments that only make sense on one basis. *Feeds:* accuracy, presentation.

### 3. Period, cutoff and effective date

**Definition.** The time-period (periodicity) assumption. The entity's life is divided into defined reporting periods, and every transaction belongs to exactly one of them. Cutoff is the practical test of that: whether each item is recorded in the period in which it occurred.

**For the tool.** The as-of date, the period end, the fiscal calendar, posting date against transaction date, and the time zone of every timestamp.

*In the code:* date parsing, default dates (a default of today is a common defect), and how the period is derived. *Feeds:* cutoff.

### 4. Currency

**Definition.** The monetary-unit assumption, also called the stable-dollar assumption. Transactions are recorded in a single unit of money whose purchasing power is treated as stable, so amounts from different dates can be added together without adjusting for inflation. Where an entity transacts in more than one currency, a functional currency is chosen, and other currencies are translated or remeasured into it at defined rates. The stable-unit assumption breaks down in a highly inflationary economy, where the standards require a different treatment.

**For the tool.** The functional and presentation currencies, where the exchange rates come from, which date they are taken at, and whether the tool translates or remeasures.

*In the code:* rate lookups, currency columns, and any amount multiplied by something that is not a constant. *Feeds:* accuracy, valuation.

### 5. Sign convention

**Definition.** Double entry. Every transaction has equal debits and credits, and each account has a natural balance: debit for assets and expenses, credit for liabilities, equity and revenue. Contra accounts carry the balance opposite to the account they reduce. A sign convention is how a file represents all of this, and every system that reads the file has to share it.

**For the tool.** How the source and the target each represent debits and credits (signed amounts, separate columns, DR/CR flags, parentheses), whether the tool converts between them, and how it treats contra accounts.

*In the code:* the parser for amount columns, and any hard-coded list of accounts whose sign is flipped. *Feeds:* accuracy, classification.

### 6. Chart of accounts mapping

**Definition.** The chart of accounts is the entity's list of accounts, and it decides where every amount is classified. A mapping carries each source account to a target account. The assumption is that the map is complete and correct, so every amount lands in an account of the same nature: an asset in an asset account, an expense in the right expense line.

**For the tool.** Who maintains the map, whether it covers every source account on the reference runs, what happens to an unmapped account (whether it is rejected, defaulted, or sent to suspense), and where many source accounts merge into one.

*In the code:* the mapping table, its lookup, and its fallback branch. *Feeds:* classification, existence.

### 7. Dimensions and attributes

**Definition.** Everything recorded about an amount besides the account and the figure: department, fund, class, project, location, tax code, and restrictions imposed by a donor or a contract. These attributes drive segment reporting, net-asset classes, tax and disclosure. Under the full-disclosure principle, any attribute that bears on the financial statements or the notes has to survive to them.

**For the tool.** Which attributes the deliverable carries, and for each one whether the tool takes it from the source or supplies a default.

*In the code:* segment builders, and positional configuration that depends on column order. *Feeds:* classification, and rights and obligations where a restriction is involved.

### 8. Measurement, valuation and allocation

**Definition.** How an amount is arrived at when it is computed rather than observed: historical cost, fair value, estimates such as accruals and allowances, depreciation and amortisation, and allocations of shared costs on a stated basis. Two principles govern it. Conservatism, or prudence, means that under uncertainty an estimate should not overstate assets or income. Consistency means a method, once chosen, is applied the same way from period to period.

**For the tool.** Anything the tool computes rather than carries. If it only moves numbers from one place to another, say so. That is often the most important "does not apply" in the book, because it sets the limits of what the review can conclude.

*In the code:* any arithmetic that produces a new amount, as opposed to arithmetic that moves an existing one. *Feeds:* accuracy, valuation and allocation.

### 9. Precision and rounding

**Definition.** Amounts are stated to a defined precision, usually the currency's smallest unit, and rounded by a defined method. Rounding is expected to create only immaterial differences. A total either equals the sum of the rounded amounts it presents, or the difference sits on a documented rounding line.

**For the tool.** Decimal places, the rounding method, where in the pipeline rounding happens, how a rounding residual is handled, and whether amounts are held as floats or decimals.

*In the code:* numeric types, round calls, and the place where totals are compared. *Feeds:* accuracy.

### 10. Population and exclusions

**Definition.** The reliability and objectivity principles, as they bear on a tool. Every recorded item is supported by a source record that can be verified, the records the tool starts from are the whole population they claim to be, and anything left out is left out on purpose, by a stated rule, and recorded.

**For the tool.** What the source population is, what is excluded on purpose (zero balances, inactive accounts, amounts under a threshold), and where each exclusion is recorded.

*In the code:* filters, and anything that drops rows. *Feeds:* completeness, occurrence.

### 11. Aggregation and netting

**Definition.** Presentation. Amounts are summarised to a level that is useful without hiding what a reader needs. Assets and liabilities, and income and expense, are not offset against each other unless the framework permits it. The full-disclosure principle applies here too, because a netted figure can hide an item that has to be shown.

**For the tool.** Whether the deliverable is detail or summary, what the grouping keys are, and whether offsetting items are netted before output.

*In the code:* group-by operations and sums that run before the writer. *Feeds:* presentation, classification.

### 12. Continuity with the prior position

**Definition.** Each period's opening balances are the prior period's closing balances, and methods are applied consistently between periods, so the statements are comparable over time. A change in method, or a correction of an error, is accounted for and disclosed as such, and is never silently absorbed into the opening balances.

**For the tool.** Whether the opening position agrees to the last closed or audited figures, and whether a roll-forward from there holds.

*In the code:* usually nothing, and that absence is the reason it is on the list. *Feeds:* completeness, and presentation for balances.

## Where the conventional assumptions are worked

The basic assumptions and principles as they are usually taught, and the item that carries each one. None is skipped. Each is worked inside the item where a tool can actually put it into effect.

| Assumption or principle | Worked in |
|---|---|
| Economic entity | 1. Reporting entity |
| Going concern | 2. Basis of accounting (the liquidation basis replaces it when it fails) |
| Accrual | 2. Basis of accounting |
| Time period (periodicity) | 3. Period, cutoff and effective date |
| Monetary unit (stable dollar) | 4. Currency |
| Conservatism (prudence) | 8. Measurement, valuation and allocation |
| Consistency | 8. Measurement, valuation and allocation, and 12. Continuity with the prior position |
| Full disclosure | 7. Dimensions and attributes, and 11. Aggregation and netting |
| Reliability | 10. Population and exclusions |
| Objectivity | 10. Population and exclusions |
| Materiality | Checklist §4, which proposes the figure every test is sized against |

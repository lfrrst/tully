# Audit assertions

The assertions the checklist is organised by: what each one means, what it means when the thing under review is a tool, and where it comes from. The book borrows this vocabulary so the tests are organised the way a reviewer already thinks. Using it does not make the book an audit, and the working-paper statement still governs.

## Where they come from

The checklist uses the two sets in **AU-C section 315, as amended by SAS No. 145**, which match those in ISA 315 (Revised 2019): six assertions about classes of transactions and events, and six about account balances, each covering the related disclosures.

**PCAOB AS 1105.11** (formerly Auditing Standard No. 15) groups assertions into five categories instead: existence or occurrence, completeness, valuation or allocation, rights and obligations, and presentation and disclosure. **AS 1105.12** allows an auditor to work from a different set, provided it is sufficient to identify the types of potential misstatement and respond to the risks. The crosswalk at the end of this file shows that the twelve cover all five categories.

**§1 of every checklist names the assertion set in one sentence, with its source.** Where the tool's output feeds the financial statements of an issuer audited under PCAOB standards, also carry the crosswalk table into §1, so that a reviewer working in PCAOB terms can place every test.

## Transactions and events

The population is the output as an event: the file as it will be posted, tested against the source.

**Occurrence.** Recorded transactions and events actually happened and belong to the entity. *For a tool review:* every line in the output traces to a real source record, or to a construction that names its rule. *PCAOB:* existence or occurrence.

**Completeness.** Every transaction and event that should have been recorded has been, and so has every related disclosure. *For a tool review:* every source record that should be there is, and everything withheld is named and justified. *PCAOB:* completeness.

**Accuracy.** Amounts and other data for recorded transactions have been recorded appropriately, and related disclosures are appropriately measured and described. *For a tool review:* amounts and attributes are right, including signs, precision, constants and rejection counts. *PCAOB:* valuation or allocation.

**Cutoff.** Transactions and events have been recorded in the correct accounting period. *For a tool review:* the period, the effective date and the basis all describe the same moment. *PCAOB:* existence or occurrence, and completeness, since an item in the wrong period is missing from one and extra in the other.

**Classification.** Transactions and events have been recorded in the proper accounts. *For a tool review:* values landed in the right accounts and the right fields. *PCAOB:* presentation and disclosure.

**Presentation.** Transactions and events are appropriately aggregated or disaggregated and clearly described, and related disclosures are relevant and understandable under the applicable framework. *For a tool review:* the right level of aggregation, clearly described, with formatting that survives to the consumer. *PCAOB:* presentation and disclosure.

## Account balances

The population is the position that results: the balances the output establishes in the target system, tested against the entity's own financial statements.

**Existence.** Assets, liabilities and equity interests exist. *For a tool review:* every balance in the output exists in the source, and every value exists in the target system. *PCAOB:* existence or occurrence.

**Rights and obligations.** The entity holds or controls the rights to its assets, and its liabilities are its own obligations. *For a tool review:* balances sit in the entity that owns them, and restrictions survive. *PCAOB:* rights and obligations.

**Completeness.** Every asset, liability and equity interest that should have been recorded has been, and so has every related disclosure. *For a tool review:* every account with a balance is present, and the position foots and agrees. *PCAOB:* completeness.

**Accuracy, valuation and allocation.** Balances are included at appropriate amounts, any valuation or allocation adjustments are appropriately recorded, and related disclosures are appropriately measured and described. *For a tool review:* amounts agree at account level. Establish whether the tool performs any valuation at all. *PCAOB:* valuation or allocation.

**Classification.** Balances have been recorded in the proper accounts. *For a tool review:* current and non-current, contra accounts and equity, which are the places where a plausible but wrong mapping hides. *PCAOB:* presentation and disclosure.

**Presentation.** Balances are appropriately aggregated or disaggregated and clearly described, and related disclosures are relevant and understandable under the applicable framework. *For a tool review:* the statement as the target system will render it, agreed to the last audited figures. *PCAOB:* presentation and disclosure.

## Crosswalk to PCAOB AS 1105.11

Tully's mapping, not the standard's. AS 1105.12 permits a different set of assertions. It does not prescribe a mapping.

| AS 1105.11 category | Covered by |
|---|---|
| Existence or occurrence | Occurrence, Cutoff (transactions); Existence (balances) |
| Completeness | Completeness, Cutoff (transactions); Completeness (balances) |
| Valuation or allocation | Accuracy (transactions); Accuracy, valuation and allocation (balances) |
| Rights and obligations | Rights and obligations (balances) |
| Presentation and disclosure | Classification, Presentation (both sets) |

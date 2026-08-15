<!-- Phase 6 deliverable. The paragraph that introduces this case in the portfolio index.
     For many readers it is the only thing they will read, so it carries the finding, not
     the topic. -->

# Portfolio index entry

## Short version (index card, ~40 words)

Everyone assumes football's transfer money is concentrating in fewer clubs and that young players
carry a growing premium. Four windows of deal-level data and a decade of FIFA's census say
otherwise — on both counts. SQL on DuckDB, two sources, one hypothesis written down beforehand.

## Long version (case intro, ~110 words)

A multi-club investment fund has to decide where its next tranche of capital goes: a developing
club that sells talent, or an elite one that buys it. The answer turns on two beliefs the football
industry treats as settled — that spending is concentrating in fewer hands, and that young players
now cost a premium.

I wrote both down as a hypothesis before touching the data, and the analysis contradicted both. The
ten biggest buyers' share of European spending fell from 32% to 27%; the price of an 18–23 player
sits at parity with a 24–29 player and is not rising. What *is* stable is who sells: 96 clubs were
net sellers in all four seasons, where chance would have given 61.

Built with SQL on DuckDB over 6,716 priced transfers, cross-checked against FIFA's official
census — which is also what stopped a survivorship bias from producing exactly the opposite
conclusion.

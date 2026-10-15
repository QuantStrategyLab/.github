# Advisory and research boundary

This document defines how research and advisory projects relate to the trading
projects in the QuantStrategyLab organization. It applies to every repository.

## Rule

Advisory projects produce research. They never touch money.

## Advisory projects

`QuantAdvisorResearch` and the repositories that feed it publish
non-personalized research: ideas, event notes, risk notes, and watch lists.
They must keep these properties:

| Property | Requirement |
|---|---|
| Report output | Every report sets `execution_allowed=false`. |
| Broker access | No broker connection and no broker credentials. |
| Permissions | No trading, account, funding, or cloud write permissions. |
| Personalization | No account-level positions, sizing, or personal advice. |
| Dependencies | No import of execution code from platform repositories. |

A change that adds any of these capabilities to an advisory project is out of
scope and must not be merged.

## From idea to live trading

An advisory idea can reach live trading by one path only:

1. A person reviews the idea and decides it is worth testing.
2. The idea becomes a research variant in a strategy package and is tested
   under UBPS v2, the organization's backtest and promotion standard. This
   includes plugin on/off comparison, stress windows, and doubled trading
   costs.
3. The candidate passes the strategy promotion gate, which pins the approved
   release.
4. The owner approves the release before it runs in production.

No step can be skipped. A research recommendation, a hit-rate statistic, or a
review score is not a substitute for any step.

## Reading in the other direction

Advisory projects may read published, public results from trading projects,
such as monthly strategy performance, as background. They must not use those
results to grade their own recommendations.

## Consumers of advisory output

Trading platforms do not read advisory reports. Consoles and digests may show
advisory output as research only:

- Label every advisory item as research, not an order or a position intent.
- When an advisory symbol matches a live holding, mark the overlap. Do not
  send a separate alert.
- A daily trading digest may include one link to the latest research report.
  It does not include the report content.

When advisory output and a risk, reconciliation, or promotion check disagree,
the check wins.

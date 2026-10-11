\# Quantum Advisor — Agent Input/Output Schemas



\## 1. Purpose



This document describes the input and output contracts of the Quantum Advisor agents. The examples below are based on the current implementation of `UserAgent`, `StrategyAgent`, and `Orchestrator`.



The sample values are illustrative. Actual outputs depend on the input data and the other agents' results.



\## 2. User Agent



\*\*File:\*\* `agents/user\_agent.py`



\*\*Responsibility:\*\* Processes investor profile information and calculates a risk-capacity score using age, experience, risk appetite, and investment horizon.



\### Input schema



| Field | Type | Default |

|---|---|---|

| `age` | Integer | `30` |

| `experience` | String | `"Beginner"` |

| `riskAppetite` | String | `"Moderate"` |

| `timeHorizon` | String | `"Medium-term"` |



\### Sample input



```json

{

&#x20; "age": 28,

&#x20; "experience": "Intermediate",

&#x20; "riskAppetite": "Moderate",

&#x20; "timeHorizon": "Long-term"

}

```



\### Output schema



| Field | Type | Description |

|---|---|---|

| `userType` | String | Investor category derived from experience |

| `riskCapacityScore` | Integer | Score bounded between 0 and 100 |



\### Sample output



```json

{

&#x20; "userType": "Intermediate Investor",

&#x20; "riskCapacityScore": 80

}

```



The score is calculated from a starting value of 50, adjusted by the implemented profile rules, and clamped to the range 0–100.



\## 3. Strategy Agent



\*\*File:\*\* `agents/strategy\_agent.py`



\*\*Responsibility:\*\* Produces a recommendation using risk, market price, news sentiment, and optional risk-review feedback.



\### Input contract



The method signature is:



```python

analyze(u, m, f, r, sentiment=None, feedback=None)

```



| Parameter | Purpose |

|---|---|

| `u` | User/profile information |

| `m` | Market analysis output; requires `currentPrice` |

| `f` | Fundamentals analysis output |

| `r` | Risk analysis output; requires `riskScore` |

| `sentiment` | Optional sentiment information |

| `feedback` | Optional risk-review feedback |



The current implementation reads `sentimentScore` and `newsSentiment` from sentiment data. Feedback can contain `needsRevision` and `reason`.



\### Illustrative input



```json

{

&#x20; "user": {

&#x20;   "userType": "Intermediate Investor"

&#x20; },

&#x20; "market": {

&#x20;   "currentPrice": 100

&#x20; },

&#x20; "fundamentals": {},

&#x20; "risk": {

&#x20;   "riskScore": 24

&#x20; },

&#x20; "sentiment": {

&#x20;   "sentimentScore": 0,

&#x20;   "newsSentiment": "Neutral"

&#x20; },

&#x20; "feedback": {

&#x20;   "needsRevision": false,

&#x20;   "reason": ""

&#x20; }

}

```



This example illustrates the data passed to the method; it is not a complete validation schema for every parameter.



\### Output schema



| Field | Type | Description |

|---|---|---|

| `recommendation` | String | `BUY`, `HOLD`, or `SELL` |

| `confidence` | String | Currently fixed to `"Moderate"` |

| `buyScore` | Number | Score assigned by the implemented recommendation rules |

| `effectiveRisk` | Number | Adjusted risk value |

| `targetPrice1` | Number | First target price |

| `targetPrice2` | Number | Second target price |

| `stopLoss` | Number | Stop-loss price |

| `reasoning` | Array of strings | Explanation of the implemented decision factors |



\### Sample output



```json

{

&#x20; "recommendation": "HOLD",

&#x20; "confidence": "Moderate",

&#x20; "buyScore": 18,

&#x20; "effectiveRisk": 24,

&#x20; "targetPrice1": 110.0,

&#x20; "targetPrice2": 120.0,

&#x20; "stopLoss": 90.0,

&#x20; "reasoning": \[

&#x20;   "Trend-based analysis",

&#x20;   "Risk score evaluated",

&#x20;   "Fundamentals checked",

&#x20;   "News sentiment: Neutral"

&#x20; ]

}

```



The output above is illustrative and assumes a market price of 100, a risk score of 24, and a sentiment score of 0.



\### Decision logic



The strategy calculates effective risk from the initial risk score and sentiment score. If risk-review feedback requests a revision, the implementation adds a revision penalty.



The recommendation is then selected using the effective-risk thresholds:



\- Below 20: `BUY`

\- From 20 to below 40: `HOLD`

\- 40 or above: `SELL`



The target prices and stop loss are calculated from the current market price using the multipliers implemented in the code.



\## 4. Orchestrator



\*\*File:\*\* `orchestrator.py`



\*\*Responsibility:\*\* Coordinates agent execution, records trace events, and conditionally requests one strategy revision.



\### Method input



```python

analyze(ticker, user)

```



\- `ticker`: Stock symbol to analyze.

\- `user`: Investor input dictionary consumed by the User Agent and other relevant agents.



\### Workflow



1\. Record `run\_started`.

2\. Execute the User Agent.

3\. Execute market, fundamentals, and news sentiment analysis.

4\. Calculate the initial risk assessment.

5\. Generate an initial strategy.

6\. Ask the Risk Agent to review the strategy.

7\. If `needsRevision` is true, request one revised strategy.

8\. Execute portfolio analysis using the final strategy.

9\. Generate the report and record `run\_completed`.



\### Conditional feedback



The orchestrator uses the Risk Agent's `needsRevision` result to determine whether a revision is required. The implementation permits one bounded revision attempt; it does not implement an unlimited autonomous loop.



\### Execution trace format



Trace records are written as JSON Lines to `logs/agent\_trace.jsonl`.



Each record contains:



```json

{

&#x20; "timestamp": "ISO-8601 timestamp",

&#x20; "ticker": "RELIANCE",

&#x20; "agent": "RiskAgent",

&#x20; "event": "risk\_assessed",

&#x20; "details": {

&#x20;   "riskScore": 24,

&#x20;   "riskLevel": "Medium"

&#x20; }

}

```



This is an illustrative trace-record structure. Use the actual generated trace as execution evidence.



\## 5. Remaining Agent Contracts



The following contracts must be documented from the current source code before final submission:



\- Market Agent

\- Fundamentals Agent

\- News Sentiment Agent

\- Risk Agent

\- Portfolio Agent

\- Portfolio Analyzer

\- Report Agent



For each component, document its method signature, required input fields, output fields, defaults, and relevant error-handling behavior. Do not assume field names or outputs without checking the implementation.



\## 6. Limitations



\- These components use the behavior implemented in the current code; separate classes alone do not prove autonomous LLM reasoning.

\- Sample JSON values are illustrative, not evidence of a particular execution.

\- API-backed outputs can depend on provider availability and data freshness.

\- The application is an educational decision-support prototype and does not provide guaranteed investment outcomes.




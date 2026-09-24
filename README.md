# Skin Clinic Campaign Analysis API

M10 PMLS – Assignment 2: Developing an API for Excel.

A FastAPI service that analyses customer skin clinic marketing campaign
and serves the results as a table that Excel can read.

\---

## 1\. The analysis

Response rate = responders ÷ customers × 100. Overall rate is **39.90%**.

**Task 1 – Gender**

|Gender|Customers|Responders|Response Rate %|
|-|-|-|-|
|Female|6,007|2,629|43.77|
|Male|3,993|1,361|34.08|

**Task 2 – Age group**

|Age Group|Customers|Responders|Response Rate %|
|-|-|-|-|
|<30|2,499|823|32.93|
|30–50|4,992|2,349|47.06|
|>50|2,509|818|32.60|

**Task 3 – Purchase in last quarter**

|Purchased|Customers|Responders|Response Rate %|
|-|-|-|-|
|Yes|6,514|3,234|49.65|
|No|3,486|756|21.69|

**Task 4 – Product usage (unique products bought in last year)**

|Products|Customers|Responders|Response Rate %|
|-|-|-|-|
|1–4|2,091|378|18.08|
|5–8|3,703|1,425|38.48|
|>8|4,206|2,187|52.00|

\---

## 2\. Endpoints

|Endpoint|What it returns|
|-|-|
|`/campaign-analysis`|All four analyses stacked into one table (default)|
|`/campaign-analysis?table=gender`|Task 1 only|
|`/campaign-analysis?table=age`|Task 2 only|
|`/campaign-analysis?table=purchase`|Task 3 only|
|`/campaign-analysis?table=products`|Task 4 only|
|`/health`|Health check|
|`/docs`|Swagger UI|

Each row looks like this:

```json
{"Analysis":"Gender","Segment":"Female","Customers":6007,"Responders":2629,"Response\_Rate\_%":43.77}
```

\---




# Log analysis

Use all three supplied logs. Answer every question with commands/scripts and actual output.

1. What UTC interval is covered? How many valid, malformed and duplicate lines are in each file?

** Access.log
Total lines: 726
Valid JSON: 725
Malformed: 1
Exact duplicate records: 5
Earliest timestamp: 2026-08-20T11:00:00.015Z
Latest timestamp: 2026-08-20T11:29:57.578Z

Duplicates:
  lines 121 and 122 | request_id=lab-000121
  lines 242 and 243 | request_id=lab-000241
  lines 364 and 365 | request_id=lab-000361
  lines 485 and 486 | request_id=lab-000481
  lines 606 and 607 | request_id=lab-000601



**Application.log
File: logs/access.log
Total lines: 726
Valid JSON: 725
Malformed: 1
Exact duplicate records: 5
Earliest timestamp: 2026-08-20T11:00:00.015Z
Latest timestamp: 2026-08-20T11:29:57.578Z

Duplicates:
  lines 121 and 122 | request_id=lab-000121
  lines 242 and 243 | request_id=lab-000241
  lines 364 and 365 | request_id=lab-000361
  lines 485 and 486 | request_id=lab-000481
  lines 606 and 607 | request_id=lab-000601


**Error.log
Total lines: 68
Parsed error records: 67
Earliest error timestamp: 2026/08/20T11:05:02Z
Latest error timestamp: 2026/08/20T11:26:47Z

Exact duplicate error records: None
Distinct error request IDs: 67

Error categories:
  connection refused: 59
  upstream timeout: 8





2. How many distinct client requests occurred? How did you deduplicate and avoid counting retries twice?

**distinct client requests: 720 --> we have 726 request in access.log with 1 malformed and 5 duplicates. so distinct requests = 726 - 6 = 720

I used request_id as the unique identifier for each client request. Upstream retries were not counted as new client requests. When a request (with request_id: "lab-000124") had multiple upstreams/statuses, such as upstream_status="502, 200", these were treated as multiple upstream attempts for the same request_id, so they counted as one client request.




3. What are the final client status counts and error rate? State your denominator.

**720 distinct client requests**.

The final client status counts were:

* **200:** 615
* **404:** 10
* **502:** 40
* **503:** 47
* **504:** 8

This gives **105 client errors**, considering all final **4xx and 5xx** responses as errors.

The error rate was calculated using the number of distinct client requests as the denominator:

**Error rate = 105 / 720 × 100 = 14.58%**

Therefore, the final client error rate is **14.58%**.

I counted the final `status` field from `access.log` once per distinct `request_id`. I did not count individual `upstream_status` values separately, because comma-separated upstream statuses represent multiple upstream attempts belonging to the same client request.




4. Which paths, time windows and backends account for the failures?

**backend 172.23.0.12 error**
using "grep '"status":502' logs/access.log | jq -r '.upstream, .path' | sort | uniq -c | sort" command **noticed** that: 

All 40 HTTP 502 failures were associated with upstream `172.23.0.12` and occurred between 11:05:02.503Z and 11:09:57.503Z. This strongly indicates an issue affecting that backend during this time window. The access log alone does not prove that the server was completely down; so I investigated error.log and found that failure reason during that period was connection refused for server **172.23.0.12** This indicates that this backend was unavailable/not accepting connections during this period.


**Dependency error window**
Between **11:12:09 and 11:21:45 UTC**, the application logs contain `dependency_error` events associated with requests handled by the application.

The dependency errors were related to **Redis**, with the application reporting `TimeoutError` events. These events were followed by HTTP `503` responses for the affected requests.

This indicates that the application was experiencing failures while communicating with the Redis dependency during this time window.


**Upstream Timeout**
Between **11:25:14–11:26:47 UTC**, **8 requests** to `/records` returned **504 Gateway Timeout**.

NGINX reported `upstream timed out` for both `172.23.0.11:8080` and `172.23.0.12:8080`, indicating that the backends did not respond within the expected timeout.




5. What are the median and p95 client latencies? State the percentile method and units.





6. Which requests retried upstream? How many succeeded after retrying?
**requests retried upstream**: 
{lab-000124, lab-000130, lab-000136, lab-000142, lab-000148, lab-000154, lab-000160, lab-000166   lab-000172, lab-000178, lab-000184, lab-000190, lab-000196, lab-000202, lab-000208, lab-000214, lab-000220, lab-000226, lab-000232}    

**19 succeeded**

7. Build an incident timeline using evidence from access, error AND application logs.
8. Show one correlated failed request and one successful request. Include IDs and timestamps.

9. Which errors appear to be proxy/connectivity issues versus dependency/application issues? What proves it?
**Error	          Category	                 Evidence**
502	        Proxy / connectivity	         NGINX connect() failed (111: Connection refused) to 172.23.0.12:8080
504	        Proxy / upstream timeout	     NGINX upstream timed out
503	        Dependency / application	     Application dependency_error for Redis/PostgreSQL

**The key proof is the log layer**:
error.log identifies NGINX ↔ upstream communication problems, while application.log identifies application ↔ dependency problems.




10. What do the logs not prove? What would you check next in a running environment?

## Commands / scripts
## Results
## Timeline and correlated examples
## Conclusions and limits

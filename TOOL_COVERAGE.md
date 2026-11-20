# Executable tool coverage

| Adapter | Established behavior | Limit |
|---|---|---|
| HTTP baseline | Bounded response, status, headers, timing and pinned IP | No authenticated session or arbitrary request body |
| Surface inventory | Observed same-origin links, form metadata and input names | No JavaScript-rendered crawling or submissions |
| Response policies | Selected security-header observations | Missing headers do not establish an exploit |
| Cookie attributes | Observed Secure/HttpOnly/SameSite | Not session lifecycle or takeover validation |
| Robots/security contact | Bounded retrieval of conventional documents | Contents do not expand scope |
| CORS comparison | Controlled Origin response | Candidate only without browser/data verification |
| Reflection | Harmless marker in an observed parameter | Not proof of XSS |
| Database differential | Input-dependent database error versus a control | Candidate only; no proven query control or extraction |
| Transport observation | Verified HTTPS connection and observed HSTS | Not a cipher/protocol audit |
| Python analysis | Syntax-checked standard-library analysis in isolated WASM | No host filesystem, native subprocesses or network |
| Subdomain discovery | Observed and certificate names, installed Subfinder when available, bounded DNS candidates, wildcard comparison | Passive-source failures and unresolved names remain visible; no parent-domain expansion |
| Sitemap discovery | Bounded sitemap retrieval, nested XML location extraction | No external-entity processing; depth/host/request limits apply |
| Content review | Directory-index and debug-trace signatures in crawled responses | Candidate information exposure, not proof of sensitive impact |
| API inventory | JSON shape and observed OpenAPI GET routes | No authenticated role comparison, mutation or ID enumeration |
| Source-mapped API GET | Associates observed client base URLs with literal GET paths; captures actual responses and authentication barriers | A public response alone does not establish unauthorized disclosure; dynamic paths and POST calls remain leads |
| JavaScript review | Actual library banners, backend URLs, HTTP-call strings and input/sink observations | Library age and isolated sinks do not prove exploitability |
| TLS certificate verification | Fresh verified handshake; certificate verification failure evidence | No HTTP requests through an unverified connection; no full cipher audit |
| File exposure | Six conventional file/document paths versus a randomized missing-path control; strict format signatures | No repository dump, credential use or brute-force file list; public specs/manifests are inventory |
| Qwen evidence analysis | Prioritizes a validated set of follow-up checks from actual content and evidence; the application renders recorded facts | Unconstrained factual prose was removed after a live hallucination; priorities do not establish findings |

Twenty adapters are executable. The 1,354-file library is a research inventory, not 1,354 independently validated runtime capabilities. No upstream installer or exploitation script was activated wholesale.

The orchestrator recursively follows observed HTML links, safe GET forms, robots directives, sitemap indexes, static JavaScript route strings and public OpenAPI GET paths. It records parent/source/depth and unfinished work. It reserves HTTP budget for tests, preserves redirect chains, applies independent offline reviews concurrently, and can re-analyze saved evidence without downloading the same application again. Browser-rendered interaction, authenticated sessions and POST workflows remain unimplemented.

The design uses [PortSwigger's crawl documentation](https://portswigger.net/burp/documentation/scanner/crawling), [ProjectDiscovery's Subfinder documentation](https://github.com/projectdiscovery/subfinder), and [OWASP's file-exposure testing guidance](https://wstg.owasp.org/stable/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/04-Review_Old_Backup_and_Unreferenced_Files_for_Sensitive_Information/). The bounded jQuery observation cites the [vendor's 3.5.0 security-fix announcement](https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/); an affected version remains a candidate until an applicable input-to-sink path is demonstrated.

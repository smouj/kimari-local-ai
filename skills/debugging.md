# Skill: Debugging

## Objective
This skill enables Kimari to systematically diagnose and troubleshoot technical issues across applications, servers, networks, and infrastructure. It covers log analysis, performance debugging, error tracing, and root cause analysis using structured diagnostic methodologies.

## Response Style
- Always start with the most likely/common causes before exploring rare edge cases
- Structure the diagnosis as a decision tree: "Check X → If yes, do Y; If no, do Z"
- Include specific commands to run at each diagnostic step
- Prioritize non-destructive diagnostic steps before suggesting configuration changes
- Always provide a "quick wins" section for the most probable fixes upfront

## Good Response Examples

**Example 1: 502 Bad Gateway diagnosis**
Quick wins (check these first):
1. **Is the upstream running?** → `curl -s http://localhost:3000/health`
2. **Check nginx error log** → `tail -50 /var/log/nginx/error.log`
3. **Check upstream logs** → `journalctl -u myapp --since "5 min ago"`

If upstream is healthy but nginx still 502s:
4. **Check nginx proxy config** → Verify `proxy_pass http://backend:3000;` and that `upstream` block exists
5. **Check timeouts** → `proxy_read_timeout` may be too low for slow requests
6. **Test DNS resolution** → `nslookup backend` from within the nginx container

If upstream is down:
7. **Check OOM killer** → `dmesg | grep -i oom`
8. **Check port binding** → `ss -tlnp | grep 3000`
9. **Review recent deployments** → `git log --oneline -5` for recent changes

**Example 2: Memory leak in Node.js**
Step 1 — Confirm it's a memory leak (not just high usage):
```bash
# Monitor heap over time
node --expose-gc -e "
  setInterval(() => {
    const used = process.memoryUsage().heapUsed / 1024 / 1024;
    console.log('Heap:', used.toFixed(2), 'MB');
  }, 5000);
"
```
Step 2 — Take a heap snapshot before and after a workload cycle:
```bash
# Install heapdump globally
node -e "const heapdump = require('heapdump');
  // ... simulate workload ...
  heapdump.writeSnapshot('./before.heapsnapshot');
  // ... more workload ...
  heapdump.writeSnapshot('./after.heapsnapshot');
"
```
Step 3 — Compare snapshots in Chrome DevTools (Memory tab → Load → Compare). Look for: detached DOM nodes, growing arrays, unclosed connections, and event listener leaks.

Common Node.js leak patterns:
- **Event listeners** not removed on cleanup (especially in long-running processes)
- **Closures** holding references to large objects
- **Global caches** without eviction policy
- **Database connections** not returned to pool

**Example 3: SSL certificate troubleshooting**
```bash
# 1. Check certificate dates
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null | openssl x509 -noout -dates

# 2. Verify the full chain is served
openssl s_client -connect app.example.com:443 -servername app.example.com -showcerts </dev/null

# 3. Check for intermediate certificate issues
# The output should show 2-3 certificates (leaf + intermediates)
# If only 1 appears, intermediate certs are missing from the server

# 4. Test from multiple perspectives
curl -vI https://app.example.com 2>&1 | grep -E "SSL|certificate|issuer"
```

## Prohibited Behaviors
- Never suggest restarting as a first step without diagnosing the root cause
- Never recommend `chmod 777` or disabling security features as a fix
- Never skip checking logs before offering solutions
- Never provide a fix without explaining why it works and what caused the issue
- Never ignore the possibility that multiple issues are contributing simultaneously

## Evaluation Tests
A Python web app returns "Connection refused" errors only during peak traffic hours — diagnose systematically
MySQL queries that normally take 10ms are suddenly taking 5+ seconds — provide a step-by-step performance investigation
A Kubernetes pod is in CrashLoopBackOff state — walk through the complete diagnostic process
Users in one geographic region are experiencing 10x higher latency than others — how would you investigate
A cron job that has worked for months suddenly fails with a permission denied error — diagnose the root cause

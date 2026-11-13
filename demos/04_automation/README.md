# Demo 4: automated weekly campaign report

`weekly_report.py` turns raw post data into the Monday-morning email a CMO actually reads:

- spend vs. **budget plan** per channel, plus cumulative pacing to date
- trials, CPA, customers, CAC and school demo requests, with week-over-week change
- **alerts**: overspend > 10%, CPA/CAC up > 25%, and a **trust signal** when parent or educator conversion drops > 30%
- writes `reports/weekly_report_wkNN.md` and `.html`; optionally posts the alerts to Slack (`SLACK_WEBHOOK_URL`)

```bash
python demos/04_automation/weekly_report.py --week 7    # privacy incident: trust alerts fire
python demos/04_automation/weekly_report.py --week 10   # TikTok 60% over plan, CAC up 81%
```

## Three ways to schedule it

**macOS / Linux: cron** (every Monday at 8:00)
```
0 8 * * 1  cd /path/to/sam-vibe-coding && python demos/04_automation/weekly_report.py
```

**Windows: Task Scheduler** (PowerShell, run once)
```powershell
$a = New-ScheduledTaskAction -Execute "python" -Argument "demos\04_automation\weekly_report.py" -WorkingDirectory "C:\path\to\sam-vibe-coding"
$t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8am
Register-ScheduledTask -TaskName "Lumora weekly report" -Action $a -Trigger $t
```

**In the cloud: GitHub Actions.** See `.github/workflows/weekly-report.yml`. It is set to manual (`workflow_dispatch`)
so it never runs by surprise. Uncomment `schedule:` to run it every Monday. Put the Slack webhook in
*Settings → Secrets → Actions* as `SLACK_WEBHOOK_URL`, never in code.

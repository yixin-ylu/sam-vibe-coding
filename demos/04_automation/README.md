# Demo 4: automation (weekly report + alerts)

`weekly_report.py` turns raw post data into a manager-ready weekly summary:

- KPI table per platform, comparing this week with last week
- **alerts** when engagement drops more than 20% or impressions rise more than 50%
- writes `reports/weekly_report_<date>.md` and `.html`
- optionally posts the alerts to Slack, if `SLACK_WEBHOOK_URL` is set

```bash
python demos/04_automation/weekly_report.py
python demos/04_automation/weekly_report.py --week 2026-10-26   # the "service crisis" week
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
Register-ScheduledTask -TaskName "SAM weekly report" -Action $a -Trigger $t
```

**In the cloud: GitHub Actions.** See `.github/workflows/weekly-report.yml`. It is set to manual
(`workflow_dispatch`) so it never runs by surprise. To run it every Monday, uncomment the `schedule:` block.
Put the Slack webhook in *Settings → Secrets → Actions* as `SLACK_WEBHOOK_URL`, never in code.

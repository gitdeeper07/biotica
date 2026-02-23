# BIOTICA Weekly Report
Week: $(date +%V) - $(date +%Y)
Period: $(date -d "7 days ago" +%Y-%m-%d) to $(date +%Y-%m-%d)

## Weekly Summary
- Total plots analyzed: {total_plots}
- Average IBR: {avg_ibr}
- Trend vs last week: {trend}%
- New alerts: {new_alerts}
- Resolved alerts: {resolved_alerts}

## Daily Breakdown
| Day | Plots | Avg IBR | Alerts |
|-----|-------|---------|--------|
| Monday | {mon_plots} | {mon_ibr} | {mon_alerts} |
| Tuesday | {tue_plots} | {tue_ibr} | {tue_alerts} |
| Wednesday | {wed_plots} | {wed_ibr} | {wed_alerts} |
| Thursday | {thu_plots} | {thu_ibr} | {thu_alerts} |
| Friday | {fri_plots} | {fri_ibr} | {fri_alerts} |
| Saturday | {sat_plots} | {sat_ibr} | {sat_alerts} |
| Sunday | {sun_plots} | {sun_ibr} | {sun_alerts} |

## Weekly Statistics
- Weekly mean IBR: {weekly_mean}
- Weekly std dev: {weekly_std}
- Minimum IBR: {weekly_min}
- Maximum IBR: {weekly_max}

## Alerts This Week
{alerts_list}

## Recommendations
{recommendations}

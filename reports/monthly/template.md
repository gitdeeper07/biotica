# BIOTICA Monthly Report
Month: $(date +%B) $(date +%Y)
Period: $(date -d "30 days ago" +%Y-%m-%d) to $(date +%Y-%m-%d)

## Executive Summary
- Total plots monitored: {total_plots}
- Overall average IBR: {avg_ibr}
- Month-over-month change: {mom_change}%
- Critical sites: {critical_sites}
- Alerts generated: {total_alerts}

## Monthly Statistics
| Metric | Value |
|--------|-------|
| Mean IBR | {mean_ibr} |
| Median IBR | {median_ibr} |
| Std Deviation | {std_ibr} |
| 10th Percentile | {p10_ibr} |
| 90th Percentile | {p90_ibr} |

## Classification Summary
| Class | Count | Percentage | Change vs Last Month |
|-------|-------|------------|---------------------|
| PRISTINE | {pristine_count} | {pristine_pct}% | {pristine_change} |
| FUNCTIONAL | {functional_count} | {functional_pct}% | {functional_change} |
| IMPAIRED | {impaired_count} | {impaired_pct}% | {impaired_change} |
| DEGRADED | {degraded_count} | {degraded_pct}% | {degraded_change} |
| COLLAPSED | {collapsed_count} | {collapsed_pct}% | {collapsed_change} |

## Top 10 Critical Sites
{critical_sites_list}

## Alerts Summary
| Severity | Count | Trend |
|----------|-------|-------|
| Critical | {critical_alerts} | {critical_trend} |
| High | {high_alerts} | {high_trend} |
| Medium | {medium_alerts} | {medium_trend} |
| Low | {low_alerts} | {low_trend} |

## Recommendations
{recommendations}

## Appendix: All Sites
{all_sites_table}

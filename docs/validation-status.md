# Validation Status

This record summarizes the test output reported during the project session. It does not claim that additional tests were executed while writing this document.

## Confirmed tests

- **API health:** `GET /health` returned status `UP` and service `monitoring-lab-api`.
- **Prometheus scrape:** `up{job="monitoring-lab-api"}` returned `1` during earlier validation.
- **Rule loading:** all three configured alert rules were loaded by Prometheus.
- **High error rate:** `MonitoringLabHighErrorRate` was observed firing with warning severity.
- **Alertmanager receipt:** the high-error-rate alert appeared as active in Alertmanager.
- **Error recovery:** the active alert later cleared from Prometheus and Alertmanager.
- **High latency:** `MonitoringLabHighLatency` was observed firing with warning severity after latency mode was enabled and requests were generated.
- **Target down:** stopping the API caused `MonitoringLabTargetDown` to fire with critical severity.
- **Target recovery:** after starting the API, `/health` returned `UP` and the target-down alert was absent from the active-alert output.

## Evidence caveat

The post-restart Prometheus target query returned `status: success`, but the PowerShell formatting did not show the numeric sample value. The exact post-recovery target value was therefore not directly confirmed from that output. The healthy API response and cleared target-down alert support the recovery conclusion.

## External notification caveat

The Alertmanager receiver is configured as `local-console`. Alert presence in Alertmanager confirms receipt, not delivery to email, Slack, or another external system.

## Release checklist

- [x] API health endpoint verified.
- [x] Prometheus scrape verified during prior test.
- [x] Alert rules loaded.
- [x] High-error-rate alert fired.
- [x] High-error-rate alert reached Alertmanager.
- [x] High-error-rate recovery observed.
- [x] High-latency alert fired.
- [x] Target-down alert fired.
- [x] API health recovered after restart.
- [x] Target-down alert cleared from active-alert output.
- [ ] Review the full repository tree and compose/config files from the actual local checkout.
- [ ] Copy/merge these final docs into the repository and commit/push them if desired.

Do not claim external notification delivery or a clean-checkout test unless those actions are actually performed.

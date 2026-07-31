# Safehouse

A cloud-only personal AI assistant, built fresh (not a fork of Bayhouse,
though it draws on that project's concepts). Started 2026-07-31.

## Goal

One assistant, running entirely in the cloud, with its own dedicated
Gmail account and its own phone number for messaging. Unlike Bayhouse,
this project has no device or hardware automation layer (no bird
feeder, no Google Home control, no ADB phone bridge) -- it keeps only
the logging/audit layer and the conversational assistant itself.

This is the practical build-out of the RFC concept in the `bayhouse-PMPA`
diary's `projects/rfc/` (the Pairing / auditable-agent standard, and the
Assistant-or-Safehouse dual employer-replacement / worker-portability
framing).

## Plan

- Cloud: Azure. Infra as code via ARM templates.
- Own Google API keys: dedicated Gmail account, dedicated Google Voice
  number.
- Runtime data storage: SQLite files for now, planned refactor to an
  Azure Storage Account later.
- Backups: git, for now.
- Hosting: a free Linux VM for the initial prototype (Azure's free-tier
  B1s VM, 750 hrs/month for 12 months, gives a persistent disk for the
  SQLite file and a long-running process for polling Gmail/Voice).

## License

GPLv3 -- see [LICENSE](LICENSE).

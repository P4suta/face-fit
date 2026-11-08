# Architecture decisions

The repository uses [Markdown Architectural Decision Records](https://adr.github.io/madr/).
Each record documents one decision.
A successor links to the accepted record when a decision changes.

Accepted records cover [recording decisions](./adr/0001-record-architecture-decisions.md) and [geometric edits](./adr/0002-geometric-edits-only.md).
Accepted records also cover the [landmark model](./adr/0003-mediapipe-landmarker-and-crown-segmentation.md), [detector reuse](./adr/0004-detect-once-architecture.md), and [command interface](./adr/0005-typer-rich-cli.md).

The [Python compatibility record](./adr/0006-support-python-3.10-to-latest.md) remains partly superseded.
The accepted [Python 3.11 decision](./adr/require-supported-pillow-on-python-3.11.md) requires supported dependencies.

The [release App credential delivery decision](./adr/sync-release-app-credentials-to-the-protected-environment.md) remains proposed.

## Authoring records

Use the [template](./adr/0000-template.md) for a concise decision record.
Name the file after the decision and include a front-matter date.
Link the record from the index and documentation navigation.
Keep the record proposed until the owner accepts the reviewed decision.

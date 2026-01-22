# uv-dependency-submission

GitHub Action for submitting uv.lock dependencies

This is a GitHub Action that will generate a complete dependency graph from `uv.lock` files in the repository and submit the graph to the GitHub repository so that the graph is complete and includes all the transitive dependencies.

The action will use `git ls-files` to locate all `uv.lock` files, validate their [schema version](https://docs.astral.sh/uv/concepts/resolution/#lockfile-versioning), then parse them with python's [tomllib](https://docs.python.org/3/library/tomllib.html) to generate JSON output of the complete dependency graph, and submit the manifests using the `gh` CLI to the GitHub repository.

![Screenshot](https://github.com/user-attachments/assets/89d5078b-2f71-4b52-a19e-c189f8a9b70a)

## Example workflow

Make sure you've enabled Dependency Graph in the Security section of the repository Settings first.

```yaml
name: Dependency Submission

on:
  # trigger manually (e.g. for initial setup)
  workflow_dispatch:
  # trigger when uv.lock files change in the default branch.
  push:
    branches: ['main', 'master']
    paths:
      - '**/uv.lock'

# Drop the broad default GITHUB_TOKEN permissions for least-privilege:
# https://docs.zizmor.sh/audits/#excessive-permissions
permissions: {}

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  dependency-submission:
    name: Submit uv dependencies
    runs-on: ubuntu-latest
    timeout-minutes: 15
    permissions:
      contents: write # needs to submit dependency graph data
    steps:
      - name: Checkout repository
        uses: actions/checkout@8e8c483db84b4bee98b60c0593521ed34d9990e8 # v6.0.1
        with:
          persist-credentials: false

      - name: Submit dependency snapshot
        uses: rmuir/uv-dependency-submission@1c48aaac13e566e39fd04269ff1900b86c1105c5 # v1.0.0
```

> [!NOTE]
> After committing the workflow file, trigger once manually from Actions UI for initial setup.

## Configuration

Currently there are no parameters.
The `gh` cli is used to upload the snapshot, you can pass `env:` variables to change some behavior:

- <https://cli.github.com/manual/gh_help_environment>

## Background

If you have a uv-based project, GitHub will detect dependencies from `uv.lock` automatically.

However, the built-in GitHub functionality is new and currently very minimal:

- Dependencies are submitted as a flat list from each `uv.lock`
- No indication of Transitive vs Direct.
- No SBOM paths (e.g. to see how particular dependency was brought in)

The built-in GitHub functionality is enough for you to receive Dependabot security alerts.

By using this action, the full graph metadata will be populated, enabling more of Github's security features.

## Caveats

- Very new and may have exciting bugs. Pull requests welcome.

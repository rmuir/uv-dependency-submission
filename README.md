# uv-dependency-submission
GitHub Action for submitting uv.lock dependencies

This is a GitHub Action that will generate a complete dependency graph from `uv.lock` files in the repository and submit the graph to the GitHub repository so that the graph is complete and includes all the transitive dependencies.

The action will use `git ls-files` to locate all `uv.lock` files, validate their [schema version](https://docs.astral.sh/uv/concepts/resolution/#lockfile-versioning), then parse them with python's [tomllib](https://docs.python.org/3/library/tomllib.html) to generate JSON output of the complete dependency graph, and submit the manifests using the `gh` CLI to the GitHub repository.

![Screenshot](https://github.com/user-attachments/assets/89d5078b-2f71-4b52-a19e-c189f8a9b70a)

# Example workflow
Make sure you've enabled Dependency Graph in the Security section of the repository Settings first.
```yaml
name: Dependency Submission

on:
  workflow_dispatch:
  push:
    branches: ['main', 'master']
    paths:
      - '**/uv.lock'

permissions: {}

jobs:
  dependency-submission:
    name: Submit uv dependencies
    runs-on: ubuntu-latest
    permissions:
      contents: write # needs to submit dependency graph data
    steps:
      - name: Checkout repository
        uses: actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v5.0.0
        with:
          persist-credentials: false

      - name: Submit dependency snapshot
        uses: rmuir/uv-dependency-submission@1c48aaac13e566e39fd04269ff1900b86c1105c5 # v1.0.0
```

# Configuration
Currently there are no parameters.
The `gh` cli is used to upload the snapshot, you can pass `env:` variables to change some behavior:
- https://cli.github.com/manual/gh_help_environment

# Background
If you have a uv-based project, by default only **direct** dependencies (from `pyproject.toml`) will show in the dependency graph
- https://github.com/dependabot/dependabot-core/issues/11913

By using this action, the full graph will be populated, enabling more of Github's security features.

# Alternatives
Existing alternatives scan the dependencies and may issue many API calls to audit packages:
- https://github.com/owenlamont/uv-secure
- https://github.com/nyudenkov/pysentry

This action works differently: it does not audit your packages. 
It will make exactly one API call to publish the graph to Github: you can use Github's security tab to do the rest.

# Caveats
- Very new and may have exciting bugs. Pull requests welcome.

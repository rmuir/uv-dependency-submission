"""Dependency submission for uv.lock files.

See https://github.com/dependabot/dependabot-core/issues/11913
"""

import datetime
import json
import os
import subprocess
import tomllib
from typing import Any


def uvlock_to_manifest(filename: str) -> dict[str, Any]:
    """Return manifest from an individual uv.lock file."""
    with open(filename, "rb") as file:
        data = tomllib.load(file)
        if data["version"] != 1:
            raise NotImplementedError(f"unsupported uv.lock version {data['version']}")

        dependencies: dict[str, dict[str, Any]] = {}
        for package in data["package"]:
            dependencies[package["name"]] = package

        for package in filter(lambda pkg: "metadata" in pkg, data["package"]):
            # paint development deps first, if they are runtime, it will get overwritten
            for dep in package["metadata"].get("requires-dev", {}).get("dev", []):
                entry = dependencies[dep["name"]]
                entry["relationship"] = "direct"
                entry["scope"] = "development"
            for dep in package["metadata"].get("requires-dist", []):
                entry = dependencies[dep["name"]]
                entry["relationship"] = "direct"
                entry["scope"] = "runtime"

        resolved: dict[str, Any] = {}
        for package in dependencies.values():
            if package["source"].get("registry") is None:
                continue
            entry: dict[str, str | list[str]] = {
                "package_url": f"pkg:pypi/{package['name']}@{package['version']}",
                "relationship": package.get("relationship", "indirect"),
            }
            if "scope" in package:
                entry["scope"] = package["scope"]
            if "dependencies" in package:
                transitive: list[str] = []
                for dep in package["dependencies"]:
                    transitive.append(f"{dep['name']}@{dependencies[dep['name']]['version']}")
                entry["dependencies"] = transitive
            resolved[f"{package['name']}@{package['version']}"] = entry

        return {
            "name": filename,
            "file": {
                "source_location": filename,
            },
            "resolved": resolved,
        }


def main():
    snapshot = {
        "version": 0,
        "job": {
            "id": os.environ["GITHUB_JOB"],
            "correlator": f"{os.environ['GITHUB_WORKFLOW']}-{os.environ['GITHUB_JOB']}",
            "html_url": f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_JOB']}",
        },
        "sha": os.environ["GITHUB_SHA"],
        "ref": os.environ["GITHUB_REF"],
        "detector": {
            "name": "uv-dependency-submission",
            "version": "1.0.0",
            "url": "https://github.com/rmuir/uv-dependency-submission",
        },
    }
    manifests = {}
    input_files = subprocess.Popen(["git", "ls-files", "--", "uv.lock", "**/uv.lock"], stdout=subprocess.PIPE)
    if input_files.stdout is not None:
        for line in input_files.stdout:
            name = line.strip().decode()
            manifests[name] = uvlock_to_manifest(name)
    snapshot["manifests"] = manifests
    snapshot["scanned"] = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")

    postdata = json.dumps(snapshot, indent=4)
    cmd = [
        "gh",
        "api",
        "--method",
        "POST",
        "-H",
        "Accept: application/vnd.github+json",
        "-H",
        "X-GitHub-Api-Version: 2022-11-28",
        f"/repos/{os.environ['GITHUB_REPOSITORY']}/dependency-graph/snapshots",
        "--input",
        "-",
    ]
    try:
        print(subprocess.check_output(cmd, input=postdata, stderr=subprocess.STDOUT, universal_newlines=True))
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise


if __name__ == "__main__":
    main()

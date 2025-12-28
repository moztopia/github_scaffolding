# GitHub Scaffolding

This repository contains Reusable CI/CD Scaffolding for GitHub Actions, designed to be easily copied to new projects.

## Features

- **Versioning**: Semantic versioning managed by a central `VERSION` file.
- **Manual Releases**: Trigger releases (Major, Minor, Patch) via GitHub Actions UI.
- **Nightly Builds**: Automatic tagging of nightly builds on pushes to `develop`.
- **Auto-Approval**: Automatic approval of PRs from `dev/*` branches (configurable).
- **Cleanup**: Scheduled cleanup of old nightly tags.

## Installation

To replicate this process in a new repository:

1. **Copy Files**: Copy the following to your repo root:
    - `VERSION`
    - `.github/main_release_names.json`
    - `.github/tags_to_keep_forever.json`
    - `.github/scripts/release.py`
    - `.github/workflows/` (all files)
    - `.github/tests/` (optional, for verification)

2. **Configure GitHub Settings**:
    - Go to **Settings** > **Actions** > **General**.
    - Under **Workflow permissions**, select **Read and write permissions**.
    - Check **Allow GitHub Actions to create and approve pull requests**.

## Usage

### Releases

Go to the **Actions** tab in your repository, select **Manual Release**, and click **Run workflow**. Choose the release type:

- `major`
- `minor`
- `patch`

### Reset (Development Only)

To reset the version to `0.0.0` (only works if repo name is `github_scaffolding`):

```bash
python3 .github/scripts/release.py --type reset
```

### Nightly Builds

Pushing to the `develop` branch will automatically trigger a nightly build/tag.

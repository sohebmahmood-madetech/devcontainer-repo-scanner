# Devcontainer Discovery Scanner

Automated Python tool designed to scan specified GitHub organizations (`alphagov`, `govuk-one-login`) and documentation lists (`docs.publishing.service.gov.uk`) to identify repositories configured with devcontainer setups.

## Prerequisites & Installation

### Environment Setup
This project uses [`uv`](https://github.com/astral-sh/uv), an extremely fast Python package and environment manager.

**1. Install `uv`** (macOS via Homebrew):
```bash
brew install uv
```

**2. Clone the repository**
```bash
git clone https://github.com/sohebmahmood-madetech/devcontainer-repo-scanner.git
cd devcontainer-repo-scanner
```

## Configuration
Set your GitHub Personal Access Token in your terminal:

```bash
export GITHUB_TOKEN="your_github_pat_here"
```

## Setup & Running the Application

**1. Run the scanner script**
```bash
uv run find_devcontainers.py
```

**2. Run the unit tests** 
```bash
uv run pytest
```
(Or run directly via standard library: uv run python test_find_devcontainers.py)

## Output & Results

Upon completion, the scanner automatically writes all discovered data to a CSV file in the root directory:

* **File Name:** `devcontainer_audit_results.csv`
* **Behavior:** Created automatically or overwritten on each script execution.

## Dependency Management
Do not use pip directly. All project dependencies are managed via uv:

**1. Add a library**
```bash
uv add <package_name>
```

**2. Add a library with version constraints (e.g., pinning urllib3)**
```bash
uv add "urllib3<2.0.0"
```

**3. Add a development dependency**
```bash
uv add --dev pytest
```
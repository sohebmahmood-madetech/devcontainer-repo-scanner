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

**3. Create and activate virtual environment**
```bash
uv venv
source .venv/bin/activate
```

### Dependency Installation
Install required packages:

```bash
uv pip install -r requirements.txt
```

## Configuration
Set your GitHub Personal Access Token in your terminal:

```bash
export GITHUB_TOKEN="your_github_pat_here"
```

## Running the Application

Run the scanner or execute the unit test suite:

```bash
# Run unit tests
python -m unittest test_find_devcontainers.py

# Run the scanner script
python find_devcontainers.py
```

## Output & Results

Upon completion, the scanner automatically writes all discovered data to a CSV file in the root directory:

* **File Name:** `devcontainer_audit_results.csv`
* **Behavior:** Created automatically or overwritten on each script execution.
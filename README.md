# Devcontainer Discovery Scanner

Automated Python tool designed to scan specified GitHub organizations (`alphagov`, `govuk-one-login`) and documentation lists (`docs.publishing.service.gov.uk`) to identify repositories configured with devcontainer setups.

## Prerequisites & Installation

### Environment Setup
Clone or create your project directory and set up a Python 3 virtual environment:

```bash
# Clone the repository
git clone https://github.com/sohebmahmood-madetech/devcontainer-repo-scanner.git
cd devcontainer-repo-scanner

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

### Dependency Installation
Install required packages:

```bash
pip install requests beautifulsoup4 "urllib3<2.0.0"
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
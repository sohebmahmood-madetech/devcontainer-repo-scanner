import unittest
from unittest.mock import MagicMock, patch
from find_devcontainers import DevcontainerScanner


class TestDevcontainerScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = DevcontainerScanner(token="fake_test_token")

    @patch("find_devcontainers.requests.Session.get")
    def test_check_devcontainer_exists_returns_true_on_200(self, mock_get):
        """Verify repository returns True when a devcontainer file is found."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response

        self.assertTrue(self.scanner.check_devcontainer_exists("alphagov/test-repo"))

    @patch("find_devcontainers.requests.Session.get")
    def test_check_devcontainer_exists_returns_false_on_404(self, mock_get):
        """Verify repository returns False when devcontainer files are missing."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_get.return_value = mock_response

        self.assertFalse(self.scanner.check_devcontainer_exists("alphagov/test-repo"))

    def test_parse_govuk_doc_repos_filters_invalid_and_duplicate_urls(self):
        """Verify HTML scraping extracts valid org/repo paths and ignores system links."""
        sample_html = """
        <html>
            <a href="https://github.com/alphagov/govuk-frontend">Valid Repo 1</a>
            <a href="https://github.com/alphagov/govuk-frontend">Duplicate Repo 1</a>
            <a href="https://github.com/alphagov/orgs/subpath">Org system path (should ignore)</a>
            <a href="https://github.com/govuk-one-login/identity-api">Valid Repo 2</a>
            <a href="https://example.com/other-link">External link</a>
        </html>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = sample_html

        with patch.object(self.scanner.session, "get", return_value=mock_response):
            repos = self.scanner.parse_govuk_doc_repos("https://fake-docs-url.gov.uk")

        self.assertIn("alphagov/govuk-frontend", repos)
        self.assertIn("govuk-one-login/identity-api", repos)
        self.assertNotIn("alphagov/orgs", repos)
        self.assertEqual(len(repos), 2)


if __name__ == "__main__":
    unittest.main()
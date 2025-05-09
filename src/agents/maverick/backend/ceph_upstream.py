import requests


class Upstream:
    def __init__(self):
        self.state = "all"
        self.label = ""

    def fetch_ceph_issues(self, label):
        if label:
            self.label = label
        # GitHub API endpoint for Ceph issues
        url = "https://api.github.com/repos/ceph/ceph/issues"
        headers = {"Accept": "application/vnd.github.v3+json"}
        params = {
            "state": self.state,  # "open", "closed", or "all"
            "per_page": "10",  # Number of issues to fetch
            "labels": self.label,  # Optional: Filter by labels (e.g., "bug", "enhancement")
        }

        # Send a GET request to the GitHub API
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            issues = response.json()
            print(issues)
            if not issues:
                return "No issues found for the label: " + self.label

            output_str = ""
            output_str += "Here are the top results from upstream!\n\n"
            for i, issue in enumerate(issues, start=1):
                output_str += f"{i}   State: {issue['state']}\n"
                output_str += f"   URL: {issue['html_url']}"
                if issue["labels"]:
                    labels = [label["name"] for label in issue["labels"]]
                    output_str += f"   Labels: {', '.join(labels)}\n"
                output_str += f"   Created at: {issue['created_at']}\n"
                output_str += f"   Updated at: {issue['updated_at']}\n\n"
            return output_str
        else:
            print(f"Error: {response.status_code}")
            return []


if __name__ == "__main__":
    upstream = Upstream()
    print(upstream.fetch_ceph_issues("performance"))

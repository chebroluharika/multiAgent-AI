import requests
import json

class Bugzilla:
    def __init__(self, url, api):
        self.bugzilla_url = url
        self.bugzilla_api = api

    def bugzilla_request(self, params):
        """Handles requests to the Bugzilla API."""
        url = f"{self.bugzilla_url}/rest/bug"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bugzilla_api}",
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("bugs", [])
        except requests.exceptions.RequestException as err:
            print(f"[ERROR] Bugzilla API request failed: {err}")
            return []

    def search_or_get_bug(self, query):
        """Search for a bug or fetch details of a specific bug by ID."""
        output_str = ""

        if query.isdigit():  # Fetch bug details if input is a bug ID
            bug_data = self.bugzilla_request(
                {"id": query, "include_fields": "id,summary,status,creation_time,assigned_to,product,component,description"}
            )
            if bug_data:
                bug = bug_data[0]
                output_str += f"Bug Details:\n"
                output_str += f"ID: {bug['id']} | Status: {bug['status']} | Product: {bug['product']} | Component: {', '.join(bug['component'])}\n"
                output_str += f"Summary: {bug['summary']}\n"
                output_str += f"Created On: {bug['creation_time']}\n"
                output_str += f"Assigned To: {bug.get('assigned_to', 'Unassigned')}\n"
                output_str += f"Bug Link: {self.bugzilla_url}/show_bug.cgi?id={bug['id']}\n\n"
                output_str += f"Description: {bug.get('description', 'No description available')}\n"
            else:
                output_str += f"[INFO] No details found for Bug ID: {query}\n"
            return output_str

        # Search for bugs based on summary or keywords
        bugs_found = {bug["id"]: bug for bug in self.bugzilla_request({"quicksearch": query})}

        # Broaden search if needed
        if len(bugs_found) < 5:
            for term in query.split():
                for bug in self.bugzilla_request({"quicksearch": term}):
                    bugs_found[bug["id"]] = bug

        sorted_bugs = sorted(
            bugs_found.values(), key=lambda b: b.get("creation_time", ""), reverse=True
        )[:5]

        # Format the output
        if sorted_bugs:
            output_str += "Bug Results:\n"
            count = 1
            for bug in sorted_bugs:
                output_str += f"{count}. ID: {bug['id']} | Status: {bug['status']} | Product: {bug['product']} | Component: {', '.join(bug['component'])}\n"
                output_str += f"   Summary: {bug['summary']}\n"
                output_str += f"   Created On: {bug['creation_time']}\n"
                output_str += f"   Assigned To: {bug.get('assigned_to', 'Unassigned')}\n"
                output_str += f"   Bug Link: {self.bugzilla_url}/show_bug.cgi?id={bug['id']}\n\n"
                count += 1
        return output_str
    
    def create_bugzilla_bug (self, product, component, summary, description):
    # Create a new bug in Bugzilla
        url = f"{self.bugzilla_url}/rest/bug"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bugzilla_api}",
        }
        payload = {
            "product": product,
            "component": component,
            "summary": summary,
            "description": description,
            "version": "unspecified",
            "op_sys": "All",
            "platform": "All",
            "severity": "normal",
            "priority": "P3",
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            bug_id = response.json().get("id")
            if bug_id:
                return f"Bug created successfully!\nBug ID: {bug_id}\nBug Link: {self.bugzilla_url}/show_bug.cgi?id={bug_id}\n"
            else:
                return "[ERROR] Bug created but ID was not returned."
        except requests.exceptions.RequestException as err:
            return f"[ERROR] Failed to create bug: {err}"


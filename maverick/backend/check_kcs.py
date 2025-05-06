import subprocess
import json
import urllib.parse


class CheckKcs:

    def __init__(self):
        pass

        # Function to fetch data from the RedHat API
    def get_results_from_kcs(self, query):
        """
        Fetch data from RedHat API using the given query
        """
        # URL-encode the query to handle spaces and special characters
        encoded_query = urllib.parse.quote(query)

        curl_command = [
            'curl', '-X', 'GET',
            f'https://api.access.redhat.com/support/search/kcs?q={encoded_query}',
            '-H', 'accept: application/json'
        ]

        try:
            # Execute the curl command and capture the output
            result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
            json_data = json.loads(result.stdout)
            # Extact data
            output_str = ""
            count = 1
            docs = json_data.get("response", {}).get("docs", [])
            for doc in docs:
                if doc.get('documentKind') == 'Solution':
                    title = doc.get('title', 'N/A')
                    view_uri = doc.get('view_uri', 'N/A')
                    output_str += f"{count}. Title: {title}\n   Solution URL: {view_uri}\n\n"
                    count += 1
            return output_str
        except subprocess.CalledProcessError as e:
            print(f"Error during API call: {e}")
            return None

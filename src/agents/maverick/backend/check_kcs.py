import json
import subprocess
import urllib.parse

import requests


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

        headers = {"accept": "application/json"}
        url = f"https://api.access.redhat.com/support/search/kcs?q={encoded_query}"
        response = requests.get(url, headers=headers)

        try:
            if response.status_code != 200:
                return f"Error: {response.status_code} for query: {query}"

            json_data = response.json()
            # Extact data
            output_str = ""
            count = 1
            docs = json_data.get("response", {}).get("docs", [])
            for doc in docs:
                if doc.get("documentKind") == "Solution":
                    title = doc.get("title", "N/A")
                    view_uri = doc.get("view_uri", "N/A")
                    output_str += (
                        f"{count}. Title: {title}\n   Solution URL: {view_uri}\n\n"
                    )
                    count += 1
            return output_str
        except Exception as e:
            print(f"Error during API call: {e}")
            return None


if __name__ == "__main__":
    kcs = CheckKcs()
    print(kcs.get_results_from_kcs("sync modules"))

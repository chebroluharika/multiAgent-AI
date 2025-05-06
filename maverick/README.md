# Ceph-Troubleshooting-Assistant
Agentic AI Troubleshooting assistant is a tool that gives better perspective and control over the product issues, fixes and support. This assistant, having access to predefined end points such as  Bugs (Bugzilla, Jira), Documentations/User Guide, Customer Portal etc, can be helping hand in resolving end users queries and If a possible solution is not identified, the agent is intelligent to start an end-to-end support workflow (JIRA, Bugzilla, support requests etc.) 

The proposed solution uses WatsonX and API calls, NLP’s to parse through the given end points (documentation, articles, bugs, upstream issues etc) and suggest the best possible solution, to the questions asked by the user.

# To run the UI Bot (frontend) code
1. source venv/bin/activate
2. git clone https://github.ibm.com/Mohit-Bisht/maverick
3. cd maverick
4. pip install -r backend/requirements.txt
5. pip install -r frontend/requirements.txt
6. cd config
7. update auth env (For bugzilla)
8. cd frontend
9. streamlit run ceph_troubleshooting_assistant.py

Reference: https://ibm-my.sharepoint.com/:f:/p/pranav_prakash3/EgFWcxcKN3NChjvX6u-_yO4B3mgc9UCJUzl4z1PVT3p_MQ?e=7ox4T6

![image](https://github.ibm.com/Mohit-Bisht/maverick/assets/420690/b2f0b6c9-cb5c-4d67-b023-81902cc74863)

![image](https://github.ibm.com/Mohit-Bisht/maverick/assets/420690/73832d26-592d-4bbc-ac28-c1007da09931)

![image](https://github.ibm.com/Mohit-Bisht/maverick/assets/420690/323fbb80-9f33-4be3-9f8e-c497a86e9fea)



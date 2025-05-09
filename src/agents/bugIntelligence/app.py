import asyncio
import re
from datetime import datetime

import bugzilla
import streamlit as st
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool

# Bugzilla API Base URL
BUGZILLA_URL = "https://bugzilla.redhat.com"
bzapi = bugzilla.Bugzilla(
    BUGZILLA_URL, api_key="Mf5LWqGyfWxDEojhk1q5vTMpCc4ByfmvhOCIk8Hh"
)


def serialize_bug_details(bug):
    """
    Serialize bug details, converting DateTime objects to strings.
    """
    return {
        "id": bug.id,
        "assigned_to": bug.assigned_to,
        "creator": bug.creator,
        "product": bug.product,
        "component": bug.component,
        "status": bug.status,
        "resolution": bug.resolution,
        "summary": bug.summary,
        "creation_time": datetime.strptime(
            bug.creation_time.value, "%Y%m%dT%H:%M:%S"
        ).strftime("%m/%d/%Y"),
        "last_change_time": datetime.strptime(
            bug.last_change_time.value, "%Y%m%dT%H:%M:%S"
        ).strftime("%m/%d/%Y"),
        "comments": get_comments(bug.id),
    }


def get_mock_bug_details(bug_id: int):
    mock_bugs = [
        {
            "id": 12345,
            "assigned_to": "mock_user@example.com",
            "creator": "creator_user@example.com",
            "product": "MockProduct",
            "component": "MockComponent",
            "status": "NEW",
            "resolution": "",
            "summary": "This is a mock bug for testing.",
            "creation_time": "01/01/2023",
            "last_change_time": "01/02/2023",
            "comments": {
                "comment_1": {
                    "time": "01/01/2023",
                    "creation_time": "01/01/2023",
                    "creator": "commenter_user@example.com",
                    "bug_comments": "This is a mock comment.",
                    "comment_count": 1,
                },
                "comment_2": {
                    "time": "01/03/2023",
                    "creation_time": "01/03/2023",
                    "creator": "another_user@example.com",
                    "bug_comments": "This is another mock comment.",
                    "comment_count": 2,
                },
            },
        },
        {
            "id": 98765,
            "assigned_to": "mock_user2@example.com",
            "creator": "creator_user2@example.com",
            "product": "MockProduct2",
            "component": "MockComponent2",
            "status": "IN_PROGRESS",
            "resolution": "",
            "summary": "This is another mock bug for testing.",
            "creation_time": "02/01/2023",
            "last_change_time": "02/02/2023",
            "comments": {
                "comment_1": {
                    "time": "02/01/2023",
                    "creation_time": "02/01/2023",
                    "creator": "commenter_user2@example.com",
                    "bug_comments": "This is a mock comment for the second bug.",
                    "comment_count": 1,
                }
            },
        },
    ]
    bug_report = list(filter(lambda bug: bug["id"] == bug_id, mock_bugs))
    if len(bug_report) == 0:
        return "No bug found"
    return bug_report[0]


def get_bug_details(bug_id):
    """
    Retrieve/returns bug details for a given bug ID.
    """
    print(f"{bug_id = }")

    bug = bzapi.getbug(bug_id)
    print(f"{bug = }")
    out = serialize_bug_details(bug)
    # out = get_mock_bug_details(bug_id)
    return out


def serialize_comments(comments):
    """
    Serialize comments, converting DateTime objects to strings.
    """
    comments_dict = {}
    out_dict = {}
    for comment in comments:
        if comment["time"]:
            comment["time"] = datetime.strptime(
                comment["time"].value, "%Y%m%dT%H:%M:%S"
            ).strftime("%m/%d/%Y")
            comments_dict["time"] = comment["time"]

        if comment["creation_time"]:
            comment["creation_time"] = datetime.strptime(
                comment["creation_time"].value, "%Y%m%dT%H:%M:%S"
            ).strftime("%m/%d/%Y")
            comments_dict["creation_time"] = comment["creation_time"]
        comments_dict["creator"] = comment["creator"]
        comments_dict["bug_comments"] = comment["text"]
        comments_dict["comment_count"] = comment["count"]
        out_dict[f"comment_{comment['count']}"] = comments_dict
    return out_dict


def get_comments(bug_id):
    """
    Retrieve/returns bug's comments for a given bug ID.
    """
    comments = bzapi.getbug(bug_id).getcomments()
    serialized_comments = serialize_comments(comments)
    return serialized_comments


def get_bugs_list_by_status_and_product(product_status: str):
    """
    Retrieve/returns list of bugs for a given product and status.
    """
    # data = json.loads(product_status)
    # product = data["product"]
    # status = data["status"]
    product_status = product_status.split(",")
    product, status = product_status[0], product_status[1]
    query_data = bzapi.query(
        {
            "bug_status": status,
            "columnlist": "product,component,assigned_to,bug_status,short_desc,changeddate,bug_severity",
            "list_id": "13553952",
            "order": "severity, ",
            "product": product,
            "query_format": "advanced",
            "limit": 0,
        }
    )
    data = [str(bug) for bug in query_data]
    data_list = []
    for d in data:
        data_list.extend(re.findall(r"\d{7}", d))
    # details = [ get_bug_details(bug_id) for bug_id in data_list]
    return {"bug id list": data_list}


def helper_function_for_get_data(data):
    bugs = {}
    bug_ids = data["bug_id_list"]

    for bug_id in bug_ids:
        details = get_bug_details(bug_id)
        if bug_id not in bugs:
            bugs[bug_id] = {"summary": "", "assignee": "", "creation_time": ""}
        bugs[bug_id].update(details)

    table_header = ["Bug ID", "Summary", "Assignee", "Creation Time"]
    table = [table_header] + [
        [bug_id, details["summary"], details["assignee"], details["creation_time"]]
        for bug_id, details in bugs.items()
    ]
    return table


def get_bugs_reported_list_by_email_id(data: str):
    """
    Retrieve/returns list of bugs reported by a given email_id
    """
    email_id, duration_in_days = data.split(",")
    duration_in_days = re.findall(r"\d+", str(duration_in_days))[0]
    query_data = bzapi.query(
        {
            "list_id": "13553952",
            "email1": email_id,
            "emailreporter1": "1",
            "query_format": "advanced",
            "v1": "-" + str(duration_in_days) + "D",
            "o1": "greaterthan",
            "f1": "creation_ts",
            "limit": 0,
        }
    )
    #'offset': 0})
    data = []
    for bug in query_data:
        bug_data = bug.get_raw_data()
        data.append(str(bug_data["id"]))
    # data = [str(bug) for bug in query_data]
    return helper_function_for_get_data({"bug_id_list": data})


def get_the_bug_list(product_component):
    """
    List bugs based on specifications.
    """
    product_component = product_component.split(",")
    product, component = product_component[0], product_component[1]
    query1 = bzapi.build_query(product=product, component=component)
    # Request the bugzilla.redhat.com extension ids_only=True to bypass limit
    query1["ids_only"] = True

    queried_bugs = bzapi.query(query1)
    ids = [bug.id for bug in queried_bugs]
    print(f"Queried {len(ids)} ids")
    return {"bug_id_list": ids}


def get_bugs_assigned_list_by_email_id(data):
    """
    Retrieve/returns list of bugs reported by a given email_id
    """
    email_id, duration_in_days = data.split(",")
    duration_in_days = re.findall(r"\d+", str(duration_in_days))[0]
    query_data = bzapi.query(
        {
            "list_id": "13553952",
            "email1": "adking@redhat.com",
            "emailassigned_to1": 1,
            "query_format": "advanced",
            "v1": "-" + str(duration_in_days) + "D",
            "o1": "greaterthan",
            "f1": "creation_ts",
            "limit": 0,
        }
    )
    #'offset': 0})
    data = []
    for bug in query_data:
        bug_data = bug.get_raw_data()
        data.append(str(bug_data["id"]))
    # data = [str(bug) for bug in query_data]
    return helper_function_for_get_data({"bug_id_list": data})


def get_all_bugs_action_by_email(data):
    """
    Retrieve/returns list of bugs reported and reported by a given email_id
    """
    reported = get_bugs_reported_list_by_email_id(data)
    assigned = get_bugs_assigned_list_by_email_id(data)
    return {"bug_id_list": reported + assigned}


async def fetch_bugs_async(product, component, limit=100):
    def fetch_bugs(offset):
        query = bzapi.build_query(product, component)
        query["include_fields"] = [
            "id",
            "summary",
            "status",
            "priority",
            "assigned_to",
            "creation_time",
            "last_change_time",
        ]
        query["limit"] = limit
        query["offset"] = offset
        return bzapi.query(query)

    all_bugs = []
    all_bugs_details = {}
    offset = 0

    while True:
        bugs = await asyncio.to_thread(fetch_bugs, offset)
        if not bugs:
            break

        all_bugs.extend(bugs)

        # print(f"fetched {len(bugs)} , Total so far: {len(all_bugs)}")
        offset += len(bugs)

        count = 1

        for bug in all_bugs:
            all_bugs_details[f"bug {count}"] = {}
            all_bugs_details[f"bug {count}"]["bug id"] = bug.id
            all_bugs_details[f"bug {count}"]["Summary"] = bug.summary
            all_bugs_details[f"bug {count}"]["status"] = bug.status
            all_bugs_details[f"bug {count}"]["priority"] = bug.priority
            all_bugs_details[f"bug {count}"]["assigned to"] = bug.assigned_to
            all_bugs_details[f"bug {count}"]["creation time"] = datetime.strptime(
                bug.creation_time.value, "%Y%m%dT%H:%M:%S"
            ).strftime("%m/%d/%Y")
            all_bugs_details[f"bug {count}"]["last change time"] = datetime.strptime(
                bug.last_change_time.value, "%Y%m%dT%H:%M:%S"
            ).strftime("%m/%d/%Y")

            count += 1

    return all_bugs_details


def get_all_bugs_details_fast(product_component):
    product_component = product_component.split(",")
    product, component = product_component[0], product_component[1]
    all_bugs = asyncio.run(fetch_bugs_async(product, component))
    return all_bugs


# Define tools
tools = [
    Tool(
        name="get bug details of a single bug",
        func=get_bug_details,
        description="give the out of the bug id, this tool will give bug details.",
    ),
    Tool(
        func=get_comments,
        name="get bug comments of a single bug",
        description="give the out of the bug id, this tool will give bug comments with details"
        + " like time, creator,  bug_comments, comment_count.",
    ),
    # Tool(
    #     func=get_bugs_list_by_status_and_product,
    #     name="list of multiple bugs provided the product and status",
    #     description="Provided the product and status as string of \"product,status\""
    #     + "tool will give all the bugs details in a table formate in collumns bug_id, status, summary,assignee, creation_time"
    # ),
    Tool(
        func=get_bugs_reported_list_by_email_id,
        name="get list of bugs reported for a given email and duration in days",
        description='lists all the bugs and its details reported by the email and time in days provided as a python string "email,days"',
    ),
    Tool(
        func=get_bugs_assigned_list_by_email_id,
        name="get list of bugs assigned for a given email and duration in days",
        description='lists all the bugs and its details assigned by the email and time in days provided as a python string "email,days"',
    ),
    # Tool(
    #     func=get_the_bug_list,
    #     name="Lists all the bugs details provided the product and component",
    #     description="Provided the product and component as string of\"product,component\""
    #                 + "tool will prints all the bugs"
    # ),
    Tool(
        func=get_all_bugs_details_fast,
        name="give the list of all bugs details fast",
        description="Provided product (Red Hat Ceph Storage) and component (RGW, Cephadm) "
        + "tool will  fetches the bug summary of all the bugs of that product and components",
    ),
]


def process_query(query: str):
    if not st.session_state.authenticated_user:
        return "⚠️ Please log in first."
    response = agent.run(query)
    st.session_state.chat_history.append((query, response))
    return response


if __name__ == "__main__":
    from langchain_ollama import OllamaLLM

    st.set_page_config(page_title="Bug Intelligence", page_icon="🐞", layout="centered")

    if "authenticated_user" not in st.session_state:
        st.session_state.authenticated_user = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.authenticated_user:
        st.sidebar.subheader("Bugzilla Login")
        username = st.sidebar.text_input("👤 Username", placeholder="Enter username")
        api_key = st.sidebar.text_input(
            "🔑 Bugzilla API Key",
            type="password",
            placeholder="Enter your Bugzilla API Key",
        )

        if st.sidebar.button("Login"):
            if api_key:
                # Attempt login using API Key
                bzapi = bugzilla.Bugzilla(BUGZILLA_URL, api_key=api_key)

                if bzapi.logged_in:
                    st.session_state["bugzilla_token"] = api_key
                    st.sidebar.success("Login successful!")
                    st.sidebar.success(
                        f"💬Hi {username} , I am Bug Intelligence (BI)! I am eager to help You!"
                    )
                    st.session_state.authenticated_user = True
                else:
                    st.sidebar.error("Login failed. Invalid API Key.")
            else:
                st.sidebar.warning("Please enter your API Key.")
    if st.session_state.authenticated_user:
        api_key = st.session_state["bugzilla_token"]
        bzapi = bugzilla.Bugzilla(BUGZILLA_URL, api_key=api_key)

    # print(get_all_bugs_details_fast("Red Hat Ceph Storage,RGW"))

    # Use only get_bug_details tool ignore everything else

    # Initialize the Ollama model
    llm = OllamaLLM(model="mistral")

    # Memory for Conversation

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Initialize the agent

    agent = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )

    print("👋 Exiting agent...")

    # Streamlit UI
    st.title("💬BUG INTELLIGENCE: AI BUG Chatbot")

    # Chat Interface

    for query, response in st.session_state.chat_history:
        st.write(f"🧑‍💻 You: {query}")
        st.write(f"🤖 Bot: {response}")

    prompt = st.chat_input("Type your command (e.g., get summary of bug)...")
    if prompt:
        if st.session_state.authenticated_user:
            st.write(f"🧑‍💻 You: {prompt}")
            with st.spinner("Processing... 🤖"):
                response = process_query(prompt)
                st.write(f"🤖 Bot: {response}")
        else:
            st.error("Please login")

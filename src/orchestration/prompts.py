ORCHESTRATOR_PROMPT = """
You are a master Ceph Orchestrator.
Your primary responsibility is to meticulously analyze user queries regarding a Ceph distributed storage cluster. Based on this analysis, you must intelligently decide which specialized agent(s) to delegate the task(s) to. After the specialized agent(s) complete their work, you will synthesize their findings into a single, coherent, and user-friendly final response.

You have two specialized agents at your disposal:
1.  **CephViz Agent**: This agent specializes in Ceph cluster management, operations, and status reporting.
    *   Delegate to `CephViz` for queries related to:
        *   Overall cluster health and status (e.g., "What is the status of my Ceph cluster?", "Is the cluster healthy?").
        *   OSD (Object Storage Daemon) status and details (e.g., "Show me the OSD status", "Are there any down OSDs?").
        *   Filesystem information (e.g., "List all CephFS filesystems", "Get metadata for 'myfs'").
        *   MDS (Metadata Server) node information (e.g., "List MDS nodes").
        *   Pool usage and configuration.
        *   General Ceph commands and configurations.
2.  **Observability Agent**: This agent specializes in monitoring, performance metrics, resource utilization, and generating visualizations.
    *   Delegate to `Observability` for queries related to:
        *   Disk occupation and storage capacity (e.g., "What is the current disk occupation?", "How much free space is left?").
        *   Performance metrics (e.g., "Show me the IOPS for the cluster", "What is the filesystem performance?").
        *   Resource usage (e.g., "MDS memory usage").
        *   Generating graphs or visual representations of data (e.g., "Create a bar chart of pool usage", "Visualize OSD capacity").

**Delegation Logic:**
*   If a user's query clearly falls under the purview of `CephViz` (e.g., "get cluster status", "list OSDs"), delegate the task to the `CephViz` agent.
*   If a user's query clearly falls under the purview of the `Observability` agent (e.g., "show disk occupation", "graph performance metrics"), delegate the task to the `Observability` agent.
*   If a user's query involves aspects handled by both agents (e.g., "What is the status of the cluster and show me its current disk usage?"), you must delegate the relevant parts of the query to *both* `CephViz` and `Observability` agents. Then, you must carefully synthesize their individual responses into a comprehensive final answer.
*   If the query is ambiguous, try to infer the primary intent and choose the most appropriate agent, or if necessary, both.

**Response Format:**
*   Always respond in plain text.
*   Ensure the final synthesized response is clear, concise, and directly addresses all parts of the user's original query.

**Example Scenarios:**
*   User Query: "What is the health of Cluster 1 and show me the OSD tree?"
    *   Delegation: `CephViz` agent.
*   User Query: "Can you generate a pie chart for the current data pool usage?"
    *   Delegation: `Observability` agent.
*   User Query: "Give me a summary of CephFS 'datafs' metadata and its current performance."
    *   Delegation: `CephViz` (for metadata) AND `Observability` (for performance). Synthesize results.
"""


BUG_INTELLIGENCE_SEARCH_BUG_CONTEXT = """
Search Bugs
-----------

Allows you to search for bugs based on particular criteria.

**Request**

To search for bugs:

.. code-block:: text

   GET /rest/bug

Unless otherwise specified in the description of a parameter, bugs are
returned if they match *exactly* the criteria you specify in these
parameters. That is, we don't match against substrings--if a bug is in
the "Widgets" product and you ask for bugs in the "Widg" product, you
won't get anything.

Criteria are joined in a logical AND. That is, you will be returned
bugs that match *all* of the criteria, not bugs that match *any* of
the criteria.

Each parameter can be either the type it says, or a list of the types
it says. If you pass an array, it means "Give me bugs with *any* of
these values." For example, if you wanted bugs that were in either
the "Foo" or "Bar" products, you'd pass:

.. code-block:: text

   GET /rest/bug?product=Foo&product=Bar

Some Bugzillas may treat your arguments case-sensitively, depending
on what database system they are using. Most commonly, though, Bugzilla is
not case-sensitive with the arguments passed (because MySQL is the
most-common database to use with Bugzilla, and MySQL is not case sensitive).

In addition to the fields listed below, you may also use criteria that
is similar to what is used in the Advanced Search screen of the Bugzilla
UI. This includes fields specified by ``Search by Change History`` and
``Custom Search``. The easiest way to determine what the field names are and what
format Bugzilla expects is to first construct your query using the
Advanced Search UI, execute it and use the query parameters in they URL
as your query for the REST call.

================  ========  =====================================================
name              type      description
================  ========  =====================================================
alias             array     The unique aliases of this bug. An empty array will
                            be returned if this bug has no aliases.
assigned_to       string    The login name of a user that a bug is assigned to.
component         string    The name of the Component that the bug is in. Note
                            that if there are multiple Components with the same
                            name, and you search for that name, bugs in *all*
                            those Components will be returned. If you don't want
                            this, be sure to also specify the ``product`` argument.
creation_time     datetime  Searches for bugs that were created at this time or
                            later. May not be an array.
creator           string    The login name of the user who created the bug. You
                            can also pass this argument with the name
                            ``reporter``, for backwards compatibility with
                            older Bugzillas.
id                int       The numeric ID of the bug.
last_change_time  datetime  Searches for bugs that were modified at this time
                            or later. May not be an array.
limit             int       Limit the number of results returned. If the limit
                            is more than zero and higher than the maximum limit
                            set by the administrator, then the maximum limit will
                            be used instead. If you set the limit equal to zero,
                            then all matching results will be returned instead.
offset            int       Used in conjunction with the ``limit`` argument,
                            ``offset`` defines the starting position for the
                            search. For example, given a search that would
                            return 100 bugs, setting ``limit`` to 10 and
                            ``offset`` to 10 would return bugs 11 through 20
                            from the set of 100.
op_sys            string    The "Operating System" field of a bug.
platform          string    The Platform (sometimes called "Hardware") field of
                            a bug.
priority          string    The Priority field on a bug.
product           string    The name of the Product that the bug is in.
resolution        string    The current resolution--only set if a bug is closed.
                            You can find open bugs by searching for bugs with an
                            empty resolution.
severity          string    The Severity field on a bug.
status            string    The current status of a bug (not including its
                            resolution, if it has one, which is a separate field
                            above).
summary           string    Searches for substrings in the single-line Summary
                            field on bugs. If you specify an array, then bugs
                            whose summaries match *any* of the passed substrings
                            will be returned. Note that unlike searching in the
                            Bugzilla UI, substrings are not split on spaces. So
                            searching for ``foo bar`` will match "This is a foo
                            bar" but not "This foo is a bar". ``['foo', 'bar']``,
                            would, however, match the second item.
tags              string    Searches for a bug with the specified tag. If you
                            specify an array, then any bugs that match *any* of
                            the tags will be returned. Note that tags are
                            personal to the currently logged in user.
target_milestone  string    The Target Milestone field of a bug. Note that even
                            if this Bugzilla does not have the Target Milestone
                            field enabled, you can still search for bugs by
                            Target Milestone. However, it is likely that in that
                            case, most bugs will not have a Target Milestone set
                            (it defaults to "---" when the field isn't enabled).
qa_contact        string    The login name of the bug's QA Contact. Note that
                            even if this Bugzilla does not have the QA Contact
                            field enabled, you can still search for bugs by QA
                            Contact (though it is likely that no bug will have a
                            QA Contact set, if the field is disabled).
url               string    The "URL" field of a bug.
version           string    The Version field of a bug.
whiteboard        string    Search the "Status Whiteboard" field on bugs for a
                            substring. Works the same as the ``summary`` field
                            described above, but searches the Status Whiteboard
                            field.
quicksearch       string    Search for bugs using quicksearch syntax.
================  ========  =====================================================
"""
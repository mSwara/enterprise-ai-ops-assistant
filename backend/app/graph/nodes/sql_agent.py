from langchain.agents import create_agent
from app.llm.client import get_llm
from app.tools.sql_tools import run_sql_query

sql_agent = create_agent(
    model=get_llm(),
    tools=[run_sql_query],
    system_prompt=(
    "You are the Data/SQL Agent. You answer analytical questions by "
    "writing SELECT-only SQL queries using the run_sql_query tool. "
    "You never attempt to modify data. If a query is rejected as "
    "unsafe, explain that to the user rather than trying to work "
    "around the restriction. Always base your answer on the actual "
    "query results, never estimate or guess numbers. "
    "The database is PostgreSQL. Always generate PostgreSQL-compatible "
    "SQL. Do not use SQLite or MySQL-specific functions such as "
    "GROUP_CONCAT. For string aggregation, use STRING_AGG instead."
),
)
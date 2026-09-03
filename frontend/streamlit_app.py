import os

import streamlit as st
import requests

# BACKEND_URL lets Docker Compose point the frontend at the "backend"
# service name instead of localhost. Defaults to 127.0.0.1 for local dev
# (running `streamlit run` directly on your machine, outside Docker).
API_BASE = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Enterprise AI Ops Assistant",
    layout="wide",
)

st.title("Enterprise AI Ops Assistant")


# -----------------------------
# Agent labels
# -----------------------------
AGENT_LABELS = {
    "customer_agent": "👤 Customer Agent",
    "sql_agent": "📊 Data/SQL Agent",
    "knowledge_agent": "📚 Knowledge Agent",
    "action_agent": "⚡ Action Agent",
    "multi_context": "🔀 Multi-Context (Customer + Policy)",
}


# -----------------------------
# Session state
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    if st.button("🆕 New Conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = None
        st.rerun()

    if st.session_state.thread_id:
        st.caption(
            f"Thread: `{st.session_state.thread_id[:8]}...`"
        )


# -----------------------------
# Display conversation history
# -----------------------------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        # -------------------------
        # User message
        # -------------------------
        if msg["role"] == "user":

            st.markdown(msg["content"])

        # -------------------------
        # Assistant message
        # -------------------------
        else:

            # Agent routing information
            routed_to = msg.get("routed_to")

            if routed_to:
                label = AGENT_LABELS.get(
                    routed_to,
                    routed_to,
                )

                st.caption(
                    f"Handled by: {label}"
                )

            # Main response
            st.markdown(msg["content"])

            # Validation information
            if not msg.get("paused"):

                validated = msg.get("validated")

                retry_count = msg.get(
                    "retry_count",
                    0,
                )

                if validated is True and retry_count == 0:

                    st.caption(
                        "✅ Verified on first attempt"
                    )

                elif validated is True and retry_count > 0:

                    st.caption(
                        f"✅ Verified after "
                        f"{retry_count} correction(s)"
                    )

                elif validated is False:

                    st.caption(
                        "⚠️ Could not be fully verified"
                    )


# -----------------------------
# Chat input
# -----------------------------
user_input = st.chat_input(
    "Ask about orders, customers, policies, or request an action..."
)


# -----------------------------
# Send message
# -----------------------------
if user_input:

    # Add user message to history
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)


    # -----------------------------
    # Assistant response
    # -----------------------------
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = requests.post(
                    f"{API_BASE}/chat",
                    json={
                        "message": user_input,
                        "thread_id": st.session_state.thread_id,
                    },
                    timeout=60,
                )

                # Explicit backend error
                if response.status_code == 500:

                    st.error(
                        "The backend encountered an internal "
                        "error processing this request. "
                        "Please try again."
                    )

                    st.stop()

                response.raise_for_status()

                data = response.json()

            except requests.exceptions.Timeout:

                st.error(
                    "The request took too long and timed out. "
                    "The backend may be under heavy load."
                )

                st.stop()

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the backend. "
                    "Is the FastAPI server running?"
                )

                st.stop()

            except requests.exceptions.RequestException as e:

                st.error(
                    f"Unexpected error: {e}"
                )

                st.stop()


        # -----------------------------
        # Update thread ID
        # -----------------------------
        st.session_state.thread_id = data["thread_id"]


        # -----------------------------
        # Handle paused HITL response
        # -----------------------------
        if data.get("paused"):

            payload = data.get(
                "approval_payload",
                {},
            )

            st.warning(
                "⏸️ This request requires human approval "
                "before proceeding."
            )

            with st.container(border=True):

                st.markdown(
                    f"**Original request:** "
                    f"{payload.get('request', 'N/A')}"
                )

                st.markdown(
                    f"**Why it was flagged:** "
                    f"{payload.get('reason', 'N/A')}"
                )

                if payload.get("recommendation"):

                    st.markdown(
                        "**System's recommendation:**"
                    )

                    st.markdown(
                        payload["recommendation"]
                    )

            st.info(
                "Go to the **Approvals** tab in the sidebar "
                "to review and approve or reject this request."
            )

            # Save compact version to chat history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "⏸️ Paused for approval — "
                        "see the Approvals tab."
                    ),
                    "routed_to": data.get("routed_to"),
                    "validated": data.get("validated"),
                    "retry_count": data.get(
                        "retry_count",
                        0,
                    ),
                    "paused": True,
                }
            )


        # -----------------------------
        # Normal response
        # -----------------------------
        else:

            # Agent routing information
            routed_to = data.get(
                "routed_to"
            )

            if routed_to:

                label = AGENT_LABELS.get(
                    routed_to,
                    routed_to,
                )

                st.caption(
                    f"Handled by: {label}"
                )


            # Main assistant response
            st.markdown(
                data["reply"]
            )


            # -----------------------------
            # Validation status
            # -----------------------------
            validated = data.get(
                "validated"
            )

            retry_count = data.get(
                "retry_count",
                0,
            )

            if validated is True and retry_count == 0:

                st.caption(
                    "✅ Verified on first attempt"
                )

            elif validated is True and retry_count > 0:

                st.caption(
                    f"✅ Verified after "
                    f"{retry_count} correction(s)"
                )

            elif validated is False:

                st.caption(
                    "⚠️ Could not be fully verified"
                )


            # -----------------------------
            # Retry button
            # -----------------------------
            if (
                "couldn't produce a fully grounded response"
                in data["reply"]
            ):

                if st.button(
                    "Retry this question",
                    key=f"retry_{len(st.session_state.messages)}",
                ):

                    # Remove assistant message if present
                    if st.session_state.messages:
                        st.session_state.messages.pop()

                    # Remove user message
                    if st.session_state.messages:
                        st.session_state.messages.pop()

                    st.rerun()


            # -----------------------------
            # Save assistant message
            # -----------------------------
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": data["reply"],
                    "routed_to": data.get(
                        "routed_to"
                    ),
                    "validated": data.get(
                        "validated"
                    ),
                    "retry_count": data.get(
                        "retry_count",
                        0,
                    ),
                    "paused": data.get(
                        "paused",
                        False,
                    ),
                }
            )
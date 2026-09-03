import os

import streamlit as st
import requests

# Same BACKEND_URL convention as streamlit_app.py — see comment there.
API_BASE = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Pending Approvals",
    layout="wide",
)

st.title("Pending Approvals")


# -----------------------------
# Load pending approvals
# -----------------------------
try:

    response = requests.get(
        f"{API_BASE}/approvals",
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

except requests.exceptions.ConnectionError:

    st.error(
        "Could not connect to the backend. "
        "Is the FastAPI server running?"
    )

    st.stop()

except requests.exceptions.Timeout:

    st.error(
        "The request took too long and timed out. "
        "The backend may be under heavy load."
    )

    st.stop()

except requests.exceptions.RequestException as e:

    st.error(
        f"Could not load approvals: {e}"
    )

    st.stop()


# -----------------------------
# Approval data
# -----------------------------
pending = data.get(
    "pending",
    []
)

count = data.get(
    "count",
    0
)


# -----------------------------
# No pending approvals
# -----------------------------
if count == 0:

    st.success(
        "No pending approvals right now."
    )


# -----------------------------
# Display pending approvals
# -----------------------------
else:

    st.info(
        f"{count} request(s) awaiting review."
    )

    for item in pending:

        thread_id = item["thread_id"]

        with st.container(border=True):

            # -------------------------
            # Request
            # -------------------------
            st.markdown(
                f"**Request:** "
                f"{item.get('request', 'N/A')}"
            )


            # -------------------------
            # Reason
            # -------------------------
            st.markdown(
                f"**Reason flagged:** "
                f"{item.get('reason', 'N/A')}"
            )


            # -------------------------
            # Recommendation
            # -------------------------
            if item.get("recommendation"):

                with st.expander(
                    "View system recommendation"
                ):

                    st.markdown(
                        item["recommendation"]
                    )


            # -------------------------
            # Thread ID
            # -------------------------
            st.caption(
                f"Thread ID: `{thread_id}`"
            )


            # -------------------------
            # Reviewer note
            # -------------------------
            note_key = f"note_{thread_id}"

            note = st.text_input(
                "Reviewer note (optional)",
                key=note_key,
            )


            # -------------------------
            # Approve / Reject buttons
            # -------------------------
            col1, col2 = st.columns(2)


            # -------------------------
            # Approve
            # -------------------------
            with col1:

                if st.button(
                    "✅ Approve",
                    key=f"approve_{thread_id}",
                    type="primary",
                ):

                    try:

                        resp = requests.post(
                            f"{API_BASE}/approvals/"
                            f"{thread_id}/resume",
                            json={
                                "approved": True,
                                "note": note,
                            },
                            timeout=30,
                        )

                        resp.raise_for_status()

                        st.success(
                            "Approved. Refreshing..."
                        )

                        st.rerun()

                    except requests.exceptions.ConnectionError:

                        st.error(
                            "Could not connect to the backend. "
                            "Is the FastAPI server running?"
                        )

                    except requests.exceptions.Timeout:

                        st.error(
                            "The approval request timed out."
                        )

                    except requests.exceptions.RequestException as e:

                        st.error(
                            f"Failed to approve: {e}"
                        )


            # -------------------------
            # Reject
            # -------------------------
            with col2:

                if st.button(
                    "❌ Reject",
                    key=f"reject_{thread_id}",
                ):

                    try:

                        resp = requests.post(
                            f"{API_BASE}/approvals/"
                            f"{thread_id}/resume",
                            json={
                                "approved": False,
                                "note": note,
                            },
                            timeout=30,
                        )

                        resp.raise_for_status()

                        st.success(
                            "Rejected. Refreshing..."
                        )

                        st.rerun()

                    except requests.exceptions.ConnectionError:

                        st.error(
                            "Could not connect to the backend. "
                            "Is the FastAPI server running?"
                        )

                    except requests.exceptions.Timeout:

                        st.error(
                            "The rejection request timed out."
                        )

                    except requests.exceptions.RequestException as e:

                        st.error(
                            f"Failed to reject: {e}"
                        )
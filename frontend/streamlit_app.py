import uuid
import streamlit as st

from api_client import (
    send_message,
    health_check,
    get_metrics,
    get_cache_stats,
)

st.set_page_config(
    page_title="Production RAG",
    page_icon="🤖",
    layout="wide",
)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Sidebar
with st.sidebar:
    st.title("⚙️ System")

    health = health_check()

    if health:
        st.success(f"Backend: {health['status']}")
    else:
        st.error("Backend Offline")

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    metrics = get_metrics()
    if metrics:
        st.subheader("Metrics")

        st.metric(
            "Requests",
            metrics["total_requests"]
        )

        st.metric(
            "Errors",
            metrics["total_errors"]
        )

        st.metric(
            "Avg Latency",
            f"{metrics['avg_latency_ms']} ms"
        )

# Main Page
st.title("🤖 Production RAG Assistant")

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input(
    "Ask something..."
):

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:
                response = send_message(
                    prompt,
                    st.session_state.thread_id,
                )

                answer = response["response"]

                st.markdown(answer)

                st.caption(
                    f"""
                    Model: {response['model_used']}
                    | Cached: {response['cached']}
                    | Latency: {response['processing_time_ms']} ms
                    """
                )

                if response["security_notes"]:
                    st.warning(
                        "\n".join(
                            response["security_notes"]
                        )
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except Exception as e:
                st.error(str(e))
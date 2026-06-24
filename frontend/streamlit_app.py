import streamlit as st
import requests
import uuid
import psutil
import pandas as pd
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Production RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# ============================
# Session State
# ============================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


# ============================
# API Helpers
# ============================

def get_health():
    try:
        return requests.get(
            f"{API_URL}/health",
            timeout=2
        ).json()
    except:
        return None


def get_metrics():
    try:
        return requests.get(
            f"{API_URL}/metrics",
            timeout=2
        ).json()
    except:
        return None


def get_cache():
    try:
        return requests.get(
            f"{API_URL}/cache/stats",
            timeout=2
        ).json()
    except:
        return None


# ============================
# Sidebar
# ============================

st.sidebar.title("⚙️ System Dashboard")

health = get_health()
metrics = get_metrics()
cache = get_cache()

if health:
    if health["status"] == "healthy":
        st.sidebar.success("Backend Healthy")
    else:
        st.sidebar.error("Backend Degraded")

    st.sidebar.write(
        f"Environment: {health['environment']}"
    )

    checks = health["checks"]

    st.sidebar.write(
        f"🤖 Agent: {'✅' if checks['agent'] else '❌'}"
    )
    st.sidebar.write(
        f"🛡 Security: {'✅' if checks['security'] else '❌'}"
    )
    st.sidebar.write(
        f"💾 Cache: {'✅' if checks['cache'] else '❌'}"
    )
else:
    st.sidebar.error("Backend Offline")


st.sidebar.divider()

# ============================
# Metrics
# ============================

if metrics:
    st.sidebar.subheader("📊 Metrics")

    st.sidebar.metric(
        "Requests",
        metrics["total_requests"]
    )

    st.sidebar.metric(
        "Errors",
        metrics["total_errors"]
    )

    st.sidebar.metric(
        "Error Rate",
        metrics["error_rate"]
    )

    st.sidebar.metric(
        "Avg Latency",
        f"{metrics['avg_latency_ms']} ms"
    )

    st.sidebar.metric(
        "Input Tokens",
        metrics["total_input_tokens"]
    )

    st.sidebar.metric(
        "Output Tokens",
        metrics["total_output_tokens"]
    )

    st.sidebar.metric(
        "Cache Hit Rate",
        metrics["cache_hit_rate"]
    )


st.sidebar.divider()

# ============================
# Cache Stats
# ============================

if cache:
    st.sidebar.subheader("💾 Cache")

    st.sidebar.metric(
        "Hits",
        cache["hits"]
    )

    st.sidebar.metric(
        "Misses",
        cache["misses"]
    )

    st.sidebar.metric(
        "Entries",
        cache["cached_entries"]
    )


st.sidebar.divider()

# ============================
# System Metrics
# ============================

st.sidebar.subheader("🖥 System")

cpu = psutil.cpu_percent()

memory = psutil.virtual_memory()

st.sidebar.metric(
    "CPU Usage",
    f"{cpu}%"
)

st.sidebar.metric(
    "RAM Usage",
    f"{memory.percent}%"
)

st.sidebar.metric(
    "RAM Free",
    f"{memory.available / (1024**3):.2f} GB"
)

st.sidebar.divider()

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.history = []
    st.rerun()


# ============================
# Main Page
# ============================

st.title("🤖 Production RAG Assistant")

st.caption(
    "Production-ready AI Assistant with Monitoring, Caching and Observability"
)


# ============================
# Chat History
# ============================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            if "metadata" in msg:

                meta = msg["metadata"]

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Model",
                    meta["model"]
                )

                c2.metric(
                    "Cached",
                    "✅" if meta["cached"] else "❌"
                )

                c3.metric(
                    "Latency",
                    f"{meta['latency']} ms"
                )

                c4.metric(
                    "Security Notes",
                    meta["security"]
                )


# ============================
# Chat Input
# ============================

prompt = st.chat_input(
    "Ask something..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {
        "message": prompt,
        "thread_id": st.session_state.thread_id
    }

    with st.spinner("Thinking..."):

        try:
            response = requests.post(
                f"{API_URL}/chat",
                json=payload,
                timeout=120
            )

            data = response.json()

            answer = data["response"]

            metadata = {
                "model":
                    data["model_used"],
                "cached":
                    data["cached"],
                "latency":
                    data["processing_time_ms"],
                "security":
                    len(
                        data.get(
                            "security_notes",
                            []
                        )
                    )
            }

            with st.chat_message("assistant"):
                st.markdown(answer)

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Model",
                    metadata["model"]
                )

                c2.metric(
                    "Cached",
                    "✅" if metadata["cached"] else "❌"
                )

                c3.metric(
                    "Latency",
                    f"{metadata['latency']} ms"
                )

                c4.metric(
                    "Security Notes",
                    metadata["security"]
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "metadata": metadata
                }
            )

            st.session_state.history.append(
                {
                    "timestamp":
                        datetime.now(),
                    "question":
                        prompt,
                    "model":
                        metadata["model"],
                    "cached":
                        metadata["cached"],
                    "latency":
                        metadata["latency"]
                }
            )

        except Exception as e:
            st.error(f"Error: {e}")


# ============================
# Request History
# ============================

if st.session_state.history:

    st.divider()

    st.subheader("📈 Request History")

    df = pd.DataFrame(
        st.session_state.history
    )

    st.dataframe(
        df,
        use_container_width=True
    )
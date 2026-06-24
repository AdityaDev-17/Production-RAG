"""
Simple smoke test for ProductionAgent.
"""

from app.agents import ProductionAgent


def test_agent():
    print("=" * 60)
    print("Initializing Production Agent...")
    print("=" * 60)

    agent = ProductionAgent()

    test_inputs = [
        "Hello! Who are you?",
        "What is the capital of India?",
        "Explain Retrieval-Augmented Generation in one sentence.",
        "Write a haiku about AI."
    ]

    for i, message in enumerate(test_inputs, start=1):
        print(f"\nTest {i}")
        print("-" * 60)
        print(f"Input : {message}")

        try:
            result = agent.invoke(message)

            print(f"Response    : {result['response']}")
            print(f"Model Used  : {result['model_used']}")
            print(f"Error       : {result['error']}")

        except Exception as e:
            print(f"Exception: {e}")

        print("-" * 60)


if __name__ == "__main__":
    test_agent()
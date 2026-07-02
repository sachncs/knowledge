"""Basic usage example for the knowledge SDK."""

from knowledge import Knowledge


def main() -> None:
    """Demonstrate the knowledge SDK workflow."""
    knowledge = Knowledge()

    # 1. Create knowledge from text
    doc = knowledge.create(
        "Python is a programming language. "
        "It supports asynchronous programming. "
        "JavaScript is used for web development.",
        verify=False,
    )

    print("Created document:")
    info = doc.inspect()
    for key, value in info.items():
        print(f"  {key}: {value}")

    # 2. Verify the document
    result = doc.verify()
    print(f"\nVerification result:")
    print(f"  Score: {result.score.overall:.1f}%")
    print(f"  Repairs applied: {result.repairs_applied}")
    print(f"  Converged: {result.converged}")

    # 3. Score quality
    score = doc.score()
    print(f"\nQuality scores:")
    print(f"  Overall:      {score.overall:.1f}%")
    print(f"  Completeness: {score.completeness:.1f}%")
    print(f"  Consistency:  {score.consistency:.1f}%")

    # 4. Save to OKF Markdown
    doc.save("example_output.md")
    print("\nDocument saved to example_output.md")


if __name__ == "__main__":
    main()

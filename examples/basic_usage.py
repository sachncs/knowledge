"""Basic usage example for the knowledge SDK."""


def main() -> None:
    print("knowledge SDK - Basic Usage")
    print("=" * 40)
    print()
    print("This example demonstrates the knowledge SDK workflow.")
    print()
    print("1. Create a Knowledge instance")
    print("2. Create an OKF document from a source")
    print("3. Verify the document")
    print("4. Save the document")
    print()
    print("Example:")
    print()
    print("  from knowledge import Knowledge")
    print()
    print("  knowledge = Knowledge()")
    print('  okf = knowledge.create("sources/my-document.md")')
    print("  okf.verify(threshold=95)")
    print('  okf.save("knowledge.md")')


if __name__ == "__main__":
    main()

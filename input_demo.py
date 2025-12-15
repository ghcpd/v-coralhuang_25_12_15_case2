from input_tools import HttpClient, ToolA, ToolB, ToolC

def main():
    client = HttpClient()
    base_url = "http://example.local"

    tools = [ToolA(client, base_url), ToolB(client, base_url), ToolC(client, base_url)]

    for t in tools:
        print(t.__class__.__name__, t.run("u1", "  hello  ", limit=10))

if __name__ == "__main__":
    main()

# Email & Slack Connectors

Pull data from external services via their MCP servers.

## Outlook / Microsoft 365

```bash
km connect outlook
```

Requires: `ms-365-mcp` installed and authenticated.

## Slack

```bash
km connect slack
```

Requires: Slack MCP server configured with workspace token.

## Custom MCP source

Any MCP server can be a data source:

```bash
km connect my-source --command "npx my-mcp-server" --tool "list_items"
```

## How it works

1. Knowledge Master connects to the external MCP server as a **client**
2. Calls the specified tool to fetch data
3. Parses the response into chunks
4. Embeds and stores in the knowledge graph
5. Links to Person nodes (senders/authors)

The result: emails, Slack messages, and code all searchable in one place.

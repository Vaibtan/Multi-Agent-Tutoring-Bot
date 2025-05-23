async def extract_response_and_tools(events):
    # Given an async iterator of events, concatenate
    # all .content and collects .tool_calls names.
    response_text = ""
    tools_used = []

    async for ev in events:
        # ADK event may have .content
        if getattr(ev, "content", None):
            response_text += ev.stringify_content()
        # ADK event may have .tool_calls
        if getattr(ev, "tool_calls", None):
            tools_used.extend(call.name for call in ev.tool_calls)
    return response_text, tools_used

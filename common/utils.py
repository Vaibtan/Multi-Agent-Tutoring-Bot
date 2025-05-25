async def extract_response_and_tools(events):
    # Given an async iterator of events, concatenate
    # all .content and collects .tool_calls names.
    response_text = ""
    tools_used = []
    async for ev in events:
        # Extract text content properly according to ADK documentation
        if getattr(ev, "content", None) and ev.content.parts:
            # Iterate through all parts in the content
            for part in ev.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
        # Extract function calls using the correct ADK method
        function_calls = ev.get_function_calls()
        if function_calls:
            tools_used.extend(call.name for call in function_calls)
        # Also check for function responses (tool results)
        function_responses = ev.get_function_responses()
        if function_responses:
            tools_used.extend(response.name for response in function_responses)
    return response_text, tools_used

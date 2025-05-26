async def extract_response_and_tools(events):
    # Given an async iterator of events, concatenate all content and collects tool_calls names
    response_text = ""
    tools_used = []
    async for ev in events:
        if getattr(ev, "content", None) and ev.content.parts:
            for part in ev.content.parts:
                if hasattr(part, 'text') and part.text: response_text += part.text
        function_calls = ev.get_function_calls()
        if function_calls: tools_used.extend(call.name for call in function_calls)
        function_responses = ev.get_function_responses()
        if function_responses: tools_used.extend(response.name for response in function_responses)
    return response_text, tools_used

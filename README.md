# LLM Tests

## Summary
This package aims to make LLM testing easier and repeatable.

The primary intention is for testing LLM memory solutions like RAG, but the functionality can be used for other purposes as well. Including tool testing.

Test files are stored as JSON using the following template.

The following example explains most of the functionality of the template.

```JSON
{
    "setups": [
        {
            "summary": "An optional summary of the prior conversations",
            "prior_conversations": [
                [{
                    "role": "user",
                    "content": "My name is User"
                },
                {
                    "role": "assistant",
                    "content": "Hi User"
                }
                ],
                [{
                    "role": "user",
                    "content": "Do you know my name"
                },
                {
                    "role": "assistant",
                    "content": "This is a new context, I can only remember across contexts with external tools"
                }]
            ]
        }
    ], 
    "tests" : [
        {
            "summary": "An optional summary for this test",
            "case_sensitive": false,
            "ignoring_thinking": true,
            "messages": [{
                    "role": "system",
                    "content": "Respond only with the word Hello"
                }],
            "expected_response": "Hello"
        },
        {
            "messages": [{
                    "role": "system",
                    "content": "Respond only with the user's name"
                }],
            "expected_response": "User"
        }
    ]
}
```


# Contributing

Start with the specification and current status. The first implementation priority is the complete local learning loop with actual inference and durable, correctable records. Subsequent work must preserve its offline behavior.

Use a focused branch and explain the problem, behavior changed and evidence. Include tests for consequential behavior and failures, not merely a test that repeats the implementation. Use synthetic records. Never attach student data, private adult vaults, API keys, recovery secrets or screenshots containing them to an issue or pull request.

Sign commits with `git commit -s` to certify the [Developer Certificate of Origin 1.1](https://developercertificate.org/). A sign-off records contribution rights; it does not assign copyright to the project or a model provider. Original code/contracts and prose have the licenses described in LICENSING.md.

Model changes include the exact checkpoint, runtime, tokenizer/template, quantization, evaluation data and results. General leaderboard scores cannot substitute for the product's memory, language, teaching and privacy checks.

Do not describe a contribution as certified for schools, private by proof, or educationally effective unless the repository contains evidence that supports that precise claim.

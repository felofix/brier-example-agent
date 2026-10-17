# Example agent

A small agent that answers a question using the OpenAI SDK and a calculator tool.
It exists so the Brier runner has something real to run.

## What a customer repo must provide

1. A `Dockerfile` that builds the agent's environment. The runner builds it with the repo root as context and runs the agent in `/repo`.
2. An entrypoint command, for example `python agent.py`. The runner runs it as `sh -c "<entrypoint>"`.
3. An agent that uses the OpenAI SDK with its default environment configuration (`openai.OpenAI()` with no arguments), reads the task from `BRIER_INSTRUCTION`, and prints its final answer as the last non-empty line of stdout. Anything else goes to stderr.

The runner sets `OPENAI_BASE_URL` and `OPENAI_API_KEY` to point at the Brier gateway, so model calls are recorded without code changes.

## Run locally

```sh
pip install openai
OPENAI_API_KEY=... BRIER_INSTRUCTION="What is 2+2? Answer with only the number." python agent.py
```

Set `BRIER_MODEL` to use a model other than `gpt-5`.

## Push as its own repo

The runner clones a git repo, so publish this folder separately:

```sh
cd examples/example-agent
git init
git add .
git commit -m "Example agent"
git remote add origin <your-repo-url>
git push -u origin main
```

`tasks.jsonl` holds twenty tasks (ten arithmetic, ten factual) with exact-match answers.

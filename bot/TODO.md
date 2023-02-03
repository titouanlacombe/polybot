pull docker compose out
test

separate services into their own repos [
    change stable diffusion to workers pulling SQL DB to get jobs and return results

    services:
    - polybot: you know, keep api (behind DNS) for mobile application project
    - workers: docker image have env var (num threads) to ovverride default
    - api: flask? api with simple SQL DB to manage jobs, authentification ? nginx proxy.

    api db:
    - users: name, passwd_hash
    - jobs: user_id, input, output

    how to make SQL "data" collumns (no sorting)
]

polybot remove some envs

buy RTX 3060 ti (7.5 it/s) ?

add GPT-3 api call (try to generate the next message (with author))

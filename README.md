# PolyBot

TODO Readme

```yaml
polybot:
  repo: git@gitlab.com:TitouanLacombe99/poly-bot.git
  main_branch: master
  envs: ["dev", "sta", "pre", "pro"]
  build: python3 -m makepie build
  up: python3 -m makepie up
  down: python3 -m makepie down
  ping_url: http://localhost/ping
  ping_delay: 5
  ping_success: pong
```

# PolyBot

### Deploy config example

```yaml
polybot:
  repo: git@gitlab.com:TitouanLacombe99/poly-bot.git
  main_branch: master
  envs: ["dev", "sta", "pre", "pro"]
  build: python3 -m makepie build
  up: python3 -m makepie up
  down: python3 -m makepie down
  ping:
    ports:
      dev: 80
      sta: 5001
      pre: 5002
      pro: 5003
    delay: 5
    success: pong
```

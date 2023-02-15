# Polybot

<img src="https://raw.githubusercontent.com/titouanlacombe/polybot_api/master/src/api/static/api/polybot.png" alt="drawing" width="300"/>

## Services

https://docs.google.com/drawings/d/1uNF-A8a_BRvgIJ-wW_RjLT-dGl5MtDIHePFvDeXnbRo/edit?usp=sharing

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

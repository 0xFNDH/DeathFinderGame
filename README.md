# [df] Death Finder Game

## dfAbout

Death Finder is a LAN multiplayer rouge-like RPG developed in Python.
The objective is for players to reach the end of the dungeon by fighting
monsters with the help of other players. The game takes inspiration from [**Nethack**](https://nethack.org/) and shares some of the same features.

> "I started this project as a fun idea but ended up creating something more than I would have excepted. All I wanted was to create a new world for my friends and I to explore."

## dfMulticast

In the latest `version 3.0`, the game was swapped to multicast sockets which bypassed network restrictions. Multicast also reduced the amount of strain on the network when multiple groups were on at the same time. The max player limit was increased to 15 as a result.

>Death Finder `version 2.0`, was converted to support UDP broadcasting which had many downsides and did not preform reliably. Packet sizes were limited to `~1800 bytes` max and the game did not operate across the full network.
>>Death Finder `version 1.0`, used TCP sockets and HTTP to communicate with the server. Players sent actions through `POST` requests and it was easy to operate. But network restrictions prevented devices from accessing the game's server.

## dfMap

|  Object       | Symbol | Stand-On |
| ------------- |:------:|:--------:|
| `Yourself`    | `@`    | Yes
| `Players`     | `&`    | No
| `Floor`       | `.`    | Yes
| `Wall`        | `#`    | No
| `Door`        | `+`    | Yes
| `Item`        | `?`    | Yes
| `Dark Floor`  | ` `    | Yes
| `Leaf`        | `,`    | Yes
| `Bush`        | `*`    | Slowed
| `Branch`      | `=`    | Unstable
| `Water`       | `^`    | Waterlogged
| `Hill`        | `:`    | Yes
| `Barrier`     | `"` or `:` | No
| `Field`       | `'` or `.` | Yes

|  Enemy        | Symbol | Level |
| ------------- |:------:|:----:|
| `goblin` | `g` | `1`
| `spider` | `s` | `1`
| `orc`    | `o` | `1`
| `nymph`  | `n` | `1`
| `blob`   | `b` | `1`
| `rat`    | `r` | `1`
| `Snake`  | `S` | `2-4`
| `Goblin` | `G` | `2-4`
| `succubus` | `q` | `2-4`
| `Kobold` | `K` | `2-4`
| `Pudding`| `P` | `2-4`
| `Stone Golum` | `#` | `4-6`
| `Mimic`  | `?` | `1-6`
| `Basilisk`  | `B` | `4-6`
| `Naga`  | `N` | `4-6`
| `Lich`  | `L` | `4-6`
| `Arch Angel`  | `A` | `4-6`
| `Dragon`  | `D` | `5-7`
| `Wyvern`  | `B` | `5-7`
| `demon prince`  | `d` | `5-7`
| `Final Boss`  | `????` | `????`

| NPC           | Symbol | Ability  |
| ------------- |:------:|:--------:|
| `Jacob`       | `J`    | No
| `JimJim`      | `J`    | Heals Player
| `Jake`        | `J`    | No
| `Hÿdor`       | `!`    | Wet Floor Sign

## dfControls

    Movement Inputs:
    ----------------
    
         diagonal     up    diagonal
                 \    |    /
                  [Q][W][E]
            left -[A][S][D]- right
                  [Z]   [C]
                 /         \
         diagonal           diagonal
        
        Lowercase WASD is used by default.
        
        Obtaining 'JUMPBOOTS' will enable Shift+WASD.
    
    
    Magic Inputs:
    -------------
        
        Book of Healing:
            !H - Slightly heals all users but subtracts XP.
        
        Shield Scroll:
            !S - Spawns a 5x5 barrier around player.
        
    
    end.



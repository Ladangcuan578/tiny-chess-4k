# Tiny Chess 4K

[![tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/Ladangcuan578/tiny-chess-4k/rank.svg)](https://make.fun/bounty/tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/Ladangcuan578/tiny-chess-4k/reward.svg)](https://make.fun/bounty/tiny-chess-01)

An original 4 KB chess engine in Python, built by an AI agent for
[make.fun's "Build the strongest chess engine in 4 KB of Python" bounty](https://make.fun/bounty/tiny-chess-01).
Leaderboard: https://make.fun/bounty/tiny-chess-01

## Design

- **Board:** 0x88 array (a1=0, h8=119). White pieces 1..6, black -1..-6.
- **Move generation:** pseudo-legal with inline legality check (king attacked
  after the move), castling, en passant, promotions. Verified by perft on the
  six standard positions (start, Kiwipete, positions 3-6).
- **Search:** negamax alpha-beta with iterative deepening to a **fixed node
  budget of 100,000 nodes per move** (never a wall clock, so replays are
  deterministic). Transposition table, MVV-LVA capture ordering, two killer
  moves per ply, null-move pruning (R=2, only with a non-pawn piece to move).
- **Quiescence:** captures and promotions out of check, every evasion in
  check, with delta pruning (margin 200) and stand-pat.
- **Evaluation:** material (P100 N320 B330 R500 Q900) + piece-square tables
  (the standard simplified tables) + a tempo bonus, all maintained
  incrementally with Zobrist hashing.
- **Protocol:** talks to the env at `MAKEFUN_ENV_URL` (`POST /game`, `/move`,
  `/resign`), 10 s per move, 200-ply cap.

## Local results (practice trials, 6 games each)

| trial | Elo | W-D-L |
|-------|-----|-------|
| 0 | 1451 | 4-0-2 |
| 1 | 1279 | 3-0-3 |
| 2 | 1451 | 4-0-2 |

Mean 1394 vs the house (sunfish 4K) baseline mean of 1365. Floor for the
final is 1154. `main.py` is the kit's `makefun compress` output of the
readable source `engine.py` (kept beside it, uncommitted); the packed entry
is 4090 bytes.

## License

MIT, see LICENSE.

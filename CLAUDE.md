# English Learning Project

A personal project to improve English skills.

## Goals
- Improve reading comprehension
- Correct grammar and spelling errors
- Build and memorize vocabulary
- Prepare for English exams

## Folder Structure
- `exam-pdfs/CET-6/` — CET-6 exam papers and audio files
- `study/` — error log, word lists, and review log
- `scripts/` — Python scripts (audio player, etc.)

## Audio Player
- Run `python scripts/player.py` to scan audio files and open HTML player in browser
- Put audio files in `exam-pdfs/CET-6/`
- Player supports: play, pause, rewind, forward, speed control
- Click "Done" to copy text, then paste in chat for correction

## Eudic Integration
- Config: `.claude/eudic.json` (API token)
- Add words to Eudic: `python scripts/eudic.py word1 word2 word3`
- Claude will automatically add new vocabulary to Eudic when correcting errors
- Words are added to "英语学习" category in Eudic

## How to Use
- Chat with Claude to practice English
- Claude corrects errors and adds new words to vocabulary
- Review words regularly using `study/review-log.md`

## Rules
1. Always correct user's English errors in every message (grammar, spelling, word choice)
2. Show corrections clearly: wrong → correct
3. Log errors in `study/error-log.md` with columns: Date, Wrong, Correct, Rule, 中文
4. Add new difficult words to `study/word-list.md`
5. Always include Chinese translation for errors
6. Be encouraging, not harsh
7. Help with listening practice — scan audio files, launch HTML player in browser
8. Add new vocabulary to Eudic using `python scripts/eudic.py <words>`

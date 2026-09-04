# raylcat
WIP Scratch sb3 -> Go -> machine code compiler using raylib.
Currently only has the ability to deal with rudimentary blocks, supporting only bitmap textures.
Transpilation logic is written in python, output code is pure Go.
This project has very little testing.
## Usage
```
git clone https://github.com/humanoidkiwifruit/raylcat.git
cd raylcat
python3 main.py run ~/path/to/your.sb3
```
## TODO
- Expand (and actually utilise) block_specs.json
- Add svg support / automatically rasterise SVGs
- Translate the rest of the opcodes
- Proper handling of whitespace/strange characters in sprite names/inputs. Hashes?
- Implement variables, lists, broadcasts
- Add subcommands to build to a binary and run binary
- Handle keyboard input
- Add ability to compile assets into generated binary
- Stop needlessly passing a *ScratchSprite into blocks that don't need it
- Increase reliability of reading block arguments. Current system is quite rudimentary
- Create an enum (?) for the keys that scratch is able to access
- Create appropriate data structures instead of blindly reading from the dictionary
- Consider turbowarp extensions
- Give constants SCREAMING_SNAKE_CASE names

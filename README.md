# raylcat
WIP Scratch sb3 -> Go -> machine code compiler using raylib.
Currently only has the ability to deal with rudimentary blocks, supporting only bitmap textures.
Transpilation logic is written in python, output code is pure Go.
This project has very little testing.
## Usage
```
git clone https://github.com/humanoidkiwifruit/raylcat.git
cd raylcat
pip install .
raylcat --help
```
## TODO
- Test argument parsing
- Add svg support / automatically rasterise SVGs
- Translate the rest of the opcodes
- Proper error handling
- Proper handling of whitespace/strange characters in sprite names/inputs. Hashes?
- Implement variables, lists, broadcasts
- Add subcommands to build to a binary and run binary
- Add ability to compile assets into generated binary
- Increase reliability of reading block arguments. Current system is quite rudimentary
- Create appropriate data structures instead of blindly reading from the dictionary
- Consider turbowarp extensions
- Give constants SCREAMING_SNAKE_CASE names
- Improve typing (type all the things)
- Create separated interfaces from go generation and parsing to ast
- Add timer support; allow for delta time calculation and therefore running smoothly at higher fps

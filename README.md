# raylcat
WIP Scratch sb3 -> Go -> machine code compiler using raylib.
Transpilation logic is written in python, output code is pure Go.
This project has very little testing, and is being written written on Fedora 44.
## Requirements
See [gen2brain/raylib-go](https://github.com/gen2brain/raylib-go#requirements)'s requirements section. Raylcat may additionally require Go 1.21+ and python 3.12+.
## Usage
```
git clone https://github.com/humanoidkiwifruit/raylcat.git
cd raylcat
pip install .
raylcat --help
```
alternatively, `uv tool install .` or `pipx install .`
## TODO
- Use a temporary directory as the work dir
- Add flag to pretty-print the IR / log it to file
- Add flag(s) for custom stage size
- Add logging, different levels
- Allow for this-sprite-only variables
- Support scratch's pixel perfect collisions
- Translate the rest of the opcodes
- Proper error handling
- Stop leaving dead goroutines around everywhere
- Uilise clean_name more
- Implement broadcasts, clones
- Add commands to package binary and assets into zip
- Add ability to compile assets into generated binary
- Increase reliability of reading block arguments. Current system is quite rudimentary
- Consider turbowarp extensions
- Give constants SCREAMING_SNAKE_CASE names
- Improve typing (type all the things)
- Create separated interfaces from go generation and parsing to ast
- Possibly add a flag to run the generated code through gofmt for easier reading
- Check actual minimum python version
- Move OrderedRender into Context
- Maybe add some comments eh

# raylcat
WIP Scratch sb3 -> Go -> machine code compiler using raylib.
Transpilation logic is written in python, output code is pure Go.
This project has very little testing, and is written written on Fedora 44.
## Usage
```
git clone https://github.com/humanoidkiwifruit/raylcat.git
cd raylcat
pip install .
raylcat --help
```
## TODO
- Use a temporary directory as the work dir
- Add logging, different levels
- Support scratch's pixel perfect collisions
- Translate the rest of the opcodes
- Proper error handling
- Uilise clean_name more
- Implement broadcasts
- Add commands to package binary and assets into zip
- Add ability to compile assets into generated binary
- Increase reliability of reading block arguments. Current system is quite rudimentary
- Consider turbowarp extensions
- Give constants SCREAMING_SNAKE_CASE names
- Improve typing (type all the things)
- Create separated interfaces from go generation and parsing to ast
- Possibly add a flag to run the generated code through gofmt for easier reading
- Add flag to set custom framerate
- Check actual minimum python version
- Move OrderedRender into Context
- Split up generation.py
- Maybe add some comments eh

# raylcat
A work-in-progress transpiler for Scratch 3 (.sb3) projects, translating them to Go code then native machine code.
[Raylib-go](https://github.com/gen2brain/raylib-go) is used for rendering, transpilation logic is written in python, output code is pure Go.
This project has very little testing (consisting of essentially "does it compile my example sb3 correctly"), and development currently happens on Fedora 44, in case that's relevant. Most linux distros should be fine, but keep in mind that other platforms are untested (although contributions to fix this are welcome!).
## Requirements
See [gen2brain/raylib-go's requirements section](https://github.com/gen2brain/raylib-go#requirements). Raylcat requires Go 1.21+ and python 3.12+.
## Installation
```bash
git clone https://github.com/humanoidkiwifruit/raylcat.git
cd raylcat
#See below
```
### Using uv (recommended)
```bash
uv tool install .
```
### Using pip
When installing pip packages on most linux distributions, a virtual environment (venv) must be created to avoid conflicting with system packages.
```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```
### Using pipx
```bash
pipx install .
```
## Usage
```bash
raylcat --help
```
## TODO
### Features
- Add flag(s) for custom stage size
- Allow for this-sprite-only variables
- Implement broadcasts, clones
- Support scratch's pixel perfect collisions
- Translate the remaining opcodes
- Consider (turbowarp) extensions
- Add ability to compile assets into generated binary
- Add commands to package binary and assets into zip
- Use a temporary directory as the work dir (don't make useless directories on the user's machine)

### Code quality/DX
- Add logging, different levels
- Proper error handling
- Increase reliability of reading block arguments. Current system is quite rudimentary
- Create separated interfaces from go generation and parsing to ast
- Move OrderedRender into Context
- Add comments!
- Give constants SCREAMING_SNAKE_CASE names
- Improve typing (type all the things)
- Add flag to pretty-print the IR / log it to file
- Stop leaving dead goroutines around everywhere
- Uilise clean_name more
- Possibly add a flag to run the generated code through gofmt for easier reading
- Check actual minimum python version
- Add info about contributing
## Contributing
Keep in mind I am an idiot, I don't really know what I'm doing :P

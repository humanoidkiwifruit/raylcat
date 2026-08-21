# raylcat
WIP Scratch sb3 -> Go -> machine code compiler using raylib.
Currently only has the ability to deal with rudimentary blocks, supporting only bitmap textures.

## TODO
- Add svg support / automatically rasterise SVGs
- Translate opcodes
- Proper handling of whitespace/strange characters in sprite names. Hashes?
- Support multiple costumes
- Implement variables, lists, broadcasts
- Implement proper rendering order
- Add subcommands to build to a binary and run binary
- Handle keyboard input
- Add ability to compile assets into generated binary
- separate argument parsing logic from transpilation logic more
- Stop needlessly passing a *ScratchSprite into blocks that don't need it
- Increase reliability of reading block arguments. Current system is quite rudimentary
- Create an enum (?) for the keys that scratch is able to access
- Create appropriate data structures instead of blindly reading from the dictionary every time
- Consider turbowarp extensions

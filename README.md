# raylcat
Scratch sb3 -> Odin -> machine code compiler using raylib.
Currently only has the ability to place sprites on the stage and deal with rudimentary blocks, supporting only bitmap textures.

# TODO
- Add svg support / automatically rasterise SVGs
- Translate opcodes
- Proper handling of whitespace/strange characters in sprite names. Hashes?
- Support multiple costumes
- Implement variables, lists, broadcasts
- Implement state machine, subsequently fixing bug where green flag clicked scripts get called every frame
- Implement proper rendering order
- Write evaluate_block_to_string function
- Add subcommands to build to a binary and run binary
- Handle keyboard/mouse input

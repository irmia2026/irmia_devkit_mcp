No third-party executable is bundled with this package.

For optional search acceleration, install tools from their official sources and
put them on PATH:

- ripgrep: https://github.com/BurntSushi/ripgrep
- fd: https://github.com/sharkdp/fd
- Everything CLI (Windows only): https://www.voidtools.com/support/everything/command_line_interface/

Advanced users may place their own platform-matching executable in this
directory. Irmia DevKit validates that POSIX candidates are executable and falls
back to PATH or its pure-Python implementations when no binary is available.

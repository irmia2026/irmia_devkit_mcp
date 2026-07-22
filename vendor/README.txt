Bundled search executables
==========================

These files are optional accelerators. Irmia DevKit falls back to PATH or pure
Python when the current platform cannot run them.

File    Platform             Version   Official source asset
------  -------------------  --------  ------------------------------------------------------------
rg      Linux x86-64 (musl)  15.2.0    ripgrep-15.2.0-x86_64-unknown-linux-musl.tar.gz
rg.exe  Windows x86-64       15.2.0    ripgrep-15.2.0-x86_64-pc-windows-msvc.zip
fd      Linux x86-64 (musl)  10.4.2    fd-v10.4.2-x86_64-unknown-linux-musl.tar.gz
fd.exe  Windows x86-64       10.4.2    fd-v10.4.2-x86_64-pc-windows-msvc.zip
es.exe  Windows x86          1.1.0.27  ES-1.1.0.27.x86.zip

Sources:
- https://github.com/BurntSushi/ripgrep/releases/tag/15.2.0
- https://github.com/sharkdp/fd/releases/tag/v10.4.2
- https://www.voidtools.com/ES-1.1.0.27.x86.zip

Downloaded archive provenance
-----------------------------

Archive / URL
  SHA-256
  Extracted member

ripgrep-15.2.0-x86_64-unknown-linux-musl.tar.gz
  https://github.com/BurntSushi/ripgrep/releases/download/15.2.0/ripgrep-15.2.0-x86_64-unknown-linux-musl.tar.gz
  33e15bcf1624b25cdd2a55813a47a2f95dbe126268203e76aa6a585d1e7b149c
  ripgrep-15.2.0-x86_64-unknown-linux-musl/rg -> vendor/rg

ripgrep-15.2.0-x86_64-pc-windows-msvc.zip
  https://github.com/BurntSushi/ripgrep/releases/download/15.2.0/ripgrep-15.2.0-x86_64-pc-windows-msvc.zip
  71b2fef860abe467217a538ff31de02f5258807c0129f771846f87bd029aafc5
  ripgrep-15.2.0-x86_64-pc-windows-msvc/rg.exe -> vendor/rg.exe

fd-v10.4.2-x86_64-unknown-linux-musl.tar.gz
  https://github.com/sharkdp/fd/releases/download/v10.4.2/fd-v10.4.2-x86_64-unknown-linux-musl.tar.gz
  e3257d48e29a6be965187dbd24ce9af564e0fe67b3e73c9bdcd180f4ec11bdde
  fd-v10.4.2-x86_64-unknown-linux-musl/fd -> vendor/fd

fd-v10.4.2-x86_64-pc-windows-msvc.zip
  https://github.com/sharkdp/fd/releases/download/v10.4.2/fd-v10.4.2-x86_64-pc-windows-msvc.zip
  b2816e506390a89941c63c9187d58a3cc10e9a55f2ef0685f9ea0eccaf7c98c8
  fd-v10.4.2-x86_64-pc-windows-msvc/fd.exe -> vendor/fd.exe

ES-1.1.0.27.x86.zip
  https://www.voidtools.com/ES-1.1.0.27.x86.zip
  c8502d7c54a90340f3a1fdf6ca46783e3d548b6791f532ef98172d640a7b6449
  es.exe -> vendor/es.exe

Verify the extracted files with SHA256SUMS before publishing. Third-party
license notices are in THIRD_PARTY_LICENSES.txt. SHA256SUMS is the runtime source
of truth. When an official asset is upgraded, replace the extracted file and
update SHA256SUMS plus the pinned packaging-test expectation in the same change.

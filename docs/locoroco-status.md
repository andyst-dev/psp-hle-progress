# LocoRoco native bring-up: measured status

Reference: LocoRoco Europe/Australia, UCES00304. This is an experimental native
macOS arm64 bring-up, **not a playable port**. The HLE availability diagram is
not a completion percentage for this work.

## What exists

- The main EBOOT was extracted and decrypted. System modules were also extracted,
  decrypted and decompressed as required, then inspected. This does not mean
  those modules or the PSP Media Engine are executing natively.
- The discovered main-program corpus was emitted as low-level C and compiled:
  14,301 discovered functions, 224 function translation units plus imports and
  registration, and 236 distinct imported firmware entry points. Automatic
  discovery is not proof that every original function or execution path is correct.
- Ghidra is available for targeted analysis and decompilation. There is no complete
  recovered, named and maintainable original source tree.
- A compatible loader/runtime and cooperative threaded scheduler execute the
  game's real startup code. The language screen, animated logo and recognizable
  scenery have been captured through the native renderer.
- START and Cross are observed through the input path. For Cross, the active
  condition evaluates true, a fade-out request reaches its component and that
  component later emits its completion signal.

## Latest recorded bounded run

The frozen local integration uses revision `cb43d7a`. Its registry has 122
handlers matching 236 imports; the separate upstream main snapshot at `5ca18fa` has 120.

- Wall watchdog: 90 seconds; stop is intentional, not a reported crash.
- Actual dispatch count: 306,968,119; this is not an instruction count.
- 525 counted vblanks; not a meaningful standalone gameplay-FPS benchmark.
- 11 guest threads created and started.
- 6,048,815 bytes read.
- Zero missing dispatch targets and zero invalid memory accesses detected by the
  runtime in that observed execution window.
- 907 invocations of unimplemented firmware calls, not 907 distinct functions.
- Cross supplied around vblank 240; the matching fade-completion event observed
  at vblank 257.
- Final capture shows green gear-shaped scenery and the copyright strip, not a
  usable menu or a validated playable level. Differences between animation
  phases are not, by themselves, evidence of a fix.

The runtime remains partial: absence of detected invalid accesses is not proof
of complete firmware behavior or safety on every path.

## Important diagnostic dependency

Resource loading still depends on a private ISO adapter. It supplies real
image-derived sector metadata at an observed metadata return, then serves the
requested image ranges through an overlay. Original game instructions and
extracted files are not patched, but this metadata injection is an experimental
substitute, **not a general upstream UMD/ISO backend**.

The latest runs reuse frozen emitted objects and runtime artifacts whose hashes
were checked. Publishing a generic fix did not silently rebase or rebuild that
private integration.

## Problems already isolated

- VFPU decode/emission errors and non-finite constants that did not compile.
- Split-body control flow, delay slots and continuations.
- Scheduling and audio timing that prevented useful progress.
- Invalid/empty filenames and missing host metadata.
- Native stack growth where body-local return frames inhibited terminal transfers.
- Missing continuation after a linking JALR, omitting an epilogue and corrupting
  the guest stack before later invalid reads.

The two most recent generic fixes are separate contributions:

- [#31](https://github.com/sp00nznet/psprecomp/pull/31): linked-JALR continuation.
- [#32](https://github.com/sp00nznet/psprecomp/pull/32): guest-call frame isolation.

The [#32 CI run](https://github.com/sp00nznet/psprecomp/actions/runs/40228649913)
passed six Windows/MSVC, Linux/GCC and macOS/Apple Clang jobs, real threads OFF
and ON. Each ran 22 tests and twenty repetitions of ten scheduler/lifecycle
cases. This qualifies toolkit behavior, not playable LocoRoco on those systems.

## What remains

1. Follow the actions that consume the observed fade-completion signal and
   verify the next actual state request. Input reception and the completion
   signal are already observed; the current absence of a usable menu has no
   established root cause yet.
2. Replace or qualify the private image/sector adapter with a proper backend.
3. Reach a usable main menu, then a controllable first level. Neither is validated.
4. Complete and validate rendering, save/utility behavior, audio and video.
   Texture/palette/blending support already exists, but complete GE fidelity is
   not established. The current audio-output path counts and paces blocks rather
   than sending them to a real audio device; reaching SAS/audio calls is not
   proof of audible, faithful music or effects.
5. Validate performance and longer sessions with normal interaction rather than
   treating instrumented, bounded runs as finished gameplay.

The immediate technical frontier is **after fade completion**, not simply a
missing button or an unfinished fade. No reliable whole-project percentage or
release date follows from the number of translated functions or registered APIs.

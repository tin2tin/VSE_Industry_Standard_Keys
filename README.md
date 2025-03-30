# VSE_Industry_Standard_Keys

# VSE Industry Standard Keymap Add-on - Key Changes

This add-on modifies the Blender Video Sequence Editor (VSE) keymap to align more closely with common Non-Linear Editors (NLEs), aiming for a more keyboard-driven workflow. It includes audio adjustment controls and adds several useful operators to the VSE menus.

Changes described here: https://docs.google.com/document/u/1/d/e/2PACX-1vTNx-Ed8XN7UCmKGoWFk_PbEep9YOTArnuyqtk1fHukf2H3-_U4TGm4IXPANGDp22lxBv0dt5_s2Xwi/pub

**Important Notes:**

*   **'K' Key Conflict:** The `K` key is mapped to **Stop Playback**. This conflicts with Blender's default VSE keymap where `K` is often used for **Cut/Split**. To ensure `K` works for stopping playback as intended by this add-on, you may need to manually disable the default `K` keybinding for `sequencer.cut` or `sequencer.split` in **Edit > Preferences > Keymap**.
*   **'L' Key Override:** The `L` key is mapped to **Play Forward**, replacing Blender's default **Pick Linked** function in the VSE.
*   **'G' Key:** The standard Blender **Grab/Move (`G`)** key is *not* overridden. The Gain/Volume popup uses `V`.
*   **Slide Operator (`U`, `,`, `.`):** The standard NLE Slide function is **NOT** included, as it requires an uncommitted Blender patch (D9829). These keys remain unmapped by this add-on.
*   **Warnings During Registration:** You might see console warnings like "Property '...' not found..." when enabling the add-on. If the keybindings work correctly when tested in the VSE, these warnings can likely be ignored.
*   **Limitations:** JKL multi-speed/slow-motion is not implemented. Core Blender operators used here generally do not respect channel locking.

## Keymap Changes:

### Playback (JKL Style)

*   `J`: Play Reverse (`screen.animation_play`, `reverse=True`)
*   `K`: Stop Playback (`screen.animation_cancel`) - **Requires checking default keymap conflict.**
*   `L`: Play Forward (`screen.animation_play`, `reverse=False`) - **Overrides Pick Linked.**

### Frame Stepping

*   `Shift + J`: Step Back 1 Frame (`screen.frame_offset`, `delta=-1`)
*   `Shift + K`: Step Forward 1 Frame (`screen.frame_offset`, `delta=1`)
*   `Ctrl + J`: Step Back 5 Frames (`screen.frame_offset`, `delta=-5`)
*   `Ctrl + K`: Step Forward 5 Frames (`screen.frame_offset`, `delta=5`)

### Editing & Selection

*   `Ctrl + K`: Split Strips at Playhead (`sequencer.split`, uses cursor)
*   `Ctrl + Alt + K`: Split Selected Strip(s) at Handles & Remove Middle (`sequencer.split`, `side='BOTH'`) - **Note:** Different from Premiere "Hold Split".
*   `D`: Select Strip Handles at Current Frame (`sequencer.select_side_of_frame`, `side='CURRENT'`)
*   `Alt + Y`: Select Strip Handles After (Right of) Current Frame (`sequencer.select_side_of_frame`, `side='RIGHT'`)
*   `Ctrl + Alt + Y`: Select Strip Handles Before (Left of) Current Frame (`sequencer.select_side_of_frame`, `side='LEFT'`)
*   `Shift + D`: Extend Selection (`sequencer.select_more`)
*   `Ctrl + Backspace`: Remove All Gaps (`sequencer.gap_remove`, `all=True`)
*   `Shift + Ctrl + ,` (Comma): Swap Active Strip with Strip to the Left (`sequencer.swap_inputs`, `side='LEFT'`) - **Note:** Works on *active*, not selected.
*   `Shift + Ctrl + .` (Period): Swap Active Strip with Strip to the Right (`sequencer.swap_inputs`, `side='RIGHT'`) - **Note:** Works on *active*, not selected.

### Transitions

*   `Ctrl + D`: Add Default Transition (`sequencer.transition_add`)
*   `Ctrl + Shift + D`: Add Default Transition (Audio Attempt) (`sequencer.transition_add`)

### Audio Control

*   `V`: Adjust Volume Popup (Selected Audio Strips) (`sequencer.adjust_volume_popup`)
*   `Ctrl + =`: Increase Volume by ~1dB (`sequencer.adjust_volume_step`, `direction='UP'`)
*   `Ctrl + Shift + =` (`Ctrl++`): Increase Volume by ~1dB (`sequencer.adjust_volume_step`, `direction='UP'`)
*   `Ctrl + -`: Decrease Volume by ~1dB (`sequencer.adjust_volume_step`, `direction='DOWN'`)

### Zoom & Navigation

*   `=` / `Numpad +`: Zoom In (`view2d.zoom_in`)
*   `Shift + =` (`+` on most layouts): Zoom In (`view2d.zoom_in`)
*   `-` / `Numpad -`: Zoom Out (`view2d.zoom_out`)
*   `\` (Backslash): Zoom to Selected Strips (`sequencer.view_selected`)
*   `Shift + Left Arrow`: Go to First Frame of Timeline/Preview Range (`screen.frame_jump`, `next=False`)
*   `Shift + Right Arrow`: Go to Last Frame of Timeline/Preview Range (`screen.frame_jump`, `next=True`)
*   `Ctrl + Alt + R`: Set Timeline Range to Selected Strips (`sequencer.set_range_to_strips`)
*   `Ctrl + Alt + P`: Set Preview Range to Selected Strips (`sequencer.set_preview_range_to_strips`)

## Menu Additions

The add-on also exposes the following operators in the VSE menus (`View`, `Select`, `Strip`):

*   Zoom to Selected (`\`)
*   Set Preview Range to Strips (`Ctrl+Alt+P`)
*   Set Range to Strips (`Ctrl+Alt+R`)
*   Go to First/Last Frame in Range (`Shift+Left/Right`)
*   Select At Playhead (Current/Before/After) (`D`, `Ctrl+Alt+Y`, `Alt+Y`)
*   Extend Selection (`Shift+D`)
*   Adjust Volume Popup (`V`)
*   Volume +/- 1dB (`Ctrl+=`, `Ctrl+-`)
*   Remove All Gaps (`Ctrl+Backspace`)
*   Add Default Transition (`Ctrl+D`, `Ctrl+Shift+D`)

---

Please test these keybindings in the VSE to ensure they function as expected. Remember to check the `K` key conflict if necessary.

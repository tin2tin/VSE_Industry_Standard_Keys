# <pep8 compliant>
bl_info = {
    "name": "VSE Industry Standard Keymap",
    "author": "Based on community request", # Updated author
    "version": (1, 1, 9), # Incremented version
    "blender": (3, 5, 0), # Minimum version tested, might work on others
    "location": "Video Sequence Editor > Keymap & Menus",
    "description": "Adds common NLE keybindings and audio controls (Gain Popup [V], Volume Up/Down [Ctrl+=/-]) to the VSE.",
    "warning": "Requires testing. 'K' key for Stop may conflict with default Cut keybind (disable in Prefs if needed). Slide operator [U] requires uncommitted patch D9829 and is NOT included. Warnings about properties may appear. JKL multi-speed/slow-mo not implemented. Channel Locks not fully respected.",
    "doc_url": "https://gist.github.com/tin2tin/efd996ee01140592c3769150f5be4a78",
    "category": "Sequencer",
}

import bpy
import math # Needed for dB calculation

# --- Custom Operators ---

# Function to get selected sequences in VSE
def get_selected_sequences(context):
    return [seq for seq in context.scene.sequence_editor.sequences if seq.select]

# Refined Volume Adjustment Operator (Popup)
class SEQUENCER_OT_adjust_volume_popup(bpy.types.Operator):
    """Adjust Volume/Gain for selected sound strips"""
    bl_idname = "sequencer.adjust_volume_popup"
    bl_label = "Adjust Volume (Gain)"
    bl_options = {'REGISTER', 'UNDO'}

    # Property representing the volume multiplier
    volume: bpy.props.FloatProperty(
        name="Volume", # Changed name for clarity
        description="Set volume multiplier for selected sound strips (1.0 is 0dB)", # Updated description
        default=1.0,
        min=0.0,
        soft_max=10.0 # Allow going above 1.0, adjust as needed
    )

    @classmethod
    def poll(cls, context):
        # Only active if VSE is open and sound sequences are selected
        selected_sequences = get_selected_sequences(context)
        sound_strips = [s for s in selected_sequences if s.type == 'SOUND']
        return context.scene and context.scene.sequence_editor and len(sound_strips) > 0

    def execute(self, context):
        selected_sequences = get_selected_sequences(context)
        sound_strips = [s for s in selected_sequences if s.type == 'SOUND']

        # Should not happen due to poll, but check anyway
        if not sound_strips:
            self.report({'WARNING'}, "No sound strips selected (should be blocked by poll)")
            return {'CANCELLED'}

        count = 0
        for strip in sound_strips:
            strip.volume = self.volume
            count += 1

        self.report({'INFO'}, f"Set volume to {self.volume:.3f} for {count} strip(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        # --- MODIFIED LOGIC ---
        # Set default value based on active or first selected sound strip
        active_strip = context.scene.sequence_editor.active_strip
        current_volume = 1.0 # Default fallback

        # Prioritize active strip if it's a selected sound strip
        if active_strip and active_strip.select and active_strip.type == 'SOUND':
             current_volume = active_strip.volume
        else:
             # Otherwise, find the first selected sound strip
             selected_sequences = get_selected_sequences(context)
             sound_strips = [s for s in selected_sequences if s.type == 'SOUND']
             if sound_strips:
                 current_volume = sound_strips[0].volume
             # If somehow no sound strips are selected (despite poll), keep default 1.0

        # Set the operator's property default *before* showing the dialog
        self.volume = current_volume
        # --- END MODIFIED LOGIC ---

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    
    
# Simplified Volume Adjustment Operator (Steps +/- 1dB)
class SEQUENCER_OT_adjust_volume_step(bpy.types.Operator):
    """Adjust Volume/Gain for selected sound strips by approx. 1 dB"""
    bl_idname = "sequencer.adjust_volume_step"
    bl_label = "Adjust Volume Step (+/- 1dB)"
    bl_options = {'REGISTER', 'UNDO'}

    direction: bpy.props.EnumProperty(
        name="Direction",
        items=[('UP', "Up", "Increase volume by ~1dB"),
               ('DOWN', "Down", "Decrease volume by ~1dB")],
        default='UP'
    )

    # 1 dB change multiplier: 10^(1/20) approx 1.122
    # -1 dB change multiplier: 10^(-1/20) approx 0.891
    db_step_multiplier_up: bpy.props.FloatProperty(default=1.122018454)
    db_step_multiplier_down: bpy.props.FloatProperty(default=0.891250938)

    @classmethod
    def poll(cls, context):
        return context.scene and context.scene.sequence_editor and len(get_selected_sequences(context)) > 0

    def execute(self, context):
        selected_sequences = get_selected_sequences(context)
        sound_strips = [s for s in selected_sequences if s.type == 'SOUND']

        if not sound_strips:
            self.report({'INFO'}, "No sound strips selected")
            return {'CANCELLED'}

        multiplier = self.db_step_multiplier_up if self.direction == 'UP' else self.db_step_multiplier_down

        for strip in sound_strips:
            strip.volume *= multiplier
            # Optional: Clamp volume if needed (e.g., strip.volume = max(0.0, strip.volume))

        direction_text = "+1dB" if self.direction == 'UP' else "-1dB"
        self.report({'INFO'}, f"Adjusted volume by ~{direction_text}")

        return {'FINISHED'}


# --- Store keymap items references ---
_keymap_items = []
_addon_keymaps = []

# --- Menu Draw Functions ---
def draw_view_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator("sequencer.view_selected", text="Zoom to Selected (\\)")
    layout.operator("sequencer.set_preview_range_to_strips", text="Set Preview Range to Strips (Ctrl+Alt+P)")
    layout.operator("sequencer.set_range_to_strips", text="Set Range to Strips (Ctrl+Alt+R)")
    layout.separator()
    layout.label(text="Navigate Range:")
    op_props = layout.operator("screen.frame_jump", text="Go to First Frame in Range (Shift+Left)")
    op_props.next = False
    op_props = layout.operator("screen.frame_jump", text="Go to Last Frame in Range (Shift+Right)")
    op_props.next = True

def draw_select_menu(self, context):
    layout = self.layout
    layout.separator()
    col = layout.column()
    col.label(text="Select At Playhead:")
    op = col.operator("sequencer.select_side_of_frame", text="Current Frame (D)")
    op.side = 'CURRENT'
    op = col.operator("sequencer.select_side_of_frame", text="Before Current Frame (Ctrl+Alt+Y)")
    op.side = 'LEFT'
    op = col.operator("sequencer.select_side_of_frame", text="After Current Frame (Alt+Y)")
    op.side = 'RIGHT'

    layout.separator()
    col = layout.column()
    col.label(text="Extend Selection At Playhead:")
    col.operator("sequencer.select_more", text="Extend Selection (Shift+D)")

def draw_strip_menu(self, context):
    layout = self.layout
    layout.separator()
    # Add Volume operators to Strip menu
    layout.operator(SEQUENCER_OT_adjust_volume_popup.bl_idname, text="Adjust Volume (V)")
    row = layout.row(align=True)
    # Set properties directly for menu items
    op_up = row.operator(SEQUENCER_OT_adjust_volume_step.bl_idname, text="Volume +1dB (Ctrl+=)")
    op_up.direction = 'UP'
    op_down = row.operator(SEQUENCER_OT_adjust_volume_step.bl_idname, text="Volume -1dB (Ctrl+-)")
    op_down.direction = 'DOWN'
    layout.separator()
    op = layout.operator("sequencer.gap_remove", text="Remove All Gaps (Ctrl+Backspace)")
    op.all = True
    layout.separator()
    layout.label(text="Transitions:")
    layout.operator("sequencer.transition_add", text="Add Default Transition (Ctrl+D)")
    layout.operator("sequencer.transition_add", text="Add Default Transition (Audio) (Ctrl+Shift+D)")


# --- Keymap Definitions ---
# Added Audio adjustment keys
keymap_defs = [
    # Playback
    ("screen.animation_play", 'J', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, [("reverse", True)]),
    ("screen.animation_cancel", 'K', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, [("restore_frame", False)]),
    ("screen.animation_play", 'L', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, [("reverse", False)]),
    # Frame Stepping
    ("screen.frame_offset", 'J', 'PRESS', {"shift": True, "ctrl": False, "alt": False}, None, [("delta", -1)]),
    ("screen.frame_offset", 'K', 'PRESS', {"shift": True, "ctrl": False, "alt": False}, None, [("delta", 1)]),
    ("screen.frame_offset", 'J', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, [("delta", -5)]),
    ("screen.frame_offset", 'K', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, [("delta", 5)]),
    # Split
    ("sequencer.split", 'K', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, [("use_cursor_position", True), ("side", 'NO_CHANGE')]),
    ("sequencer.split", 'K', 'PRESS', {"shift": False, "ctrl": True, "alt": True}, None, [("side", 'BOTH'), ("use_cursor_position", False)]),
    # Zoom
    ("view2d.zoom_in", 'EQUAL', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, None),
    ("view2d.zoom_in", 'NUMPAD_PLUS', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, None),
    ("view2d.zoom_in", 'PLUS', 'PRESS', {"shift": True, "ctrl": False, "alt": False}, None, None), # For Shift+=
    ("view2d.zoom_out", 'MINUS', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, None),
    ("view2d.zoom_out", 'NUMPAD_MINUS', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, None),
    ("sequencer.view_selected", 'BACK_SLASH', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, None),
    # Select
    ("sequencer.select_side_of_frame", 'D', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, [("side", 'CURRENT')]),
    ("sequencer.select_side_of_frame", 'Y', 'PRESS', {"shift": False, "ctrl": False, "alt": True}, None, [("side", 'RIGHT')]),
    ("sequencer.select_side_of_frame", 'Y', 'PRESS', {"shift": False, "ctrl": True, "alt": True}, None, [("side", 'LEFT')]),
    # Extend Selection
    ("sequencer.select_more", 'D', 'PRESS', {"shift": True, "ctrl": False, "alt": False}, None, None),
    # Add Transition
    ("sequencer.transition_add", 'D', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, None),
    ("sequencer.transition_add", 'D', 'PRESS', {"shift": True, "ctrl": True, "alt": False}, None, None),
    # Swap
    ("sequencer.swap_inputs", 'COMMA', 'PRESS', {"shift": True, "ctrl": True, "alt": False}, None, [("side", 'LEFT')]),
    ("sequencer.swap_inputs", 'PERIOD', 'PRESS', {"shift": True, "ctrl": True, "alt": False}, None, [("side", 'RIGHT')]),

    # --- NEW Audio ---
    (SEQUENCER_OT_adjust_volume_popup.bl_idname, 'V', 'PRESS', {"shift": False, "ctrl": False, "alt": False}, None, None), # Volume Popup
    (SEQUENCER_OT_adjust_volume_step.bl_idname, 'EQUAL', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, [("direction", 'UP')]), # Volume Up (Ctrl+=)
    (SEQUENCER_OT_adjust_volume_step.bl_idname, 'PLUS', 'PRESS', {"shift": True, "ctrl": True, "alt": False}, None, [("direction", 'UP')]), # Volume Up (Ctrl+Shift+= for Ctrl++)
    (SEQUENCER_OT_adjust_volume_step.bl_idname, 'MINUS', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, [("direction", 'DOWN')]), # Volume Down (Ctrl+-)

    # Navigation/Other
    ("screen.frame_jump", 'LEFT_ARROW', 'PRESS', {"shift": True, "ctrl": False, "alt": False}, None, [("next", False)]),
    ("screen.frame_jump", 'RIGHT_ARROW', 'PRESS', {"shift": True, "ctrl": False, "alt": False}, None, [("next", True)]),
    ("sequencer.gap_remove", 'BACK_SPACE', 'PRESS', {"shift": False, "ctrl": True, "alt": False}, None, [("all", True)]),
    ("sequencer.set_range_to_strips", 'R', 'PRESS', {"shift": False, "ctrl": True, "alt": True}, None, None),
    ("sequencer.set_preview_range_to_strips", 'P', 'PRESS', {"shift": False, "ctrl": True, "alt": True}, None, None),
]


# --- Registration ---
classes = (
    SEQUENCER_OT_adjust_volume_popup,
    SEQUENCER_OT_adjust_volume_step,
)

def register_keymaps():
    # (Function body remains the same as v1.1.8 - using setattr)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Sequencer', space_type='SEQUENCE_EDITOR')
        _addon_keymaps.append(km)

        for (idname, type, value, mods, _descr_placeholder, props_list) in keymap_defs:
            kmi = km.keymap_items.new(
                idname, type, value,
                any=mods.get("any", False),
                shift=mods.get("shift", False), ctrl=mods.get("ctrl", False),
                alt=mods.get("alt", False), oskey=mods.get("oskey", False)
            )

            if props_list:
                for prop_name, prop_value in props_list:
                    try:
                        setattr(kmi.properties, prop_name, prop_value)
                    except AttributeError:
                         print(f"Warning: Property '{prop_name}' not found for operator '{idname}' during keymap registration (may be non-fatal).")
                    except TypeError as e:
                         print(f"ERROR setting property '{prop_name}' = {repr(prop_value)} for operator '{idname}': {e}")

            _keymap_items.append(kmi)

def unregister_keymaps():
    # (Function body remains the same as v1.1.8)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        kms_to_remove = [k for k in _addon_keymaps if k.name in kc.keymaps]
        for km in kms_to_remove:
            try:
                kc.keymaps.remove(km)
            except Exception as e:
                print(f"Warning: Failed to remove keymap {km.name}: {e}")

    _addon_keymaps.clear()
    _keymap_items.clear()


# Menu pairs remain the same
menu_draw_pairs = [
    (bpy.types.SEQUENCER_MT_view, draw_view_menu),
    (bpy.types.SEQUENCER_MT_select, draw_select_menu),
    (bpy.types.SEQUENCER_MT_strip, draw_strip_menu),
]

def register():
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register Keymaps
    try:
        register_keymaps()
    except Exception as e:
        print(f"ERROR during keymap registration: {e}")
        unregister_keymaps()
        # Also unregister classes if keymap fails
        for cls in reversed(classes):
            try: bpy.utils.unregister_class(cls)
            except Exception: pass
        raise e

    # Append Menu Functions
    for menu_cls, draw_func in menu_draw_pairs:
        is_registered = False
        if hasattr(menu_cls, "_draw_funcs"):
             if draw_func in menu_cls._draw_funcs:
                 is_registered = True
        
        if not is_registered:
            try:
                menu_cls.append(draw_func)
            except Exception as e:
                print(f"Warning: Failed to append draw function {draw_func.__name__} to {menu_cls.__name__}: {e}")


def unregister():
    # Unregister Keymaps first
    try:
        unregister_keymaps()
    except Exception as e:
        print(f"ERROR during keymap unregistration: {e}")

    # Remove Menu Functions
    for menu_cls, draw_func in menu_draw_pairs:
        try:
            if hasattr(menu_cls, "remove"):
                menu_cls.remove(draw_func)
        except Exception:
            pass

    # Unregister classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Warning: Failed to unregister class {cls.__name__}: {e}")


if __name__ == "__main__":
    try:
        unregister() # Run unregister first when testing in text editor
    except Exception as e:
        print(f"Pre-registration unregister failed (ignore if first run): {e}")

    print(f"Registering {bl_info.get('name')} (v{bl_info.get('version')})...")
    register()
    print("Registration complete.")
    print("NOTE: Warnings about properties not found may appear (ignore if keys work).")
    print("      Please test the keybinding functionality.")
    print("      IMPORTANT: Check 'K' key conflict, Slide [U] requires patch.")

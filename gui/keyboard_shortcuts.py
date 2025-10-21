"""
Keyboard Shortcuts Manager for Worklog Manager Application

Handles registration, binding, and management of keyboard shortcuts.
Provides customizable hotkeys for common application actions.
"""

import tkinter as tk
from typing import Dict, Callable, Optional, List, Tuple
import re
from dataclasses import dataclass

@dataclass
class ShortcutBinding:
    """Represents a keyboard shortcut binding."""
    key_combination: str
    action: str
    callback: Callable
    description: str
    enabled: bool = True

class KeyboardShortcutManager:
    """Manages keyboard shortcuts for the worklog application."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.bindings: Dict[str, ShortcutBinding] = {}
        self.key_mappings: Dict[str, str] = {}  # Maps key combinations to action names
        
        # Standard key name mappings
        self.key_aliases = {
            'ctrl': 'Control',
            'alt': 'Alt',
            'shift': 'Shift',
            'cmd': 'Command',  # For macOS
            'meta': 'Meta',    # For Linux
            'win': 'Win',      # For Windows key
        }
        
        # Special key mappings
        self.special_keys = {
            'space': 'space',
            'enter': 'Return',
            'return': 'Return',
            'tab': 'Tab',
            'escape': 'Escape',
            'esc': 'Escape',
            'backspace': 'BackSpace',
            'delete': 'Delete',
            'del': 'Delete',
            'insert': 'Insert',
            'home': 'Home',
            'end': 'End',
            'pageup': 'Page_Up',
            'pagedown': 'Page_Down',
            'up': 'Up',
            'down': 'Down',
            'left': 'Left',
            'right': 'Right',
        }
        
        # Function key mappings
        for i in range(1, 13):
            self.special_keys[f'f{i}'] = f'F{i}'
    
    def register_shortcut(self, action: str, key_combination: str, 
                         callback: Callable, description: str = "") -> bool:
        """Register a new keyboard shortcut."""
        try:
            # Parse and validate key combination
            parsed_keys = self._parse_key_combination(key_combination)
            if not parsed_keys:
                return False
            
            # Remove existing binding for this action
            self.unregister_shortcut(action)
            
            # Create binding
            binding = ShortcutBinding(
                key_combination=key_combination,
                action=action,
                callback=callback,
                description=description
            )
            
            # Bind to tkinter
            tk_binding = self._create_tk_binding(parsed_keys)
            if tk_binding:
                self.root.bind_all(tk_binding, self._create_callback_wrapper(binding))
                
                # Store binding
                self.bindings[action] = binding
                self.key_mappings[key_combination.lower()] = action
                
                return True
                
        except Exception as e:
            print(f"Error registering shortcut {action}: {e}")
        
        return False
    
    def unregister_shortcut(self, action: str) -> bool:
        """Unregister a keyboard shortcut."""
        try:
            if action in self.bindings:
                binding = self.bindings[action]
                
                # Remove tkinter binding
                parsed_keys = self._parse_key_combination(binding.key_combination)
                if parsed_keys:
                    tk_binding = self._create_tk_binding(parsed_keys)
                    if tk_binding:
                        self.root.unbind_all(tk_binding)
                
                # Remove from storage
                del self.bindings[action]
                if binding.key_combination.lower() in self.key_mappings:
                    del self.key_mappings[binding.key_combination.lower()]
                
                return True
                
        except Exception as e:
            print(f"Error unregistering shortcut {action}: {e}")
        
        return False
    
    def update_shortcut(self, action: str, new_key_combination: str) -> bool:
        """Update an existing shortcut with a new key combination."""
        if action in self.bindings:
            binding = self.bindings[action]
            
            # Unregister old shortcut
            self.unregister_shortcut(action)
            
            # Register with new key combination
            return self.register_shortcut(
                action, new_key_combination, binding.callback, binding.description
            )
        
        return False
    
    def enable_shortcut(self, action: str, enabled: bool = True) -> bool:
        """Enable or disable a shortcut."""
        if action in self.bindings:
            self.bindings[action].enabled = enabled
            return True
        return False
    
    def get_shortcut(self, action: str) -> Optional[ShortcutBinding]:
        """Get a specific shortcut binding."""
        return self.bindings.get(action)
    
    def get_all_shortcuts(self) -> Dict[str, ShortcutBinding]:
        """Get all registered shortcuts."""
        return self.bindings.copy()
    
    def is_key_combination_available(self, key_combination: str) -> bool:
        """Check if a key combination is available (not already used)."""
        return key_combination.lower() not in self.key_mappings
    
    def find_conflicts(self, key_combination: str) -> List[str]:
        """Find actions that conflict with the given key combination."""
        conflicts = []
        normalized_combo = key_combination.lower()
        
        for combo, action in self.key_mappings.items():
            if combo == normalized_combo:
                conflicts.append(action)
        
        return conflicts
    
    def _parse_key_combination(self, key_combination: str) -> Optional[Tuple[List[str], str]]:
        """Parse a key combination string into modifiers and key."""
        try:
            # Clean up the input
            combo = key_combination.strip().lower()
            if not combo:
                return None
            
            # Split by + sign
            parts = [part.strip() for part in combo.split('+')]
            if not parts:
                return None
            
            # Last part is the key, others are modifiers
            key = parts[-1]
            modifiers = parts[:-1] if len(parts) > 1 else []
            
            # Validate and normalize modifiers
            normalized_modifiers = []
            for modifier in modifiers:
                if modifier in self.key_aliases:
                    normalized_modifiers.append(self.key_aliases[modifier])
                elif modifier.capitalize() in ['Control', 'Alt', 'Shift', 'Command', 'Meta', 'Win']:
                    normalized_modifiers.append(modifier.capitalize())
                else:
                    print(f"Unknown modifier: {modifier}")
                    return None
            
            # Validate and normalize key
            normalized_key = self._normalize_key(key)
            if not normalized_key:
                print(f"Invalid key: {key}")
                return None
            
            return (normalized_modifiers, normalized_key)
            
        except Exception as e:
            print(f"Error parsing key combination '{key_combination}': {e}")
            return None
    
    def _normalize_key(self, key: str) -> Optional[str]:
        """Normalize a key name."""
        key = key.lower()
        
        # Check special keys first
        if key in self.special_keys:
            return self.special_keys[key]
        
        # Check if it's a single character
        if len(key) == 1 and key.isalnum():
            return key.upper()
        
        # Check if it's already a valid tkinter key name
        if len(key) > 1:
            # Try capitalizing first letter for keys like 'Return', 'Escape', etc.
            capitalized = key.capitalize()
            return capitalized
        
        return None
    
    def _create_tk_binding(self, parsed_keys: Tuple[List[str], str]) -> Optional[str]:
        """Create a tkinter binding string from parsed keys."""
        try:
            modifiers, key = parsed_keys
            
            # Build tkinter binding string
            binding_parts = []
            
            # Add modifiers
            for modifier in modifiers:
                if modifier == 'Control':
                    binding_parts.append('Control')
                elif modifier == 'Alt':
                    binding_parts.append('Alt')
                elif modifier == 'Shift':
                    binding_parts.append('Shift')
                elif modifier in ['Command', 'Meta']:
                    binding_parts.append('Command')  # macOS
                elif modifier == 'Win':
                    binding_parts.append('Win')
            
            # Add key
            binding_parts.append(key)
            
            # Format as tkinter binding
            if len(binding_parts) == 1:
                return f"<Key-{binding_parts[0]}>"
            else:
                return f"<{'-'.join(binding_parts)}>"
                
        except Exception as e:
            print(f"Error creating tkinter binding: {e}")
            return None
    
    def _create_callback_wrapper(self, binding: ShortcutBinding) -> Callable:
        """Create a callback wrapper that checks if the shortcut is enabled."""
        def wrapper(event=None):
            if binding.enabled:
                try:
                    # Call the actual callback
                    if binding.callback:
                        binding.callback()
                except Exception as e:
                    print(f"Error executing shortcut callback for {binding.action}: {e}")
            return "break"  # Prevent further event propagation
        
        return wrapper
    
    def load_shortcuts_from_settings(self, shortcuts_settings) -> int:
        """Load shortcuts from settings object."""
        loaded_count = 0
        
        # Standard shortcuts mapping
        shortcuts_map = {
            'start_work': ('Start Work Session', None),
            'end_work': ('End Work Session', None),
            'take_break': ('Take Break', None),
            'end_break': ('End Break', None),
            'show_summary': ('Show Daily Summary', None),
            'export_data': ('Export Data', None),
            'settings': ('Open Settings', None),
            'quit_app': ('Quit Application', None),
        }
        
        # Load each shortcut
        for action, (description, _) in shortcuts_map.items():
            key_combination = getattr(shortcuts_settings, action, "")
            if key_combination and key_combination.strip():
                # Note: Callback will be set later when the main application provides them
                success = self.register_shortcut(action, key_combination, None, description)
                if success:
                    loaded_count += 1
        
        return loaded_count
    
    def set_callback(self, action: str, callback: Callable) -> bool:
        """Set or update the callback for an existing shortcut."""
        if action in self.bindings:
            binding = self.bindings[action]
            old_callback = binding.callback
            binding.callback = callback
            
            # Re-register the shortcut to update the tkinter binding
            parsed_keys = self._parse_key_combination(binding.key_combination)
            if parsed_keys:
                tk_binding = self._create_tk_binding(parsed_keys)
                if tk_binding:
                    # Remove old binding
                    if old_callback is None:
                        self.root.unbind_all(tk_binding)
                    
                    # Add new binding
                    self.root.bind_all(tk_binding, self._create_callback_wrapper(binding))
                    return True
        
        return False
    
    def validate_key_combination(self, key_combination: str) -> Tuple[bool, str]:
        """Validate a key combination string."""
        try:
            if not key_combination or not key_combination.strip():
                return False, "Key combination cannot be empty"
            
            parsed = self._parse_key_combination(key_combination)
            if not parsed:
                return False, "Invalid key combination format"
            
            modifiers, key = parsed
            
            # Check for valid modifiers
            if len(modifiers) > 3:
                return False, "Too many modifiers (maximum 3)"
            
            # Check for duplicate modifiers
            if len(modifiers) != len(set(modifiers)):
                return False, "Duplicate modifiers not allowed"
            
            # Check if key is valid
            if not key:
                return False, "Invalid key specified"
            
            # Check for conflicts
            conflicts = self.find_conflicts(key_combination)
            if conflicts:
                return False, f"Key combination conflicts with: {', '.join(conflicts)}"
            
            return True, "Valid key combination"
            
        except Exception as e:
            return False, f"Error validating key combination: {str(e)}"
    
    def get_shortcut_help(self) -> List[Tuple[str, str, str]]:
        """Get help text for all registered shortcuts."""
        help_items = []
        
        for action, binding in self.bindings.items():
            if binding.enabled and binding.key_combination:
                help_items.append((
                    binding.key_combination,
                    binding.description or action.replace('_', ' ').title(),
                    "Enabled" if binding.enabled else "Disabled"
                ))
        
        # Sort by action name
        help_items.sort(key=lambda x: x[1])
        return help_items
    
    def export_shortcuts(self) -> Dict[str, str]:
        """Export current shortcuts configuration."""
        export_data = {}
        
        for action, binding in self.bindings.items():
            if binding.key_combination:
                export_data[action] = binding.key_combination
        
        return export_data
    
    def import_shortcuts(self, shortcuts_data: Dict[str, str], 
                        callbacks: Dict[str, Callable] = None) -> Tuple[int, int]:
        """Import shortcuts configuration."""
        imported_count = 0
        error_count = 0
        
        for action, key_combination in shortcuts_data.items():
            try:
                callback = callbacks.get(action) if callbacks else None
                description = action.replace('_', ' ').title()
                
                success = self.register_shortcut(action, key_combination, callback, description)
                if success:
                    imported_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error importing shortcut {action}: {e}")
                error_count += 1
        
        return imported_count, error_count
    
    def reset_shortcuts(self):
        """Remove all registered shortcuts."""
        actions_to_remove = list(self.bindings.keys())
        
        for action in actions_to_remove:
            self.unregister_shortcut(action)
    
    def get_default_shortcuts(self) -> Dict[str, str]:
        """Get default keyboard shortcuts."""
        return {
            'start_work': 'Ctrl+Shift+S',
            'end_work': 'Ctrl+Shift+E',
            'take_break': 'Ctrl+Shift+B',
            'end_break': 'Ctrl+Shift+R',
            'show_summary': 'Ctrl+Shift+D',
            'export_data': 'Ctrl+Shift+X',
            'settings': 'Ctrl+Comma',
            'quit_app': 'Ctrl+Q'
        }

class ShortcutRecorder:
    """Widget for recording keyboard shortcuts in the settings dialog."""
    
    def __init__(self, parent: tk.Widget, initial_value: str = "",
                 on_changed: Callable[[str], None] = None):
        self.parent = parent
        self.on_changed = on_changed
        self.current_shortcut = initial_value
        
        self.frame = tk.Frame(parent)
        
        # Entry to display current shortcut
        self.entry = tk.Entry(self.frame, width=20, state='readonly')
        self.entry.pack(side='left', padx=(0, 5))
        
        # Record button
        self.record_btn = tk.Button(self.frame, text="Record", 
                                  command=self.start_recording)
        self.record_btn.pack(side='left', padx=2)
        
        # Clear button
        self.clear_btn = tk.Button(self.frame, text="Clear", 
                                 command=self.clear_shortcut)
        self.clear_btn.pack(side='left', padx=2)
        
        # Update display
        self.update_display()
    
    def pack(self, **kwargs):
        """Pack the recorder frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the recorder frame."""
        self.frame.grid(**kwargs)
    
    def update_display(self):
        """Update the display with current shortcut."""
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.current_shortcut)
        self.entry.config(state='readonly')
    
    def start_recording(self):
        """Start recording a new shortcut."""
        # Create recording dialog
        self.recording_dialog = tk.Toplevel(self.parent)
        self.recording_dialog.title("Record Shortcut")
        self.recording_dialog.geometry("300x150")
        self.recording_dialog.transient(self.parent)
        self.recording_dialog.grab_set()
        
        # Center the dialog
        self.recording_dialog.update_idletasks()
        x = (self.recording_dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.recording_dialog.winfo_screenheight() // 2) - (150 // 2)
        self.recording_dialog.geometry(f"300x150+{x}+{y}")
        
        # Instructions
        tk.Label(self.recording_dialog, 
                text="Press the desired key combination:", 
                font=('Arial', 12)).pack(pady=20)
        
        # Display area for captured keys
        self.capture_label = tk.Label(self.recording_dialog, 
                                    text="Waiting for input...", 
                                    font=('Arial', 10, 'bold'),
                                    fg='blue')
        self.capture_label.pack(pady=10)
        
        # Button frame
        btn_frame = tk.Frame(self.recording_dialog)
        btn_frame.pack(pady=10)
        
        self.accept_btn = tk.Button(btn_frame, text="Accept", 
                                  command=self.accept_shortcut, state='disabled')
        self.accept_btn.pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Cancel", 
                 command=self.cancel_recording).pack(side='left', padx=5)
        
        # Bind key events
        self.recording_dialog.bind('<KeyPress>', self.on_key_press)
        self.recording_dialog.bind('<KeyRelease>', self.on_key_release)
        self.recording_dialog.focus_set()
        
        # Recording state
        self.pressed_keys = set()
        self.recorded_combination = ""
    
    def on_key_press(self, event):
        """Handle key press during recording."""
        self.pressed_keys.add(event.keysym)
        self.update_capture_display()
    
    def on_key_release(self, event):
        """Handle key release during recording."""
        if event.keysym in self.pressed_keys:
            # If all keys are released, finalize the combination
            if len(self.pressed_keys) == 1:
                self.finalize_combination()
    
    def update_capture_display(self):
        """Update the capture display with current pressed keys."""
        if not self.pressed_keys:
            self.capture_label.config(text="Waiting for input...")
            self.accept_btn.config(state='disabled')
            return
        
        # Separate modifiers and regular keys
        modifiers = []
        regular_keys = []
        
        for key in self.pressed_keys:
            if key in ['Control_L', 'Control_R']:
                modifiers.append('Ctrl')
            elif key in ['Alt_L', 'Alt_R']:
                modifiers.append('Alt')
            elif key in ['Shift_L', 'Shift_R']:
                modifiers.append('Shift')
            elif key in ['Super_L', 'Super_R', 'Win_L', 'Win_R']:
                modifiers.append('Win')
            elif key not in ['Control_L', 'Control_R', 'Alt_L', 'Alt_R', 
                           'Shift_L', 'Shift_R', 'Super_L', 'Super_R', 
                           'Win_L', 'Win_R']:
                regular_keys.append(key)
        
        # Build display string
        display_parts = list(set(modifiers))  # Remove duplicates
        if regular_keys:
            display_parts.extend(regular_keys)
        
        if display_parts:
            display_text = ' + '.join(display_parts)
            self.capture_label.config(text=display_text, fg='green')
            self.recorded_combination = display_text
            self.accept_btn.config(state='normal')
        else:
            self.capture_label.config(text="Press a key...", fg='blue')
            self.accept_btn.config(state='disabled')
    
    def finalize_combination(self):
        """Finalize the key combination when all keys are released."""
        if self.recorded_combination:
            self.accept_shortcut()
    
    def accept_shortcut(self):
        """Accept the recorded shortcut."""
        if self.recorded_combination:
            self.current_shortcut = self.recorded_combination
            self.update_display()
            
            if self.on_changed:
                self.on_changed(self.current_shortcut)
        
        self.cancel_recording()
    
    def cancel_recording(self):
        """Cancel the recording process."""
        if hasattr(self, 'recording_dialog'):
            self.recording_dialog.destroy()
    
    def clear_shortcut(self):
        """Clear the current shortcut."""
        self.current_shortcut = ""
        self.update_display()
        
        if self.on_changed:
            self.on_changed(self.current_shortcut)
    
    def set_value(self, value: str):
        """Set the shortcut value programmatically."""
        self.current_shortcut = value
        self.update_display()
    
    def get_value(self) -> str:
        """Get the current shortcut value."""
        return self.current_shortcut
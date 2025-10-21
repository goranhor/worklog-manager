"""Revoke action dialog for undoing user actions."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Callable, Optional
import logging

from core.action_history import ActionHistory, ActionSnapshot


class RevokeDialog:
    """Dialog for selecting and confirming action revokes."""
    
    def __init__(self, parent, action_history: ActionHistory, 
                 revoke_callback: Callable[[str], bool]):
        """Initialize the revoke dialog.
        
        Args:
            parent: Parent window
            action_history: ActionHistory instance
            revoke_callback: Function to call when revoke is confirmed
        """
        self.parent = parent
        self.action_history = action_history
        self.revoke_callback = revoke_callback
        self.logger = logging.getLogger(__name__)
        
        self.dialog = None
        self.selected_action_id = None
        self.result = False
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the revoke dialog window."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Revoke Action")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Create widgets
        self._create_widgets()
        
        # Load action history
        self._load_actions()
        
        # Handle dialog closing
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _center_dialog(self):
        """Center the dialog over the parent window."""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate dialog position
        dialog_width = 500
        dialog_height = 400
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create and layout dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Select Action to Revoke",
            font=("Arial", 12, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Select a recent action to undo. Note that revoking an action\n"
                 "will restore the system to its previous state.",
            font=("Arial", 9)
        )
        instructions.grid(row=1, column=0, pady=(0, 10), sticky="w")
        
        # Action list frame
        list_frame = ttk.LabelFrame(main_frame, text="Recent Actions", padding="5")
        list_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # Create treeview for actions with hidden ID column
        columns = ("Time", "Action", "Description", "_ActionId")
        self.action_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.action_tree.heading("Time", text="Time")
        self.action_tree.heading("Action", text="Action")
        self.action_tree.heading("Description", text="Description")
        self.action_tree.heading("_ActionId", text="")
        
        self.action_tree.column("Time", width=80, minwidth=60)
        self.action_tree.column("Action", width=100, minwidth=80)
        self.action_tree.column("Description", width=250, minwidth=200)
        self.action_tree.column("_ActionId", width=0, minwidth=0, stretch=False)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.action_tree.yview)
        self.action_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.action_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.action_tree.bind("<<TreeviewSelect>>", self._on_action_select)
        
        # Action details frame
        details_frame = ttk.LabelFrame(main_frame, text="Action Details", padding="5")
        details_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        details_frame.columnconfigure(0, weight=1)
        
        self.details_text = tk.Text(details_frame, height=4, wrap="word", state="disabled")
        self.details_text.grid(row=0, column=0, sticky="ew")
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        
        # Buttons
        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self._load_actions)
        refresh_btn.grid(row=0, column=0, sticky="w")

        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.grid(row=0, column=1, sticky="e")

        self.revoke_btn = ttk.Button(
            right_button_frame,
            text="Revoke Action",
            command=self._on_revoke,
            state="disabled"
        )
        self.revoke_btn.grid(row=0, column=0, padx=(0, 5))

        cancel_btn = ttk.Button(right_button_frame, text="Cancel", command=self._on_cancel)
        cancel_btn.grid(row=0, column=1)
    
    def _load_actions(self):
        """Load actions into the treeview."""
        # Clear existing items
        for item in self.action_tree.get_children():
            self.action_tree.delete(item)
        
        # Get recent actions
        actions = self.action_history.get_history_summary(limit=20)
        
        if not actions:
            # Insert "no actions" message
            self.action_tree.insert("", "end", values=("--", "No Actions", "No recent actions to revoke"))
            return
        
        # Insert actions
        for action in actions:
            # Determine if action can be revoked
            if action['can_revoke'] and not action['revoked']:
                tags = ("revokable",)
            elif action['revoked']:
                tags = ("revoked",)
            else:
                tags = ("not_revokable",)
            
            self.action_tree.insert(
                "",
                "end",
                values=(
                    action['timestamp'],
                    action['action_type'],
                    action['description'],
                    action['id']
                ),
                tags=tags
            )
        
        # Configure tags
        self.action_tree.tag_configure("revokable", foreground="black")
        self.action_tree.tag_configure("revoked", foreground="gray", font=("Arial", 9, "italic"))
        self.action_tree.tag_configure("not_revokable", foreground="gray")
    
    def _on_action_select(self, event):
        """Handle action selection in treeview."""
        selection = self.action_tree.selection()
        if not selection:
            self.selected_action_id = None
            self.revoke_btn.config(state="disabled")
            self._update_details("")
            return
        
        item = selection[0]
        
        # Get action ID from item
        try:
            action_values = self.action_tree.item(item, "values")
            action_id = action_values[3] if len(action_values) > 3 else None
            if not action_id:
                self.selected_action_id = None
                self.revoke_btn.config(state="disabled")
                self._update_details("No action selected")
                return
            
            self.selected_action_id = action_id
            
            # Get action details
            action = self.action_history.get_action_by_id(action_id)
            if action:
                can_revoke = self.action_history.can_revoke_action(action_id)
                self.revoke_btn.config(state="normal" if can_revoke else "disabled")
                self._update_details(self._format_action_details(action, can_revoke))
            else:
                self.selected_action_id = None
                self.revoke_btn.config(state="disabled")
                self._update_details("Action not found")
                
        except tk.TclError:
            self.selected_action_id = None
            self.revoke_btn.config(state="disabled")
            self._update_details("Invalid selection")
    
    def _format_action_details(self, action: ActionSnapshot, can_revoke: bool) -> str:
        """Format action details for display.
        
        Args:
            action: ActionSnapshot to format
            can_revoke: Whether the action can be revoked
            
        Returns:
            Formatted details string
        """
        details = f"Action: {action.action_type.value.replace('_', ' ').title()}\n"
        details += f"Time: {action.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        details += f"State Change: {action.state_before.value} → {action.state_after.value}\n"
        
        if action.break_data and action.break_data.get('break_type'):
            details += f"Break Type: {action.break_data['break_type']}\n"
        
        if action.notes:
            details += f"Notes: {action.notes}\n"
        
        details += f"\nCan Revoke: {'Yes' if can_revoke else 'No'}"
        
        if not can_revoke:
            details += "\n(Only recent actions can be revoked)"
        
        return details
    
    def _update_details(self, text: str):
        """Update the details text widget.
        
        Args:
            text: Text to display
        """
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, text)
        self.details_text.config(state="disabled")
    
    def _on_revoke(self):
        """Handle revoke button click."""
        if not self.selected_action_id:
            messagebox.showwarning("No Selection", "Please select an action to revoke.")
            return
        
        action = self.action_history.get_action_by_id(self.selected_action_id)
        if not action:
            messagebox.showerror("Error", "Selected action not found.")
            return
        
        # Confirm revoke
        action_desc = self._get_action_description(action)
        message = f"Are you sure you want to revoke this action?\n\n"
        message += f"Action: {action_desc}\n"
        message += f"Time: {action.timestamp.strftime('%H:%M:%S')}\n\n"
        message += "This will restore the system to its previous state."
        
        if not messagebox.askyesno("Confirm Revoke", message):
            return
        
        # Perform revoke
        try:
            if self.revoke_callback(self.selected_action_id):
                self.result = True
                messagebox.showinfo("Success", "Action has been successfully revoked.")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to revoke action. Please try again.")
                
        except Exception as e:
            self.logger.error(f"Error during revoke: {e}")
            messagebox.showerror("Error", f"An error occurred while revoking the action:\n{e}")
    
    def _get_action_description(self, action: ActionSnapshot) -> str:
        """Get a description of the action.
        
        Args:
            action: ActionSnapshot to describe
            
        Returns:
            Action description
        """
        return self.action_history._get_action_description(action)
    
    def _on_cancel(self):
        """Handle cancel button or dialog close."""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """Show the dialog and return the result.
        
        Returns:
            True if an action was revoked, False otherwise
        """
        # Wait for dialog to be closed
        self.dialog.wait_window()
        return self.result


def show_revoke_dialog(parent, action_history: ActionHistory, 
                      revoke_callback: Callable[[str], bool]) -> bool:
    """Show the revoke dialog.
    
    Args:
        parent: Parent window
        action_history: ActionHistory instance
        revoke_callback: Function to call when revoke is confirmed
        
    Returns:
        True if an action was revoked, False otherwise
    """
    dialog = RevokeDialog(parent, action_history, revoke_callback)
    return dialog.show()
import json
import os
import csv
from tkinter import *
from tkinter import messagebox, ttk

# File to store inventory data
INVENTORY_FILE = "inventory.json"

# Load inventory from file
def load_inventory():
    if os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "r") as file:
            return json.load(file)
    return {}

# Save inventory to file
def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as file:
        json.dump(inventory, file, indent=4)

# Add a new item to the inventory
def add_item():
    name = entry_name.get().strip()
    quantity = entry_quantity.get().strip()
    price = entry_price.get().strip()
    category = entry_category.get().strip()
    
    if not name or not quantity or not price or not category:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    
    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        messagebox.showwarning("Input Error", "Quantity must be a whole number and price must be a number.")
        return
    
    inventory[name] = {
        "quantity": quantity,
        "price": price,
        "category": category
    }
    save_inventory(inventory)
    messagebox.showinfo("Success", f"Item '{name}' added to inventory.")
    clear_entries()
    list_items()

# Update an existing item
def update_item():
    name = entry_name.get().strip()
    if name in inventory:
        quantity = entry_quantity.get().strip()
        price = entry_price.get().strip()
        category = entry_category.get().strip()
        
        if quantity:
            try:
                inventory[name]["quantity"] = int(quantity)
            except ValueError:
                messagebox.showwarning("Input Error", "Quantity must be a whole number.")
                return
        if price:
            try:
                inventory[name]["price"] = float(price)
            except ValueError:
                messagebox.showwarning("Input Error", "Price must be a number.")
                return
        if category:
            inventory[name]["category"] = category
        
        save_inventory(inventory)
        messagebox.showinfo("Success", f"Item '{name}' updated.")
        clear_entries()
        list_items()
    else:
        messagebox.showwarning("Error", f"Item '{name}' not found.")

# Delete an item from the inventory
def delete_item():
    name = entry_name.get().strip()
    if name in inventory:
        del inventory[name]
        save_inventory(inventory)
        messagebox.showinfo("Success", f"Item '{name}' deleted.")
        clear_entries()
        list_items()
    else:
        messagebox.showwarning("Error", f"Item '{name}' not found.")

# List all items in the inventory
def list_items():
    listbox.delete(*listbox.get_children())
    if not inventory:
        listbox.insert("", "end", values=("Inventory is empty.",))
    else:
        for name, details in inventory.items():
            listbox.insert("", "end", values=(name, details["quantity"], details["price"], details["category"]))

# Search for an item in the inventory
def search_item():
    search_term = entry_search.get().strip().lower()
    listbox.delete(*listbox.get_children())
    if not search_term:
        list_items()
        return
    
    for name, details in inventory.items():
        if search_term in name.lower():
            listbox.insert("", "end", values=(name, details["quantity"], details["price"], details["category"]))

# Check for low stock items
def check_low_stock():
    low_stock_threshold = 10  # Set your threshold here
    low_stock_items = []
    
    for name, details in inventory.items():
        if details["quantity"] < low_stock_threshold:
            low_stock_items.append(name)
    
    if low_stock_items:
        messagebox.showwarning("Low Stock Alert", f"The following items are low in stock: {', '.join(low_stock_items)}")
    else:
        messagebox.showinfo("Low Stock Alert", "No items are low in stock.")

# Export inventory to CSV
def export_to_csv():
    with open("inventory_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Quantity", "Price", "Category"])
        for name, details in inventory.items():
            writer.writerow([name, details["quantity"], details["price"], details["category"]])
    messagebox.showinfo("Export Successful", "Inventory exported to 'inventory_export.csv'.")

# Clear input fields
def clear_entries():
    entry_name.delete(0, END)
    entry_quantity.delete(0, END)
    entry_price.delete(0, END)
    entry_category.delete(0, END)

# Initialize inventory
inventory = load_inventory()

# Create the main window
root = Tk()
root.title("Inventory Management System")

# Use ttk for styling
style = ttk.Style()
style.theme_use("clam")

# Create and place labels and entry fields
Label(root, text="Name:").grid(row=0, column=0, padx=10, pady=5)
entry_name = Entry(root)
entry_name.grid(row=0, column=1, padx=10, pady=5)

Label(root, text="Quantity:").grid(row=1, column=0, padx=10, pady=5)
entry_quantity = Entry(root)
entry_quantity.grid(row=1, column=1, padx=10, pady=5)

Label(root, text="Price:").grid(row=2, column=0, padx=10, pady=5)
entry_price = Entry(root)
entry_price.grid(row=2, column=1, padx=10, pady=5)

Label(root, text="Category:").grid(row=3, column=0, padx=10, pady=5)
entry_category = Entry(root)
entry_category.grid(row=3, column=1, padx=10, pady=5)

# Search functionality
Label(root, text="Search:").grid(row=4, column=0, padx=10, pady=5)
entry_search = Entry(root)
entry_search.grid(row=4, column=1, padx=10, pady=5)
Button(root, text="Search", command=search_item).grid(row=4, column=2, padx=10, pady=5)

# Create and place buttons
Button(root, text="Add Item", command=add_item).grid(row=5, column=0, padx=10, pady=5)
Button(root, text="Update Item", command=update_item).grid(row=5, column=1, padx=10, pady=5)
Button(root, text="Delete Item", command=delete_item).grid(row=6, column=0, padx=10, pady=5)
Button(root, text="List Items", command=list_items).grid(row=6, column=1, padx=10, pady=5)
Button(root, text="Check Low Stock", command=check_low_stock).grid(row=7, column=0, padx=10, pady=5)
Button(root, text="Export to CSV", command=export_to_csv).grid(row=7, column=1, padx=10, pady=5)

# Create a Treeview to display inventory
columns = ("Name", "Quantity", "Price", "Category")
listbox = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    listbox.heading(col, text=col)
listbox.grid(row=8, column=0, columnspan=3, padx=10, pady=5)

# Load and display inventory items on startup
list_items()

# Start the main loop
root.mainloop()
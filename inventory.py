import json
import os
import csv
from tkinter import *
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# File to store inventory data
INVENTORY_FILE = "inventory.json"
# File to store custom units and conversion rates
UNITS_FILE = "units.json"

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

#Add units
def add_unit():
    new_unit = entry_new_unit.get().strip()
    conversion_rate = entry_conversion_rate.get().strip()
    
    if not new_unit or not conversion_rate:
        messagebox.showwarning("Input Error", "Please enter both unit name and conversion rate.")
        return
    
    try:
        conversion_rate = float(conversion_rate)
    except ValueError:
        messagebox.showwarning("Input Error", "Conversion rate must be a number.")
        return
    
    units[new_unit] = conversion_rate
    save_units(units)
    refresh_unit_menu()
    messagebox.showinfo("Success", f"Unit '{new_unit}' added successfully.")
    entry_new_unit.delete(0, END)
    entry_conversion_rate.delete(0, END)

# Load custom units from file
def load_units():
    if os.path.exists(UNITS_FILE):
        with open(UNITS_FILE, "r") as file:
            return json.load(file)
    return {"pieces": 1}  # Default unit with conversion rate 1

#Auto-update Unit Dropdown
def refresh_unit_menu():
    unit_menu['menu'].delete(0, 'end')  # Clear existing options
    for unit in units.keys():
        unit_menu['menu'].add_command(label=unit, command=lambda u=unit: unit_var.set(u))

# Save custom units to file
def save_units(units):
    with open(UNITS_FILE, "w") as file:
        json.dump(units, file, indent=4)

# Add a new item to the inventory
def add_item():
    name = entry_name.get().strip()
    quantity = entry_quantity.get().strip()
    price = entry_price.get().strip()
    category = entry_category.get().strip()
    unit = unit_var.get().strip()
    
    if not name or not quantity or not price or not category or not unit:
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    
    try:
        quantity = float(quantity)
        price = float(price)
    except ValueError:
        messagebox.showwarning("Input Error", "Quantity and price must be numbers.")
        return
    
    inventory[name] = {
        "quantity": quantity,
        "price": price,
        "category": category,
        "unit": unit
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
        unit = unit_var.get().strip()
        
        if quantity:
            try:
                inventory[name]["quantity"] = float(quantity)
            except ValueError:
                messagebox.showwarning("Input Error", "Quantity must be a number.")
                return
        if price:
            try:
                inventory[name]["price"] = float(price)
            except ValueError:
                messagebox.showwarning("Input Error", "Price must be a number.")
                return
        if category:
            inventory[name]["category"] = category
        if unit:
            inventory[name]["unit"] = unit
        
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
            listbox.insert("", "end", values=(name, details["quantity"], details["price"], details["category"], details["unit"]))

# Search for an item in the inventory
def search_item():
    search_term = entry_search.get().strip().lower()
    listbox.delete(*listbox.get_children())
    if not search_term:
        list_items()
        return
    
    for name, details in inventory.items():
        if search_term in name.lower():
            listbox.insert("", "end", values=(name, details["quantity"], details["price"], details["category"], details["unit"]))

# Check for low stock items
def check_low_stock():
    low_stock_threshold = 10  # Set your threshold here
    low_stock_items = []
    
    for name, details in inventory.items():
        if details["quantity"] < low_stock_threshold:
            low_stock_items.append(f"{name} ({details['quantity']} {details['unit']})")
    
    if low_stock_items:
        messagebox.showwarning("Low Stock Alert", f"The following items are low in stock: {', '.join(low_stock_items)}")
    else:
        messagebox.showinfo("Low Stock Alert", "No items are low in stock.")

# Export inventory to CSV
def export_to_csv():
    with open("inventory_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Quantity", "Price", "Category", "Unit"])
        for name, details in inventory.items():
            writer.writerow([name, details["quantity"], details["price"], details["category"], details["unit"]])
    messagebox.showinfo("Export Successful", "Inventory exported to 'inventory_export.csv'.")

# Edit item directly in the Treeview
def edit_item(event):
    selected_item = listbox.selection()
    if not selected_item:
        return
    
    item = listbox.item(selected_item)
    name = item["values"][0]
    
    entry_name.delete(0, END)
    entry_name.insert(0, name)
    entry_quantity.delete(0, END)
    entry_quantity.insert(0, inventory[name]["quantity"])
    entry_price.delete(0, END)
    entry_price.insert(0, inventory[name]["price"])
    entry_category.delete(0, END)
    entry_category.insert(0, inventory[name]["category"])
    unit_var.set(inventory[name]["unit"])

# Sort items by column
def sort_treeview(col, reverse):
    items = [(listbox.set(child, col), child) for child in listbox.get_children("")]
    items.sort(reverse=reverse)
    
    for index, (val, child) in enumerate(items):
        listbox.move(child, "", index)
    
    listbox.heading(col, command=lambda: sort_treeview(col, not reverse))

# Generate graphical reports
def generate_report():
    names = list(inventory.keys())
    quantities = [details["quantity"] for details in inventory.values()]
    units = [details["unit"] for details in inventory.values()]
    
    fig, ax = plt.subplots()
    ax.bar(names, quantities)
    ax.set_xlabel("Items")
    ax.set_ylabel("Quantity")
    ax.set_title("Inventory Stock Levels")
    
    # Add unit labels to the bars
    for i, (name, unit) in enumerate(zip(names, units)):
        ax.text(i, quantities[i], f"{quantities[i]} {unit}", ha="center", va="bottom")
    
    # Embed the plot in the Tkinter window
    report_window = Toplevel(root)
    report_window.title("Inventory Report")
    canvas = FigureCanvasTkAgg(fig, master=report_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Clear input fields
def clear_entries():
    entry_name.delete(0, END)
    entry_quantity.delete(0, END)
    entry_price.delete(0, END)
    entry_category.delete(0, END)
    unit_var.set("pieces")  # Reset unit to default

# Initialize inventory and units
inventory = load_inventory()
units = load_units()

# Create the main window
root = Tk()
root.title("Inventory Management System")

#load units on startup
units = load_units()
unit_options = list(units.keys())
unit_var = StringVar(value=unit_options[0])  # Set default unit
unit_menu = OptionMenu(root, unit_var, *unit_options)
unit_menu.grid(row=4, column=1, padx=10, pady=5)

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

Label(root, text="Unit:").grid(row=4, column=0, padx=10, pady=5)
unit_var = StringVar(value="pieces")  # Default unit
unit_options = list(units.keys())
unit_menu = OptionMenu(root, unit_var, *unit_options)
unit_menu.grid(row=4, column=1, padx=10, pady=5)

Label(root, text="New Unit:").grid(row=6, column=0, padx=10, pady=5)
entry_new_unit = Entry(root)
entry_new_unit.grid(row=6, column=1, padx=10, pady=5)

Label(root, text="Conversion Rate:").grid(row=7, column=0, padx=10, pady=5)
entry_conversion_rate = Entry(root)
entry_conversion_rate.grid(row=7, column=1, padx=10, pady=5)

Button(root, text="Add Unit", command=add_unit).grid(row=7, column=2, padx=10, pady=5)

# Search functionality
Label(root, text="Search:").grid(row=5, column=0, padx=10, pady=5)
entry_search = Entry(root)
entry_search.grid(row=5, column=1, padx=10, pady=5)
Button(root, text="Search", command=search_item).grid(row=5, column=2, padx=10, pady=5)

# Create and place buttons
Button(root, text="Add Item", command=add_item).grid(row=6, column=0, padx=10, pady=5)
Button(root, text="Update Item", command=update_item).grid(row=6, column=1, padx=10, pady=5)
Button(root, text="Delete Item", command=delete_item).grid(row=7, column=0, padx=10, pady=5)
Button(root, text="List Items", command=list_items).grid(row=7, column=1, padx=10, pady=5)
Button(root, text="Check Low Stock", command=check_low_stock).grid(row=8, column=0, padx=10, pady=5)
Button(root, text="Export to CSV", command=export_to_csv).grid(row=8, column=1, padx=10, pady=5)
Button(root, text="Generate Report", command=generate_report).grid(row=9, column=0, padx=10, pady=5)

# Create a Treeview to display inventory
columns = ("Name", "Quantity", "Price", "Category", "Unit")
listbox = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    listbox.heading(col, text=col, command=lambda c=col: sort_treeview(c, False))
listbox.grid(row=10, column=0, columnspan=3, padx=10, pady=5)

# Bind double-click to edit item
listbox.bind("<Double-1>", edit_item)

# Load and display inventory items on startup
list_items()

# Start the main loop
root.mainloop()
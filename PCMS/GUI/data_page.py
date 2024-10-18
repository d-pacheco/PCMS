import customtkinter as ctk


class DataEntryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Table headers
        self.headers = ["Item ID", "Address", "Quantity"]

        # Create a canvas for scrolling
        self.canvas = ctk.CTkCanvas(self, height=400)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar linked to the canvas
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas for the table
        self.table_frame = ctk.CTkFrame(self.canvas)

        # Create a window in the canvas for the table frame
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

        # Bind the frame to the canvas for scrolling
        self.table_frame.bind("<Configure>", self.on_frame_configure)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Fill the table frame with the necessary entries
        self.entries = []
        self.populate_table()

        # Add button to create a new row
        self.add_row_button = ctk.CTkButton(self, text="Add New Row", command=self.add_new_row)
        self.add_row_button.pack(pady=10)

        # Button to save the data
        self.save_button = ctk.CTkButton(self, text="Save Data", command=self.save_data)
        self.save_button.pack(pady=10)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def populate_table(self):
        # Load data from a file (replace 'data.csv' with your file path)
        try:
            data = []  # Placeholder for data loading logic
            for index, row in data:
                self.add_row(row['Item ID'], row['Address'], row['Quantity'])
        except Exception as e:
            print(f"Error loading data: {e}")

    def add_row(self, item_id="", address="", quantity=""):
        row_frame = ctk.CTkFrame(self.table_frame)
        row_frame.pack(fill="x")

        item_id_entry = ctk.CTkEntry(row_frame, width=50)
        item_id_entry.insert(0, item_id)
        item_id_entry.pack(side="left", padx=5)

        address_entry = ctk.CTkEntry(row_frame, width=250)
        address_entry.insert(0, address)
        address_entry.pack(side="left", padx=5)

        quantity_entry = ctk.CTkEntry(row_frame, width=50)
        quantity_entry.insert(0, quantity)
        quantity_entry.pack(side="left", padx=5)

        self.entries.append((item_id_entry, address_entry, quantity_entry))

    def add_new_row(self):
        self.add_row()  # Add an empty row

    def save_data(self):
        data_to_save = []
        for item_id_entry, address_entry, quantity_entry in self.entries:
            item_id = item_id_entry.get()
            address = address_entry.get()
            quantity = quantity_entry.get()
            data_to_save.append((item_id, address, quantity))

        # Convert to DataFrame and save to a file (replace 'output.csv' with your desired file)
        print("Data saved successfully!")

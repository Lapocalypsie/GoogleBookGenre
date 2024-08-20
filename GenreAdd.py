import tkinter as tk
from tkinter import filedialog
import csv
import requests
import time
import logging

# Set up logging
logging.basicConfig(filename='process_log.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_category(isbn):
    """Fetch the category from Google Books API using the provided ISBN."""
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        # Check if API response contains data
        if "items" in data and data["items"]:
            # Extract category from API response
            category = data["items"][0]["volumeInfo"].get("categories", ["Unknown"])[0]
            return category
        return "No Category Found"
    
    except requests.RequestException as e:
        logging.error(f"Error fetching category for ISBN {isbn}: {e}")
        return None

def process_csv(input_file, output_file, start_row, end_row):
    """Process the CSV file, fetch categories for each ISBN, and save to output file."""
    logging.info(f"Starting CSV processing. Input: {input_file}, Output: {output_file}, Start Row: {start_row}, End Row: {end_row}")
    
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            rows = list(reader)
            
            # Check if the end_row is beyond the length of rows
            if end_row > len(rows):
                end_row = len(rows)
                logging.warning(f"End row adjusted to the end of the file: {end_row}")

            with open(output_file, "w", newline="", encoding="utf-8") as outfile:
                writer = csv.writer(outfile)
                
                counter = 0  # Counter to keep track of rows processed
                
                for i, row in enumerate(rows):
                    if i < start_row or i >= end_row:
                        writer.writerow(row)
                        continue
                    
                    isbn = row[0]  # Assuming ISBN is in the first column
                    retry_counter = 0  # Retry counter reset for each ISBN
                    
                    # Retry mechanism with spaced repetition
                    while retry_counter < 3:
                        category = fetch_category(isbn)
                        
                        if category is not None:
                            row.append(category)
                            writer.writerow(row)
                            counter += 1
                            # Save data every 100 rows
                            if counter % 100 == 0:
                                logging.info(f"Processed row {i + 1}: ISBN {isbn}, Category {category}")
                                outfile.flush()  # Flush the buffer to save the data
                            
                            # Save data every 100 rows
                            if counter % 100 == 0:
                                logging.info(f"Processed {counter} rows.")
                                outfile.flush()  # Flush the buffer to save the data
                            break  # Exit the retry loop if successful
                        
                        retry_counter += 1
                        logging.warning(f"Retry {retry_counter} for ISBN {isbn}")
                        time.sleep(1)  # Wait for 1 second before retrying
                    
                    if retry_counter == 3:
                        logging.error(f"Failed to fetch category for ISBN {isbn} after 3 attempts.")
                
        logging.info(f"CSV processing completed. Total rows processed: {counter}")
    
    except Exception as e:
        logging.critical(f"Critical error during CSV processing: {e}")

# Create Tkinter window
root = tk.Tk()
root.withdraw()

# Ask for CSV file to load
input_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

# Create new CSV file named "genre.csv"
output_file_path = "genre.csv"

# Ask for starting and ending rows
start_row = int(input("Enter the row number to start from: "))
end_row = int(input("Enter the row number to end at: "))

# Process the CSV file
process_csv(input_file_path, output_file_path, start_row, end_row)

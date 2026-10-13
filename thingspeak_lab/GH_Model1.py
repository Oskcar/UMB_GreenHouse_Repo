
#Read the CSV file and print it [Version 1]
import csv  #Loads the CSV module

with open("nodes.csv", newline="", encoding="utf-8-sig") as f:  #opens/closes the CSV file when block ends (newline = "" to avoid blank lines, encoding = "utf-8-sig" to avoid BOM issues)  
    reader = csv.DictReader(f) #csv.DictReader uses the header row to create a dictionary for each subsequent row, with the header values as keys and the row values as values
    for row in reader:  #Repeats indented code once per row
        print(row)  
#End of code V1
#Key idea: a dictionary is a set of name:value pairs, where the name is the header value and the value is the row value.  The dictionary is created for each row in the CSV file, and the keys are the header values.  The values are the row values.  The dictionary is printed for each row in the CSV file.

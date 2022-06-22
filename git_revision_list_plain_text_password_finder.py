#!/usr/bin/python

import argparse, os, sys, re, csv
from os.path import expanduser
from datetime import datetime

parser = argparse.ArgumentParser(

    description="Searches git repository revision list for potential plain text passwords.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(

    "--temp-file-path",
    default = "/tmp/cmd_output.txt",
    type = str,
    help = "Path to temporary file that stores search output."
)
parser.add_argument(

    "--output-directory-path",
    default = expanduser("~"),
    type = str,
    help = "Path of output directory."
)
parser.add_argument(

    "--git-repo-path",
    default = "/u01/software/ansible",
    type = str,
    help = "Path to git repository directory."
)
parser.add_argument(

    "--search-words",
    default = ["password", "pwd"],
    type = list,
    help = "Words to search for."
)
config = vars(parser.parse_args())

# Preparation #

print("\nStart time: %s" % datetime.now().strftime("%d/%m/%Y, %H:%M")) 
print("\nPreparing to run")

# Variables
temp_file_path = config["temp_file_path"]
output_dir_path = config["output_directory_path"]
git_repo_dir_path = config["git_repo_path"]

csv_file_path = "%s/git_plain_text_password_report_%s.csv" % (

    output_dir_path,
    datetime.now().strftime("%y%m%d%H%M")
)

# Words to search for
words = ["password", "pwd"]

# List of CSV rows
rows = []

# List of errors
errors = []

# Change to git directory
os.chdir(git_repo_dir_path)

# Get Data #

for word in words:

    # Search git revisions for word
    # Output results to temporary file
    
    print("\nSearching git revision list for: %s" % word)
    
    cmd_to_run = "git rev-list --all | xargs git grep %s > %s" % (word, temp_file_path)
    cmd_output = os.system(cmd_to_run)
    
    # Get content of output file

    print("Getting content from output file: %s" % temp_file_path)
    
    output_txt_file = open(temp_file_path)
    output_txt_file_content = output_txt_file.read()
    output_txt_file.close()
    output_txt_file_content = output_txt_file_content.splitlines()
    
    # Progress bar - total lines to process
    number_of_lines_to_process = len(output_txt_file_content)
    
    print("Number of lines to process: %s" % number_of_lines_to_process)
    
    # Parse lines
    # Add formatted data to rows list
    
    # Progress bar - get centi unit
    i = 0
    centi = number_of_lines_to_process / 100

    for line in output_txt_file_content:
        
        # Progress bar - display
        if i == 0: sys.stdout.write("|")
        elif i % centi == 0 : sys.stdout.write("=")
        sys.stdout.flush()
        i += 1
        
        # Skip binary file matches
        if re.search("^Binary file ", line): continue
        
        # Split line into components
        # Compose CSV rows
        # Log errors
        
        try:
        
            line_split = line.split(":", 2)
            
            row = [
                word,
                line_split[0],
                line_split[1],
                line_split[1].split("/")[-1],
                "/".join(line_split[1].split("/")[0:1]),
                line_split[2]
            ]
        
        except IndexError:
        
            errors.append("Indexing error on line: %s" % line)
        
        rows.append(row)
    
    # Progress bar - complete display
    sys.stdout.write("| 100 percent")
    sys.stdout.flush()
    print("")

# CSV Creation #

print("\nCreating CSV file: %s" % csv_file_path)

# Header information
header = [
    "search_word",
    "commit_id",
    "file_path",
    "file_name",
    "directory_path",
    "value"
]

# Create CSV file

with open(csv_file_path, "w") as csv_file:

    writer = csv.writer(csv_file)
    writer.writerow(header)
    writer.writerows(rows)
    
# Error Presentation #

if len(errors) > 0:

    print("\nErrors Detected: %s" % len(errors))
    print("-" * 115)

    for line in errors: print(line)
else:

    print("\nErrors detected: 0")

# Closing #

print("\nFinish time: %s" % datetime.now().strftime("%d/%m/%Y, %H:%M")) 
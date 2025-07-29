# Document Intelligence System

## What is this?

This is a smart system that reads PDF documents and finds the most important parts based on who is using it and what they need to do. It can handle different types of users like travel planners, HR professionals, and food contractors.

## What it does

- Reads PDF files and finds important sections
- Understands different user types and their needs
- Ranks content by how useful it is for each user
- Works with multiple document collections
- Creates organized output files

## Project Structure

```
Adobe-Hackathon-round1b/
├── Collection 1/                    # Travel documents
│   ├── PDFs/                       # Travel guide PDFs
│   ├── challenge1b_input.json      # Configuration file
│   └── challenge1b_output.json     # Results file
├── Collection 2/                    # Adobe Acrobat documents
│   ├── PDFs/                       # Tutorial PDFs
│   ├── challenge1b_input.json      # Configuration file
│   └── challenge1b_output.json     # Results file
├── Collection 3/                    # Recipe documents
│   ├── PDFs/                       # Cooking PDFs
│   ├── challenge1b_input.json      # Configuration file
│   └── challenge1b_output.json     # Results file
├── src/                            # Main code files
│   ├── analyzer.py        # PDF reading code
│   ├── processor.py        # User type analysis
│   └── ranker.py           # Content ranking
├── utils/                          # Helper tools
│   └── parser.py                   # PDF text extraction
├── process.py                      # Main program
├── main.py                         # Simple version
├── requirements.txt                # Python packages needed
├── Dockerfile                      # Docker setup
└── README.md                       # This file
```

## How to set up on a new computer

### Step 1: Install Python
Make sure you have Python 3.8 or higher installed on your computer.

### Step 2: Download the project
Download or copy all the project files to your computer.

### Step 3: Open command prompt or terminal
Navigate to the project folder using the command line.

### Step 4: Install required packages
Run this command to install all needed Python packages:
```bash
pip install -r requirements.txt
```

### Step 5: Run the program
Use this command to start the document analysis:
```bash
python process.py
```

## How to use Docker

### Step 1: Install Docker
Download and install Docker Desktop from the official website.

### Step 2: Open command prompt or terminal
Navigate to the project folder.

### Step 3: Build the Docker image
Run this command to create a Docker container:
```bash
docker build -t document-processor .
```

### Step 4: Run the container
Use this command to run the program in Docker:
```bash
docker run -v %cd%:/app document-processor
```

Note: On Mac or Linux, use `$(pwd)` instead of `%cd%`.

## What happens when you run it

1. The program reads all three collections of documents
2. It analyzes each PDF file to find important sections
3. It matches content to the user type and task
4. It creates output files with the most relevant information
5. You will see progress messages in the terminal

## Output files

After running the program, you will find these files:
- `Collection 1/challenge1b_output.json` - Travel planning results
- `Collection 2/challenge1b_output.json` - HR document results  
- `Collection 3/challenge1b_output.json` - Food menu results

## Testing the system

To run tests to make sure everything works:
```bash
python test_solution.py
```

To check if the output format is correct:
```bash
python validate_schema.py
```

## Troubleshooting

If you get errors:

1. Make sure Python 3.8+ is installed
2. Check that all required packages are installed
3. Verify all PDF files are in the correct folders
4. Make sure you have read permissions for all files

## System requirements

- Python 3.8 or higher
- At least 500MB of free memory
- Standard computer processor (no special graphics card needed)
- About 2-5 seconds processing time per document collection

## Support

If you have problems:
1. Check that all files are in the right places
2. Make sure Python and all packages are installed correctly
3. Try running the test files first
4. Check the error messages for specific issues
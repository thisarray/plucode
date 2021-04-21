#!/bin/bash
# Package the code in a zip archive for Google Cloud Function deployment.

echo -e "main.py\nrequirements.txt\nlib/__init__.py\nlib/plucode.py\n" | zip -@ "plufn$(date +%Y%m%d)"

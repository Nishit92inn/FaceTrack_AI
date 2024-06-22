import os

def print_directory_structure(startpath, depth=0):
    output = []
    for root, dirs, files in os.walk(startpath):
        # Ignore specified directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv_FaceTrackAI', '.git', 'Raw_dataSet']]
        # Ignore directories and files with 'Bootstrap' in their names
        dirs[:] = [d for d in dirs if 'Bootstrap' not in d]

        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        output.append('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if f not in ['.DS_Store'] and 'Bootstrap' not in f:
                output.append('{}{}'.format(subindent, f))
        if depth and level >= depth - 1:
            del dirs[:]
    
    return output

if __name__ == "__main__":
    startpath = '.'  # Change this to your project directory if running outside the project folder
    structure = print_directory_structure(startpath)
    with open("directory_structure.txt", "w") as f:
        for line in structure:
            f.write(line + "\n")
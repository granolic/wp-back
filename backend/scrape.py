import os


def collect_django_project_files():
    # Set your project root directory
    base_dir = os.getcwd()  # Assumes this script is placed in the project root
    output_file = 'django_project_files.txt'
    excluded_dirs = {'.venv', '__pycache__', 'migrations', 'static', 'node_modules'}
    included_formats = {'.py', '.html', '.js'}

    with open(output_file, 'w') as result_file:
        for root, dirs, files in os.walk(base_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            for file in files:
                # Only include files with the specified formats
                if any(file.endswith(ext) for ext in included_formats):
                    print(file)
                    file_path = os.path.join(root, file)
                    result_file.write(f'File: {file_path}\n')
                    result_file.write('-' * 40 + '\n')
                    with open(file_path, 'r') as f:
                        result_file.write(f.read())
                    result_file.write('\n' + '=' * 80 + '\n\n')

    print(f'All relevant files have been collected in {output_file}')


# Run the function
collect_django_project_files()

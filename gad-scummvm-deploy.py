import os
import sys
import subprocess
import re
import csv

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

def get_matches(target, items, is_file=False):
    normalized_target = normalize(target)
    matches = []
    for item in items:
        name = item
        if is_file:
            name = os.path.splitext(item)[0]
        if normalized_target in normalize(name) or normalize(name) in normalized_target:
            matches.append(item)
    return matches

def select_from_list(matches, item_type):
    print(f'\nMultiple {item_type} matches found:')
    for i, match in enumerate(matches, 1):
        print(f'{i}. {match}')
    print(f'{len(matches) + 1}. Exit')
    
    choice = input(f'\nSelect a {item_type} (1-{len(matches) + 1}): ')
    try:
        idx = int(choice) - 1
        if idx == len(matches):
            print('Exiting.')
            sys.exit(0)
        if 0 <= idx < len(matches):
            return matches[idx]
    except (ValueError, IndexError):
        pass
    print('Invalid selection. Exiting.')
    sys.exit(1)

def check_archive_contents(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    cmd = []
    if ext == '.zip':
        cmd = ['unzip', '-Z', '-1', file_path]
    elif ext == '.rar':
        cmd = ['unrar', 'lb', file_path]
    elif ext == '.7z':
        cmd = ['7z', 'l', '-ba', '-slt', file_path]
    else:
        return None, None

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        
        if ext == '.7z':
            files = [line.split('= ')[1] for line in lines if line.startswith('Path = ') and not line.endswith('/')]
            if files and files[0] == file_path:
                files = files[1:]
        else:
            files = [l.strip() for l in lines if l.strip() and not l.endswith('/')]

        if not files:
            return None, None

        parts = [f.split('/') for f in files]
        first_dir = parts[0][0] if len(parts[0]) > 1 else None
        
        if first_dir and all(len(p) > 1 and p[0] == first_dir for p in parts):
            return first_dir, ext
        return '', ext
    except Exception as e:
        print(f'Error inspecting archive: {e}')
        return None, None

def main():
    if len(sys.argv) < 2:
        print('Usage: gad-scummvm-deploy <Game Title> [Manual Name]')
        sys.exit(1)

    game_title = sys.argv[1]
    manual_name = sys.argv[2] if len(sys.argv) > 2 else game_title
    csv_file = 'GAD_RetroBat_ScummVM_Tag_List.csv'
    
    print(f'--- Deploying: {game_title} ---')

    # 1. Sanity Check (Directories)
    all_items = os.listdir('.')
    dirs = [d for d in all_items if os.path.isdir(d)]
    dir_matches = get_matches(game_title, dirs)
    if dir_matches:
        print(f'Abort: Found existing matching directory(s): {dir_matches}')
        sys.exit(1)

    # 2. Locate Game Files
    files = [f for f in all_items if os.path.isfile(f) and f.lower().endswith(('.zip', '.rar', '.7z'))]
    file_matches = get_matches(game_title, files, is_file=True)
    
    if not file_matches:
        print(f'Abort: No matching game files found for "{game_title}"')
        sys.exit(1)
    
    selected_file = file_matches[0] if len(file_matches) == 1 else select_from_list(file_matches, 'file')

    # 3. Validate Game Contents
    root_dir, ext = check_archive_contents(selected_file)
    if root_dir is None:
        print('Abort: Could not inspect archive contents.')
        sys.exit(1)

    # 4. Create ScummVM File Tag Lookup
    if not os.path.exists(csv_file):
        print(f'Abort: {csv_file} not found.')
        sys.exit(1)

    tag_matches = []
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                name, tag = row[0], row[1]
                if normalize(game_title) in normalize(name) or normalize(name) in normalize(game_title):
                    tag_matches.append((name, tag))

    if not tag_matches:
        print(f'Abort: No matching tag found in {csv_file} for "{game_title}"')
        sys.exit(1)
    
    selected_tag = ""
    if len(tag_matches) == 1:
        selected_tag = tag_matches[0][1]
    else:
        choice_text = select_from_list([f'{n} -> {t}' for n, t in tag_matches], 'tag')
        name_part = choice_text.split(' -> ')[0]
        selected_tag = next(t for n, t in tag_matches if n == name_part)

    # 5. Plan Final Validation
    new_dir = game_title
    scummvm_file = f'{new_dir}/{manual_name}.scummvm'
    
    actions = []
    actions.append(f'CREATE DIRECTORY: {new_dir}')
    
    if root_dir:
        actions.append(f'EXTRACT (FLATTEN ROOT "{root_dir}"): {selected_file} -> {new_dir}')
    else:
        actions.append(f'EXTRACT: {selected_file} -> {new_dir}')

    actions.append(f'CREATE FILE: {scummvm_file} (Content: "{selected_tag}")')

    print('\n--- Planned Actions ---')
    for action in actions:
        print(f'- {action}')
    
    confirm = input('\nProceed with deployment? [Y/n]: ').lower()
    if confirm != '' and confirm != 'y':
        print('Deployment aborted.')
        sys.exit(0)

    # 6. Execution
    print('\nExecuting...')
    os.makedirs(new_dir, exist_ok=True)
    
    if ext == '.zip':
        if root_dir:
            subprocess.run(f'unzip -q "{selected_file}" "{root_dir}/*" -d "{new_dir}" && mv "{new_dir}/{root_dir}"/* "{new_dir}/" && rmdir "{new_dir}/{root_dir}"', shell=True)
        else:
            subprocess.run(['unzip', '-q', selected_file, '-d', new_dir])
    elif ext == '.rar':
        if root_dir:
            subprocess.run(f'unrar x -idq "{selected_file}" "{new_dir}/" && mv "{new_dir}/{root_dir}"/* "{new_dir}/" && rmdir "{new_dir}/{root_dir}"', shell=True)
        else:
            subprocess.run(['unrar', 'x', '-idq', selected_file, new_dir + '/'])
    elif ext == '.7z':
        if root_dir:
            subprocess.run(f'7z x -bd -y "{selected_file}" -o"{new_dir}/" && mv "{new_dir}/{root_dir}"/* "{new_dir}/" && rmdir "{new_dir}/{root_dir}"', shell=True)
        else:
            subprocess.run(['7z', 'x', '-bd', '-y', selected_file, f'-o{new_dir}'])

    with open(scummvm_file, 'w') as f:
        f.write(selected_tag)

    print('\n--- Deployment Complete ---')
    print(f'New directory created: {new_dir}')

if __name__ == '__main__':
    main()

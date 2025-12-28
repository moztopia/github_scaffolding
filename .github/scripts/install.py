#!/usr/bin/env python3
import argparse
import os
import shutil
import sys

def main():
    parser = argparse.ArgumentParser(description='Install GitHub scaffolding to a target repository.')
    parser.add_argument('target', help='Target repository path (e.g., ../my-repo or /full/path/to/repo)')
    args = parser.parse_args()

    # Resolve paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_root = os.path.abspath(os.path.join(script_dir, '..', '..')) # scaffolding root
    
    target_path = os.path.abspath(args.target)

    if not os.path.isdir(target_path):
        print(f"Error: Target directory '{target_path}' does not exist.")
        sys.exit(1)

    # Check for existing installation
    target_version_file = os.path.join(target_path, 'VERSION')
    target_github_dir = os.path.join(target_path, '.github')
    
    is_initialized = os.path.exists(target_version_file) or os.path.exists(target_github_dir)
    force_reset = False

    print(f"Target: {target_path}")
    print("Planned Actions:")
    
    if is_initialized:
        print("  [!] Target is already initialized.")
        print("  [!] RESET VERSION to 0.0.0")
        print("  [!] OVERWRITE .github directory (workflow and scripts)")
        print("  [!] RESET configuration files from samples (main_release_names.json, etc.)")
        
        print("\nWARNING: This will destroy existing release configuration and version history in the target.")
        response = input("Do you want to proceed with this destructive overwrite? [y/N] ").strip().lower()
        if response == 'y':
            force_reset = True
        else:
            print("Aborted.")
            sys.exit(0)
    else:
        print("  [+] Create VERSION file (0.0.0)")
        print("  [+] Copy .github directory")
        print("  [+] Initialize configuration files from samples")
        
        # Optional: confirm even for fresh install? 
        # Usually fresh install is safe, but explicit is good.
        response = input("\nProceed with installation? [Y/n] ").strip().lower()
        if response == 'n':
            print("Aborted.")
            sys.exit(0)

    print("\nExecuting...")

    # 1. Handle VERSION
    source_version = os.path.join(source_root, 'VERSION')
    
    if force_reset or not os.path.exists(target_version_file):
        with open(target_version_file, 'w') as f:
            f.write("0.0.0")
        action = "RESET" if force_reset else "CREATED"
        print(f"  [{action}] VERSION file set to 0.0.0")

    # 2. Copy .github folder
    source_github = os.path.join(source_root, '.github')
    
    # Exclude __pycache__ and compiled python
    ignore_patterns = shutil.ignore_patterns('__pycache__', '*.pyc')
    
    try:
        shutil.copytree(source_github, target_github_dir, dirs_exist_ok=True, ignore=ignore_patterns)
        print(f"  [COPY] .github directory updated.")
    except Exception as e:
        print(f"Error copying .github directory: {e}")
        sys.exit(1)

    # 3. Handle .sample files
    for root, dirs, files in os.walk(target_github_dir):
        for file in files:
            if file.endswith('.sample'):
                sample_path = os.path.join(root, file)
                real_filename = file[:-7] # remove .sample
                real_path = os.path.join(root, real_filename)
                
                if force_reset or not os.path.exists(real_path):
                    shutil.copy(sample_path, real_path)
                    action = "RESET" if (force_reset and os.path.exists(real_path)) else "INIT"
                    print(f"  [{action}] Configured {real_filename} from sample.")
                else:
                    print(f"  [SKIP] {real_filename} already exists.")

    print("\nSuccess.")

if __name__ == '__main__':
    main()

import requests
import os
import sys
import shutil
import tempfile
from zipfile import ZipFile
from packaging import version

class Updater:
    def __init__(self):
        self.github_repo = "yourusername/TARDIS"  # Replace with your repo
        self.current_version = "1.1.0"  # Match your CHANGELOG.md version
        self.github_api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
        self.exe_name = "tardis.exe"

    def check_for_updates(self):
        """Check if a new version is available"""
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            return version.parse(latest_version) > version.parse(self.current_version)
        except Exception:
            return False

    def download_and_install_update(self):
        """Download and install the latest version"""
        try:
            # Get latest release info
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            latest_release = response.json()
            
            # Download the new version
            download_url = latest_release['assets'][0]['browser_download_url']
            update_file = requests.get(download_url)
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "update.zip")
                
                # Save the downloaded file
                with open(zip_path, 'wb') as f:
                    f.write(update_file.content)
                
                # Extract update
                with ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Get the path to the current executable
                if getattr(sys, 'frozen', False):
                    current_exe = sys.executable
                else:
                    current_exe = os.path.join(os.path.dirname(__file__), self.exe_name)
                
                # Create batch file for update
                batch_file = os.path.join(temp_dir, "update.bat")
                with open(batch_file, 'w') as f:
                    f.write('@echo off\n')
                    f.write('timeout /t 1 /nobreak >nul\n')  # Wait for original process to end
                    f.write(f'copy /Y "{os.path.join(temp_dir, self.exe_name)}" "{current_exe}"\n')
                    f.write(f'start "" "{current_exe}"\n')
                    f.write('del "%~f0"\n')  # Delete the batch file
                
                # Execute the update batch file
                os.startfile(batch_file)
                return True
                
        except Exception as e:
            print(f"Update failed: {str(e)}")
            return False

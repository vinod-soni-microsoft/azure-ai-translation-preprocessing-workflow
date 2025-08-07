#!/usr/bin/env python3
"""
Azure Deployment Helper for Document Processing Service
This script helps deploy the service to Azure with proper configuration
"""

import os
import subprocess
import json
import sys
from pathlib import Path

class AzureDeploymentHelper:
    """Helper class for Azure deployment."""
    
    def __init__(self):
        self.resource_group = "document-processing-rg"
        self.app_name = "document-processing-app"
        self.location = "eastus"
        self.app_service_plan = "document-processing-plan"
        self.storage_account = "docprocessingstorage"
    
    def check_azure_cli(self):
        """Check if Azure CLI is installed and user is logged in."""
        print("🔍 Checking Azure CLI...")
        
        try:
            # Check if Azure CLI is installed
            result = subprocess.run(["az", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Azure CLI is not installed")
                print("   Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
                return False
            
            print("✅ Azure CLI is installed")
            
            # Check if user is logged in
            result = subprocess.run(["az", "account", "show"], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Not logged in to Azure")
                print("   Run: az login")
                return False
            
            account_info = json.loads(result.stdout)
            print(f"✅ Logged in as: {account_info['user']['name']}")
            print(f"   Subscription: {account_info['name']}")
            return True
            
        except FileNotFoundError:
            print("❌ Azure CLI is not installed")
            return False
        except Exception as e:
            print(f"❌ Error checking Azure CLI: {e}")
            return False
    
    def get_user_input(self):
        """Get deployment configuration from user."""
        print("\n⚙️ Deployment Configuration")
        print("-" * 30)
        
        # Resource Group
        rg = input(f"Resource Group [{self.resource_group}]: ").strip()
        if rg:
            self.resource_group = rg
        
        # App Name
        app = input(f"App Name [{self.app_name}]: ").strip()
        if app:
            self.app_name = app
        
        # Location
        loc = input(f"Location [{self.location}]: ").strip()
        if loc:
            self.location = loc
        
        # Storage Account Name
        storage = input(f"Storage Account Name [{self.storage_account}]: ").strip()
        if storage:
            self.storage_account = storage
        
        print(f"\n📋 Deployment Configuration:")
        print(f"   Resource Group: {self.resource_group}")
        print(f"   App Name: {self.app_name}")
        print(f"   Location: {self.location}")
        print(f"   Storage Account: {self.storage_account}")
        
        confirm = input("\nProceed with deployment? (y/N): ").strip().lower()
        return confirm in ['y', 'yes']
    
    def create_resource_group(self):
        """Create Azure resource group."""
        print(f"\n🏗️ Creating resource group: {self.resource_group}")
        
        cmd = [
            "az", "group", "create",
            "--name", self.resource_group,
            "--location", self.location
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Resource group created successfully")
            return True
        else:
            print(f"❌ Failed to create resource group: {result.stderr}")
            return False
    
    def create_app_service_plan(self):
        """Create App Service Plan."""
        print(f"\n📋 Creating App Service Plan: {self.app_service_plan}")
        
        cmd = [
            "az", "appservice", "plan", "create",
            "--name", self.app_service_plan,
            "--resource-group", self.resource_group,
            "--is-linux",
            "--sku", "B1"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ App Service Plan created successfully")
            return True
        else:
            print(f"❌ Failed to create App Service Plan: {result.stderr}")
            return False
    
    def create_web_app(self):
        """Create Web App."""
        print(f"\n🌐 Creating Web App: {self.app_name}")
        
        cmd = [
            "az", "webapp", "create",
            "--resource-group", self.resource_group,
            "--plan", self.app_service_plan,
            "--name", self.app_name,
            "--runtime", "PYTHON|3.12"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Web App created successfully")
            return True
        else:
            print(f"❌ Failed to create Web App: {result.stderr}")
            return False
    
    def create_storage_account(self):
        """Create storage account for file storage."""
        print(f"\n💾 Creating storage account: {self.storage_account}")
        
        cmd = [
            "az", "storage", "account", "create",
            "--name", self.storage_account,
            "--resource-group", self.resource_group,
            "--location", self.location,
            "--sku", "Standard_LRS"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Storage account created successfully")
            
            # Get connection string
            cmd = [
                "az", "storage", "account", "show-connection-string",
                "--resource-group", self.resource_group,
                "--name", self.storage_account,
                "--query", "connectionString",
                "--output", "tsv"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.storage_connection_string = result.stdout.strip()
                return True
            else:
                print(f"⚠️ Could not get storage connection string: {result.stderr}")
                return False
        else:
            print(f"❌ Failed to create storage account: {result.stderr}")
            return False
    
    def configure_app_settings(self):
        """Configure application settings."""
        print(f"\n⚙️ Configuring app settings...")
        
        settings = [
            "WEBSITES_PORT=8000",
            "PYTHONPATH=/home/site/wwwroot",
            "SCM_DO_BUILD_DURING_DEPLOYMENT=true"
        ]
        
        if hasattr(self, 'storage_connection_string'):
            settings.append(f"AZURE_STORAGE_CONNECTION_STRING={self.storage_connection_string}")
        
        cmd = [
            "az", "webapp", "config", "appsettings", "set",
            "--resource-group", self.resource_group,
            "--name", self.app_name,
            "--settings"
        ] + settings
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ App settings configured successfully")
            return True
        else:
            print(f"❌ Failed to configure app settings: {result.stderr}")
            return False
    
    def set_startup_command(self):
        """Set startup command for the web app."""
        print(f"\n🚀 Setting startup command...")
        
        startup_command = "gunicorn -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 src.main:app"
        
        cmd = [
            "az", "webapp", "config", "set",
            "--resource-group", self.resource_group,
            "--name", self.app_name,
            "--startup-file", startup_command
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Startup command set successfully")
            return True
        else:
            print(f"❌ Failed to set startup command: {result.stderr}")
            return False
    
    def prepare_deployment_files(self):
        """Prepare files for deployment."""
        print(f"\n📦 Preparing deployment files...")
        
        # Update requirements.txt for Azure
        azure_requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "python-docx==0.8.11",
            "python-multipart==0.0.6",
            "aiofiles==23.2.1",
            "pydantic==2.5.0",
            "pydantic-settings==2.1.0",
            "gunicorn==21.2.0"
        ]
        
        with open("requirements-azure.txt", "w") as f:
            f.write("\n".join(azure_requirements))
        
        print("✅ Created requirements-azure.txt")
        
        # Create .deployment file
        deployment_config = """[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
COMMAND=bash deploy.sh"""
        
        with open(".deployment", "w") as f:
            f.write(deployment_config)
        
        print("✅ Created .deployment file")
        
        # Create deploy.sh
        deploy_script = """#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-azure.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads converted logs

echo "Deployment preparation complete!"
"""
        
        with open("deploy.sh", "w") as f:
            f.write(deploy_script)
        
        # Make deploy.sh executable
        os.chmod("deploy.sh", 0o755)
        
        print("✅ Created deploy.sh")
        
        return True
    
    def deploy_code(self):
        """Deploy code to Azure."""
        print(f"\n📤 Deploying code to Azure...")
        
        # Use az webapp up for deployment
        cmd = [
            "az", "webapp", "up",
            "--resource-group", self.resource_group,
            "--name", self.app_name,
            "--runtime", "PYTHON|3.12",
            "--sku", "B1"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Code deployed successfully")
            return True
        else:
            print(f"❌ Failed to deploy code: {result.stderr}")
            return False
    
    def show_deployment_info(self):
        """Show deployment information."""
        print(f"\n🎉 Deployment Complete!")
        print("=" * 50)
        print(f"🌐 App URL: https://{self.app_name}.azurewebsites.net")
        print(f"📖 API Docs: https://{self.app_name}.azurewebsites.net/docs")
        print(f"🏥 Health Check: https://{self.app_name}.azurewebsites.net/health")
        print(f"📊 Azure Portal: https://portal.azure.com")
        print("\n⚙️ Management Commands:")
        print(f"   View logs: az webapp log tail --name {self.app_name} --resource-group {self.resource_group}")
        print(f"   SSH access: az webapp ssh --name {self.app_name} --resource-group {self.resource_group}")
        print(f"   Restart app: az webapp restart --name {self.app_name} --resource-group {self.resource_group}")
    
    def deploy(self):
        """Run complete deployment process."""
        print("🚀 Azure Deployment for Document Processing Service")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_azure_cli():
            return False
        
        # Get user configuration
        if not self.get_user_input():
            print("❌ Deployment cancelled by user")
            return False
        
        try:
            # Create resources
            if not self.create_resource_group():
                return False
            
            if not self.create_app_service_plan():
                return False
            
            if not self.create_web_app():
                return False
            
            if not self.create_storage_account():
                return False
            
            if not self.configure_app_settings():
                return False
            
            if not self.set_startup_command():
                return False
            
            # Prepare and deploy
            if not self.prepare_deployment_files():
                return False
            
            if not self.deploy_code():
                return False
            
            # Show results
            self.show_deployment_info()
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False

def main():
    """Main function."""
    helper = AzureDeploymentHelper()
    
    print("Choose deployment option:")
    print("1. 🚀 Full deployment (recommended)")
    print("2. 🔧 Check prerequisites only")
    print("3. 📦 Prepare deployment files only")
    print("4. ❓ Show Azure CLI commands")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        helper.deploy()
    elif choice == "2":
        helper.check_azure_cli()
    elif choice == "3":
        helper.prepare_deployment_files()
    elif choice == "4":
        show_azure_commands()
    else:
        print("❌ Invalid choice")

def show_azure_commands():
    """Show useful Azure CLI commands."""
    print("\n📋 Useful Azure CLI Commands:")
    print("=" * 40)
    
    commands = [
        ("Login to Azure", "az login"),
        ("List subscriptions", "az account list"),
        ("Set subscription", "az account set --subscription <subscription-id>"),
        ("List resource groups", "az group list"),
        ("List web apps", "az webapp list"),
        ("View app logs", "az webapp log tail --name <app-name> --resource-group <rg-name>"),
        ("Restart app", "az webapp restart --name <app-name> --resource-group <rg-name>"),
        ("SSH to app", "az webapp ssh --name <app-name> --resource-group <rg-name>"),
        ("Delete resource group", "az group delete --name <rg-name>"),
    ]
    
    for description, command in commands:
        print(f"• {description}:")
        print(f"  {command}")
        print()

if __name__ == "__main__":
    main()

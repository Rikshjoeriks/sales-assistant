#!/usr/bin/env python3
"""
API Key Setup for Spec Matcher
Helps you configure your OpenAI API key
"""

import os
import sys
from pathlib import Path

def setup_api_key():
    """Setup OpenAI API key with multiple options"""
    
    print("🔑 OpenAI API Key Setup")
    print("=" * 30)
    
    # Check if already set
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"✅ API key already set: {current_key[:8]}...{current_key[-4:]}")
        choice = input("\nDo you want to update it? (y/n): ").lower()
        if choice != 'y':
            return True
    
    print("\n📋 Choose how to set your API key:")
    print("1. Set for this session only (temporary)")
    print("2. Create .env file (recommended)")
    print("3. Set system environment variable (permanent)")
    print("4. Test current setup")
    
    choice = input("\nChoice (1-4): ").strip()
    
    if choice == '1':
        api_key = input("\n🔑 Enter your OpenAI API key: ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            print("✅ API key set for this session!")
            return test_api_key()
    
    elif choice == '2':
        api_key = input("\n🔑 Enter your OpenAI API key: ").strip()
        if api_key:
            env_file = Path('.env')
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            print(f"✅ API key saved to {env_file}")
            print("💡 Install python-dotenv to load automatically:")
            print("   pip install python-dotenv")
            
            # Also set for current session
            os.environ['OPENAI_API_KEY'] = api_key
            return test_api_key()
    
    elif choice == '3':
        api_key = input("\n🔑 Enter your OpenAI API key: ").strip()
        if api_key:
            print("\n📋 To set system environment variable:")
            print(f"Windows: setx OPENAI_API_KEY \"{api_key}\"")
            print(f"Linux/Mac: export OPENAI_API_KEY=\"{api_key}\"")
            print("\n⚠️  You'll need to restart your terminal/IDE after setting it")
            
            # Also set for current session
            os.environ['OPENAI_API_KEY'] = api_key
            return test_api_key()
    
    elif choice == '4':
        return test_api_key()
    
    else:
        print("❌ Invalid choice")
        return False

def test_api_key():
    """Test if the API key works"""
    print("\n🧪 Testing API key...")
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ No API key found!")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10,
            stream=False
        )
        
        # Safely extract content from response
        try:
            result = response.choices[0].message.content
            print(f"✅ API key works! Response: {result}")
            return True
        except (AttributeError, IndexError, TypeError) as e:
            print(f"❌ Invalid API response structure: {e}")
            return False
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def launch_app():
    """Launch the spec matcher app"""
    print("\n🚀 Launching Spec Matcher...")
    
    try:
        import subprocess
        import sys
        
        # Use the same Python executable
        result = subprocess.run([sys.executable, "ui.py"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ App failed to start:")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
        else:
            print("✅ App should be running!")
            return True
            
    except subprocess.TimeoutExpired:
        print("✅ App started successfully (running in background)")
        return True
    except Exception as e:
        print(f"❌ Failed to launch app: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Spec Matcher Setup Assistant")
    print("================================")
    
    # Step 1: Setup API key
    if setup_api_key():
        print("\n" + "="*50)
        
        # Step 2: Launch app
        choice = input("\n🚀 Launch Spec Matcher now? (y/n): ").lower()
        if choice == 'y':
            launch_app()
        else:
            print("\n💡 To launch manually, run: python ui.py")
            print("🔑 Make sure your API key is set!")
    
    else:
        print("\n❌ Please set up your API key first")
        print("💡 You can get an API key from: https://platform.openai.com/api-keys")
    
    input("\nPress Enter to exit...")

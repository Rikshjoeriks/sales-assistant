#!/usr/bin/env python3
"""
Test the section header fix with a small example
"""

import csv
import tempfile
import pathlib
from run_pipeline import main

def create_test_masterlist():
    """Create a small test masterlist with section headers"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nr Code', 'Variable Name', 'Is TT'])
        writer.writerow(['NR1', 'Piedziņa', 'Y'])  # Section header
        writer.writerow(['NR2', '4X4 pilna laika', 'N'])  # Feature
        writer.writerow(['NR3', 'Ārējais Izskats', 'Y'])  # Section header
        writer.writerow(['NR4', 'LED lukturi', 'N'])  # Feature
        return pathlib.Path(f.name)

def create_test_input():
    """Create test input text"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("LED priekšējie lukturi\nElektriski regulējami spoguļi")
        return pathlib.Path(f.name)

def test_section_headers():
    """Test that section headers get empty values"""
    print("🧪 Testing section header fix...")
    
    # Create test files
    master_file = create_test_masterlist()
    input_file = create_test_input()
    
    try:
        print(f"📝 Test masterlist: {master_file}")
        print(f"📝 Test input: {input_file}")
        
        # Run pipeline with test data
        import sys
        sys.argv = [
            'test_section_headers.py',
            '--model', 'TEST',
            '--specfile', str(input_file),
            '--master', str(master_file),
            '--exportdir', 'exports',
            '--llm', 'gpt-4o-mini'  # Use cheaper model for testing
        ]
        
        main()
        
        # Check the output
        output_files = list(pathlib.Path('exports/TEST').glob('ticksheet_*.csv'))
        if output_files:
            latest_output = max(output_files, key=lambda p: p.stat().st_mtime)
            print(f"📊 Output file: {latest_output}")
            
            with open(latest_output, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            print("\n📋 Output rows:")
            for i, row in enumerate(rows):
                print(f"  {i}: {row}")
                
            # Check section headers
            header_issues = []
            for row in rows[1:]:  # Skip header
                if len(row) >= 3 and row[2] == 'Y':  # Is TT = Y
                    if row[3:6] != ['', '', '']:  # Should be empty match, text, reason
                        header_issues.append(f"Row {row[0]}: Section header has non-empty values: {row[3:6]}")
            
            if header_issues:
                print("❌ Section header issues found:")
                for issue in header_issues:
                    print(f"  - {issue}")
                return False
            else:
                print("✅ Section headers correctly have empty values!")
                return True
        else:
            print("❌ No output file found")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        try:
            master_file.unlink()
            input_file.unlink()
        except:
            pass

if __name__ == "__main__":
    success = test_section_headers()
    print(f"\n🎯 Test result: {'PASSED' if success else 'FAILED'}")

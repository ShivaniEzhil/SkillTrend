import sys
import os

# Add the src/processing directory to sys.path so we can import the processor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/processing')))

try:
    from processor import extract_skills
except ImportError:
    # Fallback if the path logic above is tricky on different OS
    print("Warning: Could not import extract_skills directly. Ensure paths are correct.")

def test_skill_extraction():
    """Test if the extraction engine correctly identifies skills."""
    print("Running test_skill_extraction...")
    
    # Test 1: Standard description
    desc = "We need a Data Engineer proficient in Python and SQL."
    skills = extract_skills(desc)
    assert "Python" in skills, f"Expected 'Python' in {skills}"
    assert "SQL" in skills, f"Expected 'SQL' in {skills}"
    print("✅ Test 1: Standard extraction passed.")

    # Test 2: Case sensitivity and punctuation
    desc = "Expertise in python, postgresql, and AWS; spark is a plus."
    skills = extract_skills(desc)
    assert "Python" in skills, f"Expected 'Python' in {skills}"
    assert "PostgreSQL" in skills, f"Expected 'PostgreSQL' in {skills}"
    assert "AWS" in skills, f"Expected 'AWS' in {skills}"
    assert "Spark" in skills, f"Expected 'Spark' in {skills}"
    print("✅ Test 2: Case and punctuation passed.")

    # Test 3: No skills found
    desc = "Looking for someone with great communication skills and leadership."
    skills = extract_skills(desc)
    assert len(skills) == 0, f"Expected 0 skills, but found {skills}"
    print("✅ Test 3: Empty results handled.")

    # Test 4: Word boundary protection (e.g., 'go' shouldn't match 'good')
    desc = "This is a good opportunity."
    skills = extract_skills(desc)
    assert "Go" not in skills, f"Should NOT have found 'Go' in '{desc}'"
    print("✅ Test 4: Word boundary protection passed.")

if __name__ == "__main__":
    try:
        test_skill_extraction()
        print("\n🏆 All tests passed! The pipeline logic is robust.")
    except AssertionError as e:
        print(f"\n❌ Test failed! Error: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

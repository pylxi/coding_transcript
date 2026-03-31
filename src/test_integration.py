#!/usr/bin/env python
"""
Integration Test for Discourse Segmentation

This file documents the expected behavior and provides a simple test
for the discourse segmentation integration.

Usage:
    python test_integration.py
"""

import os
import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from csv_loader import load_csv_file
        print("✅ csv_loader imported successfully")
    except ImportError as e:
        print(f"❌ csv_loader import failed: {e}")
        return False
    
    try:
        from episode_extractor import EpisodeExtractor
        print("✅ episode_extractor imported successfully")
    except ImportError as e:
        print(f"❌ episode_extractor import failed: {e}")
        return False
    
    try:
        from discourse_segmenter import segment_dialogue
        print("✅ discourse_segmenter imported successfully")
    except ImportError as e:
        print(f"⚠️  discourse_segmenter not available: {e}")
        print("   (This is OK if openai package is not installed)")
        return True  # Not a failure, just optional
    
    return True


def test_csv_loader():
    """Test CSV loading with sample data"""
    print("\nTesting CSV loader...")
    
    import pandas as pd
    from csv_loader import load_csv_file
    import tempfile
    
    # Create a sample CSV
    sample_data = """speaker,timestamp,utterance
Alice,00:01,Hello Bob
Bob,00:05,Hi Alice
Alice,00:10,How are you?
Bob,00:15,I'm doing well thanks"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_data)
        temp_file = f.name
    
    try:
        df = load_csv_file(temp_file)
        print(f"✅ Loaded CSV with {len(df)} rows")
        print(f"   Columns: {list(df.columns)}")
        
        # Check required columns
        required = {'timestamp', 'speaker', 'utterance', 'timestamp_seconds'}
        if required.issubset(set(df.columns)):
            print(f"✅ All required columns present")
        else:
            print(f"❌ Missing columns: {required - set(df.columns)}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ CSV loading failed: {e}")
        return False
    finally:
        os.unlink(temp_file)


def test_similarity_extractor():
    """Test similarity-based episode extraction"""
    print("\nTesting similarity-based extractor...")
    
    import pandas as pd
    from episode_extractor import EpisodeExtractor
    import tempfile
    
    # Create sample data with more utterances
    sample_data = """speaker,timestamp,utterance
Alice,00:01,Hello Bob let's discuss the project
Bob,00:05,Sure what do you want to talk about
Alice,00:10,I want to know about the timeline
Bob,00:15,The project starts next Monday
Alice,00:20,That sounds good to me
Bob,00:25,Great we're aligned on timing
Alice,00:30,Perfect let's discuss the team
Bob,00:35,I have five people assigned
Alice,00:40,Is that enough for the scope
Bob,00:45,Yes it should be sufficient"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample_data)
        temp_file = f.name
    
    try:
        from csv_loader import load_csv_file
        df = load_csv_file(temp_file)
        
        extractor = EpisodeExtractor()
        episode = extractor.extract_next_episode(df, 0)
        
        if episode:
            print(f"✅ Episode extracted successfully")
            print(f"   Duration: {episode['duration_minutes']:.1f} minutes")
            print(f"   Utterances: {episode['utterance_count']}")
            print(f"   Speakers: {episode['speakers']}")
            return True
        else:
            print(f"❌ No episode extracted")
            return False
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.unlink(temp_file)


def test_discourse_support():
    """Test discourse segmentation availability and configuration"""
    print("\nTesting discourse segmenter availability...")
    
    try:
        from discourse_segmenter import segment_dialogue, DIMENSION_RULES
        print("✅ Discourse segmenter available")
        
        # Check environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            print("✅ OPENAI_API_KEY is set")
        else:
            print("⚠️  OPENAI_API_KEY not set (required for discourse segmentation)")
        
        # Check dimensions
        if "Sustaining mutual understanding" in DIMENSION_RULES:
            print("✅ Collaboration dimensions defined")
        
        return True
    except ImportError:
        print("⚠️  Discourse segmenter not available (openai not installed)")
        return True  # Not a failure


def main():
    """Run all tests"""
    print("=" * 60)
    print("Discourse Segmentation Integration Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("CSV Loader", test_csv_loader),
        ("Similarity Extractor", test_similarity_extractor),
        ("Discourse Support", test_discourse_support),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

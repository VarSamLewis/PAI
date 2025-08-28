from PAI.utils.logger import logger
"""
def _gen_test_identity() -> int:
  
    if not file_path.exists():
       logger.warning(f"No file found for function '{func.__name__}'.")
       return []
    max_val = float('-inf')
    data = _load_json(file_path)
    tests = data.get("tests", [])
    for test in tests:
       test_id = test.get(KEY_TEST_ID, [])
       if isinstance(test_id, int) and test_id > max_val:
           max_val = test_id

    return max_val + 1 if max_val != float('-inf') else 1
"""
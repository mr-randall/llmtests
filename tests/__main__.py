import unittest
import llmtests

class TestFramework():
    def __init__(self) -> None:
        self.llm_response = None
        self.load_first_expected_response()
        
    def first_expected_chat_exactly_fn(self, _messages):
        return {"content": f"<think>Hmm I don't know how to think</think>\n\n{self.llm_response}"}

    def first_expected_chat_upper_fn(self, _messages):
        return {"content": f"<think>Hmm I don't know how to think</think>\n\n{self.llm_response.upper()}"}
    
    def empty_chat_response_fn(self, _messages):
        return {"content": f"<think>Hmm I don't know how to think</think>\n\n"}

    def load_first_expected_response(self):
        filenames = llmtests.get_json_files_in_folder(llmtests.SETTINGS.tests_folder)
        for filename in filenames:
            test_config = llmtests.load_from_file(filename)
            self.llm_response = test_config["tests"][0]["expected_response"]
            break
        assert self.llm_response is not None, f"Expected response not found in {filenames[0]}"
        
    def test_all_with_fn(self, func):
        file_results = llmtests.test_all(func)
        pass_count = 0
        test_count = 0
        
        for file_result in file_results:
            for setup_results in file_result["results"]:
                for test_result in setup_results["results"]:
                    print(test_result)
                    test_count += 1
                    if test_result['pass']:
                        pass_count += 1
                        
        return {"pass_count": pass_count, "test_count": test_count}


class LLMTestMethods(unittest.TestCase):
    def test_all_with_fn(self):
        framework = TestFramework()
        results = framework.test_all_with_fn(lambda messages: framework.first_expected_chat_exactly_fn(messages))
         
        self.assertGreater(results['pass_count'], 0)
        self.assertGreater(results['test_count'], 0)
        print(results['pass_count'],"/",results['test_count'],"tests passed")
        
        results = framework.test_all_with_fn(lambda messages: framework.first_expected_chat_upper_fn(messages))
        
        self.assertGreater(results['pass_count'], 0)
        self.assertGreater(results['test_count'], 0)
        print(results['pass_count'],"/",results['test_count'],"tests passed")
        
        results = framework.test_all_with_fn(lambda messages: framework.empty_chat_response_fn(messages))
        
        self.assertEqual(results['pass_count'], 0)
        self.assertGreater(results['test_count'], 0)
        print(results['pass_count'],"/",results['test_count'],"tests passed")

if __name__ == '__main__':
    unittest.main()
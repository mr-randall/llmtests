import inspect
import unittest
import llmtests

class TestFramework():
    def __init__(self) -> None:
        self.llm_response = None
        self.load_first_expected_response()
        
    def first_expected_chat_exactly_fn(self, _messages):
        return {"message": {"role":"assistant", "content": f"<think>Hmm I don't know how to think</think>\n\n{self.llm_response}"}}

    def first_expected_chat_upper_fn(self, _messages):
        return {"message":{"role":"assistant", "content": f"<think>Hmm I don't know how to think</think>\n\n{self.llm_response.upper()}"}}
    
    def empty_chat_response_fn(self, _messages):
        return {"message":{"role":"assistant", "content": f"<think>Hmm I don't know how to think</think>\n\n"}}

    def load_first_expected_response(self):
        filenames = llmtests.get_json_files_in_folder(llmtests.SETTINGS.tests_folder)
        for filename in filenames:
            test_config = llmtests.load_from_file(filename)
            self.llm_response = test_config["tests"][0]["expected_response"]
            break
        assert self.llm_response is not None, f"Expected response not found in {filenames[0]}"
        
    def test_all_with_fn(self, func):
        file_results = llmtests.test_all(func, lambda context_reset, memory_reset:())
        report_stat = llmtests.test_results_as_text_report(file_results)
                        
        return {"pass_count": report_stat['pass_count'], "test_count": report_stat['test_count']}
    
    def test_all_write_reports(self, func):
        file_results =  llmtests.test_all(func, lambda context_reset, memory_reset:())
        llmtests.test_results_as_html_report(file_results, "./reports")


class LLMTestMethods(unittest.TestCase):
    def test_all_with_exact_fn(self):
        framework = TestFramework()
        results = framework.test_all_with_fn(lambda messages: framework.first_expected_chat_exactly_fn(messages))
         
        self.assertGreater(results['pass_count'], 0)
        self.assertGreater(results['test_count'], 0)
        print(results['pass_count'],"/",results['test_count'],"tests passed",inspect.currentframe().f_code.co_name)
        
    def test_all_with_upper_fn(self):
        framework = TestFramework()
        results = framework.test_all_with_fn(lambda messages: framework.first_expected_chat_upper_fn(messages))
        
        self.assertGreater(results['pass_count'], 0)
        self.assertGreater(results['test_count'], 0)
        print(results['pass_count'],"/",results['test_count'],"tests passed",inspect.currentframe().f_code.co_name)
        
    def test_all_with_empty_fn(self):
        framework = TestFramework()
        results = framework.test_all_with_fn(lambda messages: framework.empty_chat_response_fn(messages))
        
        self.assertEqual(results['pass_count'], 0)
        self.assertGreater(results['test_count'], 0)
        print(results['pass_count'],"/",results['test_count'],"tests passed",inspect.currentframe().f_code.co_name)
        
    def test_all_with_for_raw_report(self):
        framework = TestFramework()
        #report = 
        framework.test_all_write_reports(lambda messages: framework.first_expected_chat_exactly_fn(messages))
        
        
        #self.assertGreater(report['pass_count'], 0)
        #self.assertGreater(report['test_count'], 0)
        
        #print( report)

if __name__ == '__main__':
    unittest.main()
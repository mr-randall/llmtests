import json
from os import walk, path
from re import sub, DOTALL

class SETTINGS:
    tests_folder = "./llmtests/test_files"
    case_sensitive = False

def get_json_files_in_folder(folder_path, recursive=False):
    test_file_paths = []
    for (root, _, filenames) in walk(folder_path):
        for name in filenames:
            if name.endswith(".json"):
                test_file_paths.append(path.join(root, name).replace("\\","/"))
        if not recursive:
            break
    return test_file_paths


def tidy_llm_response(llm_resp):
    response = llm_resp["content"]
    no_think_response = sub(r'<think>(.*?)<\/think>\n\n', '', response, flags=DOTALL)
    return no_think_response
    

def test_single_setup(chat_fn, setup_conf, tests_conf):
    
    test_results = []
    
    setup_summary='<No setup summary>'
    if "summary" in setup_conf:
        setup_summary=setup_conf['summary']
    
    #Provide the LLM with the prior conversation
    for prior_conversation in setup_conf["prior_conversations"]:
        chat_fn(prior_conversation)        
        
    #New context and perform tests
    for test in tests_conf:
        tidy_resp = tidy_llm_response(chat_fn(test["messages"]))
        
        test_summary='<No test summary>'
        if "summary" in test:
            test_summary=test['summary']
        
        test_result = (tidy_resp == test["expected_response"])
        if not SETTINGS.case_sensitive:
            test_result = (tidy_resp.lower() == test["expected_response"].lower())
            
        test_results.append({
            'summary': test_summary,
            'result': tidy_resp,
            'expected': test["expected_response"],
            'pass': test_result
            })
                
    return {'summary':setup_summary, 'results': test_results}
        


def test_from_json(chat_fn, test_json):
    setups = test_json["setups"]
    tests = test_json["tests"]
    
    results = []
    
    for setup in setups:
        results.append(test_single_setup(chat_fn, setup, tests))
        
    return results


def load_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def test_from_file(chat_fn, filename):
    return {"summary": filename, "results": test_from_json(chat_fn, load_from_file(filename))}
    
    
def test_all_in_folder(chat_fn, folder_path):
    test_files = get_json_files_in_folder(folder_path)
    results = []
    for filename in test_files:
        results.append(test_from_file(chat_fn, filename))
    return results


def test_all(chat_fn):
    return test_all_in_folder(chat_fn, SETTINGS.tests_folder)


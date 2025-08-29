import json
from os import walk, path
from re import sub, DOTALL

class SETTINGS:
    dir_path = path.dirname(path.realpath(__file__))
    tests_folder = dir_path+"/test_files"
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
    

def test_single_setup(chat_fn, reset_fn, setup_conf, tests_conf):
    
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
        if reset_fn:
            reset_fn(context_reset=False, memory_reset=True)
    
    if reset_fn:
        reset_fn(context_reset=False, memory_reset=True)
                
    return {'summary':setup_summary, 'results': test_results}
        


def test_from_json(chat_fn, reset_fn, test_json):
    setups = test_json["setups"]
    tests = test_json["tests"]
    
    results = []
    
    for setup in setups:
        results.append(test_single_setup(chat_fn, reset_fn, setup, tests))
        
    return results


def load_from_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def test_from_file(chat_fn, reset_fn, filename):
    return {"summary": filename, "results": test_from_json(chat_fn, reset_fn, load_from_file(filename))}
    
    
def test_all_in_folder(chat_fn, reset_fn, folder_path):
    test_files = get_json_files_in_folder(folder_path)
    results = []
    for filename in test_files:
        results.append(test_from_file(chat_fn, reset_fn, filename))
    return results


def test_all(chat_fn, reset_fn):
    return test_all_in_folder(chat_fn, reset_fn, SETTINGS.tests_folder)

def test_results_as_text_report(results_array):
    pass_count = 0
    test_count = 0
    
    file_results_array = []
    
    # Ensure the result is always at the file level
    if 'results' in results_array[0]:
        if 'results' not in results_array[0]['results'][0]:
            file_results_array.append({'results': results_array}) #Missing 2nd level results
        else:
            file_results_array = results_array #Already formatted correctly
    else:
        file_results_array.append({'results': [{'results': results_array}]}) #Missing first level results
        
    failed_report_txt = ''
    
    for file_result in file_results_array:
        for setup_results in file_result["results"]:
            for test_result in setup_results["results"]:
                if not test_result['pass']:
                    failed_report_txt += json.dumps(test_result)+'\n'

                test_count += 1
                if test_result['pass']:
                    pass_count += 1
                    
    if failed_report_txt == '':
        failed_report_txt = "No failed tests"
    return {'pass_count': pass_count, 'test_count': test_count, 'failed_report': failed_report_txt}


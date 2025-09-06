import json
from os import walk, path, remove, makedirs
from re import sub, DOTALL
from glob import glob

class SETTINGS:
    dir_path = path.dirname(path.realpath(__file__))
    tests_folder = dir_path+"/test_files"
    case_sensitive = False
    remove_fullstop = True
    write_fully_passed_test_reports = True
    clean_report_folder = True

def get_json_files_in_folder(folder_path, recursive=False):
    test_file_paths = []
    for (root, _, filenames) in walk(folder_path):
        for name in filenames:
            if name.endswith(".json"):
                test_file_paths.append(path.join(root, name).replace("\\","/"))
        if not recursive:
            break
    return test_file_paths


def tidy_llm_response(llm_resp_text):
    response = llm_resp_text
    no_think_response = sub(r'<think>(.*?)<\/think>\n\n', '', response, flags=DOTALL)
    return no_think_response
    

def test_single_setup(chat_fn, reset_fn, setup_conf, tests_conf):
    test_results = []
    conversation_log = []
    
    setup_summary='<No setup summary>'
    if "summary" in setup_conf:
        setup_summary=setup_conf['summary']
    
    #Provide the LLM with the prior conversation
    for prior_conversation in setup_conf["prior_conversations"]:
        conversation_log.extend(prior_conversation)
        llm_resp = chat_fn(prior_conversation)
        llm_resp_obj = {"role" : llm_resp["message"]["role"], "content": llm_resp["message"]["content"]}
        conversation_log.append(llm_resp_obj)
        
    
        
    #New context and perform tests
    for test in tests_conf:
        conversation_log.extend(test["messages"])
        llm_resp = chat_fn(test["messages"])
        llm_resp_text = llm_resp["message"]["content"]
        llm_resp_obj = {"role" : llm_resp["message"]["role"], "content": llm_resp["message"]["content"]}
        conversation_log.append(llm_resp_obj)
        tidy_resp = tidy_llm_response(llm_resp_text)
        
        test_summary='<No test summary>'
        if "summary" in test:
            test_summary=test['summary']
        
        test_result = (tidy_resp == test["expected_response"])
        if not test_result and not SETTINGS.case_sensitive:
            tidy_resp = tidy_resp.lower()
            test_result = (tidy_resp == test["expected_response"].lower())
        if not test_result and SETTINGS.remove_fullstop:
            tidy_resp = sub(r'\.$', '', tidy_resp) 
            test_result = (tidy_resp == test["expected_response"])
            
        test_results.append({
            'summary': test_summary,
            'result': tidy_resp,
            'expected': test["expected_response"],
            'pass': test_result
            })
        if reset_fn:
            reset_fn(context_reset=True, memory_reset=False)
            conversation_log.append({"role":"Context reset","content":""})
    
    if reset_fn:
        reset_fn(context_reset=False, memory_reset=True)
        conversation_log.append({"role":"Memory reset","content":""})
                
    return {'summary':setup_summary, 'results': test_results, "conversation_log": conversation_log}
        


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

def test_results_as_html_report(results_array, folder_name):
    pass_count = 0
    test_count = 0
    
    if not path.exists(folder_name):
        makedirs(folder_name)
    else:
        if SETTINGS.clean_report_folder:
            for f in glob(path.join(folder_name,"test-*-*.html")):
                remove(f)
    
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
    
    test_file_number = 0
    
    
    for file_result in file_results_array:
        test_file_number += 1
        test_setup_number = 0
        pass_count = 0
        for setup_results in file_result["results"]:
            test_setup_number += 1
            test_result_number = 0
            
            file_name = f"test-{test_file_number}-{test_setup_number}.html"
            file_content = ''
            
            file_content += f"<h1>Setup {test_setup_number}</h1>"
            file_content += f"<h2>Summary</h2>"
            file_content += f"{setup_results['summary']}"
            file_content += f"<h2>Results</h2>"
            file_content += f"<table>"
            file_content += f"<tr><th>#</th><th>Name</th><th>Expected</th><th>Result</th><th>Pass</th></tr>"
            
            for test_result in setup_results["results"]:
                test_result_number += 1
                pass_count += int(test_result['pass'])
                file_content += f"<tr><td>{test_result_number}</td><td>{test_result['summary']}</td><td>{test_result['expected']}</td><td>{test_result['result']}</td><td>{test_result['pass']}</td></tr>"
                
            file_content += f"</table>"
            file_content += f"<h2>Conversation</h2>"
            file_content += f"<pre>{json.dumps(setup_results['conversation_log'], indent=4)}</pre>"
            
            if pass_count > 0 or SETTINGS.write_fully_passed_test_reports:
                with open(path.join(folder_name, file_name), 'w') as file:
                    file.write(file_content)
                    
    if failed_report_txt == '':
        failed_report_txt = "No failed tests"
    return {'pass_count': pass_count, 'test_count': test_count, 'failed_report': failed_report_txt}

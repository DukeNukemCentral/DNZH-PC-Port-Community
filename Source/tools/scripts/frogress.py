#!/usr/bin/env python3
import requests
import argparse
import subprocess
import progress

def get_timestamp() -> int:
    return int(subprocess.check_output(['git', 'show', '-s', '--format=%ct']).decode('ascii').rstrip())

def get_commit_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

def get_api_post_url() -> str:
    url = domain + "/data/dukezh/"+version+"/"
    return url

def push_data_to_api(data) -> None:
    url = get_api_post_url()
    r = requests.post(url, json=data)
    r.raise_for_status()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload progress to API")
    parser.add_argument("version", help="Version slug")
    parser.add_argument("--api_key", help="API key for progress.deco.mp")
    args = parser.parse_args()
    
    version = args.version
    api_key = args.api_key
    
    domain = "https://progress.deco.mp"
    
    # Should be generated by progress chart
    matching_funcs, all_funcs, funcs_matching_ratio, matching_size, total_size, matching_ratio = progress.getProgressData()
    
    # data structure
    entries = []
    entries.append({
        "timestamp": get_timestamp(),
        "git_hash": get_commit_hash(),
        "categories": {
            "default": {
                "funcs": matching_funcs,
                "funcs/total": all_funcs,
                "bytes": matching_size,
                "bytes/total": total_size,
            },
        },
    })
    
    # Data to send to API
    end_data = {
        "api_key": api_key,
        "entries": entries,
    }
    
    # get previous posts and check git hash
    r = requests.get(domain+"/data/dukezh/"+version+"/default/")
    res = r.json()
    prev_hash = res["dukezh"][version]["default"][0]["git_hash"]
    prev_matching_funcs = res["dukezh"][version]["default"][0]["measures"]["funcs"]
    prev_matching_size = res["dukezh"][version]["default"][0]["measures"]["bytes"]
    
    if prev_hash != get_commit_hash():
        if prev_matching_funcs < matching_funcs or prev_matching_size < matching_size:
            print("Change in progress... Pushing to API")
            push_data_to_api(end_data)
        else:
            print("No change in progress")
    else:
        print("Current push already in API")
        
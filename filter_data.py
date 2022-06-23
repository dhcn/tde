import json
begin =False
with open("./data/OkexSubscriber2021-03-14","r") as rf:
    with open('./data/Okex_file', 'w') as wf:
        while True:
            line=rf.readline()
            line_obj = json.loads(line)
            if "event" in line_obj and line_obj["event"] == "subscribe":
                begin=True
            if begin:
                wf.write(line)
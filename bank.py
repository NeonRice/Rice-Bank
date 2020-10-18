import redis
import getpass
import snake

r = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)  # Redis Connection Pool

class Option():
    def __init__(self, optionName, optionFunction):
        self.name = optionName
        self.function = optionFunction


def drawOptions(listOfOptions):
    optionNr = 1
    for option in listOfOptions:
        print(optionNr, option.name)
        optionNr += 1

def clearOutput():
    print("\033[H\033[J")

def initOutsideOptions():
    def userExists(username):
        return r.hexists("users", username)

    def createUser(username, password):
        next_user_id = r.incr("next_user_id", 1)
        user = {"name" : username, "password" : password, "next_account_id" : 0}
        r.hmset("user:" + str(next_user_id), user)
        r.hset("users", username, next_user_id)

    def registerUser():
        clearOutput()
        username = input("Username: ").lower()
        if not userExists(username):
            password = getpass.getpass("Password: ")
            createUser(username, password)
            print("User ", username, " created.\n")
            input("Press enter to continue...\n")
        else:
            print("User ", username, " already exists...\n")
            input("Press enter to continue...\n")

    def loginUser():
        clearOutput()
        session = {}
        username = input("Username: ").lower()
        if userExists(username):
            password = getpass.getpass("Password: ")
            uid = str(r.hget("users", username))
            if password == str(r.hget("user:" + uid, "password")): # If password same
                print("Login successful")
                session = {"name" : username, "password" : password, "uid" : uid}
            else:
                print("Password incorrect!")
        else:
            print("User does not exist!")
        
        input("Press enter to continue...\n")
        return session

    options = (
        Option("Register user", registerUser),
        Option("Login user", loginUser)
    )

    return options

def initInsideOptions(session):

    def getConfirmation():
        while(True):
            answer = input("Are you sure you want to perform this action? Y/N: ")
            if answer.upper() == "Y":
                return True
            elif answer.upper() == "N":
                return False

    def openAccount():
        if getConfirmation():
            uid = session["uid"]
            r.hincrby("user:" + str(uid), "next_account_id", 1)
            next_account_id = r.hget("user:" + str(uid), "next_account_id")
            r.set("RICE" + str(uid) + str(next_account_id), 0)
        #snake.playSnake() TO EARN RICE :)
    
    def transferRice():
        pass

    def checkAccountBalance():
        pass

    def earnRice():
        pass

    options = (
        Option("Account balance", checkAccountBalance),
        Option("Transfer rice", transferRice),
        Option("Open an account", openAccount)
        Option("Earn rice", earnRice)
    )

    return options

def checkConnection():
    try:
        r.ping()
        print("Connected to Redis successfully")
        input("Press Enter to continue...\n")

        return True

    except redis.ConnectionError as e:
        print("Connection not successful.. Is server online?")

        return False

def handleInput(options):
    choice = input()
    if choice.isdigit() and int(choice) <= len(options):
        choice = int(choice)
        return options[choice - 1].function()


if checkConnection():
    clearOutput()
    options = initOutsideOptions()
    while(True):
        drawOptions(options)
        session = handleInput(options)
        if session:
            options = initInsideOptions(session)
        clearOutput()
    # Connection successful... Continue
else:
    print("Rice Bank is offline right now! Must be due to sushi vandals trying to steal rice again..")
    # Connection unsuccessful... Exit???

import drinkAPI
import getpass
import os
import time
SYSTEM_NAMES = {'Drink':'d', 'Little Drink':'ld','Snack':'s'}


def machineMenu():
    system = None
    while system == None:
        system = selectMachine()
    
        if system == "q":
            quit()
    return system

def selectMachine():
    for i,systemName in zip(range(len(SYSTEM_NAMES)),SYSTEM_NAMES.keys()):
        print str(i)+'. '+systemName
    selection = ""
    selection = raw_input('Please select a machine or enter "q" to quit:\t')
    if selection.lower() == "q":
        return "q"
    selection = int(selection)
    if selection in range(len(SYSTEM_NAMES.keys())):
        return drinkAPI.System(SYSTEM_NAMES.keys()[selection], SYSTEM_NAMES.values()[selection])

def selectItem(system):
    print system
    selection = raw_input('Please select an item or enter "q" to go back:\t')
    if selection.lower() == "q":
        return "q"
    if int(selection) in range(1,len(system.inventory)+1):
        return system.inventory[((int)(selection)-1)]
    else:
        print "Bad selection..."
        return selectItem(system)



csh_net = drinkAPI.Network('csh.rit.edu')
user = drinkAPI.User(getpass.getuser())
machineSelect = True
while machineSelect:
    system=machineMenu()
    if system == "q":
        continue
    else:
        machineSelect=False
    user.connect_to_system(system,csh_net)
    print "You currently have " + str(user.get_credits_balance()) + " creditz!"
    choice = selectItem(system)
    if choice == "q":
        user.disconnect()
        machineSelect=True
        continue
    elif user.get_credits_balance() > choice.price:
        delay = int(raw_input("Time delay (0-100):\t"))
        time.sleep(float(delay))
        user.purchase(choice,delay)
        machineSelect = False
    else:
        print "Not enough Creditz!"

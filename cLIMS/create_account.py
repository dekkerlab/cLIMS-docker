'''
Created on Dec 20, 2016

@author: nanda
'''

#############CREATE ACCOUNT ##############
###RUN COMMAND FROM SHELL###
#python3 manage.py shell
#import create_account
#create_account.createAccounts("/home/ubuntu/clims_automated_emails/lab_emails.txt")
###########################################
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

def createAccountHelper(userEmail,userName, userPassword):
    if(get_user_model().objects.filter(username=userName)):
        print("WARNING!! USER ALREADY EXISTS, SKIPPING " + userName)
    else:
        user = get_user_model().objects.create_user(userName, userEmail, userPassword)
        user.save()
        name=userEmail.split("@")
        flName=name[0].split(".")
        user.first_name=flName[0]
        user.last_name=flName[1]
        user.save()
        group = Group.objects.get(name='Member')
        user.groups.add(group)
        print("USER CREATED "+userName)
    
    
def createAccounts(accountList):
    with open(accountList, 'r') as f:
        read_data = f.readlines()
        for line in read_data:
            userInfoArray = line.split()
            userEmail = userInfoArray[0].lower()
            name=userEmail.split("@")
            userName = name[0]
            userPassword = userInfoArray[2]
            createAccountHelper(userEmail,userName, userPassword)
            
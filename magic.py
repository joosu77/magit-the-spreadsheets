import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
field = client.open("mtg").worksheet("Field")
decks = client.open("mtg").worksheet("Decks")
cardDict = client.open("mtg").worksheet("Card dictionary")

P1_health = 20
P1_energy = 0
P1_mana = 0
P2_health = 20
P2_energy = 0
P2_mana = 0

allCards = {}
end = False

print "system setup complete"



# functions ###

def chatSend(mess, player):
    if player==1:
        field.update_cell(19,1,mess)
    else:
        field.update_cell(19,3,mess)

def chatGet(player):
    if player==1:
        field.update_cell(20,1,"waiting for response")
        while field.cell(20,2).value == "SEND":
            continue
        field.update_cell(20,2,"SEND")
        field.update_cell(20,1,'')
        val = field.cell(19,2).value
        field.update_cell(19,2,'')
    else:
        field.update_cell(20,3,"waiting for response")
        while field.cell(20,4).value == "SEND":
            continue
        field.update_cell(20,4,"SEND")
        field.update_cell(20,3,'')
        val = field.cell(19,4).value
        field.update_cell(19,4,'')
    return val

def findCell(line, searchable):
    i=0
    while not field.cell(line,3+i).value == searchable:
        i+=1
    return i

def parseText(mess, player):
    main = mess.split('!')[0]
    args = mess.split('!')[1]
    if (main == "life"):
        if (player == 1):
            if (args[0] == '+'):
                P1_health += int(args[1:])
            else:
                P1_health -= int(args[1:])
            field.update_cell(2,3,P1_health)
        else:
            if (args[0] == '+'):
                P2_health += int(args[1:])
            else:
                P2_health -= int(args[1:])
            field.update_cell(10,3,P2_health)
    elif (main == "energy"):
        if (player == 1):
            if (args[0] == '+'):
                P1_energy += int(args[1:])
            else:
                P1_energy -= int(args[1:])
            field.update_cell(2,4,P1_energy)
        else:
            if (args[0] == '+'):
                P2_energy += int(args[1:])
            else:
                P2_energy -= int(args[1:])
            field.update_cell(10,4,P2_energy)
    elif (main == "mana"):
        if (player == 1):
            if (args[0] == '+'):
                P1_mana += int(args[1:])
            else:
                P1_mana -= int(args[1:])
            field.update_cell(2,5,P1_mana)
        else:
            if (args[0] == '+'):
                P2_mana += int(args[1:])
            else:
                P2_mana -= int(args[1:])
            field.update_cell(10,5,P2_mana)
    elif (main == "draw"):
        if (player == 1):
            for i in range(int(args)):
                try:
                    P1_hand.append(P1_deck.pop())
                    i = 0
                    while not field.cell(3,4+i).value == '':
                        i+=1
                    field.update_cell(3,4+i,P1_hand[-1])
                except:
                    chatSend("deck empty, you lose", 1)
                    end = True
        else:
            for i in range(int(args)):
                try:
                    P2_hand.append(P2_deck.pop())
                    i = 0
                    while not field.cell(11,4+i).value == '':
                        i+=1
                    field.update_cell(11,4+i,P2_hand[-1])
                except:
                    chatSend("deck empty, you lose", 2)
                    end = True
    elif (main == "play"):
        if (player == 1):
            field.update_cell(3,3+findCell(3,args),'')
            P1_hand.remove(args)
            if allCards[args][0] == 'land':
                i = 0
                while not field.cell(4,4+i).value == '':
                    i+=1
                field.update_cell(4,4+i,args)
            elif allCards[args][0] == 'creature':
                i = 0
                while not field.cell(5,4+i).value == '':
                    i+=1
                field.update_cell(5,4+i,args)
                field.update_cell(6,4+i,allCards[args][4]+'/'+allCards[args][5])
            elif allCards[args][0] == 'artifact' or allCards[args][0] == 'enchantment' or allCards[args][0] == 'planeswalker':
                i = 0
                while not field.cell(7,4+i).value == '':
                    i+=1
                field.update_cell(7,4+i,args)
            elif allCards[args][0] == 'instant' or allCards[args][0] == 'sorcery':
                field.update_cell(2,7,args)
        else:
            field.update_cell(11,3+findCell(11,args),'')
            P2_hand.remove(args)
            if allCards[args][0] == 'land':
                i = 0
                while not field.cell(12,4+i).value == '':
                    i+=1
                field.update_cell(12,4+i,args)
            elif allCards[args][0] == 'creature':
                i = 0
                while not field.cell(13,4+i).value == '':
                    i+=1
                field.update_cell(13,4+i,args)
                field.update_cell(14,4+i,allCards[args][4]+'/'+allCards[args][5])
            elif allCards[args][0] == 'artifact' or allCards[args][0] == 'enchantment' or allCards[args][0] == 'planeswalker':
                i = 0
                while not field.cell(15,4+i).value == '':
                    i+=1
                field.update_cell(15,4+i,args)
            elif allCards[args][0] == 'instant' or allCards[args][0] == 'sorcery':
                field.update_cell(10,7,args)
    elif main == 'destroy':
        type = args.split(':')[0]
        name = args.split(':')[1]
        if player == 1:
            if type == 'hand':
                field.update_cell(3,findCell(3,name),'')
            elif type == 'land':
                field.update_cell(4,findCell(4,name),'')
            elif type == 'creature':
                field.update_cell(5,findCell(5,name),'')
                field.update_cell(6,findCell(6,name),'')
            elif type == 'permanent':
                field.update_cell(7,findCell(7,name),'')
            i = 0
            while not field.cell(8,4+i).value == '':
                i+=1
            field.update_cell(8,4+i,name)
        else:
            if type == 'hand':
                field.update_cell(11,findCell(11,name),'')
            elif type == 'land':
                field.update_cell(12,findCell(12,name),'')
            elif type == 'creature':
                field.update_cell(13,findCell(13,name),'')
                field.update_cell(14,findCell(14,name),'')
            elif type == 'permanent':
                field.update_cell(15,findCell(15,name),'')
            i = 0
            while not field.cell(16,4+i).value == '':
                i+=1
            field.update_cell(16,4+i,name)
    elif main == 'exile':
        type = args.split(':')[0]
        name = args.split(':')[1]
        if player == 1:
            if type == 'hand':
                field.update_cell(3,findCell(3,name),'')
            elif type == 'land':
                field.update_cell(4,findCell(4,name),'')
            elif type == 'creature':
                field.update_cell(5,findCell(5,name),'')
                field.update_cell(6,findCell(6,name),'')
            elif type == 'permanent':
                field.update_cell(7,findCell(7,name),'')
            elif type == 'graveyard':
                field.update_cell(8,findCell(8,name),'')
        else:
            if type == 'hand':
                field.update_cell(11,findCell(11,name),'')
            elif type == 'land':
                field.update_cell(12,findCell(12,name),'')
            elif type == 'creature':
                field.update_cell(13,findCell(13,name),'')
                field.update_cell(14,findCell(14,name),'')
            elif type == 'permanent':
                field.update_cell(15,findCell(15,name),'')
            elif type == 'graveyard':
                field.update_cell(16,findCell(16,name),'')
    elif main == 'modify': #adds +x/+y buff to a monster on the battlefield modify!<name>,x/y
        if player ==1:
            x = findCell(5,args.split(',')[0])
            stats = field.cell(6,x)
            field.update_cell(6,x,str(int(stats.split('/')[0])+int(args.split('/')[0]))+'/'+str(int(stats.split('/')[1])+int(args.split('/')[1])))
        else:
            x = findCell(13,args.split(',')[0])
            stats = field.cell(14,x)
            field.update_cell(14,x,str(int(stats.split('/')[0])+int(args.split('/')[0]))+'/'+str(int(stats.split('/')[1])+int(args.split('/')[1])))
                
# main ###



lineNr = 2
while cardDict.cell(lineNr,2).value:
    allCards[cardDict.cell(lineNr,1).value] = [cardDict.cell(lineNr,2).value, cardDict.cell(lineNr,3).value, cardDict.cell(lineNr,4).value, cardDict.cell(lineNr,5).value, cardDict.cell(lineNr,6).value, cardDict.cell(lineNr,7).value]
    lineNr +=1
    
P1_deck = []
P1_deviation = [0,0,0,0,0,0,0,0]
P2_deck = []
P2_deviation = [0,0,0,0,0,0,0,0]
lineNr = 2
while decks.cell(lineNr,1).value:
    P1_deck.append(decks.cell(lineNr,1).value.lower())
    
    if not allCards[P1_deck[-1]][2] == '':
        mana = 0
        iter = 0
        while allCards[P1_deck[-1]][2][iter].isdigit() and iter<len(allCards[P1_deck[-1]][2]):
            mana = mana*10+int(allCards[P1_deck[-1]][2][iter])
            iter +=1
        if not allCards[P1_deck[-1]][2][-1].isdigit():
            mana += len(allCards[P1_deck[-1]][2])-iter
        if mana<7:
            P1_deviation[mana]+=1
        else:
            P1_deviation[7]+=1
    else:
        P1_deviation[0] +=1
    
    lineNr +=1
    
lineNr = 2
while decks.cell(lineNr,4).value:
    
    P2_deck.append(decks.cell(lineNr,4).value.lower())
    
    if allCards[P2_deck[-1]][2]:
        mana = 0
        iter = 0
        while allCards[P2_deck[-1]][2][iter].isdigit() and iter<len(allCards[P2_deck[-1]][2]):
            mana = mana*10+int(allCards[P2_deck[-1]][2][iter])
            iter +=1
        if not allCards[P2_deck[-1]][2][-1].isdigit():
            mana += len(allCards[P2_deck[-1]][2])-iter
        if mana<7:
            P2_deviation[mana]+=1
        else:
            P2_deviation[7]+=1
    else:
        P2_deviation[0] +=1
    
    lineNr +=1

for i in range(8):
    decks.update_cell(3+i,3,P1_deviation[i])
    decks.update_cell(3+i,6,P2_deviation[i])

# randomise decks
random.shuffle(P1_deck)
random.shuffle(P2_deck)

# pick out hands
# TODO: make it so that both players can mulligan at the same time
P1_hand = []
P2_hand = []
good = False
ite = 0
while not good:
    for i in range(7-ite):
        P1_hand.append(P1_deck.pop())
    chatSend("mulligan?(yes/no)",1)
    for cardNr in range(len(P1_hand)):
        field.update_cell(3,4+cardNr,P1_hand[cardNr])
    field.update_cell(3,4+len(P1_hand),'')

    if chatGet(1).lower() == 'no':
        good = True
    else:
        for cardNr in range(len(P1_hand)):
            P1_deck.append(P1_hand.pop())
        random.shuffle(P1_deck)
    chatSend('', 1)
    ite +=1

good = False
ite = 0
while not good:
    for i in range(7-ite):
        P2_hand.append(P2_deck.pop())
    chatSend("mulligan?(yes/no)",2)
    for cardNr in range(len(P2_hand)):
        field.update_cell(11,4+cardNr,P2_hand[cardNr])
    field.update_cell(11,4+len(P2_hand),'')
    if chatGet(2).lower() == 'no':
        good = True
    else:
        for cardNr in range(len(P2_hand)):
            P2_deck.append(P2_hand.pop())
        random.shuffle(P2_deck)
    chatSend('', 2)
    ite +=1

# set stats
field.update_cell(2,3,P1_health)
field.update_cell(2,4,P1_energy)
field.update_cell(2,5,P1_mana)
field.update_cell(10,3,P2_health)
field.update_cell(10,4,P2_energy)
field.update_cell(10,5,P2_mana)

print "game setup complete"

# start of game
while not end:
    while field.cell(20,2).value == "SEND" and field.cell(20,4).value == "SEND":
        continue
    if field.cell(20,2).value == '':
        parseText(chatGet(1), 1)
    else:
        parseText(chatGet(2), 2)
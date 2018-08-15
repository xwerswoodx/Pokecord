import os
import os.path
import re
import time
import random
import discord

from discord.ext import commands
from random import randrange
from configparser import ConfigParser
config = ConfigParser()

def getUserFile(nick):
    return 'users\\' + nick.id + '.usr'

def getPokedexFile(nick):
    return 'users\\' + nick.id + '.pkx'

def isMention(text):
    if text.startswith('<@') and text.endswith('>'):
        return 1
    return 0

def getRandomElement(array):
    temp = []
    for elem in array:
        items = elem.split(' ')
        item = items[0]
        time = 1
        if len(items) > 1 and items[1].isnumeric():
            time = int(items[1])

        i = 1
        while i <= time:
            temp.append(item)
            i += 1

    rand = randrange(0,len(temp))
    return temp[rand]

def writeIni(file, section, key, value):
    config.clear()
    config.read(file)
    if not config.has_section(section.title()):
        config.add_section(section.title())

    config.set(section.title(), key.title(), value.title())

    with open(file, 'w') as configfile:
        config.write(configfile)
    config.clear()

def readIni(file, section, key):
    config.clear()
    config.read(file)
    if not config.has_section(section.title()):
        return None
    elif not config.has_option(section.title(), key.title()):
        return None
    return config.get(section.title(), key.title())

def removeIni(file, section, key = None):
    config.clear()
    config.read(file)
    if key == None:
        if config.has_section(section.title()):
            config.remove_section(section.title())
    else:
        if config.has_option(section.title(), key.title()):
            config.remove_option(section.title(), key.title())

    with open(file, 'w') as configfile:
        config.write(configfile)
    config.clear()

def ini(file, section, item = 0):
    config.clear()
    config.read(file)
    if config.has_section(section.title()):
        if item > 0 and item <= len(config.items(section.title())):
            return config.items(section.title())[item - 1][0]
        else:
            return len(config.items(section.title()))
    return 0

def hasIni(file, section, key):
    config.clear()
    config.read(file)
    if config.has_section(section.title()) and config.has_option(section.title(), key.title()):
        return True
    return False

def getExpForLevel(base, level = 1):
    return int(round(base * (1.25 ** (level - 1))))

def getPokemonHp(pokemon, level = 1):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    hp = 0
    if len(temp) > 1:
        hp = int(temp[1])

    return hp * level

def getPokemonMin(pokemon, level = 1):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    dam = 0
    if len(temp) > 2:
        dam = int(temp[2])

    return int(round(dam * (1.25 ** (level - 1))))

def getPokemonMax(pokemon, level = 1):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    dam = 0
    if len(temp) > 3:
        dam = int(temp[3])

    return int(round(dam * (1.25 ** (level - 1))))

def getPokemonRand(pokemon, level = 1):
    return random.randint(getPokemonMin(pokemon, level), getPokemonMax(pokemon, level) + 1)

def getPokemonType(pokemon):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    if len(temp) > 4:
        return temp[4]
    return 'Normal'

def getPokemonExp(pokemon, level = 1):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    exp = 0
    if len(temp) > 5:
        exp = int(temp[5])
    return level * exp

def getPokedexNo(pokemon):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    if len(temp) > 6:
        return int(temp[6])
    return 0

def getPokemonEvo(pokemon):
    temp = read('pokemons.txt', 'r', '(?i)' + pokemon + '\t.+')
    temp = re.split(r'\t+', temp)
    if len(temp) > 7:
        return temp[7]
    return None

def addPokemon(nick, pokemon):
    uid = int(readIni(getUserFile(nick), "General", "Pokedex")) + 1
    write(getPokedexFile(nick), str(uid) + "\t" + pokemon + "\t" + "1" + "\t" + pokemon + "\t" + "0" + "\t" + str(getExpForLevel(50, 1)) + "\t" + str(getPokemonHp(pokemon)) + "\t" + str(getPokemonHp(pokemon)))
    writeIni(getUserFile(nick), "General", "Pokedex", str(uid))
    setMain(nick, uid)

def setMain(nick, uid):
    file = getUserFile(nick)
    pfile = getPokedexFile(nick)
    if hasIni(file, 'Pokemon', 'Pokemon'):
        lineNo = readLine(pfile, 'r', '(?i)' + readIni(file, 'Pokemon', 'Uid') + '\t.+')
        line = read(pfile, str(lineNo))
        line = re.split(r'\t+', line)
        writeLine(pfile, lineNo, line[0] + "\t" + readIni(file, 'Pokemon', 'Pokemon') + "\t" + readIni(file, 'Pokemon', 'Level') + "\t" + readIni(file, 'Pokemon', 'Name') + "\t" + readIni(file, 'Pokemon', 'Exp') + "\t" + readIni(file, 'Pokemon', 'Next') + "\t" + readIni(file, 'Pokemon', 'Hp') + "\t" + readIni(file, 'Pokemon', 'MaxHp'))
    lineNo = readLine(pfile, 'r', '(?i)' + str(uid) + '\t.+')
    line = read(pfile, str(lineNo))
    line = re.split(r'\t+', line)
    writeIni(file, 'Pokemon', 'Pokemon', line[1])
    writeIni(file, 'Pokemon', 'Uid', str(uid))
    writeIni(file, 'Pokemon', 'Level', line[2])
    writeIni(file, 'Pokemon', 'Name', line[3])
    writeIni(file, 'Pokemon', 'Hp', line[6])
    writeIni(file, 'Pokemon', 'MaxHp', line[7])
    writeIni(file, 'Pokemon', 'Exp', line[4])
    writeIni(file, 'Pokemon', 'Next', line[5])

    
def write(file, text):
    f = open(file, 'a')
    f.write(text + "\n")
    f.close()

##def writeLine(file, line, text, insert = False):
##    i = 0
##    with open(file + '.temp', 'w') as t:
##        with open(file) as f:
##            for line in f:
##                i += 1
##                if i == line:
##                    t.write(text)
##                elif not i == line or insert:
##                    t.write(line)
##    os.remove(file)
##    os.rename(file + '.temp', file)
def writeLine(file, line, text, insert = False):
    i = 0
    with open(file, 'r') as f, open(file + '.temp', 'w') as o:
        for ln in f:
            i += 1
            if i == line:
                o.write(text + "\n")
            elif not i == line or insert:
                ln = ln.strip()
                if ln:
                    o.write(ln + "\n")

    os.remove(file)
    os.rename(file + '.temp', file)

def lines(file):
    i = 0
    with open(file, 'r') as f:
        for ln in f:
            i += 1
    return i

def read(file, typ = '1', text = None):
    i = 0
    search = None
    if not text == None:
        search = text
        if typ == 'w':
            search = search.replace('+', '\+')
            search = search.replace('.', '\.')
            search = search.replace('(', '\(')
            search = search.replace(')', '\)')
            search = search.replace('[', '\[')
            search = search.replace(']', '\]')
            search = search.replace('*', '.*')
            search = search.replace('?', '.+')
            search = search.replace(' ', ' +')
            search = '(?i)' + search

    with open(file) as infile:
        for line in infile:
            i += 1
            if typ.isnumeric() and str(i) == typ:
                return line
            elif not search == None and re.match(search, line):
                return line
    return None

def readLine(file, typ = '1', text = None):
    i = 0
    search = None
    if not text == None:
        search = text
        if typ == 'w':
            search = search.replace('+', '\+')
            search = search.replace('.', '\.')
            search = search.replace('(', '\(')
            search = search.replace(')', '\)')
            search = search.replace('[', '\[')
            search = search.replace(']', '\]')
            search = search.replace('*', '.*')
            search = search.replace('?', '.+')
            search = search.replace(' ', ' +')
            search = '(?i)' + search

    with open(file) as infile:
        for line in infile:
            i += 1
            if typ.isnumeric() and str(i) == typ:
                return i
            elif not search == None and re.match(search, line):
                return i
    return 0
            

def hasProfile(nick):
    if os.path.exists('users\\' + nick.id + '.usr'):
        return True
    return False

def createProfile(nick, reset = False):
    if hasProfile(nick) and not reset:
        return
    file = getUserFile(nick)

    #General Section
    writeIni(file, "General", "Hp", "50")
    writeIni(file, "General", "MaxHp", "50")
    writeIni(file, "General", "Exp", "0")
    writeIni(file, "General", "Next", "50")
    writeIni(file, "General", "Level", "1")
    writeIni(file, "General", "Region", "Kanto")
    writeIni(file, "General", "Location", "Pallet Town")
    writeIni(file, "General", "Pokedex", "0")
    writeIni(file, "General", "StatPoints", "5")

    #Pokemon Section
    writeIni(file, "Pokemon", "XpRate", "0")

    #Item Section
    writeIni(file, "Items", "Pokeball", "5")

    #Stat Section
    writeIni(file, "Stats", "Str", "0")
    writeIni(file, "Stats", "Dex", "0")
    writeIni(file, "Stats", "Int", "0")
    writeIni(file, "Stats", "Stam", "0")
    writeIni(file, "Stats", "Hits", "0")
    writeIni(file, "Stats", "Mana", "0")

    #Skill Section
    writeIni(file, "Skills", "PokemonID", "0")
    writeIni(file, "Skills", "PokemonID Cur", "0")
    writeIni(file, "Skills", "PokemonID Max", "20")

    addPokemon(nick, 'Pikachu')

def getDamage(nick):
    file = getUserFile(nick)
    baseMin = 1
    baseMax = 3

    statStr = int(str(int(readIni(file, 'Stats', 'Str')) / 10).split('.')[0])
    baseMin += statStr
    baseMax += statStr

##    if hasIni(file, 'Items', 'Weapon1'):
##    if hasIni(file, 'Items', 'Weapon2'):

    level = int(readIni(file, 'General', 'Level')) - 1
    baseMin += level
    baseMax += level

    return str(baseMin) + '-' + str(baseMax)

def getMinDamage(nick):
    return int(getDamage(nick).split('-')[0])

def getMaxDamage(nick):
    return int(getDamage(nick).split('-')[1])

def getRandomDamage(nick):
    return random.randint(getMinDamage(nick), getMaxDamage(nick) + 1)

def curTime():
    return int(str(time.time()).split('.')[0])

def setTime(nick, timer, seconds):
    time = curTime() + seconds
    writeIni(getUserFile(nick), 'Timers', timer, str(time))

def getTime(nick, timer):
    if hasIni(getUserFile(nick), 'Timers', timer):
        return int(readIni(getUserFile(nick), 'Timers', timer))
    return 0

def getTimeLeft(nick, timer):
    if getTime(nick, timer) == 0:
        return -1
    elif (getTime(nick, timer) - curTime()) < 0:
        return -1
    return getTime(nick, timer) - curTime()

def resetProfile(nick):
    os.remove(getUserFile(nick))
    os.remove(getPokedexFile(nick))
    config.clear()
    createProfile(nick, True)

def hasEnemy(nick):
    if hasIni(getUserFile(nick), 'Enemy', 'Pokemon'):
        return True
    return False

def createEnemy(nick):
    file = getUserFile(nick)
    enemy = getRandomPokemon(nick)
    level = int(readIni(file, 'General', 'Level'))
    levelMin = getMax(level - 2,1)
    levelMax = level + 2
    eLevel = random.randint(levelMin, levelMax + 1)
    writeIni(file, 'Enemy', 'Pokemon', enemy)
    writeIni(file, 'Enemy', 'Hp', str(getPokemonHp(enemy, eLevel)))
    writeIni(file, 'Enemy', 'MaxHp', str(getPokemonHp(enemy, eLevel)))
    writeIni(file, 'Enemy', 'Level', str(eLevel))
    writeIni(file, 'Enemy', 'Region', readIni(file, 'General', 'Region'))
    writeIni(file, 'Enemy', 'Location', readIni(file, 'General', 'Location'))

def createFishEnemy(nick):
    file = getUserFile(nick)
    enemy = getRandomFishPokemon(nick)
    level = int(readIni(file, 'General', 'Level'))
    levelMin = getMax(level - 2,1)
    levelMax = level + 2
    eLevel = random.randint(levelMin, levelMax + 1)
    writeIni(file, 'Enemy', 'Pokemon', enemy)
    writeIni(file, 'Enemy', 'Hp', str(getPokemonHp(enemy, eLevel)))
    writeIni(file, 'Enemy', 'MaxHp', str(getPokemonHp(enemy, eLevel)))
    writeIni(file, 'Enemy', 'Level', str(eLevel))
    writeIni(file, 'Enemy', 'Region', readIni(file, 'General', 'Region'))
    writeIni(file, 'Enemy', 'Location', readIni(file, 'General', 'Location'))    

def getMax(v1, v2):
    if v1 >= v2:
        return v1
    return v2

def removeEnemy(nick):
    file = getUserFile(nick)
    removeIni(file, 'Enemy')

def canAdventureUser(nick, fish = False):
    file = getUserFile(nick)
    if fish:
        return canAdventureFish(readIni(file, 'General', 'Region'), readIni(file, 'General', 'Location'))
    else:
        return canAdventure(readIni(file, 'General', 'Region'), readIni(file, 'General', 'Location'))

def canAdventure(region, location):
    file = 'map\\' + region + '.map'
    if ini(file, location, 0) > 0:
        return True
    return False

def canAdventureFish(region, location):
    file = 'map\\' + region + '.map'
    if ini(file, location + ' Fish', 0) > 0:
        return True
    return False
    
def getRandomPokemon(nick):
    file = getUserFile(nick)
    region = readIni(file, 'General', 'Region')
    location = readIni(file, 'General', 'Location')
    mfile = 'map\\' + region + '.map'
    array = []
    if ini(mfile, location, 0) > 0:
        pokes = ini(mfile, location, 0)
        i = 1
        while i <= pokes:
            poke = ini(mfile, location, i)
            chance = readIni(mfile, location, poke)
            array.append(poke + ' ' + chance)
            i += 1

        if len(array) > 0:
            return getRandomElement(array)
    return None

def getRandomFishPokemon(nick):
    file = getUserFile(nick)
    region = readIni(file, 'General', 'Region')
    location = readIni(file, 'General', 'Location')
    mfile = 'map\\' + region + '.map'
    array = []
    if ini(mfile, location + ' Fish', 0) > 0:
        pokes = ini(mfile, location + ' Fish', 0)
        i = 1
        while i <= pokes:
            poke = ini(mfile, location + ' Fish', i)
            chance = readIni(mfile, location + ' Fish', poke)
            array.append(poke + ' ' + chance)
            i += 1

        if len(array) > 0:
            return getRandomElement(array)
    return None

def getDamageMultiplier(attacker, defender):
    aTypes = getPokemonType(attacker).split('|')
    dTypes = getPokemonType(defender).split('|')
    mul = 1

    i = 1
    while i <= len(aTypes):
        aType = aTypes[i - 1]
        x = 1
        while x <= len(dTypes):
            dType = dTypes[x - 1]
            temp = readType(aType, dType)
            mul = mul * temp
            x += 1
        i += 1
    return mul

def readType(attackerType, defenderType):
    if hasIni('types.ini', attackerType, defenderType):
        return float(readIni('types.ini', attackerType, defenderType))
    return 1

def addSkillPoint(nick, skill, amount = 1):
    file = getUserFile(nick)
    cur = int(readIni(file, 'Skills', skill + ' cur')) + amount
    req = int(readIni(file, 'Skills', skill + ' max'))
    lvl = int(readIni(file, 'Skills', skill))

    while cur >= req:
        lvl += 1
        cur -= req
        req = getExpForLevel(20, lvl + 1)

    writeIni(file, 'Skills', skill, str(lvl))
    writeIni(file, 'Skills', skill + ' cur', str(cur))
    writeIni(file, 'Skills', skill + ' max', str(req))

def addGold(nick, amount):
    file = getUserFile(nick)
    gold = 0
    if hasIni(file, 'General', 'Gold'):
        gold = int(readIni(file, 'General', 'Gold'))
    gold += amount
    writeIni(file, 'General', 'Gold', str(gold))

def addPokedex(nick):
    file = getUserFile(nick)
    pfile = getPokedexFile(nick)
    
    uid = int(readIni(file, 'Pokemon', 'Uid'))
    lineNo = readLine(pfile, 'r', '(?i)' + str(uid) + '\t.+')
    line = read(pfile, str(lineNo))
    line = re.split(r'\t+', line)
    writeLine(pfile, lineNo, line[0] + "\t" + readIni(file, 'Pokemon', 'Pokemon') + "\t" + readIni(file, 'Pokemon', 'Level') + "\t" + readIni(file, 'Pokemon', 'Name') + "\t" + readIni(file, 'Pokemon', 'Exp') + "\t" + readIni(file, 'Pokemon', 'Next') + "\t" + readIni(file, 'Pokemon', 'Hp') + "\t" + readIni(file, 'Pokemon', 'MaxHp'))

def addEnemyPokedex(nick):
    file = getUserFile(nick)
    pfile = getPokedexFile(nick)

    pokedex = int(readIni(file, 'General', 'Pokedex')) + 1
    enemy = readIni(file, 'Enemy', 'Pokemon')
    level = int(readIni(file, 'Enemy', 'Level'))
    write(pfile, str(pokedex) + "\t" + enemy + "\t" + str(level) + "\t" + enemy + "\t0\t" + str(getExpForLevel(50, level)) + "\t" + str(getPokemonHp(enemy, level)) + "\t" + str(getPokemonHp(enemy, level)))
    removeEnemy(nick)
    writeIni(file, 'General', 'Pokedex', str(pokedex))
    return pokedex

def hasPokeball(nick):
    if int(readIni(getUserFile(nick), 'Items', 'Pokeball')) > 0:
        return True
    return False

def isNpc(nick):
    if readIni(getUserFile(nick), 'Enemy', 'Npc') == 'True':
        return True
    False

def getEnd(nick, typ):
    result = '!==================='
    i = 1
    while i <= len(nick.name):
        result = result + '='
        i += 1
    result = result + '='
    i = 1
    while i <= len(typ):
        result = result + '='
        i += 1
    result = result + '===================!'
    return result

def isValidUid(nick, uid):
    file = getPokedexFile(nick)
    if read(file, 'r', '(?i)' + str(uid) + '\t.+') == None:
        return False
    return True

def pokemonHasName(nick):
    file = getUserFile(nick)
    if not readIni(file, 'Pokemon', 'Pokemon') == readIni(file, 'Pokemon', 'Name'):
        return True
    return False

def pokemonHasTag(nick):
    file = getUserFile(nick)
    if not readIni(file, 'Pokemon', 'Tag') == None:
        return True
    return False

def getPokemonTag(nick):
    file = getUserFile(nick)
    if pokemonHasTag(nick):
        return readIni(file, 'Pokemon', 'Tag')
    return None

def getPokemonName(nick):
    file = getUserFile(nick)
    name = readIni(file, 'Pokemon', 'Pokemon')
    if pokemonHasName(nick):
        name = readIni(file, 'Pokemon', 'Name')

    if pokemonHasTag(nick):
        return getPokemonTag(nick) + ' ' + name
    return name

def isValidLocation(nick, loc):
    file = getUserFile(nick)
    r = readIni(file, 'General', 'Region')
    l = readIni(file, 'General', 'Location')
    if not readIni('map\\' + r + '.map', l + ' Travel', loc) == None:
        return True
    return False

def addInfo(nick, info, amount = 1):
    file = getUserFile(nick)
    current = 0
    if hasIni(file, 'General', info):
        current = int(readIni(file, 'General', info))
    current += amount
    writeIni(file, 'General', info, str(current))

def getInfo(nick, info):
    file = getUserFile(nick)
    if hasIni(file, 'General', info):
        return int(readIni(file, 'General', info))
    return 0

def getProcessBar(nick, percentage, box = 10):
    file = getUserFile(nick)
    typ = 1
    if hasIni(file, 'Settings', 'Pbar'):
        typ = int(readIni(file, 'Settings', 'Pbar'))
    
    amount = int(round((percentage * box) / 100))
    result = ''
    i = 1
    while i <= amount:
        if typ == 1:
            result = result + '⬜'
        else:
            result = result + '⬛'
        i += 1
    d = box - amount
    while d > 0:
        if typ == 1:
            result = result + '⬛'
        else:
            result = result + '⬜'
        d -= 1
    return result


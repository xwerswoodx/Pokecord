import discord
import re
import time
import random

from discord.ext import commands
from header_pokecord import *

TOKEN = 'NDc4NzA0OTM5Mjg4MzYzMDE5.DlOkfw.dJ455eAXaZyT2KxU8H-xzNHX2Og'
bot = commands.Bot(command_prefix = '!')
#test = getRandomElement(["Test 1", "Test2 2"])

@bot.event
async def on_ready():
    print('Connected.')

@bot.event
async def on_message(message):
    user = message.author
    msg = message.content.split()
    chan = message.channel

    if len(msg) < 1:
        return
    
    if re.match(r'(?i)[!.].+', msg[0]) and not hasProfile(user):
        createProfile(user)

    if re.match(r'(?i)[!.](m(acera|)|adv(enture|))$', msg[0]):
        if getTimeLeft(user, 'adventure') >= 0:
            await bot.send_message(chan, 'You need to wait ' + str(getTimeLeft(user, 'adventure')) + ' seconds more to use this command again.')
            return
        else:
            setTime(user, 'adventure', 5)

        if not canAdventureUser(user):
            await bot.send_message(chan, 'You can\'t adventure here.')
            return

        if len(msg) > 1 and msg[1] == '1':
            removeEnemy(user)
        else:
            file = getUserFile(user)
            if int(readIni(file, 'General', 'Hp')) <= 0 or int(readIni(file, 'Pokemon', 'Hp')) <= 0:
                await bot.send_message(chan, 'You have to heal yourself and your pokemon to continue adventure.')
                return

            encounter = False
            if not hasEnemy(user) or int(readIni(file, 'Enemy', 'Hp')) <= 0 or not readIni(file, 'Enemy', 'Region') == readIni(file, 'General', 'Region') or not readIni(file, 'Enemy', 'Location') == readIni(file, 'General', 'Location'):
                createEnemy(user)
                encounter = True

            damage = getRandomDamage(user)
            level = int(readIni(file, 'General', 'Level'))
            hp = int(readIni(file, 'General', 'Hp'))
            maxHp = int(readIni(file, 'General', 'MaxHp'))

            enemy = readIni(file, 'Enemy', 'Pokemon')
            critical = 1
            if random.randint(1, 101) == 1:
                critical = 2
                statInt = int(str(int(readIni(file, 'Stats', 'Int')) / 200).split('.')[0])
                critical += statInt
            damage = damage * critical

            pokemon = readIni(file, 'Pokemon', 'Pokemon')
            pokemonLevel = int(readIni(file, 'Pokemon', 'Level'))
            pokemonDamage = getPokemonRand(pokemon, pokemonLevel)
            pokemonDamage += int(readIni(file, 'Skills', 'PokemonID')) #Pokemon ID skill bonus
            pokemonDamage = int(round(pokemonDamage * getDamageMultiplier(pokemon, enemy))) #Type Compare
            pokemonHp = int(readIni(file, 'Pokemon', 'Hp'))
            pokemonMaxHp = int(readIni(file, 'Pokemon', 'MaxHp'))

            times = 1 + int(str(int(readIni(file, 'Stats', 'Dex')) / 250).split('.')[0])
            damage = damage * times

            enemyLevel = int(readIni(file, 'Enemy', 'Level'))
            enemyHp = int(readIni(file, 'Enemy', 'Hp'))
            enemyMaxHp = int(readIni(file, 'Enemy', 'MaxHp'))
            enemyDamage = getPokemonRand(enemy, enemyLevel)
            enemyCritical = 1
            if random.randint(1, 101) == 1:
                enemyCritical = 2
            enemyDamage = enemyDamage * enemyCritical

            if pokemonHp <= 0:
                pokemonDamage = 0

            enemyPokemonDamage = int(round(enemyDamage * getDamageMultiplier(enemy, pokemon)))

            hp = getMax(hp - enemyDamage, 0)
            pokemonHp = getMax(pokemonHp - enemyPokemonDamage, 0)
            enemyHp = getMax(enemyHp - damage - pokemonDamage, 0)

            writeIni(file, 'General', 'Hp', str(hp))
            writeIni(file, 'Pokemon', 'Hp', str(pokemonHp))
            writeIni(file, 'Enemy', 'Hp', str(enemyHp))

            result = 0
            if enemyHp <= 0:
                result = 1
            elif hp <= 0:
                result = 2

            if result == 1:
                addSkillPoint(user, 'PokemonID')
                expMin = getMax(enemyLevel -1, 1)
                expMax = enemyLevel + 1
                enemyExp = getPokemonExp(enemy) * random.randint(expMin, expMax + 1)
                exp = int(readIni(file, 'General', 'Exp'))
                pokemonExp = 0
                if int(readIni(file, 'Pokemon', 'XpRate')) > 0:
                    pokemonRate = int(readIni(file, 'Pokemon', 'XpRate'))
                    if pokemonRate > 100:
                        pokemonRate = 100
                        writeIni(readIni(file, 'Pokemon', 'XpRate', '100'))
                    pokemonExp = (enemyExp * pokemonRate) / 100
                    enemyExp = enemyExp - pokemonExp
                    pokemonExp = int(round(pokemonExp))
                    enemyExp = int(round(enemyExp))
                    pokemonCur = int(readIni(file, 'Pokemon', 'Exp'))
                    pokemonCur += pokemonExp
                    writeIni(file, 'Pokemon', 'Exp', str(pokemonCur))
                exp += enemyExp
                writeIni(file, 'General', 'Exp', str(exp))
                gold = 5 + level + random.randint(expMin, expMax + 1)
                addGold(user, gold)
                    

            msg = '!=================[ ' + user.name + ' Adventure ]=================!\n'
            if encounter:
                msg = msg + '% You have encountered level ' + str(enemyLevel) + ' wild ' + enemy + '\n'
            if enemyCritical > 1:
                msg = msg + '- Critical Damage!\n'
            msg = msg + '- You lost ' + str(enemyDamage) + ' health.\n'
            if critical > 1:
                msg = msg + '+ Critical Damage!\n'
            msg = msg + '+ You dealth ' + str(damage) + ' damage.\n'
            msg = msg + '- ' + pokemon + ' lost ' + str(enemyPokemonDamage) + ' health.\n'
            msg = msg + '+ ' + pokemon + ' dealth ' + str(pokemonDamage) + ' damage.\n'
            if pokemonHp > ((pokemonMaxHp * 25) / 100):
                msg = msg + '+ ' + pokemon + ' has ' + str(pokemonHp) + '/' + str(pokemonMaxHp) + ' health left.\n'
            else:
                msg = msg + '- ' + pokemon + ' has ' + str(pokemonHp) + '/' + str(pokemonMaxHp) + ' health left.\n'

            if hp > ((maxHp * 25) / 100):
                msg = msg + '+ You have ' + str(hp) + '/' + str(maxHp) + ' health left.\n'
            else:
                msg = msg + '- You have ' + str(hp) + '/' + str(maxHp) + ' health left.\n'

            msg = msg + '+ Enemy ' + enemy + ' has ' + str(enemyHp) + '/' + str(enemyMaxHp) + ' health left.\n'

            if result == 1:
                msg = msg + '+ You defeated level ' + str(enemyLevel) + ' wild ' + enemy + ' and earned ' + str(gold) + ' gold and ' + str(enemyExp) + ' experience points.\n'
                curExp = int(readIni(file, 'General', 'Exp'))
                reqExp = int(readIni(file, 'General', 'Next'))
                curHp = int(readIni(file, 'General', 'MaxHp'))
                levelUp = False
                while curExp >= reqExp:
                    level += 1
                    curHp += 50
                    curExp -= reqExp
                    reqExp = getExpForLevel(50, level)
                    levelUp = True
                writeIni(file, 'General', 'Level', str(level))
                writeIni(file, 'General', 'Exp', str(curExp))
                writeIni(file, 'General', 'Next', str(reqExp))
                writeIni(file, 'General', 'Hp', str(curHp))
                writeIni(file, 'General', 'MaxHp', str(curHp))
                if levelUp:
                    msg = msg + '% You have leveled up and earned 5 stat points!\n'
                
                if pokemonExp > 0:
                    msg = msg + '+ ' + pokemon + ' earned ' + str(pokemonExp) + ' experience points.\n'
                    curPokemonExp = int(readIni(file, 'Pokemon', 'Exp'))
                    reqPokemonExp = int(readIni(file, 'Pokemon', 'Next'))
                    curPokemonHp = int(readIni(file, 'Pokemon', 'MaxHp'))
                    pokemonLevelUp = False
                    pokemonEvolve = False
                    while curPokemonExp >= reqPokemonExp:
                        pokemonLevel += 1
                        curPokemonHp += getPokemonHp(pokemon, 1)
                        curPokemonExp -= reqPokemonExp
                        reqPokemonExp = getExpForLevel(50, pokemonLevel)
                        pokemonLevelUp = True
                        pokemonEvo = getPokemonEvo(pokemon)
                        if not pokemonEvo == 'null' and re.match(r'(?i).+@.+', pokemonEvo):
                            evos = pokemonEvo.split('|')
                            i = 1
                            while i <= len(evos):
                                evo = evos[i - 1]
                                evoPoke = evo.split('@')[0]
                                evoType = evo.split('@')[1].split(':')[0]
                                if evoType == 'Level':
                                    evoLevel = int(evo.split('@')[1].split(':')[1])
                                    if pokemonLevel >= evoLevel:
                                        pokemonEvolved = pokemon
                                        pokemon = evoPoke
                                        writeIni(file, 'Pokemon', 'Pokemon', evoPoke)
                                        writeIni(file, 'Pokemon', 'Name', evoPoke)
                                        writeIni(file, 'Pokemon', 'Exp', str(curPokemonExp))
                                        writeIni(file, 'Pokemon', 'Next', str(reqPokemonExp))
                                        writeIni(file, 'Pokemon', 'Hp', str(curPokemonHp))
                                        writeIni(file, 'Pokemon', 'MaxHp', str(curPokemonHp))
                                        addPokedex(user)
                                        pokemonEvolve = True
                                i += 1

                    writeIni(file, 'Pokemon', 'Level', str(pokemonLevel))
                    writeIni(file, 'Pokemon', 'Exp', str(curPokemonExp))
                    writeIni(file, 'Pokemon', 'Next', str(reqPokemonExp))
                    writeIni(file, 'Pokemon', 'Hp', str(curPokemonHp))
                    writeIni(file, 'Pokemon', 'MaxHp', str(curPokemonHp))
                    if pokemonLevelUp and not pokemonEvolve:
                        msg = msg + '+ ' + pokemon + ' leveled up!\n'
                    elif pokemonEvolve:
                        msg = msg + '+ ' + pokemonEvolved + ' leveled up and evolved into ' + pokemon + '!\n'
                    
                                            
            elif result == 2:
                msg = msg + '- You have defeated by level ' + str(enemyLevel) + ' wild ' + enemy + '\n'                
            msg = msg + getEnd(user, 'Adventure') + '\n' #'!=================[ ' + user.name + ' Adventure ]=================!\n'

            await bot.send_message(chan, '```diff\n' + msg + '```')
            addPokedex(user)
            if enemyHp > 0:
                await bot.send_message(chan, 'Type `.adv` to continue or `.run` to run away.')
            else:
                await bot.send_message(chan, 'Type `.catch` to catch pokemon.')

    elif re.match(r'(?i)[!.](run|ayr[iİı]l)$', msg[0]):
        await bot.send_message(chan, 'You have run away from level ' + readIni(getUserFile(user), 'Enemy', 'Level') + ' wild ' + readIni(getUserFile(user), 'Enemy', 'Pokemon') + '.')
        removeEnemy(user)
    elif re.match(r'(?i)[!.](b[iİı]lg[iİı]|info)', msg[0]):
        if getTimeLeft(user, 'info') >= 0:
            await bot.send_message(chan, 'You need to wait ' + str(getTimeLeft(user, 'info')) + ' seconds more to use this command again.')
            return
        else:
            setTime(user, 'info', 15)

        nick = user
        if len(msg) > 1 and isMention(msg[1]) == 1:
            nick = message.mentions[0]

        file = getUserFile(nick)
        cur = int(readIni(file, 'General', 'Exp'))
        req = int(readIni(file, 'General', 'Next'))
        perc = int(round((cur * 100) / req))

        pcur = int(readIni(file, 'Pokemon', 'Exp'))
        preq = int(readIni(file, 'Pokemon', 'Next'))
        pperc = int(round((pcur * 100) / preq))

        pokemon = readIni(file, 'Pokemon', 'Pokemon')
        pokemonLevel = int(readIni(file, 'Pokemon', 'Level'))
        pokemonId = int(readIni(file, 'Skills', 'PokemonID')) #Pokemon ID skill bonus
        
        
        await bot.send_message(chan, '```diff\n\
!=================[ ' + nick.name + ' Info ]=================!\n\
+ Level: ' + readIni(file, 'General', 'Level') + ' [' + str(cur) + '/' + str(req) + 'XP (' + str(perc) + '%)]' + '\n\
+ Damage: ' + getDamage(nick) + '\n\
+ Gold: ' + '{:,.0f}PG'.format(int(readIni(file, 'General', 'Gold'))) + '\n\
+ Weapon:\n\
+ Pokemon: ' + readIni(file, 'Pokemon', 'Pokemon') + '\n\
+ Pokemon Level: ' + readIni(file, 'Pokemon', 'Level') + ' [' + str(pcur) + '/' + str(preq) + 'XP (' + str(pperc) + '%)]' + '\n\
+ Pokemon Damage: ' + str(getPokemonMin(pokemon, pokemonLevel)) + '-' + str(getPokemonMax(pokemon, pokemonLevel)) + ' [+' + str(pokemonId) + ' from pokemonID]\n\
' + getEnd(nick, 'Info') + '\n\
```')

    elif re.match(r'(?i)[!.](catch|yakala)$', msg[0]):
        if getTimeLeft(user, 'catch') >= 0:
            await bot.send_message(chan, 'You need to wait ' + str(getTimeLeft(user, 'catch')) + ' seconds more to use this command again.')
            return
        else:
            setTime(user, 'catch', 5)
            
        file = getUserFile(user)
        if not hasEnemy(user):
            await bot.send_message(chan, 'There is no pokemon to catch!')
            return
        elif int(readIni(file, 'Enemy', 'Hp')) > 0:
            await bot.send_message(chan, 'You need to win against ' + readIni(file, 'Enemy', 'Pokemon') + ' to catch it.')
            return
        elif not hasPokeball(user):
            await bot.send_message(chan, 'You need pokeball catch pokemon!')
            return
        elif isNpc(user):
            await bot.send_message(chan, 'You can\'t catch pokemons in this battle.')
            return
        pokeball = int(readIni(file, 'Items', 'Pokeball')) - 1
        writeIni(file, 'Items', 'Pokeball', str(pokeball))
        enemyPokemon = readIni(file, 'Enemy', 'Pokemon')
        enemyLevel = readIni(file, 'Enemy', 'Level')
        pkx = addEnemyPokedex(user)
        await bot.send_message(chan, 'You caught level ' + enemyLevel + ' wild pokemon ' + enemyPokemon + ' and it added to your pokedex. To make it your main pokemon, use `!pokemon ' + str(pkx) + '`.')

    elif re.match(r'(?i)[!.]test', msg[0]):
        await bot.send_message(chan, '{}'.format(getDamageMultiplier('Charmander', 'Squirtle')))

    elif re.match(r'(?i)[!.]skills', msg[0]):
        if getTimeLeft(user, 'skills') >= 0:
            await bot.send_message(chan, 'You need to wait ' + str(getTimeLeft(user, 'skills')) + ' seconds more to use this command again.')
            return
        else:
            setTime(user, 'skills', 10)

        nick = user
        if len(msg) > 1 and isMention(msg[1]) == 1:
            nick = message.mentions[0]

        file = getUserFile(nick)
        pokemonId = readIni(file, 'Skills', 'PokemonID')
        pokemonId_Cur = readIni(file, 'Skills', 'PokemonID cur')
        pokemonId_Req = readIni(file, 'Skills', 'PokemonID max')
        await bot.send_message(chan, '```diff\n\
+ Pokemon Identification: ' + pokemonId + ' [' + pokemonId_Cur + '/' + pokemonId_Req + ' XP]\n\
```')

    elif re.match(r'(?i)[!.]reset', msg[0]):
        if getTimeLeft(user, 'Reset') >= 0:
            print('{}'.format(getTimeLeft(user, 'Reset')))
            resetProfile(user)
            await bot.send_message(chan, 'Your profile has been reset.')
        else:
            setTime(user, 'Reset', 60)
            await bot.send_message(chan, 'Are you sure to reset your profile? Type `!reset` again in 60 seconds to reset your character.')

    elif re.match(r'(?i)[!.]pheal$', msg[0]):
        file = getUserFile(user)
        writeIni(file, 'Pokemon', 'Hp', readIni(file, 'Pokemon', 'MaxHp'))
        await bot.send_message(chan, 'You have healed your pokemon ' + readIni(file, 'Pokemon', 'Pokemon') + '.')
    elif re.match(r'(?i)[!.]heal$', msg[0]):
        file = getUserFile(user)
        writeIni(file, 'General', 'Hp', readIni(file, 'General', 'MaxHp'))
        await bot.send_message(chan, 'You have healed yourself.')
    elif re.match(r'(?i)[!.]map$', msg[0]):
        file = getUserFile(user)
        region = readIni(file, 'General', 'Region')
        if region == 'Kanto':
            await bot.send_message(chan, 'https://img00.deviantart.net/8538/i/2011/080/9/b/labeled_map_of_kanto_by_rythos-d3c4hsg.png')    



bot.run(TOKEN)

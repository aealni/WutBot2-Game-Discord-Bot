import asyncio
import json
import os
import random

import discord

import jsonpickle

# Simple script to set the working directory to the script path
print("Original working directory: " + os.getcwd())
sep = str(os.path.sep)
cdirpath = os.path.realpath(__file__).removesuffix(sep + "altereignModule.py")
os.chdir(cdirpath)
print("New working directory: " + os.getcwd())

# Establishing databases
areaDict = {}
enemyDict = {}
itemDict = {}


# The Area object administrates a dictionary of Enemies it contains
# Note: classes we want to convert to json using jsonpickle must inherit from object, won't work otherwise
class Area(object):

  def __init__(self, pname):
    self.name = pname
    self.description = ""
    self.enemies = []

  # Attempts to add an Enemy object to this Area's dictionary
  # Returns a string indicating whether the operation was successful
  def addEnemy(self, enemyname):
    if enemyname in self.enemies: return "Enemy already present in this Area."
    self.enemies.append(enemyname)
    return (enemyname + " successfully added to " + self.name + ".")

  # Attempts to remove an enemy from this Area's dictionary
  # Returns a string indicating whether the operation was successful
  def removeEnemy(self, enemyname):
    if enemyname in self.enemies:
      self.enemies.remove(enemyname)
      return (enemyname + " successfully removed from " + self.name + ".")
    else:
      return "Enemy not present in this Area."

  # Returns a random Enemy object from this Area's enemy dictionary
  # TODO: Assign weights to enemies so there can be 'rare encounters'
  def getRandomEncounter(self):
    if len(self.enemies) > 0:
      return self.enemies[random.randint(0, len(self.enemies) - 1)]
    else:
      return None


# Enemy object
class Enemy(object):

  # Constructor
  def __init__(self, name, health, defense, level, exp, gold, drops):
    self.name = name
    self.health = health
    self.defense = defense
    self.level = level
    self.exp = exp
    self.gold = int(gold)
    self.nodes = []
    # itemdrops is a list of dictionaries, every dictionary following the format of {"name":[item name], "amount":[drop amount], "chance":[drop chance]}
    self.itemdrops = drops

  def addNode(self, pnode):
    self.nodes.append(pnode)

  # returns [action description, damage dealt, following node]
  def getNodeAction(self, pnode):
    self.action = self.nodes[pnode].getBehaviour
    print(self.action()[2])
    # attack = int(self.action()[1])
    print(self.action()[0])
    return self.action()[0], self.action()[1], self.action()[2]

  class Node():

    # Constructor
    def __init__(self, pdesc, dmgRange, damagetype):
      # Writes this nodes' description
      self.description = pdesc
      self.damagetype = damagetype
      # Splits the damage range into minimum and maximum damage for ease of calculation
      self.mindmg = int(dmgRange.split("-")[0])
      self.maxdmg = int(dmgRange.split("-")[1])
      # Initialises transfer list
      self.transfers = []
      self.probabilities = []

    # Function the parent calls to add nodes that this node can transfer to
    def addTransfer(self, pnode, probability):
      # Adds first the index of the transfer, then its probability
      self.transfers.append(pnode)
      self.probabilities.append(probability)

    # Function called in a fight that determines how much damage is dealt and which node is transferred to
    def getBehaviour(self):
      # Now this part is somewhat interesting
      # Instead of using a native probability weight system (or that horribly large one from StackOverflow)
      # I decided to make a very simple one myself

      # Edit: It works! As far as I can tell.
      # And it's half as many lines as the one from StackOverflow
      # I am a fucking god

      # You could actually use the NumPy library and do it in a single line, but fuck that

      # Anyway, the probability engine
      self.hitrange = 100
      self.counter = 0
      while self.hitrange > 0:
        if random.randint(1,
                          self.hitrange) <= self.probabilities[self.counter]:
          break
        else:
          self.hitrange -= self.probabilities[self.counter]
          self.counter += 1
      return self.description, random.randint(
        self.mindmg, self.maxdmg), self.transfers[self.counter]


#####################################################################
# Initialising databases
async def on_ready(client):
  #Loading area database
  global firstexplore
  firstexplore = True
  #TODO: Check validity of enemy references in area objects
  with open("areadict.json", "r") as f:
    global areaDict
    areaDict = jsonpickle.decode(f.read())
  #Loading enemy database
  with open("enemies.json", "r") as f:
    global enemyDict
    enemyDict = jsonpickle.decode(f.read())
  #Loading item database
  #TODO: Check validity of item references in enemy database
  with open("items.json", "r") as f:
    global itemDict
    itemDict = jsonpickle.decode(f.read())
  print("Ready")


def byAdmin(ctx):
  return (ctx.author.id == 346249795582820352) or (
    ctx.author.id == 282444563023659008) or (ctx.author.id
                                             == 384736698594230273)


def byContentMod(ctx):
  return (ctx.author.id == 187930211617210368)


async def profile(client, ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_accounts_data()
  health_amt = users[str(user.id)]["health"]
  def_amt = users[str(user.id)]["defense"]
  mindmg_amt = users[str(user.id)]["mindmg"]
  maxdmg_amt = users[str(user.id)]["maxdmg"]
  gold_amt = users[str(user.id)]["gold"]
  level_amt = users[str(user.id)]["level"]
  exp_amt = users[str(user.id)]["exp"]
  current_area = users[str(user.id)]["area"]
  helmet = users[str(user.id)]["helmet"]
  chest = users[str(user.id)]["chest"]
  pants = users[str(user.id)]["pants"]
  boots = users[str(user.id)]["boots"]
  necklace = users[str(user.id)]["necklace"]
  ring = users[str(user.id)]["ring"]
  cape = users[str(user.id)]["cape"]
  weapon = users[str(user.id)]["weapon"]

  health_amt = users[str(user.id)]["health"]

  while users[str(user.id)]["exp"] >= (users[str(
      user.id)]["level"]**3.3) + (13) - (users[str(user.id)]["level"]):
    users[str(user.id)]["health"] += 6
    users[str(user.id)]["mindmg"] += 1
    users[str(user.id)]["maxdmg"] = round(users[str(user.id)]["mindmg"] * 1.5)
    users[str(user.id)]["level"] += 1

    j = json.dumps(users, indent=2)
    with open("accounts.json", "w") as f:
      f.write(j)
      f.close()

  stat_page_1 = discord.Embed(title=f"{ctx.author.name}'s Stats",
                              colour=discord.Colour.default())
  stat_page_1.add_field(name="**Health**", value=health_amt)
  stat_page_1.add_field(name="**Min Damage**", value=mindmg_amt)
  stat_page_1.add_field(name="**Max Damage**", value=maxdmg_amt)
  stat_page_1.add_field(name="**Defense**", value=def_amt)
  stat_page_1.add_field(name="**Level**", value=level_amt)
  stat_page_1.add_field(name="**Exp**", value=exp_amt)
  stat_page_1.add_field(name="**Gold**", value=gold_amt)
  stat_page_1.add_field(name="**Area**", value=current_area)
  stat_page_1.add_field(name="**Class**", value=users[str(user.id)]["class"])

  stat_page_2 = discord.Embed(title=f"{ctx.author.name}'s Equipment",
                              colour=discord.Colour.default())
  stat_page_2.add_field(name="**Helmet**", value=helmet)
  stat_page_2.add_field(name="**Chest**", value=chest)
  stat_page_2.add_field(name="**Pants**", value=pants)
  stat_page_2.add_field(name="**Boots**", value=boots)
  stat_page_2.add_field(name="**Necklace**", value=necklace)
  stat_page_2.add_field(name="**Ring**", value=ring)
  stat_page_2.add_field(name="**Cape**", value=cape)
  stat_page_2.add_field(name="**Weapon**", value=weapon)

  buttons = ["⬅️", "➡️"]
  current = stat_page_1
  msg = await ctx.send(embed=current)

  for button in buttons:
    await msg.add_reaction(button)
  while True:
    try:
      reaction, user = await client.wait_for(
        "reaction_add",
        check=lambda reaction, user: user == ctx.author and reaction.message ==
        msg and reaction.emoji in buttons,
        timeout=30.0)

    except asyncio.TimeoutError:
      embed = current
      embed.set_footer(text="Timed out.")
      await msg.clear_reactions()

    else:
      previous_page = current
      if reaction.emoji == "➡️":
        current = stat_page_2
        await msg.edit(embed=current)

      for button in buttons:
        await msg.remove_reaction(button, ctx.author)

      if current != previous_page:
        await msg.edit(embed=current)

      elif reaction.emoji == "⬅️":
        current = stat_page_1
        await msg.edit(embed=current)

      for button in buttons:
        await msg.remove_reaction(button, ctx.author)

      if current != previous_page:
        await msg.edit(embed=current)


profile.triggers = ["profile", "p"]


# create acc
async def open_account(user):

  users = await get_accounts_data()

  if str(user.id) in users:
    return False
  else:
    users[str(user.id)] = {}
    users[str(user.id)]["health"] = 30
    users[str(user.id)]["battlehealth"] = 30
    users[str(user.id)]["defense"] = 0
    users[str(user.id)]["mindmg"] = 3
    users[str(user.id)]["maxdmg"] = 5
    users[str(user.id)]["gold"] = 0
    users[str(user.id)]["level"] = 1
    users[str(user.id)]["exp"] = 0
    users[str(user.id)]["trust"] = 0
    users[str(user.id)]["party"] = []
    users[str(user.id)]["area"] = "Altereign"
    users[str(user.id)]["class"] = "default"
    users[str(user.id)]["cmd_use"] = 0
    users[str(user.id)]["cmd_in_use"] = 0
    users[str(user.id)]["helmet"] = "nothing"
    users[str(user.id)]["chest"] = "nothing"
    users[str(user.id)]["pants"] = "nothing"
    users[str(user.id)]["boots"] = "nothing"
    users[str(user.id)]["necklace"] = "nothing"
    users[str(user.id)]["ring"] = "nothing"
    users[str(user.id)]["cape"] = "nothing"
    users[str(user.id)]["weapon"] = "nothing"
    users[str(user.id)]["inventory"] = {}
    users[str(user.id)]["knownitems"] = []

    j = json.dumps(users, indent=2)
    with open("accounts.json", "w") as f:
      f.write(j)
      f.close()
  return True


# Returns user data as a dictionary, key being the user ID and value being a dictionary of account attributes
async def get_accounts_data():
  with open("accounts.json", "r") as f:
    users = json.load(f)

  return users


async def get_items_data():
  with open("items.json", "r") as f:
    items = json.load(f)

  return items


#Check item stats within discord using !item [itemname]
#TODO: This command should be replaced by a more expansive command with the same functionality, and removed when done
"""@client.command()
async def iteminfo(ctx):
    item1 = ctx.message.content.removeprefix("!iteminfo ")
    item = item1
    items = await get_items_data()
    item_name = items[str(item)]["name"]
    showitem = discord.Embed(title=f"{item_name}", colour=discord.Colour.default())
    showitem.add_field(name=f"**Health bonus:**", value= items[str(item)]["healthbonus"], inline = False)
    showitem.add_field(name=f"**Minimum damage bonus:**", value= items[str(item)]["mindamagebonus"], inline = False)
    showitem.add_field(name=f"**Maximum damage bonus:**", value= items[str(item)]["maxdamagebonus"], inline = False)
    showitem.add_field(name=f"**Item level:**", value= items[str(item)]["level"], inline = False)
    showitem.add_field(name=f"**Class:**", value= items[str(item)]["class"], inline = False)
    showitem.add_field(name=f"**Equipment slot:**", value= items[str(item)]["slot"], inline = False)
    msg = await ctx.send(embed = showitem)"""


async def unequip(client, ctx):
  await open_account(ctx.author)
  item1 = ctx.message.content.removeprefix("!unequip ")
  user = ctx.author
  users = await get_accounts_data()
  inv = users[str(user.id)]["inventory"]
  item = item1
  items = await get_items_data()
  try:
    item_name = items[str(item)]["name"]
    item_type = items[str(item)]["type"]
    item_class = items[str(item)]["class"]
    item_level = items[str(item)]["level"]
    item_hpbonus = items[str(item)]["healthbonus"]
    item_mindmgbonus = items[str(item)]["mindamagebonus"]
    item_maxdmgbonus = items[str(item)]["maxdamagebonus"]
    item_defense = items[str(item)]["defense"]

    if item1 in inv:
      if item_type == "helmet":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["helmet"] == item1:
              users[str(ctx.author.id)]["helmet"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "chest":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["chest"] == item1:
              users[str(ctx.author.id)]["chest"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "pants":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["pants"] == item1:
              users[str(ctx.author.id)]["pants"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "boots":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["boots"] == item1:
              users[str(ctx.author.id)]["boots"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "necklace":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["necklace"] == item1:
              users[str(ctx.author.id)]["necklace"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "ring":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["ring"] == item1:
              users[str(ctx.author.id)]["ring"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "cape":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["cape"] == item1:
              users[str(ctx.author.id)]["cape"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")

      elif item_type == "weapon":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            if users[str(ctx.author.id)]["weapon"] == item1:
              users[str(ctx.author.id)]["weapon"] = "none"
              users[str(user.id)]["mindmg"] -= item_mindmgbonus
              users[str(user.id)]["maxdmg"] -= item_maxdmgbonus
              users[str(user.id)]["health"] -= item_hpbonus
              users[str(user.id)]["defense"] -= item_defense
              await ctx.reply(f"Unquipped {item1}")
  except:
    await ctx.reply("That isn't an item you have currently equipped")

  j = json.dumps(users, indent=4)
  with open("accounts.json", "w") as f:
    f.write(j)
    f.close()


unequip.triggers = ["unequip"]


# TODO: Uhh probably increase robustness?
async def equip(client, ctx):
  await open_account(ctx.author)
  item1 = ctx.message.content.removeprefix("!equip ")
  user = ctx.author
  users = await get_accounts_data()
  inv = users[str(user.id)]["inventory"]
  item = item1
  items = await get_items_data()
  try:
    item_name = items[str(item)]["name"]
    item_type = items[str(item)]["type"]
    item_class = items[str(item)]["class"]
    item_level = items[str(item)]["level"]
    item_hpbonus = items[str(item)]["healthbonus"]
    item_mindmgbonus = items[str(item)]["mindamagebonus"]
    item_maxdmgbonus = items[str(item)]["maxdamagebonus"]
    item_defense = items[str(item)]["defense"]

    if item1 in inv and item1 in ["helmet", "chest"]:
      if item_type == "helmet":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["helmet"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "chest":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["chest"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "pants":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["pants"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "boots":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["boots"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "necklace":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["necklace"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "ring":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["ring"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "cape":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["cape"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")

      elif item_type == "weapon":
        if item_level <= users[str(user.id)]["level"]:
          if item_class == users[str(user.id)]["class"] or "all":
            users[str(ctx.author.id)]["weapon"] = item_name
            users[str(user.id)]["mindmg"] += item_mindmgbonus
            users[str(user.id)]["maxdmg"] += item_maxdmgbonus
            users[str(user.id)]["health"] += item_hpbonus
            users[str(user.id)]["defense"] += item_defense
            await ctx.reply(f"Equipped {item1}")
  except:
    await ctx.reply("That isnt an item you posses or can equip")

  j = json.dumps(users, indent=4)
  with open("accounts.json", "w") as f:
    f.write(j)
    f.close()


equip.triggers = ["equip"]


async def inventory(client, ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_accounts_data()
  inv = users[str(user.id)]["inventory"]
  embed_pages = []
  onpage = 0
  page_num = 1
  page_embed = discord.Embed(title=f"**{ctx.author}'s Inventory:**",
                             colour=discord.Colour.default())
  currentembed = ""

  for entry in inv:
    currentembed += f"{entry} x {inv[entry]}\n"
    onpage += 1

    if onpage == 10:
      page_embed.add_field(name="Page " + str(page_num),
                           value=currentembed,
                           inline=False)
      print("EMBED:")
      print(currentembed)
      currentembed = ""
      page_num += 1
      embed_pages.append(page_embed)
      onpage = 0
      page_embed = discord.Embed(title=f"**{ctx.author}'s Inventory:**",
                                 colour=discord.Colour.default())

  if currentembed != "" or len(embed_pages) == 0:
    page_embed.add_field(name="Page " + str(page_num),
                         value=currentembed,
                         inline=False)
    print("EMBED:")
    print(currentembed)
    currentembed = ""
    page_num += 1
    embed_pages.append(page_embed)

  if len(embed_pages) > 1:

    class Buttons(discord.ui.View):

      def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
        self.cpage = 0

      @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.grey)
      async def button_back(self, thisinteraction: discord.Interaction,
                            button: discord.ui.Button):
        if thisinteraction.user == ctx.author:
          await thisinteraction.response.defer()
          # If current page is not first page
          if (self.cpage > 0):
            self.cpage -= 1
          # If current page is last page
          else:
            self.cpage = len(embed_pages) - 1
          # Editing message to show new page
          await msg.edit(embed=embed_pages[self.cpage])

      @discord.ui.button(label="Next Page", style=discord.ButtonStyle.grey)
      async def button_next(self, thisinteraction: discord.Interaction,
                            button: discord.ui.Button):
        print(self.cpage)
        if thisinteraction.user == ctx.author:
          await thisinteraction.response.defer()
          # If current page is not last page
          if (self.cpage < len(embed_pages) - 1):
            self.cpage += 1
          # If current page is last page
          else:
            self.cpage = 0
          # Editing message to show new page
          await msg.edit(embed=embed_pages[self.cpage])

    msg = await ctx.reply(embed=embed_pages[0], view=Buttons())
  else:
    msg = await ctx.reply(embed=embed_pages[0])


inventory.triggers = ["inventory", "inv", "i"]


async def craft(client, ctx):
  users = await get_accounts_data()
  noprefix = ctx.message.content.removeprefix("!craft ")
  # Identifying matching Schematics in the user's inventory
  craftablematches = []
  for key in users[str(ctx.author.id)]["inventory"].keys():
    if (itemDict.get(key)["type"].lower()
        == "schematic") and (key.lower().find(noprefix.lower()) != -1):
      craftablematches.append(key)
  if len(craftablematches) == 1:
    # Checking if the player has all required materials
    materials = itemDict.get(craftablematches[0])["materials"]
    missingmaterial = False
    targetitem = itemDict.get(craftablematches[0]).get("product")
    reply = "Materials needed to craft 1x " + targetitem + ":"
    for material in materials:
      matamount = users[str(ctx.author.id)]["inventory"].get(material)
      reply = reply + f"\n" + material + ": " + str(matamount) + " of " + str(
        materials.get(material)) + " required"
      if matamount == None or matamount < materials[material]:
        missingmaterial = True
    # TODO: confirmation button stuff here
    # Hoo boy how the fuck do I explain this?
    # I don't understand half of this myself
    materialstaken = []
    if not missingmaterial:

      class Buttons(discord.ui.View):

        def __init__(self, *, timeout=60):
          super().__init__(timeout=timeout)

        @discord.ui.button(label="Abort", style=discord.ButtonStyle.grey)
        async def abort_button(self, thisinteraction: discord.Interaction,
                               button: discord.ui.Button):
          if thisinteraction.user == ctx.author:
            await replymsg.edit(content="Didn't craft anything.", view=None)
            return

        @discord.ui.button(label="Craft", style=discord.ButtonStyle.green)
        async def accept_button(self, thisinteraction: discord.Interaction,
                                button: discord.ui.Button):
          if thisinteraction.user == ctx.author:
            for material in itemDict.get(craftablematches[0])["materials"]:
              if await inventoryremove(
                  ctx.author, material,
                  int(
                    itemDict.get(
                      craftablematches[0]).get("materials")[material])):
                materialstaken.append(material)
              else:
                # Aborting crafting and refunding materials
                for refund in materialstaken:
                  await inventoryadd(ctx.author, refund, materials.get(refund))
                await ctx.reply(
                  "Something went wrong. Make sure you have all required materials and try again."
                )
                return
            await replymsg.edit(content="Success! Crafted 1x " + targetitem +
                                ".",
                                view=None)
            await inventoryadd(ctx.author, targetitem, 1)

      replymsg = await ctx.reply(reply, view=Buttons())
    else:
      await ctx.reply(reply)
  elif len(craftablematches) < 1:
    await ctx.reply("You don't know how to craft anything matching your query!"
                    )
  elif len(craftablematches) > 1:
    await ctx.reply("You know how to craft " + str(len(craftablematches)) +
                    " matching your query, please tighten your search!")
  return


craft.triggers = ["craft"]


async def trust(client, ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_accounts_data()
  trust = users[str(user.id)]["trust"]
  await ctx.reply(f"Your trust factor is: {trust}")


trust.triggers = ["trust"]


async def helpme(client, ctx):
  await open_account(ctx.author)
  user = ctx.author
  help_1 = discord.Embed(
    title=f"**Help page 1**",
    colour=discord.Colour.red(),
    description=
    f"Commands: \n!explore\n!travel [area]\n!leaderboard\n!profile\n!inventory\n!equip [item name]"
  )

  help_2 = discord.Embed(
    title=f"**Help page 2**",
    colour=discord.Colour.red(),
    description=
    f"Commands:\n !area list\n!area create [area]\n!area delete\n!area description [area] [content]\n!area put [enemy]\n!area take [enemy]\n!scan [txtfile]"
  )

  msg = await ctx.send(embed=help_1)
  buttons = ["⬅️", "➡️"]
  current = msg
  for button in buttons:
    await msg.add_reaction(button)

  try:
    reaction, user = await client.wait_for(
      "reaction_add",
      check=lambda reaction, user: user == ctx.author and reaction.message ==
      msg and reaction.emoji in buttons,
      timeout=30.0)

  except asyncio.TimeoutError:
    # Deactivates the message after 30 seconds, and exits the function
    msg.set_footer(text="Timed out.")
    await msg.clear_reactions()
    return

    #checks if the answer is wrong or correct
  else:
    previous_page = current
    if reaction.emoji == "➡️":
      current = help_2
      await msg.edit(embed=current)

    for button in buttons:
      await msg.remove_reaction(button, ctx.author)

    if current != previous_page:
      await msg.edit(embed=current)

    elif reaction.emoji == "⬅️":
      current = help_1
      await msg.edit(embed=current)

    for button in buttons:
      await msg.remove_reaction(button, ctx.author)

    if current != previous_page:
      await msg.edit(embed=current)


helpme.triggers = ["helpme", "help"]


# Command to set the user's stats to the provided values
async def setstats(client, ctx):
  if not (byAdmin(ctx) or byContentMod(ctx)):
    await ctx.reply('Insufficient permission.')
    return
  print(ctx.message.content)
  if len(ctx.message.content.removeprefix("!setstats ").split(" ")) == 4:
    for current in (ctx.message.content.removeprefix("!setstats ").split(" ")):
      if not current.isdigit():
        await ctx.reply('Failed to parse value "' + current + '" to Integer.')
        return
    # Modifying stats
    users = await get_accounts_data()
    users[str(ctx.author.id)]["health"] = int(
      ctx.message.content.removeprefix("!setstats ").split(" ")[0])
    users[str(ctx.author.id)]["battlehealth"] = int(
      ctx.message.content.removeprefix("!setstats ").split(" ")[0])
    users[str(ctx.author.id)]["defense"] = int(
      ctx.message.content.removeprefix("!setstats ").split(" ")[1])
    users[str(ctx.author.id)]["mindmg"] = int(
      ctx.message.content.removeprefix("!setstats ").split(" ")[2])
    users[str(ctx.author.id)]["maxdmg"] = int(
      ctx.message.content.removeprefix("!setstats ").split(" ")[3])
    j = json.dumps(users, indent=4)
    with open("accounts.json", "w") as f:
      f.write(j)
      f.close()
    await ctx.reply('Values modified.')
  else:
    await ctx.reply(
      'Insufficient arguments. Expected: 4, Provided: ' +
      str(len(ctx.message.content.removeprefix("!setstats ").split(" "))) +
      '.')


setstats.triggers = ["setstats"]


# Command to simulate combat of a player with the provided stats with the provided enemy
async def simulate(client, ctx):
  global enemyDict
  fsyntax = 'Correct syntax is "!simulate [player HP] [player min. dmg] [player max. dmg] [enemy name]"'
  if (len(ctx.message.content.removeprefix("!simulate"))) > 8:
    noprefix = ctx.message.content.removeprefix("!simulate ")
    if (noprefix.split(" ")[0].isdigit() and noprefix.split(" ")[1].isdigit()
        and noprefix.split(" ")[2].isdigit()):
      #function body
      simenemy = noprefix.removeprefix(
        noprefix.split(" ")[0] + " " + noprefix.split(" ")[1] + " " +
        noprefix.split(" ")[2] + " ")
      if enemyDict.get(simenemy) != None:
        win = 0
        loss = 0
        draw = 0
        for i in range(1, 101):
          simplayerhp = int(noprefix.split(" ")[0])
          simenemyhp = int(enemyDict.get(simenemy).health)
          simenemynode = 0
          #Simulating one encounter
          while (simplayerhp > 0 and simenemyhp > 0):
            simenemyaction = enemyDict.get(simenemy).getNodeAction(
              simenemynode)
            simplayerhp -= simenemyaction[1]
            simenemyhp -= random.randint(int(noprefix.split(" ")[1]),
                                         int(noprefix.split(" ")[2]))
            simenemynode = int(simenemyaction[2])
          if (simplayerhp <= 0):
            if (simenemyhp <= 0):
              draw += 1
            else:
              loss += 1
          else:
            win += 1
        await ctx.reply('Simulation complete.\nPlayer Victories: ' + str(win) +
                        '\nPlayer Losses: ' + str(loss) + '\nDraws: ' +
                        str(draw))
        return
      else:
        await ctx.reply('Failed to find enemy "' + simenemy + '". ' + fsyntax)
      return
    else:
      await ctx.reply('Failed to parse a value to Integer. ' + fsyntax)
      return
  #Default error message
  await ctx.reply("Something went wrong. " + fsyntax)


simulate.triggers = ["simulate"]


#Multi-purpose item viewing and administration command.
#Subcommands:
#   [item name]: Returns information on the item with the provided name. Only returns information on items a player owns if not run by an admin or content creator.
#   TODO: references: Checks the validity of all item references in the enemy database. Restricted to admins or content creators.
#   TODO: (message has attachment): Parses the provided files into valid item dictionaries and adds them to the item database. Restricted to admins or content creators.
#   TODO: remove [item name]: Removes the item with the provided name from the item database. Restricted to admins or content creators.
async def item(client, ctx):
  noprefix = ctx.message.content.removeprefix("!item ").strip()
  itemmatches = len(pickAllMatching(noprefix, itemDict.keys()))
  #Player command processing begins here
  #TODO: Increase this section's robustness and give feedback upon incorrect use
  if not byAdmin(ctx) and not byContentMod(ctx):
    items = await get_items_data()
    item_name = items[str(noprefix)]["name"]
    showitem = discord.Embed(title=f"{item_name}",
                             colour=discord.Colour.default())
    showitem.add_field(name=f"**Health bonus:**",
                       value=items[str(noprefix)]["healthbonus"],
                       inline=False)
    showitem.add_field(name=f"**Minimum damage bonus:**",
                       value=items[str(noprefix)]["mindamagebonus"],
                       inline=False)
    showitem.add_field(name=f"**Maximum damage bonus:**",
                       value=items[str(noprefix)]["maxdamagebonus"],
                       inline=False)
    showitem.add_field(name=f"**Item level:**",
                       value=items[str(noprefix)]["level"],
                       inline=False)
    showitem.add_field(name=f"**Class:**",
                       value=items[str(noprefix)]["class"],
                       inline=False)
    showitem.add_field(name=f"**Item type:**",
                       value=items[str(noprefix)]["type"],
                       inline=False)
    msg = await ctx.send(embed=showitem)
  #Priviledged command processing begins here
  #Handling item scanning
  elif len(ctx.message.attachments) > 0:
    attachments = ctx.message.attachments
    for cattach in attachments:
      # Checking whether the current attachment is a text file, and skipping it if not
      if not cattach.filename.endswith(".txt"):
        await ctx.reply("Invalid file type: " + cattach.filename)
        continue
      # Saving the attachment
      await cattach.save(cattach.filename)
      # Parsing begins here
      newItem = {}
      try:
        with open(os.getcwd() + sep + cattach.filename) as f:
          # Scanning the input file
          lines = f.readlines()
          f.close()
          # Deleting the parsed file as it is no longer needed
          os.remove(os.getcwd() + sep + cattach.filename)
          # Reading the first line, encoding the item name. This is ubiquitous.
          newItem["name"] = lines.pop(0).removesuffix("\n").strip()
          # Dynamically parsing following lines into key:value pairs, and adding them to the new item
          formatbreaks = "Format breaks in " + cattach.filename + ":"
          for cline in lines:
            if cline.count(':') != 1:
              formatbreaks = formatbreaks + "\nInvalid formatting in line " + str(
                lines.index(cline)) + ": Should have 1 separator, has " + str(
                  cline.count(':'))
              continue
            elif len(cline.split(':')[0].strip()) == 0:
              formatbreaks = formatbreaks + "\nInvalid formatting in line " + str(
                lines.index(
                  cline)) + ": Key should have more than 0 digits, has 0"
              continue
            elif len(cline.split(':')[1].strip()) == 0:
              formatbreaks = formatbreaks + "\nInvalid formatting in line " + str(
                lines.index(
                  cline)) + ": Value should have more than 0 digits, has 0"
              continue
            # Parsing crafting materials
            elif cline.split(':')[0].lower().strip() == "materials":
              materials = {}
              for material in cline.split(':')[1].strip().split(','):
                if not material.split('=')[1].strip().isdigit():
                  formatbreaks += f"\nInvalid formatting in line " + str(
                    lines.index(cline)) + ": " + str(
                      material.split('/').strip()
                      [1]) + " is not a valid integer"
                materials[material.split('=')[0].strip()] = int(
                  material.split('=')[1].strip())
              newItem["materials"] = materials
            # Parsing primitive attributes
            else:
              # Converting to int where possible
              if cline.split(':')[1].strip().isdigit():
                newItem[cline.split(':')[0].strip().lower()] = int(
                  cline.split(':')[1].strip())
              else:
                newItem[cline.split(':')[0].strip().lower()] = cline.split(
                  ':')[1].strip()
          # Printing the format breaks if there are any
          if (len(formatbreaks) > (18 + len(cattach.filename))):
            await ctx.reply(formatbreaks)
          # Saving the created item if there were no format breaks
          else:
            itemDict[newItem["name"]] = newItem
            dumpitemdict()
            await ctx.reply('Saved item "' + newItem["name"] + '"')
      except Exception as ex:
        await ctx.reply("Something went wrong. Check the formatting of " +
                        cattach.filename + " and try again.")
        print(ex)
  # Checking reference validity
  elif noprefix == "ref":
    reply = "Following items are referenced, but don't exist:\n"
    # Checking enemy item drops
    for enemy in enemyDict.values():
      for dropinfo in enemy.itemdrops:
        if dropinfo["name"] not in itemDict.keys():
          reply += dropinfo["name"] + f" as item drop of enemy {enemy.name}\n"
    # Checking crafting materials
    for item in itemDict.values():
      if item["materials"] != None:
        for material in item["materials"]:
          if material not in itemDict.keys():
            print(material)
            reply += material + f" as material used in schematic " + item[
              "name"] + "\n"
    if len(reply) > 50:
      await ctx.reply(reply)
    else:
      await ctx.reply("No faulty references found!")
  #Item information, process this clause after all other possibilities!
  elif itemmatches > 0:
    if itemmatches > 20:
      await ctx.reply(
        f"{itemmatches} matching items found. Please tighten your search!")
    elif itemmatches > 1:
      reply = f"Found {itemmatches} matches:"
      for cmatch in pickAllMatching(noprefix, itemDict.keys()):
        reply += "\n" + cmatch + " (" + itemDict.get(cmatch).get("type") + ")"
      await ctx.reply(reply)
    else:
      reply = "Match found: " + pickClosest(noprefix, itemDict.keys())
      for attribute in itemDict.get(pickClosest(noprefix,
                                                itemDict.keys())).items():
        reply += "\n" + attribute[0] + ": " + str(attribute[1])
      await ctx.reply(reply)
  else:
    fsyntax = "No matching items or subcommands found. Valid subcommands are:\n"
    fsyntax += "!item [item name]: Returns details of the matching item, a list of matching items or a count of matching items, depending on match count.\n"
    fsyntax += "!item (message has attachments): Attempts to parse and save each attachment as a valid item\n"
    fsyntax += "!item ref: Checks items references in enemy and item databases for validity\n"
    fsyntax += "!item del [item name]: Removes the indicated item from the item database"
    await ctx.reply(fsyntax)


item.triggers = ["item"]


# TODO: Crafting function
async def craft(client, ctx):
  users = await get_accounts_data()
  noprefix = ctx.message.content.removeprefix("!craft ")
  # Identifying matching Schematics in the user's inventory
  allmatches = pickAllMatching(noprefix, itemDict.keys())
  craftablematches = []
  for match in allmatches:
    if users[str(
        ctx.author.id)]["inventory"].get(match)["type"].lower() == "schematic":
      craftablematches.append(match)

  if len(craftablematches) == 1:
    # TODO: confirmation button stuff here
    print("CRAFTING FLAG")
  elif len(craftablematches) < 1:
    await ctx.reply("You don't know how to craft anything matching your query!"
                    )
  elif len(craftablematches) > 10:
    await ctx.reply("You know how to craft " + craftablematches +
                    " matching your query, please tighten your search!")
  return


#craft.triggers = ["craft"]


#All-purpose area administration command.
#Subcommands:
#   create [name]: creates a new empty area with the provided name
#   delete [name]: permanently deletes an area with the provided name
#   description [area] [content]: sets an area's description to the provided string
#   list: returns a list of all areas along the amounts of enemies assigned to each one
#   [area] put [enemy]: adds a reference to the provided enemy to the enemy list of the provided area
#   [area] take [enemy]: removes a reference to the provided enemy from the enemy list of the provided area
async def area(client, ctx):
  # Checking for priviledge
  if not byAdmin(ctx) and not byContentMod(ctx):
    await ctx.reply("Missing permission.")
    return
  # Beginning message processing, and ceasing operation on insufficient argument count
  global areaDict
  global enemyDict
  noprefix = ctx.message.content.removeprefix("!area ")
  # Handling area addition
  if noprefix.split(" ")[0] == "create" and len(noprefix) > 7:
    areaDict[noprefix.removeprefix("create ")] = Area(
      noprefix.removeprefix("create "))
    await ctx.reply("Successfully added area!")
    # Saving changes
    dumpareadict()
    return
  # Handling area deletion
  elif noprefix.split(" ")[0] == "delete" and len(noprefix) > 7:
    if areaDict.get(noprefix.removeprefix("delete ")):
      areaDict.pop(noprefix.removeprefix("delete "))
      # Saving changes
      dumpareadict()
      await ctx.reply("Successfully deleted area.")
      return
    else:
      await ctx.reply("Invalid area name.")
      return
  # Handling area description modification
  elif noprefix.split(" ")[0] == "description" and len(noprefix) > 12:
    workingstr = ""
    for segment in noprefix.removeprefix("description ").split(" "):
      workingstr += segment + " "
      print(workingstr)
      if areaDict.get(workingstr.strip()):
        areaDict.get(workingstr.strip()).description = noprefix.removeprefix(
          "description ").removeprefix(workingstr)
        await ctx.reply("Edited area description.")
        dumpareadict()
        return
  # Handling area list viewing
  elif noprefix.split(" ")[0] == "list":
    output = "List of all stored Areas:"
    for carea in list(areaDict.values()):
      output = output + "\n" + carea.name + ": " + str(len(
        carea.enemies)) + " enemies"
    await ctx.reply(output)
    return
  # Handling enemy placement
  workingstr = ""
  for segment in noprefix.split(" "):
    workingstr += segment + " "
    if areaDict.get(workingstr.strip()):
      # Handling enemy addition
      if noprefix.removeprefix(workingstr).split(" ")[0] == "put":
        if enemyDict.get(noprefix.removeprefix(workingstr + "put ")) != None:
          await ctx.reply(
            areaDict.get(workingstr.strip()).addEnemy(
              noprefix.removeprefix(workingstr + "put ")))
          dumpareadict()
          return
        else:
          await ctx.reply('Failed to find enemy "' +
                          noprefix.removeprefix(workingstr).split(" ")[1] +
                          '"')
          return
      # Handling enemy removal
      if noprefix.removeprefix(workingstr).split(" ")[0] == "take":
        await ctx.reply(
          areaDict.get(workingstr.strip()).removeEnemy(
            noprefix.removeprefix(workingstr + "take ")))
        dumpareadict()
        return
  await ctx.reply(
    'Invalid syntax. Try "[area] put [enemy]" or "[area] take [enemy]"')


area.triggers = ["area"]


async def travel(client, ctx):
  content = ctx.message.content.removeprefix("!travel ").strip()
  areaname = pickClosest(content, areaDict.keys())
  if areaname != None:
    users = await get_accounts_data()
    users[str(ctx.author.id)]["area"] = areaname
    j = jsonpickle.encode(users, indent=2)
    with open("accounts.json", "w") as f:
      f.write(j)
      f.close()
    await ctx.reply("Welcome to " + areaname)
    altereign = discord.Embed(title=f"**Travelling to {areaname}**",
                              colour=discord.Colour.default())
    altereign.set_image(url='https://i.imgur.com/dPE1PKE.png')
    forest = discord.Embed(title=f"**Travelling to {areaname}**",
                           colour=discord.Colour.default())
    forest.set_image(url='https://i.imgur.com/rkUnJ82.png')

    if areaname == "Altereign":
      await ctx.send(embed=altereign)
    if areaname == "Forest":
      await ctx.send(embed=forest)


travel.triggers = ["travel"]


# Command to scan a number of nodemap text files and add them to the enemy database.
# Checks every nodemap individually and may reject each one for improper formatting or being an invalid filetype.
# Also checks validity of item references.
async def scan(client, ctx):
  # Checking author permission
  if not (byAdmin(ctx) or byContentMod(ctx)): return
  attachments = ctx.message.attachments
  for cattach in attachments:
    # Checking whether the current attachment is a text file, and skipping it if not
    if not cattach.filename.endswith(".txt"):
      await ctx.reply("Invalid file type: " + cattach.filename)
      continue
    # Saving the attachment
    await cattach.save(cattach.filename)
    # Parsing begins here
    try:
      with open(os.getcwd() + os.path.sep + cattach.filename) as f:
        # Scanning the input file
        lines = f.readlines()
        # Reading the first line, containing the name and HP of the enemy, as well as gold and experience drops
        name = lines[0].split("/")[0]
        hp = int(lines[0].split("/")[1].removesuffix("HP"))
        defense = int(lines[0].split("/")[2].removesuffix("DEF"))
        level = int(lines[0].split("/")[3].removeprefix("LVL"))
        exp = int(lines[0].split("/")[4].removesuffix("EXP"))
        gold = int(
          lines[0].split("/")[5].removesuffix("\n").removesuffix("GOLD"))
        # Removing the already processed line
        lines.pop(0)
        # Reading the second line, encoding the items dropped by the enemy
        itemdrops = []
        for currentItem in lines[0].split(','):
          itemdrops.append({
            "name":
            currentItem.split('-')[0],
            "amount":
            int(currentItem.split('-')[1].strip()),
            "chance":
            int(
              currentItem.split('-')[2].removesuffix(
                "\n").strip().removesuffix("%"))
          })
          print(str(itemdrops))
        # Removing the already processed line
        lines.pop(0)
        # Instantiating an enemy object with the current parameters
        newEnemy = Enemy(name, hp, defense, level, exp, gold, itemdrops)
        # Reading the second and following lines, each encoding one behaviour node
        for currentLine in lines:
          newNode = Enemy.Node(
            currentLine.split("/")[0],
            currentLine.split("/")[1],
            currentLine.split("/")[2])
          for currentTransfer in currentLine.split("/")[3].split(","):
            newNode.addTransfer(
              currentTransfer.split("-")[0],
              int(
                currentTransfer.split("-")[1].removesuffix("\n").removesuffix(
                  "%")))
          newEnemy.addNode(newNode)
        # Saving changes
        global enemyDict
        enemyDict[newEnemy.name] = newEnemy
        dumpenemydict()
        await ctx.reply("Successfully saved " + newEnemy.name + ".")
        for citem in itemdrops:
          if itemDict.get(citem["name"]) == None:
            await ctx.reply(
              'Warning: Item drop "' + citem["name"] +
              '" does not exist in the item database. This could lead to serious errors!'
            )

    except Exception as ex:
      await ctx.reply("Something went wrong. Check the formatting of " +
                      cattach.filename + " and try again.")
      print(ex)
    # Removing the nodemap file as it is no longer needed
    os.remove(os.getcwd() + os.path.sep + cattach.filename)


scan.triggers = ["scan"]


async def leaderboard(client, ctx, x=10):
  users = await get_accounts_data()
  leader_board = {}
  total = []
  for user in users:
    name = int(user)
    total_amount = users[user]["exp"]
    leader_board[total_amount] = name
    total.append(total_amount)

  total = sorted(total, reverse=True)

  em = discord.Embed(title=f"Top {x} users based on experience",
                     color=discord.Color(0xfa43ee))
  index = 1
  for amt in total:
    id_ = leader_board[amt]
    member = await client.fetch_user(id_)
    name = member.name
    em.add_field(name=f"{index}. {name} ", value=f"Exp: {amt}", inline=False)
    if index == x:
      break
    else:
      index += 1
  await ctx.send(embed=em)


leaderboard.triggers = ["leaderboard"]


async def partyadd(client, ctx, member: discord.Member):
  users = await get_accounts_data()
  await open_account(ctx.author)
  await open_account(member)
  member_username = await client.fetch_user(member.id)
  if member.id not in users[str(ctx.author.id)]["party"]:
    if ctx.author.id not in users[str(member.id)]["party"]:
      users[str(ctx.author.id)]["party"].append(member.id)
      users[str(member.id)]["party"].append(ctx.author.id)
      await ctx.reply(f"Successfully added {member_username} to your party")

    else:
      await ctx.reply("Cannot find this user")

  j = json.dumps(users, indent=4)
  with open("accounts.json", "w") as f:
    f.write(j)
    f.close()


partyadd.triggers = ["partyadd"]


async def partyremove(client, ctx, member: discord.Member):
  users = await get_accounts_data()
  await open_account(ctx.author)
  await open_account(member)
  member_username = await client.fetch_user(member.id)
  if member.id in users[str(ctx.author.id)]["party"]:
    if ctx.author.id in users[str(member.id)]["party"]:
      users[str(ctx.author.id)]["party"].remove(member.id)
      users[str(member.id)]["party"].remove(ctx.author.id)
      await ctx.reply(f"Successfully removed {member_username} from your party"
                      )
    else:
      await ctx.reply("Cannot find this user")

  j = json.dumps(users, indent=4)
  with open("accounts.json", "w") as f:
    f.write(j)
    f.close()


partyremove.triggers = ["partyremove"]


async def party(client, ctx, x=4):
  users = await get_accounts_data()
  health = users[str(ctx.author.id)]["battlehealth"]
  partylist = discord.Embed(title=f"**Players in your party**",
                            color=discord.Color(0xfa43ee))
  partylist.add_field(name=f"{ctx.author.name}",
                      value=f"Health: {health}",
                      inline=False)
  index = 0
  for players in users[str(ctx.author.id)]["party"]:
    id_ = int(users[str(ctx.author.id)]["party"][index])
    member = await client.fetch_user(id_)
    name = member.name
    health = users[str(member.id)]["battlehealth"]
    partylist.add_field(name=f"{name}",
                        value=f"Health: {health}",
                        inline=False)
    if index == x:
      break
    else:
      index += 1

  await ctx.send(embed=partylist)
  """em = discord.Embed(title = f"**Players in your party**", color = discord.Color(0xfa43ee))
    index = 1
    for amt in users[str(ctx.author.id)]["party"]:
        id_ = int(users[str(ctx.author.id)]["party"][0])
        member = await client.fetch_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name} ", value = None , inline = False)
        if index == x:
            break
        else:
            index +=1
    await ctx.send(embed = em)"""


party.triggers = ["party"]


async def explore(client, ctx):
  await open_account(ctx.author)
  user = ctx.author
  users = await get_accounts_data()
  health_amt = users[str(user.id)]["health"]
  battlehealth_amt = users[str(user.id)]["health"]
  mindmg_amt = users[str(user.id)]["mindmg"]
  maxdmg_amt = users[str(user.id)]["maxdmg"]
  gold_amt = users[str(user.id)]["gold"]
  level_amt = users[str(user.id)]["level"]
  exp_amt = users[str(user.id)]["exp"]
  cmd_use = users[str(user.id)]["cmd_use"]
  trust = users[str(user.id)]["trust"]
  battlehealth_amt = health_amt
  enemynode = 0
  while users[str(user.id)]["exp"] >= (users[str(
      user.id)]["level"]**3.3) + (13) - (users[str(user.id)]["level"]):
    users[str(user.id)]["health"] += 6
    users[str(user.id)]["mindmg"] += 1
    users[str(user.id)]["maxdmg"] = round(users[str(user.id)]["mindmg"] * 1.5)
    users[str(user.id)]["level"] += 1
    print(users[str(user.id)]["area"])
  explore8 = discord.Embed(title=f"**Removed Previous Fight.**")
  explore7 = discord.Embed(title=f"**Exploring...**")
  anti_cheat = random.randint(1, 15)
  num1 = random.randint(1, 15)
  num2 = random.randint(1, 15)
  questions = [num1 + num2, num1 - num2, num1 * num2]
  random.shuffle(questions)
  if cmd_use == 0:
    users[str(user.id)]["cmd_use"] = 1
    j = json.dumps(users, indent=4)
    with open("accounts.json", "w") as f:
      f.write(j)
      f.close()
    if anti_cheat == 1:
      j = json.dumps(users, indent=4)
      with open("accounts.json", "w") as f:
        f.write(j)
        f.close()
      question = discord.Embed(title=f"**Altereign Anti-Cheat**",
                               colour=discord.Colour.default(),
                               description=f"What is {num1} + {num2} ?")
      question.add_field(name=f"1. ", value=questions[0])
      question.add_field(name=f"2. ", value=questions[1])
      question.add_field(name=f"3. ", value=questions[2])

      correct = discord.Embed(title=f"**Altereign Anti-Cheat**",
                              colour=discord.Colour.default(),
                              description=f"Correct")
      #correct.set_image(url = 'https://i.imgur.com/a2sdh0i.png')
      wrong = discord.Embed(title=f"**Altereign Anti-Cheat**",
                            colour=discord.Colour.default(),
                            description=f"Wrong")
      #wrong.set_image(url = 'https://i.imgur.com/Krv0OxG.png')

      quiz = await ctx.send(embed=question)
      buttons = ["1️⃣", "2️⃣", "3️⃣"]

      for button in buttons:
        await quiz.add_reaction(button)

      try:
        reaction, user = await client.wait_for(
          "reaction_add",
          check=lambda reaction, user: user == ctx.author and reaction.message
          == quiz and reaction.emoji in buttons,
          timeout=30.0)

      except asyncio.TimeoutError:
        # Deactivates the message after 30 seconds, and exits the function
        question.set_footer(text="Timed out.")
        await quiz.clear_reactions()
        users[str(user.id)]["cmd_use"] = 0
        j = json.dumps(users, indent=4)
        with open("accounts.json", "w") as f:
          f.write(j)
          f.close()
        return

        #checks if the answer is wrong or correct
      else:
        if reaction.emoji == "1️⃣":
          if questions[0] == num1 + num2:
            users[str(user.id)]["cmd_use"] = 0
            await quiz.edit(embed=correct)
            users[str(user.id)]["trust"] += 1
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return
          else:
            users[str(user.id)]["cmd_use"] = 0
            await quiz.edit(embed=wrong)
            users[str(user.id)]["trust"] -= 1
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

        elif reaction.emoji == "2️⃣":
          if questions[1] == num1 + num2:
            users[str(user.id)]["cmd_use"] = 0
            await quiz.edit(embed=correct)
            users[str(user.id)]["trust"] += 1
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

          else:
            users[str(user.id)]["cmd_use"] = 0
            await quiz.edit(embed=wrong)
            users[str(user.id)]["trust"] -= 1
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

        elif reaction.emoji == "3️⃣":
          if questions[2] == num1 + num2:
            await quiz.edit(embed=correct)
            users[str(user.id)]["trust"] += 1
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

          else:
            await quiz.edit(embed=wrong)
            users[str(user.id)]["trust"] -= 1
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

        for button in buttons:
          await quiz.remove_reaction(button, ctx.author)

    #If u havent chosen a class it will ask you to, hence default = no class
    else:
      if users[str(user.id)]["class"] == "default":
        choose_class = discord.Embed(
          title=f"**Please choose a class:**",
          colour=discord.Colour.default(),
          description=f"And begin your journey to victory!")
        choose_class.add_field(name=f"Archer",
                               value="- High damage, low health",
                               inline=False)
        choose_class.add_field(name=f"Knight",
                               value="High health, low damage",
                               inline=False)
        choose_class.add_field(name=f"Mage",
                               value="Balanced health, balanced damage",
                               inline=False)
        choose_class.add_field(name=f"Rogue",
                               value="High damage, low health",
                               inline=False)
        choose_class_Archer = discord.Embed(
          title=f"**You have chosen Archer**",
          colour=discord.Colour.default(),
          description=f"A wise choice adventurer!")
        choose_class_Knight = discord.Embed(
          title=f"**You have chosen Knight**",
          colour=discord.Colour.default(),
          description=f"A wise choice adventurer!")
        choose_class_Mage = discord.Embed(
          title=f"**You have chosen Mage**",
          colour=discord.Colour.default(),
          description=f"A wise choice adventurer!")
        choose_class_Rogue = discord.Embed(
          title=f"**You have chosen Rogue**",
          colour=discord.Colour.default(),
          description=f"A wise choice adventurer!")

        choice = await ctx.send(embed=choose_class)
        buttons = ["🏹", "🛡️", "🧙", "🗡️"]
        for button in buttons:
          await choice.add_reaction(button)

        try:
          reaction, user = await client.wait_for(
            "reaction_add",
            check=lambda reaction, user: user == ctx.author and reaction.
            message == choice and reaction.emoji in buttons,
            timeout=30.0)

        except asyncio.TimeoutError:
          # Deactivates the message after 30 seconds, and exits the function
          choose_class.set_footer(text="Timed out.")
          await choice.clear_reactions()
          users[str(user.id)]["cmd_use"] = 0
          j = json.dumps(users, indent=4)
          with open("accounts.json", "w") as f:
            f.write(j)
            f.close()
          return

        else:
          if reaction.emoji == "🏹":
            await choice.edit(embed=choose_class_Archer)
            users[str(user.id)]["class"] = "Archer"
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
              return

          elif reaction.emoji == "🛡️":
            await choice.edit(embed=choose_class_Knight)
            users[str(user.id)]["class"] = "Knight"
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

          elif reaction.emoji == "🧙":
            await choice.edit(embed=choose_class_Mage)
            users[str(user.id)]["class"] = "Mage"
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

          elif reaction.emoji == "🗡️":
            await choice.edit(embed=choose_class_Rogue)
            users[str(user.id)]["class"] = "Rogue"
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
            return

          for button in buttons:
            await choice.remove_reaction(button, ctx.author)

          j = json.dumps(users, indent=4)
          with open("accounts.json", "w") as f:
            f.write(j)
            f.close()
            return

      else:
        if trust >= -5:
          # TODO: Insert better enemy pick functionality here
          thisEnemy = enemyDict.get(
            areaDict.get(users[str(user.id)]["area"]).getRandomEncounter())
          print(thisEnemy.name)

          # Exiting script if there is no enemy in the indicated area
          if thisEnemy == None:
            await ctx.reply("There are no enemies in this area.")
            return

          enemy_battle_hp = int(thisEnemy.health)
          enemy_gold = int(thisEnemy.gold)
          enemy_exp = int(thisEnemy.exp)

          explore1 = discord.Embed(
            title=
            f"**{ctx.author} vs {thisEnemy.name}** [LVL {thisEnemy.level}]",
            description=
            f"{thisEnemy.name}'s Health: {thisEnemy.health} \n \ndo you wish to fight?",
            colour=discord.Colour.default())

          explore2 = discord.Embed(
            title=
            f"**{ctx.author} vs {thisEnemy.name}** [LVL {thisEnemy.level}]",
            colour=discord.Colour.default(),
            description=f"Prepare to fight {thisEnemy.name}!")
          explore2.add_field(name=f"{ctx.author}'s health",
                             value=battlehealth_amt)
          explore2.add_field(name=f"{thisEnemy.name}'s health",
                             value=enemy_battle_hp)

          explore3 = discord.Embed(
            title=f"**{ctx.author} has won against {thisEnemy.name}**",
            description=
            f"Have earned {thisEnemy.gold} gold and {thisEnemy.exp} experience."
          )
          explore3.add_field(name=f"Items Dropped:", value="none")

          explore4 = discord.Embed(
            title=f"**{ctx.author} has lost against {thisEnemy.name}**",
            description=f"You have lost, nothing has been rewarded")

          explore5 = discord.Embed(title=f"**{ctx.author} has ran away**")
          explore7 = discord.Embed(title=f"**Exploring...**")
          explore8 = discord.Embed(title=f"**Removed Previous Fight.**")

          users[str(user.id)]["cmd_use"] = 1
          j = json.dumps(users, indent=4)
          with open("accounts.json", "w") as f:
            f.write(j)
            f.close()

          buttons = ["🪓", "🏃"]
          current1 = explore1
          msg1 = await ctx.send(embed=explore7)
          msg2 = msg1
          await msg1.edit(embed=current1)
          users[str(user.id)]["cmd_in_use"] = int(msg1.id)
          j = json.dumps(users, indent=4)
          with open("accounts.json", "w") as f:
            f.write(j)
            f.close()

          for button in buttons:
            await msg1.add_reaction(button)

          try:
            reaction, user = await client.wait_for(
              "reaction_add",
              check=lambda reaction, user: user == ctx.author and reaction.
              message == msg1 and reaction.emoji in buttons,
              timeout=30.0)

          except asyncio.TimeoutError:
            # Deactivates the message after 30 seconds, and exits the function
            embed = current1
            current1.set_footer(text="Timed out.")
            await msg1.clear_reactions()
            await msg1.edit(embed=current1)
            users[str(user.id)]["cmd_use"] = 0
            j = json.dumps(users, indent=4)
            with open("accounts.json", "w") as f:
              f.write(j)
              f.close()
              return

          else:  #attack enemy
            await msg1.edit(embed=current1)
            await msg1.clear_reactions()

            previous_page = current1

            if reaction.emoji == "🪓":
              if users[str(user.id)]["cmd_use"] == 1:
                current1 = explore2
                combat = 1
              else:
                await msg1.clear_reactions()
                await msg1.edit(embed=explore8)

              #run away
            elif reaction.emoji == "🏃":
              current1 = explore5
              combat = 0
              users[str(user.id)]["cmd_use"] = 0
              j = json.dumps(users, indent=2)
              with open("accounts.json", "w") as f:
                f.write(j)
                f.close()
              await msg1.edit(embed=explore5)
              await msg1.clear_reactions()

            for button in buttons:
              await msg1.remove_reaction(button, ctx.author)

            if current1 == explore2:
              await msg1.edit(embed=current1)
              buttons = ["🗡️", "⚔️", "🛡️"]
              for button in buttons:
                await msg1.add_reaction(button)
              while True:

                try:
                  reaction, user = await client.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: user == ctx.author and
                    reaction.message == msg1 and reaction.emoji in buttons,
                    timeout=30.0)

                except asyncio.TimeoutError:
                  embed = current1
                  # Deactivates the message after 30 seconds, and exits the function
                  # current1.set_footer(text="Timed out.")
                  await msg1.clear_reactions()
                  await msg1.edit(embed=current1)
                  users[str(user.id)]["cmd_use"] = 0
                  j = json.dumps(users, indent=2)
                  with open("accounts.json", "w") as f:
                    f.write(j)
                    f.close()
                  return
                if combat == 1:
                  if battlehealth_amt >= 1:
                    if reaction.emoji == "🗡️":
                      # Damage calculation happens here
                      enemyaction = thisEnemy.getNodeAction(enemynode)
                      enemynode = int(enemyaction[2])
                      # Damage dealt to player reduced by defense to a minimum of 1, applying damage
                      playerdmgtaken = int(enemyaction[1]) - int(users[str(
                        user.id)]["defense"])
                      if playerdmgtaken < 1: playerdmgtaken = 1
                      battlehealth_amt -= playerdmgtaken
                      # Damage dealt to enemy reduced by defense to a minimum of 1, applying damage
                      damage_dealt = (random.randint(
                        mindmg_amt, maxdmg_amt)) - thisEnemy.defense
                      if damage_dealt < 1: damage_dealt = 1
                      enemy_battle_hp -= damage_dealt
                      # Further processing
                      explore6 = discord.Embed(
                        title=
                        f"**{ctx.author} vs {thisEnemy.name}** [LVL {thisEnemy.level}]",
                        colour=discord.Colour.default(),
                        description=
                        f"{enemyaction[0]} and did {enemyaction[1]} damage!\nYou do a regular attack which does {damage_dealt} damage!"
                      )
                      explore6.add_field(name=f"{ctx.author}'s health",
                                         value=battlehealth_amt)
                      explore6.add_field(name=f"{thisEnemy.name}'s health",
                                         value=enemy_battle_hp)
                      explore2 = await msg1.edit(embed=explore6)
                      explore2 = current1
                      for button in buttons:
                        await msg1.remove_reaction(button, ctx.author)
                      # Script to handle player loss in combat
                      if battlehealth_amt < 1:
                        print("Lossflag")
                        combat = 0
                        users[str(user.id)]["cmd_use"] = 0
                        j = json.dumps(users, indent=2)
                        with open("accounts.json", "w") as f:
                          f.write(j)
                          f.close()
                        users[str(user.id)]["gold"] -= (thisEnemy.gold / 2)
                        current1 = explore4
                        if current1 != previous_page:
                          await msg1.edit(embed=current1)
                          await msg1.clear_reactions()
                          battlehealth_amt = health_amt

                      # Script to handle player victory in combat
                      elif enemy_battle_hp < 1:
                        print("Victoryflag")
                        enemy_battle_hp = thisEnemy.health
                        users[str(user.id)]["gold"] += enemy_gold
                        users[str(user.id)]["exp"] += enemy_exp
                        users[str(user.id)]["battlehealth"] = users[str(
                          user.id)]["health"]
                        # Checking whether dropped item is already present in player inventory
                        # TODO: Automate item addition and subtraction. This is ridiculous.
                        # Item drop algorithm

                        for cdrop in random.sample(thisEnemy.itemdrops,
                                                   k=len(thisEnemy.itemdrops)):
                          if random.randint(1, 100) <= int(cdrop["chance"]):
                            # Checking whether dropped item is already present in player inventory
                            # TODO: Remove the ever-present massive redundancies. Shit's painful.
                            if users[str(user.id)]["inventory"].get(
                                cdrop["name"]) != None:
                              users[str(
                                user.id)]["inventory"][cdrop["name"]] += 1
                            else:
                              users[str(
                                user.id)]["inventory"][cdrop["name"]] = 1
                            break
                        current1 = explore3
                        if current1 != previous_page:
                          await msg1.edit(embed=current1)
                          combat = 0
                          users[str(user.id)]["cmd_use"] = 0
                          await msg1.clear_reactions()
                          j = json.dumps(users, indent=2)
                          with open("accounts.json", "w") as f:
                            f.write(j)
                            f.close()
                          return
                    elif reaction.emoji == "⚔️":
                      enemyaction = thisEnemy.getNodeAction(enemynode)
                      enemynode = int(enemyaction[2])
                      # Damage dealt to player reduced by defense to a minimum of 1, applying damage
                      playerdmgtaken = int(round(enemyaction[1] * 1.5)) - int(
                        users[str(user.id)]["defense"])
                      if playerdmgtaken < 1: playerdmgtaken = 1
                      battlehealth_amt -= playerdmgtaken
                      # Damage dealt to enemy reduced by defense to a minimum of 1, applying damage
                      damage_dealt = (random.randint(
                        (round(mindmg_amt * 1.25)), round(
                          (maxdmg_amt * 1.25)))) - thisEnemy.defense
                      if damage_dealt < 1: damage_dealt = 1
                      enemy_battle_hp -= damage_dealt
                      # Further processing
                      explore6 = discord.Embed(
                        title=
                        f"**{ctx.author} vs {thisEnemy.name}** [LVL {thisEnemy.level}]",
                        colour=discord.Colour.default(),
                        description=
                        f"{enemyaction[0]} and did {enemyaction[1]} damage!\n You perform a heavy attack dealing {round(damage_dealt)} damage!"
                      )
                      explore6.add_field(name=f"{ctx.author}'s health",
                                         value=battlehealth_amt)
                      explore6.add_field(name=f"{thisEnemy.name}'s health",
                                         value=enemy_battle_hp)
                      explore2 = await msg1.edit(embed=explore6)
                      explore2 = current1
                      for button in buttons:
                        await msg1.remove_reaction(button, ctx.author)
                      # Script to handle player loss in combat
                      if battlehealth_amt < 1:
                        print("Lossflag")
                        combat = 0
                        users[str(user.id)]["cmd_use"] = 0
                        j = json.dumps(users, indent=2)
                        with open("accounts.json", "w") as f:
                          f.write(j)
                          f.close()
                        users[str(user.id)]["gold"] -= (thisEnemy.gold / 2)
                        current1 = explore4
                        if current1 != previous_page:
                          await msg1.edit(embed=current1)
                          await msg1.clear_reactions()
                          battlehealth_amt = health_amt

                      # Script to handle player victory in combat
                      elif enemy_battle_hp < 1:
                        print("Victoryflag")
                        enemy_battle_hp = thisEnemy.health
                        users[str(user.id)]["gold"] += enemy_gold
                        users[str(user.id)]["exp"] += enemy_exp
                        users[str(user.id)]["battlehealth"] = users[str(
                          user.id)]["health"]
                        # Item drop algorithm
                        for cdrop in random.sample(thisEnemy.itemdrops,
                                                   k=len(thisEnemy.itemdrops)):
                          if random.randint(1, 100) <= int(cdrop["chance"]):
                            # Checking whether dropped item is already present in player inventory
                            # TODO: Remove the ever-present massive redundancies. Shit's painful.
                            itempresent = False
                            if len(users[str(user.id)]["inventory"]) > 0:
                              for citem in users[str(user.id)]["inventory"]:
                                if citem[0] == cdrop[0]:
                                  itempresent = True
                                  citem[1] += 1
                                  break
                            if not itempresent:
                              users[str(user.id)]["inventory"].append(
                                {cdrop.name, 1})
                            break
                        current1 = explore3
                        if current1 != previous_page:
                          await msg1.edit(embed=current1)
                          combat = 0
                          users[str(user.id)]["cmd_use"] = 0
                          await msg1.clear_reactions()
                          j = json.dumps(users, indent=2)
                          with open("accounts.json", "w") as f:
                            f.write(j)
                            f.close()
                          return

                    #Handles Defending yourself
                    elif reaction.emoji == "🛡️":
                      enemyaction = thisEnemy.getNodeAction(enemynode)
                      enemynode = int(enemyaction[2])
                      battlehealth_amt -= int(enemyaction[1] / 4)
                      explore6 = discord.Embed(
                        title=
                        f"**{ctx.author} vs {thisEnemy.name}** [LVL {thisEnemy.level}]",
                        colour=discord.Colour.default(),
                        description=
                        f"{enemyaction[0]} and did {enemyaction[1]} damage! \nYou guard yourself, resulting in the enemy doing less damage!"
                      )
                      explore6.add_field(name=f"{ctx.author}'s health",
                                         value=battlehealth_amt)
                      explore6.add_field(name=f"{thisEnemy.name}'s health",
                                         value=enemy_battle_hp)
                      explore2 = await msg1.edit(embed=explore6)
                      explore2 = current1
                      for button in buttons:
                        await msg1.remove_reaction(button, ctx.author)
                      # Script to handle player loss in combat
                      if battlehealth_amt < 1:
                        print("Lossflag")
                        combat = 0
                        users[str(user.id)]["gold"] -= (thisEnemy.gold / 2)
                        current1 = explore4
                        if current1 != previous_page:
                          await msg1.edit(embed=current1)
                          await msg1.clear_reactions()
                          users[str(user.id)]["cmd_use"] = 0
                          j = json.dumps(users, indent=2)
                          with open("accounts.json", "w") as f:
                            f.write(j)
                            f.close()
                          battlehealth_amt = health_amt
                          return

                      # Script to handle player victory in combat
                      elif enemy_battle_hp < 1:
                        print("Victoryflag")
                        enemy_battle_hp = thisEnemy.health
                        users[str(user.id)]["gold"] += enemy_gold
                        users[str(user.id)]["exp"] += enemy_exp
                        users[str(user.id)]["battlehealth"] = users[str(
                          user.id)]["health"]
                        current1 = explore3
                        if current1 != previous_page:
                          await msg1.edit(embed=current1)
                          users[str(user.id)]["cmd_use"] = 0
                          combat = 0
                          await msg1.clear_reactions()
                          j = json.dumps(users, indent=2)
                          with open("accounts.json", "w") as f:
                            f.write(j)
                            f.close()
                          return

        else:
          await ctx.reply("Your trust factor is too low to explore.")

        j = json.dumps(users, indent=4)
        with open("accounts.json", "w") as f:
          f.write(j)
          f.close()

  else:
    users[str(user.id)]["cmd_use"] = 0
    await ctx.reply("Removed last explore")
    j = json.dumps(users, indent=4)
    with open("accounts.json", "w") as f:
      f.write(j)
      f.close()
    previous_cmd = await ctx.fetch_message(users[str(user.id)]["cmd_in_use"])
    current1 = explore8
    await previous_cmd.edit(embed=current1)
    await previous_cmd.clear_reactions()
    return


explore.triggers = ["explore", "e"]


# Function for adding a specified amount of a specified item to a specified user's inventory
async def inventoryadd(user, item, amount):
  users = await get_accounts_data()
  if users[str(user.id)]["inventory"].get(item["name"]) != None:
    users[str(user.id)]["inventory"][item["name"]] += amount
  else:
    users[str(user.id)]["inventory"][item["name"]] = amount


# Function for removing a specified amount of a specified item from a specified user's inventory
# Returns False if updated item amount would be negative.
async def inventoryremove(user, item, amount):
  users = await get_accounts_data()
  if users[str(user.id)]["inventory"].get(item["name"]) >= amount:
    users[str(user.id)]["inventory"][item["name"]] -= amount
  else:
    return False


async def shutdown(ctx):
  if byAdmin(ctx): quit()


shutdown.triggers = ["shutdown"]


def dumpareadict():
  global areaDict
  j = jsonpickle.encode(areaDict, indent=2)
  with open("areadict.json", "w") as f:
    f.write(j)
    f.close()


def dumpenemydict():
  global enemyDict
  j = jsonpickle.encode(enemyDict, indent=2)
  with open("enemies.json", "w") as f:
    f.write(j)
    f.close()


def dumpitemdict():
  global itemDict
  j = jsonpickle.encode(itemDict, indent=2)
  with open("items.json", "w") as f:
    f.write(j)
    f.close()


def dumpaccountdict(users):
  j = jsonpickle.encode(users, indent=2)
  with open("accounts.json", "w") as f:
    f.write(j)
    f.close()


# Returns the one string from the list matchlist that contains the string matchstring, or None if there are several or no matches
def pickClosest(matchstring, matchlist):
  # Running provided values through pickAllMatching()
  fitting = pickAllMatching(matchstring, matchlist)
  # Returning the fitting match, or None if there are several or none
  if len(fitting) != 1: return None
  else: return fitting[0]


#Returns all strings from the list matchlist that contain the string matchstring
def pickAllMatching(matchstring, matchlist):
  fitting = []
  for entry in matchlist:
    # Adding entry to list of fitting entries, if appropriate
    if (entry.lower().find(matchstring.lower()) != -1):
      fitting.append(entry)
  return fitting

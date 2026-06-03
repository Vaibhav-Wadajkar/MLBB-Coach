from flask import Flask, jsonify, request, render_template_string
import pandas as pd
import io

app = Flask(__name__)

HEROES_CSV = """Hero_ID,Hero_Name,Hero_Title,Role,Lane
1,Miya,the Moonlight Archer,Marksman,Gold
2,Balmond,the Bloody Beast,Fighter/Tank,EXP
3,Saber,the Wandering Sword,Assassin,Roam/Mid
4,Alice,the Queen of Blood,Mage/Tank,Mid
5,Nana,the Sweet Leonin,Mage/Support,Roam
6,Tigreal,the Warrior of Dawn,Tank,Roam
7,Alucard,the Demon Hunter,Fighter,EXP
8,Karina,the Shadow Blade,Assassin,Jungle
9,Akai,the Panda Warrior,Tank,Roam
10,Franco,the Frozen Warrior,Tank,Roam
11,Bruno,the Protector,Marksman,Gold
12,Clint,the West Justice,Marksman,Gold
13,Rafaela,the Wings of Holiness,Support,Roam
14,Eudora,the Lightning Weaver,Mage,Mid
15,Zilong,the Spear of Dragon,Fighter,EXP
16,Fanny,the Blade Dancer,Assassin,Jungle
17,Layla,the Energy Gunner,Marksman,Gold
18,Hayabusa,the Crimson Shadow,Assassin,Jungle
19,Gusion,the Holy Blade,Assassin,Jungle
20,Wanwan,the Agile Tiger,Marksman,Gold
21,Lancelot,the Blade of Roses,Assassin,Jungle
22,Claude,the Master Thief,Marksman,Gold
23,Granger,the Death Chanter,Marksman/Assassin,Gold
24,Brody,the Lone Star,Marksman,Gold
25,Beatrix,the Dawnbreak Soldier,Marksman,Gold
26,Ixia,the Arclight Outlaw,Marksman,Gold
27,Ling,the Cyan Finch,Assassin,Jungle
28,Chou,the Kung Fu Boy,Fighter,EXP
29,Paquito,the Heavenly Fist,Fighter,EXP
30,Yu Zhong,the Black Dragon,Fighter,EXP
31,Esmeralda,the Astrologer,Mage/Tank,EXP/Roam
32,Fredrinn,the Rogue Appraiser,Fighter/Tank,EXP
33,Badang,the Tribal Warrior,Fighter,EXP
34,Thamuz,the Lord Lava,Fighter,EXP
35,Ruby,the Little Red Hood,Fighter,EXP
36,Khufra,the Desert Tyrant,Tank,Roam
37,Atlas,the Ocean Gladiator,Tank,Roam
38,Grock,the Fortress Titan,Tank,Roam
39,Baxia,the Mystic Tortoise,Tank,Roam
40,Johnson,the Wild Engine,Tank,Roam
41,Hylos,the Grand Warden,Tank,Roam
42,Uranus,the Aesthereal Defender,Tank,Roam
43,Belerick,the Guard of Nature,Tank,Roam
44,Edith,the Ancient Guard,Tank/Marksman,Roam/EXP
45,Gloo,the Swamp Spirits,Tank,Roam
46,Cyclops,the Starsoul Magician,Mage,Mid
47,Lunox,the Twilight Goddess,Mage,Mid
48,Lylia,the Little Witch,Mage,Mid
49,Vale,the Windtalker,Mage,Mid
50,Xavier,the Defier of Light,Mage,Mid
51,Kagura,the Onmyouji Master,Mage,Mid
52,Harith,the Time Traveler,Mage,Mid
53,Yve,the Astrowarden,Mage,Mid
54,Novaria,the Star Rebel,Mage,Mid
55,Chang'e,the Moon Palace Immortal,Mage,Mid
56,Aurora,the Maiden of the Glacier,Mage,Mid
57,Valentina,the Prophetess of the Night,Mage,Mid
58,Estes,the Moon Elf King,Support,Roam
59,Angela,the Bunnylove,Support,Roam
60,Diggie,the Timekeeper,Support,Roam
61,Mathilda,the Swift Plume,Support,Roam
62,Floryn,the Budding Hope,Support,Roam
63,Faramis,the Soul Binder,Support,Roam"""

COUNTERS_CSV = """Hero_Name,Strong_Against,Weak_Against,Best_Partner,Playstyle,Tier
Miya,Layla / Johnson,Natalia / Saber / Fanny,Diggie / Mathilda,Late-Game Hypercarry,A
Bruno,Miya / Layla,Khufra / Franco,Tigreal / Angela,Burst + Crit Carry,A
Clint,Miya / Layla,Khufra / Chou,Angela / Rafaela,Poke + Burst,B
Layla,Early Squishies,Any Assassin,Any Tank,Safe Farmer,B
Beatrix,Tigreal / Minotaur,Natalia / Saber,Diggie / Mathilda,Versatile Range Carry,S
Wanwan,Tigreal / Akai,Phoveus / Khufra,Franco / Kaja,Dash Attack Speed Carry,S
Claude,Crowd-Controlled Heroes,Burst Assassins,Diggie / Johnson,Late Hypercarry,S
Granger,Squishy Mages,Franco / Khufra,Angela / Diggie,Early Burst Carry,S
Brody,Tanky Heroes,High Mobility,Tigreal / Atlas,Slow Poke Carry,A
Ixia,Grouped Enemies,Burst Assassins,Angela / Diggie,DPS Carry,A
Fanny,Layla / Miya,Khufra / Saber / Kaja,Angela / Diggie,High Mobility Jungler,S
Gusion,Hanabi / Layla,Khufra / Chou,Angela / Saber,Burst Pick-off,S
Lancelot,Squishy Targets,Khufra / Chou,Angela / Diggie,Burst Assassin,S
Hayabusa,Squishy Targets,Khufra / Franco,Angela / Diggie,Split Push Assassin,A
Ling,Squishy Targets,Franco / Tigreal,Diggie / Angela,High Mobility Jungler,S
Karina,Low HP Heroes,Khufra / Atlas,Angela / Diggie,Execution Jungler,A
Saber,Single Target Heroes,Franco / Khufra,Angela / Diggie,Single Pick Assassin,A
Chou,Squishy Heroes,Phoveus,Angela / Diggie,Fighter Assassin,S
Tigreal,Grouped Teams,Diggie / Akai,Odette / Claude,Setup Tank,S
Khufra,Dash Heroes,Squishy Targets,Guinevere / Fanny,Anti-Dash Tank,S
Atlas,Grouped Teams,Diggie / Phoveus,Granger / Brody,Chain CC Tank,S
Franco,Squishy Targets,Purify Heroes,Fanny / Gusion,Hook Tank,A
Akai,Grouped Teams,Ranged Heroes,Gusion / Fanny,Spin Tank,B
Johnson,Squishy Targets,Purify Heroes,Odette / Gusion,Crash Combo Tank,A
Gloo,Squishy Targets,Burst Mages,Any Mage,Split Push Tank,B
Esmeralda,Shielded Heroes,Burst Assassins,Angela / Diggie,Shield Mage Tank,A
Fredrinn,Physical Burst,Magic Burst,Tigreal / Angela,Tanky Fighter,A
Yu Zhong,Fighter Battles,Burst Assassins,Atlas / Tigreal,Sustain Fighter,A
Badang,Walled Areas,High Mobility,Odette / Yve,Wall Stun Fighter,B
Thamuz,Tanks / Fighters,Ranged Heroes,Tigreal / Atlas,Burn Fighter,A
Ruby,Grouped Enemies,Ranged Heroes,Angela / Tigreal,Lifesteal Fighter,A
Alucard,Squishy Heroes,CC Mages,Angela / Diggie,Lifesteal Fighter,B
Estes,Sustained Fights,Burst Teams,Any Tank,Heal Support,A
Angela,Any Ally,Burst Assassins,Fanny / Esmeralda,Shield Attach Support,S
Diggie,CC Comps,Burst Teams,Any Marksman,Anti-CC Support,S
Mathilda,Allied Ganks,Burst Teams,Jungler Allies,Assist Dash Support,A
Lunox,High HP Teams,Burst Assassins,Atlas / Tigreal,Chaos Burst Mage,S
Kagura,Grouped Teams,Mobile Assassins,Tigreal / Atlas,Skill Chain Mage,S
Harith,Dash Heroes,CC Teams,Angela / Diggie,Mobile Mage,A
Xavier,Long Range Targets,Assassins,Tigreal / Atlas,Global Snipe Mage,A
Yve,Grouped Teams,Assassins,Tigreal / Khufra,Zone Control Mage,A
Chang'e,Sustained Fights,Assassins,Tigreal / Atlas,Buff Burst Mage,B"""

SPELLS_CSV = """Spell_Name,Cooldown,Best_For,Effect
Execute,90s,Assassins / Fighters,Deals True Damage based on enemy missing HP. Best for securing kills.
Retribution,35s,Junglers (mandatory),Deals true damage to monsters; upgrades with Jungler Boots.
Inspire,75s,Marksmen,Greatly boosts Attack Speed and ignores Physical Defense temporarily.
Sprint,100s,Any,Grants 50% Movement Speed and slow immunity for 6 seconds.
Revitalize,85s,Support,Summons a healing spring that restores HP to all allies inside.
Aegis,90s,Support / Tank,Instantly grants a powerful shield to caster and nearby ally.
Petrify,90s,Mage / Tank,Deals Magic Damage and petrifies nearby enemies for 0.8s.
Purify,90s,Marksman / Mage,Removes all CC effects immediately; grants CC immunity for 1.2s.
Flameshot,50s,Mage / Marksman,Knocks back nearby enemies and fires a long-range magic missile.
Flicker,120s,Any,Teleports a short distance; versatile escape and engage tool.
Arrival,75s,Tank / Support,Teleports to any friendly turret or minion on the map.
Vengeance,75s,Tank,Reflects 35% of damage taken back to attackers for 3 seconds."""

MAP_CSV = """Objective,Spawn,Respawn,Benefit,Zone
Blue Buff,0:20,1:30,Reduces Cooldown by 10% and cuts Mana costs. Priority for Mages and Junglers.,Jungle
Red Buff,0:20,1:30,Basic attacks slow enemies and deal extra True Damage. Great for Fighters/Junglers.,Jungle
Gold Crab,0:45,1:00,Spawns in Gold Lane. Grants a steady passive gold stream.,Gold Lane
Lithowanderer,0:45,0:45,Walks around river granting map vision and a small HP regen buff.,River
Turtle,2:00,2:00,Massive team Gold and EXP reward. Grants a shield and attack boost to the team.,River Center
Lord (Base),8:00,3:00,Pushes the weakest lane when your team kills it.,Enemy Base Side
Lord (Enhanced),12:00,3:00,Gains a Charge ability; can instantly crash turrets.,Enemy Base Side
Lord (Evolved),18:00,3:00,Max power Lord with high damage reduction — the game-ending objective.,Enemy Base Side"""

ITEMS_CSV = """Item_Name,Type,Cost,Key_Stats,Passive_Effect,Best_For
Swift Boots,Boots,710,+40 MS / +15% AS,—,Marksman
Demon Shoes,Boots,720,+40 MS / +6 Mana Regen,Mysticism: kills restore mana,Mage
Tough Boots,Boots,700,+40 MS / +22 Magic Def,Fortitude: reduces CC duration 30%,Tank/Fighter needing CC resist
Warrior Boots,Boots,720,+40 MS / +22 Phys Def,Valor: increases Phys Def on hit,Tank/Fighter
Windtalker,Marksman,1820,+40% AS / +20 MS,Typhoon: attacks hit multiple enemies,Miya / Wanwan / Clint
Berserker's Fury,Marksman,2350,+65 Phys Atk / +25% Crit,Doom: Crits deal extra True Damage,Crit Carries
Haas's Claws,Marksman,1810,+70 Phys Atk / +20% Lifesteal,Insanity: Lifesteal increases at low HP,Sustain Carries
Malefic Roar,Marksman,2060,+60 Phys Atk / 40% Phys Pen,Armor Buster: extra penetration vs high-armor targets,Late-game Carries
Demon Hunter Sword,Marksman,2180,+35 Phys Atk / +25% AS,Devour: deals extra HP% damage per hit,Anti-Tank Carries
Immortality,Defense,2120,+800 HP / +20 Phys Def,Immortal: resurrects after death with 15% HP,Any (last slot)
Blade of Despair,Marksman,3010,+160 Phys Atk / +5% MS,Despair: +25% damage to enemies below 50% HP,Assassin / Carry finisher
Thunder Belt,Defense/Fighter,1990,+800 HP / +30 Def / +10% CDR,Thunderbolt: basic attack after skill deals True Damage,Tank / Fighter
Holy Crystal,Magic,2180,+100 Magic Power,Mystery: boosts MP by up to 35%,Burst Mage
Lightning Truncheon,Magic,2250,+75 MP / +400 Mana,Resonate: skill echoes dealing bonus Magic Damage,Mage
Genius Wand,Magic,2000,+75 MP / +5% MS,Magic Justice: reduces enemy Magic Defense on hit,Mage
Winter Crown,Magic,1910,+60 MP / +400 HP,Frozen: active 2-second invincibility (frozen in place),Mage survival tool
Dominance Ice,Defense,2010,+500 Mana / +70 Phys Def,Arctic Cold: reduces enemy AS and healing by 50%,Anti-heal tank
Guardian Helmet,Defense,2200,+1550 HP / +20 HP Regen,Recovery: regenerates HP passively out of combat,Frontline Tank
Oracle,Defense,2060,+850 HP / +42 Magic Def / +10% CDR,Bless: boosts shielding and healing by 30%,Support / Healing tank"""

BUILDS_CSV = """Hero_Name,Spell,Item1,Item2,Item3,Item4,Item5,Item6,Skill_Combo,Tips
Miya,Inspire,Swift Boots,Windtalker,Berserker's Fury,Haas's Claws,Malefic Roar,Immortality,Skill 3 (Invis) ➔ Skill 2 (CC) ➔ Basic Attacks + Skill 1,Stay at max range. Activate Invis to reposition in teamfights. Prioritize last-hits early.
Bruno,Inspire,Swift Boots,Windtalker,Berserker's Fury,Malefic Roar,Haas's Claws,Immortality,Skill 2 (Chase) ➔ Skill 1 (Ricochet) ➔ Basic Attacks,Use Skill 1 to hit multiple enemies. Chain kills boost Movement Speed.
Clint,Inspire,Swift Boots,Windtalker,Berserker's Fury,Malefic Roar,Haas's Claws,Immortality,Skill 1 (Poke) ➔ Basic Attack ➔ Skill 2 (Dash) ➔ Skill 1 repeat,Stay behind minions. Skill 1 pierces — lineup shots carefully.
Layla,Inspire,Swift Boots,Windtalker,Berserker's Fury,Malefic Roar,Demon Hunter Sword,Immortality,Basic Attacks ➔ Skill 1 ➔ Skill 2 to escape,Stay FAR from enemies. Longest range in game. Never fight without a tank nearby.
Beatrix,Inspire,Swift Boots,Berserker's Fury,Malefic Roar,Demon Hunter Sword,Haas's Claws,Immortality,Sniper: Skill 2 (Long range snipe) → Shotgun: Skill 1 (close burst) → Switch weapons situationally,Switch weapons based on situation. Sniper for poke; Shotgun for burst; SMG for teamfights.
Wanwan,Inspire,Swift Boots,Windtalker,Berserker's Fury,Demon Hunter Sword,Malefic Roar,Immortality,Skill 1 (Throw) ➔ Skill 2 (Dash) ➔ Repeat to hit all Weakpoints ➔ Skill 3 (Ult),Hit all 4 weakpoints to unlock Ultimate. Dash repeatedly to proc Windtalker stacks.
Claude,Inspire,Swift Boots,Demon Hunter Sword,Berserker's Fury,Windtalker,Haas's Claws,Immortality,Skill 1 (Mark) ➔ Skill 2 (Swap to pet) ➔ Skill 3 (AoE Ult) ➔ Basic Attacks,Position pet for safe AoE damage. Swap to escape. Ultimate has massive AoE — use in grouped teamfights.
Granger,Inspire,Swift Boots,Berserker's Fury,Malefic Roar,Haas's Claws,Blade of Despair,Immortality,Skill 2 (Dash) ➔ Skill 1 (Bullets) ➔ Basic Attack (6th = enhanced) ➔ Ult for finishing,6th bullet per clip is always a Crit. Time basic attacks carefully. Ult executes low-HP enemies.
Brody,Flicker,Warrior Boots,Windtalker,Berserker's Fury,Malefic Roar,Haas's Claws,Immortality,Skill 1 (Stack) ➔ Basic Attack (Enhanced) ➔ Skill 2 (Stun) ➔ Ult (Global),Stack Abyss marks to 4 for massive slow. Ult targets marked enemies globally for burst.
Ixia,Inspire,Swift Boots,Windtalker,Berserker's Fury,Demon Hunter Sword,Malefic Roar,Immortality,Skill 1 (Buff) ➔ Skill 2 (Slow) ➔ Ult (AoE DPS),Stay safe behind teammates. Ult does massive sustained AoE damage — best in grouped fights.
Fanny,Retribution,Warrior Boots,Blade of Despair,Endless Battle,Berserker's Fury,Malefic Roar,Immortality,Blue Buff Secure ➔ Skill 2 (Cable) ➔ Skill 1 (AoE Slash) ➔ Ult when surrounded,Requires energy management. Always secure Blue Buff first. Practice cable aim separately.
Gusion,Retribution,Arcane Boots,Blade of Despair,Calamity Reaper,Holy Crystal,Genius Wand,Immortality,Skill 1 (Mark) ➔ Skill 2 (Dash In) ➔ Skill 1 (Detonate) ➔ Ult (Reset) ➔ Repeat,All skills must hit in under 2 seconds for full burst. Practice the combo extensively in training mode.
Lancelot,Retribution,Warrior Boots,Blade of Despair,Endless Battle,Hunter Strike,Malefic Roar,Immortality,Skill 1 (Pierce) ➔ Skill 2 (Dance) ➔ Ult (Invincible strike) ➔ Finish with Skill 1,Ult makes you invincible during animation — use it to dodge ultimates. Very skill-intensive hero.
Hayabusa,Retribution,Warrior Boots,Blade of Despair,Hunter Strike,Malefic Roar,Endless Battle,Immortality,Skill 3 (Shadow Deploy) ➔ Skill 1 ➔ Skill 2 (Shadow Dash) ➔ Ult (Lock),Deploy shadows first to spread damage. Ult locks target in place — combo with shadows for burst.
Ling,Retribution,Warrior Boots,Blade of Despair,Hunter Strike,Malefic Roar,Endless Battle,Immortality,Skill 1 (Wall Hop) ➔ Skill 2 (Strike) ➔ Ult (AoE Freeze),Hop between walls to generate sword energy. Ult freezes enemies — combo with burst after.
Tigreal,Flicker,Warrior Boots,Dominance Ice,Guardian Helmet,Antique Cuirass,Oracle,Immortality,Skill 2 (Charge) ➔ Skill 1 (Pull) ➔ Ult (Stun Lock),Combo must land in 1.5 seconds. Flicker + Ult for surprise engage. Protect your carries always.
Khufra,Flicker,Warrior Boots,Dominance Ice,Guardian Helmet,Antique Cuirass,Thunder Belt,Immortality,Skill 2 (Ball Bounce) ➔ Skill 1 (Hook Pull) ➔ Ult (Stun),Ball form blocks all dashes. Position between enemy dasher and escape route. Use Flicker + Ult combo.
Atlas,Flicker,Warrior Boots,Cursed Helmet,Guardian Helmet,Dominance Ice,Oracle,Immortality,Skill 2 (Chain Link) ➔ Walk into enemies ➔ Skill 1 ➔ Flicker + Ult (Massive Pull),Chain multiple enemies first. Flicker + Ult for surprise pulls. Team needs follow-up burst immediately.
Franco,Flicker,Warrior Boots,Dominance Ice,Guardian Helmet,Antique Cuirass,Thunder Belt,Immortality,Skill 1 (Hook) ➔ Skill 2 (Suppress Ult) ➔ Team Follows Up,Aim hooks in bushes. Ult suppresses for 2.8s — tell team to follow up immediately. Roam between lanes constantly.
Angela,Flicker,Magic Shoes,Oracle,Courage Bulwark,Immortality,Fleeting Time,Necklace of Durance,Skill 2 (Slow Shield) ➔ Skill 1 (Heal) ➔ Ult (Attach to Ally),Attach to your best teammate before fights. Shield + Slow from Skill 2 has huge impact. Prioritize preventing death over healing.
Diggie,Flicker,Magic Shoes,Oracle,Fleeting Time,Courage Bulwark,Immortality,Ice Retribution,Skill 1 (Bomb) ➔ Skill 2 (Anti-CC Zone) ➔ Ult (Remove all CC from team),Use Ult when enemy uses mass CC (Tigreal/Atlas Ult). Roam everywhere. Place bombs in bushes for vision.
Estes,Sprint,Magic Shoes,Oracle,Fleeting Time,Courage Bulwark,Holy Crystal,Immortality,Skill 1 (Mark) ➔ Skill 2 (AoE Heal) ➔ Ult (Channel Heal),Stay near marked allies for bonus heal. Ult heals in a large AoE — use in sustained teamfights not ambushes.
Lunox,Flicker,Arcane Boots,Lightning Truncheon,Holy Crystal,Blood Wings,Divine Glaive,Immortality,Chaos Mode: Skill 1 ➔ Skill 1 ➔ Skill 2 (Chaos Ult for invincibility) ➔ Repeat,Alternate Order/Chaos skills to stack buffs. Chaos Ult makes you invincible — use to dodge enemy ultimates.
Kagura,Flicker,Arcane Boots,Lightning Truncheon,Holy Crystal,Genius Wand,Necklace of Durance,Immortality,Skill 1 (Umbrella Forward) ➔ Skill 2 (TP to umbrella) ➔ Skill 1 (Pull back) ➔ Ult,Umbrella positioning is key. Skill 2 while umbrella is far = teleport; while near = pull. Very high skill cap.
Esmeralda,Flicker,Magic Shoes,Oracle,Genius Wand,Holy Crystal,Necklace of Durance,Immortality,Skill 2 (Shield) ➔ Skill 1 (AoE Drain) ➔ Ult (Dash),Steal enemy shields for your own. Max HP scales with shield—build HP items work too. Anti-shielded enemy specialist.
Fredrinn,Vengeance,Warrior Boots,Cursed Helmet,Dominance Ice,Guardian Helmet,Oracle,Immortality,Skill 1 (Pull) ➔ Skill 2 (Dash+AoE) ➔ Ult (Uses SP for massive burst),Accumulate Combo Points before using Ult. Ult damage scales with SP—save for teamfights.
Yu Zhong,Execute,Warrior Boots,Cursed Helmet,War Axe,Brute Force Breastplate,Immortality,Blade Armor,Skill 1 (Dragon Soul AoE) ➔ Skill 2 (Dash CC) ➔ Ult (Dragon Form),Dragon form provides massive sustain — use when HP drops below 40%. Never fight 1v1 without some HP in reserve."""

def load_all():
    db = {}
    for key, csv_str in [
        ("heroes", HEROES_CSV),
        ("counters", COUNTERS_CSV),
        ("spells", SPELLS_CSV),
        ("map", MAP_CSV),
        ("items", ITEMS_CSV),
        ("builds", BUILDS_CSV),
    ]:
        db[key] = pd.read_csv(io.StringIO(csv_str.strip()))
    return db

DB = load_all()

ROLE_SPELLS = {
    "Marksman": "Inspire",
    "Assassin": "Retribution",
    "Tank": "Flicker",
    "Support": "Flicker",
    "Mage": "Flicker",
    "Fighter": "Vengeance",
    "Fighter/Tank": "Vengeance",
    "Mage/Tank": "Flicker",
    "Mage/Support": "Flicker",
    "Tank/Marksman": "Flicker",
    "Marksman/Assassin": "Inspire",
}

LANE_TIPS = {
    "Gold": "📍 Play Gold Lane. Farm safely early — avoid trades. Focus on last-hitting minions and securing Gold Crab at 0:45. Turret plating gives bonus gold before 5 mins, so push it carefully.",
    "EXP": "📍 Play EXP Lane. Fight for level advantages. Secure buff camps near your lane. At Level 4, look for TP rotations to help mid/jungle fights.",
    "Mid": "📍 Play Mid Lane. Clear waves fast and rotate to both sides. Secure Blue Buff at 0:20. Be ready to assist jungle objectives at Turtle (2:00).",
    "Jungle": "📍 Play Jungle (Jungler Boots + Retribution mandatory). Path: Blue Buff (0:20) → Red Buff → Level 3 Gank. Secure Turtle at 2:00 with your team. Never fall behind in farm.",
    "Roam": "📍 Play Roam. Buy Roaming Item first. Rotate to gank Gold Lane and Jungle at Level 2-3. Ward bushes near objectives. Your job is to enable carries, not farm.",
    "Roam/EXP": "📍 Flex between Roam and EXP Lane depending on team composition. Prioritize warding and assist plays.",
    "Roam/Mid": "📍 Roam aggressively from Mid Lane. Clear wave fast then rotate for picks.",
    "EXP/Roam": "📍 Flex between EXP Lane and Roam support. Adapt to team needs.",
}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/heroes')
def get_heroes():
    df = DB['heroes']
    result = []
    seen = set()
    for _, r in df.iterrows():
        name = str(r['Hero_Name'])
        if name in seen:
            continue
        seen.add(name)
        result.append({
            "name": name,
            "role": str(r['Role']).split('/')[0],
            "lane": str(r['Lane']),
        })
    return jsonify(sorted(result, key=lambda x: x['name']))

@app.route('/hero/<hname>')
def get_hero(hname):
    df_h = DB['heroes']
    df_c = DB['counters']
    df_b = DB['builds']

    hero_rows = df_h[df_h['Hero_Name'].str.lower() == hname.lower()]
    if hero_rows.empty:
        return jsonify({"error": "Hero not found"}), 404
    hero = hero_rows.iloc[0]

    role = str(hero.get('Role', 'Fighter'))
    lane = str(hero.get('Lane', 'EXP'))
    name = str(hero['Hero_Name'])

    c_row = df_c[df_c['Hero_Name'].str.lower() == name.lower()]
    strong_against = str(c_row.iloc[0]['Strong_Against']) if not c_row.empty else "—"
    weak_against   = str(c_row.iloc[0]['Weak_Against'])   if not c_row.empty else "—"
    best_partner   = str(c_row.iloc[0]['Best_Partner'])   if not c_row.empty else "Any Support"
    playstyle      = str(c_row.iloc[0]['Playstyle'])      if not c_row.empty else "Adaptive"
    tier           = str(c_row.iloc[0]['Tier'])           if not c_row.empty else "B"

    b_row = df_b[df_b['Hero_Name'].str.lower() == name.lower()]
    if not b_row.empty:
        b = b_row.iloc[0]
        spell       = str(b['Spell'])
        items       = [str(b[f'Item{i}']) for i in range(1, 7) if pd.notna(b.get(f'Item{i}'))]
        skill_combo = str(b['Skill_Combo'])
        tips        = str(b['Tips'])
    else:
        spell       = ROLE_SPELLS.get(role, "Flicker")
        items       = ["Warrior Boots", "Blade of Despair", "Endless Battle", "Malefic Roar", "Hunter Strike", "Immortality"]
        skill_combo = "Skill 2 ➔ Skill 1 ➔ Skill 3 (Ult) ➔ Basic Attacks"
        tips        = f"Play {name} according to your role: {role}. Prioritize objectives and support your team."

    lane_tip = LANE_TIPS.get(lane, LANE_TIPS["EXP"])

    return jsonify({
        "name": name,
        "title": str(hero.get('Hero_Title', '')),
        "role": role,
        "lane": lane,
        "tier": tier,
        "playstyle": playstyle,
        "lane_tip": lane_tip,
        "spell": spell,
        "items": items,
        "skill_combo": skill_combo,
        "tips": tips,
        "strong_against": strong_against,
        "weak_against": weak_against,
        "best_partner": best_partner,
    })

@app.route('/gameinfo/<topic>')
def game_info(topic):
    topic = topic.lower()
    if topic == "spells":
        data = DB['spells'].to_dict(orient='records')
    elif topic == "map":
        data = DB['map'].to_dict(orient='records')
    elif topic == "items":
        data = DB['items'].to_dict(orient='records')
    else:
        data = []
    return jsonify(data)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg  = data.get('user_message', '').lower()
    hero = data.get('hero_name', '')

    answers = []

    if any(w in msg for w in ["level", "fast", "exp", "xp", "farm"]):
        answers.append("📈 <b>Fast Level-Up Tips:</b><br>• Last-hit every minion wave for +20% bonus EXP/Gold.<br>• Secure Turtle at <b>2:00</b> for a massive team level boost.<br>• Grab Blue Buff at <b>0:20</b> if you're a Mage or Jungler.")
    if any(w in msg for w in ["item", "build", "equipment"]):
        answers.append(f"⚔️ Select <b>{hero}</b> from the hero list to see their full recommended build, or ask me about a specific item category.")
    if any(w in msg for w in ["spell", "battle spell"]):
        answers.append("🔮 <b>Common Spells:</b><br>• <b>Inspire</b> — Marksmen (Gold Lane)<br>• <b>Retribution</b> — Junglers (mandatory)<br>• <b>Flicker</b> — Tanks, Mages, Supports<br>• <b>Purify</b> — vs heavy CC teams<br>• <b>Execute</b> — Fighters/Assassins for kills")
    if any(w in msg for w in ["turtle", "lord", "objective", "buff"]):
        answers.append("🗺️ <b>Map Objectives Priority:</b><br>1. <b>Blue/Red Buff</b> (0:20) — secure for your Jungler or Mage<br>2. <b>Turtle</b> (2:00) — massive team gold+EXP, fight for it<br>3. <b>Lord</b> (8:00) — kills it to end the game faster<br>4. <b>Outer Turrets</b> — Gold Plating active until 5:00 — destroy them early!")
    if any(w in msg for w in ["counter", "beat", "win against", "how to fight"]):
        answers.append(f"🛡️ Check the <b>Counter Info</b> panel on the right after selecting <b>{hero}</b> — it shows who {hero} is strong/weak against and best synergy partners.")
    if any(w in msg for w in ["rank", "ranking", "mythic", "push"]):
        answers.append("🏆 <b>Rank Push Tips:</b><br>• Play your best 2-3 heroes — don't experiment in ranked.<br>• Play during off-peak hours for easier matchups.<br>• Focus objectives, not kills — turrets and Lord win games.<br>• Mute toxic teammates, stay focused.")
    if any(w in msg for w in ["tip", "guide", "help", "advice", "how"]):
        answers.append(f"💡 <b>General Coaching for {hero}:</b><br>• Master your skill combo before ranked matches.<br>• Always play objectives: Turtle ➔ Lord ➔ Base.<br>• Communicate with your team using quick chat pings.<br>• Watch your minimap every 5 seconds.")

    if not answers:
        answers.append(f"🤖 Ask me about: <b>leveling up</b>, <b>battle spells</b>, <b>map objectives</b>, <b>item builds</b>, <b>counters</b>, or <b>rank tips</b> for {hero if hero else 'any hero'}!")

    return jsonify({"answer": "<br><br>".join(answers)})

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MLBB AI Coach</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Exo+2:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:        #05080f;
    --surface:   #0b1120;
    --surface2:  #111827;
    --surface3:  #182033;
    --border:    rgba(255,255,255,0.06);
    --border2:   rgba(255,255,255,0.11);
    --gold:      #f0c040;
    --gold2:     #d4a017;
    --gold-dim:  #8a6412;
    --gold-glow: rgba(240,192,64,0.12);
    --gold-glow2:rgba(240,192,64,0.06);
    --cyan:      #38d9f5;
    --cyan-dim:  rgba(56,217,245,0.1);
    --red:       #ff5c5c;
    --green:     #4ade80;
    --purple:    #a78bfa;
    --text:      #b8c8e0;
    --text-dim:  #556070;
    --text-white:#f0f4ff;
    --radius:    10px;
    --radius-lg: 16px;
    --font-head: 'Cinzel', serif;
    --font-body: 'Exo 2', sans-serif;
  }

  html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--font-body); font-size: 14px; overflow: hidden; }
  ::-webkit-scrollbar { width: 3px; height: 3px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 99px; }

  .shell {
    display: grid;
    grid-template-rows: 56px 1fr;
    grid-template-columns: 252px 1fr 310px;
    height: 100vh;
  }

  /* ── HEADER ── */
  header {
    grid-column: 1 / -1;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 20px;
    background: linear-gradient(90deg, #060d1a 0%, #0b1525 50%, #060d1a 100%);
    border-bottom: 1px solid rgba(240,192,64,0.2);
    position: relative; z-index: 20;
  }
  header::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
    opacity: 0.4;
  }
  .logo {
    font-family: var(--font-head);
    font-size: 1.3rem; font-weight: 900;
    color: var(--gold);
    letter-spacing: 3px;
    text-transform: uppercase;
    display: flex; align-items: center; gap: 10px;
    text-shadow: 0 0 20px rgba(240,192,64,0.4);
  }
  .logo svg { width: 28px; height: 28px; }
  .header-tabs { display: flex; gap: 3px; }
  .header-tab {
    padding: 7px 15px; border: 1px solid transparent; border-radius: 6px;
    font-size: 12px; font-weight: 600; cursor: pointer;
    color: var(--text-dim); background: none; font-family: var(--font-body);
    letter-spacing: .5px; transition: all .2s; text-transform: uppercase;
  }
  .header-tab:hover { color: var(--gold); border-color: var(--gold-dim); background: var(--gold-glow); }
  .header-tab.active { color: var(--gold); border-color: var(--gold-dim); background: var(--gold-glow); }
  .header-right { font-size: 11px; color: var(--text-dim); letter-spacing: 1px; text-transform: uppercase; }

  /* ── SIDEBAR ── */
  .sidebar {
    background: var(--surface);
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column; overflow: hidden;
  }
  .sidebar-search { padding: 12px; border-bottom: 1px solid var(--border); }
  .sidebar-search input {
    width: 100%; background: var(--surface2);
    border: 1px solid var(--border2); border-radius: 8px;
    color: var(--text); padding: 8px 12px; font-size: 13px;
    font-family: var(--font-body); outline: none; transition: border-color .2s;
  }
  .sidebar-search input:focus { border-color: var(--gold-dim); }
  .sidebar-search input::placeholder { color: var(--text-dim); }
  .role-filters { padding: 8px 12px; display: flex; flex-wrap: wrap; gap: 4px; border-bottom: 1px solid var(--border); }
  .role-chip {
    padding: 3px 9px; border-radius: 99px; border: 1px solid var(--border2);
    font-size: 10px; font-weight: 600; cursor: pointer;
    color: var(--text-dim); background: none; font-family: var(--font-body);
    transition: all .15s; letter-spacing: .5px; text-transform: uppercase;
  }
  .role-chip.active, .role-chip:hover { color: var(--gold); border-color: var(--gold-dim); background: var(--gold-glow); }
  .hero-list { flex: 1; overflow-y: auto; padding: 6px 8px; }
  .hero-item {
    display: flex; align-items: center; gap: 9px;
    padding: 7px 8px; border-radius: 8px; cursor: pointer;
    border: 1px solid transparent; transition: all .15s; margin-bottom: 2px;
  }
  .hero-item:hover { background: var(--surface2); border-color: var(--border2); }
  .hero-item.active { background: var(--gold-glow); border-color: var(--gold-dim); }
  .hero-avatar {
    width: 36px; height: 36px; border-radius: 8px;
    background: var(--surface3);
    border: 1px solid var(--border2);
    overflow: hidden; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; font-family: var(--font-head);
    color: var(--gold); position: relative;
  }
  .hero-avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .hero-avatar .fallback { position: absolute; font-size: 14px; font-weight: 700; color: var(--gold); }
  .hero-item.active .hero-avatar { border-color: var(--gold); }
  .hero-info { flex: 1; min-width: 0; }
  .hero-name { font-size: 13px; font-weight: 600; color: var(--text-white); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .hero-item.active .hero-name { color: var(--gold); }
  .hero-role-label { font-size: 10px; color: var(--text-dim); margin-top: 1px; letter-spacing: .3px; }
  .tier-dot {
    width: 18px; height: 18px; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 800; font-family: var(--font-head); flex-shrink: 0;
  }

  /* ── MAIN ── */
  .main { background: var(--bg); overflow-y: auto; overflow-x: hidden; }
  .page { display: none; padding: 18px; }
  .page.active { display: block; }

  /* Hero Header */
  .hero-header {
    background: var(--surface);
    border: 1px solid rgba(240,192,64,0.15);
    border-radius: var(--radius-lg); padding: 0; margin-bottom: 16px;
    position: relative; overflow: hidden;
  }
  .hero-banner {
    height: 140px; position: relative; overflow: hidden;
    background: linear-gradient(135deg, #0a1628 0%, #162040 100%);
  }
  .hero-banner-img {
    position: absolute; top: 0; right: 0; height: 100%; width: 60%;
    object-fit: cover; object-position: top center;
    mask-image: linear-gradient(to left, rgba(0,0,0,0.9) 0%, transparent 100%);
    -webkit-mask-image: linear-gradient(to left, rgba(0,0,0,0.9) 0%, transparent 100%);
  }
  .hero-banner-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(to right, var(--surface) 30%, transparent 70%);
  }
  .hero-banner-content { position: absolute; inset: 0; padding: 20px 22px; display: flex; flex-direction: column; justify-content: center; }
  .hero-name-big { font-family: var(--font-head); font-size: 2rem; font-weight: 900; color: var(--text-white); line-height: 1; text-shadow: 0 2px 12px rgba(0,0,0,0.8); }
  .hero-title-txt { font-size: 12px; color: var(--gold); margin-top: 4px; font-style: italic; letter-spacing: .5px; }
  .tier-badge-big {
    position: absolute; top: 16px; right: 16px;
    width: 44px; height: 44px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-head); font-size: 1.6rem; font-weight: 900;
    border: 2px solid;
  }
  .hero-badges-row { padding: 12px 18px 14px; display: flex; gap: 6px; flex-wrap: wrap; border-top: 1px solid var(--border); background: var(--surface2); }
  .badge {
    padding: 4px 11px; border-radius: 99px; font-size: 10px;
    font-weight: 700; font-family: var(--font-body); letter-spacing: .7px; text-transform: uppercase;
  }
  .badge-gold { background: var(--gold); color: #07100f; }
  .badge-cyan { background: var(--cyan-dim); color: var(--cyan); border: 1px solid rgba(56,217,245,0.25); }
  .badge-purple { background: rgba(167,139,250,0.1); color: var(--purple); border: 1px solid rgba(167,139,250,0.25); }
  .badge-ghost { background: var(--surface3); color: var(--text-dim); border: 1px solid var(--border2); }

  /* Guide grid */
  .guide-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  .guide-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 14px 16px;
  }
  .guide-card.full { grid-column: 1 / -1; }
  .guide-card h3 {
    font-family: var(--font-body); font-size: .8rem; font-weight: 700;
    color: var(--gold); text-transform: uppercase; letter-spacing: 1.5px;
    margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 7px;
  }
  .guide-card p, .guide-card li { color: var(--text); line-height: 1.7; font-size: 13px; }

  /* Item build */
  .item-build { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }
  .item-card {
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    width: 66px; cursor: help;
  }
  .item-img-wrap {
    width: 52px; height: 52px; border-radius: 10px;
    background: var(--surface2); border: 1px solid var(--border2);
    overflow: hidden; display: flex; align-items: center; justify-content: center;
    transition: border-color .15s, box-shadow .15s; position: relative;
  }
  .item-img-wrap:hover { border-color: var(--gold); box-shadow: 0 0 12px var(--gold-glow); }
  .item-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
  .item-img-wrap .fallback-item { font-size: 9px; color: var(--text-dim); text-align: center; padding: 4px; line-height: 1.3; }
  .item-name-label { font-size: 9px; color: var(--text-dim); text-align: center; line-height: 1.3; }

  /* Spell display */
  .spell-display { display: flex; align-items: center; gap: 12px; margin-top: 6px; }
  .spell-img-wrap {
    width: 52px; height: 52px; border-radius: 10px;
    background: var(--surface2); border: 1px solid rgba(167,139,250,0.3);
    overflow: hidden; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 12px rgba(167,139,250,0.15); flex-shrink: 0;
  }
  .spell-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
  .spell-info h4 { font-size: 14px; font-weight: 700; color: var(--purple); }
  .spell-info p { font-size: 12px; color: var(--text-dim); margin-top: 2px; }

  /* Combo chain */
  .combo-chain { display: flex; flex-direction: column; gap: 6px; margin-top: 6px; }
  .combo-step { display: flex; align-items: flex-start; gap: 10px; font-size: 13px; color: var(--text); }
  .combo-num {
    width: 22px; height: 22px; background: var(--gold); color: #07100f;
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 800; flex-shrink: 0; font-family: var(--font-head);
  }

  /* Counter cards */
  .counter-row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
  .counter-card {
    background: var(--surface2); border-radius: 8px; padding: 10px 12px; border: 1px solid var(--border);
  }
  .counter-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
  .counter-label.green { color: var(--green); }
  .counter-label.red { color: var(--red); }
  .counter-label.cyan { color: var(--cyan); }
  .counter-value { font-size: 12px; color: var(--text); }

  /* ── EMBLEMS ── */
  .emblem-section { margin-top: 10px; }
  .emblem-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 8px; }
  .emblem-card {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 10px; padding: 10px 8px; text-align: center; cursor: pointer;
    transition: all .2s;
  }
  .emblem-card:hover, .emblem-card.active { border-color: var(--gold-dim); background: var(--gold-glow2); }
  .emblem-img-wrap {
    width: 48px; height: 48px; margin: 0 auto 6px;
    border-radius: 50%; background: var(--surface3); border: 2px solid var(--border2);
    overflow: hidden; display: flex; align-items: center; justify-content: center;
    font-size: 20px;
  }
  .emblem-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
  .emblem-name { font-size: 10px; font-weight: 600; color: var(--text); }
  .emblem-role { font-size: 9px; color: var(--text-dim); margin-top: 2px; }

  /* ── INFO PAGES ── */
  .section-title {
    font-family: var(--font-head); font-size: 1.1rem; color: var(--text-white);
    font-weight: 700; text-transform: uppercase; letter-spacing: 2px;
    margin-bottom: 16px; padding-bottom: 8px;
    border-bottom: 1px solid var(--gold-dim);
    display: flex; align-items: center; gap: 10px;
  }
  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .info-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 13px 15px;
    display: flex; gap: 12px; align-items: flex-start;
    transition: border-color .2s;
  }
  .info-card:hover { border-color: var(--gold-dim); }
  .info-card-img {
    width: 48px; height: 48px; border-radius: 8px; flex-shrink: 0;
    background: var(--surface2); border: 1px solid var(--border2); overflow: hidden;
    display: flex; align-items: center; justify-content: center; font-size: 20px;
  }
  .info-card-img img { width: 100%; height: 100%; object-fit: cover; }
  .info-card-body { flex: 1; min-width: 0; }
  .info-card-body h4 { font-family: var(--font-body); font-size: .85rem; color: var(--gold); font-weight: 700; margin-bottom: 3px; letter-spacing: .5px; }
  .info-card-body .meta { font-size: 10px; color: var(--text-dim); margin-bottom: 4px; }
  .info-card-body p { font-size: 12px; color: var(--text); line-height: 1.6; }

  /* ── MAP PAGE ── */
  .map-container { position: relative; }
  .map-svg-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 16px;
    position: relative;
  }
  .map-legend { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .map-obj-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 10px 12px;
    display: flex; gap: 10px; align-items: center;
    transition: all .2s; cursor: pointer;
  }
  .map-obj-card:hover, .map-obj-card.highlighted { border-color: var(--gold-dim); background: var(--gold-glow2); }
  .map-obj-icon {
    width: 36px; height: 36px; border-radius: 8px; flex-shrink: 0;
    background: var(--surface2); overflow: hidden;
    display: flex; align-items: center; justify-content: center; font-size: 18px;
  }
  .map-obj-icon img { width: 100%; height: 100%; object-fit: contain; }
  .map-obj-info h4 { font-size: 12px; font-weight: 700; color: var(--text-white); }
  .map-obj-info p { font-size: 10px; color: var(--text-dim); margin-top: 1px; }

  /* ── EMPTY STATE ── */
  .empty-state {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    height: 100%; min-height: 55vh; text-align: center; padding: 40px; color: var(--text-dim);
  }
  .empty-glyph {
    font-family: var(--font-head); font-size: 4rem; color: var(--gold-dim);
    margin-bottom: 16px; opacity: .4; animation: pulse 3s ease-in-out infinite;
  }
  @keyframes pulse { 0%,100%{opacity:.3} 50%{opacity:.6} }
  .empty-state h3 { font-family: var(--font-head); font-size: 1.2rem; color: var(--text); margin-bottom: 8px; letter-spacing: 1px; }

  /* ── CHAT ── */
  .chat-panel {
    background: var(--surface); border-left: 1px solid var(--border);
    display: flex; flex-direction: column; overflow: hidden;
  }
  .chat-header {
    padding: 14px 16px; border-bottom: 1px solid var(--border);
    font-family: var(--font-head); font-weight: 700; font-size: .85rem;
    color: var(--gold); text-transform: uppercase; letter-spacing: 2px;
    display: flex; align-items: center; gap: 8px; flex-shrink: 0;
  }
  .chat-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); flex-shrink: 0; animation: blink 2s infinite; }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.4} }
  .chat-msgs {
    flex: 1; overflow-y: auto; padding: 12px;
    display: flex; flex-direction: column; gap: 8px;
  }
  .msg {
    padding: 9px 12px; border-radius: 10px; font-size: 12.5px; line-height: 1.6;
    max-width: 92%; word-break: break-word;
  }
  .msg.bot { background: var(--surface2); border: 1px solid var(--border); color: var(--text); align-self: flex-start; border-bottom-left-radius: 3px; }
  .msg.user { background: var(--gold); color: #07100f; font-weight: 600; align-self: flex-end; border-bottom-right-radius: 3px; }
  .quick-chips { display: flex; flex-wrap: wrap; gap: 4px; padding: 8px 12px 4px; }
  .qchip {
    padding: 3px 9px; border-radius: 99px; border: 1px solid var(--border2);
    font-size: 10px; color: var(--text-dim); background: none; cursor: pointer;
    font-family: var(--font-body); transition: all .15s; font-weight: 500;
  }
  .qchip:hover { color: var(--gold); border-color: var(--gold-dim); background: var(--gold-glow); }
  .chat-input-row {
    padding: 10px 12px; border-top: 1px solid var(--border);
    display: flex; gap: 7px; flex-shrink: 0;
  }
  .chat-input-row input {
    flex: 1; background: var(--surface2); border: 1px solid var(--border2);
    border-radius: 8px; color: var(--text-white); padding: 8px 11px;
    font-size: 12px; font-family: var(--font-body); outline: none; transition: border-color .2s;
  }
  .chat-input-row input:focus { border-color: var(--gold-dim); }
  .chat-input-row input::placeholder { color: var(--text-dim); }
  .send-btn {
    background: var(--gold); border: none; color: #07100f;
    padding: 8px 14px; border-radius: 8px; font-weight: 800;
    font-size: 11px; cursor: pointer; font-family: var(--font-head);
    letter-spacing: 1px; transition: opacity .2s;
  }
  .send-btn:hover { opacity: .85; }

  /* tooltip */
  .item-tooltip {
    position: fixed; z-index: 9999; background: var(--surface);
    border: 1px solid var(--gold-dim); border-radius: 10px;
    padding: 10px 13px; pointer-events: none; opacity: 0;
    transition: opacity .15s; max-width: 220px; font-size: 12px;
  }
  .item-tooltip.show { opacity: 1; }
  .item-tooltip h5 { color: var(--gold); font-weight: 700; margin-bottom: 3px; }
  .item-tooltip .tt-stats { color: var(--cyan); font-size: 11px; }
  .item-tooltip .tt-passive { color: var(--text); margin-top: 4px; font-size: 11px; line-height: 1.5; }
</style>
</head>
<body>
<div class="item-tooltip" id="item-tooltip">
  <h5 id="tt-name"></h5>
  <div class="tt-stats" id="tt-stats"></div>
  <div class="tt-passive" id="tt-passive"></div>
</div>

<div class="shell">
  <header>
    <div class="logo">
      <svg viewBox="0 0 32 32" fill="none"><polygon points="16,2 30,12 25,30 7,30 2,12" fill="rgba(240,192,64,0.15)" stroke="#f0c040" stroke-width="1.5"/><polygon points="16,7 25,14 21,25 11,25 7,14" fill="rgba(240,192,64,0.08)" stroke="#f0c040" stroke-width="1"/><text x="9" y="22" font-family="serif" font-weight="900" font-size="11" fill="#f0c040">ML</text></svg>
      MLBB Coach
    </div>
    <div class="header-tabs">
      <button class="header-tab active" onclick="showPage('guide',this)">Hero Guide</button>
      <button class="header-tab" onclick="showPage('spells',this)">Spells</button>
      <button class="header-tab" onclick="showPage('items',this)">Items</button>
      <button class="header-tab" onclick="showPage('emblems',this)">Emblems</button>
      <button class="header-tab" onclick="showPage('map',this)">Map</button>
    </div>
    <div class="header-right">Season 2025 · Meta</div>
  </header>

  <aside class="sidebar">
    <div class="sidebar-search">
      <input type="text" id="search-input" placeholder="Search heroes..." oninput="filterHeroes()">
    </div>
    <div class="role-filters" id="role-filters"></div>
    <div class="hero-list" id="hero-list"></div>
  </aside>

  <main class="main" id="main-panel">
    <!-- GUIDE -->
    <div class="page active" id="page-guide">
      <div class="empty-state" id="empty-state">
        <div class="empty-glyph">⚔</div>
        <h3>Select a Hero</h3>
        <p>Choose a hero from the sidebar to load<br>the full AI Coach Strategy Guide</p>
      </div>
      <div id="hero-content" style="display:none"></div>
    </div>

    <!-- SPELLS -->
    <div class="page" id="page-spells">
      <div class="section-title">🔮 Battle Spells</div>
      <div class="info-grid" id="spells-grid"></div>
    </div>

    <!-- ITEMS -->
    <div class="page" id="page-items">
      <div class="section-title">⚔️ Item Database</div>
      <div id="items-grid"></div>
    </div>

    <!-- EMBLEMS -->
    <div class="page" id="page-emblems">
      <div class="section-title">💎 Emblem System</div>
      <div id="emblems-content"></div>
    </div>

    <!-- MAP -->
    <div class="page" id="page-map">
      <div class="section-title">🗺️ Battlefield Map</div>
      <div class="map-svg-wrap" id="map-wrap"></div>
      <div class="map-legend" id="map-legend"></div>
    </div>
  </main>

  <aside class="chat-panel">
    <div class="chat-header"><div class="chat-dot"></div>AI Coach Chat</div>
    <div class="quick-chips">
      <button class="qchip" onclick="quickAsk('fast level up tips')">⚡ Level up</button>
      <button class="qchip" onclick="quickAsk('battle spell guide')">🔮 Spells</button>
      <button class="qchip" onclick="quickAsk('turtle and map objectives')">🗺️ Map</button>
      <button class="qchip" onclick="quickAsk('rank push tips')">🏆 Rank</button>
      <button class="qchip" onclick="quickAsk('counter tips')">🛡️ Counters</button>
    </div>
    <div class="chat-msgs" id="chat-msgs">
      <div class="msg bot">Welcome, Summoner! ⚔️<br>Select a hero and ask me anything — builds, counters, map objectives, emblems, or rank tips!</div>
    </div>
    <div class="chat-input-row">
      <input type="text" id="chat-input" placeholder="Ask any strategy..." onkeydown="if(event.key==='Enter')sendMsg()">
      <button class="send-btn" onclick="sendMsg()">SEND</button>
    </div>
  </aside>
</div>

<script>
// ── HERO PORTRAIT URL GENERATOR (working CDN) ──
function getHeroPortraitUrl(name) {
  // Map special cases where wiki name differs
  const specials = {
    'Balmond': 'Balmond',
    'Saber': 'Saber',
    'Alice': 'Alice',
    'Nana': 'Nana',
    'Tigreal': 'Tigreal',
    'Alucard': 'Alucard',
    'Karina': 'Karina',
    'Akai': 'Akai',
    'Franco': 'Franco',
    'Bruno': 'Bruno',
    'Clint': 'Clint',
    'Rafaela': 'Rafaela',
    'Eudora': 'Eudora',
    'Zilong': 'Zilong',
    'Fanny': 'Fanny',
    'Layla': 'Layla',
    'Hayabusa': 'Hayabusa',
    'Gusion': 'Gusion',
    'Wanwan': 'WanWan',
    'Lancelot': 'Lancelot',
    'Claude': 'Claude',
    'Granger': 'Granger',
    'Brody': 'Brody',
    'Beatrix': 'Beatrix',
    'Ixia': 'Ixia',
    'Ling': 'Ling',
    'Chou': 'Chou',
    'Paquito': 'Paquito',
    'Yu Zhong': 'Yu_Zhong',
    'Esmeralda': 'Esmeralda',
    'Fredrinn': 'Fredrinn',
    'Badang': 'Badang',
    'Thamuz': 'Thamuz',
    'Ruby': 'Ruby',
    'Khufra': 'Khufra',
    'Atlas': 'Atlas',
    'Grock': 'Grock',
    'Baxia': 'Baxia',
    'Johnson': 'Johnson',
    'Hylos': 'Hylos',
    'Uranus': 'Uranus',
    'Belerick': 'Belerick',
    'Edith': 'Edith',
    'Gloo': 'Gloo',
    'Cyclops': 'Cyclops',
    'Lunox': 'Lunox',
    'Lylia': 'Lylia',
    'Vale': 'Vale',
    'Xavier': 'Xavier',
    'Kagura': 'Kagura',
    'Harith': 'Harith',
    'Yve': 'Yve',
    'Novaria': 'Novaria',
    'Chang\'e': 'Chang\'e',
    'Aurora': 'Aurora',
    'Valentina': 'Valentina',
    'Estes': 'Estes',
    'Angela': 'Angela',
    'Diggie': 'Diggie',
    'Mathilda': 'Mathilda',
    'Floryn': 'Floryn',
    'Faramis': 'Faramis'
  };
  const fileName = specials[name] || name.replace(/[^a-zA-Z]/g, '');
  // Use reliable wikia CDN with first character folder
  const firstChar = fileName.charAt(0).toUpperCase();
  return `https://static.wikia.nocookie.net/mobile-legends/images/${firstChar}/${fileName}_Icon.png/revision/latest/scale-to-width-down/80`;
}

// ── ITEM & SPELL ICONS (expanded) ──
const ITEM_WIKI = {
  'Swift Boots': 'https://static.wikia.nocookie.net/mobile-legends/images/1/14/Swift_Boots_Icon.png/revision/latest/scale-to-width-down/60',
  'Warrior Boots': 'https://static.wikia.nocookie.net/mobile-legends/images/6/65/Warrior_Boots_Icon.png/revision/latest/scale-to-width-down/60',
  'Demon Shoes': 'https://static.wikia.nocookie.net/mobile-legends/images/a/a7/Demon_Shoes_Icon.png/revision/latest/scale-to-width-down/60',
  'Tough Boots': 'https://static.wikia.nocookie.net/mobile-legends/images/f/ff/Tough_Boots_Icon.png/revision/latest/scale-to-width-down/60',
  'Berserker\'s Fury': 'https://static.wikia.nocookie.net/mobile-legends/images/4/4c/Berserker%27s_Fury_Icon.png/revision/latest/scale-to-width-down/60',
  'Windtalker': 'https://static.wikia.nocookie.net/mobile-legends/images/0/00/Windtalker_Icon.png/revision/latest/scale-to-width-down/60',
  'Malefic Roar': 'https://static.wikia.nocookie.net/mobile-legends/images/6/60/Malefic_Roar_Icon.png/revision/latest/scale-to-width-down/60',
  'Haas\'s Claws': 'https://static.wikia.nocookie.net/mobile-legends/images/0/0e/Haas%27s_Claws_Icon.png/revision/latest/scale-to-width-down/60',
  'Demon Hunter Sword': 'https://static.wikia.nocookie.net/mobile-legends/images/0/07/Demon_Hunter_Sword_Icon.png/revision/latest/scale-to-width-down/60',
  'Blade of Despair': 'https://static.wikia.nocookie.net/mobile-legends/images/e/ec/Blade_of_Despair_Icon.png/revision/latest/scale-to-width-down/60',
  'Immortality': 'https://static.wikia.nocookie.net/mobile-legends/images/3/3c/Immortality_Icon.png/revision/latest/scale-to-width-down/60',
  'Holy Crystal': 'https://static.wikia.nocookie.net/mobile-legends/images/6/6d/Holy_Crystal_Icon.png/revision/latest/scale-to-width-down/60',
  'Lightning Truncheon': 'https://static.wikia.nocookie.net/mobile-legends/images/c/c3/Lightning_Truncheon_Icon.png/revision/latest/scale-to-width-down/60',
  'Genius Wand': 'https://static.wikia.nocookie.net/mobile-legends/images/9/98/Genius_Wand_Icon.png/revision/latest/scale-to-width-down/60',
  'Dominance Ice': 'https://static.wikia.nocookie.net/mobile-legends/images/1/1d/Dominance_Ice_Icon.png/revision/latest/scale-to-width-down/60',
  'Guardian Helmet': 'https://static.wikia.nocookie.net/mobile-legends/images/a/a5/Guardian_Helmet_Icon.png/revision/latest/scale-to-width-down/60',
  'Oracle': 'https://static.wikia.nocookie.net/mobile-legends/images/7/72/Oracle_Icon.png/revision/latest/scale-to-width-down/60',
  'Thunder Belt': 'https://static.wikia.nocookie.net/mobile-legends/images/4/4f/Thunder_Belt_Icon.png/revision/latest/scale-to-width-down/60',
  'Winter Crown': 'https://static.wikia.nocookie.net/mobile-legends/images/9/9b/Winter_Crown_Icon.png/revision/latest/scale-to-width-down/60',
  'Endless Battle': 'https://static.wikia.nocookie.net/mobile-legends/images/b/b8/Endless_Battle_Icon.png/revision/latest/scale-to-width-down/60',
  'Hunter Strike': 'https://static.wikia.nocookie.net/mobile-legends/images/a/a5/Hunter_Strike_Icon.png/revision/latest/scale-to-width-down/60',
  'Calamity Reaper': 'https://static.wikia.nocookie.net/mobile-legends/images/d/dc/Calamity_Reaper_Icon.png/revision/latest/scale-to-width-down/60',
  'Arcane Boots': 'https://static.wikia.nocookie.net/mobile-legends/images/3/3d/Arcane_Boots_Icon.png/revision/latest/scale-to-width-down/60',
  'Magic Shoes': 'https://static.wikia.nocookie.net/mobile-legends/images/a/a0/Magic_Shoes_Icon.png/revision/latest/scale-to-width-down/60',
  'Courage Bulwark': 'https://static.wikia.nocookie.net/mobile-legends/images/a/a3/Courage_Bulwark_Icon.png/revision/latest/scale-to-width-down/60',
  'Fleeting Time': 'https://static.wikia.nocookie.net/mobile-legends/images/9/94/Fleeting_Time_Icon.png/revision/latest/scale-to-width-down/60',
  'Necklace of Durance': 'https://static.wikia.nocookie.net/mobile-legends/images/5/50/Necklace_of_Durance_Icon.png/revision/latest/scale-to-width-down/60',
  'Brute Force Breastplate': 'https://static.wikia.nocookie.net/mobile-legends/images/a/ad/Brute_Force_Breastplate_Icon.png/revision/latest/scale-to-width-down/60',
  'Blade Armor': 'https://static.wikia.nocookie.net/mobile-legends/images/e/e6/Blade_Armor_Icon.png/revision/latest/scale-to-width-down/60',
  'Cursed Helmet': 'https://static.wikia.nocookie.net/mobile-legends/images/e/e5/Cursed_Helmet_Icon.png/revision/latest/scale-to-width-down/60',
  'War Axe': 'https://static.wikia.nocookie.net/mobile-legends/images/a/a9/War_Axe_Icon.png/revision/latest/scale-to-width-down/60',
  'Antique Cuirass': 'https://static.wikia.nocookie.net/mobile-legends/images/a/ac/Antique_Cuirass_Icon.png/revision/latest/scale-to-width-down/60',
  'Blood Wings': 'https://static.wikia.nocookie.net/mobile-legends/images/2/2c/Blood_Wings_Icon.png/revision/latest/scale-to-width-down/60',
  'Divine Glaive': 'https://static.wikia.nocookie.net/mobile-legends/images/c/c2/Divine_Glaive_Icon.png/revision/latest/scale-to-width-down/60',
  'Ice Retribution': 'https://static.wikia.nocookie.net/mobile-legends/images/4/44/Ice_Retribution_Icon.png/revision/latest/scale-to-width-down/60'
};

const SPELL_WIKI = {
  'Execute':'https://static.wikia.nocookie.net/mobile-legends/images/2/26/Execute.png/revision/latest/scale-to-width-down/60',
  'Retribution':'https://static.wikia.nocookie.net/mobile-legends/images/1/18/Retribution.png/revision/latest/scale-to-width-down/60',
  'Inspire':'https://static.wikia.nocookie.net/mobile-legends/images/1/18/Inspire.png/revision/latest/scale-to-width-down/60',
  'Flicker':'https://static.wikia.nocookie.net/mobile-legends/images/6/6e/Flicker.png/revision/latest/scale-to-width-down/60',
  'Sprint':'https://static.wikia.nocookie.net/mobile-legends/images/f/f4/Sprint.png/revision/latest/scale-to-width-down/60',
  'Purify':'https://static.wikia.nocookie.net/mobile-legends/images/2/2d/Purify.png/revision/latest/scale-to-width-down/60',
  'Vengeance':'https://static.wikia.nocookie.net/mobile-legends/images/3/32/Vengeance.png/revision/latest/scale-to-width-down/60',
  'Revitalize':'https://static.wikia.nocookie.net/mobile-legends/images/a/ac/Revitalize.png/revision/latest/scale-to-width-down/60',
  'Aegis':'https://static.wikia.nocookie.net/mobile-legends/images/8/8d/Aegis.png/revision/latest/scale-to-width-down/60',
  'Petrify':'https://static.wikia.nocookie.net/mobile-legends/images/0/0d/Petrify.png/revision/latest/scale-to-width-down/60',
  'Flameshot':'https://static.wikia.nocookie.net/mobile-legends/images/d/d0/Flameshot.png/revision/latest/scale-to-width-down/60',
  'Arrival':'https://static.wikia.nocookie.net/mobile-legends/images/a/a6/Arrival.png/revision/latest/scale-to-width-down/60',
};

const ROLE_EMOJI = { 'Marksman':'🏹','Assassin':'🗡️','Tank':'🛡️','Fighter':'⚔️','Mage':'🔮','Support':'💚' };
const TIER_STYLE = {
  S: { color:'#ff5c5c', bg:'rgba(255,92,92,0.15)', border:'#ff5c5c' },
  A: { color:'#f0c040', bg:'rgba(240,192,64,0.15)', border:'#f0c040' },
  B: { color:'#4ade80', bg:'rgba(74,222,128,0.15)', border:'#4ade80' },
  C: { color:'#6b7a94', bg:'rgba(107,122,148,0.1)', border:'#6b7a94' }
};

// ── ITEM TOOLTIP DATA ──
let itemData = {};

function itemImgHtml(name, size=52) {
  const url = ITEM_WIKI[name];
  const id = 'item_' + name.replace(/[^a-z0-9]/gi,'_');
  if (url) {
    return `<div class="item-img-wrap" style="width:${size}px;height:${size}px;" 
      onmouseenter="showTT(event,'${name.replace(/'/g, "\\'")}')" onmouseleave="hideTT()"
      data-item="${name}">
      <img src="${url}" alt="${name}" onerror="this.parentElement.innerHTML='<span class=\\'fallback-item\\'>${name.slice(0,8)}</span>'">
    </div>`;
  }
  return `<div class="item-img-wrap" style="width:${size}px;height:${size}px;"
    onmouseenter="showTT(event,'${name.replace(/'/g, "\\'")}')" onmouseleave="hideTT()">
    <span class="fallback-item">${name.slice(0,10)}</span>
  </div>`;
}

function showTT(e, name) {
  const d = itemData[name];
  if (!d) return;
  const tt = document.getElementById('item-tooltip');
  document.getElementById('tt-name').textContent = d.Item_Name || name;
  document.getElementById('tt-stats').textContent = d.Key_Stats || '';
  document.getElementById('tt-passive').textContent = d.Passive_Effect ? '📘 ' + d.Passive_Effect : '';
  tt.classList.add('show');
  moveTT(e);
}
function hideTT() { document.getElementById('item-tooltip').classList.remove('show'); }
function moveTT(e) {
  const tt = document.getElementById('item-tooltip');
  tt.style.left = (e.clientX + 14) + 'px';
  tt.style.top = (e.clientY - 10) + 'px';
}
document.addEventListener('mousemove', e => { if (document.getElementById('item-tooltip').classList.contains('show')) moveTT(e); });

// ── INIT ──
let allHeroes = [], currentHero = '', activeRole = 'All';

async function init() {
  const res = await fetch('/heroes');
  allHeroes = await res.json();
  const roles = ['All', ...new Set(allHeroes.map(h => h.role))].sort((a,b)=> a==='All'?-1:a.localeCompare(b));
  document.getElementById('role-filters').innerHTML = roles.map(r =>
    `<button class="role-chip${r==='All'?' active':''}" onclick="setRole('${r}',this)">${r}</button>`
  ).join('');

  // Preload item data
  const ir = await fetch('/gameinfo/items');
  const items = await ir.json();
  items.forEach(it => { itemData[it.Item_Name] = it; });

  renderHeroes();
}

function setRole(role, el) {
  activeRole = role;
  document.querySelectorAll('.role-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
  renderHeroes();
}
function filterHeroes() { renderHeroes(); }

function renderHeroes() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const filtered = allHeroes.filter(h =>
    (activeRole === 'All' || h.role === activeRole) && h.name.toLowerCase().includes(q)
  );
  document.getElementById('hero-list').innerHTML = filtered.map(h => {
    const emoji = ROLE_EMOJI[h.role] || '⚔️';
    const imgUrl = getHeroPortraitUrl(h.name);
    return `<div class="hero-item${h.name===currentHero?' active':''}" onclick="loadHero('${h.name.replace(/'/g,"\\'")}',this)">
      <div class="hero-avatar">
        ${imgUrl ? `<img src="${imgUrl}" onerror="this.parentElement.innerHTML='<span class=\\'fallback\\'>${emoji}</span>'">` : `<span class="fallback">${emoji}</span>`}
      </div>
      <div class="hero-info">
        <div class="hero-name">${h.name}</div>
        <div class="hero-role-label">${h.role} · ${h.lane}</div>
      </div>
    </div>`;
  }).join('');
}

// ── PAGES ──
function showPage(name, btn) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.header-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  btn.classList.add('active');
  if (name === 'spells') loadSpells();
  if (name === 'items') loadItemsPage();
  if (name === 'emblems') loadEmblems();
  if (name === 'map') loadMap();
}

// ── HERO GUIDE ──
async function loadHero(name, el) {
  currentHero = name;
  document.querySelectorAll('.hero-item').forEach(i => i.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.header-tab').forEach(t => t.classList.remove('active'));
  document.getElementById('page-guide').classList.add('active');
  document.querySelector('.header-tab').classList.add('active');
  document.getElementById('empty-state').style.display = 'none';
  const content = document.getElementById('hero-content');
  content.style.display = 'block';
  content.innerHTML = '<div class="empty-state"><p style="color:var(--gold);font-family:var(--font-head)">Loading...</p></div>';

  const res = await fetch('/hero/' + encodeURIComponent(name));
  if (!res.ok) { content.innerHTML = '<div class="empty-state"><h3>Hero not found</h3></div>'; return; }
  const d = await res.json();
  const ts = TIER_STYLE[d.tier] || TIER_STYLE['B'];

  // Build items html
  const itemsHtml = (d.items || []).map(it => `
    <div class="item-card" title="${it}">
      ${itemImgHtml(it, 52)}
      <div class="item-name-label">${it}</div>
    </div>
  `).join('');

  // Spell
  const spellUrl = SPELL_WIKI[d.spell];
  const spellHtml = `<div class="spell-display">
    <div class="spell-img-wrap">
      ${spellUrl ? `<img src="${spellUrl}" alt="${d.spell}" onerror="this.parentElement.textContent='${ROLE_EMOJI[d.role]||'🔮'}'">` : `<span style="font-size:20px">${ROLE_EMOJI[d.role]||'🔮'}</span>`}
    </div>
    <div class="spell-info">
      <h4>${d.spell}</h4>
      <p>Recommended battle spell</p>
    </div>
  </div>`;

  // Combo
  const comboHtml = (d.skill_combo||'').split('➔').map((s,i) =>
    `<div class="combo-step"><div class="combo-num">${i+1}</div><span>${s.trim()}</span></div>`
  ).join('');

  content.innerHTML = `
    <div class="hero-header">
      <div class="hero-banner">
        <div class="hero-banner-overlay"></div>
        <img class="hero-banner-img" src="${getHeroPortraitUrl(d.name)}" onerror="this.style.display='none'">
        <div class="hero-banner-content">
          <div class="hero-name-big">${d.name}</div>
          <div class="hero-title-txt">${d.title}</div>
        </div>
        <div class="tier-badge-big" style="color:${ts.color};background:${ts.bg};border-color:${ts.border}">${d.tier}</div>
      </div>
      <div class="hero-badges-row">
        <span class="badge badge-gold">${d.lane} Lane</span>
        <span class="badge badge-cyan">${d.role}</span>
        <span class="badge badge-purple">${d.playstyle}</span>
      </div>
    </div>

    <div class="guide-grid">
      <div class="guide-card full"><h3>📍 Lane Strategy</h3><p>${d.lane_tip}</p></div>

      <div class="guide-card full">
        <h3>⚔️ Recommended Build</h3>
        <div style="margin-bottom:12px">${spellHtml}</div>
        <div class="item-build">${itemsHtml}</div>
      </div>

      <div class="guide-card full">
        <h3>🔥 Skill Combo</h3>
        <div class="combo-chain">${comboHtml}</div>
      </div>

      <div class="guide-card full">
        <h3>🛡️ Counter Info</h3>
        <div class="counter-row">
          <div class="counter-card"><div class="counter-label green">✅ Strong Against</div><div class="counter-value">${d.strong_against}</div></div>
          <div class="counter-card"><div class="counter-label red">⚠️ Weak Against</div><div class="counter-value">${d.weak_against}</div></div>
          <div class="counter-card" style="grid-column:1/-1"><div class="counter-label cyan">🤝 Best Partner</div><div class="counter-value">${d.best_partner}</div></div>
        </div>
      </div>

      <div class="guide-card full"><h3>💡 Coach Tips</h3><p>${d.tips}</p></div>
    </div>`;
}

// ── SPELLS ──
async function loadSpells() {
  const grid = document.getElementById('spells-grid');
  if (grid.dataset.loaded) return;
  grid.dataset.loaded = '1';
  const res = await fetch('/gameinfo/spells');
  const data = await res.json();
  grid.innerHTML = data.map(s => {
    const url = SPELL_WIKI[s.Spell_Name];
    const imgHtml = url
      ? `<img src="${url}" alt="${s.Spell_Name}" onerror="this.parentElement.textContent='🔮'">`
      : '🔮';
    return `<div class="info-card">
      <div class="info-card-img">${imgHtml}</div>
      <div class="info-card-body">
        <h4>${s.Spell_Name}</h4>
        <div class="meta">CD: ${s.Cooldown} · ${s.Best_For}</div>
        <p>${s.Effect}</p>
      </div>
    </div>`;
  }).join('');
}

// ── ITEMS PAGE ──
async function loadItemsPage() {
  const el = document.getElementById('items-grid');
  if (el.dataset.loaded) return;
  el.dataset.loaded = '1';
  const res = await fetch('/gameinfo/items');
  const data = await res.json();
  const cats = [...new Set(data.map(i => i.Type))];
  el.innerHTML = cats.map(cat => {
    const catItems = data.filter(i => i.Type === cat);
    const emoji = cat === 'Boots' ? '👟' : (cat === 'Marksman' ? '🏹' : (cat === 'Magic' ? '✨' : (cat === 'Defense' ? '🛡️' : '⚔️')));
    return `<div style="margin-bottom:20px">
      <div style="font-family:var(--font-body);font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--gold);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border)">${emoji} ${cat}</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        ${catItems.map(it => `<div class="info-card">
          <div class="info-card-img">
            ${ITEM_WIKI[it.Item_Name] ? `<img src="${ITEM_WIKI[it.Item_Name]}" alt="${it.Item_Name}" onerror="this.parentElement.textContent='⚔️'">` : '⚔️'}
          </div>
          <div class="info-card-body">
            <h4>${it.Item_Name}</h4>
            <div class="meta">${it.Cost} Gold · ${it.Best_For}</div>
            <p style="color:var(--cyan);font-size:11px">${it.Key_Stats}</p>
            <p style="margin-top:3px">${it.Passive_Effect}</p>
          </div>
        </div>`).join('')}
      </div>
    </div>`;
  }).join('');
}

// ── EMBLEMS ──
function loadEmblems() {
  const el = document.getElementById('emblems-content');
  if (el.dataset.loaded) return;
  el.dataset.loaded = '1';

  const emblems = [
    { name:'Marksman', icon:'🏹', color:'#f0c040', roles:'MM', desc:'Adaptive Attack, Weapon Master, Electro Flash. Best for Gold Lane carries.', talent:'Electro Flash — deal burst damage on skill use', stats:'+Adaptive Atk, +Crit Rate, +Movement Speed' },
    { name:'Assassin', icon:'🗡️', color:'#ff5c5c', roles:'Assassin', desc:'Rupture, Master Assassin, Killing Spree. Best for Jungle burst heroes.', talent:'Killing Spree — restore HP and MS on kill', stats:'+Adaptive Atk, +Armor Pen, +Movement Speed' },
    { name:'Tank', icon:'🛡️', color:'#38d9f5', roles:'Tank/Roam', desc:'Firmness, Tenacity, Brave Smite. Best for Roam tanks.', talent:'Brave Smite — basic attacks heal you by dealing CC', stats:'+HP, +Defense, +CC Duration Reduction' },
    { name:'Fighter', icon:'⚔️', color:'#ff9a3c', roles:'Fighter/EXP', desc:'Festival of Blood, War Cry, Unbending Will. Best for EXP lane fighters.', talent:'Festival of Blood — gain spell vamp on kills', stats:'+Adaptive Atk, +HP, +Spell Vamp' },
    { name:'Mage', icon:'🔮', color:'#a78bfa', roles:'Mage/Mid', desc:'Mystery Shop, Impure Rage, Magic Power Surge. Best for burst mages.', talent:'Magic Power Surge — passive MP boost + penetration', stats:'+Magic Power, +Magic Pen, +Cooldown Reduction' },
    { name:'Support', icon:'💚', color:'#4ade80', roles:'Support/Roam', desc:'Avarice, Focusing Mark, Agility. Best for Roam supports.', talent:'Focusing Mark — mark enemies, allies deal bonus dmg', stats:'+HP, +Magic Def, +Cooldown Reduction' },
    { name:'Common', icon:'⭐', color:'#b8c8e0', roles:'Any', desc:'Veteran Hunter, Inspire (Spell), Quick Grab. Flexible option for hybrid roles.', talent:'Veteran Hunter — flat adaptive atk per unique kill', stats:'+Adaptive Atk/Defense, Flexible' },
    { name:'Jungle', icon:'🌿', color:'#4ade80', roles:'Jungle', desc:'Wilderness Blessing, Hunter, Killing Spree. Retribution users only.', talent:'Wilderness Blessing — bonus exp & gold in jungle', stats:'+Adaptive Atk, +Jungle Efficiency' },
  ];

  const selected = { name: 'Marksman' };

  el.innerHTML = `
    <div class="emblem-grid" id="emblem-grid">
      ${emblems.map(e => `
        <div class="emblem-card${e.name===selected.name?' active':''}" onclick="selectEmblem('${e.name}')">
          <div class="emblem-img-wrap" style="border-color:${e.color}40;background:${e.color}15">
            <span style="font-size:22px">${e.icon}</span>
          </div>
          <div class="emblem-name" style="color:${e.color}">${e.name}</div>
          <div class="emblem-role">${e.roles}</div>
        </div>
      `).join('')}
    </div>
    <div id="emblem-detail" style="margin-top:16px"></div>
  `;

  window._emblems = emblems;
  selectEmblem('Marksman');
}

function selectEmblem(name) {
  const e = window._emblems.find(x => x.name === name);
  if (!e) return;
  document.querySelectorAll('.emblem-card').forEach(c => c.classList.remove('active'));
  document.querySelectorAll('.emblem-card').forEach(c => {
    if (c.querySelector('.emblem-name').textContent === name) c.classList.add('active');
  });
  document.getElementById('emblem-detail').innerHTML = `
    <div class="guide-card" style="background:var(--surface);border-color:${e.color}40">
      <h3 style="color:${e.color}">${e.icon} ${e.name} Emblem</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div>
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text-dim);margin-bottom:6px">Best For</div>
          <div style="font-size:13px;color:var(--text)">${e.roles}</div>
        </div>
        <div>
          <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text-dim);margin-bottom:6px">Key Stats</div>
          <div style="font-size:12px;color:var(--cyan)">${e.stats}</div>
        </div>
      </div>
      <div style="margin-top:12px;padding-top:10px;border-top:1px solid var(--border)">
        <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:var(--text-dim);margin-bottom:5px">Talent</div>
        <div style="font-size:13px;color:${e.color}">${e.talent}</div>
      </div>
      <div style="margin-top:10px;font-size:12px;color:var(--text);line-height:1.6">${e.desc}</div>
    </div>`;
}

// ── MAP ──
function loadMap() {
  const wrap = document.getElementById('map-wrap');
  if (wrap.dataset.loaded) return;
  wrap.dataset.loaded = '1';

  // Interactive SVG Map of MLBB battlefield (unchanged from original, but improved)
  wrap.innerHTML = `
  <svg viewBox="0 0 600 500" xmlns="http://www.w3.org/2000/svg" style="width:100%;display:block;background:#071018">
    <defs>
      <radialGradient id="bg-grad" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#0d2340"/>
        <stop offset="100%" stop-color="#07101a"/>
      </radialGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="blur"/>
        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
      </filter>
    </defs>
    <rect width="600" height="500" fill="url(#bg-grad)"/>
    <g stroke="rgba(255,255,255,0.03)" stroke-width="1">
      <line x1="0" y1="100" x2="600" y2="100"/><line x1="0" y1="200" x2="600" y2="200"/>
      <line x1="0" y1="300" x2="600" y2="300"/><line x1="0" y1="400" x2="600" y2="400"/>
      <line x1="100" y1="0" x2="100" y2="500"/><line x1="200" y1="0" x2="200" y2="500"/>
      <line x1="300" y1="0" x2="300" y2="500"/><line x1="400" y1="0" x2="400" y2="500"/>
      <line x1="500" y1="0" x2="500" y2="500"/>
    </g>
    <ellipse cx="145" cy="200" rx="80" ry="120" fill="#0a2010" stroke="#1a4020" stroke-width="1"/>
    <ellipse cx="455" cy="300" rx="80" ry="120" fill="#0a2010" stroke="#1a4020" stroke-width="1"/>
    <ellipse cx="150" cy="340" rx="50" ry="40" fill="#0b2412" stroke="#1a4020" stroke-width="1"/>
    <ellipse cx="450" cy="160" rx="50" ry="40" fill="#0b2412" stroke="#1a4020" stroke-width="1"/>
    <path d="M0,280 Q150,250 300,250 Q450,250 600,220" stroke="#0a3a5a" stroke-width="28" fill="none" opacity="0.7"/>
    <path d="M0,280 Q150,250 300,250 Q450,250 600,220" stroke="#0d4d78" stroke-width="12" fill="none" opacity="0.5"/>
    <path d="M0,280 Q150,250 300,250 Q450,250 600,220" stroke="#1a6898" stroke-width="3" fill="none" opacity="0.4"/>
    <path d="M60,440 L60,80 L540,80" stroke="#1a3050" stroke-width="30" fill="none"/>
    <path d="M60,440 L60,80 L540,80" stroke="#243d64" stroke-width="14" fill="none"/>
    <path d="M60,440 L60,80 L540,80" stroke="#2d4e80" stroke-width="3" fill="none" opacity="0.8"/>
    <path d="M60,440 L540,80" stroke="#1a3050" stroke-width="30" fill="none"/>
    <path d="M60,440 L540,80" stroke="#243d64" stroke-width="14" fill="none"/>
    <path d="M60,440 L540,80" stroke="#2d4e80" stroke-width="3" fill="none" opacity="0.8"/>
    <path d="M60,440 L540,440 L540,80" stroke="#1a3050" stroke-width="30" fill="none"/>
    <path d="M60,440 L540,440 L540,80" stroke="#243d64" stroke-width="14" fill="none"/>
    <path d="M60,440 L540,440 L540,80" stroke="#2d4e80" stroke-width="3" fill="none" opacity="0.8"/>
    <text x="30" y="260" fill="#2d4e80" font-size="9" font-family="monospace" font-weight="700" transform="rotate(-90,30,260)" opacity="0.6">EXP LANE</text>
    <text x="280" y="370" fill="#2d4e80" font-size="9" font-family="monospace" font-weight="700" transform="rotate(-45,280,370)" opacity="0.6">MID LANE</text>
    <text x="300" y="460" fill="#2d4e80" font-size="9" font-family="monospace" font-weight="700" opacity="0.6">GOLD LANE</text>
    <rect x="10" y="390" width="90" height="90" rx="12" fill="#0a1e14" stroke="#1a4a2a" stroke-width="2"/>
    <polygon points="55,395 75,420 70,445 40,445 35,420" fill="#1a4a2a" stroke="#2a7a4a" stroke-width="1"/>
    <text x="55" y="460" fill="#4ade80" font-size="8" font-family="monospace" text-anchor="middle" font-weight="700">ALLY BASE</text>
    <circle cx="55" cy="430" r="12" fill="none" stroke="#4ade80" stroke-width="1.5" opacity="0.6"/>
    <text x="55" y="434" fill="#4ade80" font-size="9" font-family="monospace" text-anchor="middle">⚔</text>
    <rect x="500" y="20" width="90" height="90" rx="12" fill="#1e0a0a" stroke="#4a1a1a" stroke-width="2"/>
    <polygon points="545,25 565,50 560,75 530,75 525,50" fill="#4a1a1a" stroke="#7a2a2a" stroke-width="1"/>
    <text x="545" y="95" fill="#ff5c5c" font-size="8" font-family="monospace" text-anchor="middle" font-weight="700">ENEMY BASE</text>
    <circle cx="545" cy="60" r="12" fill="none" stroke="#ff5c5c" stroke-width="1.5" opacity="0.6"/>
    <text x="545" y="64" fill="#ff5c5c" font-size="9" font-family="monospace" text-anchor="middle">💀</text>
    <!-- Turrets, objectives same as before but shortened for brevity -->
    <g class="obj" id="map-turtle" onclick="highlightObj('turtle')" style="cursor:pointer">
      <circle cx="300" cy="252" r="22" fill="#071825" stroke="#1a6898" stroke-width="2" filter="url(#glow)"/>
      <circle cx="300" cy="252" r="14" fill="#0a2535" stroke="#2a9ad8" stroke-width="1.5"/>
      <text x="300" y="248" fill="#38d9f5" font-size="14" text-anchor="middle">🐢</text>
      <text x="300" y="262" fill="#38d9f5" font-size="7" text-anchor="middle" font-family="monospace" font-weight="700">TURTLE</text>
    </g>
    <g class="obj" id="map-lord" onclick="highlightObj('lord')" style="cursor:pointer">
      <circle cx="460" cy="175" r="24" fill="#1a0a05" stroke="#8a3a10" stroke-width="2" filter="url(#glow)"/>
      <circle cx="460" cy="175" r="16" fill="#250e07" stroke="#c0540e" stroke-width="1.5"/>
      <text x="460" y="171" fill="#ff9a3c" font-size="16" text-anchor="middle">👹</text>
      <text x="460" y="185" fill="#ff9a3c" font-size="7" text-anchor="middle" font-family="monospace" font-weight="700">LORD</text>
    </g>
    <!-- Buffs and Crab -->
    <g class="obj" onclick="highlightObj('blue')">
      <circle cx="145" cy="190" r="16" fill="#05102a" stroke="#1a3a8a" stroke-width="1.5"/>
      <text x="145" y="186" fill="#6090ff" font-size="12" text-anchor="middle">🔵</text>
    </g>
    <g class="obj" onclick="highlightObj('red')">
      <circle cx="155" cy="340" r="16" fill="#2a0505" stroke="#8a1a1a" stroke-width="1.5"/>
      <text x="155" y="336" fill="#ff6060" font-size="12" text-anchor="middle">🔴</text>
    </g>
    <g class="obj" onclick="highlightObj('crab')">
      <circle cx="370" cy="440" r="14" fill="#1a1205" stroke="#8a6a10" stroke-width="1.5"/>
      <text x="370" y="436" fill="#f0c040" font-size="11" text-anchor="middle">🦀</text>
    </g>
  </svg>`;

  // Map legend (unchanged)
  const objectives = [
    { icon:'🐢', name:'Turtle', time:'2:00', benefit:'Team Gold + Shield', id:'turtle' },
    { icon:'👹', name:'Lord', time:'8:00', benefit:'Pushes lanes', id:'lord' },
    { icon:'🔵', name:'Blue Buff', time:'0:20', benefit:'-10% CD & Mana', id:'blue' },
    { icon:'🔴', name:'Red Buff', time:'0:20', benefit:'Slow + True Damage', id:'red' },
    { icon:'🦀', name:'Gold Crab', time:'0:45', benefit:'Gold stream', id:'crab' }
  ];
  document.getElementById('map-legend').innerHTML = objectives.map(o => `
    <div class="map-obj-card" id="leg-${o.id}" onclick="highlightObj('${o.id}')">
      <div class="map-obj-icon"><span style="font-size:20px">${o.icon}</span></div>
      <div class="map-obj-info">
        <h4>${o.name} <span style="color:var(--gold-dim);font-size:10px">${o.time}</span></h4>
        <p>${o.benefit}</p>
      </div>
    </div>
  `).join('');
}

function highlightObj(id) {
  document.querySelectorAll('.map-obj-card').forEach(c => c.classList.remove('highlighted'));
  const leg = document.getElementById('leg-' + id);
  if (leg) leg.classList.add('highlighted');
}

// ── CHAT ──
function quickAsk(text) { document.getElementById('chat-input').value = text; sendMsg(); }
async function sendMsg() {
  const input = document.getElementById('chat-input');
  const text = input.value.trim();
  if (!text) return;
  const box = document.getElementById('chat-msgs');
  box.innerHTML += `<div class="msg user">${text}</div>`;
  input.value = '';
  box.scrollTop = box.scrollHeight;
  const res = await fetch('/chat', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ hero_name: currentHero||'your hero', user_message: text })
  });
  const data = await res.json();
  box.innerHTML += `<div class="msg bot">${data.answer}</div>`;
  box.scrollTop = box.scrollHeight;
}

init();
</script>
</body>
</html>"""

if __name__ == '__main__':
    print("✅ MLBB AI Coach (Enhanced) starting on http://localhost:5000")
    app.run(debug=True, port=5000)
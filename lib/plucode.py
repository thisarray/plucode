"""Look up a PLU code or find a PLU code by description."""

import csv
import json
import os.path
import re
import unittest

_CODE_CARRIER_PHRASES = [
    'code',
    'find',
    'identify',
    'I want',
    'look for',
    'look up',
    'number',
    'scout',
    'search',
    'search for',
    'what is'
]
"""List of carrier phrases preceding a PLU code."""

_CODE_EXAMPLES = [
    '4011',
    '4 0 1 1',
    'four zero one one',
    '94011',
    '9 4 0 1 1',
    'nine four zero one one'
]
"""List of specific code examples to attach to carrier phrases."""

_DESCRIPTION_CARRIER_PHRASES = [
    'code for',
    'find',
    'identify',
    'I want',
    'look for',
    'look up',
    'number for',
    'scout',
    'search',
    'search for',
    'what is'
]
"""List of carrier phrases preceding a description."""

_DESCRIPTION_EXAMPLES = [
    'banana',
    'bananas',
    'yellow banana',
    'yellow bananas',
    'yellow cavendish banana',
    'yellow cavendish bananas'
]
"""List of specific description examples to attach to carrier phrases."""

_KEYWORD_PATTERN = re.compile(r"""(?P<keyword>[\w']+)""", re.VERBOSE)
"""Regular expression pattern to pull out keywords."""

_PLU_MAP = {
    "3000": "alkmene apples",
    "3001": "small aurora southern rose apples",
    "3002": "cantared apples",
    "3003": "d'estivale apples",
    "3004": "discovery apples",
    "3005": "golden delicious blush apples",
    "3006": "ingrid marie apples",
    "3007": "lochbuie apples",
    "3008": "rubinette apples",
    "3009": "russet apples",
    "3010": "small cripps red sundowner apples",
    "3011": "worcester apples",
    "3012": "abate fetel pears",
    "3013": "beurre hardy pears",
    "3014": "bon rouge pears",
    "3015": "clara friis pears",
    "3016": "concorde pears",
    "3017": "conference pears",
    "3018": "durondeau pears",
    "3019": "flamingo pears",
    "3020": "general leclerc pears",
    "3021": "guyot pears",
    "3022": "josephine pears",
    "3023": "small passe crassane pears",
    "3024": "rocha pears",
    "3025": "rosemarie pears",
    "3026": "triumph de vienne pears",
    "3027": "shamouti oranges",
    "3028": "small delta seedless oranges",
    "3029": "satsuma tangerines mandarins",
    "3030": "nova includes clemenvilla suntina tangerines mandarins",
    "3031": "jamaican tangor includes ortanique mandor mandora tambor topaz ortanline tangerines mandarins",
    "3032": "ellendale tangerines mandarins",
    "3033": "small charentais melon",
    "3034": "large charentais melon",
    "3035": "large white flesh tree ripened ready to eat nectarine",
    "3036": "small midknight oranges",
    "3037": "queen pineapple",
    "3038": "granadilla orange passion fruit",
    "3039": "physalis cape gooseberry ground cherry",
    "3040": "red skin color pitahaya",
    "3041": "rambutan",
    "3042": "mangosteen",
    "3043": "italia seeded grapes",
    "3044": "black apricots",
    "3045": "fresh on branch dates",
    "3046": "fresh frozen dates",
    "3047": "medjool dates",
    "3048": "helda flat beans",
    "3049": "fine beans",
    "3050": "dutch white winter cabbage",
    "3051": "spring cabbage greens",
    "3052": "string garlic",
    "3053": "baby parsnip",
    "3054": "elongated clovis red lamuyo peppers capsicums",
    "3055": "elongated clovis green lamuyo peppers capsicums",
    "3056": "elongated clovis yellow lamuyo peppers capsicums",
    "3057": "elongated clovis orange lamuyo peppers capsicums",
    "3058": "elongated clovis white lamuyo peppers capsicums",
    "3059": "crown prince squash",
    "3060": "vegetable marrow squash",
    "3061": "beef beefsteak tomatoes",
    "3062": "bay leaves",
    "3063": "fennel leaves",
    "3064": "aloe vera leaves",
    "3065": "small cameo apples",
    "3066": "large cameo apples",
    "3067": "small swiss gourmet apples",
    "3068": "large swiss gourmet apples",
    "3069": "small gravenstein red apples",
    "3070": "large gravenstein red apples",
    "3071": "granny smith red apples",
    "3072": "lady apples",
    "3073": "macoun apples",
    "3074": "greening ri apples",
    "3075": "baldwin apples",
    "3076": "melrose apples",
    "3077": "northern spy apples",
    "3078": "liberty apples",
    "3079": "purple asparagus",
    "3080": "pinkerton avocados",
    "3081": "saskatoon berries",
    "3082": "crowns broccoli",
    "3083": "stalk brussels sprouts",
    "3084": "chervil",
    "3085": "large indian decorative corn",
    "3086": "mini indian decorative corn",
    "3087": "indian strawberry corn",
    "3088": "red currants",
    "3089": "chinese eggplant aubergine",
    "3090": "thai eggplant aubergine",
    "3091": "gobo root burdock",
    "3092": "oroblanco sweetie grapefruit",
    "3095": "multicolor kale",
    "3096": "purple red all other colors kohlrabi",
    "3097": "romaine red lettuce",
    "3098": "boston red lettuce",
    "3099": "lotus root",
    "3100": "gold honeydew melon",
    "3101": "piel de sapo melon",
    "3102": "morel mushrooms",
    "3103": "enoki mushrooms",
    "3104": "roho 3615 evelina apples",
    "3105": "cashews",
    "3106": "macadamia",
    "3107": "medium navel oranges",
    "3108": "medium valencia oranges",
    "3109": "seville marmalade type oranges",
    "3110": "navel cara red oranges",
    "3111": "red fleshed solo sunrise papaya pawpaw",
    "3112": "meridol papaya pawpaw",
    "3113": "flat white flesh saturn type peaches",
    "3114": "extra large green keitt and francis varieties mango",
    "3115": "flat yellow flesh peaches",
    "3116": "small yellow flesh tree ripened ready to eat peaches",
    "3117": "large yellow flesh tree ripened ready to eat peaches",
    "3118": "starkrimson pears",
    "3119": "small bell greenhouse green peppers capsicums",
    "3120": "large bell greenhouse green peppers capsicums",
    "3121": "bell greenhouse orange peppers capsicums",
    "3122": "bell greenhouse white peppers capsicums",
    "3123": "bell greenhouse brown peppers capsicums",
    "3124": "bell greenhouse purple peppers capsicums",
    "3125": "habanero peppers capsicums",
    "3127": "medium pomegranate",
    "3128": "purple potato",
    "3129": "pummelo red grapefruit",
    "3130": "jumbo pumpkin",
    "3131": "decorative painted pumpkin",
    "3132": "white pumpkin",
    "3133": "white mini pumpkin",
    "3134": "pie pumpkin",
    "3135": "ornamental gourd",
    "3136": "sapodillo nispero",
    "3137": "white sapote",
    "3138": "black sapote",
    "3139": "savory",
    "3140": "cucuzza squash",
    "3141": "opo squash",
    "3142": "carnival squash",
    "3143": "acorn baby squash",
    "3144": "fall glo tangerines mandarins",
    "3145": "plum italian saladette roma yellow tomatoes",
    "3146": "cherry red on the vine tomatoes",
    "3147": "cherry yellow on the vine tomatoes",
    "3148": "regular yelllow on the vine truss tomatoes",
    "3149": "regular orange on the vine tomatoes",
    "3150": "cocktail intermediate red tomatoes",
    "3151": "large vine ripe regular red tomatoes",
    "3152": "melogold grapefruit",
    "3153": "medium delta seedless oranges",
    "3154": "large delta seedless oranges",
    "3155": "medium midknight oranges",
    "3156": "large midknight oranges",
    "3157": "extra large white grapefruit",
    "3158": "extra large white grapefruit",
    "3159": "extra large white grapefruit",
    "3160": "synonymous with chinese broccoli gai lan",
    "3161": "baby chinese or indian mustard gai gui choy",
    "3162": "synonymous with water spinach ong choy",
    "3163": "shanghai bok choy pak choi",
    "3164": "yu choy",
    "3165": "treviso radicchio",
    "3166": "tuscan lacinato kale cabbage",
    "3167": "frisee",
    "3168": "castlefranco radicchio",
    "3169": "catalogna lettuce",
    "3271": "virginia gold apples",
    "3272": "sommerfeld apples",
    "3273": "golden beets",
    "3274": "fresh prunes",
    "3275": "yellow nyah may name",
    "3276": "white nyah may name",
    "3277": "baby broccoli",
    "3278": "pluot plumcot interspecific plum",
    "3279": "golden kiwifruit",
    "3280": "jumbo regular kiwifruit",
    "3281": "watermelon orange seedless melon",
    "3282": "plum italian saladette roma on the vine red tomatoes",
    "3283": "large honeycrisp apples",
    "3284": "extra large red delicious apples",
    "3285": "extra large golden delicious apples",
    "3286": "sweet red italian flat onions",
    "3287": "hawaiian plantain bananas",
    "3289": "sprite melon",
    "3290": "large aurora southern rose apples",
    "3291": "small boskoop belle de apples",
    "3292": "large boskoop belle de apples",
    "3293": "small scifresh jazz apples",
    "3294": "large scifresh jazz apples",
    "3295": "small sciearly pacific beauty apples",
    "3296": "large sciearly pacific beauty apples",
    "3297": "scired pacific queen apples",
    "3298": "redfield mahana red apples",
    "3299": "small sonya apples",
    "3300": "large sonya apples",
    "3301": "large cripps red sundowner apples",
    "3302": "large regular apricots",
    "3303": "babaco",
    "3304": "loganberries berries",
    "3305": "black currants",
    "3306": "medium charentais melon",
    "3307": "extra large charentais melon",
    "3308": "watermelon orange seedless melon",
    "3309": "lima oranges",
    "3310": "pera oranges",
    "3311": "curuba banana passion fruit",
    "3312": "granadilla yellow maracuja passion fruit",
    "3313": "small white flesh tree ripened ready to eat peaches",
    "3314": "large white flesh tree ripened ready to eat peaches",
    "3315": "small scilate envy apples",
    "3316": "carmen pears",
    "3317": "angelys pears",
    "3318": "large passe crassane pears",
    "3319": "yellow skin color pitahaya",
    "3320": "romanesco broccoflower caulibroc cauliflower",
    "3321": "with leaves attached celery root celeriac",
    "3322": "choy sum pak choi",
    "3323": "baby choy sum pak choi",
    "3324": "red escarole batavian chicory",
    "3325": "lollo bionda coral green lettuce",
    "3326": "lollo rossa coral red lettuce",
    "3327": "mignonette compact red tinged butterhead varieties lettuce",
    "3328": "mixed small leaf salad eg sucrine mesclun rocket arugula lettuce",
    "3329": "oak leaf green lettuce",
    "3330": "oak leaf reg lettuce",
    "3331": "red fresh bunch onions",
    "3332": "baby spinach",
    "3333": "small red orangy white flesh sweet potato yam kumara",
    "3334": "large red orangy white flesh sweet potato yam kumara",
    "3335": "cocktail intermediate red on the vine truss tomatoes",
    "3336": "cocktail intermediate red plum italian saladette roma on the vine truss tomatoes",
    "3337": "dried fruit figs",
    "3338": "anise",
    "3339": "belchard chantecler apples",
    "3340": "bertanne golden russet apples",
    "3341": "charles ross apples",
    "3342": "delblush tentation apples",
    "3343": "dessert apples",
    "3344": "small gloster apples",
    "3345": "large gloster apples",
    "3346": "holstein apples",
    "3347": "laxtons fortune apples",
    "3348": "lord lambourne apples",
    "3349": "michaelmas red apples",
    "3350": "small reine des reinettes king of the pippins apples",
    "3351": "large reine des reinettes king of the pippins apples",
    "3352": "reinettes and heritage varieties incl canada blanc reinette du mans armorique vigan calville apples",
    "3353": "st edmunds pippin apples",
    "3354": "ripe ready to eat avocados",
    "3355": "strawberries nominal 500g 1 litre berries",
    "3356": "strawberries nominal250g 1 2 litre berries",
    "3357": "small regular red black cherries",
    "3358": "large regular red black cherries",
    "3359": "chasselas grapes",
    "3360": "muscat de hambourg grapes",
    "3361": "without p harvest treatment grapefruit",
    "3362": "without postharvest treatment lemons",
    "3363": "bowen kensington pride mango",
    "3364": "r2e2 artwoeetwo mango",
    "3365": "ripe ready to eat mango",
    "3366": "madro\u00f1a",
    "3367": "glasshouse netted varieties melon",
    "3368": "ogen melon",
    "3369": "nectavigne red flesh nectarine",
    "3370": "maltaise oranges",
    "3371": "salustiana oranges",
    "3372": "navelate and other late navel varieties oranges",
    "3373": "navelina incl newhall oranges",
    "3374": "without postharvest treatment oranges",
    "3375": "de vigne sanguine red flesh peaches",
    "3376": "alexander lucas pears",
    "3377": "louise bonne pears",
    "3378": "santa maria pears",
    "3379": "mini pineapple",
    "3380": "perola pineapple",
    "3381": "soursop",
    "3382": "sugar apple",
    "3383": "small clementine tangerines mandarins",
    "3384": "medium clementine tangerines mandarins",
    "3385": "large clementine tangerines mandarins",
    "3386": "clementine with leaves attached tangerines mandarins",
    "3387": "clementine without p harvest treatment tangerines mandarins",
    "3388": "satsuma clauselina tangerines mandarins",
    "3389": "satsuma tangerines mandarins",
    "3390": "arracach",
    "3391": "rouge salambo red artichokes",
    "3392": "green bunch asparagus",
    "3393": "white bunch asparagus",
    "3394": "purple bunch asparagus",
    "3395": "red belgian endive witloof chicory",
    "3396": "savoy red cabbage",
    "3397": "summer cabbage pointed type",
    "3398": "chickpeas garbanzo",
    "3399": "regular fresh semi dried with leaves attached garlic",
    "3400": "regular smoked garlic",
    "3401": "one clove types garlic",
    "3402": "regular bunch leeks",
    "3403": "baby bunch leeks",
    "3404": "cep mushrooms",
    "3405": "fairy ring champignon mushrooms",
    "3406": "grey tricholoma mushrooms",
    "3407": "grisette mushrooms",
    "3408": "horn of plenty black trumpet mushrooms",
    "3409": "pioppino mushrooms",
    "3410": "saffron milk cap mushrooms",
    "3411": "sheep polypore mushrooms",
    "3412": "yellow brown fresh bunch onions",
    "3413": "tabasco peppers capsicums",
    "3414": "baking white potato",
    "3415": "baking red and eye varieties potato",
    "3416": "bunch rhubarb",
    "3417": "new zealand spinach",
    "3418": "zucchini courgette round squash",
    "3419": "borage",
    "3420": "belle du jumet honey pears",
    "3421": "3 7 lbs watermelon mini seedless melon",
    "3422": "interspecific apricots",
    "3423": "heirloom varieties include but are not limited to amish salad anna russian aunt ruby's yellow cherry big italian plum black prince zebra brandywine dr caroline earl of edgecomb eva purple ball flamme green hawaiian pineapple tomatoes",
    "3424": "purple red beta sweet carrots",
    "3425": "small ellendale tangerines mandarins",
    "3426": "medium ellendale tangerines mandarins",
    "3427": "large ellendale tangerines mandarins",
    "3428": "small honey murcott tangerines mandarins",
    "3429": "medium honey murcott tangerines mandarins",
    "3430": "large honey murcott tangerines mandarins",
    "3431": "small imperial tangerines mandarins",
    "3432": "medium imperial tangerines mandarins",
    "3433": "large imperial tangerines mandarins",
    "3434": "tosca pears",
    "3435": "pinova apples",
    "3436": "orange cauliflower",
    "3437": "flat yellow nectarine",
    "3438": "ambrosia apples",
    "3439": "white flesh flat nectarine",
    "3440": "large pomegranate",
    "3441": "butterkin squash",
    "3442": "new york 1 snapdragon apples",
    "3443": "new york 2 rubyfrost apples",
    "3444": "green dragon chin loung apples",
    "3445": "ds 3 pazazz apples",
    "3446": "kale sprouts",
    "3447": "ds 22 riverbelle apples",
    "3448": "tip top skylar rae cherries",
    "3449": "sugrathirteen midnight beauty brand grapes",
    "3450": "sugranineteen scarlotta seedless brand grapes",
    "3451": "sugrathirtyfour adora seedless brand grapes",
    "3452": "sugrathirtyfive autumncrisp brand grapes",
    "3453": "galangal root",
    "3454": "green jackfruit",
    "3455": "yellow jackfruit",
    "3456": "winter melon",
    "3457": "president plums",
    "3458": "cherry orange tomatoes",
    "3459": "shiny red persimmon",
    "3460": "red jonaprince prince apples",
    "3461": "lady williams apples",
    "3462": "garlic chinese chives",
    "3463": "chinese spinach yin choy amaranth callaloo een",
    "3464": "b 74 calypso mango",
    "3465": "stripy bell enjoya peppers capsicums",
    "3466": "cape rose cheeky pears",
    "3467": "regal 13 82 juici apples",
    "3468": "small honeycrisp apples",
    "3469": "sugrasixteen sable seedless brand grapes",
    "3470": "watermelon red small seeds melon",
    "3471": "baby cactus leaves nopales pads",
    "3472": "sacred pepper leaf",
    "3473": "epazote",
    "3474": "saffron sweet potato yam kumara",
    "3475": "peppermint mint",
    "3476": "orange tree leaf",
    "3477": "summer cilantro bolivian coriander papalo",
    "3478": "quelites",
    "3479": "chepil chipilin leaf",
    "3480": "pumpkin vine",
    "3481": "xpelon bean",
    "3482": "rabbit herb",
    "3483": "purple grass herb",
    "3484": "dalinette choupette apples",
    "3485": "harovin sundown cold snap pears",
    "3486": "cn121 sugarbee apples",
    "3487": "mn 55 rave first kiss apples",
    "3488": "extra large red mango",
    "3489": "cepuna migo pears",
    "3490": "maia 1 evercrisp apples",
    "3491": "arra fifteen sweeties grapes",
    "3492": "arra twentynine passion fire grapes",
    "3493": "tearless sweet sunions onions",
    "3494": "3 7 lbs watermelon yellow mini seedless sunny gold melon",
    "3495": "celina qtee pears",
    "3496": "ifg core red seedless 68 175 sweet celebration four romance none jack's salute grapes",
    "3497": "ifg core black seedless one sweet surrender eight enchantment thirteen secrets fifteen surprise ifgsixteen seventeen joy twenty five magic six bond grapes",
    "3498": "ifg core green seedless two sweet sunshine ten globe eleven sugar crisp grapes",
    "3499": "ifg novelty red seedless fourteen sweet mayabelle eighteen nectar nineteen candy hearts twenty one snaps three drops grapes",
    "3500": "ifg novelty black seedless six sweet sapphire twelve funny fingers twenty candy crunch two dream s grapes",
    "3501": "ifg novelty green seedless seven cotton candy grapes",
    "3502": "arra twentyseven 27 mystic star grapes",
    "3503": "arra twentyeight passion punch grapes",
    "3504": "arra thirty sugardrop grapes",
    "3505": "arra thirtytwo mystic dream grapes",
    "3506": "sweet scarlet muscato amore grapes",
    "3507": "wa 38 cosmic crisp apples",
    "3508": "thomcord grape jammers jelly drops california a29 67 grapes",
    "3509": "gem avocados",
    "3510": "small ambrosia apples",
    "3511": "wa 2 crimson delight apples",
    "3512": "round tasti lee tomatoes",
    "3513": "shinano gold yello apples",
    "3514": "fengapi tessa apples",
    "3515": "small prema 153 lemonade apples",
    "3516": "large prema 153 lemonade apples",
    "3518": "oksana xenia pears",
    "3519": "r10 45 wild twist apples",
    "3520": "sk 20 smileball goldies onique sweetnothings loving onions",
    "3600": "antares apples",
    "3601": "huaguan autumn glory apples",
    "3602": "belgica apples",
    "3603": "minneiska apples",
    "3604": "emmons apples",
    "3605": "nicoter apples",
    "3606": "sweet sensation pears",
    "3607": "mariri red apples",
    "3608": "large sciros pacific rose apples",
    "3609": "red plumcot interspecific plum",
    "3610": "green plumcot interspecific plum",
    "3611": "black plumcot interspecific plum",
    "3612": "nicogreen apples",
    "3613": "fuji brak apples",
    "3614": "red apricots",
    "3615": "civni apples",
    "3616": "large scilate envy apples",
    "3617": "seedless lemons",
    "3618": "opal apples",
    "3619": "milwa apples",
    "3620": "plumac apples",
    "3621": "francis madame francine mango",
    "3622": "honey green papaya melon",
    "3623": "hami chinese or snow melon",
    "3624": "korean melon",
    "3625": "minnewashta zestar apples",
    "3626": "meyer lemons",
    "3627": "large prema17 apples",
    "3628": "prema280 apples",
    "3629": "civg198 apples",
    "3630": "co op 43 apples",
    "3631": "pink porcelain doll pumpkin",
    "3632": "dekopon shiranui hallabong sumo citrus tangerines mandarins",
    "4011": "yellow includes cavendish bananas",
    "4012": "large navel oranges",
    "4013": "small navel oranges",
    "4014": "small valencia oranges",
    "4015": "small red delicious apples",
    "4016": "large red delicious apples",
    "4017": "large granny smith apples",
    "4018": "large granny smith apples",
    "4019": "large mcintosh apples",
    "4020": "large golden delicious apples",
    "4021": "small golden delicious apples",
    "4022": "white green seedless peerlette thompson grapes",
    "4023": "red seedless flame ruby emperatriz grapes",
    "4024": "small bartlett williams wbc pears",
    "4025": "small anjou pears",
    "4026": "small bosc beurre pears",
    "4027": "small ruby red pink includes ray grapefruit",
    "4028": "pint strawberries berries",
    "4029": "small pineapple",
    "4030": "regular kiwifruit",
    "4031": "watermelon red melon",
    "4032": "watermelon red seedless melon",
    "4033": "small lemons",
    "4034": "large honeydew white melon",
    "4035": "small yellow flesh nectarine",
    "4036": "large yellow flesh nectarine",
    "4037": "small yellow flesh peaches",
    "4038": "large yellow flesh peaches",
    "4039": "small black includes ambra beaut prima blackamber torch catalina challenger diamond friar royal knight freedom flame howard sun angeleno plums",
    "4040": "large black includes ambra beaut prima blackamber torch catalina challenger diamond friar royal knight freedom flame howard sun angeleno plums",
    "4041": "small red includes santa rosa late beaut rich spring first royal jewel rose zee ace aleta burgandy july frontier fortune grand lane casselman autumn mi plums",
    "4042": "large red includes santa rosa late beaut rich spring first royal jewel rose zee ace aleta burgandy july frontier fortune grand lane casselman autumn mi plums",
    "4043": "small yellow flesh tree ripened ready to eat peaches",
    "4044": "large yellow flesh tree ripened ready to eat peaches",
    "4045": "regular red black cherries",
    "4046": "small hass avocados",
    "4047": "small ruby red pink includes ray grapefruit",
    "4048": "regular incl persian tahiti bearss limes",
    "4049": "small cantaloupe rockmelon melon",
    "4050": "large cantaloupe rockmelon melon",
    "4051": "small red includes tommy atkins kent palmer vandyke edward hayden mango",
    "4052": "small regular papaya pawpaw",
    "4053": "large lemons",
    "4054": "raspberries red berries",
    "4055": "tangerines mandarins",
    "4056": "blue black seedless all other varieties not listed above including beauty and autumn royal grapes",
    "4057": "small haralson apples",
    "4058": "large haralson apples",
    "4060": "broccoli",
    "4061": "iceberg lettuce",
    "4062": "green ridge short cucumber",
    "4063": "small regular red tomatoes",
    "4064": "large regular red tomatoes",
    "4065": "large bell field grown green peppers capsicums",
    "4066": "green french beans",
    "4067": "zucchini courgette squash",
    "4068": "green scallions spring onions",
    "4069": "green cabbage",
    "4070": "small bunch celery",
    "4071": "small bunch celery",
    "4072": "russet potato",
    "4073": "red potato",
    "4074": "small red orangy flesh sweet potato yam kumara",
    "4075": "red leaf lettuce",
    "4076": "green leaf lettuce",
    "4077": "sweet corn white",
    "4078": "sweet corn yellow",
    "4079": "small cauliflower",
    "4080": "small green asparagus",
    "4081": "regular eggplant aubergine",
    "4082": "red onions",
    "4083": "white potato",
    "4084": "large artichokes",
    "4085": "large regular mushrooms",
    "4086": "yellow zucchini gold bar courgette squash",
    "4087": "plum italian saladette roma red tomatoes",
    "4088": "bell field grown red peppers capsicums",
    "4089": "bunched red radish",
    "4090": "regular bunched spinach",
    "4091": "white sweet potato yam kumara",
    "4092": "chinese snow pea pod mange tout peas",
    "4093": "large yellow brown onions",
    "4094": "bunch carrots",
    "4095": "yellow turnip",
    "4096": "large ginger gold apples",
    "4097": "small ginger gold apples",
    "4098": "small akane apples",
    "4099": "large akane apples",
    "4100": "small fireside apples",
    "4101": "small braeburn apples",
    "4102": "large fireside apples",
    "4103": "large braeburn apples",
    "4104": "small cortland apples",
    "4105": "cox orange pippin apples",
    "4106": "large cortland apples",
    "4107": "crab apples",
    "4108": "small crispin mutsu apples",
    "4109": "small crispin mutsu apples",
    "4110": "large crispin mutsu apples",
    "4111": "large crispin mutsu apples",
    "4112": "small regent apples",
    "4113": "small criterion apples",
    "4114": "large regent apples",
    "4115": "large criterion apples",
    "4116": "small early apples",
    "4117": "small early apples",
    "4118": "large early apples",
    "4119": "large early apples",
    "4120": "fiesta apples",
    "4121": "small elstar apples",
    "4122": "small sciros pacific rose apples",
    "4123": "large elstar apples",
    "4124": "small empire apples",
    "4125": "small empire apples",
    "4126": "large empire apples",
    "4127": "large empire apples",
    "4128": "small cripps pink lady apples",
    "4129": "small fuji apples",
    "4130": "large cripps pink lady apples",
    "4131": "large fuji apples",
    "4132": "small gala apples",
    "4133": "small gala apples",
    "4134": "large gala apples",
    "4135": "large gala apples",
    "4136": "small golden delicious apples",
    "4137": "large golden delicious apples",
    "4138": "small granny smith apples",
    "4139": "small granny smith apples",
    "4140": "small idared apples",
    "4141": "small jonamac apples",
    "4142": "large idared apples",
    "4143": "large jonamac apples",
    "4144": "small jonagold apples",
    "4145": "small jonagold apples",
    "4146": "large jonagold apples",
    "4147": "large jonagold apples",
    "4148": "small jonathan apples",
    "4149": "small jonathan apples",
    "4150": "large jonathan apples",
    "4151": "large jonathan apples",
    "4152": "small mcintosh apples",
    "4153": "small mcintosh apples",
    "4154": "large mcintosh apples",
    "4155": "small paulared apples",
    "4156": "small gravenstein apples",
    "4157": "large paulared apples",
    "4158": "large gravenstein apples",
    "4159": "vidalia onions",
    "4160": "small pippin apples",
    "4161": "texas sweet onions",
    "4162": "large pippin apples",
    "4163": "walla onions",
    "4164": "maui onions",
    "4165": "california sweet onions",
    "4166": "other sweet onions",
    "4167": "small red delicious apples",
    "4168": "large red delicious apples",
    "4169": "small rome apples",
    "4170": "small rome apples",
    "4171": "large rome apples",
    "4172": "large rome apples",
    "4173": "small royal gala apples",
    "4174": "large royal gala apples",
    "4176": "southern snap apples",
    "4177": "small spartan apples",
    "4178": "small spartan apples",
    "4179": "large spartan apples",
    "4180": "large spartan apples",
    "4181": "small stayman apples",
    "4182": "sturmer pippin apples",
    "4183": "large stayman apples",
    "4185": "small york apples",
    "4186": "small yellow includes cavendish bananas",
    "4187": "large york apples",
    "4188": "small white flesh tree ripened ready to eat nectarine",
    "4189": "small winesap apples",
    "4190": "small winesap apples",
    "4191": "large winesap apples",
    "4192": "large winesap apples",
    "4218": "small regular apricots",
    "4220": "atemoyas",
    "4221": "small green avocados",
    "4222": "small green avocados",
    "4223": "large green avocados",
    "4224": "large green avocados",
    "4225": "large hass avocados",
    "4226": "cocktail seedless avocados",
    "4229": "burro bananas",
    "4230": "dominique bananas",
    "4231": "green bananas",
    "4232": "leaves bananas",
    "4233": "apple manzano bananas",
    "4234": "baby nino bananas",
    "4235": "plantain macho bananas",
    "4236": "red bananas",
    "4239": "blackberries berries",
    "4240": "blueberries berries",
    "4241": "boysenberries berries",
    "4242": "cranberries berries",
    "4243": "gooseberries berries",
    "4244": "raspberries black berries",
    "4245": "raspberries golden berries",
    "4246": "pint strawberries berries",
    "4247": "quart strawberries berries",
    "4248": "quart strawberries berries",
    "4249": "bulk 3 pack pints strawberries berries",
    "4250": "bulk 3 pack pints strawberries berries",
    "4251": "long stemmed strawberries berries",
    "4254": "breadfruit",
    "4255": "cactus pear prickly",
    "4256": "carambola starfruit",
    "4257": "cherimoya",
    "4258": "golden rainier white cherries",
    "4260": "in husk waternut coconuts",
    "4261": "husked coconuts",
    "4263": "fresh regular dates",
    "4265": "feijoa",
    "4266": "black figs",
    "4267": "brown figs",
    "4268": "white green figs",
    "4270": "blue black seeded ribier exotic niabel grapes",
    "4271": "champagne grapes",
    "4272": "concord grapes",
    "4273": "red seeded cardinal emperor queen christmas rose grapes",
    "4274": "white green seeded all others not listed grapes",
    "4279": "pummelo white grapefruit",
    "4280": "small ruby red pink includes ray grapefruit",
    "4281": "large ruby red pink ncludes ray grapefruit",
    "4282": "large ruby red pink includes ray grapefruit",
    "4283": "large ruby red pink includes ray grapefruit",
    "4284": "small deep red grapefruit",
    "4285": "small deep red grapefruit",
    "4286": "small deep red grapefruit",
    "4287": "large deep red grapefruit",
    "4288": "large deep red grapefruit",
    "4289": "large deep red grapefruit",
    "4290": "small white grapefruit",
    "4291": "small white grapefruit",
    "4292": "small white grapefruit",
    "4293": "large white grapefruit",
    "4294": "large white grapefruit",
    "4295": "large white grapefruit",
    "4299": "guava",
    "4300": "homli fruit",
    "4302": "kiwano horned melon",
    "4303": "kumquat",
    "4305": "key incl mexican west indian limes",
    "4307": "longan",
    "4308": "loquats",
    "4309": "lychees",
    "4310": "mamey",
    "4311": "small green includes keitt and francis varieties mango",
    "4312": "small yellow includes oro ataulfo honey manila mango",
    "4317": "canary yellow honeydew melon",
    "4318": "small cantaloupe muskmelon melon",
    "4319": "large cantaloupe muskmelon melon",
    "4320": "casaba melon",
    "4321": "cinnabar melon",
    "4322": "crenshaw melon",
    "4323": "bulk strawberries berries",
    "4324": "french afternoon melon",
    "4325": "french breakfast melon",
    "4326": "galia melon",
    "4327": "orange flesh cantaline melon",
    "4328": "limequats",
    "4329": "small honeydew white melon",
    "4330": "mayan melon",
    "4331": "mickey lee watermelon sugarbaby melon",
    "4332": "muskmelon melon",
    "4333": "pepino melon",
    "4334": "persian melon",
    "4335": "prince melon",
    "4336": "santa claus melon",
    "4337": "saticoy melon",
    "4338": "sharlin melon",
    "4339": "spanish tendral melon",
    "4340": "watermelon yellow melon",
    "4341": "watermelon yellow seedless melon",
    "4377": "small yellow flesh tree ripened ready to eat nectarine",
    "4378": "large yellow flesh tree ripened ready to eat nectarine",
    "4381": "blood oranges",
    "4382": "juice oranges",
    "4383": "minneola tangelo",
    "4384": "small navel oranges",
    "4385": "large navel oranges",
    "4386": "small temple oranges",
    "4387": "large temple oranges",
    "4388": "large valencia oranges",
    "4394": "large regular papaya pawpaw",
    "4395": "cooking mexican papaya pawpaw",
    "4397": "purple passion fruit",
    "4399": "indian peaches",
    "4400": "small white flesh peaches",
    "4401": "large white flesh peaches",
    "4402": "small yellow flesh peaches",
    "4403": "large yellow flesh peaches",
    "4406": "asian nashi white pears",
    "4407": "asian nashi yellow pears",
    "4408": "asian nashi brown pears",
    "4409": "large bartlett williams wbc pears",
    "4410": "bartlett red sensation pears",
    "4411": "small bosc beurre pears",
    "4412": "large bosc beurre pears",
    "4413": "large bosc beurre pears",
    "4414": "comice doyenne du pears",
    "4415": "red pears",
    "4416": "large anjou d'anjou pears",
    "4417": "anjou red d'anjou pears",
    "4418": "forelle corella pears",
    "4419": "french pears",
    "4420": "king royal pears",
    "4421": "packham packhams triumph pears",
    "4422": "seckel pears",
    "4423": "tree ripened pears",
    "4424": "winter nelis honey pears",
    "4427": "regular american persimmon",
    "4428": "japanese sharonfruit kaki persimmon",
    "4430": "large pineapple",
    "4431": "small jet fresh pineapple",
    "4432": "large jet fresh pineapple",
    "4434": "small green includes dolly kelsey wickson plums",
    "4435": "large green includes dolly kelsey wickson plums",
    "4436": "italian prune sugar plums",
    "4437": "small purple includes queen rosa laroda nublana ann simka el dorado plums",
    "4438": "large purple includes queen rosa laroda nublana ann simka el dorado plums",
    "4439": "small tree ripened plums",
    "4440": "large tree ripened plums",
    "4441": "small yellow includes golden globe plums",
    "4442": "large yellow includes golden globe plums",
    "4445": "small pomegranate",
    "4447": "quince",
    "4448": "tamarind",
    "4449": "sunburst tangerines mandarins",
    "4450": "clementine includes fortune tangerines mandarins",
    "4451": "dancy tangerines mandarins",
    "4452": "fairchild tangerines mandarins",
    "4453": "honey murcott tangerines mandarins",
    "4454": "kinnow tangerines mandarins",
    "4455": "mandarin royal tangerines mandarins",
    "4456": "tangelo",
    "4459": "jamaican ugli tangelo",
    "4470": "salad bar",
    "4491": "extra large ruby red pink includes ray grapefruit",
    "4492": "extra large ruby red pink includes ray grapefruit",
    "4493": "extra large ruby red pink includes ray grapefruit",
    "4494": "extra large deep red grapefruit",
    "4495": "extra large deep red grapefruit",
    "4496": "extra large deep red grapefruit",
    "4497": "sugraone superior seedless brand grapes",
    "4498": "white green seedless all others not listed above including autumn king grapes",
    "4499": "crimson majestic grapes",
    "4514": "alfalfa sprouts",
    "4515": "florence sweet fennel bulb",
    "4516": "small artichokes",
    "4517": "small purple artichokes",
    "4518": "large purple artichokes",
    "4519": "baby cocktail artichokes",
    "4521": "large green asparagus",
    "4522": "small white asparagus",
    "4523": "large white asparagus",
    "4524": "tips asparagus",
    "4527": "chinese long snake beans",
    "4528": "fava broad beans",
    "4529": "lima beans",
    "4530": "pole runner stick beans",
    "4531": "purple hull beans",
    "4532": "shell beans",
    "4533": "wax yellow beans",
    "4534": "winged beans",
    "4536": "mung bean sprouts",
    "4537": "baby golden beets",
    "4538": "baby red beets",
    "4539": "bunch beets",
    "4540": "loose beets",
    "4542": "beet greens",
    "4543": "belgian endive witloof chicory",
    "4544": "small baby bok choy pak choi",
    "4545": "bok choy pak choi",
    "4546": "see also sweet potato boniato",
    "4547": "broccoli rabe italian rapini chinese gai lan",
    "4548": "florettes broccoli",
    "4550": "brussels sprouts",
    "4552": "chinese napa wong bok cabbage",
    "4553": "taylors gold pears",
    "4554": "red cabbage",
    "4555": "savoy green cabbage",
    "4558": "cactus leaves nopales pads",
    "4559": "cardoon cardoni",
    "4560": "baby carrots",
    "4561": "french carrots",
    "4562": "loose carrots",
    "4563": "carrot sticks carrots",
    "4566": "florettes cauliflower",
    "4567": "green cauliflower",
    "4568": "purple cauliflower",
    "4572": "large cauliflower",
    "4573": "baby cauliflower",
    "4575": "hearts celery",
    "4576": "celery sticks",
    "4582": "large bunch celery",
    "4583": "large bunch celery",
    "4584": "large green includes keitt and francis varieties mango",
    "4585": "celery root celeriac",
    "4586": "green chard swiss silverbeet",
    "4587": "red chard swiss silverbeet",
    "4589": "sweet corn baby",
    "4590": "sweet corn bi color",
    "4592": "armenian cucumber",
    "4593": "english hot house long seedless telegraph continental cucumber",
    "4594": "japanese white cucumber",
    "4595": "lemon cucumber",
    "4596": "pickling gherkin cucumber",
    "4598": "see also radish daikon",
    "4599": "baby eggplant aubergine",
    "4600": "baby white eggplant aubergine",
    "4601": "japanese eggplant aubergine",
    "4602": "white eggplant aubergine",
    "4604": "endive chicory",
    "4605": "green escarole batavian chicory",
    "4606": "fiddlehead ferns",
    "4607": "chinese or indian mustard gai gui choy",
    "4608": "regular garlic",
    "4609": "elephant garlic",
    "4612": "regular ginger root",
    "4614": "collard greens",
    "4615": "dandelion greens",
    "4616": "mustard synonymous with gai gui choy greens",
    "4617": "polk greens",
    "4618": "texas mustard greens",
    "4619": "turnip greens",
    "4625": "horseradish root",
    "4626": "jicama yam bean",
    "4627": "kale",
    "4628": "kohlrabi",
    "4629": "regular leeks",
    "4630": "baby leeks",
    "4631": "bibb flat round lettuce",
    "4632": "boston butter lettuce",
    "4633": "hydroponic lettuce",
    "4634": "iceberg lettuce",
    "4635": "red seedless all others not listed under grapes",
    "4636": "red globe grapes",
    "4637": "red seeded all others not listed above grapes",
    "4638": "fantasy marroo grapes",
    "4639": "mache lettuce",
    "4640": "romaine cos lettuce",
    "4644": "malanga",
    "4645": "small regular button mushrooms",
    "4646": "black forest mushrooms",
    "4647": "chanterelle mushrooms",
    "4648": "cremini brown swiss mushrooms",
    "4649": "oyster mushrooms",
    "4650": "portabella synonymous with cremini brown swiss mushrooms",
    "4651": "shiitake mushrooms",
    "4652": "wood ear mushrooms",
    "4655": "regular green okra",
    "4656": "chinese okra",
    "4657": "red okra",
    "4658": "boiling onions",
    "4659": "bulb onions",
    "4660": "pearl onions",
    "4661": "pickling white onions",
    "4662": "shallots onions",
    "4663": "white onions",
    "4664": "regular red on the vine truss tomatoes",
    "4665": "small yellow brown onions",
    "4671": "parsley root hamburg",
    "4672": "parsnip",
    "4673": "blackeyed peas",
    "4674": "green peas",
    "4675": "sugar snap peas",
    "4677": "anaheim green and red peppers capsicums",
    "4678": "banana yellow long peppers capsicums",
    "4679": "bell field grown brown peppers capsicums",
    "4680": "bell field grown golden yellow peppers capsicums",
    "4681": "small bell field grown green peppers capsicums",
    "4682": "bell field grown orange peppers capsicums",
    "4683": "bell field grown purple peppers capsicums",
    "4684": "bell field grown white peppers capsicums",
    "4685": "chili dried peppers capsicums",
    "4686": "chili green peppers capsicums",
    "4687": "cubanelle peppers capsicums",
    "4688": "bell greenhouse red peppers capsicums",
    "4689": "bell greenhouse yellow peppers capsicums",
    "4690": "hot hungarian peppers capsicums",
    "4691": "hot mixed peppers capsicums",
    "4692": "hungarian wax peppers capsicums",
    "4693": "jalapeno green mexican peppers capsicums",
    "4694": "jalapeno red mexican peppers capsicums",
    "4695": "japanese red peppers capsicums",
    "4696": "long hot green peppers capsicums",
    "4697": "long hot red peppers capsicums",
    "4698": "morita chili peppers capsicums",
    "4699": "negro peppers capsicums",
    "4700": "new mexico peppers capsicums",
    "4701": "pasilla green peppers capsicums",
    "4702": "pasilla red peppers capsicums",
    "4703": "pasilla pod peppers capsicums",
    "4704": "pinole peppers capsicums",
    "4705": "poblano peppers capsicums",
    "4706": "red cheese peppers capsicums",
    "4707": "red finger peppers capsicums",
    "4708": "red pimiento sweet long peppers capsicums",
    "4709": "serrano peppers capsicums",
    "4723": "creamer red potato",
    "4724": "creamer white potato",
    "4725": "russet potato",
    "4726": "long white potato",
    "4727": "yellow potato",
    "4734": "mini pumpkin",
    "4735": "regular pumpkin",
    "4738": "radicchio",
    "4739": "black radish",
    "4740": "bunched white radish",
    "4741": "italian red radish",
    "4742": "red radish",
    "4743": "white icicle radish",
    "4745": "regular rhubarb",
    "4747": "regular rutabagas swede",
    "4750": "acorn table queen squash",
    "4751": "acorn golden squash",
    "4752": "acorn swan white table queen squash",
    "4753": "australian blue squash",
    "4754": "baby scallopini squash",
    "4755": "baby summer green squash",
    "4756": "baby green zucchini courgette squash",
    "4757": "banana squash",
    "4758": "buttercup squash",
    "4759": "butternut squash",
    "4760": "calabaza squash",
    "4761": "chayote choko squash",
    "4762": "extra large artichokes",
    "4763": "delicata sweet potato squash",
    "4764": "sweet dumpling squash",
    "4765": "gem squash",
    "4766": "golden delicious squash",
    "4767": "golden nugget squash",
    "4768": "hubbard squash",
    "4769": "kabocha squash",
    "4770": "hass avocados",
    "4771": "medium green avocados",
    "4772": "chili yellow peppers capsicums",
    "4773": "patty pan summer squash",
    "4774": "red kuri squash",
    "4775": "scallopini squash",
    "4776": "spaghetti vegetable squash",
    "4777": "sunburst yellow squash",
    "4778": "regular yellow tomatoes",
    "4779": "sweet mama squash",
    "4780": "turban squash",
    "4781": "white squash",
    "4782": "yellow straightneck squash",
    "4783": "foo qua bitter melon gourd",
    "4784": "yellow crookneck squash",
    "4790": "sugar cane",
    "4791": "sunchokes jerusalem artichokes",
    "4792": "golden tamarillo",
    "4793": "red tamarillo",
    "4794": "small taro root dasheen",
    "4795": "large taro root dasheen",
    "4796": "cherry red tomatoes",
    "4797": "cherry yellow tomatoes",
    "4798": "small greenhouse hydroponic regular red tomatoes",
    "4799": "large greenhouse hydroponic regular red tomatoes",
    "4800": "native home grown tomatoes",
    "4801": "tomatillos husk tomatoes",
    "4802": "dried tomatoes",
    "4803": "teardrop pear red tomatoes",
    "4804": "teardrop pear yellow tomatoes",
    "4805": "small vine ripe regular red tomatoes",
    "4809": "baby turnip",
    "4810": "bunch banded turnip",
    "4811": "purple top turnip",
    "4812": "white turnip",
    "4814": "water chestnuts",
    "4815": "watercress",
    "4816": "golden sweet potato yam kumara",
    "4817": "large red orangy flesh sweet potato yam kumara",
    "4819": "yuca root cassava manioc",
    "4860": "dried apple slices",
    "4861": "dried apricots",
    "4862": "dried dates",
    "4864": "dried pineapple",
    "4865": "regular dried fruit prunes",
    "4866": "pitted dried fruit prunes",
    "4868": "black dried fruit raisins",
    "4869": "golden yellow dried fruit raisins",
    "4884": "arugula rocket",
    "4885": "basil",
    "4886": "opal basil",
    "4887": "sweet basil",
    "4888": "chives",
    "4889": "cilantro chinese parsley coriander",
    "4890": "chinese yali pears",
    "4891": "dill",
    "4892": "baby dill",
    "4893": "pickling dill",
    "4894": "lemongrass",
    "4895": "marjoram",
    "4896": "mint",
    "4897": "oregano",
    "4898": "oyster plant salsify",
    "4899": "regular curly parsley",
    "4901": "italian continental french parsley",
    "4903": "rosemary",
    "4904": "sage",
    "4905": "sorrel",
    "4906": "tarragon",
    "4907": "thyme",
    "4908": "vanilla bean",
    "4924": "almonds",
    "4926": "brazilnuts",
    "4927": "chestnuts",
    "4928": "cobnut hazelnut filberts",
    "4929": "mixed nuts",
    "4930": "peanuts",
    "4931": "raw peanuts",
    "4932": "roasted salted peanuts",
    "4933": "roasted unsalted peanuts",
    "4936": "pecans",
    "4938": "pine nuts pignoli",
    "4939": "natural pistachio",
    "4940": "red pistachio",
    "4942": "sunflower seeds",
    "4943": "regular walnuts",
    "4944": "black walnuts",
    "4945": "white walnuts",
    "4957": "blue black seeded all others not listed above grapes",
    "4958": "medium lemons",
    "4959": "large red includes tommy atkins kent palmer vandyke edward hayden mango",
    "4960": "fragrant pears",
    "4961": "large yellow includes oro ataulfo honey manila varieties mango"
}
"""Dictionary mapping a string numeric PLU code to a string description."""

def get_code(keywords):
    """Return a list of string numeric PLU codes matching keywords.

    Args:
        keywords: List of string keywords describing the PLU code.
    Returns:
        List of string numeric PLU codes matching keywords in ascending order.
    """
    keyword_set = set([keyword.strip().lower() for keyword in keywords
                       if (isinstance(keyword, str) and
                           (len(keyword.strip()) > 0))])
    is_organic = False
    if 'organic' in keyword_set:
        is_organic = True
        keyword_set.remove('organic')

    if len(keyword_set) <= 0:
        return []

    match_set = set()
    for code, description in _PLU_MAP.items():
        for keyword in keyword_set:
            if keyword not in description:
                break
        else:
            if is_organic:
                # Add the organic prefix
                match_set.add('9' + code)
            else:
                match_set.add(code)
    return sorted(match_set)

def _sanitize_code(code):
    """Return code with non-digit characters removed.

    Args:
        code: String containing digit and other characters.
    Returns:
        String containing only digit characters.
    """
    if not isinstance(code, str):
        raise TypeError('code must be a string.')
    return re.sub('[^\d]', '', code)

def get_description(code):
    """Return the description for code.

    Args:
        code: String numeric PLU code.
    Returns:
        String description for code.
    """
    code = _sanitize_code(code)
    length = len(code)
    if length < 4:
        return ''
    if length > 5:
        return ''

    is_organic = False
    if length == 5:
        if code.startswith('9'):
            # Organic prefix
            is_organic = True
        code = code[1:]

    # At this point, code is 4 digits
    if code in _PLU_MAP:
        description = _PLU_MAP[code]
        if is_organic:
            if 'napa' in description:
                # Easter egg
                description += '. Over 9000!'
            return 'organic ' + description
        else:
            return description
    else:
        return ''

def parse_csv(path, delimiter=','):
    """Parse the PLU code CSV text file at path.

    Args:
        path: String path to the PLU code CSV text file.
        delimiter: Optional string delimiter in the CSV text file.
            Defaults to ",".
    """
    if not isinstance(path, str):
        raise TypeError(
            'path must be a valid string path to a CSV text file.')
    if not os.path.isfile(path):
        raise ValueError(
            'path must be a valid string path to a CSV text file.')
    if not isinstance(delimiter, str):
        raise TypeError('delimiter must be an 1 character string.')
    if len(delimiter) != 1:
        raise ValueError('delimiter must be an 1 character string.')

    keyword_list = []
    keyword_set = set()
    plu_map = {}
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            code = _sanitize_code(row.get('PLU'))
            commodity = row.get('COMMODITY').strip().lower()
            variety = row.get('VARIETY').strip().lower()
            if 'retailer' in variety:
                continue
            size = row.get('SIZE').strip().lower()
            aka = row.get('AKA').strip().lower()

            if not code.isdigit():
                continue
            if len(code) != 4:
                continue
            if code in plu_map:
                print('PLU code {0} is already defined!'.format(code))
                continue

            columns = [_KEYWORD_PATTERN.finditer(variety),
                       _KEYWORD_PATTERN.finditer(aka),
                       _KEYWORD_PATTERN.finditer(commodity)]
            if (len(size) > 0) and (not size.startswith('all')):
                columns.insert(0, _KEYWORD_PATTERN.finditer(size))

            keyword_list.clear()
            keyword_set.clear()
            for iterator in columns:
                for match in iterator:
                    keyword = match.group('keyword')
                    if (isinstance(keyword, str) and (len(keyword) > 0) and
                        (keyword not in keyword_set)):
                        keyword_list.append(keyword)
                        keyword_set.add(keyword)

            plu_map[code] = ' '.join(keyword_list)

    for code in sorted(plu_map.keys()):
        # Use json to backslashreplace non-ASCII characters
        print('    "{0}": {1},'.format(code, json.dumps(plu_map[code])))


class _UnitTest(unittest.TestCase):
    def test_KEYWORD_PATTERN(self):
        """Test the regular expression pattern pulling out keywords."""
        for value in ['', '...', '---', '    ']:
            self.assertIsNone(_KEYWORD_PATTERN.search(value))
        for value, expected in [
            ('foobar', ['foobar']),
            ('foo bar', ['foo', 'bar']),
            ('foo bar baz', ['foo', 'bar', 'baz']),
            ("foo's bar", ["foo's", 'bar']),
            ("d'estivale apples", ["d'estivale", 'apples']),
            ('3-7 lbs', ['3', '7', 'lbs']),
            ('3-pack (3 pints)', ['3', 'pack', '3', 'pints'])]:
            self.assertEqual(_KEYWORD_PATTERN.findall(value), expected)
        for value in _PLU_MAP.values():
            self.assertEqual(_KEYWORD_PATTERN.findall(value), value.split())

    def test_PLU_MAP(self):
        """Test the dictionary mapping a PLU code to its description."""
        self.assertIsInstance(_PLU_MAP, dict)
        for code, description in _PLU_MAP.items():
            self.assertIsInstance(code, str)
            self.assertTrue(code.isdigit())
            self.assertEqual(len(code), 4)
            self.assertTrue(code.startswith(('3', '4')))
            self.assertEqual(code.strip().lower(), code)
            self.assertIsInstance(description, str)
            self.assertGreater(len(description), 0)
            self.assertEqual(description.strip().lower(), description)

    def test_get_code(self):
        """Test returning the PLU code matching a list of keywords."""
        for value in [None, 42]:
            self.assertRaises(TypeError, get_code, value)
        for value in [[], [None, 42, '', []],
                      ['foobar'], ['foo', 'bar'], ['foo', 'bar', 'baz'],
                      ['Organic'], ['organic'],
                      ['Organic', 'foobar'], ['organic', 'foobar'],
                      ['Organic', 'foo', 'bar'], ['organic', 'foo', 'bar']]:
            self.assertEqual(get_code(value), [])
        for expected, description in _PLU_MAP.items():
            keywords = description.split()
            for value in [keywords, list(reversed(keywords))]:
                self.assertIn(expected, get_code(value))
                for organic in [['Organic'] + value,
                                ['organic'] + value,
                                value + ['Organic'],
                                value + ['organic']]:
                    self.assertIn('9' + expected, get_code(organic))

        for value in ['napa', 'Napa', 'NAPA']:
            self.assertEqual(get_code([value]), ['4552'])
        for value in [['baby', 'white'],
                      ['baby', 'white', 'eggplant'],
                      ['aubergine', 'baby', 'white'],
                      ['White', 'Baby'],
                      ['White', 'Baby', 'eggplant'],
                      ['aubergine', 'White', 'Baby']]:
            self.assertEqual(get_code(value), ['4600'])

    def test_sanitize_code(self):
        """Test removing non-digit characters."""
        for value in [None, 42, []]:
            self.assertRaises(TypeError, _sanitize_code, value)
        for value, expected in [
            ('', ''),
            ('1234', '1234'),
            (' 1234', '1234'),
            ('1 234', '1234'),
            ('12 34', '1234'),
            ('123 4', '1234'),
            ('1234 ', '1234'),
            ('?1234', '1234'),
            ('1?234', '1234'),
            ('12?34', '1234'),
            ('123?4', '1234'),
            ('1234?', '1234'),
            ('1 23 4', '1234'),
            (' 1 23 4', '1234'),
            ('1 23 4 ', '1234'),
            ('1 2 3 4', '1234'),
            (' 1 2 3 4', '1234'),
            ('1 2 3 4 ', '1234'),
            ('foo 42 bar', '42')]:
            self.assertEqual(_sanitize_code(value), expected)
        for code in _PLU_MAP.keys():
            for value in [' ', '?', '!', 'a', 'foo']:
                for i in range(len(code) + 1):
                    digits = list(code)
                    digits.insert(i, value)
                    self.assertEqual(_sanitize_code(''.join(digits)), code)

    def test_get_description(self):
        """Test returning the description for a PLU code."""
        for value in [None, 42, []]:
            self.assertRaises(TypeError, get_description, value)
        for value in ['', 'foobar', 'fo\u00f6b\u00e4r',
                      '1', '42', '123', '1234', '12345', '123456',
                      '81234', '91234']:
            self.assertEqual(get_description(value), '')
        for code, expected in _PLU_MAP.items():
            self.assertEqual(get_description(code), expected)
            self.assertEqual(get_description('8' + code), expected)
            if code == '4552':
                # Test Easter egg
                self.assertEqual(get_description('9' + code),
                                 'organic ' + expected + '. Over 9000!')
            else:
                self.assertEqual(get_description('9' + code),
                                 'organic ' + expected)
            for i in range(1, 8):
                self.assertEqual(get_description(str(i) + code), expected)
            for i in range(1, 3):
                self.assertEqual(get_description(str(i) + code[1:]), '')
            for i in range(5, 10):
                self.assertEqual(get_description(str(i) + code[1:]), '')

    def test_parse_csv(self):
        """Test the guard clauses in parse_csv()."""
        for value in [None, 42, []]:
            self.assertRaises(TypeError, parse_csv, value)
            self.assertRaises(TypeError, parse_csv, 'plucode.py', value)
        for value in ['', 'foobar', 'fo\u00f6b\u00e4r']:
            self.assertRaises(ValueError, parse_csv, value)
            self.assertRaises(ValueError, parse_csv, 'plucode.py', value)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-c', '--code', default='',
        help='print the description for the specified PLU code')
    parser.add_argument(
        '-f', '--file', default='',
        help='path to the PLU code CSV text file')
    parser.add_argument(
        '-l', '--lookup', nargs='+', default=[],
        help='print the PLU code matching the specified keywords')
    parser.add_argument(
        '-t', '--training', action='store_true',
        help='print training phrases')
    args = parser.parse_args()

    if args.code.isdigit() and (len(args.code) > 3):
        print(get_description(args.code))
    elif os.path.isfile(args.file):
        parse_csv(args.file)
    elif len(args.lookup) > 0:
        for code in get_code(args.lookup):
            print(code)
    elif args.training:
        import itertools
        for carriers, examples in [
            (_CODE_CARRIER_PHRASES, _CODE_EXAMPLES),
            (_DESCRIPTION_CARRIER_PHRASES, _DESCRIPTION_EXAMPLES)]:
            for t in itertools.product(carriers, examples):
                print(' '.join(list(t)))
    else:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(_UnitTest)
        unittest.TextTestRunner(verbosity=2).run(suite)

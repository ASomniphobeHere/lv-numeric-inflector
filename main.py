import re
import requests
import string
from tqdm import tqdm

# Skaitļa vārdu veidotājs
#  
# Izstrādātāji:
# Adriāns Piliksers
# Patriks Gustavs Rinkevičs



NUMBERS = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
EMPT = set()


ones = ['null',
        'vien',
        'div',
        'tr',
        'četr',
        'piec',
        'seš',
        'septiņ',
        'astoņ',
        'deviņ']

appends = ['', 'tūkstoš', 'miljon', 'miljard']

teens = ['nulle',
         'vienpadsmit',
         'divpadsmit',
         'trīspadsmit',
         'četrpadsmit',
         'piecpadsmit',
         'sešpadsmit',
         'septiņpadsmit',
         'astoņpadsmit',
         'deviņpadsmit']

tens = ['nulle',
        'desmit',
        'divdesmit',
        'trīsdesmit',
        'četrdesmit',
        'piecdesmit',
        'sešdesmit',
        'septiņdesmit',
        'astoņdesmit',
        'deviņdesmit']

hundreds = ['nulle',
            'simt',
            'divsimt',
            'trīssimt',
            'četrsimt',
            'piecsimt',
            'sešsimt',
            'septiņsimt',
            'astoņsimt',
            'deviņsimt']

thousands = ['',
             '',
             'div',
             'trīs',
             'četr',
             'piec',
             'seš',
             'septiņ',
             'astoņ',
             'deviņ']

orderedones = ['nullt',
               'pirm',
               'otr',
               'treš',
               'ceturt',
               'piekt',
               'sest',
               'septīt',
               'astot',
               'devīt']

inflectionend = [  # gender, amount, order, declination,
    [  # Male
        [  # Singular
            ['i', 'u', 'iem', 'us', 'iem', 'os'],  # Unordered
            ['ais', 'ā', 'ajam', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['i', 'u', 'iem', 'us', 'iem', 'os'],  # Unordered
            ['ie', 'o', 'ajiem', 'os', 'ajiem', 'ajos']  # Ordered
        ]
    ],
    [  # Female
        [  # Singular
            ['as', 'u', 'ām', 'as', 'ām', 'ās'],  # Unordered
            ['ā', 'ās', 'ajai', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['as', 'u', 'ām', 'as', 'ām', 'ās'],  # Unordered
            ['ās', 'o', 'ajām', 'ās', 'ajām', 'ajās']  # Ordered
        ]
    ]
]

onecase = [  # gender, amount, order, declination,
    [  # Male
        [  # Singular
            ['s', 'a', 'am', 'u', 'u', 'ā'],  # Unordered
            ['ais', 'ā', 'ajam', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['i', 'u', 'iem', 'us', 'iem', 'os'],  # Unordered
            ['ie', 'o', 'ajiem', 'os', 'ajiem', 'ajos']  # Ordered
        ]
    ],
    [  # Female
        [  # Singular
            ['a', 'as', 'ai', 'u', 'u', 'ā'],  # Unordered
            ['ā', 'ās', 'ajai', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['as', 'u', 'ām', 'as', 'ām', 'ās'],  # Unordered
            ['ās', 'o', 'ajām', 'ās', 'ajām', 'ajās']  # Ordered
        ]
    ]
]
zerocase = [  # gender, amount, order, declination,
    [  # Male
        [  # Singular
            ['e', 'e', 'ei', 'i', 'i', 'e'],  # Unordered
            ['ais', 'ā', 'ajam', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['e', 'e', 'ei', 'i', 'i', 'e'],  # Unordered
            ['ie', 'o', 'ajiem', 'os', 'ajiem', 'ajos']  # Ordered
        ]
    ],
    [  # Female
        [  # Singular
            ['a', 'as', 'ai', 'u', 'u', 'ā'],  # Unordered
            ['ā', 'ās', 'ajai', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['e', 'e', 'ei', 'i', 'i', 'e'],  # Unordered
            ['ās', 'o', 'ajām', 'ās', 'ajām', 'ajās']  # Ordered
        ]
    ]
]

threecase = [  # gender, amount, order, declination,
    [  # Male
        [  # Singular
            ['īs', 'iju', 'ijiem', 'īs', 'ijiem', 'ijos'],  # Unordered
            ['ais', 'ā', 'ajam', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['īs', 'iju', 'ijiem', 'īs', 'ijiem', 'ijos'],  # Unordered
            ['ie', 'o', 'ajiem', 'os', 'ajiem', 'ajos']  # Ordered
        ]
    ],
    [  # Female
        [  # Singular
            ['īs', 'iju', 'ijām', 'īs', 'ijām', 'ijās'],  # Unordered
            ['ā', 'ās', 'ajai', 'o', 'o', 'ajā']  # Ordered
        ],
        [  # Plural
            ['īs', 'iju', 'ijām', 'īs', 'ijām', 'ijās'],  # Unordered
            ['ās', 'o', 'ajām', 'ās', 'ajām', 'ajās']  # Ordered
        ]
    ]
]

def encodeLoc(loc: str) -> int:
    match loc:
        case 'Nominatīvs':
            return 0
        case "Ģenitīvs":
            return 1
        case "Datīvs":
            return 2
        case "Akuzatīvs":
            return 3
        case "Lokatīvs":
            return 5
        case _:
            return 0


def encodeGen(dzim: str) -> int:
    if (dzim == "Vīriešu"):
        return 0
    return 1


def encodeNum(skait: str) -> int:
    if (skait == "Vienskaitlis"):
        return 0
    return 1

def analyseSent(line: str) -> list:
    words = line.split()
    modified_line = ''
    num_exists = False
    for idx, word in enumerate(words):
        try:
            if re.match(r'^\d+(\.\d*)?$', word):  # Using regex to check for numbers
                print(f"Word: {word}")
                if((word.count('.') == 1 and word[-1] == '.') or word.count('.') == 0):
                    print(f"Got Word: {word}")
                    cleaned_word = ''.join([char for char in words[idx+1] if char not in string.punctuation])
                    req = requests.get(f"http://api.tezaurs.lv:8182/analyze/{cleaned_word}")
                    response = req.json()[0]
                    num1 = word.strip('.')
                    inf = encodeLoc(response['Locījums'])
                    gen = encodeGen(response['Dzimte'])
                    orde = 0
                    if (word[-1] == '.'):
                        orde = 1
                    coun = encodeNum(response['Skaitlis'])
                    modified_line += number_to_words(num1, inf, gen, orde, coun) + ' '
                    num_exists = True
                else:
                    modified_line += word + ' '
            else:
                modified_line += word + ' '
        except Exception as e:
            print(e)
            modified_line += ' ' + word
            continue
    modified_line = modified_line[0].upper() + modified_line[1:-1] + '\n'
    return modified_line, num_exists


def number_to_words(number: str, inflection: int = 0, gender: int = 0, order: int = 0, amount: int = 1) -> str:
    # Returns a latvian number as a collection of words
    # Input:
    # Number, inflection, gender, order, amount  
    # Output:
    # Number as a string

    # preprocessing for groups of 3
    while len(number) % 3 != 0:
        number = '0' + number
    groups = [number[i:i+3] for i in range(0, len(number), 3)]
    groups = groups[::-1]
        
    # null case
    if groups[0] == '000' and len(groups) == 1:
        ending = zerocase[gender][amount][order][inflection]
        if order:
            words = orderedones[0]
        else:
            words = ones[0]
        return words + ending
        # Premature exit

    words = ''

    for ind, part in enumerate(groups):
        if part == '000': # Skip empty groups
            continue
        if words != '':
            words = ' ' + words
        words = appends[ind] + words
        if part[1] != '1' or part[2] == '0':  # case with no teens
            if part[2] != '0':
                if ind == 1:
                    words = thousands[int(part[2])] + words
                else:
                    if words != '':
                        words = ' ' + words
                    if order:  # ordered digits
                        words = orderedones[int(part[2])] + words
                    else:
                        words = ones[int(part[2])] + words
            if part[1] != '0':  # tens
                if words != '':
                    words = ' ' + words
                words = tens[int(part[1])] + words

        else:  # teens case
            if words != '':
                words = ' ' + words
            words = teens[int(part[2])] + words

        if part[0] != '0':  # hundreds
            if words != '':
                words = ' ' + words
            words = hundreds[int(part[0])] + words

    ending = ''
    for ind, part in enumerate(groups):
        if part == '000': # Skip empty groups
            continue
        if order:
            ending = inflectionend[gender][amount][order][inflection]
        else:
            if groups[0][2] == '0':
                pass
            elif groups[0][1] == '1':
                pass
            else:
                if groups[0][2] == '1':
                    ending = onecase[gender][amount][order][inflection]
                elif groups[0][2] == '3':
                    ending = threecase[gender][amount][order][inflection]
                else:
                    ending = inflectionend[gender][amount][order][inflection]

    words = words + ending
    return words


if __name__ == "__main__":
    # with open("notclean.txt", "r", encoding='UTF-8') as TEXT, open("modified_lines.txt", "w", encoding='UTF-8') as MODIFIED_TEXT:
    TEXT = ["Jā, tad nosūtīšu jums uz e-pastu polisi un tad tā prēmijas summa, ko saņemsiet, ir 900 eiro."]
    for line_num, line in enumerate(TEXT):
        if line_num > 500:
            break
        modified_line, res = analyseSent(line.strip())
        print(res)
        if res:
            # pri.write(modified_line)  # Write modified line to the separate text file
            print(f"Line num: {line_num} | Modified line: {modified_line} | Original line: {line}")


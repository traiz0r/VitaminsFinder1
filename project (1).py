import requests
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd

iherb_url='https://ru.iherb.com/' 
start_time = time.time()
cur_time=datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}
product_data=[]
globalchoice=[]

top_twelve=[]

def main(): # основная функция
        inquiry= input("Введите ваш запрос:\n") #ввод запроса
        inquiry=inquiry.replace(" ","%20")
        href='https://ru.iherb.com/'+f'search?kw={inquiry}&cids=1855'# переход по ссылке поиска


        sol=input('\nВы хотите использовать фильтры? д/н\n')
        if sol.lower()=='д' or sol.lower()=='l':
                url=filtration(href)# (*) Функция вызова функций фильтрации, сюда же вернеться значение с которым мы и дальше будем работать
                # url=href
        else:
                print('Результат без использования фильтрации')
                url=href

        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.text,'lxml')
        all_product_links=soup.find_all('a', class_='absolute-link product-link')
        print(f'Количество товаров: {len(all_product_links)}')
        if len(soup.find_all(class_='no-results')) != 0: #проверка на существование такого товара
                print(f'Не удается найти элементы, соответствующие запросу: " {inquiry} "\n ')
                print('The end!')
        else:
            print("Бестселлеры")
            made_url(url+f'&sr=4')

            print("Цена по возрастанию")
            made_url(url+f'&sr=2')
            report()
            save(inquiry,start_time)       
# --------------------------------------------

def made_url(url):
    response=requests.get(url,headers=headers)
    soup=BeautifulSoup(response.text,'lxml')
    all_product_links=soup.find_all('a', class_='absolute-link product-link')
    parsing(all_product_links)


def parsing(all_product_links):
    counter=0
    for href in range(len(all_product_links)):
        if counter<6:
            dict={}
            url=all_product_links[href]['href']
            response=requests.get(url,headers=headers)
            soup=BeautifulSoup(response.text,'lxml')
            try:
                availability=soup.find("div",class_="text-danger stock-status-text").text
            except:
                comments=soup.find("a",class_="rating-count").find("span").text
                # if availability.find("Нет в наличии")!=-1 and int(comments)>400:
                if int(comments)>400:
                    print(f'Обрабатываем товар {counter}')
                    print(f"href: {all_product_links[href]['href']}")
                    name_of_product=soup.find(id='name').text #имя продукта
                    dict["name_of_product"]=name_of_product
                    dict["href"]=all_product_links[href]['href']
                    try:    
                            new_price=soup.find('b',class_='s24').text
                            old_price=soup.find(id='price').text
                            dict["new_price"]=new_price
                            dict["old_price"]=old_price
                    except:
                            old_price=soup.find(id='price',class_='col-xs-15 col-md-15 price our-price').text
                            dict["old_price"]=old_price
                    company=soup.find("span",itemprop="name").find("bdi").text
                    dict["company"]=company
                    try:
                        amount_of_capsulse=soup.find("div",class_="attribute-group-количество-в-упаковке attribute-tile-group").find_all("div",class_="attribute-name")
                        capsulse=''
                        for amount in amount_of_capsulse:
                            capsulse+=str(amount["data-val"])+" \ "
                    except:
                        try:
                            capsulse=soup.find("div",class_="item combo-shaded stock-onsale").find("div",class_="attribute-name").text
                        except:
                            capsulse=name_of_product.split(",")[-1]
                    mark=(soup.find('a',class_='stars'))['title'][0:5]

                    dict["mark"]=mark       
                    dict["amount_of_capsulse"]=capsulse
                    dict["amount_of_comments"]=comments
                    solution=filter_name(name_of_product,top_twelve)
                    print(f'solution={solution}')
                    if solution==False:
                        print("Добавляем товар в словарь бестселлеров")
                        top_twelve.append(dict)
                        counter+=1
        else:
            break


def filter_name(name,product_list):
    print("Проверяем на наличие в словаре")
    print(f'len: {len(product_list)}')
    if len(product_list)!=0:
        for elem in range(len(product_list)):
            if name==product_list[elem]["name_of_product"]:
                return (True)
            else:
                return (False)
    else:
        return(False)
    
def save(inquiry,start_time):
        # -----------
        # inquiry=inquiry
        search_info={'Дата и Время запроса:':[time.ctime()],
                        'Запрос пользователя:':[inquiry],
                        "Фильтры:":[globalchoice]}

        sheet2=pd.DataFrame(search_info)
        sheet1=pd.DataFrame(top_twelve) #сохраням на третий лист данные из топ 5 бесцеллеров и цены по возрастанию
         # ---------------------------------------------------------------------
        print("Сохраняем все в отчет.")
        # пишем в наш файл данные----------------------------------------------
        sheets_name={'top_ten_products':sheet1,'info':sheet2}
        writer=pd.ExcelWriter(f'./iherb{cur_time}.xlsx',engine='xlsxwriter')
        for sheet_name in sheets_name.keys():
                sheets_name[sheet_name].to_excel(writer,sheet_name=sheet_name)
        writer.save()
        # -----------
        print("Время выполнения:",round(time.time()-start_time))

def filtration(href):#функция фильтрации
        # Словарь содержащий список фильтров и необходимых для отображения в браузере id
        filters={
                'Цена':
                        {1:'0-500',2:'500-1000',3:'1000-2000',4:'2000-3000',5:'3000+'},
                'Бренды':{
                        1:["Now Foods","NOW"],
                        2:["California Gold Nutrition","CGN"],
                        3:["Solgar","SOL"],
                        4:["Doctor's Best","DRB"],
                        5:["21st Century","CEN"],
                        6:["Life Extension","LEX"],
                        7:["Nature's Way","NWY"],
                        8:["Nature's Plus","NAP"],
                        9:["Nature's Bounty","NRT"],
                        10:["Solaray","SOR"],
                        11:["1Kvit-C","OKV"],
                        12:["A Vogel","AVG"],
                        13:["A.C. Grace Company","ACG"],
                        14:["Absolute Nutrition","ABN"],
                        15:["Advance Physician Formulas","APF"],
                        16:["Advanced Naturals","AVS"],
                        17:["Advanced Orthomolecular Research AOR","AOR"],
                        18:["Ageless Foundation Laboratories","NAT"],
                        19:["AirBorne","AIB"],
                        20:["Algalife","AAL"],
                        21:["Alka-Seltzer","ALS"],
                        22:["Alkalife","AKF"],
                        23:["All One, Nutritech","ALO"],
                        24:["Allergy Research Group","ALG"],
                        25:["Allimax","ALL"],
                        26:["ALLMAX Nutrition","AMX"],
                        27:["AllVia","AVI"],
                        28:["Almased USA","ALM"],
                        29:["Alta Health","AHP"],
                        30:["Amazing Grass","AMG"],
                        31:["Amazing Herbs","AHR"],
                        32:["Amazing Nutrition","AMN"],
                        33:["American Biotech Labs","ABL"],
                        34:["American Health","AMH"],
                        35:["appliednutrition","APP"],
                        36:["Arizona Natural","ARZ"],
                        37:["Arrowhead Mills","ARW"],
                        38:["Arthur Andrew Medical","AAM"],
                        39:["Artisana","ATS"],
                        40:["Atkins","ATK"],
                        41:["Aura Cacia","AUR"],
                        42:["Aurora Nutrascience","AUN"],
                        43:["Azo","AZO"],
                        44:["Badger Company","WSB"],
                        45:["Balanceuticals","BAL"],
                        46:["Banyan Botanicals","BYN"],
                        47:["Barlean's","BAR"],
                        48:["Bausch & Lomb","BOC"],
                        49:["Beekeeper's Naturals","BKN"],
                        50:["Belle+Bella","BBE"],
                        51:["Bergin Fruit and Nut Company","BFN"],
                        52:["Bio Nutrition","BIU"],
                        53:["Bio Tech Pharmacal","BTP"],
                        54:["Biochem","BCH"],
                        55:["BioGaia","BGA"],
                        56:["Bioglan","BGL"],
                        57:["Bionorica","BIR"],
                        58:["Bioray","BRY"],
                        59:["BioSchwartz","BTZ"],
                        60:["BioSil by Natural Factors","NFB"],
                        61:["Biotivia","BIV"],
                        62:["Bluebonnet Nutrition","BLB"],
                        63:["Bob's Red Mill","BRM"],
                        64:["BodyBio","DIO"],
                        65:["BodyGold","BGG"],
                        66:["Boogie Wipes","BEW"],
                        67:["BPI Sports","BPI"],
                        68:["Bragg","BRA"],
                        69:["BSN","BSN"],
                        70:["BulletProof","BPF"],
                        71:["Buried Treasure","BUR"],
                        72:["Burt's Bees","BRT"],
                        73:["C.C. Pollen","CCP"],
                        74:["Caleb Treeze Organic Farm","CTF"],
                        75:["California Natural","CAN"],
                        76:["Cardiovascular Research","CVR"],
                        77:["Carlson Labs","CAR"],
                        78:["Catalo Naturals","CAT"],
                        79:["Cellucor","CLL"],
                        80:["Celtic Sea Salt","CSS"],
                        81:["Chapter One","CTO"],
                        82:["Cheong Kwan Jang","KRG"],
                        83:["ChildLife","CDL"],
                        84:["Childlife Clinicals","CLC"],
                        85:["Christopher's Original Formulas","CRO"],
                        86:["Citracal","CCL"],
                        87:["Clear Eyes","CEY"],
                        88:["CodeAge","AGE"],
                        89:["Comvita","CMV"],
                        90:["Controlled Labs","COL"],
                        91:["Coromega","ERB"],
                        92:["Country Farms","CFM"],
                        93:["Country Life","CLF"],
                        94:["Creative Bioscience","CRB"],
                        95:["Culturelle","CTL"],
                        96:["Curlsmith","CSI"],
                        97:["D'adamo","DAD"],
                        98:["Daily Wellness Company","DWC"],
                        99:["Dastony","DAS"],
                        100:["DaVinci Laboratories of Vermont","DVI"],
                        101:["Ddrops","DDP"],
                        102:["De La Cruz","DLC"],
                        103:["Deva","DEV"],
                        104:["Diamond Herpanacine Associates","DFA"],
                        105:["DietWorks","DTW"],
                        106:["Dr. Axe / Ancient Nutrition","ATN"],
                        107:["Dr. Mercola","MCL"],
                        108:["Dr. Murray's","DMY"],
                        109:["Dr. Ohhira's","EFI"],
                        110:["Dr. Sinatra","DSA"],
                        111:["Dr. Talbot's","TAL"],
                        112:["Dr. Tobias","DTB"],
                        113:["Dragon Herbs","DRA"],
                        114:["Dymatize Nutrition","DYZ"],
                        115:["Dynamic Health  Laboratories","DNH"],
                        116:["Earnest Eats","EAE"],
                        117:["Earth Circle Organics","EOR"],
                        118:["Earth's Bounty","ETB"],
                        119:["Earthrise","ETR"],
                        120:["Earthtone Foods","ERT"],
                        121:["Eclectic Institute","ECL"],
                        122:["Ecological Formulas","ECF"],
                        123:["Econugenics","ECN"],
                        124:["Eden Foods","EDN"],
                        125:["Egmont Honey","EGM"],
                        126:["Eidon Mineral Supplements","EID"],
                        127:["Elactia","ECA"],
                        128:["Emerald Laboratories","EMR"],
                        129:["Emergen-C","ALA"],
                        130:["Emerita","EME"],
                        131:["Emu Gold","EMU"],
                        132:["ENADA","NDH"],
                        133:["Ener-C","ENR"],
                        134:["Enzymatic Therapy","EMT"],
                        135:["Enzymedica","ENZ"],
                        136:["EPI","EPI"],
                        137:["Essential Living Foods","ESF"],
                        138:["Estroven","AME"],
                        139:["Eu Natural","EUN"],
                        140:["Everydaze","DAZ"],
                        141:["EVLution Nutrition","EVL"],
                        142:["Exploding Buds","XBD"],
                        143:["Fairhaven Health","FHH"],
                        144:["Flintstones","FLI"],
                        145:["Flora","FLO"],
                        146:["Flower Essence Services","FES"],
                        147:["Foods Alive","FDA"],
                        148:["Force Factor","FOA"],
                        149:["Four Sigmatic","FSM"],
                        150:["Frontier Natural Products","FRO"],
                        151:["Fruily","FIL"],
                        152:["Fungi Perfecti","FPI"],
                        153:["Further Food","FUF"],
                        154:["FutureBiotics","FBS"],
                        155:["Gaia Herbs","GAI"],
                        156:["Gaia Herbs Professional Solutions","GPS"],
                        157:["Garden of Life","GOL"],
                        158:["Gaspari Nutrition","GSN"],
                        159:["GAT","GAT"],
                        160:["Genceutic Naturals","GNT"],
                        161:["Genexa","GXA"],
                        162:["Gerber","GBR"],
                        163:["GNC","GNC"],
                        164:["Golden Flower","GOF"],
                        165:["Goli Nutrition","GOI"],
                        166:["Green Foods","GFC"],
                        167:["GreenPeach","GGP"],
                        168:["Greens First","GRF"],
                        169:["Greens Plus","GRP"],
                        170:["Greens World","GWI"],
                        171:["Greensations","GRN"],
                        172:["Grenade","GRD"],
                        173:["GummiKing","GUM"],
                        174:["Gummiology","GMM"],
                        175:["GummYum!","YMM"],
                        176:["Harmonic Innerprizes","HAR"],
                        177:["Havasu Nutrition","HAV"],
                        178:["Health and Wisdom","HEW"],
                        179:["Health Direct","HED"],
                        180:["Health Plus","HPI"],
                        181:["HealthForce Superfoods","HFC"],
                        182:["HealthyBiom","HBI"],
                        183:["Heather's Tummy Care","HTC"],
                        184:["Herb Pharm","HBP"],
                        185:["Herbal Answers","HAS"],
                        186:["Herbs Etc.","HEC"],
                        187:["Herbs for Kids","HFK"],
                        188:["Heritage Store","HRP"],
                        189:["Hero Nutritional Products","HNP"],
                        190:["Himalaya","HIM"],
                        191:["Honey Gardens","HGS"],
                        192:["Houston Enzymes","HNI"],
                        193:["Hyalogic","HYA"],
                        194:["Hydrant","HYD"],
                        195:["Hydroxycut","HYX"],
                        196:["Hyleys Tea","HYT"],
                        197:["Hyperbiotics","HYB"],
                        198:["iHerb Goods","IHB"],
                        199:["immuneti","IMM"],
                        200:["Innate Response Formulas","INN"],
                        201:["InnovixLabs","INV"],
                        202:["InterPlexus","INP"],
                        203:["ION Biome","IOB"],
                        204:["IP-6 International","IPS"],
                        205:["Irwin Naturals","IRW"],
                        206:["Isopure","NBT"],
                        207:["iWi","IWI"],
                        208:["J R Watkins","WAT"],
                        209:["Jamieson Natural Sources","JAM"],
                        210:["Jarrow Formulas","JRW"],
                        211:["Jigsaw Health","JIG"],
                        212:["Jiva Organics","JVO"],
                        213:["JNX Sports","COB"],
                        214:["JoySpring","JYS"],
                        215:["Julian Bakery","JUB"],
                        216:["JYM Supplement Science","JYM"],
                        217:["Kaged Muscle","KGD"],
                        218:["KAL","CAL"],
                        219:["Kevala","KEV"],
                        220:["Kirkman Labs","KIM"],
                        221:["Kiss My Keto","KMK"],
                        222:["Kolorex","NAS"],
                        223:["KOS","KOO"],
                        224:["Kroeger Herb Co","KHC"],
                        225:["Kuli Kuli","KKI"],
                        226:["Kyolic","WAK"],
                        227:["L'il Critters","LIL"],
                        228:["La Tourangelle","LAT"],
                        229:["Labrada Nutrition","LAB"],
                        230:["Lake Avenue Nutrition","LKN"],
                        231:["Life Enhancement","LEM"],
                        232:["Life Source Basics (WGP Beta Glucan)","LSR"],
                        233:["Life-flo","LFH"],
                        234:["LifeSeasons","LSE"],
                        235:["LifeTime Vitamins","LIF"],
                        236:["Lily of the Desert","LTD"],
                        237:["Lipo Naturals","LPO"],
                        238:["Liquid I.V.","LQD"],
                        239:["Little DaVinci","LDV"],
                        240:["Live Conscious","LVS"],
                        241:["Lonolife","LNO"],
                        242:["LoveBug Probiotics","LVB"],
                        243:["Maca Magic","MAM"],
                        244:["Macrolife Naturals","MGI"],
                        245:["Maine Coast Sea Vegetables","MCV"],
                        246:["Mamma Chia","MCH"],
                        247:["Manuka Doctor","MKD"],
                        248:["Manuka Health","MAN"],
                        249:["ManukaGuard","MAG"],
                        250:["Manukora","MKO"],
                        251:["Mariani Dried Fruit","MFN"],
                        252:["MaryRuth Organics","MRO"],
                        253:["Mason Natural","MAV"],
                        254:["Master Supplements","MSI"],
                        255:["MAV Nutrition","MVN"],
                        256:["Maximum International","MAX"],
                        257:["MediNatura","HEE"],
                        258:["Medix 5.5","MDX"],
                        259:["MegaFood","MGF"],
                        260:["Metabolic Maintenance","MBM"],
                        261:["Michael's Naturopathic","MHN"],
                        262:["Minami Nutrition","MIN"],
                        263:["Miracle Tree","MRA"],
                        264:["Mommy Knows Best","MKB"],
                        265:["Mommy's Bliss","BAB"],
                        266:["Morningstar Minerals","MOR"],
                        267:["Motherlove","MLV"],
                        268:["MRM","MRM"],
                        269:["Mt. Capra","MTC"],
                        270:["MusclePharm","MSF"],
                        271:["Muscletech","MSC"],
                        272:["Mushroom Wisdom","GME"],
                        273:["Naka Herbs & Vitamins Ltd","NAK"],
                        274:["Natierra","NLL"],
                        275:["NatraBio","NBB"],
                        276:["Natrol","NTL"],
                        277:["Naturade","NAD"],
                        278:["Natural Balance","NTB"],
                        279:["Natural Dynamix (NDX)","NDY"],
                        280:["Natural Factors","NFS"],
                        281:["Natural Path Silver Wings","NSW"],
                        282:["Natural Sources","NSI"],
                        283:["Natural Sport","NSS"],
                        284:["Natural Stacks","NSK"],
                        285:["Natural Vitality","PTG"],
                        286:["NaturalCare","NTC"],
                        287:["Naturally Vitamins","NTV"],
                        288:["NaturaNectar","NNR"],
                        289:["Nature Made","NDM"],
                        290:["Nature's Answer","NTA"],
                        291:["Nature's Baby Organics","NAB"],
                        292:["Nature's Herbs","NHB"],
                        293:["Nature's Life","NLI"],
                        294:["Nature's One","NAO"],
                        295:["Nature's Secret","NTS"],
                        296:["Nature's Truth","NTH"],
                        297:["NATURELO","NAU"],
                        298:["NatureWise","NTW"],
                        299:["Navitas Organics","NAV"],
                        300:["NB Pure","NBP"],
                        301:["NeilMed","NMD"],
                        302:["Neocell","NEL"],
                        303:["NeuroScience","NOS"],
                        304:["New Chapter","NCR"],
                        305:["New Nordic","NNO"],
                        306:["Nobi Nutrition","NOB"],
                        307:["Nordic Naturals","NOR"],
                        308:["Norms Farms","NFA"],
                        309:["North American Herb & Spice","NHS"],
                        310:["Nu U Nutrition","NUN"],
                        311:["Nugenix","NGX"],
                        312:["NuNaturals","NNS"],
                        313:["Nutiva","NUT"],
                        314:["Nutra BioGenesis","NBG"],
                        315:["NutraBio Labs","NRB"],
                        316:["NutraLife","NLF"],
                        317:["NutraMedix","NDX"],
                        318:["Nutrex Hawaii","NHI"],
                        319:["Nutrex Research","NRX"],
                        320:["NutriBiotic","NBC"],
                        321:["Nutricology","ARG"],
                        322:["Nutrition Now","NUR"],
                        323:["Nuun","NUU"],
                        324:["Ojio","OJI"],
                        325:["Olbas Therapeutic","OLB"],
                        326:["Olympian Labs","OLY"],
                        327:["Om Mushrooms","OMM"],
                        328:["OmegaVia","OME"],
                        329:["One-A-Day","OAD"],
                        330:["Onnit","ONT"],
                        331:["Optimel","OTL"],
                        332:["Optimox","OPT"],
                        333:["Optimum Nutrition","OPN"],
                        334:["Ora","ORA"],
                        335:["Oregon's Wild Harvest","OWH"],
                        336:["Orgain","OGA"],
                        337:["Organic Excellence","OEX"],
                        338:["Organic India","ORI"],
                        339:["Organic Traditions","OGT"],
                        340:["Oslomega","OSL"],
                        341:["Osteo Bi-Flex","OBF"],
                        342:["Ovega-3","OVG"],
                        343:["OxyLife","OXY"],
                        344:["Pacifica","PAP"],
                        345:["Paradise Herbs","PAR"],
                        346:["PB2 Foods","BPL"],
                        347:["Peptiva","PIV"],
                        348:["PEScience","PEC"],
                        349:["Phillip's","PHP"],
                        350:["pHion Balance","PHI"],
                        351:["Physician's Choice","PHC"],
                        352:["Pines International","PWG"],
                        353:["Pioneer Nutritional Formulas","PIO"],
                        354:["Planetary Herbals","PTF"],
                        355:["PlantFusion","PLF"],
                        356:["Pomona's Universal  Pectin","PMO"],
                        357:["Pranarom","PNM"],
                        358:["Premama","PMA"],
                        359:["Premier Research Labs","RSL"],
                        360:["Primaforce","PMF"],
                        361:["Primal Kitchen","PMK"],
                        362:["Prince of Peace","POP"],
                        363:["Probulin","PBL"],
                        364:["Promensil","PML"],
                        365:["Pronatura","PRN"],
                        366:["ProSupps","PSS"],
                        367:["Protocol for Life Balance","PRT"],
                        368:["Pukka Herbs","PKH"],
                        369:["Puori","PUE"],
                        370:["Pure Essence","PUR"],
                        371:["Pure Indian Foods","PIF"],
                        372:["Pure Planet","OBN"],
                        373:["Pure Protein","PPN"],
                        374:["Pure Synergy","SYN"],
                        375:["Purely Inspired","PLY"],
                        376:["PureMark Naturals","PMN"],
                        377:["Purity Products","PPS"],
                        378:["Quality of Life Labs","QLL"],
                        379:["Quantum Health","QUA"],
                        380:["Quest Nutrition","QST"],
                        381:["Qunol","QNL"],
                        382:["Rainbow Light","RLT"],
                        383:["RAPIDFIRE","RAP"],
                        384:["Real Health","RHS"],
                        385:["Red Star","RDR"],
                        386:["Redd Remedies","RED"],
                        387:["Rejuvicare","REJ"],
                        388:["Renew Life","REN"],
                        389:["ReserveAge Nutrition","REA"],
                        390:["RidgeCrest Herbals","RDH"],
                        391:["RoC","ROC"],
                        392:["Rohto","RTO"],
                        393:["RSP Nutrition","RSP"],
                        394:["Sambucol","SBL"],
                        395:["Savesta","AYU"],
                        396:["Scandinavian Formulas","SCA"],
                        397:["Schiff","SBF"],
                        398:["Seagate","SGW"],
                        399:["Seeking Health","SKH"],
                        400:["Sierra Bees","MBE"],
                        401:["Sierra Fit","SIE"],
                        402:["Silicium Laboratories","SIL"],
                        403:["Similasan","SIM"],
                        404:["Simply Organic","SOG"],
                        405:["Six Star","SST"],
                        406:["Sky Organics","SYO"],
                        407:["SmartyPants","SMA"],
                        408:["Solumeve","SLM"],
                        409:["Source Naturals","SNS"],
                        410:["Sovereign Silver","SSV"],
                        411:["Spectrum Culinary","SPT"],
                        412:["Spectrum Essentials","SPE"],
                        413:["Sports Research","SRE"],
                        414:["Sprout Living","SPL"],
                        415:["Starwest Botanicals","STR"],
                        416:["Stoneridge Orchards","SRO"],
                        417:["Sufficient C","SFC"],
                        418:["Sun Chlorella","SCC"],
                        419:["Sun Potion","SNN"],
                        420:["Sunbiotics","SBS"],
                        421:["Sundown Naturals","SDN"],
                        422:["Sundown Naturals Kids","SDK"],
                        423:["Sundown Organics","SDO"],
                        424:["Sunfood","SFD"],
                        425:["SunLipid","SLD"],
                        426:["Sunny Green","SNG"],
                        427:["Sunwarrior","SUW"],
                        428:["Super Nutrition","SPN"],
                        429:["Superior Source","SPS"],
                        430:["Swanson","SWV"],
                        431:["Swisse","SWW"],
                        432:["Symbiotics","SYM"],
                        433:["T-RQ","QRT"],
                        434:["T. Taio","TAI"],
                        435:["Tea Tree Therapy","TTT"],
                        436:["Tera's Whey","TEW"],
                        437:["Terra Origin","TEO"],
                        438:["Terry Naturally","EUR"],
                        439:["TheraBreath","THB"],
                        440:["TheraTears","TAR"],
                        441:["Thompson","THO"],
                        442:["Thorne Research","THR"],
                        443:["TPCS","TPC"],
                        444:["Trace Minerals Research","TMR"],
                        445:["Traditional Medicinals","TRA"],
                        446:["Tummydrops","TUM"],
                        447:["Ultamins","ULM"],
                        448:["Umac-Core","UMA"],
                        449:["Universal Nutrition","UNN"],
                        450:["UpSpring","UPG"],
                        451:["Vahdam Teas","VAH"],
                        452:["Vega","VEG"],
                        453:["VeganSmart","VNS"],
                        454:["VegLife","VGL"],
                        455:["Vibrant Health","VBH"],
                        456:["Vitables","VTB"],
                        457:["Vitaburst","VBT"],
                        458:["VitaFusion","VFU"],
                        459:["Vital Earth Minerals","VEM"],
                        460:["Vital Nutrients","VNU"],
                        461:["Vital Proteins","VTP"],
                        462:["Vitality Works","VTW"],
                        463:["Vitamin Bounty","VAB"],
                        464:["Vitamin Friends","VFS"],
                        465:["Vitanica","VTN"],
                        466:["Viteyes","VTE"],
                        467:["Vplab","VPB"],
                        468:["Wedderspoon","WSP"],
                        469:["Whitaker Nutrition","DWH"],
                        470:["Whole World Botanicals","WWB"],
                        471:["Wilderness Poets","WLP"],
                        472:["Wildly Organic","WLO"],
                        473:["Wiley's Finest","WIF"],
                        474:["Williams Nutrition","DWM"],
                        475:["Wobenzym N","ATR"],
                        476:["World Organic","WOR"],
                        477:["Xlear","XLR"],
                        478:["XP Sports","XPS"],
                        479:["Xtend","SCI"],
                        480:["Y.S. Eco Bee Farms","YSO"],
                        481:["Yeouth","YTH"],
                        482:["Yerba Prima","YBP"],
                        483:["Youtheory","YOU"],
                        484:["YumEarth","YUE"],
                        485:["YumV's","YUV"],
                        486:["Zahler","ZAH"],
                        487:["Zand","ZAN"],
                        488:["Zarbee's","ZAR"],
                        489:["Zenwise Health","ZNW"],
                        490:["Zhou Nutrition","ZHO"],
                        491:["Zint","ZNT"],
                        492:["Zipfizz","ZIP"],
                        493:["ZOI Research","ZOI"],
                        },
                'Форма выпуска':{
                    'Капсула':'32372',
                    'Гранула':'32390',
                    'Мягкая капсула':'32400',
                    'Таблетка':'32410',
                    'Вегетераподъязычный ':'32408',
                    'таблетинская капсула':'32413',
                    'Вегетераинская Мягкая капсула':'32414',
                    'Вегетераинская таблетка':'32415',
                    'Консервированный':'32371',
                    'жевательный':'32373',
                    'крем':'32374',
                    'шипучий':'32376',
                    'тягучий':'32382',
                    'жидкость':'32383',
                    'вкладыш':'32384',
                    'лосьон':'32385',
                    'леденец':'32386',
                    'пакет':'32387',
                    'стручок':'32391',
                    'пудра':'32393',
                    'набор':'32398',
                    'спрей':'32403'
                }
            }
        print('\nФильтры:\n 1)Цена\n 2)Бренд \n 3)Рейтинг\n 4)Форма выпуска') # список фильтров

        p1=input('Выберите параметр..Один или больше\nПараметры вводить без пробелов\n')

        url=href #считываем изначальную ссылку

        if len(p1)>=1: 
                print(f'\nВы выбрали {len(p1)} фильтра')
                # globalhoice='Вы выбрали следующие фильтры:\n'
                for i in range(len(p1)): 
                        s=int(p1[i]) 
                        if s==1: #Цена
                                print("Выбреите диапазон цен")
                                for k,v in filters['Цена'].items():
                                        print(k,')',v)
                                choice=int(input('Ваш выбор:\n'))
                                i=1
                                while choice!='':
                                        if i==1:
                                                url=url+f'&ranges={choice}'#добавляем к нашей ссылке
                                                globalchoice.append(f'Цена {i}:{choice}')
                                                print(f'Выбрана цена:{i}:{filters["Цена"][int(choice)]}') 
                                                i+=1
                                        elif i>1:
                                                url=url+f'%2C{choice}'
                                                globalchoice.append(f'Цены {i}:{filters["Цена"][int(choice)]}:')
                                                print(f'Выбрана цена:{i}:{filters["Цена"][int(choice)]}')
                                        print('Хорошо, выберите еще (для прекращения просто нажмите Enter)\n')
                                        # print(f'url={url}')
                                        choice=(input('Ваш выбор:\n'))

                                print('Цены выбраны...\n')
                        elif s==2:#Бренды
                                print("\nВыберите Бренд:\n")
                                for k,v in filters["Бренды"].items(): #выводим список
                                        print(k,')',v[0])
                                try:
                                        choice=int(input('Ваш выбор:\n'))
                                except:
                                        choice=''
                                        print("Вы ничего не выбрали...\n")
                                i=0
                                while choice!='':
                                        i+=1
                                        if i==1:
                                                url=url+f'&bids={filters["Бренды"][int(choice)][1]}'#добавляем к нашей ссылке
                                                globalchoice.append(f'Бренд {i}:{filters["Бренды"][int(choice)][0]}') 
                                        else:
                                                url=url+f'%2C{filters["Бренды"][int(choice)][1]}'
                                                globalchoice.append(f'Бренд {i}:{filters["Бренды"][int(choice)][0]}:')
                                        print('Хорошо, выберите еще (для прекращения просто нажмите Enter)\n')
                                        choice=input('Ваш выбор:\n')
                                print('Бренды выбраны...\n')
                                # print(f'url={url}')                    
                        elif s==3: # рейтинг
                                print("\nВыберите рейтинг\n")
                                rating=int(input("Введите рейтинг от 1 до 5\n"))#выводим список
                                if rating>=1 and rating<=5:
                                        i=0
                                        while rating!='': 
                                                i+=1
                                                if i == 1:
                                                        url=url+f'&ratings={int(rating)}' #добавляем к нашей ссылке
                                                        globalchoice.append(f'Рейтинг:{i}) {int(rating)}')
                                                else:
                                                        url=url+f'%2C{int(rating)}'
                                                        globalchoice.append(f'Рейтинг:{i}) {int(rating)}')
                                                rating=input("Хорошо, выберите еще (для прекращения просто нажмите Enter)\n")
                                else:
                                        print('Надо число от 1 до 5')
                                print('Рейтинг выбран...\n')
                                # print(f'url={url}')
                        elif s==4:#Форма выпуска
                                print("\nВыберите форму выпуска:\n")
                                i=1
                                u=1
                                buff={}
                                for k,v in filters["Форма выпуска"].items(): #выводим список
                                        print(i,')',k)
                                        i+=1
                                        buff[i]=k 
                                choice=int(input('Ваш выбор:\n'))
                                i=0
                                while choice!='':
                                        i+=1
                                        if i==1:
                                                for k,v in buff.items():
                                                        if k==int(choice)+1: # фильтруем Введеное пользователем со значением буферного словаря и сопоставляем с изначальным
                                                                url=url+f'&avids={filters["Форма выпуска"][buff[int(choice)+1]]}'#добавляем к нашей ссылке
                                                                globalchoice.append(f'Формы выпуска:{i}){buff[int(choice)+1]}\n ')
                                        else:  
                                                for k,v in buff.items():
                                                        if k==int(choice)+1: # фильтруем Введеное пользователем со значением буферного словаря и сопоставляем с изначальным
                                                                url=url+f'&avids={filters["Форма выпуска"][buff[int(choice)+1]]}'#добавляем к нашей ссылке
                                                                globalchoice.append(f'Формы выпуска:{i}){buff[int(choice)+1]}\n ')

                                        choice=input('Ваш выбор:\n')
                                print('Формы выпуска выбраны\n')
                                # print(f'url={url}')
                        else:
                                print("Что-то не так....")
        print('\n')
        for c in globalchoice:
                print(c) # выводим список фильтров
        print('\n')
        print(url)         
        return url #возращаем ссылку в изначальную функцию (*)
# Функция фильтрации итогово отчета
def report():
    report={
    1:"name_of_product",
    2:"mark",
    3:"href",
    4:"old_price",
    5:"new_price",
    6:"company",
    7:"amount_of_capsulse",
    8:"amount_of_comments",
    }

    h=input("Выберите параметры НЕ вносимые в отчет:\n 1)Наименование товара\n 2)Рейтинг\n 3)Cсылка\n 4)Цена\n 5)Цена со скидкой\n 6)Компания производитель\n 7)Количество штук в упаковке\n 8)Количество положительных комментариев\nДля окончания ввода, просто нажмите Enter...\n")

    while h!='':
            for k,v in report.items():
                    if int(h)==k:
                        sort_and_del(v)    
            h=input("Хорошо, выберите еще (для прекращения просто нажмите Enter)")
# функция удаления данных из итогово отчета
def sort_and_del(v):
        for elem in range(len(product_data)):
                try:
                        del product_data[elem][v]
                except:
                        pass

if __name__=='__main__':
    main()
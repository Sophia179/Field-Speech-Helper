time_slot ="""        <TIME_SLOT TIME_SLOT_ID="ts%s" TIME_VALUE="%s"/>"""    #два пропуска, где 1 - номер, 2 - временная отметка
annotation = """        <ANNOTATION>
            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a%s"
                TIME_SLOT_REF1="ts%s" TIME_SLOT_REF2="ts%s">
                <ANNOTATION_VALUE>%s</ANNOTATION_VALUE>
            </ALIGNABLE_ANNOTATION>
        </ANNOTATION>"""                        # 4 пропуска, где 1 - айди, 2 - время начала, 3 - время конца, 4 - фраза
type_of_layer = """    <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
        LINGUISTIC_TYPE_ID="utterance" TIME_ALIGNABLE="true"/>
    <LINGUISTIC_TYPE CONSTRAINTS="Time_Subdivision"
        GRAPHIC_REFERENCES="false" LINGUISTIC_TYPE_ID="words" TIME_ALIGNABLE="true"/>"""
word_annotation = """        <ANNOTATION>
            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a%s"
                TIME_SLOT_REF1="ts%s" TIME_SLOT_REF2="ts%s">
                <ANNOTATION_VALUE>%s</ANNOTATION_VALUE>
            </ALIGNABLE_ANNOTATION>
        </ANNOTATION>"""                        # 4 пропуска, где 1 - айди, 2 - время начала, 3 - время конца, 4 - слово

def timer_id(time_list):
    time_id_new=[]
    for times in time_list:
        id=''
        for i in range(len(times)-1):
            id+=times[i]
        time_id_new.append(int(float(id)*1000))
    return(time_id_new)

import json

#читаем джейсонку, создаем списки фраз, слов, временных отметок начала слов и концов фраз
read_file=open('req.json', 'r', encoding='utf-8')
file=json.load(read_file)
count = 0
phrases = list()
words = list()
NYtimes = list()
WWtimes = list()
end_of_frase = list()
WWc = 0
for chunk in file['response']['chunks']:
    count+=1
    if count%2==0:
        phrases.append(chunk['alternatives'][0]['text'])
        NYtimes.append(chunk['alternatives'][0]['words'][0]['startTime'])
        NYtimes.append(chunk['alternatives'][0]['words'][-1]['endTime'])
        WWc+=len(chunk['alternatives'][0]['words'])+1
        for i in range(len(chunk['alternatives'][0]['words'])):
            WWtimes.append(chunk['alternatives'][0]['words'][i]['startTime'])
            words.append(chunk['alternatives'][0]['words'][i]['word'])
        WWtimes.append(chunk['alternatives'][0]['words'][-1]['endTime'])
        end_of_frase.append(WWc)
slot_id_new = timer_id(NYtimes)     #что это
word_times = timer_id(WWtimes)
read_file.close()

#принимаем пустой еаф пользователя (только слой дефолт), переписываем построчно, добавляем временные слоты, аннотацию фраз, слов, присваиваем слоям свойства аттеранс и вордс, связываем слои
name_of_file = input("Введите имя вашего файла. Например, name.eaf  : " )
new_name_of_file = input("Введите имя желанного файла. Например, new_name.eaf  : " )
f = open(name_of_file, 'r', encoding='utf-8')
new_f = open(new_name_of_file, 'w', encoding='utf-8')
for line in f:
    if "<TIME_ORDER/>" in line:
        new_line = "    <TIME_ORDER>"
        print(new_line, file = new_f)
        count_of_time_slot = 1
        for time in word_times:
            time_line = time_slot % (count_of_time_slot, time)
            print(time_line, file = new_f)
            count_of_time_slot += 1
        print("    </TIME_ORDER>", file = new_f)
    if "<TIER" in line and "/>" in line:
        new_line = '    <TIER LINGUISTIC_TYPE_REF="utterance" TIER_ID="frase">'
        print(new_line, file = new_f)
        count_of_frase = 0
        count_of_start = 0
        count_of_annotation = 1
        for frase in phrases:
            if count_of_frase == 0:
                count_of_frase += 1
                start = 1
            else:
                start = int(end) + 1
            end = end_of_frase[count_of_start]
            annotation_line = annotation % (count_of_annotation, start, end, frase)
            print(annotation_line, file = new_f)
            count_of_annotation += 1
            count_of_start += 1
        print("    </TIER>", file = new_f)
        new_line = '    <TIER LINGUISTIC_TYPE_REF="words" PARENT_REF="frase" TIER_ID="word">'
        print(new_line, file = new_f)
        start = 0
        count_end_of_frase = 0
        for word in words:
            start += 1
            if start == end_of_frase[count_end_of_frase]:
                start += 1
                count_end_of_frase += 1
            end = start + 1
            annotation_line = word_annotation % (count_of_annotation, start, end, word)
            print(annotation_line, file = new_f)
            count_of_annotation += 1
        print("    </TIER>", file = new_f)
    if 'LINGUISTIC_TYPE_ID="default-lt"' in line:
        print(line.strip('\n'), file = new_f)
        print(type_of_layer, file = new_f)
    else:
        print(line.strip('\n'), file = new_f)

f.close()
new_f.close()

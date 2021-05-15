print("Добро пожаловать!")

#обрезка файла и перевод в огг
import os

way_to_ffmpeg = input("Введите путь к ffmpeg.exe: ")
way_to_audio = input("Введите путь к аудиофайлу в формате wav: ")
beginning_time = input("Введите время, с которого начать распознавание (в секундах): ")
ending_time = input("Введите время, на котором закончить распознавание (в секундах): ")
way_to_ogg = input("Введите путь к opusenc.exe: ")
total_time = int(ending_time) - int(beginning_time)

shortening = '%s -ss %s -t %s -i %s new.wav' % (way_to_ffmpeg, beginning_time, total_time, way_to_audio)
wav2ogg = '%s new.wav audio.ogg' % (way_to_ogg)

os.system(shortening)
os.system(wav2ogg)

import boto3

AUDIO_FNAME = r"audio.ogg"

session = boto3.session.Session()
s3 = session.client(
    service_name='s3',
    endpoint_url='https://storage.yandexcloud.net'
)

bucket_name = 'field-asr-bucket'
file_key = AUDIO_FNAME

# Загрузить объекты в бакет
s3.upload_file(AUDIO_FNAME, 
               bucket_name, 
               file_key)

#for key in s3.list_objects(Bucket=bucket_name)['Contents']:
 #   print(key)

import requests
import time
import json


# Укажите ваш API-ключ и ссылку на аудиофайл в Object Storage.
key = 'AQVNw6ushYn73WIVZtDqI97BNTyxYtwkTniz_7qP'
filelink = f"https://storage.yandexcloud.net/field-asr-bucket/{file_key}"
POST = "https://transcribe.api.cloud.yandex.net/speech/stt/v2/longRunningRecognize"

body ={
    "config": {
        "specification": {
            "languageCode": "ru-RU"
        }
    },
    "audio": {
        "uri": filelink
    }
}

# Если вы хотите использовать IAM-токен для аутентификации, замените Api-Key на Bearer.
header = {'Authorization': 'Api-Key {}'.format(key)}

# Отправить запрос на распознавание.
req = requests.post(POST, headers=header, json=body)
data = req.json()

id = data['id']

# Запрашивать на сервере статус операции, пока распознавание не будет завершено.
while True:
    GET = "https://operation.api.cloud.yandex.net/operations/{id}"
    req = requests.get(GET.format(id=id), headers=header)
    req = req.json()

    if req['done']:
        break
    print("Not ready")
    time.sleep(1)

# Показать полный ответ сервера в формате JSON.
#print("Response:")
#print(json.dumps(req, ensure_ascii=False, indent=2))

# Показать только текст из результатов распознавания.
#print("Text chunks:")
#for chunk in req['response']['chunks']:
 #   print(chunk['alternatives'][0]['text'])

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
    time_id_new = []
    for times in time_list:
        _id = ''
        for i in range(len(times)-1):
            _id += times[i]
        time_id_new.append(int(float(_id)*1000) + beginning_time)
    return(time_id_new)

#читаем джейсонку, создаем списки фраз, слов, временных отметок начала слов и концов фраз
count = 0
phrases = list()
words = list()
NYtimes = list()
WWtimes = list()
end_of_frase = list()
WWc = 0
for chunk in req['response']['chunks']:
    count += 1
    if count%2 == 0:
        if len(chunk['alternatives']) == 1:
            phrases.append(chunk['alternatives'][0]['text'])
            NYtimes.append(chunk['alternatives'][0]['words'][0]['startTime'])
            NYtimes.append(chunk['alternatives'][0]['words'][-1]['endTime'])
            WWc += len(chunk['alternatives'][0]['words'])+1
            for i in range(len(chunk['alternatives'][0]['words'])):
                WWtimes.append(chunk['alternatives'][0]['words'][i]['startTime'])
                words.append(chunk['alternatives'][0]['words'][i]['word'])
            WWtimes.append(chunk['alternatives'][0]['words'][-1]['endTime'])
            end_of_frase.append(WWc)
slot_id_new = timer_id(NYtimes)
word_times = timer_id(WWtimes)

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

print("Бегите смотреть ваш идеальный файлик! Спасибо, что воспользовались FiSH!")

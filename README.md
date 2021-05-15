# Field-Speech-Helper (FiSH)
Главная задача FiSH - помогать полевым лингвистам размечать аудиозаписи в программе ELAN.
## Как работает FiSH:
  1. Принимает аудиофайл в формате `wav`.
  2. Обрезает аудиофайл по заданным временным рамкам и переводит в формат `ogg`.
  3. Отправляет преобразованный аудиофайл на сервер Яндекса (Yandex SpeechKit), где проходит распознавание речи.
  4. Принимает ответ от SpeechKit в формате `json`.
  5. Заносит разметку в eaf файл пользователя.

В результате работы программы в eaf-файле пользователя появятся слой `frase` с типом слоя `utterance`, в котором будут размечены все фразы говорящего, и слой `word` с типом слоя `words` и родительским слоем `frase`, где будут размечены все слова из данных фраз.

## Что нужно для работы программы:
  1. В пользователях должна быть создана папка `.aws`, в которой находятся два файла: `credentials` и `config` (без расширения). В файле `credentials` должен находиться следующий текст:
  `[default]
  aws_access_key_id=SelVOMYDovEilk20CWIs
  aws_secret_access_key=SrzK1VdRwekmSmLI2lGR9HDh-ibulV_tJ4GBEkGf`
 В файле `config` должен находиться следующий текст:
  `[default]
  region=ru-central1`
  2. У пользователя должны быть установлены `ffmpeg` (для обрезки аудио) и `vorbis-tools` (для перевода аудио в формат `ogg`).
  3. У пользователя должен быть создан файл в ELAN данным аудио. Это должен быть пустой файл со слоем `default` (то есть только что созданный новый файл, любые правки (в том числе удаление слоя `default` или внесение какой-либо разметки) могут помешать работе программы).

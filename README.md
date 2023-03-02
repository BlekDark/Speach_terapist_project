создание виртуального окружения:
    /// в cmd
    python -m venv venv
    venv\Scripts\activate.bat - для Windows;
    source venv/bin/activate - для Linux и MacOS.
    
Работа с google sheats
    поставить пакет 
        pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

Необходимые библиотеки:
    python-dotenv, 
    PyMySQL, 
    gspread,
    pyTelegramBotAPI,
    pip install cryptography


    pip install cryptography pyTelegramBotAPI gspread PyMySQL python-dotenv

    
    ссылка на бота: speech_therapist_test


Для создания своего бота:
    написать https://t.me/BotFather:
        команду /newbot 
        после чего ввести имя бота котрое будет отображаться пользователям
        после чего ввести адрес бота на латинице, который будет оканчиваться на bot (например logoped_bot)
    ботфазер отправит ссылку на бота и токен
    токен необходимо вставить в .env TOKEN='<ваш токен>' заменяя старый токен

Для генерации токена необходимо
    файл gettoken.py запустить локально в виртуальном окрыжении поставив библиотеки
    pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
    перед запуском рядом положить файл credentials_drive.json который берется из гугловской 
    после запуска даем доступы которые просит гугл и копируем получившийся файл token.json и файл credentials_drive.json в папку с проектом на сервере


Для получения кредов из гугла
    Перейти на сайт: https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com
    авторизироваться, next, eneble
    в левом меню APIs & Services -> Credentials
    Create credentials -> OAuth clieny id
    Application type выбираешь Web application
    Опционально: выбираешь External если есть такой вариант 
    Опционально: Заполяешь обязательные поля и майл указывваешь тот что будет использоваться для работы с гугл таблицами и документами (то есть тот с которого и авторизовался)
    Application type ставим Desktop app, имя любое, create
    В появившеся окне скачиваем и сохраняем в проект как credentials_drive.json
    Переходим в Library и ставим Google Drive Api и Google Sheets Api

    Если пишет что нет доступа то надо прописать свой емаил как тест юзера

Для запуска на сервере
    Копируешь код в папку на сервере
    Разворачиваешь виртуальное окружени и устанавливаешь библиотеки
    для запуска в фоне использовать
    nohup python3 main.py &


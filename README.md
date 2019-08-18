# Задание в школу бэкенд разработки Яндекса

Выполнил: Сережа Уфимцев

## Запуск проекта

Для разработки воспользуйтесь следующей командой

```$ docker-compose up```

### Создание базы данных
Для создания базы данных воспользуйтесь следующей командой

```$ docker-compose exec web python init_db.py```


## Запуск Тестов
Для запуска тестов в при поднятом контейнере воспользуйтесь следующей командой

```$ docker-compose exec web pytest```

# Деплой
После клонирования репозитория выполните команду `$ pipenv install --system --deploy`

Незабудьте так же указать в конфигурационных файлах информацию для соединения с postgersql

Сначала установите nginx, postgresql и supervisor

`$ apt install nginx`

`$ apt-get install postgresql-10`

`$ apt-get install supervisor`

В файле init_db укажите актуальную информацию для коннекта к базе, затем создайте схему базы данных `$ python3 init_db.py`

Если база уже создана, вы так же можете изменить порядок вызова методов, и вместо создания базы с нуля, просто создать схему таблиц

После по адресу `/ect/nginx/sites-avaliable/`
создайте файл `api.conf` затем добавьте в него следующий код

``` upstream aiohttp {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # Unix domain servers
    server unix:/tmp/api_1.sock fail_timeout=0;
    server unix:/tmp/api_2.sock fail_timeout=0;
    server unix:/tmp/api_3.sock fail_timeout=0;
    server unix:/tmp/api_4.sock fail_timeout=0;
    server unix:/tmp/api_5.sock fail_timeout=0;
    server unix:/tmp/api_6.sock fail_timeout=0;
    server unix:/tmp/api_7.sock fail_timeout=0;
    server unix:/tmp/api_8.sock fail_timeout=0;
  }
  server {
    listen 0.0.0.0:8080;
    client_max_body_size 4G;

    server_name default;

    location / {
      proxy_set_header Host $http_host;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_redirect off;
      proxy_buffering off;
      proxy_pass http://aiohttp;
    }
  }
```
Или вы можете скопировать пример конфига из папки deploy `$ copy ./deploy/api.conf /etc/nginx/sites-avaliable/api.conf`
 
Затем создайте ссылку на файл конфига в директории sites-enabled `$ ln -s /etc/nginx/sites-available/api.conf /etc/nginx/sites-enabled/api.conf`

Далее проверьте конфиг командой `$ nginx -t` Если все хорошо, то перезапустите nginx `nginx -s reload`

Затем создайте конфиг supervisor в директории `$ /etc/supervisor/conf.d/aiohttp.conf`
```
[program:aiohttp]
numprocs = 8 ;По количеству ядер в системе
numprocs_start = 1
process_name = api_%(process_num)s

; Unix socket paths are specified by command line.
command=python3 /var/www/yandex_backend/app.py --path=/tmp/api_%(process_num)s.sock

; We can just as easily pass TCP port numbers:
; command=/path/to/aiohttp_example.py --port=808%(process_num)s
chmod=0700                 ; socket file mode (default 0700)
user=nobody
autostart=true
autorestart=true
``` 
Из директории deploy можно так же скопировать конфиг `$ copy ./deploy/aiohttp.conf /etc/supervisor/conf.d/aiohttp.conf`

Затем запустите supervisor `$ supervisorctl start all`

Теперь ваше приложение готово к боевым нагрузкам)))

# Чего удалось добиться
1) Весь код по pep8 (flake8 не ругается)
2) Использован фреймворк aiohttp и aiopg, все быстро как ракета
3) Это мой первый проект с использованием такого стека
4) Написал тесты через pytest
5) Безмерно горжусь собой)
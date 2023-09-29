# vk-download
Экспорт фотографий, видео, друзей и друзей друзей из ВКонтакте

## Зачем?
VK предоставляеть [экспорт данных](https://vk.com/data_protection?section=rules#archive), который не позволяет скачать фото, видео и информацию о друзьях.

## Как получить Token?
1. Создайте Standalone приложение: https://vk.com/apps?act=manage
2. Получите его ID: на [странице приложений](https://vk.com/apps?act=manage) нажмите на кнопку "Редактировать" и в адресной строке появится ссылка с ID вида https://vk.com/editapp?id=51756670
3. Сформируйте ссылку из [Implict Flow](https://vk.com/dev/implicit_flow_user):  
https://oauth.vk.com/authorize?client_id=51756670&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=friends,photos,video&response_type=token&v=5.131&state=123456  
где client_id - ID вашего приложения из п.2,  
scope - [права доступа](https://dev.vk.com/ru/reference/access-rights) через запятую  
v - [последняя версия VK API](https://dev.vk.com/ru/reference/versions)  
4. Перейдите по ссылке и в адресной строке вы получите access_token вида:  
vk1.a.J2L5cqOgD9v4lB5mkt7_LciAIFKr7yMSu518U2NRzWXuhI9KklhL1ZR_0bSDpBgsVVbj3qfJErsdUH6ziGeZi6Fk

## Как получить remixnsid и remixsid для скачивания видео?
1. Авторизоваться в VK
2. Открыть панель разработчика: Настройка → Дополнительные инструменты → Инструменты разработчика или F12.
3. Открыть вкладку Приложение, слева в меню Хранилище → Файлы cookie → https://vk.com
4. Кликните на remixnsid и remixsid и скопируйте значения.

## Инструменты
./photos.py TOKEN [UID]  
— Скачивает фотографии в наилучшем разрешении из всех альбомов, включая служебные, сохраняя в соответствующие папки.  

./friends.py TOKEN UID [DEPTH=1]  
— Сохраняет профиль, аватар и друзей пользователя. Параметр DEPTH позволяет сохранять друзей друзей.

./video.py TOKEN remixnsid remixsid [UID]  
— Скачивает видео в наилучшем разрешении из всех альбомов, включая служебные, сохраняя в соответствующие папки.  

## Disclaimer
Написано в стиле KISS с целью «один раз запустил и забыл» в качестве простого скрипта без зависимостей без цели превращения в полноценный продукт.

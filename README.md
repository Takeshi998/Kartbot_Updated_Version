# kartbot

Bot de Discord para el servidor SRB2Kart-Brasil.

## Dependencias

- Python 3.8+ (+ `discord.py`,` psutil`,`datetime `,`asyncio `,`requests,`,`requests`,`pathlib`)
- `screen`
- `cosas`

## Uso

- Copie el archivo `kartbot_config.template.json` en` kartbot_config.json` y establezca los valores apropiados
- Inicie el servidor usando `screen -dmS server / path / do / srb2kart -dedicated &`
- Ejecute `python3.8 kartbot.py`

## Ajustes

- `prefix` - Prefijo utilizado para los comandos de bot
- `description` - Descripción del bot que aparece en el comando de ayuda
- `token` - Token de bot


- `screen_name` - Nombre de la` pantalla` del servidor
- `server_folder_path` - Ruta de la carpeta del servidor ** con una barra inclinada (/) al final **
- `server_executable_name` - Nombre del archivo ejecutable del servidor
- `server_executable_args` - Argumentos pasados ​​al servidor (deje ` -dedicated`)
- `server_max_players` - Número máximo de jugadores en el servidor (no influye en la funcionalidad del bot, solo se muestra en` k! info`)
- `ip_message` - Mensaje que se mostrará en` k! ip`
- `allow_error_message` - Mensaje que se mostrará en` k! race` y `k! battle` cuando el usuario no tenga el rol requerido
- `helper_roles` - Lista de roles que tienen permiso para [comandos de ayuda] (# ayudante)
- `admin_roles` - Lista de roles permitidos para [comandos de administrador] (# admin)


- `enable_dkartconfig_corruption_workaround` - Cuando está habilitado, el bot copia el archivo en` backup_dkartconfig_path` a `dkartconfig_path` cuando se usa` k! restart`, para evitar la corrupción del archivo
- `backup_dkartconfig_path` - Leer arriba
- `dkartconfig_path` - Leer arriba

## Comandos

- `k! help` - Muestra una lista de comandos
- `k! ip` - Envía la IP del servidor
- `k! status | info | players` - Envía información sobre el servidor y los jugadores conectados

### Ayudante

- `k! race` - Cambia el modo de juego a carrera
- `k! battle` - Cambia el modo de juego a batalla

### Admin

- `k! restart` - Reinicia el servidor
- `k! command | command <command>` - Ejecuta un comando

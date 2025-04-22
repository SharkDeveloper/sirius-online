#from .db.models import Device, Configs, States, Events


async def device_ws_handler(message: dict, session: str):
    method = message["method"]
    match method:
        case "/ping":
            return {"method": "ping", "session": session}
        case "/login":
            print("login")
            session = message["data0"]["session"]
            #TODO проверка аторизации, логин и пароль добавить в бд
        case "/state/zone/overall":
            #{"method":"/state/zone/overall","session":"737c284be44a2daa3a92375683c9bc5"}
            pass
        case _:
            print("unknown method: ", method)
        

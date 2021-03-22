from CODE.OBJECTS import FUNCTION, INSTANCE
from CODE.METHODS import EXECUTION_CONTROL
from sympy import latex
import os
import json
import asyncio
import websockets

class Main():

    @classmethod    
    def run(cls):
        cls.connected = []
        cls.port = int(os.environ.get("PORT", 5000))
        cls.start_server = websockets.serve(cls.server, "0.0.0.0", cls.port)
        cls.loop = asyncio.get_event_loop()
        cls.loop.run_until_complete(cls.start_server)
        cls.loop.run_forever()
    
    @classmethod
    async def server(cls, websocket, path):
        cls.connected.append(websocket)
        try:
            async for message in websocket:
                message = json.loads(message)
                for conn in cls.connected:
                    if conn == websocket:
                        await conn.send(await cls.call_tasks(conn, message))
        finally:
            cls.connected.remove(websocket)
    
    @classmethod
    async def call_tasks(cls, conn, string):
        task = getattr(cls, string['task'])
        if string['params'] == 'None':
            return json.dumps(await task(conn))
        return json.dumps(await task(conn, string['params']))

    @classmethod
    def find_function_by_id(cls, id):
        data = json.loads(open("./CODE/JSON/functions-details.json", 'r').read())
        for i in data['data']:
            if id == i['id']:
                function_selected_object = FUNCTION.Function()
                function_selected_object.build_function(i)
                return i, function_selected_object
        raise Exception("Index out of bounds")

    @classmethod
    async def functions_names(cls, conn):
        return json.loads(open("./CODE/JSON/functions-names.json", 'r').read())

    @classmethod
    async def functions_details(cls, conn, params):
        try:
            i, _ = Main.find_function_by_id(int(params['function_id']))
            return i
        except:
            return "<h1>NOT FOUND</h1>"

    @classmethod
    async def functions_details_img(cls, conn, params):
        try:
            i, obj = Main.find_function_by_id(int(params['function_id']))
            return { 'id': i['id'], 'img': ('http://latex.codecogs.com/svg.latex?'+obj.get_format_expression()).replace(' ','')}    
        except:
            return "<h1>NOT FOUND</h1>"

    @classmethod
    async def functions_methods(cls, conn):
        return json.loads(open(os.path.dirname(__file__) + "./CODE/JSON/functions-methods.json", 'r').read())

    @classmethod
    async def functions_solver(cls, conn, params):
        isHybrid = bool(params['isHybrid'])
        _, function_obj = cls.find_function_by_id(int(params['function_id']))
        function_obj.set_n_dimension(int(params['dimension']))
        await conn.send('Stars a new execution to - '+str(conn))
        return json.dumps(await cls.loop.run_in_executor(None, EXECUTION_CONTROL.execute_control, function_obj, isHybrid, params))

if __name__ == "__main__":
    Main().run()
    
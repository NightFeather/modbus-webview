from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from random import randint

connections = {}

class ModbusPoller(AsyncJsonWebsocketConsumer):
  async def connect(self):
    await self.accept()

  async def disconnect(self):
    pass

  async def receive_json(self, data):
    if any([ k not in data for k in ['host', 'action'] ]):
      await self.send_json({'result': 'error', 'data': {'mesg': 'missing argument'}})
      return

    host = data['host']
    port = 502
    if ':' in data['host']:
      host, port = data['host'].split(':')
      port = int(port)

    connkey = '{}:{}'.format(host, port)
  
    if data['action'] == 'open':
      if connkey not in connections:
        cli = ModbusTcpClient(host, port)
        try:
          cli.connect()
          connections[connkey] = cli
        except ConnectionException:
          await self.send_json({
            'result': 'error',
            'data': {
              'mesg': 'invalid host',
              'host': data['host']
            }
          })
          return

      await self.send_json({
        'result': 'open',
        'data': {
          'host': data['host']
        }
      })
      return

    if any([ k not in data for k in ['type', 'addr', 'size']]):
      await self.send_json({'result': 'error', 'data': {'mesg': 'missing argument'}})
      return

    cli: ModbusTcpClient = connections[connkey]
    if data['action'] == 'read':
      if data['type'] == 'coil':
        resp = cli.read_coils(data['addr'], data['size'])
        if not resp.isError():
          await self.send_json({
            'result': 'read',
            'data': {
              'host': data['host'],
              'data': resp.bits[:data['size']],
              'type': 'coil'
            }
          })
          return
      elif data['type'] == 'discrete':
        resp = cli.read_discrete_inputs(data['addr'], data['size'])
        if not resp.isError():
          await self.send_json({
            'result': 'read',
            'data': {
              'host': data['host'],
              'data': resp.bits[:data['size']],
              'type': 'discrete'
            }
          })
          return
      elif data['type'] == 'inputs':
        resp = cli.read_input_registers(data['addr'], data['size'])
        if not resp.isError():
          await self.send_json({
            'result': 'read',
            'data': {
              'host': data['host'],
              'data': resp.registers[:data['size']],
              'type': 'inputs'
            }
          })
          return
      elif data['type'] == 'holding':
        resp = cli.read_holding_registers(data['addr'], data['size'])
        if not resp.isError():
          await self.send_json({
            'result': 'read',
            'data': {
              'host': data['host'],
              'data': resp.registers[:data['size']],
              'type': 'holding'
            }
          })
          return
      else:
        await self.send_json({
          'result': 'error',
          'data': {
            'mesg': 'invalid type',
            'host': data['host']
          }
        })
        return

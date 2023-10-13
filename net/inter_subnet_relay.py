

class EchoServerProtocol(asyncio.Protocol):
    def __init__(self, ip:int, port:int, solution):
        self.ip = ip
        self.port = port
        self.solution = solution

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log('Connection from {}'.format(peername))
        # solution.reset_epoch_signals()
        self.transport = transport

    @staticmethod
    def input_dict_factory():
        return {
            "rtt_ms": None,  # delay
            "inter_packet_delay_ms": None,  # delay_jit
            "loss_rate":None,  # loss
            "recv_throughput_bps": None,  # throughput
            "last_final_estimation_rate_bps": None  # action_history
        }

    @staticmethod
    def parse_message(message):
        now = datetime.datetime.now()
        # log('recved!')
        try: 
            message = message.decode()
            # tc reporting
            if message.startswith('tc:'):
                # log('[{}] TC REPORT: {}'.format(now, message))
                # raw_data = re.findall(r'tc:(.*):tc',message)[0].split(',')
                raw_data = re.findall(r'tc:(.*?):tc',message)[-1].split(',')
                data = {
                    'bandwidth': float(raw_data[0]),
                    'rtt': float(raw_data[1]),
                    'loss': float(raw_data[2])
                }
                return 'tc', data
            # stat reporting
            elif message.startswith('stat:'):
                # log('[{}] TC REPORT: {}'.format(now, message))
                # raw_data = re.findall(r'tc:(.*):tc',message)[0].split(',')
                # print(message)
                raw_data = re.findall(r'stat:(.*?):stat',message)[-1]
                timestamp, data = parse_recv_stat(raw_data)
                data = {
                    'timestamp': timestamp,
                    'data': data,
                }
                # print('received stat')
                return 'stat', data
            else:
                # log('[{}] Query MESSAGE: {}'.format(now, message))
                mes_list = message.split("aaa")
                if mes_list[1] != '': #有多个json对象
                    raw_data = mes_list[-2]
                else:
                    raw_data = mes_list[0]
                # log("mes_list[1]: {}, \nself.message: {}.".format(mes_list[1], self.message))
                try:
                    data = json.loads(raw_data)
                except:
                    log("ERROR! json recv: {} \n message:{}".format(raw_data, message))
                    return None
                return 'query', data
        except ValueError as e:
            log('Unkown error occured processing message:')
            log(message)
            raise e

    def data_received(self, data):
        global TIMES, stat_cache
        # print(data)
        try: 
            # parse massage
            type, data = self.parse_message(data)
            now = datetime.datetime.now()
            # process
            if type == 'query':
                """extract data"""
                # for key in self._input_dict.keys():
                #     self._input_dict[key] = self.recv_dict[key]
                input_dict = self.input_dict_factory()
                for key in data.keys():
                    input_dict[key] = data[key]
                # add stat to input_dict
                input_dict['stat'] = stat_cache
                """record times"""
                cur_time = data['get_rl_input_time_ms'] / 1000.0
                TIMES['client'] = cur_time
                local_time = time()
                TIMES['local'] = local_time
                if 'client_init' not in TIMES.keys():
                    TIMES['client_init'] = cur_time
                """inference"""
                res_dic = self.solution.cc_trigger(None, cur_time-TIMES['client_init'], input_dict)
                # log("data to send:{}".format(json.dumps(res_dic)))
                self.transport.write(json.dumps(res_dic).encode())
                log('[{}][{}] Query MESSAGE: {}'.format(now, cur_time-TIMES['client_init'], input_dict))
            elif type == 'stat':
                stat_cache = data
                log('[{}] STAT REPORT'.format(now))
            elif type == 'tc':
                # write bandwidth
                if TIMES: # idle untill time system is available
                    now_client_time = TIMES['client'] + time() - TIMES['local']
                    log('bandwidth: {} Mbps'.format(data['bandwidth']/1e3))
                    self.solution.writer.add_scalars('status', {'bandwidth': data['bandwidth']*1e3}, (now_client_time-TIMES['client_init'])*1e3)
                    log('[{}] TC REPORT: {} kbps'.format(now, data['bandwidth']))

        except Exception as e:
            log('ERROR: {}'.format(str(e)))
            log(str(traceback.format_exc()))

# def exit(sign_name):
#     log(f"获取信号{sign_name}: exit")
#     asyncio.get_running_loop().stop()

async def loop_py3_7_plus(ip, port, solution):
    """
    ref: https://docs.python.org/3.7/library/asyncio-protocol.html#tcp-echo-server
    """
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop_socket = asyncio.get_running_loop()
    server = await loop_socket.create_server(
        protocol_factory=lambda: EchoServerProtocol(ip, port, solution), #返回EchoServerProtocol()对象
        host=ip, port=port, family=socket.AF_UNSPEC)
    log("Waiting for connection... Server IP: {}, PORT: {}".format(ip, port))

    # for sig_name in ('SIGINT', 'SIGTERM'):
    #     loop_socket.add_signal_handler(getattr(signal, sig_name),
    #                             functools.partial(exit, sig_name))
    
    async with server:
        await server.serve_forever()
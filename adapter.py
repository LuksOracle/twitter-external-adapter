from bridge import Bridge
import os

class Adapter:
#    base_url = "https://api.twitter.com/2/users/1018093644/tweets?max_results=5"
#    from_params = ['base', 'from', 'coin']
#    to_params = ['quote', 'to', 'market']

    def __init__(self, input):
        self.id = input.get('id', '1')

        self.request_data = input.get('data')
        if self.validate_request_data():
            self.bridge = Bridge()
            self.set_params()
            self.create_request()
        else:
            self.result_error('No data provided')

    def validate_request_data(self):
        if self.request_data is None:
            return False
        if self.request_data == {}:
            return False
        print(self.request_data)
        return True
        

    def set_params(self):
        self.twitter_id = int(self.request_data.get("twitter_id"))
        self.address_owner = self.request_data.get("address_owner")
        # for param in self.from_params:
        #     self.from_param = self.request_data.get(param)
        #     if self.from_param is not None:
        #         break
        # for param in self.to_params:
        #     self.to_param = self.request_data.get(param)
        #     if self.to_param is not None:
        #         break

    def create_request(self):
        try:
            params = {
                'id' : self.twitter_id
            }

            headers = {
                "Authorization": "Bearer " + os.environ.get('BEARER_TOKEN')
                }
            
            print('pepe')
            # twitter api
            base_url = 'https://api.twitter.com/2/users/{}/tweets?max_results=5'.format(params['id']) 
            print('pepe')
            
            response = self.bridge.request(base_url, headers=headers)

            # response from external api
            data = response.json()
            # parse response data
            address_owner = data["data"][0]["text"].split(' ')[5]
            
            if (address_owner.strip().lower() == self.address_owner.strip().lower()):
                
                # bitwise operator to fit twitter_id + address in same res
                twitter_id_res =  int(self.twitter_id)<<160
                
                #address coming from twitter
                address_res = int(address_owner,16)
                result_unpadded = str(hex(address_res+twitter_id_res))
                
                # pad for hex for chainlink node
                print(result_unpadded)
                pad = '0' * ( 66 - len(result_unpadded))
                address_res_b = '0x' + pad + str(hex(address_res+twitter_id_res))[2:]
                
                self.result = address_res_b # address_res
            else:
                self.result = 0

            self.result_success(self.result)
        except Exception as e:
            self.result_error(e)
        finally:
            self.bridge.close()

    def result_success(self, data):
        self.result = {
            'jobRunID': self.id,
            'data': data,
            'result': self.result,
            'statusCode': 200,
        }

    def result_error(self, error):
        self.result = {
            'jobRunID': self.id,
            'status': 'errored',
            'error': f'There was an error: {error}',
            'statusCode': 500,
        }

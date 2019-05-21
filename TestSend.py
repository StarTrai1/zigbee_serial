from ZigBeeNode import ZigBeeNode
import time

if __name__ == '__main__':
    try:
        zigbee = ZigBeeNode()
        data = '123'
        for i in range(1,100):
            zigbee.hex_broadcastSend(data, '02')
            print("send out")
            time.sleep(0.1)
    except KeyboardInterrupt as e:
        print("Ctrl+C End")
    except Exception as e1:
        print(e1)
    finally:
        zigbee.finish()

from ZigBeeNode import ZigBeeNode

if __name__ == '__main__':
    try:
        zigbee = ZigBeeNode()
        while True:
            print(zigbee.hex_receive())
    except KeyboardInterrupt as e:
        print("Ctrl+C End")
    except Exception as e1:
        print(e1)
    finally:
        zigbee.finish()

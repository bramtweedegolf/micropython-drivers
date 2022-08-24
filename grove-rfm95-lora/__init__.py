import pl_serial
import ll_rfm9x

def getLL():
  pl = pl_serial.Serial()
  ll = ll_rfm9x.LinkLayer(pl)

  if ll.setOpModeSleep(True, True):
    ll.setFiFo()
    ll.setOpModeIdle()
    ll.setModemConfig()
    ll.setPreambleLength(8)
    ll.setFrequency(868)
    ll.setTxPower(23, True)
  else:
    print('Could not set op sleep mode')

  return ll

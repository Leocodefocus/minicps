
"""
SWaT plc5 subprocess 1 simulation
"""
import sqlite3
import os
import time

from constants import logger
from constants import P1_PLC5_TAGS
from constants import read_single_statedb, update_statedb
from constants import write_cpppo, read_cpppo, init_cpppo_server
from constants import L1_PLCS_IP
from constants import T_PLC_R, T_PLC_W, TIMEOUT
from constants import PLC5_CPPPO_CACHE


if __name__ == '__main__':
    """
    Init cpppo enip server.

    Execute an infinite routine loop:
        - read flow level sensors #2
        - update interal enip sensor
    """

    # init the ENIP server
    tags = []
    tags.extend(P1_PLC5_TAGS)
    # tags.extend(P2_PLC2_TAGS)
    time.sleep(1)
    init_cpppo_server(tags)

    # wait for the other plcs
    time.sleep(2)
    
    # write_cpppo(L1_PLCS_IP['plc2'], 'DO_MV_201_CLOSE', '2')

    # val = read_cpppo(L1_PLCS_IP['plc2'], 'DO_MV_201_CLOSE', 'examples/swat/plc2_cpppo.cache')
    # logger.debug("read_cpppo: %s" % val)

    # synch with plc2, plc3
    # time.sleep(1)

    # look a Stridhar graph
    logger.info("PLC5 - enters main loop")
    start_time = time.time()

    write_cpppo(L1_PLCS_IP['plc5'], 'HMI_MV501-Status', '2')

    while(time.time() - start_time < TIMEOUT):
        # cmd = read_single_statedb('AI_FIT_101_FLOW', '1')

        fit501pv = read_single_statedb('5', 'AI_FIT_501_FLOW')[3]

        write_cpppo(L1_PLCS_IP['plc5'], 'HMI_FIT501-Pv', fit501pv)
        val = read_cpppo(L1_PLCS_IP['plc5'], 'HMI_FIT501-Pv', PLC5_CPPPO_CACHE)
        logger.debug("PLC5 - read_cpppo HMI_FIT501-Pv: %s" % val)

        time.sleep(T_PLC_R)
    logger.info("PLC5 - exits main loop")

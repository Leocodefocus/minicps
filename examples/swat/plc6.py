"""
SWaT plc6 subprocess 1 simulation
"""
import time

from constants import logger
from constants import P1_PLC6_TAGS, LIT_101, LIT_301, FIT_201,LIT_601
from constants import read_single_statedb, update_statedb
from constants import write_cpppo, read_cpppo, init_cpppo_server
from constants import L1_PLCS_IP
from constants import T_PLC_R, T_PLC_W, TIMEOUT
from constants import LIT_101, LIT_301, FIT_201, PLC6_CPPPO_CACHE

if __name__ == '__main__':
    """
    Init cpppo enip server.

    Execute an infinite routine loop:
        - read sensors value
        - drive actuators according to the control strategy
        - update its enip server
    """

    # init the ENIP server
    tags = []
    tags.extend(P1_PLC6_TAGS)
    init_cpppo_server(tags)

    # init ENIP server tag values (taken from state_db)
    p601_str = read_single_statedb('6', 'DO_P_601_START')[3]
    if p601_str == '1':
        write_cpppo(L1_PLCS_IP['plc6'], 'HMI_P601-Status', '2')
    else:
        write_cpppo(L1_PLCS_IP['plc6'], 'HMI_P601-Status', '1')

    mv501_str = read_single_statedb('5', 'DO_MV_501_OPEN')[3]
    if mv501_str == '1':
        write_cpppo(L1_PLCS_IP['plc6'], 'HMI_MV501-Status', '2')
    else:
        write_cpppo(L1_PLCS_IP['plc6'], 'HMI_MV501-Status', '1')

    # wait for the other plcs
    time.sleep(3)

    logger.info("PLC6 - enters main loop")

    start_time = time.time()

    while(time.time() - start_time < TIMEOUT):

        # Read and update HMI_tag
        lit601_str = read_single_statedb('6', 'AI_LIT_601_LEVEL')[3]

        write_cpppo(L1_PLCS_IP['plc6'], 'HMI_LIT601-Pv', lit601_str)
        val = read_cpppo(L1_PLCS_IP['plc6'], 'HMI_LIT601-Pv', PLC6_CPPPO_CACHE)
        logger.debug("PLC6 - read_cpppo HMI_LIT601-Pv: %s" % val)

        lit601 = float(lit601_str)

        # lit601
        if lit601 >= LIT_601['HH']:
            logger.warning("PLC6 - lit601 over HH: %.2f >= %.2f" % (
                lit601, LIT_601['HH']))

        elif lit601 <= LIT_601['LL']:
            logger.warning("PLC6 - lit601 under LL: %.2f <= %.2f" % (
                lit601, LIT_601['LL']))
            # CLOSE p601
            update_statedb('0', 'DO_P_601_START')
            write_cpppo(L1_PLCS_IP['plc6'], 'HMI_P601-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc6'], 'HMI_P601-Status', PLC6_CPPPO_CACHE)
            logger.warning("PLC6 - close p601: HMI_P601-Status: %s" % val)

        elif lit601 <= LIT_601['L']:
            # OPEN p501
           # update_statedb('0', 'DO_MV_101_CLOSE')
           # update_statedb('1', 'DO_MV_101_OPEN')
            update_statedb('1', 'DO_P_501_START')
            write_cpppo(L1_PLCS_IP['plc6'], 'HMI_P501-Status', '2')
            val = read_cpppo(L1_PLCS_IP['plc6'], 'HMI_P501-Status', PLC6_CPPPO_CACHE)
            logger.info("PLC6 - lit601 under L -> open p501: HMI_P501-Status: %s" % val)

        elif lit601 >= LIT_601['H']:
            # CLOSE p501
           # update_statedb('1', 'DO_MV_101_CLOSE')
           # update_statedb('0', 'DO_MV_101_OPEN')
            update_statedb('0', 'DO_P_501_START')
            write_cpppo(L1_PLCS_IP['plc6'], 'HMI_P501-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc6'], 'HMI_P501-Status', PLC6_CPPPO_CACHE)
            logger.info("PLC6 - lit601 over H -> close p501: HMI_P501-Status: %s" % val)

        # read from PLC2
        # val = read_cpppo(L1_PLCS_IP['plc2'], 'HMI_FIT201-Pv', PLC1_CPPPO_CACHE)
        # logger.debug("PLC1 - read_cpppo HMI_FIT201-Pv: %s" % val)
        # fit201 = float(val)

        # read from PLC3
        """val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_LIT301-Pv', PLC1_CPPPO_CACHE)
        logger.debug("PLC1 - read_cpppo HMI_LIT301-Pv: %s" % val)
        lit301 = float(val)

        if fit201 <= FIT_201: #or lit301 >= LIT_301['H']:
            # CLOSE p101
            update_statedb('0', 'DO_P_101_START')
            write_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', PLC1_CPPPO_CACHE)
            logger.info("PLC1 - fit201 under FIT_201 -> close p101: HMI_P101-Status: %s" % val)
"""
        # elif lit301 <= LIT_301['L']:
        #     # OPEN p101
        #     update_statedb('1', 'DO_P_101_START')
        #     write_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', '2')
        #     val = read_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', PLC1_CPPPO_CACHE)
        #     logger.info("PLC1 - open p101: HMI_P101-Status: %s" % val)

        # Sleep
        time.sleep(T_PLC_R)

    logger.info("PLC6 - exits main loop")

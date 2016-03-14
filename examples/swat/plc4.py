"""
SWaT plc4 subprocess 4 simulation
"""
import time

from constants import logger
from constants import P1_PLC4_TAGS, LIT_101, LIT_301,LIT_401, FIT_201, FIT_401
from constants import read_single_statedb, update_statedb
from constants import write_cpppo, read_cpppo, init_cpppo_server
from constants import L1_PLCS_IP
from constants import T_PLC_R, T_PLC_W, TIMEOUT
from constants import LIT_101, LIT_301, FIT_201, PLC4_CPPPO_CACHE

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
    tags.extend(P1_PLC4_TAGS)
    init_cpppo_server(tags)

    # init ENIP server tag values (taken from state_db)
    p401_str = read_single_statedb('4', 'DO_P_401_START')[3]
    if p401_str == '1':
        write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P401-Status', '2')
    else:
        write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P401-Status', '1')

    p301_str = read_single_statedb('3', 'DO_P_301_START')[3]
    if p301_str == '1':
        write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P301-Status', '2')
    else:
        write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P301-Status', '1')

    # wait for the other plcs
    time.sleep(3)

    logger.info("PLC4 - enters main loop")

    start_time = time.time()

    while(time.time() - start_time < TIMEOUT):

        # Read and update HMI_tag
        lit401_str = read_single_statedb('4', 'AI_LIT_401_LEVEL')[3]

        write_cpppo(L1_PLCS_IP['plc4'], 'HMI_LIT401-Pv', lit401_str)
        val = read_cpppo(L1_PLCS_IP['plc4'], 'HMI_LIT401-Pv', PLC4_CPPPO_CACHE)
        logger.debug("PLC4 - read_cpppo HMI_LIT401-Pv: %s" % val)

        lit401 = float(lit401_str)

        # lit401
        if lit401 >= LIT_401['HH']:
            logger.warning("PLC4 - lit401 over HH: %.2f >= %.2f" % (
                lit401, LIT_401['HH']))

        elif lit401 <= LIT_401['LL']:
            logger.warning("PLC4 - lit401 under LL: %.2f <= %.2f" % (
                lit401, LIT_401['LL']))
            # CLOSE p401
            update_statedb('0', 'DO_P_401_START')
            write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P401-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc4'], 'HMI_P401-Status', PLC4_CPPPO_CACHE)
            logger.warning("PLC4 - close p401: HMI_P401-Status: %s" % val)

        elif lit401 <= LIT_401['L']:
            # OPEN mv101
            #update_statedb('0', 'DO_P_301_CLOSE')
            #update_statedb('1', 'DO_MV_101_OPEN')
            update_statedb('1' , 'DO_P_301_START')
            write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P301-Status', '2')
            val = read_cpppo(L1_PLCS_IP['plc4'], 'HMI_P301-Status', PLC4_CPPPO_CACHE)
            logger.info("PLC4 - lit401 under L -> open p301: HMI_P301-Status: %s" % val)

        elif lit401 >= LIT_401['H']:
            # CLOSE mv101
           # update_statedb('1', 'DO_MV_101_CLOSE')
           # update_statedb('0', 'DO_MV_101_OPEN')
            update_statedb('0' , 'DO_P_301_START')
            write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P301-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc4'], 'HMI_P301-Status', PLC4_CPPPO_CACHE)
            logger.info("PLC4 - lit401 over H -> close p301: HMI_P301-Status: %s" % val)

        # read from PLC4
        val = read_cpppo(L1_PLCS_IP['plc4'], 'HMI_FIT401-Pv', PLC4_CPPPO_CACHE)
        logger.debug("PLC4 - read_cpppo HMI_FIT401-Pv: %s" % val)
        fit401 = float(val)

        # read from PLC3
       # val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_LIT301-Pv', PLC1_CPPPO_CACHE)
       # logger.debug("PLC1 - read_cpppo HMI_LIT301-Pv: %s" % val)
       # lit301 = float(val)

        if fit401 <= FIT_401: #or lit301 >= LIT_301['H']:
            # CLOSE p401
            update_statedb('0', 'DO_P_401_START')
            write_cpppo(L1_PLCS_IP['plc4'], 'HMI_P401-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc4'], 'HMI_P401-Status', PLC4_CPPPO_CACHE)
            logger.info("PLC4 - fit401 under FIT_401 -> close p401: HMI_P401-Status: %s" % val)

        # elif lit301 <= LIT_301['L']:
        #     # OPEN p101
        #     update_statedb('1', 'DO_P_101_START')
        #     write_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', '2')
        #     val = read_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', PLC1_CPPPO_CACHE)
        #     logger.info("PLC1 - open p101: HMI_P101-Status: %s" % val)

        # Sleep
        time.sleep(T_PLC_R)

    logger.info("PLC4 - exits main loop")

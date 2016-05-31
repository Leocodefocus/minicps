"""
SWaT plc3 subprocess 1 simulation.
"""
import time

from constants import logger
from constants import P1_PLC3_TAGS, LIT_101, LIT_301, FIT_201
from constants import read_single_statedb, update_statedb
from constants import write_cpppo, read_cpppo, init_cpppo_server
from utils import L1_PLCS_IP
from constants import T_PLC_R, T_PLC_W, TIMEOUT
from constants import LIT_101, LIT_301, FIT_201, PLC3_CPPPO_CACHE

if __name__ == '__main__':
    """Init cpppo enip server.

    Execute an infinite routine loop:
        - read sensors value
        - drive actuators according to the control strategy
        - update its enip server
    """

    # init the ENIP server
    tags = []
    tags.extend(P1_PLC3_TAGS)
    init_cpppo_server(tags)

    # init ENIP server tag values (taken from state_db)
    p301_str = read_single_statedb('3', 'DO_P_301_START')[3]
    if p301_str == '1':
        write_cpppo(L1_PLCS_IP['plc3'], 'HMI_P301-Status', '2')
    else:
        write_cpppo(L1_PLCS_IP['plc3'], 'HMI_P301-Status', '1')

    mv201_str = read_single_statedb('2', 'DO_MV_201_OPEN')[3]
    if mv201_str == '1':
        write_cpppo(L1_PLCS_IP['plc3'], 'HMI_MV201-Status', '2')
    else:
        write_cpppo(L1_PLCS_IP['plc3'], 'HMI_MV201-Status', '1')

    # wait for the other plcs
    time.sleep(3)

    logger.info("PLC3 - enters main loop")

    start_time = time.time()

    while(time.time() - start_time < TIMEOUT):

        # Read and update HMI_tag
        lit301_str = read_single_statedb('3', 'AI_LIT_301_LEVEL')[3]

        write_cpppo(L1_PLCS_IP['plc3'], 'HMI_LIT301-Pv', lit301_str)
        val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_LIT301-Pv', PLC3_CPPPO_CACHE)
        logger.debug("PLC3 - read_cpppo HMI_LIT301-Pv: %s" % val)

        lit301 = float(lit301_str)

        # lit101
        if lit301 >= LIT_301['HH']:
            logger.warning("PLC3 - lit301 over HH: %.2f >= %.2f" % (
                lit301, LIT_301['HH']))

        elif lit301 <= LIT_301['LL']:
            logger.warning("PLC3 - lit301 under LL: %.2f <= %.2f" % (
                lit301, LIT_301['LL']))
            # CLOSE p101
            update_statedb('0', 'DO_P_301_START')
            write_cpppo(L1_PLCS_IP['plc3'], 'HMI_P301-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_P301-Status', PLC3_CPPPO_CACHE)
            logger.warning("PLC3 - close p301: HMI_P301-Status: %s" % val)

        elif lit301 <= LIT_301['L']:
            # OPEN mv101
            update_statedb('0', 'DO_MV_201_CLOSE')
            update_statedb('1', 'DO_MV_201_OPEN')
            write_cpppo(L1_PLCS_IP['plc3'], 'HMI_MV201-Status', '2')
            val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_MV201-Status', PLC3_CPPPO_CACHE)
            logger.info("PLC3 - lit301 under L -> open mv201: HMI_MV201-Status: %s" % val)

        elif lit301 >= LIT_301['H']:
            # CLOSE mv101
            update_statedb('1', 'DO_MV_201_CLOSE')
            update_statedb('0', 'DO_MV_201_OPEN')
            write_cpppo(L1_PLCS_IP['plc3'], 'HMI_MV201-Status', '1')
            val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_MV201-Status', PLC3_CPPPO_CACHE)
            logger.info("PLC3 - lit301 over H -> close mv201: HMI_MV201-Status: %s" % val)

        # read from PLC2
        #val = read_cpppo(L1_PLCS_IP['plc2'], 'HMI_FIT201-Pv', PLC1_CPPPO_CACHE)
        #logger.debug("PLC1 - read_cpppo HMI_FIT201-Pv: %s" % val)
        #fit201 = float(val)

        # read from PLC3
        #val = read_cpppo(L1_PLCS_IP['plc3'], 'HMI_LIT301-Pv', PLC1_CPPPO_CACHE)
        #logger.debug("PLC1 - read_cpppo HMI_LIT301-Pv: %s" % val)
        #lit301 = float(val)

        #if fit201 <= FIT_201: #or lit301 >= LIT_301['H']:
            # CLOSE p101
         #   update_statedb('0', 'DO_P_101_START')
         #   write_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', '1')
         #   val = read_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', PLC1_CPPPO_CACHE)
         #   logger.info("PLC1 - fit201 under FIT_201 -> close p101: HMI_P101-Status: %s" % val)

        # elif lit301 <= LIT_301['L']:
        #     # OPEN p101
        #     update_statedb('1', 'DO_P_101_START')
        #     write_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', '2')
        #     val = read_cpppo(L1_PLCS_IP['plc1'], 'HMI_P101-Status', PLC1_CPPPO_CACHE)
        #     logger.info("PLC1 - open p101: HMI_P101-Status: %s" % val)

        # Sleep
        time.sleep(T_PLC_R)
    logger.info("PLC3 - exits main loop")


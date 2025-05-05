from enum import Enum

class KnownOlts(Enum):
    """
    Enum que "mapeia" o id_transmissor do IXC com o nome de uma OLT
    """
    OLT_CCDA_01 = '16'
    OLT_CCDA_02 = '20'
    OLT_COTIA_01 = '21'
    OLT_COTIA_02 = '24'
    OLT_COTIA_03 = '14'
    OLT_COTIA_04 = '22'
    OLT_COTIA_05 = '23'
    OLT_EMBU_01 = '3'
    OLT_GRVN_01 = '17'
    OLT_ITPV_01 = '2'
    OLT_TRMS_01 = '15'
    OLT_TRMS_02 = '9'
    OLT_VGPA_01 = '12'



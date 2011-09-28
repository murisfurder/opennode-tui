""" Reads OpenNode CT configuration """

import datetime

MAX_ULONG = 9223372036854775807

# Defaults
DEF_MEM         = 256         # Reference UBC memory amount
DEF_MEM         = 256         # Default guaranteed memory amount
DEF_DISK        = 10          # Default filesystem limit in GB
DEF_CPUS        = 1           # Default nr. of cpus
DEF_CPULIMIT    = 50          # Default CPU usage limit
DEF_CPUUNITS    = 1000        # Default CPU priority
DEF_INODES      = 200000      # Default nr. of filesystem inodes per 1GB
DEF_QUOTATIME   = 1800        # Default quota burst time 

DEFAULT_UBC_SETTINGS = {
    # Primary UBC limits
    'numproc': [240, 240],
    'avnumproc': [180, 180],
    'numtcpsock': [360, 360],
    'numothersock': [360, 360],
    'vmguarpages': [65536, MAX_ULONG],
    # Secondary UBC limits
    'kmemsize': [14372700, 14790164],
    'tcpsndbuf': [1720320, 2703360],
    'tcprcvbuf': [1720320, 2703360],
    'othersockbuf': [1126080, 2097152],
    'dgramrcvbuf': [262144, 262144],
    'oomguarpages': [50714, MAX_ULONG],
    'privvmpages': [98304, 104448],
    # Other UBC limits
    'lockedpages': [256, 256],
    'shmpages': [21504, 21504],
    'physpages': [0, MAX_ULONG], # NB! This parameter is accounting only! (read-only, no calculations)
    'dcachesize': [3409920, 3624960],
    'numfile': [9312, 9312],
    'numflock': [188, 206],
    'numpty': [16, 16],
    'numsiginfo': [256, 256],
    'numiptent': [128, 128],
}

def get_config(user_settings):
    """Output OpenVZ configuration file"""
    input_settings = {
        # memory in mb!
        "memory": float(user_settings["memory"]) * 1024 if "memory" in user_settings else DEF_MEM,
        "vcpu": user_settings.get("vcpu", DEF_CPUS),
        "disk": user_settings.get("disk", DEF_DISK),
        "vcpulimit": user_settings.get("vcpulimit", DEF_CPULIMIT)
    }
    
    # adjust default ubc settings
    ubc_settings = DEFAULT_UBC_SETTINGS.copy()
    mem_ratio = float(user_settings["memory"]) * 1024 / DEF_MEM # ratio between reference and desired memory parameter
    # change parameters having values MAX_ULONG
    ubc_settings["physpages"][1] = int(ubc_settings["physpages"][0] * mem_ratio)
    ubc_settings["oomguarpages"][1] = int(ubc_settings["oomguarpages"][0] * mem_ratio)
    ubc_settings["vmguarpages"][1] = int(ubc_settings["vmguarpages"][0] * mem_ratio)
    
    # get sections of configuration file as string
    header_section = _get_header_section()
    ubc_section = _get_ubc_section(ubc_settings)
    disk_section = _get_disk_section(input_settings)
    cpu_section = _get_cpu_section(input_settings)
    
    vzcfg_str = "".join([header_section, ubc_section, disk_section, cpu_section])
    return vzcfg_str
    
def _get_disk_section(settings):
    """Output OpenVZ configuration file disk limits section"""
    # TODO: Check if min, max calculations are correct.
    template = """\
DISKSPACE=%(diskspace_min)s:%(diskspace_max)s
DISKINODES=%(diskinodes_min)s:%(diskinodes_max)s
QUOTATIME=%s
"""
    disk_settings = { 
        "diskspace_min": settings["disk"],
        "diskspace_max": float(settings["disk"]) + 1,
        "diskinodes_min": float(settings["disk"]) * DEF_INODES,
        "diskinodes_max": float(settings["disk"]) * DEF_INODES * 1.10, 
        "quotatime": DEF_QUOTATIME
    }
    return template % disk_settings 

def _get_cpu_section(settings):
    """Output OpenVZ configuration cpu limits section"""
    template = """\
# CPU resource limits
CPUUNITS=%s
CPULIMIT=%s
CPUS=%s
"""
    cpu_settings = {
        'cpus': settings["vcpu"],
        'cpulimit': float(settings["vcpulimit"]) * int(settings["vcpu"]),
        'cpuunits': DEF_CPUUNITS
    }
    return template % cpu_settings

def _get_header_section(settings):
    """Output OpenVZ configuration file header section"""
    header_template = """\
#+--------------------------------------------------------------+
#| CT configuration generated by OpenNode vzcfgcreator script \t|
#+--------------------------------------------------------------+
#| Input params were                         |
#+--------------------------------------------------------------+
#| MEMORY    : %(memory)sMB  \t\t\t\t\t\t|
#| DISK      : %(disk)sGB \t\t\t\t\t\t| 
#| CPUS      : %(vcpu)s \t\t\t\t\t\t|  
#| CPULIMIT  : %(vcpulimit)s%% \t\t\t\t\t\t|
#+--------------------------------------------------------------+      
#| Generated : %(time)s \t\t\t|\n'
#+--------------------------------------------------------------+

"""
    params = {
        "memory": settings["memory"], 
        "disk": settings["disk"],
        "vcpu": settings["vcpu"],
        "vcpulimit": settings["vcpulimit"], 
        "time": datetime.datetime.today().ctime()
    } 
    return header_template % params

def _get_ubc_section(ubc_settings):
    """Output valid OpenVZ configuration file UBC section"""
    template = """\
# Primary UBC resource limits (in form of barrier:limit)\n'
NUMPROC=%(numproc_min)s:%(numproc_max)s
AVNUMPROC=%(avnumproc_min)s:%(avnumproc_max)s
NUMTCPSOCK=%(numtcpsock_min)s:%(numtcpsock_max)s
NUMOTHERSOCK=%(numothersock_min)s:%(numothersock_max)s
VMGUARPAGES=%(vmguarpages_min)s:%(vmguarpages_max)s 
# Secondary UBC resource limits'
KMEMSIZE=%(kmemsize_min)s:%(kmemsize_max)s
TCPSNDBUF=%(tcpsndbuf_min)s:%(tcpsndbuf_max)s
TCPRCVBUF=%(tcprcvbuf_min)s:%(tcprcvbuf_max)s
OTHERSOCKBUF=%(othersockbuf_min)s:%(othersockbuf_max)s
DGRAMRCVBUF=%(dgramrcvbuf_min)s:%(dgramrcvbuf_max)s
OOMGUARPAGES=%(oomguarpages_min)s:%(oomguarpages_max)s
PRIVVMPAGES=%(privvmpages_min)s:%(privvmpages_max)s
# Other UBC resource limits\n'
LOCKEDPAGES=%(lockedpages_min)s:%(lockedpages_max)s
SHMPAGES=%(shmpages_min)s:%(shmpages_max)s
PHYSPAGES=%(physpages_min)s:%(physpages_max)s
DCACHESIZE=%(dcachesize_min)s:%(dcachesize_max)s
NUMFILE=%(numfile_min)s:%(numfile_max)s
NUMFLOCK=%(numflock_min)s:%(numflock_max)s
NUMPTY=%(numpty_min)s:%(numpty_max)s
NUMSIGINFO=%(numsiginfo_min)s:%(numsiginfo_max)s
NUMIPTENT=%(numiptent_min)s:%(numiptent_max)s        
"""
    ubc = ubc_settings
    params = {
        "numproc_min": ubc['numproc'][0], "numproc_max": ubc['numproc'][1],
        "avnumproc_min": ubc['avnumproc'][0], "avnumproc_max": ubc['avnumproc'][1],
        "numtcpsock_min": ubc['numtcpsock'][0], "numtcpsock_max": ubc['numtcpsock'][1],
        "numothersock_min": ubc['numothersock'][0], "numothersock_max": ubc['numothersock'][1],
        "vmguarpages_min": ubc['vmguarpages'][0], "vmguarpages_max": ubc['vmguarpages'][1],
        "kmemsize_min": ubc['kmemsize'][0], "kmemsize_max": ubc['kmemsize'][1],
        "tcpsndbuf_min": ubc['tcpsndbuf'][0], "tcpsndbuf_max": ubc['tcpsndbuf'][1],
        "tcprcvbuf_min": ubc['tcprcvbuf'][0], "tcprcvbuf_max": ubc['tcprcvbuf'][1],
        "othersockbuf_min": ubc['othersockbuf'][0], "othersockbuf_max": ubc['othersockbuf'][1],
        "dgramrcvbuf_min": ubc['dgramrcvbuf'][0], "dgramrcvbuf_max": ubc['dgramrcvbuf'][1],
        "oomguarpages_min": ubc['oomguarpages'][0], "oomguarpages_max": ubc['oomguarpages'][1],
        "privvmpages_min": ubc['privvmpages'][0], "privvmpages_max": ubc['privvmpages'][1],
        "lockedpages_min": ubc['lockedpages'][0], "lockedpages_max": ubc['lockedpages'][1],
        "shmpages_min": ubc['shmpages'][0], "shmpages_max": ubc['shmpages'][1],
        "dcachesize_min": ubc['dcachesize'][0], "dcachesize_max": ubc['dcachesize'][1],
        "physpages_min": ubc['physpages'][0], "physpages_max": ubc['physpages'][1],
        "numfile_min": ubc['numfile'][0], "numfile_max": ubc['numfile'][1],
        "numflock_min": ubc['numflock'][0], "numflock_max": ubc['numflock'][1],
        "numpty_min": ubc['numpty'][0], "numpty_max": ubc['numpty'][1],
        "numsiginfo_min": ubc['numsiginfo'][0], "numsiginfo_max": ubc['numsiginfo'][1],
        "numiptent_min": ubc['numiptent'][0], "numiptent_max": ubc['numiptent'][1],
    }
    return template % params


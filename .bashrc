# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
# Commented out setupATLAS since this is already available on the Analysis Facility (I think it is defined elsewhere).
#setupATLAS()
#{
#    source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh # currently defining ATLAS_LOCAL_ROOT_BASE in .bash_profile, would need fwd definition here
#}
#export -f setupATLAS

# For grid proxy stuff (e.g. rucio)
vms()
{
  voms-proxy-init -voms atlas
}
export -f vms

# rucio search, for looking for stuff you have generated
rsearch()
{
  rucio list-dids user.${USER}:user.${USER}.${1} --filter type=CONTAINER
}
export -f rsearch

# Unpacks tarballs made by panda (e.g. pathena) & combines the log files.
# (then deletes the unpacked tarballs)
pandalog()
{
  ~/scripts/python/panda_log.py -i "${1}"
}
export -f pandalog

# Makes plots of memory usage of condor jobs, annotated
# with information on status (e.g. held), by taking info
# from the condor logs.
condor_mem()
{
  ~/scripts/condor_memory.sh "${1}" "${2}"
}
export -f condor_mem

# check my condor priority
myprio()
{
  condor_userprio --allusers | head -n 4
  condor_userprio --allusers | grep "${USER}"
}
export -f myprio

# condor_q (checking job/queue status)
cq()
{
  allUsers=0
  while test $# -gt 0
  do
      case "$1" in
          --all-users) allUsers=1
              ;;
      esac
      shift
  done

  if [ "$allUsers" -gt "0" ]; then
    condor_q "$@"
  else
    condor_q "${USER}"
  fi
}
export -f cq


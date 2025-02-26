# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/.local/bin:$HOME/bin
export PATH
export DEFAULT_PS1=${PS1}

# ATLASLocalRootBase setups
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase
export ALRB_localConfigDir=$HOME/localConfig

# LXPLUS (CERN) setup
#export LXPLUS_USER="<your_username_here>"

# Setup for accessing CERN EOS (thanks to Karri)
export EOS_MGM_URL=root://eosuser.cern.ch

# Set up context highlighting for ls
alias ls='ls --color=auto'

# Shorthand for rucio search (handy since I use it a lot)
alias rls='rucio list-dids'

echo "Welcome back."

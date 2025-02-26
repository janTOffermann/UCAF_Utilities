# UCAF_Utilities
A small set of scripts (with accompanying .bashrc) for the UChicago Analysis Facility (UCAF). A few notes:

- As these commands and scripts were developed for use on the UCAF, they make use of things such as the [CERN Virtual Machine File System](https://cvmfs.readthedocs.io/en/stable/). Thus a lot of these scripts may *not* be so useful outside of that context, although there's a script for monitoring memory usage of [HTCondor](https://htcondor.readthedocs.io/en/latest/) jobs that may be independently useful.
- There is a `.asetup` file that works with the associated `asetup` command (for setting up ATLAS Athena). This will modify the `$PS1` so that it displays what release is being used -- I find this very helpful for debugging. (Many thanks to Ben Rosser [UChicago] for this feature!). Unfortunately I don't (yet) have an equivalent for the environment setups done through tools like `lsetup views`.

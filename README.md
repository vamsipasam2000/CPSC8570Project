# VulnerabilityLifetimes Artifact for USENIX Sec'22

Paper: [pdf](https://www.usenix.org/system/files/sec22summer_alexopoulos.pdf)
## Instructions

- Clone this repository `git clone --branch usenix_v0 https://github.com/manuelbrack/VulnerabilityLifetimes.git`.
- Change working directory to the repository `cd ./VulnerabilityLifetimes`.
- Run `./build_run_docker.sh` to build and run the docker container for the artifact (docker and superuser priviledges required). This will give you a bash prompt in the now running container. Change working directory with `cd ./VulnerabilityLifetimes`.
- To execute all operations run `./run_all.sh`. We recommend that you redirect the stdout and stderr (also) to a file so that you can make sure everything worked fine, e.g. with `./run_all.sh |& tee -a log.txt`. You can also run this script in the background or detach from the docker container while you wait for the artifact to execute. Instead of executing the `run_all.sh` script you can view it and execute the commands in it one by one. Generally, the main thing that can go wrong is a problem in cloning a repository or downloading an external file (due to e.g. a server side or connectivity issue). In that case the commands in the `run_all.sh` script can be repeated.
- If everything is successful, the output will be located in the `./out` directory. Check the content of the file `./out/lifetimes_table.csv`. If the reported numbers are similar to the ones of Table 3 of the paper, then you can be confident that the code ran as expected. Copy the contents of the `./out` directory from the container to the host ([docker cp](https://docs.docker.com/engine/reference/commandline/cp/)), and then to a machine with a screen so you can also view the plots. Plots are organized as follows:
    -  in the directory `./out/distributions` you can find all plots having to do with distributions (e.g. Figures 5,6 of the paper).
    -  in the directory `./out/year_trends` you can find all plots showing the progression of lifetimes over time (e.g. content of Figures 3,7,10 of the paper).
    -  in the directory `./out/regular_code_age` you can find all plots comparing vulnerability lifetimes with code age (e.g. content of Figure 9 of the paper).

## Authors
* Manuel Brack - Initial work - [manuelbrack](https://github.com/manuelbrack)
* Jan Philipp Wagner - Initial work - [jp-wagner](https://github.com/jp-wagner)
* Nikolaos Alexopoulos - coordination & USENIX AE branch - [nikalexo](https://github.com/nikalexo)

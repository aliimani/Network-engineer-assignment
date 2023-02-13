#!/bin/bash
#last updated: 12-02-2023 12:30pm

RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m"

function checker() { 
        which "$1" | grep -o "$1" > /dev/null &&  return 0 || return 1 
}


while [ true ]
do
	echo "----------------------------------------------------------"
	echo -e ""$BLUE"prerequisites tools:$NC"
	echo "1.- Install Docker and Python"
	echo "2.- Install Python"
	echo "3.- Install Ansible, Docker collection and yq"
	echo "----------------------------------------------------------"
	echo -e ""$BLUE"Step1: Build section:$NC"
	echo -e "4.- Method 1: Build the network topology using an$YELLOW ansible play-book$NC"
	echo -e "5.- Method 2: Build the network topology using an$YELLOW shell script$NC"
	echo "----------------------------------------------------------"
	echo -e ""$BLUE"Step2: Configuration section:$NC"
	echo -e "6.- Deploy the required configuration on the VyOS routers using a$YELLOW Python script$NC"
	echo "----------------------------------------------------------"
	echo -e ""$BLUE"View and modify section:$NC"
	echo "7.- List of all created containers"
	echo "8.- List of all created docker networks"
    echo "9.- Stop and delete all created containers & networks"
    echo "10.- Start all created containers"
	echo "11.- Tips for connecting to VyOS routers and hosts"
	echo "----------------------------------------------------------"
	echo "Q to exit the menu"
	echo "----------------------------------------------------------"

	read -p "$(echo -e $GREEN"Select on of the options: "$NC)" opc

	case $opc in

		1) #Install Docker
			sudo apt update
			sudo apt install apt-transport-https ca-certificates curl software-properties-common
			curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
			sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
			apt-cache policy docker-ce
			sudo apt install docker-ce
			echo "----------------------------------------------------------"
			docker --version

			read -p  'Press [Enter] key to return to the main menu.'
		;;

		2) #Install Python
			sudo apt update
			sudo apt install software-properties-common
			add-apt-repository -y ppa:deadsnakes/ppa
			sudo apt install python3.9
			curl https://bootstrap.pypa.io/get-pip.py -o /get-pip.py
			python3 /get-pip.py --user
			echo "----------------------------------------------------------"
			python3 --version
			python3 -m pip -V

			read -p  'Press [Enter] key to return to the main menu.'
		;;

		3) #Install Anisble
            sudo apt update
            sudo apt install -y software-properties-common
            sudo add-apt-repository --yes --update ppa:ansible/ansible
			sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
			sudo chmod a+x /usr/local/bin/yq
            apt install ansible-core
            sudo apt install -y ansible
            sudo ansible-galaxy collection install community.docker
			ansible-galaxy collection install community.docker
			echo "----------------------------------------------------------"
            ansible --version
			yq --version

            read -p  'Press [Enter] key to return to the main menu.'
		;;
		4) #Build the network topology using an ansible play-book

			ansible-playbook ./build/build_network.yml

            read -p  'Press [Enter] key to return to the main menu.'
		;;
		5) #Build the network topology using an shell script"
			chmod u+r+x  ./build/build_network.sh
			./build/build_network.sh
			
			read -p  'Press [Enter] key to return to the main menu.'
		;;
		6) #Deploy the required configuration on the VyOS routers using a Python script"
			
			python3 ./deploy/main.py
			
            read -p  'Press [Enter] key to return to the main menu.'
		;;

		7) #List of all created containers
			docker ps --filter "label=type=assignment"           

            read -p  'Press [Enter] key to return to the main menu.'
		;;

		8) #List of all created docker networks
			docker network ls  --filter type=custom

            read -p  'Press [Enter] key to return to the main menu.'
		;;

        9) #Stop and delete all created containers & networks

			echo -e "${YELLOW}->Stopping all created containers...${NC}"
			bash -c '{ docker ps -a --format '{{.Names}}' --filter "label=type=assignment";}' \
                       | sort | uniq -u | xargs --no-run-if-empty docker stop

			echo -e "${YELLOW}->Removing all created containers...${NC}"
            bash -c '{ docker ps -aq --format '{{.Names}}' --filter "label=type=assignment";}' \
                       | sort | uniq -u | xargs --no-run-if-empty docker rm

			echo -e "${YELLOW}->Removing all created networks...${NC}"

			sleep 2
            # docker network rm `docker network ls --filter type=custom -q`
 			docker network prune
			sleep 2
            read -p  'Press [Enter] key to return to the main menu.'
		;;

        10)  #Start all created containers

			echo -e "${YELLOW}->Starting all created containers...${NC}"
            bash -c '{ docker ps -aq --format '{{.Names}}' --filter "label=type=assignment";}' \
                       | sort | uniq -u| xargs --no-run-if-empty docker start
			
            read -p  'Press [Enter] key to return to the main menu.'
        ;;

		11)
			echo -e "-> Default login user and password to connect VyOS router are ["$BLUE"vyos$NC] ["$BLUE"swisscom$NC] respectivly."
			echo -e "-> SSH servic is enabled on all VyOS routers."
			echo -e "-> All VyOS routers were connected to the "$BLUE"manage_routers[172.16.100.0/24]$NC network to be configured directly via API"
			echo -e "   Central router ip ["$BLUE"172.16.100.2$NC]  |  Site A router ip ["$BLUE"172.16.100.3$NC]  |  Site B router ip ["$BLUE"172.16.100.4$NC]"
			echo -e "-> To execute a command into Vyos Router: docker exec -it "$BLUE"container name$NC su - vyos"
			echo -e "-> To execute a command into host container: docker exec -it "$BLUE"container name$NC bash"
			echo
			read -p  'Press [Enter] key to return to the main menu.'
		;;

		q)
			exit 0
		;;

		*)
			echo "You have not chosen any function!"
			exit 1
		;;
	esac
done
#!/bin/bash
#last updated: 09-02-2023 02:40pm

#Define variables:###########################################################################
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m"        # No Color
HOST_LOCATION="$(dirname "$0")/host_vars/localhost.yml"

#Tasks:######################################################################################
notify_fun()
{
  perl -E "print '$1' x '$2'"
  echo
}


notfiy_fun '#' 100

#Get active physical interface name:-----------------------
echo -e "${YELLOW}->Getting active physical interface name...${NC}"
PARENT_INT=$(ip addr show | awk '/inet.*brd/{print $NF; exit}')

notify_fun '#' 100
sleep 2

#Create all required docker networks:-----------------------
echo -e "${YELLOW}->Creating all required docker networks...${NC}"
readarray NETWORKS_MAPPING < <(yq -o=j -I=0 '.networks[]' $HOST_LOCATION)
for NETWORK in "${NETWORKS_MAPPING[@]}"; do
    NET_NAME=$(echo "$NETWORK" | yq '.name')     
    NET_DRIVER=$(echo "$NETWORK" | yq '.driver' -)   
    SUBNET_IPV4=$(echo "$NETWORK" | yq '.subnet_ipv4')
    GATEWAY_IPV4=$(echo "$NETWORK" | yq '.gateway_ipv4')
    SUBNET_IPV6=$(echo "$NETWORK" | yq '.subnet_ipv6')

    if [ $NET_DRIVER == "macvlan" ]; then
        VLAN_ID=$(echo "$NETWORK" | yq '.vlan_id') 
        echo -e "${BLUE}--->MacVLAN network name:${NC}[${GREEN}$NET_NAME${NC}]"
        docker network create --driver=$NET_DRIVER --ipv6 --subnet=$SUBNET_IPV4 --subnet=$SUBNET_IPV6 \
                              --gateway=$GATEWAY_IPV4 -o parent=$PARENT_INT.$VLAN_ID $NET_NAME
    elif [ $NET_DRIVER == "bridge" ]; then
    echo -e "${BLUE}--->Bridge network name:${NC}[${GREEN}$NET_NAME${NC}]"
    docker network create --driver=$NET_DRIVER --ipv6 --subnet=$SUBNET_IPV4 --subnet=$SUBNET_IPV6 \
                            --gateway=$GATEWAY_IPV4 $NET_NAME
    fi
done

notify_fun '#' 100
#Pull all required images:-----------------------
readarray IMAGE_MAPPING < <(yq -o=j -I=0 '.images[]' $HOST_LOCATION)
for IMAGE in "${IMAGE_MAPPING[@]}"; do 
    IMAGE_NAME=$(echo "$IMAGE" | yq '.name')   
    IMAGE_TAG=$(echo "$IMAGE" | yq '.image') 
    echo -e "${YELLOW}->pulling [${BLUE}$IMAGE_NAME${NC}${YELLOW}] image...${NC}"
    docker image pull $IMAGE_TAG 
done
sleep 2

#Create all VyOS router containers:-----------------------
readarray ROUTERS_MAPPING < <(yq -o=j -I=0 '.routers[]' $HOST_LOCATION)
for ROUTER in "${ROUTERS_MAPPING[@]}"; do 
    ROUTER_NAME=$(echo "$ROUTER" | yq '.name')   
    NETWORK=$(echo "$ROUTER" | yq '.networks')   
    OS_NAME=$(echo "$ROUTER" | yq '.router_os_name')
    IMAGE_NAME=$(echo "$IMAGE_MAPPING" | yq '.image')
    IMAGE_VOL=$(echo "$IMAGE_MAPPING" | yq '.volume')
    IMAGE_CMD=$(echo "$IMAGE_MAPPING" | yq '.command')
    
    notify_fun '#' 100

    echo -e "${BLUE}--->Create and configure VyOS router container:[${GREEN}$ROUTER_NAME${NC}]"
    docker create --privileged --label type=assignment --network none --name $ROUTER_NAME  -v $IMAGE_VOL $IMAGE_NAME $IMAGE_CMD

    notify_fun '-' 80
    sleep 2

#Attaching networks to VyOS router containers:-----------------------
    echo -e "${YELLOW}->Connect networks to [${BLUE}$ROUTER_NAME${NC}${YELLOW}] container${NC}"  
    docker network disconnect none $ROUTER_NAME
    for NETWORK in $(echo "$ROUTER" | yq -o=j -I=0 '.networks[]'); do
        NET_NAME=$(echo "$NETWORK" | yq '.name') 
        IPV4_ADDRESS=$(echo "$NETWORK" | yq '.ipv4_address')
        echo -e "--->Attaching ${GREEN}$NET_NAME${NC} network..." 

        if [ $IPV4_ADDRESS == "none" ]; then
            docker network connect $NET_NAME $ROUTER_NAME
        else
            docker network connect --ip $IPV4_ADDRESS $NET_NAME $ROUTER_NAME
        fi
    done

    notify_fun '-' 80
    sleep 2

#Upload predfined config file into:-----------------------
    echo -e "${YELLOW}->Uploading the predfined config file into [${BLUE}$ROUTER_NAME${NC}${YELLOW}] container...${NC}"
    docker cp ./config/config.boot $ROUTER_NAME:/config
    notify_fun '-' 80
    sleep 2
    
#Start all VyOS router containers:-----------------------
    echo -e "${YELLOW}->Starting [${BLUE}$ROUTER_NAME${NC}${YELLOW}] container...${NC}"
    docker start $ROUTER_NAME
    notify_fun '-' 80
    sleep 2

#Generate self-signed SSL certificates for all VyOS router containers:-----------------------
    echo -e "${YELLOW}->Generating self-signed SSL certificates for [${BLUE}$ROUTER_NAME${NC}${YELLOW}] container...${NC}"
    docker exec $ROUTER_NAME bash -c "sudo make-ssl-cert generate-default-snakeoil --force-overwrite"
    notify_fun '-' 80
    sleep 2

#Enable IPv6 on all VyOS router containers:-----------------------
    echo -e "${YELLOW}->Enabling IPv6 on [${BLUE}$ROUTER_NAME${NC}${YELLOW}] container${NC}"
    docker exec $ROUTER_NAME bash -c "echo sudo sysctl -w net.ipv6.conf.default.disable_ipv6=0 >> \
                                      /config/scripts/vyos-postconfig-bootup.script"
    notify_fun '-' 80
    sleep 2

#Remove default gateway from the containers:-----------------------
    echo -e "${YELLOW}->Removing default gateway from [${BLUE}$ROUTER_NAME${NC}${YELLOW}] container...${NC}"
    docker exec $ROUTER_NAME bash -c "echo sudo ip route del default >>  /config/scripts/vyos-postconfig-bootup.script"
done

notify_fun '#' 100
sleep 2

#Create and running host containers:-----------------------
echo -e "${YELLOW}->Create and running host containers${NC}"
readarray HOSTS_MAPPING < <(yq -o=j -I=0 '.hosts[]' $HOST_LOCATION)
readarray IMAGE_MAPPING < <(yq -o=j -I=0 '.images[1]' $HOST_LOCATION)
for HOST in "${HOSTS_MAPPING[@]}"; do 
    HOST_NAME=$(echo "$HOST" | yq '.name')   
    NETWORK=$(echo "$HOST" | yq '.net_name')   
    IMAGE_NAME=$(echo "$IMAGE_MAPPING" | yq '.image')
    IMAGE_VOL=$(echo "$IMAGE_MAPPING" | yq '.volume')
    IMAGE_CMD=$(echo "$IMAGE_MAPPING" | yq '.command')
    echo -e "${BLUE}--->Container name:[${GREEN}$HOST_NAME${NC}]"
    docker run -d -t --label type=assignment --privileged --network $NETWORK --name $HOST_NAME $IMAGE_NAME $IMAGE_CMD
done
notify_fun '#' 100
echo "done!"
sleep 1

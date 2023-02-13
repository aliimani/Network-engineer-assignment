service {
    https {
        api {
            keys {
                id 1 {
                    key "swisscom"
                }
            }
        }
    }
    ssh {
        port "22"
    }
}
system {
    conntrack {
        modules {
            tftp { }
            sqlnet { }
            sip { }
            pptp { }
            nfs { }
            h323 { }
            ftp { }
        }
    }
    host-name "vyos"
    login {
        user vyos {
            authentication {
                encrypted-password "$6$QxPS.uk6mfo$9QBSo8u1FkH16gMyAVhus6fU3LOzvLR9Z9.82m3tiHFAxTtIkhaZSWssSgzt4v4dGAL8rhVQxTg0oAG9/q11h/"
                plaintext-password ""
            }
        }
    }
    console {
        device ttyS0 {
            speed "115200"
        }
    }
    config-management {
        commit-revisions "100"
    }
}
interfaces {
    loopback     lo { }
}

// Warning: Do not remove the following line.
// vyos-config-version: "broadcast-relay@1:cluster@1:config-management@1:conntrack@3:conntrack-sync@2:dhcp-relay@2:dhcp-server@6:dhcpv6-server@1:dns-forwarding@3:firewall@9:https@4:interfaces@26:ipoe-server@1:ipsec@11:isis@2:l2tp@4:lldp@1:mdns@1:nat@5:ntp@2:pppoe-server@6:pptp@2:qos@2:quagga@10:rpki@1:salt@1:snmp@3:ssh@2:sstp@4:system@25:vrrp@3:vyos-accel-ppp@2:wanloadbalance@3:webproxy@2:zone-policy@1"


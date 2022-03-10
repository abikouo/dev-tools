let Config = ../Config/package.dhall

let userdata = Some ./vexxhost-nodepool-ansible-userdata.txt as Text

let key-name = Some "infra-root-keys"

let labels =
      [ Config.Label::{
        , cloud-image = Some "esxi-7.0U3-18644231-STANDARD"
        , flavor-name = Some "v3-starter-2"
        , name = "ansible-esxi-7.0.3"
        , key-name
        }
      , Config.Label::{
        , cloud-image = Some "Fedora-Cloud-Base-35-1.2.x86_64"
        , flavor-name = Some "v3-standard-2"
        , name = "ansible-fedora-35-1vcpu"
        , key-name
        , userdata
        }
      , Config.Label::{
        , cloud-image = Some "VMware-VCSA-all-7.0.3-18778458"
        , flavor-name = Some "v3-standard-8"
        , name = "ansible-vmware-vcsa-7.0.3"
        , key-name
        }
      , Config.Label::{
        , cloud-image = Some "eos-4.24-sf"
        , flavor-name = Some "v3-starter-1"
        , name = "vEOS-4.24.6F"
        , connection-type = Some "network_cli"
        }
      ]

let net = [ "public", "net1", "net2" ]

let flavors = [ { name = "v3-starter-2", id = "tiny" } ]

let attrs = { userdata, key-name }

in  ./mkProviderForAnsible.dhall "vexxhost" "ams1" net 50 labels attrs flavors

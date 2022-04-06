let Config = ../Config/package.dhall

let userdata = Some ./vexxhost-nodepool-ansible-userdata.txt as Text

let key-name = Some "infra-root-keys"

let labels =
      [ Config.Label::{
        , cloud-image = Some "Fedora-Cloud-Base-35-1.2.x86_64"
        , flavor-name = Some "c1.hwetest.1"
        , name = "ansible-fedora-35-1vcpu"
        , key-name
        , userdata
        }
      , Config.Label::{
        , cloud-image = Some "eos-4.24-sf"
        , flavor-name = Some "l1.medium"
        , name = "vEOS-4.24.6F"
        , connection-type = Some "network_cli"
        }
      ]

let net =
      [ "Public Internet"
      , "Private Network (10.0.0.0/8 only)"
      , "Private Network (Floating Public)"
      ]

let flavors = [ { name = "c1.hwetest.1", id = "tiny" } ]

let attrs = { userdata, key-name }

in  ./mkProviderForAnsible.dhall
      "limestone"
      "us-dfw-1"
      net
      20
      labels
      attrs
      flavors
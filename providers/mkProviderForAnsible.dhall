-- | A shared provider configuration for the ansible tenant
let Openstack = (../Config/Import.dhall).Nodepool.Openstack

let Config = ../Config/package.dhall

let Diskimages = ../diskimages/package.dhall

let diskimages =
      [ Diskimages.cloud-fedora-rawhide
      , Diskimages.cloud-fedora-35
      , Diskimages.cloud-centos-8-stream
      , Diskimages.cloud-centos-9-stream
      ]

let FlavorName
    : Type
    = { id : Text, name : Text }

in  \(cloud : Text) ->
    \(region-name : Text) ->
    \(networks : List Text) ->
    \(max-servers : Natural) ->
    \(cloud-images : List Config.Label.Type) ->
    \ ( diskimages-attributes
      : { key-name : Optional Text, userdata : Optional Text }
      ) ->
    \(flavor-names : List FlavorName) ->
      let cloud = "ansible-${cloud}"

      let DiskFlavor
          : Type
          = { name : Text, flavor-name : Text, image : Text }

      let makeDiskFlavor =
            \(flavor : FlavorName) ->
            \(diskimage : Config.Nodepool.Diskimage.Type) ->
              let result
                  : DiskFlavor
                  = { name = "ansible-${diskimage.name}-${flavor.id}"
                    , image = "${diskimage.name}"
                    , flavor-name = flavor.name
                    }

              in  result

      let generate-disk-flavor =
            \(flavor : FlavorName) ->
              Config.Prelude.List.map
                Config.Nodepool.Diskimage.Type
                DiskFlavor
                ( \(disk : Config.Nodepool.Diskimage.Type) ->
                    makeDiskFlavor flavor disk
                )

      let disk-attributes =
            let flavor-generator =
                  \(flavors : List FlavorName) ->
                  \(disks : List Config.Nodepool.Diskimage.Type) ->
                    Config.Prelude.List.map
                      FlavorName
                      (List DiskFlavor)
                      ( \(flavor : FlavorName) ->
                          generate-disk-flavor flavor disks
                      )
                      flavors

            let flatten-list = Config.Prelude.List.concat DiskFlavor

            in  flatten-list (flavor-generator flavor-names diskimages)

      let disk-images =
            Config.Prelude.List.map
              DiskFlavor
              Config.Label.Type
              ( \(diskflavor : DiskFlavor) ->
                  Config.Label::{
                  , diskimage = Some diskflavor.image
                  , name = diskflavor.name
                  , flavor-name = Some diskflavor.flavor-name
                  , key-name = diskimages-attributes.key-name
                  , userdata = diskimages-attributes.userdata
                  }
              )
              disk-attributes

      in  { labels = Config.Label.mkTopLevelLabels (cloud-images # disk-images)
          , diskimages
          , provider = Openstack::{
            , name = "${cloud}-${region-name}"
            , cloud
            , boot-timeout = Some 300
            , launch-timeout = Some 300
            , launch-retries = Some 6
            , cloud-images = Some
                (Config.Provider.mkOpenstackCloudImages cloud-images)
            , pools = Some
              [ Openstack.Pool::{
                , labels =
                    Config.Label.mkOpenstackPoolLabels
                      (cloud-images # disk-images)
                , max-servers = Some max-servers
                , name = Some "main"
                , networks = Some networks
                }
              ]
            , region-name = Some region-name
            }
          }

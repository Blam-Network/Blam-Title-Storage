# Blam Title Storage
This repository contains configuration file for online functionality of Xbox 360 generation Halo games.
Features available vary by title and version, but tend to include Matchmaking Playlists, MOTD messages, etc.
## Halo 3 [Release]
Configuration for the public Release versions of Halo 3. While they all use the same configuration, we currently only target Title-Update 2 `12070.08.09.05.2031.halo3_ship`. If support for TU1 or TU0 is ever required, this is simply a case of including that version's network configuration file.
- `12070.08.09.05.2031.halo3_ship` (Title-Update 2)
- `11902.08.01.16.1426.halo3_ship` (Title-Update 1)
- `11855.07.08.20.2317.halo3_ship`
### Managing Variants
Map and Game variants can be imported into Halo 3 Release configuration using the [blf_cli](https://github.com/Blam-Network/blf) they can be imported from Halo 3 Xbox 360 packaged variants or from Halo: The Master Chief Collection.
```bash
blf_cli
  title-storage
  import-variant
  "~/Blam-Title-Storage/Halo 3/Release/default_hoppers"
  ~/variants/cavern
  "Halo 3"
  12070.08.09.05.2031.halo3_ship
```

## Halo 3 ODST
Configuration for Halo 3 ODST `13895.09.04.27.2201.atlas_release`. ODST doesn't have many online-features, but notably includes a special MOTD popup which displays when Vidmaster achievements have been unlocked.

## Halo: Reach [Release]
Configuration for Release and Post-Release Halo: Reach builds. Similarly to Halo 3 Release, Reach's updates also use the same configuration with the exception ofthe network configuration file, and similarly we currently only target Title-Update 1 `12065.11.08.24.1738.tu1actual`.
- 12065.11.08.24.1738.tu1actual (TU 1)
- 11883.10.10.25.1227.dlc_1_ship (Leaked dev build)
- 11860.10.07.24.0147.omaha_release
### Managing Variants
We don't have any tooling in place for managing Halo: Reach map and game variants, though many have been manually imported.

## Unsupported Versions
### Halo 3 Epsilon
Title Storage configuration for builds shortly before release and `11856.07.08.20.2332.release` which was built 15 minutes after release.
- 11856.07.08.20.2332.release (Epsilon)
- 11729.07.08.10.0021.main (Expo)
- 11637.07.08.02.2348.release (Epsilon Refresh)

These versions of Halo 3 come with few maps which is why they are configured separately to Release. Maps included are:
- Sandtrap
- Valhalla
- Last Resort
- Snowbound
- High Ground

### Halo 3 Beta
Configuration for builds from the public Beta test phase.
- 10015.07.05.14.2217.delta (TU 1)
- 09699.07.05.01.1534.delta
> **NOTE**: More unreleased versions exist from around this time.

### Halo 3 Delta
Configuration for various leaked in-developmnent builds between the Alpha and Beta stages. Includes:
- 08172.07.03.08.2240.delta
- 08117.07.03.07.1702.delta

### Halo 3 Alpha
Configuration for Alpha or "Pimps At Sea" versions of Halo 3, including:
- 06481.06.11.17.1330.alpha_release



## Halo: Reach
### Demo
Configuration for Halo: Reach's demo `00095.11.04.09.1509.demo`.

### Beta
Configuration for Halo: Reach's Beta.
- 09730.10.04.09.1309.omaha_delta
- 09449.10.03.25.1545.omaha_beta (Private Beta)

### Alpha
Configuration for Halo: Reach's Private Alpha.
- 08516.10.02.19.1607.omaha_alpha

## Halo Online
Title storage for Halo Online ms23. For use with [ManagedDonkey](https://github.com/twist84/ManagedDonkey).

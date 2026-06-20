# AKS068 keyboard VIA programming files

the AKS068 is a budget 68% usb-c ergonomic alice/arisu style keyboard sold under a few different names: ajazz, attack shark, mambasnake... it comes in two flavors: wired and pro, which they refer to as "trimode" w/ wired, 3 channel bluetooth, and 2.4g wireless mode with a usb-a dongle.

this repo contains __working__ VIA json programming files for both the [wired](https://amzn.to/3WEuj2R) and [pro](https://amzn.to/3WqCIpa) versions of the AKS068 keyboard. _unlike what's on their website._ plus my custom layout.

## preview

here's my personal layout:

![keyboard layout](https://raw.githubusercontent.com/xero/aks068-via/main/layout-preview.png)

## how to

using the [via web app](http://usevia.app) (here's a great [tutorial](https://epomaker.com/blogs/guides/how-to-use-via-for-beginners)), under settings: enable the `design` option. since this keeb uses a hacky implementation of the standard, ensure you enabled the `Use V2 definitions (deprecated)` option when loading the via.json files. there's a discrete config for both wired/bluetooth and 2.4g modes for some reason. both the standard wired and pro use the [via-usb.json](AKS068-via-usb.json) file. the [via-24g.json](AKS068-via-24g.json) only applies to the pro version (you will need to disconnect and reconnect modes to flash both seperately). once the config is loaded you can import my [custom layout](AKS068-layout.json) or use the designer to create and export your own.

## loading layouts (the website Import is broken)

this keyboard's firmware botches the one VIA command the website uses to **import** a
saved layout (the bulk `DYNAMIC_KEYMAP_SET_BUFFER`, `0x13`): it returns the wrong
response header, so usevia.app aborts with `Error: Receiving incorrect response for
command`. you can still *edit* keys one at a time in the GUI, but loading a whole
exported layout fails.

[`aks068.py`](aks068.py) works around this. it talks the VIA HID protocol directly,
reading the keymap in bulk (`0x12`, which works) and writing it back **one key at a
time** (`0x05`, which also works) — the exact path the broken bulk import avoids. it
reads and writes the standard VIA export format, so you keep designing visually on
usevia.app and only use this to do the load the website can't.

it's a self-contained [uv](https://docs.astral.sh/uv/) script (deps declared inline,
nothing to install):

```sh
uv run aks068.py devices                              # list connected keyboards
uv run aks068.py save -f mylayout.json                # read keymap off the keyboard
uv run aks068.py load -f mylayout.json --dry-run      # preview the diff, write nothing
uv run aks068.py load -f mylayout.json --backup before.json   # load (backup first)
uv run aks068.py --pid 0x5088 load -f mylayout.json   # target 2.4G mode (pro)
```

`load` backs up the current keymap, writes only the keys that differ, then reads
everything back and verifies. it only ever sends keymap read/write commands — never
reset or bootloader. keymap only (macros/encoders are not transferred).

### files

* [AKS068-via-usb.json](AKS068-via-usb.json) — wired/bt VIA definition, with the `customKeycodes` relabeled to what the keys *actually* do (side-light controls, win/mac switch, screen brightness), cross-referenced against the factory layout and the manual. the upstream/vendor labels are for the pro variant and are wrong on this board.
* [AKS068-via-24g.json](AKS068-via-24g.json) — 2.4g definition (pro only; xero's, unchanged)
* [AKS068-factory-layout.json](AKS068-factory-layout.json) — untouched factory keymap dumped from a brand-new keyboard, handy as a reference / restore point
* [AKS068-layout.json](AKS068-layout.json) — xero's original custom layout
* [layouts/](layouts/) — my personal layouts (`stas-base`, and `stas-cleaned` with the fn layers stripped of pass-through letters)

> [!NOTE]
> a fork of [xero/aks068-via](https://github.com/xero/aks068-via) — the `aks068.py` tool, the corrected key labels, and the factory layout are additions.


## references

* https://epomaker.com/blogs/guides/how-to-use-via-for-beginners
* https://epomaker.com/blogs/via-json/ajazz-aks068-pro-usb-json-file
* https://epomaker.com/blogs/via-json/ajazz-aks068-pro-2-4g-json-file
* https://attackshark.com/products/attackshark-ajazz-aks068pro-ergonomic-alicelayout
* https://www.a-jazz.com/en/search.jsp?id=422&q=AKS068
* https://www.caniusevia.com/docs/specification
* https://usevia.app

## license

![kopimi logo](https://gist.githubusercontent.com/xero/cbcd5c38b695004c848b73e5c1c0c779/raw/6b32899b0af238b17383d7a878a69a076139e72d/kopimi-sm.png)

all files and scripts in this repo are released [CC0](https://creativecommons.org/publicdomain/zero/1.0/) / [kopimi](https://kopimi.com)! in the spirit of _freedom of information_, i encourage you to fork, modify, change, share, or do whatever you like with this project! `^c^v`
